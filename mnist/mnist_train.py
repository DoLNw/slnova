# 导入库
import torch
import torchvision.transforms as transforms
from torchvision import datasets
import matplotlib.pyplot as plt
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import base64
import time
from termcolor import cprint
import xlwt
import os

import conf
CONF = conf.CONF

data_dir = CONF.MNIST.data_fold_path

from db.mysql import upload_ml_info, upload_is_training_status, upload_is_aggregating_status, get_all_training_host_uuids
from rabbitmq import rabbitmq
from scheduler.main.manager import SchedulerManager
from scheduler.main.host_state import hoststate


model_save_fold = CONF.MNIST.model_save_fold + "/" + hoststate.uuid   # 每一个主机训练好的模型存放的目录
save_aggre_model_fold_path = CONF.MNIST.save_aggre_model_fold_path    # 每一个主机存放的聚合的模型的目录
current_work_dir = os.path.abspath(os.path.dirname(__file__))       # 当前文件所在的目录

# 创建一个workbook设置编码
workbook = xlwt.Workbook(encoding='utf-8')
# 创建一个worksheet
worksheet = workbook.add_sheet('sheet')

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
weight_avg = True

# 若设置成不是1，那么就会断点续传了
global_epoch = 1

# 构建网络
# pytorch需要用类来构建网络，且需要继承nn.Module。其中必须要定义forward方法来进行前向传播，后向传播在pytorch内部会实现。
class ConvNet(nn.Module):
    def __init__(self):
        super(ConvNet, self).__init__()
        # batch*1*28*28（每次会送入batch个样本，输入通道数1（黑白图像），图像分辨率是28x28）
        # 下面的卷积层Conv2d的第一个参数指输入通道数，第二个参数指输出通道数，第三个参数指卷积核的大小
        self.conv1 = nn.Conv2d(1, 10, 5) # 输入通道数1，输出通道数10，核的大小5
        self.conv2 = nn.Conv2d(10, 20, 3) # 输入通道数10，输出通道数20，核的大小3
        # 下面的全连接层Linear的第一个参数指输入通道数，第二个参数指输出通道数
        self.fc1 = nn.Linear(20*10*10, 500) # 输入通道数是2000，输出通道数是500
        self.fc2 = nn.Linear(500, 10) # 输入通道数是500，输出通道数是10，即10分类
    def forward(self,x):
        in_size = x.size(0) # 在本例中in_size=512，也就是BATCH_SIZE的值。输入的x可以看成是512*1*28*28的张量。
        out = self.conv1(x) # batch*1*28*28 -> batch*10*24*24（28x28的图像经过一次核为5x5的卷积，输出变为24x24）
        out = F.relu(out) # batch*10*24*24（激活函数ReLU不改变形状））
        out = F.max_pool2d(out, 2, 2) # batch*10*24*24 -> batch*10*12*12（2*2的池化层会减半）
        out = self.conv2(out) # batch*10*12*12 -> batch*20*10*10（再卷积一次，核的大小是3）
        out = F.relu(out) # batch*20*10*10
        out = out.view(in_size, -1) # batch*20*10*10 -> batch*2000（out的第二维是-1，说明是自动推算，本例中第二维是20*10*10）
        out = self.fc1(out) # batch*2000 -> batch*500
        out = F.relu(out) # batch*500
        out = self.fc2(out) # batch*500 -> batch*10
        out = F.log_softmax(out, dim=1) # 计算log(softmax(x))
        return out


# 训练模型
def train(model, train_loader, optimizer, epoch):
    if not os.path.exists(model_save_fold):
        # os.mkdir(model_save_fold)
        os.system("mkdir -p {0}".format(model_save_fold)) # 此处需要-p，允许创建目录及子目录
    if not os.path.exists(save_aggre_model_fold_path):
        os.mkdir(save_aggre_model_fold_path)
    # if os.path.exists(CONF.STN.model_save_fold + "/" + hoststate.uuid + '/' + hoststate.uuid + '.xlsx'): # 删除excel数据文件，防止出现重写错误
    #     os.remove(CONF.STN.model_save_fold + "/" + hoststate.uuid + '/' + hoststate.uuid + '.xlsx')

    # global workbook
    # global worksheet
    #
    # # 创建一个workbook设置编码
    # workbook = xlwt.Workbook(encoding='utf-8')
    # # 创建一个worksheet
    # worksheet = workbook.add_sheet('sheet')

    # worksheet.write(2, 20, hoststate.uuid)
    # worksheet.write(3, 20, con_filename)


    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(DEVICE), target.to(DEVICE)
        optimizer.zero_grad()

        # 前向 + 反向 + 更新
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()

        if (batch_idx + 1) % 30 == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                       100. * batch_idx / len(train_loader), loss.item()))


def test(model, test_loader):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(DEVICE), target.to(DEVICE)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()  # 将一批的损失相加
            pred = output.max(1, keepdim=True)[1]  # 找到概率最大的下标
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)
    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.4f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))

    return test_loss, 100. * correct / len(test_loader.dataset)

def start_train():
    # 设置超参数
    BATCH_SIZE = 512
    EPOCHS = 20

    global global_epoch

    # 构造数据器
    train_loader = torch.utils.data.DataLoader(
        datasets.MNIST(data_dir, train=True, download=True,
                       transform=transforms.Compose([
                           transforms.ToTensor(),
                           transforms.Normalize((0.1307,), (0.3081,))
                       ])),
        batch_size=BATCH_SIZE, shuffle=True)

    test_loader = torch.utils.data.DataLoader(
        datasets.MNIST(data_dir, train=False, transform=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])),
        batch_size=BATCH_SIZE, shuffle=True)


    # 定义损失和优化器
    model = ConvNet().to(DEVICE)
    optimizer = optim.Adam(model.parameters())

    for epoch in range(1, EPOCHS + 1):
        train(model, train_loader, optimizer, epoch)
        loss, acc = test(model, test_loader)

        sl_epoch_end(loss, acc)

        if global_epoch % 4 == 0:
            # 此处，在每4轮，融合的前后分别进行一次参数融合
            sl_aggre(model, test_loader)

        # workbook.save(CONF.STN.model_save_fold + "/" + hoststate.uuid + '/' + hoststate.uuid + '.xlsx')

        global_epoch += 1

    # 结束的时候需要添加sl_finish方法
    sl_finish(model, test_loader)

"""
termcolor 支持以下颜色：
grey, red, green, yellow, blue, magenta, cyan, white

支持以下以下背景高亮：
on_grey, on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white

支持以下属性：
bold, dark, underline, blink, reverse, concealed
"""

# 在训练中添加这三个方法，注意最上面还要添加import方法
# 训练前的更新信息方法，写在了main.py中
# 每一次训练结束之后，需要更新信息
def sl_epoch_end(loss, accuracy):
    upload_ml_info(loss, accuracy, global_epoch, "{0}/MNIST-{1}.pth".format(model_save_fold, global_epoch))


# 若到达一定训练轮数之后，进行参数聚合
def sl_aggre(mod, test_loader):
    # 保存方式2，模型参数（官方推荐）
    torch.save(mod.state_dict(), "{0}/MNIST-{1}.pth".format(model_save_fold, global_epoch)) # 一定轮数后存储模型，然后聚合

    rabbitmq.send_waiting_scheduler_message()

    # 等待所有主机训练结束，然后收到开始调度的通知
    cprint('waiting scheduler...', "white", "on_grey")
    while not hoststate.receive_scheduler_signal:
        time.sleep(1)
    hoststate.receive_scheduler_signal = False

    # 开始调度
    # 训练完之后，大家一起计算，那计算出来的结果基本是一致的
    # 只有得到自己是聚合节点的时候，才进行
    # 称重之后，自己是权重最高的，自己需要当聚合的节点
    # 存储模型后同时发送模型，然后等待其它训练好得到新模型，然后进行下一轮epoch
    scheduler_manager = SchedulerManager()
    dest = scheduler_manager.select_destinations()
    cprint("\n调度得到的所有的个数： " + str(len(dest)) + "\n", "white")

    for dest_host_state in dest:
        print(dest_host_state.short_description())

    aggregate_host_uuid = dest[0].uuid

    # 如果那个聚合节点的不是自己
    if aggregate_host_uuid != hoststate.uuid:
        # 以下是自己这个模型，自己的模型得先评估一下
        cprint('test before aggretation', "cyan", flush=True)
        test(mod, test_loader)

        cprint("<====== not aggregating node ======>", "yellow")
        hoststate.aggreNode = False
        # model_file = open(file_name, "rb").read()
        model_file = open("{0}/MNIST-{1}.pth".format(model_save_fold, global_epoch), "rb").read()
        encode_str = base64.b64encode(model_file)
        cprint("sending model...", "white", "on_grey")
        rabbitmq.send_rabbitmq_message(encode_str, rabbitmq.ExchangeType.DIRECT, aggregate_host_uuid)    # 发送模型

        cprint("receiving updated model...", "white", "on_grey")
        # 判断是否收到了更新的模型，收到的话rabbitmq的接收会发送消息的
        while not hoststate.receive_update_model:
            time.sleep(1)
        # 收到了更新后的模型

        cprint("loading updated model...", "white", "on_grey")
        loaded_model = torch.load("{0}/MNISTaggre-{1}.pth".format(save_aggre_model_fold_path, global_epoch))
        mod.load_state_dict(loaded_model)
        cprint("<====== loading updated model finished ======>", "yellow")
        hoststate.receive_update_model = False
    else:
        cprint("<====== aggregating node ======>", "yellow")
        hoststate.aggreNode = True
        # 等待收集完毕，然后聚合完毕，然后发送完毕
        upload_is_aggregating_status(True)
        # 收集所有的模型
        # 进行更新
        # 分发更新的数据库

        # 有没有收集完毕，收集的model的数目就是current_training_hosts_num
        count = 0
        current_training_host_uuids = get_all_training_host_uuids()
        current_training_hosts_num = len(current_training_host_uuids)
        cprint("waiting for receiving other hosts' model...current_training_hosts_num: {}".format(current_training_hosts_num), "white", "on_grey")
        while hoststate.receive_all_model_files < current_training_hosts_num - 1:
            time.sleep(1)
            count += 1
            # 每60秒在判断一次目前还有多少主机正在运行s
            if count >= 60:
                count = 0
                current_training_host_uuids = get_all_training_host_uuids()
                current_training_hosts_num = len(current_training_host_uuids)
                cprint("waiting for receivingx other hosts' model...current_training_hosts_num: {}".format(current_training_hosts_num), "white", "on_grey")
        hoststate.receive_all_model_files = 0

        #####################################模型融合########################################
        cprint("received all models, aggregating {0} models now...".format(current_training_hosts_num), "white", "on_grey")

        model_dirs = ["{0}/MNIST-{1}.pth".format(model_save_fold, global_epoch)]  # 第一个表示自己的模型
        for i in range(current_training_hosts_num - 1):
            model_dirs.append("{0}/MNIST{1}-{2}.pth".format(save_aggre_model_fold_path, i, global_epoch))

        #####################################取出模型，计算加权平均的权重########################################
        losses = []
        loss_all = 0
        acces = []
        acc_all = 0

        weights = []

        # 测试评估所有模型在本地数据集
        # 第一个是自己的模型，应该效果会最好
        cprint('test before aggregation', "cyan", flush=True)
        # 以下是其他的几个模型在本地数据集的评估
        # 根据上面的目录集合，获得模型集合
        models_paras = []

        with torch.no_grad():
            for i, dict_model_dir in enumerate(model_dirs):
                model_param = (torch.load(dict_model_dir))
                models_paras.append(model_param)

                # 自己的模型需要先评估一下，是需要存储的
                if i == 0:
                    loss, accuracy = test(mod, test_loader)

                if weight_avg:
                    # 把每一个模型，放到我本地的数据集进行评估，得到这几个参数
                    # 由于是越小越小，所以需要取倒数
                    if i != 0:
                        mod.load_state_dict(model_param)
                        loss, accuracy = test(mod, test_loader)

                    losses.append(loss)
                    loss_all += loss

                    acces.append(accuracy)
                    acc_all += accuracy

            model_size = len(models_paras)

            if weight_avg:
                for i in range(model_size):
                    acces[i] = round(acces[i] / acc_all, 5)

                    weights.append(acces[i])
            else:
                for i in range(model_size):
                    weights.append(1 / model_size)

        #####################################取出模型，计算加权平均的权重########################################
        params = {}

        # if model_size >= 2:  # 至少有两个模型，则需要融合
        # 对其他的每一个模型进行一个个的合并，不再需要判断，因为若只有一个在训练，那么models_paras唯空

        for i, model_paras in enumerate(models_paras):
            cprint(weights[i], "red")
            for key, val in model_paras.items():
                if i == 0:
                    params[key] = val * weights[i]
                else:
                    params[key] += val * weights[i]

        # 释放掉?
        models_paras = []

        cprint("models aggre successfully", "yellow")

        # 加载更新好的网络参数
        mod.load_state_dict(params)

        # 下面这个名字随便取，因为不需要加载这个模型，自己：上面直接加载进参数，其他主机：收到模型后会更改模型名字
        # 不能随便取啊兄弟，预测的时候，需要用到这个模型，而且还需要json文件（这个自己加一下也行）
        torch.save(mod.state_dict(), "{0}/MNISTaggre-{1}.pth".format(save_aggre_model_fold_path, global_epoch))  # 一定轮数后存储模型，然后聚合
        cprint('saved model to {0}/MNISTaggre-{1}.pth'.format(save_aggre_model_fold_path, global_epoch), "magenta")
        #####################################模型融合########################################

        # 更新后的模型参数分发给其他的主机
        model_file = open("{0}/MNISTaggre-{1}.pth".format(save_aggre_model_fold_path, global_epoch),
                          "rb").read()
        encode_str = base64.b64encode(model_file)

        cprint("distributing updated model to {0} host...".format(current_training_hosts_num-1), "white",
               "on_grey")
        for uuid in current_training_host_uuids:
            if uuid != hoststate.uuid:
                rabbitmq.send_rabbitmq_message(encode_str, rabbitmq.ExchangeType.DIRECT, uuid)    # 发送模型

        cprint("<====== distribute updated model to others successfully ======>", "yellow")
        upload_is_aggregating_status(False)


    # 等待聚合节点分发更新后的参数模型，等待更新完之后，进行下一次的训练，或者到达完成
    cprint('aggregating task finished, waiting for others...', "white", "on_grey")
    rabbitmq.send_epoch_message(global_epoch)

    while not hoststate.receive_next_epoch_train_signal:
        time.sleep(1)
    hoststate.receive_next_epoch_train_signal = False

    cprint('test after aggregation', "cyan", flush=True)
    test(mod, test_loader)

# 所有训练结束之后，需要告知训练结束s
def sl_finish(mod, test_loader):
    # 训练结束
    cprint('<============================== training finished ==============================>', "magenta")
    cprint('<============================== testing   started ==============================>', "magenta")
    test(mod, test_loader)
    cprint('<============================== testing  finished ==============================>', "magenta")

    global global_epoch
    global_epoch = 1
    upload_is_training_status(False)
    rabbitmq.send_finish_message()


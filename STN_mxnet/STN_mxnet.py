# -*- coding:utf-8 -*-s

import time
import json
import argparse
import numpy as np
import mxnet as mx
import base64
import os

import re
import xlwt

import shutil
from termcolor import cprint

from STN_mxnet.utils_4n0_3layer_12T_res import (construct_model, generate_data,
                       masked_mae_np, masked_mape_np, masked_mse_np)

from db.mysql import upload_ml_info, upload_is_training_status, upload_is_aggregating_status, get_all_training_host_uuids
from rabbitmq import rabbitmq
from scheduler.main.manager import SchedulerManager
from scheduler.main.host_state import hoststate

import conf
CONF = conf.CONF


# parser = argparse.ArgumentParser()
# parser.add_argument("--config", type=str, help='configuration file')
# parser.add_argument("--test", action="store_true", help="test program")
# parser.add_argument("--plot", help="plot network graph", action="store_true")
# parser.add_argument("--save", action="store_true", help="save model")
# args = parser.parse_args()

class Args(object):
    """docstring for args"""

    def __init__(self):
        super(Args, self).__init__()

        self.config = CONF.STN.config_path
        # self.test = False
        self.test = True
        self.plot = False
        self.save = True
        self.weight_avg = True


args = Args()

model_save_fold = CONF.STN.model_save_fold + "/" + hoststate.uuid   # 每一个主机训练好的模型存放的目录
save_aggre_model_fold_path = CONF.STN.save_aggre_model_fold_path    # 每一个主机存放的聚合的模型的目录
current_work_dir = os.path.abspath(os.path.dirname(__file__))       # 当前文件所在的目录
# config_filename = current_work_dir + "/" + args.config              # 当前ml的配置文件的目录
config_filename_dir = current_work_dir

# 创建一个workbook设置编码
workbook = xlwt.Workbook(encoding='utf-8')
# 创建一个worksheet
worksheet = workbook.add_sheet('sheet')


# 若设置成不是1，那么就会断点续传了
global_epoch = 1

# 这个最后的一次评估，不是使用的最后的聚合模型，而是使用的聚合模型之后在训练一些轮数之后自己的模型
def eval(mod, test_loader, test_y, config, after_aggretion=False, save = True):
    t = time.time()
    test_loader.reset()
    prediction = mod.predict(test_loader)[1].asnumpy()

    tmp_info = []
    for idx in range(config['num_for_predict']):
        y, x = test_y[:, : idx + 1, :], prediction[:, : idx + 1, :]
        tmp_info.append((
            masked_mae_np(y, x, 0),
            masked_mape_np(y, x, 0),
            masked_mse_np(y, x, 0) ** 0.5
        ))
    mae, mape, rmse = tmp_info[-1]

    cprint('test: Epoch: {}, RMSE: {:.2f}, MAE: {:.2f}, MAPE: {:.2f}, '
           'time: {:.2f}s'.format(global_epoch, rmse, mae, mape, time.time() - t), "cyan", flush=True)
    if save:
        # global_epoch-1，否则的话，global_epoch指示的是下一轮
        if not after_aggretion:
            worksheet.write(global_epoch + 1, 8, global_epoch)
            worksheet.write(global_epoch + 1, 9, rmse)
            worksheet.write(global_epoch + 1, 10, mae)
            worksheet.write(global_epoch + 1, 11, mape)
            worksheet.write(global_epoch + 1, 12, time.time() - t)
        else:
            worksheet.write(global_epoch + 1, 14, global_epoch)
            worksheet.write(global_epoch + 1, 15, rmse)
            worksheet.write(global_epoch + 1, 16, mae)
            worksheet.write(global_epoch + 1, 17, mape)
            worksheet.write(global_epoch + 1, 18, time.time() - t)

    return mae, mape, rmse, time.time() - t

def training(con_filename):
    config_filename = config_filename_dir + "/" + con_filename

    worksheet.write(2, 20, hoststate.uuid)
    worksheet.write(3, 20, con_filename)

    if not os.path.exists(model_save_fold):
        # os.mkdir(model_save_fold)
        os.system("mkdir -p {0}".format(model_save_fold)) # 此处需要-p，允许创建目录及子目录
    if not os.path.exists(save_aggre_model_fold_path):
        os.mkdir(save_aggre_model_fold_path)
    if os.path.exists(CONF.STN.model_save_fold + "/" + hoststate.uuid + '/' + hoststate.uuid + '.xlsx'): # 删除excel数据文件，防止出现重写错误
        os.remove(CONF.STN.model_save_fold + "/" + hoststate.uuid + '/' + hoststate.uuid + '.xlsx')

    with open(config_filename, 'r') as f:
        config = json.loads(f.read())

    net = construct_model(config)

    epochs = config['epochs']
    if args.test:
        epochs = 40
    batch_size = config['batch_size']
    num_of_vertices = config['num_of_vertices']
    graph_signal_matrix_filename = config['graph_signal_matrix_filename']  # npz文件
    if isinstance(config['ctx'], list):
        ctx = [mx.gpu(i) for i in config['ctx']]
    elif isinstance(config['ctx'], int):
        ctx = mx.gpu(config['ctx'])

    loaders = []
    true_values = []
    for idx, (x, y) in enumerate(generate_data(graph_signal_matrix_filename)):
        if args.test:
            x = x[: 100]
            y = y[: 100]

        # 为了处理170个节点自己改动的第一个地方
        # 此处是要训练的数据，需要取出第三维的前170个节点的数据
        if len(x[0][0]) != 170:  # 如果节点个数不是170个，取出前170个的呗
            x = x[:, :, : 170]
            y = y[:, :, : 170]

        y = y.squeeze(axis=-1)
        # print(x.shape, y.shape)
        loaders.append(
            mx.io.NDArrayIter(
                x, y if idx == 0 else None,
                batch_size=batch_size,
                shuffle=(idx == 0),
                label_name='label'
            )
        )
        if idx == 0:
            training_samples = x.shape[0]
        else:
            true_values.append(y)

    train_loader, val_loader, test_loader = loaders
    val_y, test_y = true_values

    global_train_steps = training_samples // batch_size + 1
    all_info = []


    mod = mx.mod.Module(
        net,
        data_names=['data'],
        label_names=['label'],
        context=ctx
    )

    mod.bind(
        data_shapes=[(
            'data',
            (batch_size, config['points_per_hour'], num_of_vertices, 1)
        ), ],
        label_shapes=[(
            'label',
            (batch_size, config['points_per_hour'], num_of_vertices)
        )]
    )

    mod.init_params(initializer=mx.init.Xavier(magnitude=0.0003))
    lr_sch = mx.lr_scheduler.PolyScheduler(
        max_update=global_train_steps * epochs * config['max_update_factor'],
        base_lr=config['learning_rate'],
        pwr=2,
        warmup_steps=global_train_steps
    )

    mod.init_optimizer(
        optimizer=config['optimizer'],
        optimizer_params=(('lr_scheduler', lr_sch),)
    )

    num_of_parameters = 0
    for param_name, param_value in mod.get_params()[0].items():
        # print(param_name, param_value.shape)
        num_of_parameters += np.prod(param_value.shape)
    # print("Number of Parameters: {}".format(num_of_parameters), flush=True)

    metric = mx.metric.create(['RMSE', 'MAE'], output_names=['pred_output'])

    if args.plot:
        graph = mx.viz.plot_network(net)
        graph.format = 'png'
        graph.render('graph')



    global global_epoch
    lowest_val_loss = 1e6


    # 在训练之前，需要考虑一下断点续传的问题，因为有时候可能由于传输等一些的原因，训练会出错
    # 如果传进来的global_epoch不是1，那就证明我不是从头开始训练，我需要从这里开始训练
    # 但是我现在是每隔20轮存储一次，所以训练的节点只能每20加一次。
    # 把global_epoch当作全局变量，然后传入20就代表将前面的20的聚合模型导入，然后从第21轮开始训练
    # global_epoch = 80

    if global_epoch != 1 and global_epoch % 20 == 0:
        cprint("restore training from epoch: {0}".format(global_epoch), "green")
        # sym是网络，arg_params是权重参数，aux_params是辅助状态
        sym, arg_params, aux_params = mx.model.load_checkpoint("{0}/aggre".format(save_aggre_model_fold_path),
                                                               global_epoch)
        mod.set_params(arg_params, aux_params, allow_missing=True)
        global_epoch += 1
    else:
        cprint("start new training...".format(global_epoch), "green")

    for _ in range(epochs):
        t = time.time()
        info = [global_epoch]
        train_loader.reset()
        metric.reset()
        for idx, databatch in enumerate(train_loader):
            mod.forward_backward(databatch)
            mod.update_metric(metric, databatch.label)
            mod.update()
        metric_values = dict(zip(*metric.get()))

        cprint('training: Epoch: %s, RMSE: %.2f, MAE: %.2f, time: %.2f s' % (
            global_epoch, metric_values['rmse'], metric_values['mae'],
            time.time() - t), "cyan", flush=True)
        worksheet.write(global_epoch + 1, 0, global_epoch)
        worksheet.write(global_epoch + 1, 1, metric_values['rmse'])
        worksheet.write(global_epoch + 1, 2, metric_values['mae'])
        worksheet.write(global_epoch + 1, 3, time.time() - t)
        info.append(metric_values['mae'])

        val_loader.reset()
        prediction = mod.predict(val_loader)[1].asnumpy()
        loss = masked_mae_np(val_y, prediction, 0)
        cprint('validation: Epoch: %s, loss: %.2f, time: %.2f s' % (
            global_epoch, loss, time.time() - t), "cyan", flush=True)
        worksheet.write(global_epoch + 1, 5, loss)
        worksheet.write(global_epoch + 1, 6, time.time() - t)
        info.append(loss)

        # 每一次的训练完成之后，需要添加sl_epoch_end
        sl_epoch_end(loss)

        if global_epoch % 20 == 0:
            # 此处，在每20轮，融合的前后分别进行一次参数融合

            sl_aggre(mod, test_loader, test_y, config)

        workbook.save(CONF.STN.model_save_fold + "/" + hoststate.uuid + '/' + hoststate.uuid + '.xlsx')

        # if loss < lowest_val_loss:
        #
        #     test_loader.reset()
        #     prediction = mod.predict(test_loader)[1].asnumpy()
        #     tmp_info = []
        #     for idx in range(config['num_for_predict']):
        #         y, x = test_y[:, : idx + 1, :], prediction[:, : idx + 1, :]
        #         tmp_info.append((
        #             masked_mae_np(y, x, 0),
        #             masked_mape_np(y, x, 0),
        #             masked_mse_np(y, x, 0) ** 0.5
        #         ))
        #     mae, mape, rmse = tmp_info[-1]
        #     print('test: Epoch: {}, MAE: {:.2f}, MAPE: {:.2f}, RMSE: {:.2f}, '
        #           'time: {:.2f}s'.format(
        #             global_epoch, mae, mape, rmse, time.time() - t))
        #     print(flush=True)
        #     info.extend((mae, mape, rmse)) # 列表末尾一次性追加多个值
        #     info.append(tmp_info)
        #     all_info.append(info)
        #     lowest_val_loss = loss

        global_epoch += 1

    # 结束的时候需要添加sl_finish方法
    sl_finish(mod, test_loader, test_y, config)



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
def sl_epoch_end(loss):
    upload_ml_info(loss, 0, global_epoch,
                   "{0}/STN-{1}.params".format(model_save_fold, "%04d" % (global_epoch // 20 * 20)))

# 若到达一定训练轮数之后，进行参数聚合
def sl_aggre(mod, test_loader, test_y, config):
    mod.save_checkpoint('{}/STN'.format(model_save_fold), global_epoch)
    cprint('saved model to {0}/STN-{1}.params'.format(model_save_fold, "%04d" % global_epoch), "magenta") # 一定轮数后存储模型，然后聚合

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
        eval(mod, test_loader, test_y, config, after_aggretion=False, save=True)

        cprint("<====== not aggregating node ======>", "yellow")
        hoststate.aggreNode = False
        # model_file = open(file_name, "rb").read()
        model_file = open("{0}/STN-{1}.params".format(model_save_fold, "%04d" % global_epoch), "rb").read()
        encode_str = base64.b64encode(model_file)
        cprint("sending model...", "white", "on_grey")
        rabbitmq.send_rabbitmq_message(encode_str, rabbitmq.ExchangeType.DIRECT, aggregate_host_uuid)    # 发送模型

        cprint("receiving updated model...", "white", "on_grey")
        # 判断是否收到了更新的模型，收到的话rabbitmq的接收会发送消息的
        while not hoststate.receive_update_model:
            time.sleep(1)
        # 收到了更新后的模型

        cprint("loading updated model...", "white", "on_grey")
        # sym是网络，arg_params是权重参数，aux_params是辅助状态
        sym, arg_params, aux_params = mx.model.load_checkpoint("{0}/aggre".format(save_aggre_model_fold_path), global_epoch)
        mod.set_params(arg_params, aux_params, allow_missing=True)
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

        if not os.path.exists('{}/STN-symbol.json'.format(save_aggre_model_fold_path)):
            mod.save_checkpoint('{}/STN'.format(save_aggre_model_fold_path),
                                global_epoch)  # 自己的模型在aggre文件夹中也存储一遍，这样的话会有json文件
        if not os.path.exists('{}/aggre-symbol.json'.format(save_aggre_model_fold_path)):
            shutil.copyfile('{}/STN-symbol.json'.format(save_aggre_model_fold_path),
                            '{}/aggre-symbol.json'.format(save_aggre_model_fold_path))  # 为了拿到json文件

        model_dirs = ['{}/STN'.format(model_save_fold)]  # 这里面的目录，不用存储后缀，第一个表示自己的模型
        for i in range(current_training_hosts_num - 1):
            json_path = "{0}/STN{1}-symbol.json".format(save_aggre_model_fold_path, i)
            if not os.path.exists(json_path):
                shutil.copyfile('{}/STN-symbol.json'.format(save_aggre_model_fold_path), json_path)  # 为了拿到json文件
            model_dirs.append("{0}/STN{1}".format(save_aggre_model_fold_path, i))



        #####################################取出模型，计算加权平均的权重########################################
        maes = []
        mae_all = 0
        rmses = []
        rmse_all = 0
        mapes = []
        mape_all = 0

        weights = []

        # 测试评估所有模型在本地数据集
        # 第一个是自己的模型，应该效果会最好
        cprint('test before aggregation', "cyan", flush=True)
        # 以下是其他的几个模型在本地数据集的评估
        # 根据上面的目录集合，获得模型集合
        models_paras = []

        for i, model_prefix in enumerate(model_dirs):
            # 里面第0个sym网络结构，第1个是参数，第2个辅助状态
            model_param = mx.model.load_checkpoint(model_prefix, global_epoch)
            arg_param = model_param[1]
            aux_param = model_param[2]
            models_paras.append(arg_param)

            # 自己的模型需要先评估一下，是需要存储的
            if i == 0:
                mae, mape, rmse, mytime = eval(mod, test_loader, test_y, config, after_aggretion=False, save=True)

            if args.weight_avg:
                # 把每一个模型，放到我本地的数据集进行评估，得到这几个参数
                # 由于是越小越小，所以需要取倒数
                if i != 0:
                    mod.set_params(arg_param, aux_param, allow_missing=True)
                    mae, mape, rmse, mytime = eval(mod, test_loader, test_y, config, after_aggretion=False, save=False)

                mae = round(1 / mae, 5)
                maes.append(mae)
                mae_all += mae

                rmse = round(1 / rmse, 5)
                rmses.append(rmse)
                rmse_all += rmse

                mape = round(1 / mape, 5)
                mapes.append(mape)
                mape_all += mape

        model_size = len(models_paras)

        if args.weight_avg:
            for i in range(model_size):
                maes[i] = round(maes[i] / mae_all, 5)
                rmses[i] = round(rmses[i] / rmse_all, 5)
                mapes[i] = round(mapes[i] / mape_all, 5)

                weights.append((maes[i] + rmses[i] + mapes[i]) / 3)  # 注意，这里三个指标，所以除以3
        else:
            for i in range(model_size):
                weights.append(1 / model_size)

        #####################################取出模型，计算加权平均的权重########################################
        arg_params = {}

        # if model_size >= 2:  # 至少有两个模型，则需要融合
        # 对其他的每一个模型进行一个个的合并，不再需要判断，因为若只有一个在训练，那么models_paras唯空

        for i, model_paras in enumerate(models_paras):
            # print(len(model_paras))
            cprint(weights[i], "red")
            for param_name, param_value in model_paras.items():
                if i == 0:
                    arg_params[param_name] = param_value * weights[i]
                else:
                    arg_params[param_name] += param_value * weights[i]

        # 释放掉?
        models_paras = []

        cprint("models aggre successfully", "yellow")

        # 加载网络的参数
        aux_params = {}
        mod.set_params(arg_params, aux_params, allow_missing=True)

        # 下面这个名字随便取，因为不需要加载这个模型，自己：上面直接加载进参数，其他主机：收到模型后会更改模型名字
        # 不能随便取啊兄弟，预测的时候，需要用到这个模型，而且还需要json文件（这个自己加一下也行）
        mod.save_checkpoint("{0}/aggre".format(save_aggre_model_fold_path), global_epoch)
        cprint('saved model to {0}/aggre-{1}.params'.format(save_aggre_model_fold_path, "%04d" % global_epoch), "magenta")
        #####################################模型融合########################################


        # 更新后的模型参数分发给其他的主机
        model_file = open("{0}/aggre-{1}.params".format(save_aggre_model_fold_path, "%04d" % global_epoch),
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
    eval(mod, test_loader, test_y, config, True)

# 所有训练结束之后，需要告知训练结束s
def sl_finish(mod, test_loader, test_y, config):
    # 训练结束
    cprint('<============================== training finished ==============================>', "magenta")
    cprint('<============================== testing   started ==============================>', "magenta")
    eval(mod, test_loader, test_y, config, save=False)
    cprint('<============================== testing  finished ==============================>', "magenta")

    global global_epoch
    global_epoch = 1
    upload_is_training_status(False)
    rabbitmq.send_finish_message()


# training(epochs)
#
# the_best = min(all_info, key=lambda x: x[2])
# print('step: {}\ntraining loss: {:.2f}\nvalidation loss: {:.2f}\n'
#       'tesing: MAE: {:.2f}\ntesting: MAPE: {:.2f}\n'
#       'testing: RMSE: {:.2f}\n'.format(*the_best))
# print(the_best)
#
# if args.save:
#     mod.save_checkpoint('STN', epochs)

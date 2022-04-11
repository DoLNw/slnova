# -*- coding:utf-8 -*-

import time
import json
import argparse
import numpy as np
import mxnet as mx
import base64
import os
import shutil
from termcolor import cprint

from STN_mxnet.utils_4n0_3layer_12T_res import (construct_model, generate_data,
                       masked_mae_np, masked_mape_np, masked_mse_np)

from db.mysql import upload_ml_info, upload_is_training_status, upload_is_aggregating_status, get_all_training_host_uuids
from rabbitmq.rabbitmq import ExchangeType, send_rabbitmq_message
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
        self.model_save_fold = CONF.STN.model_save_fold
        self.save_aggre_model_fold_path = CONF.STN.save_aggre_model_fold_path
        self.data_fold = CONF.STN.data_fold
        self.test = True
        self.plot = False
        self.save = True
args = Args()

# 给model下在创建个该及其的uuid的文件夹
args.model_save_fold += "/" + hoststate.uuid
if not os.path.exists(args.model_save_fold):
    os.mkdir(args.model_save_fold)
if not os.path.exists(args.save_aggre_model_fold_path):
    os.mkdir(args.save_aggre_model_fold_path)

current_work_dir = os.path.abspath(os.path.dirname(__file__)) # 当前文件所在的目录
config_filename = current_work_dir + "/" + args.config

global_epoch = 1

def training(epochs):
    with open(config_filename, 'r') as f:
        config = json.loads(f.read())

    print(json.dumps(config, sort_keys=True, indent=4))

    net = construct_model(config)

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
        y = y.squeeze(axis=-1)
        print(x.shape, y.shape)
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
    epochs = config['epochs']

    if args.test:
        epochs = 100

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
    print("Number of Parameters: {}".format(num_of_parameters), flush=True)

    metric = mx.metric.create(['RMSE', 'MAE'], output_names=['pred_output'])

    if args.plot:
        graph = mx.viz.plot_network(net)
        graph.format = 'png'
        graph.render('graph')






    global global_epoch
    lowest_val_loss = 1e6
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

        print('training: Epoch: %s, RMSE: %.2f, MAE: %.2f, time: %.2f s' % (
            global_epoch, metric_values['rmse'], metric_values['mae'],
            time.time() - t), flush=True)
        info.append(metric_values['mae'])

        val_loader.reset()
        prediction = mod.predict(val_loader)[1].asnumpy()
        loss = masked_mae_np(val_y, prediction, 0)
        print('validation: Epoch: %s, loss: %.2f, time: %.2f s' % (
            global_epoch, loss, time.time() - t), flush=True)
        info.append(loss)

        # 下面是我自己添加的
        upload_ml_info(loss, 0, global_epoch, "{0}/STN-{1}.params".format(args.model_save_fold, "%04d"%(global_epoch // 20 * 20)))

        if global_epoch % 20 == 0:
            mod.save_checkpoint('{}/STN'.format(args.model_save_fold), global_epoch)
            cprint('saved model to {0}/STN-{1}.params'.format(args.model_save_fold, "%04d" % global_epoch))

            send_rabbitmq_message(json.dumps(
                {'start': False, 'epoch': -1, 'scheduler': True, 'uuid': str(hoststate.uuid), "finished": False}),
                                  ExchangeType.FANOUT)
            # 等待所有主机训练结束，然后收到开始调度的通知
            cprint('waiting scheduler...')
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
            print("\n最后得到的所有的个数： " + str(len(dest)) + "\n")

            for dest_host_state in dest:
                print(dest_host_state.short_description())

            aggregate_host_uuid = dest[0].uuid

            # 如果那个聚合节点的不是自己
            if aggregate_host_uuid != hoststate.uuid:
                print("not aggre node")
                hoststate.aggreNode = False
                # model_file = open(file_name, "rb").read()
                model_file = open("{0}/STN-{1}.params".format(args.model_save_fold, "%04d" % global_epoch), "rb").read()
                encode_str = base64.b64encode(model_file)
                send_rabbitmq_message(encode_str, ExchangeType.DIRECT, aggregate_host_uuid)

                # 判断是否收到了更新的模型，若收到了，则
                while not hoststate.receive_update_model:
                    time.sleep(1)
                # 收到了更新后的模型
                print("loading updated model...")
                # sym是网络，arg_params是权重参数，aux_params是辅助状态
                sym, arg_params, aux_params = mx.model.load_checkpoint("{0}/STN".format(args.model_save_fold), global_epoch)
                mod.set_params(arg_params, aux_params, allow_missing=True)
                print("loading updated model finished")

                hoststate.receive_update_model = False
            else:
                print("aggre node")
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
                print("current_training_hosts_num: {}".format(current_training_hosts_num))
                while hoststate.receive_all_model_files < current_training_hosts_num - 1:
                    time.sleep(1)
                    count += 1
                    # 每60秒在判断一次目前还有多少主机正在运行s
                    if count >= 60:
                        count = 0
                        current_training_host_uuids = get_all_training_host_uuids()
                        current_training_hosts_num = len(current_training_host_uuids)
                        print("current_training_hosts_num: {}".format(current_training_hosts_num))
                hoststate.receive_all_model_files = 0

                #####################################模型融合########################################
                if not os.path.exists('{}/STN-symbol.json'.format(args.save_aggre_model_fold_path)):
                    mod.save_checkpoint('{}/STN'.format(args.save_aggre_model_fold_path), global_epoch) # 自己的模型在aggre文件夹中也存储一遍，这样的话会有json文件
                if not os.path.exists('{}/aggre-symbol.json'.format(args.save_aggre_model_fold_path)):
                    shutil.copyfile('{}/STN-symbol.json'.format(args.save_aggre_model_fold_path), '{}/aggre-symbol.json'.format(args.save_aggre_model_fold_path))  # 为了拿到json文件

                model_dirs = []                            # 这里面的目录，不用存储后缀
                for i in range(current_training_hosts_num-1):
                    json_path = "{0}/STN{1}-symbol.json".format(args.save_aggre_model_fold_path, i)
                    if not os.path.exists(json_path):
                        shutil.copyfile('{}/STN-symbol.json'.format(args.save_aggre_model_fold_path), json_path)  # 为了拿到json文件
                    model_dirs.append("{0}/STN{1}".format(args.save_aggre_model_fold_path, i))

                models_paras = []
                for model_prefix in model_dirs:
                    # 里面第0个sym网络结构，第1个是参数，第2个辅助状态
                    models_paras.append(mx.model.load_checkpoint(model_prefix, global_epoch)[1])

                model_size = len(models_paras) + 1  # 算上自己

                arg_params = {}

                if model_size >= 2:  # 至少有两个模型，则需要融合
                    for param_name, param_value in mod.get_params()[0].items():
                        arg_params[param_name] = param_value / model_size

                    # 对其他的每一个模型进行一个个的合并
                    for model_paras in models_paras:
                        print(len(model_paras))
                        for param_name, param_value in model_paras.items():
                            arg_params[param_name] += param_value / model_size

                # 释放掉
                models_paras = []

                print("models aggre successfully")

                # 加载网络的参数
                aux_params = {}
                mod.set_params(arg_params, aux_params, allow_missing=True)

                # 下面这个名字随便取，因为不需要加载这个模型，自己：上面直接加载进参数，其他主机：收到模型后会更改模型名字
                # 不能随便取啊兄弟，预测的时候，需要用到这个模型，而且还需要json文件（这个自己加一下也行）
                mod.save_checkpoint("{0}/aggre".format(args.save_aggre_model_fold_path), global_epoch)
                cprint('saved model to {0}/aggre-{1}.params'.format(args.save_aggre_model_fold_path, "%04d" % global_epoch))
                #####################################模型融合########################################
                # 更新后的模型参数分发给其他的主机
                model_file = open("{0}/aggre-{1}.params".format(args.save_aggre_model_fold_path, "%04d" % global_epoch), "rb").read()
                encode_str = base64.b64encode(model_file)

                for uuid in current_training_host_uuids:
                    if uuid != hoststate.uuid:
                        send_rabbitmq_message(encode_str, ExchangeType.DIRECT, uuid)

                upload_is_aggregating_status(False)

            # 等待聚合节点分发更新后的参数模型，等待更新完之后，进行下一次的训练
            cprint('waiting for next epoch {}...'.format(global_epoch + 1))
            send_rabbitmq_message(json.dumps(
                {'start': False, 'epoch': global_epoch, 'scheduler': False, 'uuid': str(hoststate.uuid), "finished": False}),
                                  ExchangeType.FANOUT)
            while not hoststate.receive_next_epoch_train_signal:
                time.sleep(1)
            hoststate.receive_next_epoch_train_signal = False



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

    # 训练结束
    cprint('training is finished')
    upload_is_training_status(False)
    send_rabbitmq_message(json.dumps(
        {'start': False, 'epoch': -1, 'scheduler': False, 'uuid': str(hoststate.uuid), "finished": True}),
                          ExchangeType.FANOUT)


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

# -*- coding:utf-8 -*-

import time
import json
import threading
import atexit

import sys
sys.path.append("..")

from scheduler.main.host_state import hoststate
from db.mysql import nessus_upload_task, basic_info_upload_taskask, upload_is_training_status, upload_ml_info, upload_basic_info, upload_is_aggregating_status
# from ml.run.magface_pyt import train
from rabbitmq.rabbitmq import RabbitComsumer, send_rabbitmq_message, ExchangeType
from STN_mxnet.STN_mxnet import training


# atexit模块的主要作用是在程序即将结束之间执行的代码。比如使用ctrl+c
# 注册
@atexit.register
def clean():
    # upload_ml_info()
    upload_is_training_status(False)
    upload_is_aggregating_status(False)

    print("stoped training...")



# Python3 多线程    https://www.runoob.com/python3/python3-multithreading.html
class RabbitmqThread(threading.Thread):
    def __init__(self, thread_id, name, exchange_type, routing_key=""):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.exchange_type = exchange_type
        self.routing_key = routing_key
        # self.thread_id.exit()

    def run(self):
        rabbit_consumer = RabbitComsumer(self.exchange_type)
        rabbit_consumer.start_consumer(self.routing_key)


class UploadBasicInfoThread(threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        # self.thread_id.exit()

    def run(self):
        basic_info_upload_taskask()
        # while True:
            # # 注意，打开数据库这个操作还是很耗时的，用这个sleep的话，这个数据库得一直开着
            # upload_basic_info()
            # time.sleep(0.5)


if __name__ == "__main__":
    print("{0} init successfully!".format(hoststate.uuid))
    fanout_rabbitmq_thread = RabbitmqThread(1, "fanout_rabbitmq_thread", ExchangeType.FANOUT, "")
    fanout_rabbitmq_thread.start()

    direct_rabbitmq_thread = RabbitmqThread(2, "direct_rabbitmq_thread", ExchangeType.DIRECT, routing_key=hoststate.uuid)
    direct_rabbitmq_thread.start()

    # 1. 动态更新状态
    # basic_info_upload_taskask()             # 持续更新本地机器的信息状态，上传到数据库
    # nessus_upload_task()    # 持续扫描机器的安全风险，上传到数据库

    upload_basic_info_thread = UploadBasicInfoThread(1, "direct_rabbitmq_thread")
    upload_basic_info_thread.start()

    # ml的一些参数的初始化
    upload_ml_info()
    upload_is_training_status(False)
    upload_is_aggregating_status(False)


    while True:
        # 若收到指令且当前没有训练任务的话，开始训练，并把指令设置成False
        if hoststate.receive_start_train_signal:
            hoststate.receive_start_train_signal = False
            if not hoststate.is_training:
                upload_is_training_status(True)

                send_rabbitmq_message(json.dumps({'start': True, 'epoch': -1, 'scheduler': False, 'uuid': str(hoststate.uuid), "finished": False}), ExchangeType.FANOUT)
                # train()
                upload_ml_info()
                training()
                # hoststate.is_training 设置成False是在train那个文件中
            else:
                print("当前存在训练，无法开启新的训练")
        time.sleep(10)




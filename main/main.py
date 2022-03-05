# -*- coding:utf-8 -*-

import time
import threading

import sys
sys.path.append("..")

from scheduler.main.host_state import hoststate
from db.mysql import basic_info_upload_taskask, nessus_upload_task, upload_is_training_status, upload_ml_info
from ml.run.magface_pyt import train
from rabbitmq.rabbitmq import RabbitComsumer


# Python3 多线程    https://www.runoob.com/python3/python3-multithreading.html
class FanoutRabbitmqThread(threading.Thread):
    def __init__(self, thread_id, name):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        # self.thread_id.exit()

    def run(self):
        rabbit_consumer = RabbitComsumer("fanout")
        rabbit_consumer.start_consumer()


if __name__ == "__main__":
    fanout_rabbitmq_thread = FanoutRabbitmqThread(1, "fanout_rabbitmq_thread")
    fanout_rabbitmq_thread.start()

    # 1. 动态更新状态
    basic_info_upload_taskask()             # 持续更新本地机器的信息状态，上传到数据库
    # nessus_upload_task()    # 持续扫描机器的安全风险，上传到数据库

    while True:
        # 若收到指令且当前没有训练任务的话，开始训练，并把指令设置成False
        if hoststate.receive_start_train_signal:
            hoststate.receive_start_train_signal = False
            if not hoststate.is_training:
                upload_is_training_status(True)
                train()
                # hoststate.is_training 设置成False是在train那个文件中
            else:
                print("当前存在训练，无法开启新的训练")
        time.sleep(10)



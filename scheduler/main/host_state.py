# -*- coding: utf-8 -*-

from info import getinfo

class HostState(object):
    def __init__(self,
                 uuid="0000",
                 disk_allocation_ratio=1,
                 name="nullName",
                 ip="0.0.0.0",
                 total_disk_gb=0,
                 total_memory_gb=0,
                 gpu_total_memory_gb=0,
                 cpu_max_freq=0,
                 time="1970-0-0 00:00:00",
                 cpu_percent=0,
                 used_disk_gb=0,
                 used_memory_gb=0,
                 gpu_used_memory_gb=0,
                 cpu_current_freq=0,
                 high_vul=0,
                 medium_vul=0,
                 low_vul=0,
                 info_vul=0,
                 model_size_mb=0,
                 loss=0.0,
                 accuracy=0.0,
                 # 显示的时候从0开始，存储的时候，是从1开始存储的，因为训练的时候26，101这样，为了每5次存储时首位都存储
                 epoch=-1):

        # 不变的基本信息
        self.uuid = uuid
        self.disk_allocation_ratio = disk_allocation_ratio
        self.name = name
        self.ip = ip

        # 以下是不变的跟变的对比
        # 磁盘使用量与总量
        self.total_disk_gb = total_disk_gb
        # 内存使用量与总量
        self.total_memory_gb = total_memory_gb
        # 此处默认第0个GPU
        self.gpu_total_memory_gb = gpu_total_memory_gb
        # CPU当前频率与总频率（某些cpu可以根据使用率自动调节倍频）
        self.cpu_max_freq = cpu_max_freq



        # 变的信息
        self.time = time
        self.cpu_percent = cpu_percent

        self.used_disk_gb = used_disk_gb
        self.used_memory_gb = used_memory_gb
        self.gpu_used_memory_gb = gpu_used_memory_gb
        self.cpu_current_freq = cpu_current_freq

        self.high_vul = high_vul
        self.medium_vul = medium_vul
        self.low_vul = low_vul
        self.info_vul = info_vul

        # 以下几个参数是随着机器学习而实时变化的
        self.model_size_mb = model_size_mb
        self.loss = loss
        self.accuracy = accuracy
        self.epoch = epoch
        self.is_aggregating = False
        self.is_training = False                    # 指示机器学习是否正在执行

        self.receive_start_train_signal = False     # 指示是否收到训练任务的信号，不需要被传入数据库

    def description(self):
            return """
                      时间：\(self.time)
                      cpu频率：   \(self.cpu_current_freq)GHz
                      cpu使用率： \(String(format:"%.2f", self.cpuPercent))%
                      磁盘分配率： \(String(format:"%.2f", self.diskAllocationRatio))
                      磁盘总量：   \(self.totalUsableDiskGB)GB
                      磁盘空闲总量：\(String(format:"%.2f", self.freeDiskGB))GB
                      空闲内存：   \(self.freeMemoryMB)MB
                      uuid：     \(self.uuid)
                      """


# 实现一个定期向数据库更新电脑参数数据
hoststate = HostState(uuid=getinfo.get_uuid(),
                      disk_allocation_ratio=1,
                      name=getinfo.get_name(),
                      ip=getinfo.get_ip(),
                      total_disk_gb=getinfo.get_total_disk_gb(),
                      gpu_total_memory_gb=getinfo.gpu_total_memory_gb(),
                      total_memory_gb=getinfo.get_total_memory_gb(),
                      cpu_max_freq=getinfo.get_cpu_max_freq(),
                      time=getinfo.get_time(),
                      cpu_percent=getinfo.get_cpu_percent(),
                      used_disk_gb=getinfo.get_used_disk_gb(),
                      used_memory_gb=getinfo.get_used_memory_gb(),
                      gpu_used_memory_gb=getinfo.gpu_used_memory_gb(),
                      cpu_current_freq=getinfo.get_cpu_current_freq())  # 另外的参数需要在其他地方更新


def update_basic_info():
    # 这些是需要更改的，有些参数不需要更改，我就不再更改了，比如当前IP，uuid等信息。
    hoststate.time = getinfo.get_time()
    hoststate.cpu_percent = getinfo.get_cpu_percent()

    hoststate.used_disk_gb = getinfo.get_used_disk_gb()
    hoststate.used_memory_gb = getinfo.get_used_memory_gb()
    hoststate.gpu_used_memory_gb = getinfo.gpu_used_memory_gb()
    hoststate.cpu_current_freq = getinfo.get_cpu_current_freq()


def update_model_size_mb(model_path):
    return getinfo.get_model_size(model_path)

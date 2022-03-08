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
        self.is_training = False  # 指示机器学习是否正在执行

        self.receive_start_train_signal = False  # 指示是否收到训练任务的信号，不需要被传入数据库
        self.receive_next_epoch_train_signal = False

    def description(self):
        return """
                     uuid: {uuid}
                     disk_allocation_ratio: {disk_allocation_ratio}
                     name: {name}
                     ip: {ip}
                     total_disk_gb: {total_disk_gb}
                     total_memory_gb: {total_memory_gb}
                     gpu_total_memory_gb: {gpu_total_memory_gb}
                     cpu_max_freq: {cpu_max_freq}
                     time: {time}
                     cpu_percent: {cpu_percent}
                     used_disk_gb: {used_disk_gb}
                     used_memory_gb: {used_memory_gb}
                     gpu_used_memory_gb: {gpu_used_memory_gb}
                     cpu_current_freq: {cpu_current_freq}
                     high_vul: {high_vul}
                     medium_vul: {medium_vul}
                     low_vul: {low_vul}
                     info_vul: {info_vul}
                     model_size_mb: {model_size_mb}
                     loss: {loss}
                     accuracy: {accuracy}
                     epoch: {epoch}
                   """.format(uuid=self.uuid,
                              disk_allocation_ratio=self.disk_allocation_ratio,
                              name=self.name,
                              ip=self.ip,
                              total_disk_gb=self.total_disk_gb,
                              total_memory_gb=self.total_memory_gb,
                              gpu_total_memory_gb=self.gpu_total_memory_gb,
                              cpu_max_freq=self.cpu_max_freq,
                              time=self.time,
                              cpu_percent=self.cpu_percent,
                              used_disk_gb=self.used_disk_gb,
                              used_memory_gb=self.used_memory_gb,
                              gpu_used_memory_gb=self.gpu_used_memory_gb,
                              cpu_current_freq=self.cpu_current_freq,
                              high_vul=self.high_vul,
                              medium_vul=self.medium_vul,
                              low_vul=self.low_vul,
                              info_vul=self.info_vul,
                              model_size_mb=self.model_size_mb,
                              loss=self.loss,
                              accuracy=self.accuracy,
                              epoch=self.epoch,
                              is_aggregating=self.is_aggregating,
                              is_training=self.is_training,
                              receive_start_train_signal=self.receive_start_train_signal)

    def short_description(self):
        return "name: {name} uuid: {uuid}".format(name=self.name, uuid=self.uuid)


def format_hoststate(datas):
    host_states = []

    for data in datas:
        # if data[23]:  # 如果该机器正在训练的话，那么这个主机是需要的
        host_states.append(HostState(data[0], data[1], data[2], data[3],
                                    data[4], data[5], data[6], data[7],
                                    data[8], data[9], data[10], data[11],
                                    data[12], data[13], data[14], data[15],
                                    data[16], data[17], data[18], data[19],
                                    data[20], data[21]))
    return host_states


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

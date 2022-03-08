# -*- coding: utf-8 -*-

import psutil
import socket
import uuid
# https://github.com/giampaolo/psutil
import time
import urllib.request
from json import load
import os

from pynvml import *

# def nvidia_info():
#     nvidia_dict = {
#         "state": True,
#         "nvidia_version": "",
#         "nvidia_count": 0,
#         "gpus": []
#     }
#     try:
#         nvmlInit()
#         nvidia_dict["nvidia_version"] = nvmlSystemGetDriverVersion().decode('utf-8')
#         nvidia_dict["nvidia_count"] = nvmlDeviceGetCount()
#         for i in range(nvidia_dict["nvidia_count"]):
#             handle = nvmlDeviceGetHandleByIndex(i)
#             memory_info = nvmlDeviceGetMemoryInfo(handle)
#             gpu = {
#                 "gpu_name": nvmlDeviceGetName(handle).decode('utf-8'),
#                 "total": memory_info.total,
#                 "free": memory_info.free,
#                 "used": memory_info.used,
#                 "temperature": f"{nvmlDeviceGetTemperature(handle, 0)}℃",
#                 "powerStatus": nvmlDeviceGetPowerState(handle)
#             }
#             nvidia_dict['gpus'].append(gpu)
#     except NVMLError as _:
#         nvidia_dict["state"] = False
#     except Exception as _:
#         nvidia_dict["state"] = False
#     finally:
#         try:
#             nvmlShutdown()
#         except:
#             pass
#     return nvidia_dict["gpus"][0]["used"], nvidia_dict["gpus"][0]["total"]

# 默认取第0个GPU
def gpu_used_memory_gb():
    try:
        nvmlInit()
        if nvmlDeviceGetCount() >= 1:
            handle = nvmlDeviceGetHandleByIndex(0)
            memory_info = nvmlDeviceGetMemoryInfo(handle)
            return memory_info.used / 1000 / 1000 / 1000
    except Exception as e:
        print(e)
    finally:
        try:
            nvmlShutdown()
        except:
            pass

    return 0.0

def gpu_total_memory_gb():
    try:
        nvmlInit()
        if nvmlDeviceGetCount() >= 1:
            handle = nvmlDeviceGetHandleByIndex(0)
            memory_info = nvmlDeviceGetMemoryInfo(handle)
            return memory_info.total / 1000 / 1000 / 1000
    except Exception as e:
        print(e)
    finally:
        try:
            nvmlShutdown()
        except:
            pass

    return 0.0


def get_model_size(model_path):
    if os.path.exists(model_path):
        return os.path.getsize(model_path) / 1000 / 1000  # MB

    return 0.00


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


# uuid1, 由MAC地址、当前时间戳、随机数生成。可以保证全球范围内的唯一性，但MAC的使用同时带来安全性问题，局域网中可以使用IP来代替MAC。
# uuid4, 随机
# 3和5，基于md5和sha1
def get_uuid():
    # return uuid.uuid1()
    # return uuid.uuid4()
    name = uuid.UUID(int=uuid.getnode()).hex[-12:]  # 这是mac地址，所以唯一了
    # uuida = uuid.uuid5(uuid.NAMESPACE_DNS, name)
    # uuidb = str(uuida).split('-')
    # uuidc = "".join(uuidb)
    # print(uuidc)
    return uuid.uuid5(uuid.NAMESPACE_DNS, name)


def get_mac_address():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0, 11, 2)])


# #获取本机电脑名
def get_name():
    # return socket.getfqdn(socket.gethostname())
    return socket.gethostname()


# #获取本机ip
def get_ip():
    return load(urllib.request.urlopen('http://jsonip.com'))['ip']
    # return socket.gethostbyname(get_name())


# 获取CPU的主要频率
def get_cpu_current_freq():
    return psutil.cpu_freq().current


def get_cpu_max_freq():
    return psutil.cpu_freq().max


# 获取使用的内存空间
def get_used_memory_gb():
    memory = psutil.virtual_memory()
    return (memory.total - memory.available) / 1000 / 1000 / 1000


def get_total_memory_gb():
    return psutil.virtual_memory().total / 1000 / 1000 / 1000


# 获取使用的磁盘空间
def get_used_disk_gb():
    return psutil.disk_usage('/').used / 1000 / 1000 / 1000  # 以GB结尾


# 获取磁盘的总容量
def get_total_disk_gb():
    return psutil.disk_usage('/').total / 1000 / 1000 / 1000


def get_cpu_percent():
     return psutil.cpu_percent()


if __name__ == '__main__':
    # print(get_used_memory_mb())
    print(get_model_size("dqwd"))

    # print(psutil.cpu_times())
    #
    # # CPU频率
    # print(psutil.cpu_current_freq().current)
    #
    # # print(psutil.virtual_memory())
    # # 系统内存的剩余内存
    # print(psutil.virtual_memory())
    # print(str(psutil.virtual_memory().free / 1024 / 1024 / 1024) + "G")
    #
    # print(psutil.disk_partitions())
    # print(psutil.disk_usage('/'))
    # print(psutil.disk_usage('/').free / 1000 / 1000 / 1000)
    #
    # # print(psutil.sensors_fans())
    #
    # print(psutil.net_io_counters(pernic=True))
    # print(psutil.net_if_addrs())
    #
    # # 电池百分比
    # print(psutil.sensors_battery().percent)
    # # for proc in psutil.process_iter(['pid', 'name']):
    # #     print(proc.info)
    #
    # # print(socket.getfqdn(socket.gethostname()))
    #
    # print(get_total_disk_gb())
    #
    # print(psutil.disk_usage('/'))
    #
    # print(get_ip())

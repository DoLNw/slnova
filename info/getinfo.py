import psutil
import socket
import uuid
# https://github.com/giampaolo/psutil

#与上次调用经过时间内的cpu的使用率
def get_cpu_percent():
    return psutil.cpu_percent(0.1)  # 会阻塞


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
    return socket.gethostbyname(get_name())

# print(get_mac_address())
# print(get_name())
# print(get_ip())



# 获取CPU的主要频率
def get_cpu_freq():
    return psutil.cpu_freq().current


# 获取空闲的磁盘空间
def get_free_memory_mb():
    return psutil.virtual_memory().free / 1024 / 1024  # 以MB结尾


# 获取磁盘的总容量
def get_total_usable_disk_gb():
    return psutil.disk_usage('/').free / 1024 / 1024 / 1024


if __name__ == '__main__':
    print(psutil.cpu_times())

    # CPU频率
    print(psutil.cpu_freq().current)

    # print(psutil.virtual_memory())
    # 系统内存的剩余内存
    print(psutil.virtual_memory())
    print(str(psutil.virtual_memory().free / 1024 / 1024 / 1024) + "G")

    print(psutil.disk_partitions())
    print(psutil.disk_usage('/'))
    print(psutil.disk_usage('/').free / 1024 / 1024 / 1024)

    # print(psutil.sensors_fans())

    print(psutil.net_io_counters(pernic=True))
    print(psutil.net_if_addrs())

    # 电池百分比
    print(psutil.sensors_battery().percent)
    # for proc in psutil.process_iter(['pid', 'name']):
    #     print(proc.info)

import psutil

# https://github.com/giampaolo/psutil

# 获取CPU的主要频率
def get_cpu_freq():
    return psutil.cpu_freq().current

# 获取空闲的磁盘空间
def get_free_disk():
    return psutil.virtual_memory().free / 1024 / 1024 # 以MB结尾

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
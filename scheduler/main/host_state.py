# -*- coding: utf-8 -*-


class HostState(object):
    def __init__(self, free_disk_gb=0, ip="0.0.0.0", name="nullName", isrunning=True, uuid="0000", cpufreq=0,
                 free_memory_mb=0, total_usable_disk_gb=0, disk_allocation_ratio=1, cpu_percent=0,
                 time="1970-0-0 00:00:00", high_vul=0, medium_vul=0, low_vul=0, info_vul=0):
        self.free_disk_gb = free_disk_gb
        self.isrunning = isrunning
        self.uuid = uuid
        self.cpufreq = cpufreq
        self.free_memory_mb = free_memory_mb
        self.total_usable_disk_gb = total_usable_disk_gb
        self.disk_allocation_ratio = disk_allocation_ratio
        self.cpu_percent = cpu_percent
        self.name = name
        self.ip = ip
        self.time = time
        self.high_vul = high_vul
        self.medium_vul = medium_vul
        self.low_vul = low_vul
        self.info_vul = info_vul

    def description(self):
            return """
                      时间：\(self.time)
                      是否正在运行：\(self.isRunning)
                      cpu频率：   \(self.cpuFreq)GHz
                      cpu使用率： \(String(format:"%.2f", self.cpuPercent))%
                      磁盘分配率： \(String(format:"%.2f", self.diskAllocationRatio))
                      磁盘总量：   \(self.totalUsableDiskGB)GB
                      磁盘空闲总量：\(String(format:"%.2f", self.freeDiskGB))GB
                      空闲内存：   \(self.freeMemoryMB)MB
                      uuid：     \(self.uuid)
                      """
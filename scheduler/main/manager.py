# -*- coding: utf-8 -*-


import sys
sys.path.append("..")

import conf

from scheduler.main import filter_scheduler

CONF = conf.CONF


# 规定，定义的时候，上面需要两个空行
# 总的调度管理者
class SchedulerManager(object):
    def __init__(self):
        # print("%d %s     %-20s   %-30s" % (1, "func", "manager.py", "SchedulerManager __init__"))

        # 所以此处直接使用FilterScheduler的实例了，本来是需要选择一下的
        # 获取到调度的调度器，本来要通过conf的配置选择的，我此处直接选定了
        self.driver = filter_scheduler.FilterScheduler()

    def select_destinations(self):
        # print("%d %s     %-20s   %-30s" % (1, "func", "manager.py", "select_destinations"))

        # 调用选定的FilterScheduler，来进行调度，选择最合适的主机，返回的结果从大到小排序
        dests = self.driver.select_destinations()
        return dests


if __name__ == '__main__':
    schedulerManager = SchedulerManager()
    dest = schedulerManager.select_destinations()
    print("\n最后得到的所有的个数： " + str(len(dest)) + "\n")
    for hostState in dest:
        print(hostState.short_description())

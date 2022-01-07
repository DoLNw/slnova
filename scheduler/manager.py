import sys
sys.path.append("/Users/jc")

from stevedore import driver
import slnova.conf

from slnova.scheduler import filter_scheduler

CONF = slnova.conf.CONF

# 总的调度管理者
class SchedulerManager(object):
    def __init__(self):
        print("1 func" + "      " + "manager.py" + "      " + "SchedulerManager __init__")
        scheduler_driver = CONF.scheduler.driver
        # 此处直接加了包，然后添加进这个FilterScheduler了，用官方的有问题
        # self.driver = driver.DriverManager(
        #     "slnova.scheduler.driver",
        #     scheduler_driver,
        #     invoke_on_load=True).driver
        # 所以此处直接使用FilterScheduler的实例了，本来是需要选择一下的
        # 获取到调度的调度器，本来要通过conf的配置选择的，我此处直接选定了
        self.driver = filter_scheduler.FilterScheduler()

    def select_destinations(self):
        print("1 func" + "      " + "manager.py" + "      " + "select_destinations")
        # 调用选定的FilterScheduler，来进行调度，选择最合适的主机，返回的结果从大到小排序
        dests = self.driver.select_destinations()
        return dests


if __name__ == '__main__':
    schedulerManager = SchedulerManager()
    dest  = schedulerManager.select_destinations()
    print(len(dest))
    for hostState in dest:
        print(hostState.cpufreq)
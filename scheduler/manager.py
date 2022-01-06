import sys
sys.path.append("/Users/jc")

from stevedore import driver
import slnova.conf
from slnova.scheduler import filter_scheduler

CONF = slnova.conf.CONF

class SchedulerManager(object):
    def __init__(self):
        print("func" + "      " + "manager.py" + "      " + "SchedulerManager __init__")
        scheduler_driver = CONF.scheduler.driver
        # self.driver = driver.DriverManager(
        #     "slnova.scheduler.driver",
        #     scheduler_driver,
        #     invoke_on_load=True).driver
        self.driver = filter_scheduler.FilterScheduler()

    def select_destinations(self):
        print("func" + "      " + "manager.py" + "      " + "select_destinations")
        dests = self.driver.select_destinations()
        return dests


if __name__ == '__main__':
    schedulerManager = SchedulerManager()
    schedulerManager.select_destinations()
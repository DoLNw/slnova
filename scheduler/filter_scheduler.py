import sys
sys.path.append("/Users/jc")

import slutils
from slnova.scheduler import driver

# 基于Scheduler实现的调度类，用这个类来进行调度
class FilterScheduler(driver.Scheduler):
    def __init__(self, *args, **kwargs):
        super(FilterScheduler, self).__init__(*args, **kwargs)
        print("func" + "      " + "filter_scheduler" + "      " + "FilterScheduler __init__")

    def select_destinations(self):
        print("2 func" + "      " + "filter_scheduler" + "      " + "select_destinations")
        """Returns a sorted list of HostState objects that satisfy the
                supplied request_spec.
        """
        # 调用自身的方法，进行调度选择
        selected_hosts = self._schedule()
        return selected_hosts

    def _schedule(self):
        print("2 func" + "      " + "filter_scheduler" + "      " + "_schedule")
        """Returns a list of hosts that meet the required specs, ordered by
                their fitness.
        """
        # 调用自身的的方法，获取所有的主机的各种状态，hosts是HostState的列表类型
        hosts = self._get_all_host_states()
        # 调用自身方法，获得排序结果（筛选加称重）
        hosts = self._get_sorted_hosts(hosts)

        return hosts

    def _get_all_host_states(self):
        print("func" + "      " + "filter_scheduler" + "      " + "_get_all_host_states")
        # 调用host_manager的方法，获取所有主机的各种状态
        return self.host_manager.get_all_host_states()

    def _get_sorted_hosts(self, host_states):
        print("func" + "      " + "filter_scheduler" + "      " + "_get_sorted_hosts")
        # 调用host_manager的方法，获取筛选过后的主机
        filtered_hosts = self.host_manager.get_filtered_hosts(host_states)
        # 获取称重过后的主机
        weighed_hosts = self.host_manager.get_weighed_hosts(filtered_hosts)
        # 称重过后得到的类型不是[HostState]，所以下面转换
        weighed_hosts = [h.obj for h in weighed_hosts]

        return weighed_hosts
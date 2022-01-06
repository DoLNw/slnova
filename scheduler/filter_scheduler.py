import sys
sys.path.append("/Users/jc")

import slutils
from slnova.scheduler import driver

class FilterScheduler(driver.Scheduler):
    def __init__(self, *args, **kwargs):
        super(FilterScheduler, self).__init__(*args, **kwargs)
        print("func" + "      " + "filter_scheduler" + "      " + "FilterScheduler __init__")

    def select_destinations(self):
        print("func" + "      " + "filter_scheduler" + "      " + "select_destinations")
        """Returns a sorted list of HostState objects that satisfy the
                supplied request_spec.
        """
        selected_hosts = self._schedule()
        return selected_hosts

    def _schedule(self):
        print("func" + "      " + "filter_scheduler" + "      " + "_schedule")
        """Returns a list of hosts that meet the required specs, ordered by
                their fitness.
        """
        hosts = self._get_all_host_states()
        hosts = self._get_sorted_hosts(hosts)

        return hosts

    def _get_all_host_states(self):
        print("func" + "      " + "filter_scheduler" + "      " + "_get_all_host_states")
        return self.host_manager.get_all_host_states()

    def _get_sorted_hosts(self, host_states):
        print("func" + "      " + "filter_scheduler" + "      " + "_get_sorted_hosts")
        filtered_hosts = self.host_manager.get_filtered_hosts(host_states)
        weighed_hosts = self.host_manager.get_weighed_hosts(filtered_hosts)

        return weighed_hosts
import sys
sys.path.append("/Users/jc")

import slutils
import slnova.conf
from slnova.scheduler import filters
from slnova.scheduler import weights
from slnova import exception

CONF = slnova.conf.CONF

# class HostState(object):
    # def __init__(self):

class HostManager(object):
    def __init__(self):
        print("func" + "      " + "host_manager.py" + "      " + "HostManager __init__")
        self.filter_handler = filters.HostFilterHandler()
        filter_classes = self.filter_handler.get_matching_classes(
            CONF.filter_scheduler.available_filters)
        self.filter_cls_map = {cls.__name__: cls for cls in filter_classes}
        self.filter_obj_map = {}
        self.enabled_filters = self._choose_host_filters(self._load_filters())

        self.weight_handler = weights.HostWeightHandler()
        weigher_classes = self.weight_handler.get_matching_classes(
            CONF.filter_scheduler.weight_classes)
        self.weighers = [cls() for cls in weigher_classes]

    def get_all_host_states(self):
        print("func" + "      " + "host_manager.py" + "      " + "get_all_host_states")
        """Returns a generator of HostStates that represents all the hosts
        the HostManager knows about. Also, each of the consumable resources
        in HostState are pre-populated and adjusted based on data in the db.
        """
        return self._get_host_states()

    def _get_host_states(self):
        print("func" + "      " + "host_manager.py" + "      " + "_get_host_states")
        return []

    def get_filtered_hosts(self, host_states):
        print("func" + "      " + "host_manager.py" + "      " + "get_filtered_hosts")
        aa = 12
    def get_weighed_hosts(self, filtered_hosts):
        print("func" + "      " + "host_manager.py" + "      " + "get_weighed_hosts")
        aa = 12


    def _load_filters(self):
        print("func" + "      " + "host_manager.py" + "      " + "_load_filters")
        return CONF.filter_scheduler.enabled_filters

    def _choose_host_filters(self, filter_cls_names):
        print("func" + "      " + "host_manager.py" + "      " + "_choose_host_filters")
        """Since the caller may specify which filters to use we need
        to have an authoritative list of what is permissible. This
        function checks the filter names against a predefined set
        of acceptable filters.
        """
        if not isinstance(filter_cls_names, (list, tuple)):
            filter_cls_names = [filter_cls_names]

        good_filters = []
        bad_filters = []
        for filter_name in filter_cls_names:
            if filter_name not in self.filter_obj_map:
                if filter_name not in self.filter_cls_map:
                    bad_filters.append(filter_name)
                    continue
                filter_cls = self.filter_cls_map[filter_name]
                self.filter_obj_map[filter_name] = filter_cls()
            good_filters.append(self.filter_obj_map[filter_name])
        if bad_filters:
            msg = ", ".join(bad_filters)
            raise exception.SchedulerHostFilterNotFound(filter_name=msg)
        return good_filters




if __name__ == '__main__':
    slutils.get_current_module()
    print(CONF.filter_scheduler.available_filters)
    hostManager = HostManager()
    # print(hostManager.filter_classes)
    print(hostManager.weight_handler)






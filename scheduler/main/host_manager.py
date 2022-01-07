import slnova.conf

from slnova.scheduler import filters
from slnova.scheduler import weights
from slnova.scheduler import exception
from slnova.info import getinfo

CONF = slnova.conf.CONF


class HostState(object):
    def __init__(self, cpufreq=0, free_disk_mb=0, total_usable_disk_gb=0):
        self.cpufreq = cpufreq
        self.free_disk_mb = free_disk_mb
        self.total_usable_disk_gb = total_usable_disk_gb
        self.disk_allocation_ratio = 1

    def description(self):
            return ("cpufreq: %-5d, free_disk_mb: %-8d, total_usable_disk_gb: %-3d, disk_allocation_ratio: %-.2f" % (self.cpufreq, self.free_disk_mb, self.total_usable_disk_gb, 1))


        # 规定：定义的时候，上面需要两个空行
class HostManager(object):
    def __init__(self):
        print("%d %s     %-20s   %-30s" % (2, "func", "host_manager.py", "HostManager __init__"))

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
        print("%d %s     %-20s   %-30s" % (4, "func", "host_manager.py", "get_all_host_states"))
        """Returns a generator of HostStates that represents all the hosts
        the HostManager knows about. Also, each of the consumable resources
        in HostState are pre-populated and adjusted based on data in the db.
        """

        return self._get_host_states()

    def _get_host_states(self):
        print("%d %s     %-20s   %-30s" % (4, "func", "host_manager.py", "_get_host_states"))

        # hostState = HostState()
        # hostState.cpufreq = getinfo.get_cpu_freq()
        host12 = HostState(12, 60, 100)
        host100 = HostState(100, 12, 100)
        host9 = HostState(9, 19, 100)

        return [host12, host100, host9]

    def get_filtered_hosts(self, host_states):
        """Filter hosts and return only ones passing all filters."""
        print("%d %s     %-20s   %-30s" % (4, "func", "host_manager.py", "get_filtered_hosts"))

        return self.filter_handler.get_filtered_objects(self.enabled_filters, host_states)

    def get_weighed_hosts(self, filtered_hosts):
        print("%d %s     %-20s   %-30s" % (4, "func", "host_manager.py", "get_weighed_hosts"))

        return self.weight_handler.get_weighed_objects(self.weighers, filtered_hosts)

    def _load_filters(self):
        print("%d %s     %-20s   %-30s" % (2, "func", "host_manager.py", "_load_filters"))
        return CONF.filter_scheduler.enabled_filters

    def _choose_host_filters(self, filter_cls_names):
        print("%d %s     %-20s   %-30s" % (2, "func", "host_manager.py", "_choose_host_filters"))
        """Since the caller may specify which filters to use we need
        to have an authoritative list of what is permissible. This
        function checks the filter names against a predefined set
        of acceptable filters.
        """
        # 返回所有可用的过滤器名称和对应的过滤器类
        # 过滤器采用了插件模式,我们可以自定义过滤器,只需要将文件放入nova/scheduler/filters下面,
        # 那么就可以通过配置选项scheduler_default_filters来使用其中的过滤器
        # 每当nova-scheduler开始运行, 它就会自动在该目录下加载过滤器

        if not isinstance(filter_cls_names, (list, tuple)):
            filter_cls_names = [filter_cls_names]

        # 我们可能会因为手误配置了不存在的调度器名, 那么下面就是对要使用的过滤器进行验证,
        # 以杜绝这种错误的发生
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

import conf

from oslo_log import log as logging

from scheduler import filters

LOG = logging.getLogger(__name__)

CONF = conf.CONF


class GPURamFilter(filters.BaseHostFilter):

    RUN_ON_REBUILD = False

    def host_passes(self, host_state):
        requested_gpu_ram_gb = 10            # 一个主机传递1g模型参数，最多10个，因为计算的时候有偏差1024还是1000

        if host_state.gpu_total_memory_gb < requested_gpu_ram_gb:
            return False

        return True

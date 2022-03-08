import conf

from scheduler import weights

CONF = conf.CONF

class MemoryRamWeigher(weights.BaseHostWeigher):
    # 权重
    def weight_multiplier(self):
        """Override the weight multiplier."""
        return CONF.filter_scheduler.gpu_ram_weight_multiplier

    # 返回哪一个参数进行计算
    def _weigh_object(self, host_state):
        """Higher weights win.  We want spreading to be the default."""
        return host_state.gpu_total_memory_gb



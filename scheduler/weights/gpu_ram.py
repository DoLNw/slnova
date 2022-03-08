import conf

from scheduler import weights

CONF = conf.CONF


class GPURamWeigher(weights.BaseHostWeigher):
    # 权重
    def weight_multiplier(self):
        """Override the weight multiplier."""
        return CONF.filter_scheduler.memory_weight_multiplier

    # 返回哪一个参数进行计算
    def _weigh_object(self, host_state):
        """Higher weights win.  We want spreading to be the default."""
        return host_state.total_memory_gb

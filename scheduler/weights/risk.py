import conf

from scheduler import weights

CONF = conf.CONF


class RiskRamWeigher(weights.BaseHostWeigher):
    # 权重
    def weight_multiplier(self):
        """Override the weight multiplier."""
        return CONF.filter_scheduler.risk_weight_multiplier

    # 返回哪一个参数进行计算
    def _weigh_object(self, host_state):
        """Higher weights win.  We want spreading to be the default."""
        all_vul = host_state.info_vul + host_state.low_vul + host_state.medium_vul + host_state.high_vul

        if all_vul != 0:
            return host_state.high_vul / all_vul * 1.0 + host_state.medium_vul / all_vul * 0.7 \
                   + host_state.low_vul / all_vul * 0.4
        return 0
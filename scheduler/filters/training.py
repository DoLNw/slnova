import conf

from oslo_log import log as logging

from scheduler import filters

LOG = logging.getLogger(__name__)

CONF = conf.CONF


class TrainingRamFilter(filters.BaseHostFilter):

    RUN_ON_REBUILD = False

    def host_passes(self, host_state):
        if not host_state.is_training:
            return False

        return True
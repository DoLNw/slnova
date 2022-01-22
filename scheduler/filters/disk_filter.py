# Copyright (c) 2012 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import slnova.conf

from oslo_log import log as logging

from slnova.scheduler import filters
# from slnova.i18n import _LW
# from slnova.scheduler.filters import utils

LOG = logging.getLogger(__name__)

CONF = slnova.conf.CONF


class DiskFilter(filters.BaseHostFilter):
    """Disk Filter with over subscription flag."""

    RUN_ON_REBUILD = False

    # spec_obj: 在官方文档里面是class RequestSpec(base.NovaObject)
    def _get_disk_allocation_ratio(self, host_state):
        return host_state.disk_allocation_ratio

    # 实现如何过滤，怎么算符合
    def host_passes(self, host_state):
        """Filter based on disk usage."""
        # 计算出请求得到的容量
        # requested_disk = (1024 * (spec_obj.root_gb +
        #                           spec_obj.ephemeral_gb) +
        #                   spec_obj.swap)
        requested_disk_mb = 20 * 1024

        free_disk_mb = host_state.free_disk_gb * 1024
        # 总共的容量
        total_usable_disk_mb = host_state.total_usable_disk_gb * 1024

        # Do not allow an instance to overcommit against itself, only against
        # other instances.  In other words, if there isn't room for even just
        # this one instance in total_usable_disk space, consider the host full.
        # 磁盘总容量需要大于请求容量，否则不符合
        if total_usable_disk_mb < requested_disk_mb:
            LOG.debug("%(host_state)s does not have %(requested_disk)s "
                      "MB usable disk space before overcommit, it only "
                      "has %(physical_disk_size)s MB.",
                      {'host_state': host_state,
                       'requested_disk': requested_disk_mb,
                       'physical_disk_size':
                           total_usable_disk_mb})
            return False

        # 应该是磁盘分配比例把，默认给1得了
        disk_allocation_ratio = self._get_disk_allocation_ratio(host_state)

        # 总共可使用的容量
        disk_mb_limit = total_usable_disk_mb * disk_allocation_ratio
        used_disk_mb = total_usable_disk_mb - free_disk_mb   # 已经使用掉的磁盘容量
        usable_disk_mb = disk_mb_limit - used_disk_mb

        # 计算出来的可用>=请求的，则满足，否则不满足
        if usable_disk_mb < requested_disk_mb:
            LOG.debug("%(host_state)s does not have %(requested_disk)s MB "
                    "usable disk, it only has %(usable_disk_mb)s MB usable "
                    "disk.", {'host_state': host_state,
                               'requested_disk': requested_disk_mb,
                               'usable_disk_mb': usable_disk_mb})
            return False

        # disk_gb_limit = disk_mb_limit / 1024
        # host_state.limits['disk_gb'] = disk_gb_limit
        return True


# class AggregateDiskFilter(DiskFilter):
#     """AggregateDiskFilter with per-aggregate disk allocation ratio flag.
#
#     Fall back to global disk_allocation_ratio if no per-aggregate setting
#     found.
#     """
#
#     RUN_ON_REBUILD = False
#
#     def _get_disk_allocation_ratio(self, host_state, spec_obj):
#         aggregate_vals = utils.aggregate_values_from_key(
#             host_state,
#             'disk_allocation_ratio')
#         try:
#             ratio = utils.validate_num_values(
#                 aggregate_vals, host_state.disk_allocation_ratio,
#                 cast_to=float)
#         except ValueError as e:
#             LOG.warning(_LW("Could not decode disk_allocation_ratio: '%s'"), e)
#             ratio = host_state.disk_allocation_ratio
#
#         return ratio

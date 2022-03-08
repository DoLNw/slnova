# -*- coding: utf-8 -*-
#
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

import conf

from oslo_log import log as logging

from scheduler import filters
# from i18n import _LW
# from scheduler.filters import utils

LOG = logging.getLogger(__name__)

CONF = conf.CONF


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
        requested_disk_gb = 1.0 * 10            # 一个主机传递1g模型参数，最多10个

        # Do not allow an instance to overcommit against itself, only against
        # other instances.  In other words, if there isn't room for even just
        # this one instance in total_usable_disk space, consider the host full.
        # 磁盘总容量需要大于请求容量，否则不符合
        if host_state.total_disk_gb < requested_disk_gb:
            LOG.debug("%(host_state)s does not have %(requested_disk)s "
                      "GB usable disk space before overcommit, it only "
                      "has %(physical_disk_size)s GB.",
                      {'host_state': host_state,
                       'requested_disk': requested_disk_gb,
                       'physical_disk_size':
                           host_state.total_disk_gb})
            return False

        # 总共可使用的容量
        usable_disk_gb = host_state.total_disk_gb - host_state.used_disk_gb

        # 计算出来的可用>=请求的，则满足，否则不满足
        if usable_disk_gb < requested_disk_gb:
            LOG.debug("%(host_state)s does not have %(requested_disk)s GB "
                    "usable disk, it only has %(usable_disk_mb)s GB usable "
                    "disk.", {'host_state': host_state,
                               'requested_disk': requested_disk_gb,
                               'usable_disk_mb': usable_disk_gb})
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

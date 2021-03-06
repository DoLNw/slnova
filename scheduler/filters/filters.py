# -*- coding: utf-8 -*-
#
# Copyright (c) 2011-2012 OpenStack Foundation
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

"""
Filter support
"""

from oslo_log import log as logging

from scheduler.i18n import _LI
from scheduler import loadables

LOG = logging.getLogger(__name__)


class BaseFilter(object):
    """Base class for all filter classes."""
    # 一个的过滤过程
    def _filter_one(self, obj):
        """Return True if it passes the filter, False otherwise.
        Override this in a subclass.
        """
        return True

    def filter_all(self, filter_obj_list):
        """Yield objects that pass the filter.

        Can be overridden in a subclass, if you need to base filtering
        decisions on all objects.  Otherwise, one can just override
        _filter_one() to filter a single object.
        """
        for obj in filter_obj_list:
            if self._filter_one(obj):
                yield obj            # yield可以用next一次次的迭代出来


# 处理类，获取所有需要的过滤器，并且过滤
class BaseFilterHandler(loadables.BaseLoader):
    """Base class to handle loading filter classes.

    This class should be subclassed where one needs to use filters.
    """

    def get_filtered_objects(self, filters, objs):
        # objs指待过滤的多个HostState，不懂为啥下面还需要list一下
        # print(objs[0].__class__)
        # print(objs.__class__)
        list_objs = list(objs)
        LOG.debug("Starting with %d host(s)", len(list_objs))
        print("\nStarting filters with {} host(s) ...".format(len(list_objs)))
        # Track the hosts as they are removed. The 'full_filter_results' list
        # contains the host/nodename info for every host that passes each
        # filter, while the 'part_filter_results' list just tracks the number
        # removed by each filter, unless the filter returns zero hosts, in
        # which case it records the host/nodename for the last batch that was
        # removed. Since the full_filter_results can be very large, it is only
        # recorded if the LOG level is set to debug.
        # full_filter_results指过滤成功的主机
        # part_filter_results指被过滤掉的主机
        # 只有当full_filter_results为0时，part_filter_results才会被记录
        part_filter_results = []
        full_filter_results = []
        log_msg = "%(cls_name)s: (start: %(start)s, end: %(end)s)"
        for filter_ in filters:  # 对于每一个都需要过滤
            cls_name = filter_.__class__.__name__
            start_count = len(list_objs)
            # 对每个list_obj进行_filter_one过滤, _filter_one实际会调用host_passes进行真正的过滤操作
            # 因此, 每个过滤器类只需要继承BaseHostFilter类并实现host_passes方法即可,
            # 这里会返回一个生成器对象
            objs = filter_.filter_all(list_objs)
            if objs is None:
                LOG.debug("Filter %s says to stop filtering", cls_name)
                return
            list_objs = list(objs)
            end_count = len(list_objs)
            part_filter_results.append(log_msg % {"cls_name": cls_name, "start": start_count, "end": end_count})
            if list_objs:
                remaining = [(getattr(obj, "host", obj),
                              getattr(obj, "nodename", ""))
                             for obj in list_objs]
                full_filter_results.append((cls_name, remaining))
            else:
                # 如果在该过滤器运行之后,没有list_obj通过过滤,
                # 那么就不需要运行剩余的过滤器了
                LOG.info(_LI("Filter %s returned 0 hosts"), cls_name)
                full_filter_results.append((cls_name, None))
                break
            LOG.debug("Filter %(cls_name)s returned " 
                      "%(obj_len)d host(s)",
                      {'cls_name': cls_name, 'obj_len': len(list_objs)})

        # 返回最终通过所有过滤的list_obj
        return list_objs

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
Pluggable Weighing support
"""

import abc
import six

from scheduler import loadables


# 参数归一化
def normalize(weight_list, minval=None, maxval=None):
    """Normalize the values in a list between 0 and 1.0.

    The normalization is made regarding the lower and upper values present in
    weight_list. If the minval and/or maxval parameters are set, these values
    will be used instead of the minimum and maximum from the list.

    If all the values are equal, they are normalized to 0.
    """

    if not weight_list:
        return ()

    if maxval is None:
        maxval = max(weight_list)

    if minval is None:
        minval = min(weight_list)

    maxval = float(maxval)
    minval = float(minval)

    if minval == maxval:
        return [0] * len(weight_list)

    range_ = maxval - minval
    return ((i - minval) / range_ for i in weight_list)


# 取到该HostState对应要称重的weight的参数
class WeighedObject(object):
    """Object with weight information."""
    def __init__(self, obj, weight):
        self.obj = obj
        self.weight = weight

    def __repr__(self):
        return "<WeighedObject '%s': %s>" % (self.obj, self.weight)


@six.add_metaclass(abc.ABCMeta)
class BaseWeigher(object):
    """Base class for pluggable weighers.

    The attributes maxval and minval can be specified to set up the maximum
    and minimum values for the weighed objects. These values will then be
    taken into account in the normalization step, instead of taking the values
    from the calculated weights.
    """

    minval = None
    maxval = None

    # 返回权重
    def weight_multiplier(self):
        """How weighted this weigher should be.

        Override this method in a subclass, so that the returned value is
        read from a configuration option to permit operators specify a
        multiplier for the weigher.
        """
        return 1.0

    # 得到某个主机中需要称重的参数
    @abc.abstractmethod
    def _weigh_object(self, obj):
        """Weigh an specific object."""

    # 得到各个主机中需要称重的参数
    def weigh_objects(self, weighed_obj_list):
        """Weigh multiple objects.

        Override in a subclass if you need access to all objects in order
        to calculate weights. Do not modify the weight of an object here,
        just return a list of weights.
        """
        # Calculate the weights
        weights = []
        for obj in weighed_obj_list:
            weight = self._weigh_object(obj.obj)   # weight为每一个HostState想要比较的参数

            # Record the min and max values if they are None. If they are
            # anything but none, we assume that the weigher had set them.
            if self.minval is None:
                self.minval = weight
            if self.maxval is None:
                self.maxval = weight

            if weight < self.minval:
                self.minval = weight
            elif weight > self.maxval:
                self.maxval = weight

            weights.append(weight)

        return weights


# 处理类，获取到所有需要的称重器并且称重
class BaseWeightHandler(loadables.BaseLoader):
    object_class = WeighedObject

    def get_weighed_objects(self, weighers, obj_list):
        """Return a sorted (descending), normalized list of WeighedObjects."""
        # print(obj_list[0].__class__)
        # obj_list是list类型的，元素为HostState
        weighed_objs = [self.object_class(obj, 0.0) for obj in obj_list]
        # weighed_objs是list类型的，元素为WeighedHost
        # print(weighed_objs[0].__class__)
        print("\nStarting weights with {} host(s) ...".format(len(obj_list)))

        # # 只有1个HostState的话直接返回就行了
        # if len(weighed_objs) <= 1:
        #     return weighed_objs

        # 用各个称重类进行处理
        for weigher in weighers:
            weights = weigher.weigh_objects(weighed_objs)  # 对于每一个称重的类，取出各个HostState的需要比较的参数

            # Normalize the weights，把需要比较的参数正则化（每一个称重类应该是比较一个参数的）
            weights = normalize(weights,
                                minval=weigher.minval,
                                maxval=weigher.maxval)

            # 注意，这里面的obj就是HostState加weight，类型为WeightHost
            for i, weight in enumerate(weights):
                obj = weighed_objs[i]
                obj.weight += weigher.weight_multiplier() * weight

        # 估计reverse之后是从大到小吧
        return sorted(weighed_objs, key=lambda x: x.weight, reverse=True)

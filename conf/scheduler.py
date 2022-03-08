# -*- coding: utf-8 -*-
#
# Copyright 2015 OpenStack Foundation
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

from oslo_config import cfg


filter_scheduler_group = cfg.OptGroup(name="filter_scheduler", title="Filter scheduler options")

filter_scheduler_opts = [
    cfg.MultiStrOpt("available_filters",
        default=["scheduler.filters.all_filters"],
        deprecated_name="scheduler_available_filters",
        deprecated_group="DEFAULT",
        help=""" """),
    cfg.ListOpt("enabled_filters",
        default=[
          # "RetryFilter",
          # "AvailabilityZoneFilter",
          # "ComputeFilter",
          # "ComputeCapabilitiesFilter",
          # "ImagePropertiesFilter",
          # "ServerGroupAntiAffinityFilter",
          # "ServerGroupAffinityFilter",
            "DiskFilter",
            "GPURamFilter",
          ],
        deprecated_name="scheduler_default_filters",
        deprecated_group="DEFAULT",
        help=""" """),


    cfg.ListOpt("weight_classes",
        default=["scheduler.weights.all_weighers"],
        deprecated_name="scheduler_weight_classes",
        deprecated_group="DEFAULT",
        help=""" """),
    cfg.FloatOpt("gpu_ram_weight_multiplier",
        default=1.0,
        deprecated_group="DEFAULT",
        help=""" """),
    cfg.FloatOpt("disk_weight_multiplier",
        default=1.0,
        deprecated_group="DEFAULT",
        help=""" """),
    cfg.FloatOpt("risk_weight_multiplier",
        default=1.0,
        deprecated_group="DEFAULT",
        help=""" """),
    cfg.FloatOpt("memory_weight_multiplier",
        default=1.0,
        deprecated_group="DEFAULT",
        help=""" """),
]


def register_opts(conf):
    conf.register_group(filter_scheduler_group)
    conf.register_opts(filter_scheduler_opts, group=filter_scheduler_group)


def list_opts():
    return {filter_scheduler_group: filter_scheduler_opts}

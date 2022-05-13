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

# This package got introduced during the Mitaka cycle in 2015 to
# have a central place where the config options of Nova can be maintained.
# For more background see the blueprint "centralize-config-options"

from oslo_config import cfg

from conf import scheduler
from conf import myinfo
from conf import rabbitmq
from conf import magface_pyt
from conf import STN_mxnet
from conf import mnist

CONF = cfg.CONF

scheduler.register_opts(CONF)
myinfo.register_opts(CONF)
rabbitmq.register_opts(CONF)
magface_pyt.register_opts(CONF)
STN_mxnet.register_opts(CONF)
mnist.register_opts(CONF)

# remote_debug.register_cli_opts(CONF)

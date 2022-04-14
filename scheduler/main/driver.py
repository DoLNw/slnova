# -*- coding: utf-8 -*-
#
# Copyright (c) 2010 OpenStack Foundation
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
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
Scheduler base class that all Schedulers should inherit from
"""

import conf

from scheduler.main import host_manager

CONF = conf.CONF


# 调度器父类
class Scheduler(object):
    """The base class that all Scheduler classes should inherit from."""

    def __init__(self):
        # print("%d %s     %-20s   %-30s" % (2, "func", "driver.py", "Scheduler __init__"))

        # 本来可以通过driver.DriverManager获取conf指定的host_manager的，现在我直接给它指定成HostManager了
        self.host_manager = host_manager.HostManager()

    def select_destinations(self):
        # print("%d %s     %-20s   %-30s" % (2, "func", "driver.py", "select_destinations"))
        """Returns a list of HostState objects that have been chosen by the
        scheduler driver, one for each requested instance
        (spec_obj.num_instances)
        """
        return []


if __name__ == '__main__':
    scheduler = Scheduler()

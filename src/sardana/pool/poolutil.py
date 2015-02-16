#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""Pool utils"""

__all__ = ["PoolUtil"]

__docformat__ = 'restructuredtext'

from taurus.core.util.containers import CaselessDict


class _PoolUtil(object):

    def __init__(self):
        self._ctrl_proxies = CaselessDict()

    def __call__(self, *args, **kwargs):
        return self

    def get_device(self, *args, **kwargs):
        ctrl_name = args[0]
        device_name = args[1]
        ctrl_devs = self._ctrl_proxies.get(ctrl_name)
        if ctrl_devs is None:
            self._ctrl_proxies[ctrl_name] = ctrl_devs = CaselessDict()
        dev = ctrl_devs.get(device_name)
        if dev is None:
            import PyTango
            ctrl_devs[device_name] = dev = PyTango.DeviceProxy(device_name)
        return dev

    get_motor = get_phy_motor = get_pseudo_motor = get_motor_group = \
        get_exp_channel = get_ct_channel = get_zerod_channel = get_oned_channel = \
        get_twod_channel = get_pseudo_counter_channel = get_measurement_group = \
        get_com_channel = get_ioregister = get_device

PoolUtil = _PoolUtil()

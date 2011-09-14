#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
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

""" """

__all__ = ["SardanaDevice", "SardanaDeviceClass"]

__docformat__ = 'restructuredtext'

from PyTango import Device_4Impl, DeviceClass, Util

from taurus.core.util.log import Logger

class SardanaDevice(Device_4Impl, Logger):
    
    def __init__(self, dclass, name):
        Device_4Impl.__init__(self, dclass, name)
        self.init(name)
        if self._alias:
            name = "Tango_%s" % self.alias
        Logger.__init__(self, name)
        
    def init(self, name):
        util = Util.instance()
        db = util.get_database()
        try:
            
            self._alias = db.get_alias(name)
            if self._alias.lower() == 'nada':
                self._alias = None
        except:
            self._alias = None
    
    @property
    def alias(self):
        return self._alias

    def init_device(self):
        self.get_device_properties(self.get_device_class())

        detect_evts = "state", "status"
        non_detect_evts = ()
        self.set_change_events(detect_evts, non_detect_evts)

    def set_change_events(self, evts_checked_by_tango, evts_not_checked_by_tango):
        for evt in evts_checked_by_tango:
            self.set_change_event(evt, True, True)
        for evt in evts_not_checked_by_tango:
            self.set_change_event(evt, True, False)

    def initialize_dynamic_attributes(self):
        pass
    

class SardanaDeviceClass(DeviceClass):

    #    Class Properties
    class_property_list = {}

    #    Device Properties
    device_property_list = {
    }

    #    Command definitions
    cmd_list = {
    }

    #    Attribute definitions
    attr_list = {
    }

    def dyn_attr(self, dev_list):
        for dev in dev_list:
            try:
                dev.initialize_dynamic_attributes()
            except:
                dev.warning("Failed to initialize dynamic attributes",
                            exc_info=1)


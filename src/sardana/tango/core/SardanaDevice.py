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

import threading

from PyTango import Device_4Impl, DeviceClass, Util, DevState, \
    AttrQuality, TimeVal, ArgType

from taurus.core.util.log import Logger

from util import to_tango_state

class SardanaDevice(Device_4Impl, Logger):
    
    def __init__(self, dclass, name):
        Device_4Impl.__init__(self, dclass, name)
        self.init(name)
        #if self.alias is not None:
        #    name = "Tango_%s" % self.alias
        #else:
        #    name = "Tango_%s" % self.get_name()
        Logger.__init__(self, name)
        
        self._state = DevState.ON
        self._status = 'Waiting to be initialized...'
        
        # access to some tango API (like MultiAttribute and Attribute) is 
        # still not thread safe so we have this lock to protect
        self.tango_lock = threading.Lock()
        
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
        self.set_state(self._state)
        
        self.get_device_properties(self.get_device_class())
        
        detect_evts = "state", "status"
        non_detect_evts = ()
        self.set_change_events(detect_evts, non_detect_evts)
    
    def delete_device(self):
        pass
    
    def set_change_events(self, evts_checked_by_tango, evts_not_checked_by_tango):
        for evt in evts_checked_by_tango:
            self.set_change_event(evt, True, True)
        for evt in evts_not_checked_by_tango:
            self.set_change_event(evt, True, False)

    def initialize_dynamic_attributes(self):
        pass
    
    def set_attribute(self, attr, value=None, timestamp=None, quality=None,
                      error=None, priority=1):
        fire_event = priority > 0
        
        recover = False
        if priority > 1 and attr.is_check_change_criteria():
            attr.set_change_event(True, False)
            recover = True
        
        try:
            if error is not None:
                if fire_event:
                    attr.fire_change_event(error)
                return
            
            if value is None:
                attr.set_quality(AttrQuality.ATTR_INVALID, fire_event)
                return
            
            if timestamp is not None and not isinstance(timestamp, TimeVal):
                timestamp = TimeVal.fromtimestamp(timestamp)
            
            if attr.get_data_type() == ArgType.DevEncoded:
                attr.set_value(*value)
            else:
                attr.set_value(value)
            
            if quality is not None:
                attr.set_quality(quality)
            
            if timestamp is not None:
                attr.set_date(timestamp)
            
            if fire_event:
                attr.fire_change_event()
        finally:
            if recover:
                attr.set_change_event(True, True)
        
    def calculate_tango_state(self, ctrl_state, update=True):
        self._state = state = to_tango_state(ctrl_state)
        if update:
            self.set_state(state)
        return state
    
    def calculate_tango_status(self, ctrl_status, update=True):
        self._status = status = ctrl_status
        if update:
            self.set_status(status)
        return status
    
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

    def __init__(self, name):
        DeviceClass.__init__(self, name)
        self.set_type(name)
        
    def dyn_attr(self, dev_list):
        for dev in dev_list:
            try:
                dev.initialize_dynamic_attributes()
            except:
                dev.warning("Failed to initialize dynamic attributes",
                            exc_info=1)


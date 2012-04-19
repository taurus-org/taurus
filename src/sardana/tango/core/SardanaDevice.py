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

"""Generic Sardana Tango Device module"""

from __future__ import with_statement

__all__ = ["SardanaDevice", "SardanaDeviceClass"]

__docformat__ = 'restructuredtext'

import time
import threading

from PyTango import Device_4Impl, DeviceClass, Util, DevState, \
    AttrQuality, TimeVal, ArgType

from taurus.core.util.log import Logger, DebugIt, InfoIt

from sardana import InvalidId
from util import to_tango_state, NO_DB_MAP


class SardanaDevice(Device_4Impl, Logger):
    
    def __init__(self, dclass, name):
        self._in_write = False
        self._event_stack = []
        Device_4Impl.__init__(self, dclass, name)
        self.init(name)
        Logger.__init__(self, name)
        
        self._state = DevState.ON
        self._status = 'Waiting to be initialized...'
        
        # access to some tango API (like MultiAttribute and Attribute) is 
        # still not thread safe so we have this lock to protect
        # Wa can't always use methods which use internally the
        # C++ AutoTangoMonitor because it blocks the entire tango device.
        self.tango_lock = threading.RLock()
        
    def init(self, name):
        util = Util.instance()
        db = util.get_database()
        if db is None:
            self._alias = self._get_nodb_device_info()[0]
        else:
            try:
                
                self._alias = db.get_alias(name)
                if self._alias.lower() == 'nada':
                    self._alias = None
            except:
                self._alias = None
    
    @property
    def alias(self):
        return self._alias
    
    def get_full_name(self):
        db = Util.instance().get_database()
        db_name = db.get_db_host() + ":" + db.get_db_port()
        return db_name + "/" + self.get_name()
    
    def init_device(self):
        self.set_state(self._state)
        util = Util.instance()
        db = util.get_database()
        if db is None:
            self.init_device_nodb()
        else:
            self.get_device_properties(self.get_device_class())
        
        detect_evts = "state", "status"
        non_detect_evts = ()
        self.set_change_events(detect_evts, non_detect_evts)
    
    def _get_nodb_device_info(self):
        name = self.get_name()
        tango_class = self.get_device_class().get_name()
        devices = NO_DB_MAP.get(tango_class, ())
        for dev_info in devices:
            if dev_info[1] == name:
                return dev_info
    
    def init_device_nodb(self):
        alias, dev_name, props = self._get_nodb_device_info()
        for prop_name, prop_value in props.items():
            setattr(self, prop_name, prop_value)
    
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
        with self.tango_lock:
            stack = self._event_stack
            stack.append((attr, value, timestamp, quality, error, priority))
            if self._in_write:
                return
            for event in stack:
                self._set_attribute(*event)
            #return self._set_attribute(attr, value=value, timestamp=timestamp,
            #                           quality=quality, error=error,
            #                           priority=priority)
            self._event_stack = []
    
    def set_attribute(self, attr, value=None, timestamp=None, quality=None,
                      error=None, priority=1):
        set_attr = self._set_attribute_fire
        with self.tango_lock:
            return set_attr(attr, value=value, timestamp=timestamp,
                            quality=quality, error=error, priority=priority)
    
    #@InfoIt()
    def _set_attribute_fire(self, attr, value=None, timestamp=None, quality=None,
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
            
            # some versions of Tango have a memory leak if you do:
            #     state_attr.set_value(DevState.ON)
            #     state_attr.fire_change_event()
            # so this workaround solves the memory leak:
            attr_name = attr.get_name().lower()
            if attr_name == "state":
                self.set_state(value)
                attr.fire_change_event()
                return
            elif attr_name == "status":
                self.set_status(value)
                attr.fire_change_event()
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
    
    def _set_attribute_push(self, attr, value=None, timestamp=None, quality=None,
                      error=None, priority=1):
        fire_event = priority > 0
        
        recover = False
        if priority > 1 and attr.is_check_change_criteria():
            attr.set_change_event(True, False)
            recover = True
        
        attr_name = attr.get_name()
        
        try:
            if error is not None and fire_event:
                self.push_change_event(attr_name, error)
                return
            
            if timestamp is None:
                timestamp = time.time()
            elif isinstance(timestamp, TimeVal):
                timestamp = TimeVal.totime(timestamp)

            if quality is None:
                quality = AttrQuality.ATTR_VALID
            
            data_type = attr.get_data_type()
            if fire_event:
                if data_type == ArgType.DevEncoded:
                    fmt, data = value
                    self.push_change_event(attr_name, fmt, data, timestamp, quality)
                else:
                    self.push_change_event(attr_name, value, timestamp, quality)
            else:
                if data_type == ArgType.DevEncoded:
                    fmt, data = value
                    attr.set_value_date_quality(fmt, data, timestamp, quality)
                else:
                    attr.set_value_date_quality(value, timestamp, quality)
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
    
    def device_name_factory(self, dev_name_list):
        tango_class = self.get_name()
        devices = NO_DB_MAP.get(tango_class, ())
        for dev_info in devices:
            dev_name_list.append(dev_info[1])
        

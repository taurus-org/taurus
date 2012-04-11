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

__all__ = ["CTExpChannel", "CTExpChannelClass"]

__docformat__ = 'restructuredtext'

import sys
import time
import math

from PyTango import Util, DevFailed
from PyTango import DevVoid, DevLong, DevLong64, DevDouble, DevBoolean, \
    DevString, DispLevel, DevState, AttrQuality, \
    Except, READ, READ_WRITE, SCALAR, SPECTRUM

from taurus.core.util.log import InfoIt, DebugIt

from sardana import State, SardanaServer
from sardana.sardanaattribute import SardanaAttribute
from sardana.tango.core.util import to_tango_state

from PoolDevice import PoolElementDevice, PoolElementDeviceClass


class CTExpChannel(PoolElementDevice):

    def __init__(self, dclass, name):
        PoolElementDevice.__init__(self, dclass, name)
        CTExpChannel.init_device(self)

    def init(self, name):
        PoolElementDevice.init(self, name)

    def get_ct(self):
        return self.element

    def set_ct(self, ct):
        self.element = ct

    ct = property(get_ct, set_ct)
    
    @DebugIt()
    def delete_device(self):
        PoolElementDevice.delete_device(self)

    @DebugIt()
    def init_device(self):
        PoolElementDevice.init_device(self)

        detect_evts = "state", "value"
        non_detect_evts = ()
        self.set_change_events(detect_evts, non_detect_evts)
        
        if self.ct is None:
            full_name = self.get_full_name()
            name = self.alias or full_name
            ct = self.pool.create_element(type="CTExpChannel", name=name, 
                full_name=full_name, id=self.Id, axis=self.Axis,
                ctrl_id=self.Ctrl_id)
            if self.instrument is not None:
                ct.set_instrument(self.instrument)
            ct.add_listener(self.on_ct_changed)
            self.ct = ct
        # force a state read to initialize the state attribute
        state = self.ct.state
    
    def on_ct_changed(self, event_source, event_type, event_value):
        # during server startup and shutdown avoid processing element
        # creation events
        if SardanaServer.server_state != State.Running:
            return
        
        timestamp = time.time()
        name = event_type.name
        quality = AttrQuality.ATTR_VALID
        priority = event_type.priority
        error = None
        attr = self.get_device_attr().get_attr_by_name(name)

        if name == "state":
            event_value = self.calculate_tango_state(event_value)
        elif name == "status":
            event_value = self.calculate_tango_status(event_value)
        else:
            if isinstance(event_value, SardanaAttribute):
                if event_value.error:
                    error = Except.to_dev_failed(*event_value.exc_info)
                timestamp = event_value.timestamp
                event_value = event_value.value
            
            if name == "value":
                state = self.ct.get_state()
                if state == State.Moving:
                    quality = AttrQuality.ATTR_CHANGING
        self.set_attribute(attr, value=event_value, timestamp=timestamp,
                           quality=quality, priority=priority)
    
    def always_executed_hook(self):
        #state = to_tango_state(self.ct.get_state(cache=False))
        pass
    
    def read_attr_hardware(self,data):
        pass

    def read_Value(self, attr):
        ct = self.ct
        #use_cache = ct.is_action_running() and not self.Force_HW_Read
        use_cache = self.get_state() == DevState.MOVING and not self.Force_HW_Read
        value = self.ct.get_value(cache=use_cache)
        quality = None
        if self.get_state() == DevState.MOVING:
            quality = AttrQuality.ATTR_CHANGING
        self.set_attribute(attr, value=value, quality=quality, priority=0)
    
    def is_Value_allowed(self, req_type):
        if self.get_state() in [DevState.FAULT, DevState.UNKNOWN]:
            return False
        return True
    
    def Start(self):
        self.ct.start_acquisition()
    

class CTExpChannelClass(PoolElementDeviceClass):

    #    Class Properties
    class_property_list = {
    }

    #    Device Properties
    device_property_list = {
    }
    device_property_list.update(PoolElementDeviceClass.device_property_list)

    #    Command definitions
    cmd_list = {
        'Start' :   [ [DevVoid, ""], [DevVoid, ""] ],
    }
    cmd_list.update(PoolElementDeviceClass.cmd_list)

    #    Attribute definitions
    attr_list = {
        'Value'     : [ [ DevDouble, SCALAR, READ ] ],
    }
    attr_list.update(PoolElementDeviceClass.attr_list)



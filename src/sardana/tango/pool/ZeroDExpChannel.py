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

__all__ = ["ZeroDExpChannel", "ZeroDExpChannelClass"]

__docformat__ = 'restructuredtext'

import sys
import time
import math

from PyTango import Util, DevFailed
from PyTango import DevVoid, DevLong, DevLong64, DevDouble, DevBoolean, DevString
from PyTango import DispLevel, DevState, AttrQuality
from PyTango import READ, READ_WRITE, SCALAR, SPECTRUM

from taurus.core.util.log import InfoIt, DebugIt

from PoolDevice import PoolElementDevice, PoolElementDeviceClass
from sardana.tango.core.util import to_tango_state


class ZeroDExpChannel(PoolElementDevice):

    def __init__(self, dclass, name):
        PoolElementDevice.__init__(self, dclass, name)
        ZeroDExpChannel.init_device(self)

    def init(self, name):
        PoolElementDevice.init(self, name)

    def get_zerod(self):
        return self.element

    def set_zerod(self, zerod):
        self.element = zerod

    zerod = property(get_zerod, set_zerod)
    
    @DebugIt()
    def delete_device(self):
        pass
        #self.pool.delete_element(self.element.get_name())
        #self.ct = None

    @DebugIt()
    def init_device(self):
        PoolElementDevice.init_device(self)

        detect_evts = "state", "value"
        non_detect_evts = ()
        self.set_change_events(detect_evts, non_detect_evts)
        
        if self.ct is None:
            full_name = self.get_name()
            name = self.alias or full_name
            zerod = self.pool.create_element(type="ZeroDExpChannel", name=name,
                full_name=full_name, id=self.Id, axis=self.Axis,
                ctrl_id=self.Ctrl_id)
            zerod.add_listener(self.on_zerod_changed)
            self.zerod = zerod
        # force a state read to initialize the state attribute
        state = self.zerod.state
    
    def on_zerod_changed(self, event_source, event_type, event_value):
        t = time.time()
        name = event_type.name
            
        multi_attr = self.get_device_attr()
        attr = multi_attr.get_attr_by_name(name)
        quality = AttrQuality.ATTR_VALID
        
        recover = False
        if event_type.priority > 1:
            attr.set_change_event(True, False)
            recover = True
        
        try:
            if name == "state":
                event_value = to_tango_state(event_value)
                self.set_state(event_value)
                self.push_change_event(name)
            else:
                state = to_tango_state(self.ct.get_state())
                if name == "value":
                    if state == DevState.MOVING:
                        quality = AttrQuality.ATTR_CHANGING
                self.push_change_event(name, event_value, t, quality)
        finally:
            if recover:
                attr.set_change_event(True, True)

    def always_executed_hook(self):
        #state = to_tango_state(self.zerod.get_state(cache=False))
        pass

    def read_attr_hardware(self,data):
        pass

    def read_Value(self, attr):
        attr.set_value(self.zerod.get_value(cache=False))
    
    def is_Value_allowed(self, req_type):
        if self.get_state() in [DevState.FAULT, DevState.UNKNOWN]:
            return False
        return True
    
    def Start(self):
        self.zerod.start_acquisition()
    

class ZeroDExpChannelClass(PoolElementDeviceClass):

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
        'Value'     : [ [ DevDouble, SCALAR, READ_WRITE ] ],
    }
    attr_list.update(PoolElementDeviceClass.attr_list)

    def __init__(self, name):
        PoolElementDeviceClass.__init__(self, name)
        self.set_type(name);


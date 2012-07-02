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

__all__ = ["IORegister", "IORegisterClass"]

__docformat__ = 'restructuredtext'

import time

from PyTango import DevFailed, Except
from PyTango import DevVoid, DevLong
from PyTango import DevState, AttrQuality
from PyTango import READ_WRITE, SCALAR


from taurus.core.util import InfoIt, DebugIt

from PoolDevice import PoolElementDevice, PoolElementDeviceClass

from sardana import State, SardanaServer
from sardana.sardanaattribute import SardanaAttribute


class IORegister(PoolElementDevice):

    def __init__(self, dclass, name):
        PoolElementDevice.__init__(self, dclass, name)
        IORegister.init_device(self)

    def init(self, name):
        PoolElementDevice.init(self, name)

    def get_ior(self):
        return self.element

    def set_ior(self, ior):
        self.element = ior

    ior = property(get_ior, set_ior)

    @DebugIt()
    def delete_device(self):
        PoolElementDevice.delete_device(self)
        ior = self.ior
        if ior is not None:
            ior.remove_listener(self.on_ior_changed)

    @DebugIt()
    def init_device(self):
        PoolElementDevice.init_device(self)
        
        ior = self.ior
        if ior is None:
            full_name = self.get_full_name()
            name = self.alias or full_name
            self.ior = ior = \
                self.pool.create_element(type="IORegister", name=name,
                    full_name=full_name, id=self.Id, axis=self.Axis,
                    ctrl_id=self.Ctrl_id)
            if self.instrument is not None:
                ior.set_instrument(self.instrument)
        ior.add_listener(self.on_ior_changed)
        # force a state read to initialize the state attribute
        state = ior.get_state(cache=False)

    def on_ior_changed(self, event_source, event_type, event_value):
        # during server startup and shutdown avoid processing element
        # creation events
        if SardanaServer.server_state != State.Running:
            return

        timestamp = time.time()
        name = event_type.name.lower()
        multi_attr = self.get_device_attr()
        try:
            attr = multi_attr.get_attr_by_name(name)
        except DevFailed:
            return
        quality = AttrQuality.ATTR_VALID
        priority = event_type.priority
        error = None

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

            state = self.ior.get_state(propagate=0)

            if state == State.Moving and name == "value":
                quality = AttrQuality.ATTR_CHANGING
        self.set_attribute(attr, value=event_value, timestamp=timestamp,
                           quality=quality, priority=priority, error=error,
                           synch=False)

    def always_executed_hook(self):
        #state = to_tango_state(self.ior.get_state(cache=False))
        pass

    def read_attr_hardware(self,data):
        pass

    def initialize_dynamic_attributes(self):
        attrs = PoolElementDevice.initialize_dynamic_attributes(self)

        detect_evts = "value",
        non_detect_evts = ()

        for attr_name in detect_evts:
            if attrs.has_key(attr_name):
                self.set_change_event(attr_name, True, True)
        for attr_name in non_detect_evts:
            if attrs.has_key(attr_name):
                self.set_change_event(attr_name, True, False)
        return

    def read_Value(self, attr):
        attr.set_value(self.ior.get_value(cache=False))

    def write_Value(self, attr):
        value = attr.get_write_value()
        self.ior.set_value(value)

    def is_Value_allowed(self, req_type):
        if self.get_state() in [DevState.FAULT, DevState.UNKNOWN]:
            return False
        return True

    def Start(self):
        self.ior.start_acquisition()


class IORegisterClass(PoolElementDeviceClass):

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
    attr_list = {}
    attr_list.update(PoolElementDeviceClass.attr_list)

    standard_attr_list = {
        'Value'     : [ [ DevLong, SCALAR, READ_WRITE ],
                        { 'Memorized'     : "true_without_hard_applied", }, ],
    }
    standard_attr_list.update(PoolElementDeviceClass.standard_attr_list)

    def _get_class_properties(self):
        ret = PoolElementDeviceClass._get_class_properties(self)
        ret['Description'] = "IORegister device class"
        ret['InheritedFrom'].insert(0, 'PoolElementDevice')
        return ret

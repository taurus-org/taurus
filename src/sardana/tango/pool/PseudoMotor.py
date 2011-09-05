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

__all__ = ["PseudoMotor", "PseudoMotorClass"]

__docformat__ = 'restructuredtext'

import time

from PyTango import Util, DevFailed
from PyTango import DevVoid, DevShort, DevLong, DevLong64, DevDouble, DevBoolean, DevString
from PyTango import DevVarStringArray
from PyTango import DispLevel, DevState, AttrQuality
from PyTango import READ, READ_WRITE, SCALAR, SPECTRUM

from taurus.core.util.log import InfoIt, DebugIt

from PoolDevice import PoolElementDevice, PoolElementDeviceClass
from sardana.tango.core import to_tango_state

class PseudoMotor(PoolElementDevice):

    def __init__(self, dclass, name):
        PoolElementDevice.__init__(self, dclass, name)
        PseudoMotor.init_device(self)

    def init(self, name):
        PoolElementDevice.init(self, name)

    def _is_allowed(self, req_type):
        return PoolElementDevice._is_allowed(self, req_type)

    def get_pseudo_motor(self):
        return self.element

    def set_pseudo_motor(self, pseudo_motor):
        self.element = pseudo_motor

    pseudo_motor = property(get_pseudo_motor, set_pseudo_motor)
    
    @DebugIt()
    def delete_device(self):
        self.pool.delete_element(self.pseudo_motor.get_name())
        self.pseudo_motor = None
    
    @InfoIt()
    def init_device(self):
        PoolElementDevice.init_device(self)

        detect_evts = "state", "status", "position"
        non_detect_evts = ()
        self.set_change_events(detect_evts, non_detect_evts)
        
        self.Elements = map(int, self.Elements)
        if self.pseudo_motor is None:
            pseudo_motor = self.pool.create_element(type="PseudoMotor",
                name=self.alias, full_name=self.get_name(), id=self.Id,
                axis=self.Axis, ctrl_id=self.Ctrl_id, user_elements=self.Elements)
            if self.instrument is not None:
                motor.set_instrument(self.instrument)
            pseudo_motor.add_listener(self.on_pseudo_motor_changed)
            self.pseudo_motor = pseudo_motor
        # force a state read to initialize the state attribute
        self.set_state(DevState.ON)
        
    def on_pseudo_motor_changed(self, event_source, event_type, event_value):
        t = time.time()
        name = event_type.name
        multi_attr = self.get_device_attr()
        attr = multi_attr.get_attr_by_name(name)
        quality = AttrQuality.ATTR_VALID
        
        recover = False
        if event_type.priority > 1:
            self.info("priority event %s=%s", name, event_value)
            attr.set_change_event(True, False)
            recover = True
        
        try:
            if name == "state":
                event_value = to_tango_state(event_value)
                self.set_state(event_value)
                self.push_change_event(name, event_value)
            elif name == "status":
                self.set_status(event_value)
                self.push_change_event(name, event_value)
            else:
                state = to_tango_state(self.pseudo_motor.get_state())
                #state = self.get_state()
                if name == "position":
                    if state == DevState.MOVING:
                        quality = AttrQuality.ATTR_CHANGING
                self.push_change_event(name, event_value, t, quality)
        finally:
            if recover:
                attr.set_change_event(True, True)

    def always_executed_hook(self):
        #state = to_tango_state(self.pseudo_motor.get_state(cache=False))
        pass

    def read_attr_hardware(self,data):
        pass
    
    def read_Position(self, attr):
        moving = self.get_state() == DevState.MOVING
        position = self.pseudo_motor.get_position(cache=moving)
        attr.set_value(position)
        if moving:
            attr.set_quality(AttrQuality.ATTR_CHANGING)
    
    def write_Position(self, attr):
        self.pseudo_motor.position = attr.get_write_value()
    
    def MoveRelative(self, argin):
        raise NotImplementedError
    
    def is_MoveRelative_allowed(self):
        if self.get_state() in [PyTango.DevState.FAULT, DevState.MOVING, DevState.UNKNOWN]:
            return False
        return True
    
    is_Position_allowed = _is_allowed


class PseudoMotorClass(PoolElementDeviceClass):

    #    Class Properties
    class_property_list = {
    }

    #    Device Properties
    device_property_list = {
        "Elements" :    [ DevVarStringArray, "elements used by the pseudo", [ ] ],
    }
    device_property_list.update(PoolElementDeviceClass.device_property_list)

    #    Command definitions
    cmd_list = {
        'MoveRelative' :   [ [DevDouble, "amount to move"], [DevVoid, ""] ],
    }
    cmd_list.update(PoolElementDeviceClass.cmd_list)

    #    Attribute definitions
    attr_list = {
        'Position'     : [ [ DevDouble, SCALAR, READ_WRITE ] ],
    }
    attr_list.update(PoolElementDeviceClass.attr_list)

    def __init__(self, name):
        PoolElementDeviceClass.__init__(self, name)
        self.set_type(name)


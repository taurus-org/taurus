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

__all__ = ["Motor", "MotorClass"]

__docformat__ = 'restructuredtext'

import time

from PyTango import Util, DevFailed
from PyTango import DevVoid, DevShort, DevLong, DevLong64, DevDouble, DevBoolean, DevString
from PyTango import DispLevel, DevState, AttrQuality
from PyTango import READ, READ_WRITE, SCALAR, SPECTRUM

from taurus.core.util.log import InfoIt, DebugIt

from PoolDevice import PoolElementDevice, PoolElementDeviceClass
from sardana.tango.core.util import to_tango_state

class Motor(PoolElementDevice):

    def __init__(self, dclass, name):
        PoolElementDevice.__init__(self, dclass, name)
        Motor.init_device(self)

    def init(self, name):
        PoolElementDevice.init(self, name)

    def _is_allowed(self, req_type):
        return PoolElementDevice._is_allowed(self, req_type)

    def get_motor(self):
        return self.element

    def set_motor(self, motor):
        self.element = motor

    motor = property(get_motor, set_motor)
    
    @DebugIt()
    def delete_device(self):
        self.pool.delete_element(self.motor.get_name())
        self.motor = None
    
    @InfoIt()
    def init_device(self):
        PoolElementDevice.init_device(self)

        detect_evts = "state", "status", "position", "dialposition", "limit_switches"
        non_detect_evts = "step_per_unit", "offset", "sign", "velocity", \
            "acceleration", "deceleration", "base_rate", "backlash"
        self.set_change_events(detect_evts, non_detect_evts)
        
        if self.motor is None:
            motor = self.pool.create_element(type="Motor",
                name=self.alias, full_name=self.get_name(), id=self.Id,
                axis=self.Axis, ctrl_id=self.Ctrl_id)
            if self.instrument is not None:
                motor.set_instrument(self.instrument)
            if self.Sleep_bef_last_read > 0:
                motor.set_instability_time(self.Sleep_bef_last_read / 1000.0)
            motor.add_listener(self.on_motor_changed)
            self.motor = motor
        # force a state read to initialize the state attribute
        self.set_state(DevState.ON)
        
    def on_motor_changed(self, event_source, event_type, event_value):
        t = time.time()
        name = event_type.name
        if name == "dial_position":
            name = "dialposition"
        multi_attr = self.get_device_attr()
        attr = multi_attr.get_attr_by_name(name)
        quality = AttrQuality.ATTR_VALID
        
        recover = False
        if event_type.priority > 1:
            self.debug("priority event %s",name)
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
                state = to_tango_state(self.motor.get_state())
                if name == "position" or name == "dialposition":
                    if state == DevState.MOVING:
                        quality = AttrQuality.ATTR_CHANGING
                self.push_change_event(name, event_value, t, quality)
        finally:
            if recover:
                attr.set_change_event(True, True)

    def always_executed_hook(self):
        #state = to_tango_state(self.motor.get_state(cache=False))
        dev_class, multi_attr1 = self.get_device_class(), self.get_device_attr()
        pass
    
    def read_attr_hardware(self,data):
        pass
    
    def read_Position(self, attr):
        moving = self.get_state() == DevState.MOVING
        position = self.motor.get_position(cache=moving)
        attr.set_value(position)
        if moving:
            attr.set_quality(AttrQuality.ATTR_CHANGING)
    
    def write_Position(self, attr):
        self.motor.position = attr.get_write_value()
    
    def read_Acceleration(self, attr):
        attr.set_value(self.motor.get_acceleration(cache=False))
    
    def write_Acceleration(self, attr):
        self.motor.acceleration = attr.get_write_value()
    
    def read_Deceleration(self, attr):
        attr.set_value(self.motor.get_deceleration(cache=False))
    
    def write_Deceleration(self, attr):
        self.motor.deceleration = attr.get_write_value()
    
    def read_Base_rate(self, attr):
        attr.set_value(self.motor.get_base_rate(cache=False))
    
    def write_Base_rate(self, attr):
        self.motor.base_rate = attr.get_write_value()
    
    def read_Velocity(self, attr):
        attr.set_value(self.motor.get_velocity(cache=False))
    
    def write_Velocity(self, attr):
        self.motor.velocity = attr.get_write_value()

    def read_Offset(self, attr):
        attr.set_value(self.motor.get_offset(cache=False))
    
    def write_Offset(self, attr):
        self.motor.offset = attr.get_write_value()
    
    def read_DialPosition(self, attr):
        moving = self.get_state() == DevState.MOVING
        dial_position = self.motor.get_dial_position(cache=moving)
        attr.set_value(dial_position)
        if moving:
            attr.set_quality(AttrQuality.ATTR_CHANGING)
    
    def read_Step_per_unit(self, attr):
        attr.set_value(self.motor.get_step_per_unit(cache=False))
    
    def write_Step_per_unit(self, attr):
        self.motor.step_per_unit = attr.get_write_value()
    
    def read_Backlash(self, attr):
        attr.set_value(self.motor.get_backlash(cache=False))
    
    def write_Backlash(self, attr):
        self.motor.backlash = attr.get_write_value()
    
    def read_Sign(self, attr):
        sign = self.motor.get_sign(cache=False)
        attr.set_value(sign)
    
    def write_Sign(self, attr):
        self.motor.sign = attr.get_write_value()
    
    def read_Limit_switches(self, attr):
        attr.set_value(self.motor.get_limit_switches(cache=False))
    
    def DefinePosition(self, argin):
        raise NotImplementedError
    
    def is_DefinePosition_allowed(self):
        if self.get_state() in [PyTango.DevState.FAULT, DevState.MOVING, DevState.UNKNOWN]:
            return False
        return True
    
    def SaveConfig(self):
        raise NotImplementedError
    
    def is_SaveConfig_allowed(self):
        if self.get_state() in [PyTango.DevState.FAULT, DevState.MOVING, DevState.UNKNOWN]:
            return False
        return True
    
    def MoveRelative(self, argin):
        raise NotImplementedError
    
    def is_MoveRelative_allowed(self):
        if self.get_state() in [PyTango.DevState.FAULT, DevState.MOVING, DevState.UNKNOWN]:
            return False
        return True
    
    is_Position_allowed = _is_allowed
    is_Acceleration_allowed = _is_allowed
    is_Deceleration_allowed = _is_allowed
    is_Base_rate_allowed = _is_allowed
    is_Velocity_allowed = _is_allowed
    is_Offset_allowed = _is_allowed
    is_DialPosition_allowed = _is_allowed
    is_Step_per_unit_allowed = _is_allowed
    is_Backlash_allowed = _is_allowed
    is_Sign_allowed = _is_allowed
    is_Limit_switches_allowed = _is_allowed


class MotorClass(PoolElementDeviceClass):

    #    Class Properties
    class_property_list = {
    }

    #    Device Properties
    device_property_list = {
        'Sleep_bef_last_read' : [DevLong, "Number of mS to sleep before the last read during a motor movement", 0],
        '_Acceleration' : [DevDouble, "", -1],
        '_Deceleration' : [DevDouble, "", -1],
        '_Velocity'     : [DevDouble, "", -1],
        '_Base_rate'    : [DevDouble, "", -1],
    }
    device_property_list.update(PoolElementDeviceClass.device_property_list)

    #    Command definitions
    cmd_list = {
        'DefinePosition' : [ [DevDouble, "New position"], [DevVoid, ""] ],
        'SaveConfig' :     [ [DevVoid, ""], [DevVoid, ""] ],
        'MoveRelative' :   [ [DevDouble, "amount to move"], [DevVoid, ""] ],
    }
    cmd_list.update(PoolElementDeviceClass.cmd_list)

    #    Attribute definitions
    attr_list = {
        'Position'     : [ [ DevDouble, SCALAR, READ_WRITE ] ],
        'Acceleration' : [ [ DevDouble, SCALAR, READ_WRITE ] ],
        'Deceleration' : [ [ DevDouble, SCALAR, READ_WRITE ] ],
        'Base_rate'    : [ [ DevDouble, SCALAR, READ_WRITE ],
                           { 'label'         : 'Base rate', } ],
        'Velocity'     : [ [ DevDouble, SCALAR, READ_WRITE ] ],
        'Offset'       : [ [ DevDouble, SCALAR, READ_WRITE ],
                           { 'Memorized'     : "true",
                             'Display level' : DispLevel.EXPERT } ],
        'DialPosition' : [ [ DevDouble, SCALAR, READ ],
                           { 'label'         : "Dial position",
                             'Display level' : DispLevel.EXPERT } ],
        'Step_per_unit': [ [ DevDouble, SCALAR, READ_WRITE],
                           { 'Memorized'     : "true",
                             'label'         : "Steps p/ unit",
                             'Display level' : DispLevel.EXPERT } ],
        'Backlash'     : [ [ DevLong, SCALAR, READ_WRITE],
                           { 'Memorized'     : "true",
                             'Display level' : DispLevel.EXPERT } ],
        'Sign'         : [ [ DevShort, SCALAR, READ_WRITE],
                           { 'Memorized'     : "true",
                             'Display level' : DispLevel.EXPERT } ],
        'Limit_switches': [ [ DevBoolean, SPECTRUM, READ, 3],
                            { 'label'       : "Limit switches (H,U,L)",
                              'description' : "This attribute is the motor "\
                              "limit switches state. It's an array with 3 \n"\
                              "elements which are:\n"\
                              "0 - The home switch\n"\
                              "1 - The upper limit switch\n"\
                              "2 - The lower limit switch\n"\
                              "False means not active. True means active" } ],
    }
    attr_list.update(PoolElementDeviceClass.attr_list)

    def __init__(self, name):
        PoolElementDeviceClass.__init__(self, name)
        self.set_type(name)


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

__all__ = ["MotorGroup", "MotorGroupClass"]

__docformat__ = 'restructuredtext'

import time

from PyTango import Util, DevFailed, Except
from PyTango import DevVoid, DevLong, DevLong64, DevDouble, DevBoolean, DevString
from PyTango import DispLevel, DevState, AttrQuality
from PyTango import READ, READ_WRITE, SCALAR, SPECTRUM

from taurus.core.util.log import InfoIt, DebugIt

from sardana import State, SardanaServer
from sardana.tango.core.util import to_tango_state
from PoolDevice import PoolGroupDevice, PoolGroupDeviceClass


class MotorGroup(PoolGroupDevice):
    
    def __init__(self, dclass, name):
        PoolGroupDevice.__init__(self, dclass, name)
        MotorGroup.init_device(self)

    def init(self, name):
        PoolGroupDevice.init(self, name)

    def _is_allowed(self, req_type):
        return PoolGroupDevice._is_allowed(self, req_type)
    
    def get_motor_group(self):
        return self.element
    
    def set_motor_group(self, motor_group):
        self.element = motor_group
    
    motor_group = property(get_motor_group, set_motor_group)
    
    @DebugIt()
    def delete_device(self):
        PoolGroupDevice.delete_device(self)
    
    @DebugIt()
    def init_device(self):
        PoolGroupDevice.init_device(self)
    
        detect_evts = "position",
        non_detect_evts = "elementlist",
        self.set_change_events(detect_evts, non_detect_evts)

        self.Elements = map(int, self.Elements)
        if self.motor_group is None:
            full_name = self.get_full_name()
            name = self.alias or full_name
            motor_group = self.pool.create_motor_group(name=name, id=self.Id,
                full_name=full_name, user_elements=self.Elements)
            motor_group.add_listener(self.on_motor_group_changed)
            self.motor_group = motor_group

    def on_motor_group_changed(self, event_source, event_type, event_value):
        # during server startup and shutdown avoid processing element
        # creation events
        if SardanaServer.server_state != State.Running:
            return
        timestamp = time.time()
        name = event_type.name
        
        multi_attr = self.get_device_attr()
        attr = multi_attr.get_attr_by_name(name)
        quality = AttrQuality.ATTR_VALID
        priority = event_type.priority
        error = None
        if name == "state":
            event_value = self.calculate_tango_state(event_value)
        elif name == "status":
            event_value = self.calculate_tango_status(event_value)
        else:
            state = self.motor_group.get_state(propagate=0)
            
            if name == "position":
                if state == State.Moving:
                    quality = AttrQuality.ATTR_CHANGING
                try:
                    event_value = self._to_motor_positions(event_value)
                except DevFailed, df:
                    error = df
        
        self.set_attribute(attr, value=event_value, timestamp=timestamp,
                           quality=quality, priority=priority, error=error)
    
    def always_executed_hook(self):
        pass 
        #state = to_tango_state(self.motor_group.get_state(cache=False))
    
    def read_attr_hardware(self,data):
        pass
    
    def _to_motor_positions(self, pos):
        positions = []
        for elem in self.motor_group.get_user_elements():
            position = pos[elem]
            if position.in_error():
                Except.throw_python_exception(*position.exc_info)
            positions.append(position.value)
        return positions

    def read_Position(self, attr):
        # if motors are moving their position is already being updated with a
        # high frequency so don't bother overloading and just get the cached
        # values
        motor_group = self.motor_group
        use_cache = motor_group.is_in_operation() and not self.Force_HW_Read
        self.debug("read_Position(cache=%s)", use_cache)
        positions = motor_group.get_position(cache=use_cache, propagate=0)
        state = motor_group.get_state(cache=use_cache, propagate=0)
        positions = self._to_motor_positions(positions)
        quality = None
        if state == State.Moving:
            quality = AttrQuality.ATTR_CHANGING
        self.set_attribute(attr, value=positions, quality=quality, priority=0)
        
    def write_Position(self, attr):
        position = attr.get_write_value()
        self.debug("write_Position(%s)", position)
        try:
            self.wait_for_operation()
        except:
            raise Exception("Cannot move: already in motion")
        try:
            self.motor_group.position = position
        except PoolException, pe:
            throw_sardana_exception(pe)
        
    is_Position_allowed = _is_allowed
    

class MotorGroupClass(PoolGroupDeviceClass):

    #    Class Properties
    class_property_list = {
    }

    #    Device Properties
    device_property_list = {
    }
    device_property_list.update(PoolGroupDeviceClass.device_property_list)

    #    Command definitions
    cmd_list = {
    }
    cmd_list.update(PoolGroupDeviceClass.cmd_list)

    #    Attribute definitions
    attr_list = {
        'Position'     : [ [ DevDouble, SPECTRUM, READ_WRITE, 4096 ], ],
                           # Position is not scalar and can not be memorized
                           #{ 'Memorized'     : "true_without_hard_applied", }, ],
    }
    attr_list.update(PoolGroupDeviceClass.attr_list)



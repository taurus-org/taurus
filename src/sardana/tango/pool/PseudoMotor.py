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

import sys
import time

from PyTango import DevFailed, Except, READ_WRITE, SCALAR, DevVoid, \
    DevDouble, DevBoolean, DevVarStringArray, DevState, AttrQuality

from taurus.core.util.log import DebugIt

from sardana import State, SardanaServer
from sardana.sardanaattribute import SardanaAttribute
from sardana.pool.poolexception import PoolException
from sardana.tango.core.util import exception_str, \
    to_tango_type_format, throw_sardana_exception
from PoolDevice import PoolElementDevice, PoolElementDeviceClass


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
        PoolElementDevice.delete_device(self)
        pseudo_motor = self.pseudo_motor
        if pseudo_motor is not None:
            pseudo_motor.remove_listener(self.on_pseudo_motor_changed)
            
    @DebugIt()
    def init_device(self):
        PoolElementDevice.init_device(self)
        
        self.Elements = map(int, self.Elements)
        pseudo_motor = self.pseudo_motor
        if self.pseudo_motor is None:
            full_name = self.get_full_name()
            name = self.alias or full_name
            self.pseudo_motor = pseudo_motor = \
                self.pool.create_element(type="PseudoMotor", name=name,
                    full_name=full_name, id=self.Id, axis=self.Axis,
                    ctrl_id=self.Ctrl_id, user_elements=self.Elements)
            if self.instrument is not None:
                pseudo_motor.set_instrument(self.instrument)
        pseudo_motor.add_listener(self.on_pseudo_motor_changed)
        pseudo_motor.set_drift_correction(self.DriftCorrection)
        
        self.set_state(DevState.ON)

    def on_pseudo_motor_changed(self, event_source, event_type, event_value):
        try:
            self._on_pseudo_motor_changed(event_source, event_type,
                                          event_value)
        except:
            msg = 'Error occured "on_pseudo_motor_changed(%s.%s): %s"'
            exc_info = sys.exc_info()
            self.error(msg, self.pseudo_motor.name, event_type.name,
                       exception_str(*exc_info[:2]))
            self.debug("Details", exc_info=exc_info)

    def _on_pseudo_motor_changed(self, event_source, event_type, event_value):
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

            state = self.pseudo_motor.get_state(propagate=0)

            if state == State.Moving and name == "position":
                quality = AttrQuality.ATTR_CHANGING
        self.set_attribute(attr, value=event_value, timestamp=timestamp,
                           quality=quality, priority=priority, error=error,
                           synch=False)

    def always_executed_hook(self):
        #state = to_tango_state(self.pseudo_motor.get_state(cache=False))
        pass

    def read_attr_hardware(self, data):
        pass

    def get_dynamic_attributes(self):
        std_attrs, dyn_attrs = \
            PoolElementDevice.get_dynamic_attributes(self)

        # For position attribute, listen to what the controller says for data
        # type (between long and float)
        pos = std_attrs.get('position')
        if pos is not None:
            attr_name, data_info, attr_info = pos
            ttype, tformat = to_tango_type_format(attr_info.get('type'))
            data_info[0][0] = ttype
        return std_attrs, dyn_attrs

    def initialize_dynamic_attributes(self):
        attrs = PoolElementDevice.initialize_dynamic_attributes(self)

        detect_evts = "position",
        non_detect_evts = ()

        for attr_name in detect_evts:
            if attr_name in attrs:
                self.set_change_event(attr_name, True, True)
        for attr_name in non_detect_evts:
            if attr_name in attrs:
                self.set_change_event(attr_name, True, False)
        return

    def read_Position(self, attr):
        pseudo_motor = self.pseudo_motor
        use_cache = pseudo_motor.is_in_operation() and not self.Force_HW_Read
        position = pseudo_motor.get_position(cache=use_cache, propagate=0)
        state = pseudo_motor.get_state(cache=use_cache, propagate=0)
        if position.error:
            Except.throw_python_exception(*position.exc_info)
        quality = None
        if state == State.Moving:
            quality = AttrQuality.ATTR_CHANGING
        self.set_attribute(attr, value=position.value, quality=quality,
                           priority=0, timestamp=position.timestamp)

    def write_Position(self, attr):
        position = attr.get_write_value()
        self.debug("write_Position(%s)", position)
        try:
            self.wait_for_operation()
        except:
            raise Exception("Cannot move: already in motion")
        pseudo_motor = self.pseudo_motor
        try:
            pseudo_motor.position = position
        except PoolException, pe:
            throw_sardana_exception(pe)

    def MoveRelative(self, argin):
        raise NotImplementedError

    def is_MoveRelative_allowed(self):
        if self.get_state() in (DevState.FAULT, DevState.MOVING,
                                DevState.UNKNOWN):
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
        'DriftCorrection':
            [DevBoolean,
            "Locally apply drift correction on pseudo motors. Default is the "
            "current global drift correction in the Pool Device",
            None],
    }
    device_property_list.update(PoolElementDeviceClass.device_property_list)

    #    Command definitions
    cmd_list = {
        'MoveRelative' :   [ [DevDouble, "amount to move"], [DevVoid, ""] ],
    }
    cmd_list.update(PoolElementDeviceClass.cmd_list)

    #    Attribute definitions
    standard_attr_list = {
        'Position'     : [ [ DevDouble, SCALAR, READ_WRITE ],
                           { 'Memorized'     : "true_without_hard_applied", }, ],
    }
    standard_attr_list.update(PoolElementDeviceClass.standard_attr_list)

    def _get_class_properties(self):
        ret = PoolElementDeviceClass._get_class_properties(self)
        ret['Description'] = "Pseudo motor device class"
        ret['InheritedFrom'].insert(0, 'PoolElementDevice')
        return ret

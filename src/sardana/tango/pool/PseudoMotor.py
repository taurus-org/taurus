#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
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
    DevDouble, DevBoolean, DevVarStringArray, DevVarDoubleArray, DevState, \
    AttrQuality

from taurus.core.util.log import DebugIt

from sardana import State, SardanaServer
from sardana.sardanaexception import SardanaException
from sardana.sardanaattribute import SardanaAttribute
from sardana.tango.core.util import exception_str, to_tango_type_format, \
    throw_sardana_exception
from sardana.tango.pool.PoolDevice import PoolElementDevice, \
    PoolElementDeviceClass


class PseudoMotor(PoolElementDevice):

    def __init__(self, dclass, name):
        self.in_write_position = False
        PoolElementDevice.__init__(self, dclass, name)

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
        pseudo_motor.set_drift_correction(self.DriftCorrection)
        pseudo_motor.add_listener(self.on_pseudo_motor_changed)

        self.set_state(DevState.ON)

    def on_pseudo_motor_changed(self, event_source, event_type, event_value):
        try:
            self._on_pseudo_motor_changed(event_source, event_type,
                                          event_value)
        except:
            msg = 'Error occurred "on_pseudo_motor_changed(%s.%s): %s"'
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

        try:
            attr = self.get_attribute_by_name(name)
        except DevFailed:
            return
        quality = AttrQuality.ATTR_VALID
        priority = event_type.priority
        value, w_value, error = None, None, None

        if name == "state":
            value = self.calculate_tango_state(event_value)
        elif name == "status":
            value = self.calculate_tango_status(event_value)
        else:
            if isinstance(event_value, SardanaAttribute):
                if event_value.error:
                    error = Except.to_dev_failed(*event_value.exc_info)
                else:
                    value = event_value.value
                timestamp = event_value.timestamp
            else:
                value = event_value
            state = self.pseudo_motor.get_state(propagate=0)

            if name == "position":
                w_value = event_value.w_value
                if state == State.Moving:
                    quality = AttrQuality.ATTR_CHANGING

        self.set_attribute(attr, value=value, w_value=w_value,
                           timestamp=timestamp, quality=quality,
                           priority=priority, error=error, synch=False)

    def always_executed_hook(self):
        #state = to_tango_state(self.pseudo_motor.get_state(cache=False))
        pass

    def read_attr_hardware(self, data):
        pass

    def get_dynamic_attributes(self):
        cache_built = hasattr(self, "_dynamic_attributes_cache")

        std_attrs, dyn_attrs = \
            PoolElementDevice.get_dynamic_attributes(self)

        if not cache_built:
            # For position attribute, listen to what the controller says for
            # data type (between long and float)
            pos = std_attrs.get('position')
            if pos is not None:
                _, data_info, attr_info = pos
                ttype, _ = to_tango_type_format(attr_info.dtype)
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
        if position.error:
            throw_sardana_exception(position)
        state = pseudo_motor.get_state(cache=use_cache, propagate=0)
        quality = None
        if state == State.Moving:
            quality = AttrQuality.ATTR_CHANGING
        self.set_attribute(attr, value=position.value, w_value=position.w_value,
                           quality=quality, priority=0,
                           timestamp=position.timestamp)

    def write_Position(self, attr):
        self.in_write_position = True
        try:
            position = attr.get_write_value()
            self.debug("write_Position(%s)", position)
            try:
                self.wait_for_operation()
            except:
                raise Exception("Cannot move: already in motion")
            pseudo_motor = self.pseudo_motor
            try:
                pseudo_motor.position = position
            except SardanaException as se:
                throw_sardana_exception(se)
        finally:
            self.in_write_position = False

    def CalcPseudo(self, physical_positions):
        """Returns the pseudo motor position for the given physical positions"""
        if not len(physical_positions):
            physical_positions = None
        result = self.pseudo_motor.calc_pseudo(physical_positions=physical_positions)
        if result.error:
            throw_sardana_exception(result)
        return result.value

    def CalcPhysical(self, pseudo_position):
        """Returns the physical motor positions for the given pseudo motor
        position assuming the current pseudo motor write positions for all the
        other sibling pseudo motors"""
        result = self.pseudo_motor.calc_physical(pseudo_position)
        if result.error:
            throw_sardana_exception(result)
        return result.value

    def CalcAllPhysical(self, pseudo_positions):
        """Returns the physical motor positions for the given pseudo motor
        position(s)"""
        result = self.pseudo_motor.calc_physical(pseudo_positions)
        if result.error:
            throw_sardana_exception(result)
        return result.value

    def CalcAllPseudo(self, physical_positions):
        """Returns the pseudo motor position(s) for the given physical positions"""
        result = self.pseudo_motor.calc_all_pseudo(physical_positions)
        if result.error:
            throw_sardana_exception(result)
        return result.value

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
        'CalcPseudo'      : [ [DevVarDoubleArray, "physical positions"], [DevDouble, "pseudo position"] ],
        'CalcPhysical'    : [ [DevDouble, "pseudo position"], [DevVarDoubleArray, "physical positions"] ],
        'CalcAllPseudo'   : [ [DevVarDoubleArray, "physical positions"], [DevVarDoubleArray, "pseudo positions"] ],
        'CalcAllPhysical' : [ [DevVarDoubleArray, "pseudo positions"], [DevVarDoubleArray, "physical positions"] ],
        'MoveRelative'    : [ [DevDouble, "amount to move"], [DevVoid, ""] ],
    }
    cmd_list.update(PoolElementDeviceClass.cmd_list)

    #    Attribute definitions
    standard_attr_list = {
        'Position'     : [ [ DevDouble, SCALAR, READ_WRITE ],
                           { 'label'      : "Position",
                             'abs_change' : '1.0', }, ],
    }
    standard_attr_list.update(PoolElementDeviceClass.standard_attr_list)

    def _get_class_properties(self):
        ret = PoolElementDeviceClass._get_class_properties(self)
        ret['Description'] = "Pseudo motor device class"
        ret['InheritedFrom'].insert(0, 'PoolElementDevice')
        return ret

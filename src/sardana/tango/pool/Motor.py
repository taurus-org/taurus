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

"""The sardana tango motor module"""

__all__ = ["Motor", "MotorClass"]

__docformat__ = 'restructuredtext'

import sys
import time

from PyTango import DevFailed, Except, DevVoid, DevShort, \
    DevLong, DevDouble, DevBoolean, DispLevel, DevState, AttrQuality, \
    READ, READ_WRITE, SCALAR, SPECTRUM

from taurus.core.util.log import DebugIt

from sardana import State, SardanaServer
from sardana.sardanautils import str_to_value
from sardana.sardanaattribute import SardanaAttribute
from sardana.pool.poolexception import PoolException
from sardana.tango.core.util import memorize_write_attribute, exception_str, \
    to_tango_type_format, throw_sardana_exception
from sardana.tango.pool.PoolDevice import PoolElementDevice, \
    PoolElementDeviceClass


class Motor(PoolElementDevice):
    """The tango motor device class. This class exposes through a tango device
the sardana motor (:class:`~sardana.pool.poolmotor.PoolMotor`).
    
.. rubric:: The states

The motor interface knows five states which are ON, MOVING, ALARM,
FAULT and UNKNOWN. A motor device is in MOVING state when it is
moving! It is in ALARM state when it has reached one of the limit
switches and is in FAULT if its controller software is not available
(impossible to load it) or if a fault is reported from the hardware
controller. The motor is in the UNKNOWN state if an exception occurs
during the communication between the pool and the hardware controller.
When the motor is in ALARM state, its status will indicate which limit
switches is active.

.. rubric:: The commands

The motor interface supports 3 commands on top of the Tango classical
Init, State and Status commands. These commands are summarized in the
following table:

==============  ================  ================
Command name    Input data type   Output data type  
==============  ================  ================
Stop            void              void              
Abort           void              void              
DefinePosition  Tango::DevDouble  void              
SaveConfig      void              void              
==============  ================  ================

- **Stop** : It stops a running motion. This command does not have input or
  output argument.

- **Abort** : It aborts a running motion. This command does not have input or
  output argument.

- **DefinePosition** : Loads a position into controller. It has one input
  argument which is the new position value (a double). It is allowed only in
  the ON or ALARM states. The unit used for the command input value is the
  physical unit: millimeters or milli-radians. It is always an absolute
  position.

- **SaveConfig** : Write some of the motor parameters in database. Today, it
  writes the motor acceleration, deceleration, base_rate and velocity into
  database as motor device properties. It is allowed only in the ON or ALARM
  states

The classical Tango Init command destroys the motor and re-create it. 

.. rubric:: The attributes

The motor interface supports several attributes which are summarized
in the following table:

==============  =================  ===========  ========  =========  ===============
Name            Data type          Data format  Writable  Memorized  Operator/Expert  
==============  =================  ===========  ========  =========  ===============
Position        Tango::DevDouble   Scalar       R/W       No *       Operator         
DialPosition    Tango::DevDouble   Scalar       R         No         Expert         
Offset          Tango::DevDouble   Scalar       R/W       Yes        Expert         
Acceleration    Tango::DevDouble   Scalar       R/W       No         Expert         
Base_rate       Tango::DevDouble   Scalar       R/W       No         Expert         
Deceleration    Tango::DevDouble   Scalar       R/W       No         Expert         
Velocity        Tango::DevDouble   Scalar       R/W       No         Expert         
Limit_Switches  Tango::DevBoolean  Spectrum     R         No         Expert         
SimulationMode  Tango::DevBoolean  Scalar       R         No         Expert         
Step_per_unit   Tango::DevDouble   Scalar       R/W       Yes        Expert         
Backlash        Tango::DevLong     Scalar       R/W       Yes        Expert         
==============  =================  ===========  ========  =========  ===============

- **Position** : This is read-write scalar double attribute. With the classical
  Tango min and max_value attribute properties, it is easy to define
  authorized limit for this attribute. See the definition of the
  DialPosition and Offset attributes to get a precise definition of the
  meaning of this attribute. It is not allowed to read or write this
  attribute when the motor is in FAULT or UNKNOWN state. It is also not
  possible to write this attribute when the motor is already MOVING. 
  The unit used for this attribute is the physical unit: millimeters or
  milli-radian. It is always an **absolute position** .

- **DialPosition** : This attribute is the motor dial position. The following
  formula links together the Position, DialPosition, Sign and Offset attributes:
  
      Position = Sign * DialPosition + Offset
  
  This allows to have the motor position centered around any position
  defined by the Offset attribute (classically the X ray beam position).
  It is a read only attribute. To set the motor position, the user has
  to use the Position attribute. It is not allowed to read this
  attribute when the motor is in FAULT or UNKNOWN mode. The unit used
  for this attribute is the physical unit: millimeters or milli-radian.
  It is also always an **absolute** position.

- **Offset** : The offset to be applied in the motor position computation. By
  default set to 0. It is a memorized attribute. It is not allowed to
  read or write this attribute when the motor is in FAULT, MOVING or
  UNKNOWN mode.

- **Acceleration** : This is an expert read-write scalar double attribute.
  This parameter value is written in database when the SaveConfig command is
  executed. It is not allowed to read or write this attribute when the motor is
  in FAULT or UNKNOWN state.

- **Deceleration** : This is an expert read-write scalar double attribute.
  This parameter value is written in database when the SaveConfig command is
  executed. It is not allowed to read or write this attribute when the motor is
  in FAULT or UNKNOWN state.

- **Base_rate** : This is an expert read-write scalar double attribute. This
  parameter value is written in database when the SaveConfig command is executed.
  It is not allowed to read or write this attribute when the motor is in
  FAULT or UNKNOWN state.

- **Velocity** : This is an expert read-write scalar double attribute.
  This parameter value is written in database when the SaveConfig command is
  executed. It is not allowed to read or write this attribute when the motor is
  in FAULT or UNKNOWN state.

- **Limit_Switches** : Three limit switches are managed by this attribute.
  Each of the switch are represented by a boolean value: False means inactive
  while True means active. It is a read only attribute. It is not possible to
  read this attribute when the motor is in UNKNOWN mode. It is a
  spectrum attribute with 3 values which are:

    - Data[0] : The Home switch value
    
    - Data[1] : The Upper switch value
    
    - Data[2] : The Lower switch value
    
- **SimulationMode** : This is a read only scalar boolean attribute. When set,
  all motion requests are not forwarded to the software controller and then to
  the hardware. When set, the motor position is simulated and is immediately
  set to the value written by the user. To set this attribute, the user
  has to used the pool device Tango interface. The value of the
  position, acceleration, deceleration, base_rate, velocity and offset
  attributes are memorized at the moment this attribute is set. When
  this mode is turned off, if the value of any of the previously
  memorized attributes has changed, it is reapplied to the memorized
  value. It is not allowed to read this attribute when the motor is in
  FAULT or UNKNOWN states.

- **Step_per_unit** : This is the number of motor step per millimeter or per
  degree. It is a memorized attribute. It is not allowed to read or write this
  attribute when the motor is in FAULT or UNKNOWN mode. It is also not
  allowed to write this attribute when the motor is MOVING. The default
  value is 1.

- **Backlash** : If this attribute is defined to something different than 0,
  the motor will always stop the motion coming from the same mechanical
  direction. This means that it could be possible to ask the motor to go
  a little bit after the desired position and then to return to the
  desired position. The attribute value is the number of steps the motor
  will pass the desired position if it arrives from the "wrong"
  direction. This is a signed value. If the sign is positive, this means
  that the authorized direction to stop the motion is the increasing
  motor position direction. If the sign is negative, this means that the
  authorized direction to stop the motion is the decreasing motor
  position direction. It is a memorized attribute. It is not allowed to
  read or write this attribute when the motor is in FAULT or UNKNOWN
  mode. It is also not allowed to write this attribute when the motor is
  MOVING. Some hardware motor controllers are able to manage this
  backlash feature. If it is not the case, the motor interface will
  implement this behavior.
  
All the motor devices will have the already described attributes but
some hardware motor controller supports other features which are not
covered by this list of pre-defined attributes. Using Tango dynamic
attribute creation, a motor device may have extra attributes used to
get/set the motor hardware controller specific features. These are the
attributes specified on the controller with
:attr:`~sardana.pool.controller.Controller.axis_attribues`.

.. rubric:: The properties

- **Sleep_before_last_read** : This property exposes the motor 
  *instability time*. It defines the time in milli-second that the software
  managing a motor movement will wait between it detects the end of the
  motion and the last motor position reading. 

.. rubric:: Getting motor state and limit switches using event

The simplest way to know if a motor is moving is to survey its state.
If the motor is moving, its state will be MOVING. When the motion is
over, its state will be back to ON (or ALARM if a limit switch has
been reached). The pool motor interface allows client interested by
motor state or motor limit switches value to use the Tango event
system subscribing to motor state change event. As soon as a motor
starts a motion, its state is changed to MOVING and an event is sent.
As soon as the motion is over, the motor state is updated ans another
event is sent. In the same way, as soon as a change in the limit
switches value is detected, a change event is sent to client(s) which
have subscribed to change event on the Limit_Switches attribute. 


.. rubric:: Reading the motor position attribute

For each motor, the key attribute is its position. Special care has
been taken on this attribute management. When the motor is not moving,
reading the Position attribute will generate calls to the controller
and therefore hardware access. When the motor is moving, its position
is automatically read every 100 milli-seconds and stored in the Tango
polling buffer. This means that a client reading motor Position
attribute while the motor is moving will get the position from the
Tango polling buffer and will not generate extra controller calls. It
is also possible to get a motor position using the Tango event system.
When the motor is moving, an event is sent to the registered clients
when the change event criterion is true. By default, this change event
criterion is set to be a difference in position of 5. It is tunable on
a motor basis using the classical motor Position attribute abs_change
property or at the pool device basis using its DefaultMotPos_AbsChange
property. Anyway, not more than 10 events could be sent by second.
Once the motion is over, the motor position is made unavailable from
the Tango polling buffer and is read a last time after a tunable
waiting time (Sleep_bef_last_read property). A forced change event
with this value is sent to clients using events. 
    """

    def __init__(self, dclass, name):
        """Constructor"""
        self.in_write_position = False
        PoolElementDevice.__init__(self, dclass, name)

    def init(self, name):
        PoolElementDevice.init(self, name)

    def _is_allowed(self, req_type):
        return PoolElementDevice._is_allowed(self, req_type)

    def get_motor(self):
        return self.element

    def set_motor(self, motor):
        self.element = motor

    motor = property(get_motor, set_motor)

    def set_write_dial_position_to_db(self):
        dial = self.motor.get_dial_position_attribute()
        if dial.has_write_value():
            data = dict(DialPosition=dict(__value=dial.w_value, __value_ts=dial.w_timestamp))
            db = self.get_database()
            db.put_device_attribute_property(self.get_name(), data)

    def get_write_dial_position_from_db(self):
        name = 'DialPosition'
        db = self.get_database()
        pos_props = db.get_device_attribute_property(self.get_name(), name)[name]
        w_pos = pos_props["__value"][0]

        _, _, attr_info = self.get_dynamic_attributes()[0][name]
        w_pos = str_to_value(w_pos, attr_info.dtype, attr_info.dformat)

        w_pos, w_ts = float(pos_props["__value"][0]), None
        if "__value_ts" in pos_props:
            w_ts = float(pos_props["__value_ts"][0])
        return w_pos, w_ts

    @DebugIt()
    def delete_device(self):
        PoolElementDevice.delete_device(self)
        motor = self.motor
        if motor is not None:
            motor.remove_listener(self.on_motor_changed)

    @DebugIt()
    def init_device(self):
        PoolElementDevice.init_device(self)
        motor = self.motor
        if motor is None:
            full_name = self.get_full_name()
            name = self.alias or full_name
            self.motor = motor = \
                self.pool.create_element(type="Motor", name=name,
                    full_name=full_name, id=self.Id, axis=self.Axis,
                    ctrl_id=self.Ctrl_id)
            if self.instrument is not None:
                motor.set_instrument(self.instrument)
            # if in constructor, for all memorized no init attributes (position)
            # let poolmotor know their write values
            if self.in_constructor:
                try:
                    w_pos, w_ts = self.get_write_dial_position_from_db()
                    self.in_write_position = True
                    try:
                        motor.set_write_position(w_pos, timestamp=w_ts)
                    finally:
                        self.in_write_position = False
                except KeyError:
                    pass

        if self.Sleep_bef_last_read > 0:
            motor.set_instability_time(self.Sleep_bef_last_read / 1000.0)
        motor.add_listener(self.on_motor_changed)
        self.set_state(DevState.ON)

    def on_motor_changed(self, event_source, event_type, event_value):
        try:
            self._on_motor_changed(event_source, event_type, event_value)
        except not DevFailed:
            msg = 'Error occurred "on_motor_changed(%s.%s): %s"'
            exc_info = sys.exc_info()
            self.error(msg, self.motor.name, event_type.name,
                       exception_str(*exc_info[:2]))
            self.debug("Details", exc_info=exc_info)

    def _on_motor_changed(self, event_source, event_type, event_value):
        # during server startup and shutdown avoid processing element
        # creation events
        if SardanaServer.server_state != State.Running:
            return

        timestamp = time.time()
        name = event_type.name.lower()

        if name == "w_position" and not self.in_write_position:
            self.debug("Storing dial set point: %s", self.motor.dial_position.w_value)
            self.set_write_dial_position_to_db()
            return

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
            state = self.motor.get_state(propagate=0)

            if name == "position":
                w_value = event_source.get_position_attribute().w_value
                if state == State.Moving:
                    quality = AttrQuality.ATTR_CHANGING
            elif name == "dialposition" and state == State.Moving:
                quality = AttrQuality.ATTR_CHANGING

        self.set_attribute(attr, value=value, w_value=w_value,
                           timestamp=timestamp, quality=quality,
                           priority=priority, error=error, synch=False)

    def always_executed_hook(self):
        pass

    def read_attr_hardware(self, data):
        pass

    def get_dynamic_attributes(self):
        cache_built = hasattr(self, "_dynamic_attributes_cache")

        std_attrs, dyn_attrs = \
            PoolElementDevice.get_dynamic_attributes(self)

        if not cache_built:
            # For position attribute, listen to what the controller says for data
            # type (between long and float)
            pos = std_attrs.get('position')
            if pos is not None:
                _, data_info, attr_info = pos
                ttype, _ = to_tango_type_format(attr_info.dtype)
                data_info[0][0] = ttype
        return std_attrs, dyn_attrs

    def initialize_dynamic_attributes(self):
        attrs = PoolElementDevice.initialize_dynamic_attributes(self)

        detect_evts = "position", "dialposition",
        non_detect_evts = "limit_switches", "step_per_unit", "offset", \
            "sign", "velocity", "acceleration", "deceleration", "base_rate", \
            "backlash"

        for attr_name in detect_evts:
            if attr_name in attrs:
                self.set_change_event(attr_name, True, True)
        for attr_name in non_detect_evts:
            if attr_name in attrs:
                self.set_change_event(attr_name, True, False)

    def read_Position(self, attr):
        motor = self.motor
        use_cache = motor.is_in_operation() and not self.Force_HW_Read
        state = motor.get_state(cache=use_cache, propagate=0)
        position = motor.get_position(cache=use_cache, propagate=0)
        if position.error:
            Except.throw_python_exception(*position.exc_info)
        quality = None
        if state == State.Moving:
            quality = AttrQuality.ATTR_CHANGING
        self.set_attribute(attr, value=position.value, w_value=position.w_value,
                           quality=quality, priority=0,
                           timestamp=position.timestamp)

    def write_Position(self, attr):
        self.in_write_position = True
        position = attr.get_write_value()
        try:
            self.info("write_Position(%s)", position)
            try:
                self.wait_for_operation()
            except:
                raise Exception("Cannot move: already in motion")
            try:
                self.motor.position = position
            except PoolException, pe:
                throw_sardana_exception(pe)

            # manually store write dial position in the database
            self.set_write_dial_position_to_db()
        finally:
            self.in_write_position = False

    def read_Acceleration(self, attr):
        attr.set_value(self.motor.get_acceleration(cache=False))

    @memorize_write_attribute
    def write_Acceleration(self, attr):
        self.motor.acceleration = attr.get_write_value()

    def read_Deceleration(self, attr):
        attr.set_value(self.motor.get_deceleration(cache=False))

    @memorize_write_attribute
    def write_Deceleration(self, attr):
        self.motor.deceleration = attr.get_write_value()

    def read_Base_rate(self, attr):
        attr.set_value(self.motor.get_base_rate(cache=False))

    @memorize_write_attribute
    def write_Base_rate(self, attr):
        self.motor.base_rate = attr.get_write_value()

    def read_Velocity(self, attr):
        attr.set_value(self.motor.get_velocity(cache=False))

    @memorize_write_attribute
    def write_Velocity(self, attr):
        self.motor.velocity = attr.get_write_value()

    def read_Offset(self, attr):
        attr.set_value(self.motor.get_offset(cache=False).value)

    @memorize_write_attribute
    def write_Offset(self, attr):
        self.motor.offset = attr.get_write_value()

    def read_DialPosition(self, attr):
        motor = self.motor
        use_cache = motor.is_in_operation() and not self.Force_HW_Read
        state = motor.get_state(cache=use_cache, propagate=0)
        dial_position = motor.get_dial_position(cache=use_cache, propagate=0)
        if dial_position.error:
            Except.throw_python_exception(*dial_position.exc_info)
        quality = None
        if state == State.Moving:
            quality = AttrQuality.ATTR_CHANGING
        self.set_attribute(attr, value=dial_position.value, quality=quality,
                           priority=0, timestamp=dial_position.timestamp)

    def read_Step_per_unit(self, attr):
        attr.set_value(self.motor.get_step_per_unit(cache=False))

    @memorize_write_attribute
    def write_Step_per_unit(self, attr):
        step_per_unit = attr.get_write_value()
        self.motor.step_per_unit = step_per_unit

    def read_Backlash(self, attr):
        attr.set_value(self.motor.get_backlash(cache=False))

    @memorize_write_attribute
    def write_Backlash(self, attr):
        self.motor.backlash = attr.get_write_value()

    def read_Sign(self, attr):
        sign = self.motor.get_sign(cache=False).value
        attr.set_value(sign)

    @memorize_write_attribute
    def write_Sign(self, attr):
        self.motor.sign = attr.get_write_value()

    def read_Limit_switches(self, attr):
        motor = self.motor
        use_cache = motor.is_in_operation() and not self.Force_HW_Read
        limit_switches = motor.get_limit_switches(cache=use_cache)
        self.set_attribute(attr, value=limit_switches.value, priority=0,
                           timestamp=limit_switches.timestamp)

    def DefinePosition(self, argin):
        self.motor.define_position(argin)

        # update write value of position attribute
        pos_attr = self.get_wattribute_by_name("position")
        pos_attr.set_write_value(argin)

    def is_DefinePosition_allowed(self):
        if self.get_state() in (DevState.FAULT, DevState.MOVING,
                                DevState.UNKNOWN):
            return False
        return True

    def SaveConfig(self):
        raise NotImplementedError

    def is_SaveConfig_allowed(self):
        if self.get_state() in (DevState.FAULT, DevState.MOVING,
                                DevState.UNKNOWN):
            return False
        return True

    def MoveRelative(self, argin):
        raise NotImplementedError

    def is_MoveRelative_allowed(self):
        if self.get_state() in (DevState.FAULT, DevState.MOVING,
                                DevState.UNKNOWN):
            return False
        return True

    def get_attributes_to_restore(self):
        """Make sure position is the last attribute to restore"""
        restore_attributes = PoolElementDevice.get_attributes_to_restore(self)
        try:
            restore_attributes.remove('Position')
            restore_attributes.append('Position')
        except ValueError:
            pass
        return restore_attributes

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
        'Sleep_bef_last_read' : [DevLong,
            "Number of mS to sleep before the last read during a motor "
            "movement", 0],
        '_Acceleration' : [DevDouble, "", -1],
        '_Deceleration' : [DevDouble, "", -1],
        '_Velocity'     : [DevDouble, "", -1],
        '_Base_rate'    : [DevDouble, "", -1],
    }
    device_property_list.update(PoolElementDeviceClass.device_property_list)

    #    Command definitions
    cmd_list = {
        'DefinePosition' : [ [DevDouble, "New position"], [DevVoid, ""] ],
        'SaveConfig'     : [ [DevVoid, ""], [DevVoid, ""] ],
        'MoveRelative'   : [ [DevDouble, "amount to move"], [DevVoid, ""] ],
    }
    cmd_list.update(PoolElementDeviceClass.cmd_list)

    #    Attribute definitions
    attr_list = {}
    attr_list.update(PoolElementDeviceClass.attr_list)

    standard_attr_list = {
        'Position'     : [ [ DevDouble, SCALAR, READ_WRITE ],
                           { 'abs_change' : '1.0', } ],
        'Acceleration' : [ [ DevDouble, SCALAR, READ_WRITE ],
                           { 'Memorized'     : "true", } ],
        'Deceleration' : [ [ DevDouble, SCALAR, READ_WRITE ],
                           { 'Memorized'     : "true", } ],
        'Base_rate'    : [ [ DevDouble, SCALAR, READ_WRITE ],
                           { 'Memorized'     : "true",
                             'label'         : 'Base rate', } ],
        'Velocity'     : [ [ DevDouble, SCALAR, READ_WRITE ],
                           { 'Memorized'     : "true", } ],
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
    standard_attr_list.update(PoolElementDeviceClass.standard_attr_list)

    def _get_class_properties(self):
        ret = PoolElementDeviceClass._get_class_properties(self)
        ret['Description'] = "Motor device class"
        ret['InheritedFrom'].insert(0, 'PoolElementDevice')
        return ret

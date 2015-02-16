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

"""This module is part of the Python Pool libray. It defines the base classes
for"""

__all__ = ["PoolMotor"]

__docformat__ = 'restructuredtext'

import time
import math

from sardana import EpsilonError, State, ElementType
from sardana.sardanaattribute import SardanaAttribute, ScalarNumberAttribute, \
    SardanaSoftwareAttribute
from sardana.sardanaevent import EventType
from sardana.sardanautils import assert_type, is_number
from sardana.pool.poolelement import PoolElement
from sardana.pool.poolmotion import PoolMotion, MotionState


class Position(SardanaAttribute):

    def __init__(self, *args, **kwargs):
        super(Position, self).__init__(*args, **kwargs)
        self.get_offset().add_listener(self.on_change)
        self.get_sign().add_listener(self.on_change)
        self.get_dial().add_listener(self.on_change)

    def get_dial(self):
        return self.obj.get_dial_position_attribute()

    def get_offset(self):
        return self.obj.get_offset_attribute()

    def get_sign(self):
        return self.obj.get_sign_attribute()

    def _in_error(self):
        return self.get_dial().in_error()

    def _has_value(self):
        return self.get_dial().has_value()

    def _has_write_value(self):
        return self.get_dial().has_write_value()

    def _get_value(self):
        return self.calc_position()

    def _get_write_value(self):
        dial = self.get_dial().get_write_value()
        return self.calc_position(dial=dial)

    def _set_value(self, value, exc_info=None, timestamp=None, propagate=1):
        raise Exception("Cannot set position value for %s" % self.obj.name)

    def _set_write_value(self, w_value, timestamp=None, propagate=1):
        # let the write value be stored by dial using the current offset and
        # sign. This way, retrieving the write value is done in reverse applying
        # the offset and sign in use at that time
        w_dial = self.calc_dial_position(w_value)
        self.get_dial().set_write_value(w_dial, timestamp=timestamp, propagate=0)
        self.fire_write_event(propagate=propagate)

    def _get_exc_info(self):
        return self.get_dial().get_exc_info()

    def _get_timestamp(self):
        return self.get_dial().get_timestamp()

    def _get_write_timestamp(self):
        return self.get_dial().get_write_timestamp()

    def calc_position(self, dial=None):
        """Returns the computed position from last the dial position from the
        given parameter or (if None), the last dial position obtained from
        hardware read. 
        
        :param dial: the new dial position [default: None, meaning use the
                     current dial position.
        :return: the computed user position
        :rtype: obj
        
        :raises:
            :exc:`Exception` if dial_position is None and no read value has
            been set yet"""
        obj = self.obj
        if dial is None:
            dial_attr = obj.dial_position
            if dial_attr.in_error():
                raise dial_attr.exc_info[1]
            dial = dial_attr.value
        if not is_number(dial):
            raise Exception("Controller returns not a number %s" % dial)
        sign, offset = obj.sign.value, obj.offset.value
        return sign * dial + offset

    def calc_dial_position(self, position=None):
        """Returns the dial position for the  given position. If position is
        not given (or is None) it uses this object's *write* value.
        
        :param position:
            the position to be converted to dial [default: None meaning use the
            this attribute's *write* value
        :type position: obj
        :return: the computed dial position
        :rtype: obj"""
        obj = self.obj
        if position is None:
            position = self.w_value
        sign, offset = obj.sign.value, obj.offset.value
        return (position - offset) / sign

    def calc_motion(self, new_position):
        """Calculate the motor position, dial position, backlash for the
        given final position."""
        obj = self.obj
        ctrl = obj.controller
        step_per_unit = obj._step_per_unit
        backlash = obj._backlash

        # compute dial position
        new_dial = self.calc_dial_position(new_position)

        # add backlash if necessary
        do_backlash = False

        if obj.has_backlash() and not ctrl.has_backlash():
            dial_attr = self.get_dial()

            if dial_attr.in_error():
                raise dial_attr.get_exc_info()[1]

            old_dial = dial_attr.value
            displacement = new_dial - old_dial

            if math.fabs(displacement) > EpsilonError:
                positive_displacement = displacement > 0
                positive_backlash = self.is_backlash_positive()
                do_backlash = positive_backlash != positive_displacement
                if do_backlash:
                    new_dial = new_dial - backlash / step_per_unit

        # compute a rounding value if necessary
        if ctrl.wants_rounding():
            nb_step = round(new_dial * step_per_unit)
            new_dial = nb_step / step_per_unit

        backlash_position = new_dial
        if do_backlash:
            backlash_position = new_dial + backlash / step_per_unit

        return new_position, new_dial, do_backlash, backlash_position

    def on_change(self, evt_src, evt_type, evt_value):
        self.fire_read_event(propagate=evt_type.priority)

    def update(self, cache=True, propagate=1):
        self.get_dial().update(cache=cache, propagate=propagate)


class DialPosition(ScalarNumberAttribute):

    def update(self, cache=True, propagate=1):
        if not cache or not self.has_value():
            dial_position_value = self.obj.read_dial_position()
            self.set_value(dial_position_value, propagate=propagate)


class LimitSwitches(ScalarNumberAttribute):
    pass


class Offset(SardanaSoftwareAttribute):
    pass


class Sign(SardanaSoftwareAttribute):
    pass


class PoolMotor(PoolElement):
    """An internal Motor object. **NOT** part of the official API. Accessing
    this object from a controller plug-in may lead to undetermined behavior
    like infinite recursion."""

    def __init__(self, **kwargs):
        kwargs['elem_type'] = ElementType.Motor
        PoolElement.__init__(self, **kwargs)
        on_change = self.on_change
        self._offset = Offset(self, initial_value=0, listeners=on_change)
        self._sign = Sign(self, initial_value=1, listeners=on_change)
        self._dial_position = DialPosition(self, listeners=on_change)
        self._position = Position(self, listeners=on_change)
        self._backlash = 0
        self._step_per_unit = 1.0
        self._limit_switches = LimitSwitches(self, name="Limit_switches",
                                             initial_value=3 * (False,),
                                             listeners=on_change)
        self._acceleration = None
        self._deceleration = None
        self._velocity = None
        self._base_rate = None
        self._instability_time = None
        self._in_start_move = False
        motion_name = "%s.Motion" % self._name
        self.set_action_cache(PoolMotion(self, motion_name))

    # --------------------------------------------------------------------------
    # Event forwarding
    # --------------------------------------------------------------------------

    def on_change(self, evt_src, evt_type, evt_value):
        # forward all events coming from attributes to the listeners
        self.fire_event(evt_type, evt_value)

    # --------------------------------------------------------------------------
    # state information
    # --------------------------------------------------------------------------

    def _from_ctrl_state_info(self, state_info):
        state_info, _ = state_info

        try:
            state_str = State.whatis(state_info)
            return int(state_info), "{0} is in {1}".format(self.name, state_str), 0
        except KeyError:
            pass

        if len(state_info) > 2:
            state, status, ls = state_info[:3]
        else:
            state, other = state_info[:2]
            if is_number(other):
                ls, status = other, ''
            else:
                ls, status = 0, other
        state, ls = int(state), tuple(map(bool, (ls & 1, ls & 2, ls & 4)))
        return state, status, ls

    def _set_state_info(self, state_info, propagate=1):
        PoolElement._set_state_info(self, state_info, propagate=propagate)
        ls = state_info[-1]
        if self._sign.value < 0:
            ls = ls[0], ls[2], ls[1]
        self._set_limit_switches(ls, propagate=propagate)

    # --------------------------------------------------------------------------
    # state information
    # --------------------------------------------------------------------------

    _STD_STATUS = "{name} is {state}{limit_switches}{ctrl_status}"
    def calculate_state_info(self, state_info=None):
        if state_info is None:
            state = self._state
            status = self._status
            ls = self._limit_switches.value
        else:
            state, status, ls = state_info
        if state == State.On:
            state_str = "Stopped"
        elif state == State.Moving:
            state_str = "Moving"
            motion = self.get_operation()
            if motion is None:
                state_str += " (external)"
            else:
                motion_state = motion._motion_info[self].motion_state
                if motion_state == MotionState.MovingBacklash:
                    state_str += " (backlash)"
                elif motion_state == MotionState.MovingInstability:
                    state_str += " (instability)"
        else:
            state_str = "in " + State[state]

        limit_switches = ""
        if ls[0]:
            limit_switches += ". Hit home switch"
        if ls[1]:
            limit_switches += ". Hit upper switch"
        if ls[2]:
            limit_switches += ". Hit lower switch"

        if len(status) > 0:
            status = "\n" + status
        new_status = self._STD_STATUS.format(name=self.name, state=state_str,
                                             limit_switches=limit_switches,
                                             ctrl_status=status)
        return state, new_status, ls

    # --------------------------------------------------------------------------
    # limit switches
    # --------------------------------------------------------------------------

    def inspect_limit_switches(self):
        """returns the current (cached value of the limit switches

        :return: the current limit switches flags"""
        return self._limit_switches

    def get_limit_switches(self, cache=True, propagate=1):
        """Returns the motor limit switches state.

        :param cache:
            if ``True`` (default) return value in cache, otherwise read value
            from hardware
        :type cache:
            bool
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int
        :return:
            the motor limit switches state
        :rtype:
            :class:`~sardana.sardanaattribute.SardanaAttribute`"""
        self.get_state(cache=cache, propagate=propagate)
        return self._limit_switches

    def set_limit_switches(self, ls, propagate=1):
        self._set_limit_switches(ls, propagate=propagate)

    def put_limit_switches(self, ls, propagate=1):
        self._limit_switches = tuple(ls)

    def _set_limit_switches(self, ls, propagate=1):
        self._limit_switches.set_value(tuple(ls), propagate=propagate)

    limit_switches = property(get_limit_switches, set_limit_switches,
                              doc="motor limit switches")

    # --------------------------------------------------------------------------
    # instability time
    # --------------------------------------------------------------------------

    def has_instability_time(self, cache=True):
        it = self._instability_time
        return it is not None and it > 0.0

    def get_instability_time(self, cache=True):
        return self._instability_time

    def set_instability_time(self, instability_time, propagate=1):
        self._instability_time = instability_time
        if propagate > 0:
            self.fire_event(EventType("instability_time", priority=propagate),
                            instability_time)

    instability_time = property(get_instability_time, set_instability_time,
                                doc="motor instability time")

    # --------------------------------------------------------------------------
    # backlash
    # --------------------------------------------------------------------------

    def has_backlash(self, cache=True):
        return self._backlash != 0

    def is_backlash_positive(self, cache=True):
        return self._backlash > 0

    def is_backlash_negative(self, cache=True):
        return self._backlash < 0

    def get_backlash(self, cache=True):
        return self._backlash

    def set_backlash(self, backlash, propagate=1):
        self._backlash = backlash
        if propagate > 0:
            self.fire_event(EventType("backlash", priority=propagate), backlash)

    backlash = property(get_backlash, set_backlash, doc="motor backlash")

    # --------------------------------------------------------------------------
    # offset
    # --------------------------------------------------------------------------

    def get_offset_attribute(self):
        return self._offset

    def get_offset(self, cache=True):
        return self._offset

    def set_offset(self, offset, propagate=1):
        self._offset.set_value(offset, propagate=propagate)

    offset = property(get_offset, set_offset, doc="motor offset")

    # --------------------------------------------------------------------------
    # sign
    # --------------------------------------------------------------------------

    def get_sign_attribute(self):
        return self._sign

    def get_sign(self, cache=True):
        return self._sign

    def set_sign(self, sign, propagate=1):
        old_sign = self._sign.value
        self._sign.set_value(sign, propagate=propagate)
        # invert lower with upper limit switches and send event in case of change
        ls = self._limit_switches
        if old_sign != sign and ls.has_value():
            value = ls.value
            value = value[0], value[2], value[1]
            self._set_limit_switches(value, propagate=propagate)

    sign = property(get_sign, set_sign, doc="motor sign")

    # --------------------------------------------------------------------------
    # step per unit
    # --------------------------------------------------------------------------

    def get_step_per_unit(self, cache=True, propagate=1):
        if not cache or self._step_per_unit is None:
            step_per_unit = self.read_step_per_unit()
            self._set_step_per_unit(step_per_unit, propagate=propagate)
        return self._step_per_unit

    def set_step_per_unit(self, step_per_unit, propagate=1):
        if step_per_unit <= 0.0:
            raise Exception("Step per unit must be > 0.0")
        self.controller.set_axis_par(self.axis, "step_per_unit", step_per_unit)
        self._set_step_per_unit(step_per_unit, propagate=propagate)

    def _set_step_per_unit(self, step_per_unit, propagate=1):
        self._step_per_unit = step_per_unit
        if propagate:
            self.fire_event(EventType("step_per_unit", priority=propagate), step_per_unit)
            # force ask controller for new position to send priority event
            self.get_position(cache=False, propagate=2)

    def read_step_per_unit(self):
        step_per_unit = self.controller.get_axis_par(self.axis, "step_per_unit")
        assert_type(float, step_per_unit)
        return step_per_unit

    step_per_unit = property(get_step_per_unit, set_step_per_unit,
                             doc="motor steps per unit")

    # --------------------------------------------------------------------------
    # acceleration
    # --------------------------------------------------------------------------

    def get_acceleration(self, cache=True, propagate=1):
        if not cache or self._acceleration is None:
            acceleration = self.read_acceleration()
            self._set_acceleration(acceleration, propagate=propagate)
        return self._acceleration

    def set_acceleration(self, acceleration, propagate=1):
        self.controller.set_axis_par(self.axis, "acceleration", acceleration)
        self._set_acceleration(acceleration, propagate=propagate)

    def _set_acceleration(self, acceleration, propagate=1):
        self._acceleration = acceleration
        if not propagate:
            return
        self.fire_event(EventType("acceleration", priority=propagate), acceleration)

    def read_acceleration(self):
        acceleration = self.controller.get_axis_par(self.axis, "acceleration")
        assert_type(float, acceleration)
        return acceleration

    acceleration = property(get_acceleration, set_acceleration,
                            doc="motor acceleration")

    # --------------------------------------------------------------------------
    # deceleration
    # --------------------------------------------------------------------------

    def get_deceleration(self, cache=True, propagate=1):
        if not cache or self._deceleration is None:
            deceleration = self.read_deceleration()
            self._set_deceleration(deceleration, propagate=propagate)
        return self._deceleration

    def set_deceleration(self, deceleration, propagate=1):
        self.controller.set_axis_par(self.axis, "deceleration", deceleration)
        self._set_deceleration(deceleration, propagate=propagate)

    def _set_deceleration(self, deceleration, propagate=1):
        self._deceleration = deceleration
        if not propagate:
            return
        self.fire_event(EventType("deceleration", priority=propagate), deceleration)

    def read_deceleration(self):
        deceleration = self.controller.get_axis_par(self.axis, "deceleration")
        assert_type(float, deceleration)
        return deceleration

    deceleration = property(get_deceleration, set_deceleration,
                            doc="motor deceleration")
    # --------------------------------------------------------------------------
    # base_rate
    # --------------------------------------------------------------------------

    def get_base_rate(self, cache=True, propagate=1):
        if not cache or self._base_rate is None:
            base_rate = self.read_base_rate()
            self._set_base_rate(base_rate, propagate=propagate)
        return self._base_rate

    def set_base_rate(self, base_rate, propagate=1):
        self.controller.set_axis_par(self.axis, "base_rate", base_rate)
        self._set_base_rate(base_rate, propagate=propagate)

    def _set_base_rate(self, base_rate, propagate=1):
        self._base_rate = base_rate
        if not propagate:
            return
        self.fire_event(EventType("base_rate", priority=propagate), base_rate)

    def read_base_rate(self):
        base_rate = self.controller.get_axis_par(self.axis, "base_rate")
        assert_type(float, base_rate)
        return base_rate

    base_rate = property(get_base_rate, set_base_rate,
                         doc="motor base rate")

    # --------------------------------------------------------------------------
    # velocity
    # --------------------------------------------------------------------------

    def get_velocity(self, cache=True, propagate=1):
        if not cache or self._velocity is None:
            velocity = self.read_velocity()
            self._set_velocity(velocity, propagate=propagate)
        return self._velocity

    def set_velocity(self, velocity, propagate=1):
        self.controller.set_axis_par(self.axis, "velocity", velocity)
        self._set_velocity(velocity, propagate=propagate)

    def _set_velocity(self, velocity, propagate=1):
        self._velocity = velocity
        if not propagate:
            return
        self.fire_event(EventType("velocity", priority=propagate), velocity)

    def read_velocity(self):
        velocity = self.controller.get_axis_par(self.axis, "velocity")
        assert_type(float, velocity)
        return velocity

    velocity = property(get_velocity, set_velocity,
                        doc="motor velocity")

    # --------------------------------------------------------------------------
    # position & dial position
    # --------------------------------------------------------------------------

    def define_position(self, position):
        dial = self.get_position_attribute().calc_dial_position(position)
        self.controller.define_position(self.axis, dial)
        # force an event with the new position
        self.get_position(cache=False, propagate=2)

    def get_position_attribute(self):
        """Returns the position attribute object for this motor
        
        :return: the position attribute
        :rtype: :class:`~sardana.sardanaattribute.SardanaAttribute`"""
        return self._position

    def get_position(self, cache=True, propagate=1):
        """Returns the user position.

        :param cache:
            if ``True`` (default) return value in cache, otherwise read value
            from hardware
        :type cache:
            bool
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int
        :return:
            the user position
        :rtype:
            :class:`~sardana.sardanaattribute.SardanaAttribute`"""
        position = self._position
        position.update(cache=cache, propagate=propagate)
        return position

    def set_position(self, position):
        """Moves the motor to the specified user position

        :param position:
            the user position to move to
        :type position:
            :class:`~numbers.Number`"""
        self.start_move(position)

    def set_write_position(self, w_position, timestamp=None, propagate=1):
        """Sets a new write value for the user position.

        :param w_position:
            the new write value for user position
        :type w_position:
            :class:`~numbers.Number`
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int"""
        self._position.set_write_value(w_position, timestamp=timestamp,
                                       propagate=propagate)

    def read_dial_position(self):
        """Reads the dial position from hardware.

        :return:
            a :class:`~sardana.sardanavalue.SardanaValue` containing the dial
            position
        :rtype:
            :class:`~sardana.sardanavalue.SardanaValue`"""
        return self.motion.read_dial_position(serial=True)[self]

    def put_dial_position(self, dial_position_value, propagate=1):
        """Sets a new dial position.

        :param dial_position_value:
            the new dial position value
        :type dial_position_value:
            :class:`~sardana.sardanavalue.SardanaValue`
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int"""
        dp = self._dial_position
        dp.set_value(dial_position_value, propagate=propagate)
        return dp

    def get_dial_position_attribute(self):
        """Returns the dial position attribute object for this motor
        
        :return: the dial position attribute
        :rtype: :class:`~sardana.sardanaattribute.SardanaAttribute`"""
        return self._dial_position

    def get_dial_position(self, cache=True, propagate=1):
        """Returns the dial position.

        :param cache:
            if ``True`` (default) return value in cache, otherwise read value
            from hardware
        :type cache:
            bool
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int
        :return:
            the dial position
        :rtype:
            :class:`~sardana.sardanaattribute.SardanaAttribute`"""
        dp = self._dial_position
        dp.update(cache=cache, propagate=propagate)
        return dp

    position = property(get_position, set_position, doc="motor user position")
    dial_position = property(get_dial_position, doc="motor dial position")

    # --------------------------------------------------------------------------
    # default acquisition channel
    # --------------------------------------------------------------------------

    def get_default_attribute(self):
        return self.get_position_attribute()

    # --------------------------------------------------------------------------
    # motion
    # --------------------------------------------------------------------------

    def get_motion(self):
        return self.get_action_cache()

    motion = property(get_motion, doc="motion object")

    # --------------------------------------------------------------------------
    # motion calculation
    # --------------------------------------------------------------------------

    def calculate_motion(self, new_position, items=None, calculated=None):
        """Calculate the motor position, dial position, backlash for the
        given final position. Items specifies the where to put the calculated
        values, calculated is not used by physical motors"""

        step_per_unit = self._step_per_unit
        backlash = self._backlash
        ctrl = self.controller
        pos_attr = self.get_position_attribute()

        # compute dial position
        new_dial = pos_attr.calc_dial_position(new_position)

        # add backlash if necessary
        do_backlash = False

        if self.has_backlash() and not ctrl.has_backlash():
            dial_attr = self.get_dial_position_attribute()

            if dial_attr.in_error():
                raise dial_attr.get_exc_info()[1]

            old_dial = dial_attr.value
            displacement = new_dial - old_dial

            if math.fabs(displacement) > EpsilonError:
                positive_displacement = displacement > 0
                positive_backlash = self.is_backlash_positive()
                do_backlash = positive_backlash != positive_displacement
                if do_backlash:
                    new_dial = new_dial - backlash / step_per_unit

        # compute a rounding value if necessary
        if ctrl.wants_rounding():
            nb_step = round(new_dial * step_per_unit)
            new_dial = nb_step / step_per_unit

        backlash_position = new_dial
        if do_backlash:
            backlash_position = new_dial + backlash / step_per_unit

        if items is None:
            items = {}
        items[self] = new_position, new_dial, do_backlash, backlash_position
        return items

    def start_move(self, new_position):
        self._in_start_move = True
        try:
            return self._start_move(new_position)
        finally:
            self._in_start_move = False

    def _start_move(self, new_position):
        if not self._simulation_mode:
            # update the dial value from the controller in case motor has been
            # moved outside sardana.
            # TODO: also update step_per_unit
            self.get_dial_position_attribute().update(cache=False, propagate=1)

            # calculate the motion (dial position, backlash, etc)
            items = self.calculate_motion(new_position)
            self.debug("Start motion user=%f, dial=%f, backlash? %s, "
                       "dial_backlash=%f", *items[self])

            timestamp = time.time()
            # update the write position
            self.set_write_position(items[self][0], timestamp=timestamp, propagate=0)

            # move!
            self.motion.run(items=items)

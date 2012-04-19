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

"""This module is part of the Python Pool libray. It defines the base classes
for"""

__all__ = [ "PoolMotor" ]

__docformat__ = 'restructuredtext'

import math
import operator
import numbers

from sardana import EpsilonError, State, ElementType, \
    is_number
from sardana.sardanaattribute import SardanaAttribute, ScalarNumberAttribute, \
    SardanaSoftwareAttribute
from sardana.sardanaevent import EventType

from poolelement import PoolElement
from poolmotion import PoolMotion, PoolMotionItem, MotionState, MotionMap

class Position(SardanaAttribute):
    pass

class DialPosition(ScalarNumberAttribute):
    pass

class LimitSwitches(ScalarNumberAttribute):
    pass

class Offset(SardanaSoftwareAttribute):
    pass

class Sign(SardanaSoftwareAttribute):
    pass

class PoolMotor(PoolElement):
    """An internal Motor object. **NOT** part of the official API. Accessing
    this object from a controller plugin may lead to undetermined behaviour like
    infinite recursion."""
    
    def __init__(self, **kwargs):
        PoolElement.__init__(self, **kwargs)
        self._position = Position(self)
        self._dial_position = DialPosition(self)
        self._offset = Offset(self, initial_value=0)
        self._sign = Sign(self, initial_value=1)
        self._backlash = 0
        self._step_per_unit = 1.0
        self._limit_switches = LimitSwitches(self, name="Limit_switches",
                                             initial_value=3*(False,))
        self._acceleration = None
        self._deceleration = None
        self._velocity = None
        self._base_rate = None
        self._instability_time = None
        motion_name = "%s.Motion" % self._name
        self.set_action_cache(PoolMotion(self, motion_name))
    
    def get_type(self):
        return ElementType.Motor
    
    # --------------------------------------------------------------------------
    # state information
    # --------------------------------------------------------------------------
    
    def _from_ctrl_state_info(self, state_info):
        state_info, error = state_info
        if len(state_info) > 2:
            state, status, ls = state_info[:3]
        else:
            state, other = state_info[:2]
            if operator.isNumberType(other):
                ls, status = other, ''
            else:
                ls, status = 0, other
        state, ls = int(state), tuple(map(bool, (ls&1,ls&2,ls&4)))
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
            state, status, ls = self._state, self._status, self._limit_switches.value
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
                              doc="motor limit_switches")
    
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
                                doc="motor instability_time")
    
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
    
    def get_offset(self, cache=True):
        return self._offset
    
    def set_offset(self, offset, propagate=1):
        self._offset.set_value(offset, propagate=propagate)
        # recalculate position and send event
        position, exc_info = self.to_user_position(offset=self._offset)
        self._position.set_value(position, exc_info=exc_info,
                                 propagate=propagate)
    
    offset = property(get_offset, set_offset, doc="motor offset")
    
    # --------------------------------------------------------------------------
    # sign
    # --------------------------------------------------------------------------
    
    def get_sign(self, cache=True):
        return self._sign
    
    def set_sign(self, sign, propagate=1):
        self._sign.set_value(sign, propagate=propagate)
        # recalculate position and send event
        position, exc_info = self.to_user_position(sign=self._sign)
        self._position.set_value(position, exc_info=exc_info,
                                 propagate=propagate)
        # invert lower with upper limit switches and send event in case of change
        ls = self._limit_switches
        if ls.has_value():
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
        return self.controller.get_axis_par(self.axis, "step_per_unit")
    
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
        return self.controller.get_axis_par(self.axis, "acceleration")
    
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
        return self.controller.get_axis_par(self.axis, "deceleration")
    
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
        return self.controller.get_axis_par(self.axis, "base_rate")
    
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
        return self.controller.get_axis_par(self.axis, "velocity")
    
    velocity = property(get_velocity, set_velocity,
                        doc="motor velocity")
    
    # --------------------------------------------------------------------------
    # position & dial position
    # --------------------------------------------------------------------------
    
    def define_position(self, position):
        dial = (position - self.offset.value) / self.sign.value
        self.controller.define_position(self.axis, dial)
        self.get_position(cache=False, propagate=2)
    
    def to_user_position(self, dial_position=None, sign=None, offset=None):
        """Utility method to calculate user position from dial position, sign
        and offset.
        
        :param dial_position:
            the dial position. If None (default), the current dial position is
            used to calculate the user position
        :type dial_position:
            :class:`~sardana.sardanaattribute.SardanaAttribute` or
            :obj:`tuple` <:class:`~numbers.Number`/:obj:`None`, exc_info/:obj:`None`>
        :param sign:
            the sign. If None (default), the current sign is
            used to calculate the user position
        :type sign:
            :class:`~sardana.sardanaattribute.SardanaAttribute`
        :param offset:
            the offset. If None (default), the current offset is
            used to calculate the user position
        :type offset:
            :class:`~sardana.sardanaattribute.SardanaAttribute`
        
        :return:
            a tuple with user position or None and exc_info or None
        :rtype:
            :obj:`tuple` <:class:`~numbers.Number`/:obj:`None`, exc_info/:obj:`None`>"""
        if dial_position is None:
            dial_position = self.get_dial_position(propagate=0)
        if sign is None:
            sign = self.sign
        if offset is None:
            offset = self.offset
        
        sign, offset = sign.value, offset.value
        
        pos, exc_info = None, None
        if isinstance(dial_position, SardanaAttribute):
            if dial_position.error:
                exc_info = dial_position.exc_info
            else:
                pos = sign * dial_position.value + offset
        else:
            dp, exc_info = dial_position
            if is_number(dp):
                pos = sign * dp + offset
        return pos, exc_info
    
    def to_dial_position(self, position=None, sign=None, offset=None):
        """Utility method to calculate dial position from user position, sign
        and offset.
        
        :param position:
            the user position. If None (default), the current user position is
            used to calculate the dial position
        :type position:
            :class:`~sardana.sardanaattribute.SardanaAttribute` or
            :obj:`tuple` <:class:`~numbers.Number`/:obj:`None`, exc_info/:obj:`None`>
        :param sign:
            the sign. If None (default), the current sign is
            used to calculate the dial position
        :type sign:
            :class:`~sardana.sardanaattribute.SardanaAttribute`
        :param offset:
            the offset. If None (default), the current offset is
            used to calculate the dial position
        :type offset:
            :class:`~sardana.sardanaattribute.SardanaAttribute`
        
        :return:
            a tuple with dial position or None and exc_info or None
        :rtype:
            :obj:`tuple` <:class:`~numbers.Number`/:obj:`None`, exc_info/:obj:`None`>"""
        if position is None:
            position = self.get_position(propagate=0)
        if sign is None:
            sign = self.sign
        if offset is None:
            offset = self.offset
        
        sign, offset = sign.value, offset.value
        
        dp, exc_info = None, None
        if isinstance(position, SardanaAttribute):
            if position.error:
                exc_info = position.exc_info
            else:
                dp = (position.value - offset) / sign
        else:
            pos, exc_info = position
            if is_number(pos):
                dp = (pos - offset) / sign
        return dp, exc_info
    
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
        if not cache or not self._position.has_value():
            dial_position_info = self.read_dial_position()
            self._set_dial_position(dial_position_info, propagate=propagate)
        return self._position
    
    def set_position(self, position):
        """Moves the motor to the specified user position
        
        :param position:
            the user position to move to
        :type position:
            :class:`~numbers.Number`"""
        self._position.set_write_value(position)
        self.start_move(position)
    
    def put_position(self, position_info, propagate=1):
        """Sets a new user position.
           
        :param position_info:
            the new user position info
        :type position_info:
            :obj:`tuple` <:class:`~numbers.Number`/:obj:`None`, exc_info/:obj:`None`>
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int"""
        self._set_position(position_info, propagate=propagate)
    
    def _set_position(self, position_info, propagate=1):
        dial_position_info = self.to_dial_position(position=position_info)
        self._set_dial_position(dial_position_info, propagate=propagate)
        
    def read_dial_position(self):
        """Reads the dial position from hardware.
        
        :return:
            a tuple with dial position or None and exc_info or None
        :rtype:
            :obj:`tuple` <:class:`~numbers.Number`/:obj:`None`, exc_info/:obj:`None`>"""
        return self.motion.read_dial_position(serial=True)[self]
    
    def put_dial_position(self, dial_position_info, propagate=1):
        """Sets a new dial position.
           
        :param dial_position_info:
            the new dial position info
        :type dial_position_info:
            :obj:`tuple` <:class:`~numbers.Number`/:obj:`None`, exc_info/:obj:`None`>
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int"""
        self._set_dial_position(dial_position_info, propagate=propagate)
    
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
        if not cache or not self._dial_position.has_value():
            dial_position_info = self.read_dial_position()
            self._set_dial_position(dial_position_info, propagate=propagate)
        return self._dial_position
    
    def _set_dial_position(self, dial_position_info, propagate=1):
        """Sets a new dial position.
           
        :param dial_position_info:
            the new dial position
        :type dial_position_info:
            :obj:`tuple` <:class:`~numbers.Number`/:obj:`None`, exc_info/:obj:`None`>
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int"""
        self._dial_position.set_value(*dial_position_info, propagate=propagate)
        position_info = self.to_user_position(dial_position=self._dial_position)
        self._position.set_value(*position_info, propagate=propagate)
    
    position = property(get_position, set_position, doc="motor user position")
    dial_position = property(get_dial_position, doc="motor dial position")
    
    # --------------------------------------------------------------------------
    # default acquisition channel
    # --------------------------------------------------------------------------
    
    def get_default_acquisition_channel(self):
        return 'position'
    
    # --------------------------------------------------------------------------
    # motion
    # --------------------------------------------------------------------------
    
    def get_motion(self):
        return self.get_action_cache()
    
    motion = property(get_motion, doc="motion object")
    
    # --------------------------------------------------------------------------
    # motion calculation
    # --------------------------------------------------------------------------
    
    def calculate_motion(self, new_position, items=None):
        
        step_per_unit, backlash = self._step_per_unit, self._backlash
        
        ctrl = self.controller
        
        # compute dial position
        new_dial, exc_info = \
            self.to_dial_position(position=(new_position, None))
        
        # add backlash if necessary
        do_backlash = False
        
        if self.has_backlash() and not ctrl.has_backlash():
            # get the current dial position from HW (just in case the motor was
            # moved outside sardana)
            old_dial = self.get_dial_position(cache=False, propagate=0)
            
            if old_dial.in_error():
                raise old_dial.get_exc_info()[1]
            
            old_dial = old_dial.value
            displacement = new_dial - old_dial
            
            if math.fabs(displacement) > EpsilonError:
                positive_displacement = displacement > 0
                positive_backlash = self.is_backlash_positive()
                do_backlash = positive_backlash != positive_displacement
                if do_backlash:
                    new_dial = new_dial - backlash / step_per_unit
        
        # compute a rounding value if necessary
        if ctrl.wants_rounding():
            nb_step  = round(new_dial * step_per_unit)
            new_dial = nb_step / step_per_unit
        
        backlash_position = new_dial
        if do_backlash:
            backlash_position = new_dial + backlash / step_per_unit
        
        if items is None:
            items = {}
        items[self] = new_position, new_dial, do_backlash, backlash_position
        return items
    
    def start_move(self, new_position):
        if not self._simulation_mode:
            items = self.calculate_motion(new_position)
            self.debug("Start motion pos=%f, dial=%f, do_backlash=%s, "
                       "dial_backlash=%f", *items[self])
            self.motion.run(items=items)

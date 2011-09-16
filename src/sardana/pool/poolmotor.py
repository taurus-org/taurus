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

from sardana import EpsilonError, State
from poolbase import *

from pooldefs import ElementType
from poolevent import EventType
from poolelement import PoolElement
from poolmotion import PoolMotion, PoolMotionItem, MotionState, MotionMap


class PoolMotor(PoolElement):

    def __init__(self, **kwargs):
        PoolElement.__init__(self, **kwargs)
        self._position = None
        self._wposition = None
        self._dial_position = None
        self._offset = 0.0
        self._sign = 1
        self._backlash = 0
        self._step_per_unit = 1.0
        self._limit_switches = None
        self._limit_switches_event = None
        self._acceleration = None
        self._deceleration = None
        self._velocity = None
        self._base_rate = None
        self._instability_time = None
        motion_name = "%s.Motion" % self._name
        self.set_action_cache(PoolMotion(self.pool, motion_name))
    
    def get_type(self):
        return ElementType.Motor
    
    # --------------------------------------------------------------------------
    # state information
    # --------------------------------------------------------------------------
    
    def _from_ctrl_state_info(self, state_info):
        if len(state_info) > 2:
            state, status, ls = state_info[:3]
        else:
            state, other = state_info[:2]
            if operator.isNumberType(other):
                ls, status = other, ''
            else:
                ls, status = 0, other
        state, ls = int(state), tuple(map(bool, (ls&4,ls&2,ls&1)))
        return state, status, ls
    
    def _set_state_info(self, state_info, propagate=1):
        PoolElement._set_state_info(self, state_info, propagate=propagate)
        ls = state_info[-1]
        self._set_limit_switches(ls, propagate=propagate)
    
    # --------------------------------------------------------------------------
    # state information
    # --------------------------------------------------------------------------
    
    _STD_STATUS = "{name} is {state}{limit_switches}\n{ctrl_status}"
    def calculate_state_info(self, state_info=None):
        if state_info is None:
            state, status, ls = self._state, self._status, self._limit_switches
        else:
            state, status, ls = state_info
        if state == State.On:
            state_str = "Stopped"
        elif state == State.Moving:
            motion_state = self.motion._motion_info[self].motion_state
            state_str = "Moving"
            if motion_state == MotionState.MovingBacklash:
                state_str += " (backlash)"
            elif motion_state == MotionState.MovingInstability:
                state_str += " (instability)"
        else:
            state_str = State[state]
            
        
        limit_switches = ""
        if ls[0]:
            limit_switches += ". Hit home switch"
        if ls[1]:
            limit_switches += ". Hit upper switch"
        if ls[2]:
            limit_switches += ". Hit lower switch"

        new_status = self._STD_STATUS.format(name=self.name, state=state_str,
                                             limit_switches=limit_switches,
                                             ctrl_status=status)
        return state, new_status, ls
    
    # --------------------------------------------------------------------------
    # limit switches
    # --------------------------------------------------------------------------

    def inspect_limit_switches(self):
        return self._limit_switches
    
    def get_limit_switches(self, cache=True, propagate=1):
        self.get_state(cache=cache, propagate=propagate)
        return self._limit_switches
    
    def set_limit_switches(self, ls, propagate=1):
        self._set_limit_switches(ls, propagate=propagate)

    def put_limit_switches(self, ls, propagate=1):
        self._limit_switches = tuple(ls)
    
    def _set_limit_switches(self, ls, propagate=1):
        self._limit_switches = tuple(ls)
        if not propagate:
            return
        if ls == self._limit_switches_event:
            # current ls is equal to last ls_event. Skip event
            return
        self._limit_switches_event = ls
        self.fire_event(EventType("limit_switches", priority=propagate), ls)
    
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
        self._offset = offset
        if propagate:
            self.fire_event(EventType("offset", priority=propagate), offset)
        # recalculate position and send event
        self._position = self.to_user_position(offset=offset)
        if propagate:
            self.fire_event(EventType("position", priority=propagate), self._position)
    
    offset = property(get_offset, set_offset, doc="motor offset")
    
    # --------------------------------------------------------------------------
    # sign
    # --------------------------------------------------------------------------
    
    def get_sign(self, cache=True):
        return self._sign
    
    def set_sign(self, sign, propagate=1):
        self._sign = sign
        if propagate:
            self.fire_event(EventType("sign", priority=propagate), sign)
        # recalculate position and send event
        self._position = self.to_user_position(sign=sign)
        if propagate:
            self.fire_event(EventType("position", priority=propagate), self._position)
        # invert lower with upper limit switches and send event in case of change
        ls = self._limit_switches
        if ls is not None:
            self._set_limit_switches((ls[0],ls[2],ls[1]), propagate=propagate)
        
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
    
    def to_user_position(self, dial_position=None, sign=None, offset=None):
        """utility method to calculate user position from dial position, sign
        and offset"""
        if dial_position is None:
            dial_position = self.get_dial_position(propagate=0)
        if sign is None:
            sign = self.sign
        if offset is None:
            offset = self.offset
        position = sign * dial_position + offset
        return position

    def to_dial_position(self, position=None, sign=None, offset=None):
        """utility method to calculate dial position from user position, sign
        and offset"""
        if position is None:
            position = self.get_position(propagate=0)
        if sign is None:
            sign = self.sign
        if offset is None:
            offset = self.offset
        dial_position = (position - offset) / sign
        return dial_position
    
    def get_position(self, cache=True, propagate=1):
        if not cache or self._position is None:
            dial_position = self.read_dial_position()
            self._set_dial_position(dial_position, propagate=propagate)
        return self._position
    
    def set_position(self, position):
        self._wposition = position
        self.start_move(position)
    
    def put_position(self, position, propagate=1):
        self._set_position(position, propagate=propagate)
    
    def _set_position(self, position, propagate=1):
        dial_position = self.to_dial_position(position=position)
        self._set_dial_position(dial_position, propagate=propagate)
        
    def read_dial_position(self):
        return self.motion.read_dial_position(serial=True)[self]
    
    def put_dial_position(self, dial_position, propagate=1):
        self._set_dial_position(dial_position, propagate=propagate)
    
    def get_dial_position(self, cache=True, propagate=1):
        if not cache or self._dial_position is None:
            dial_position = self.read_dial_position()
            self._set_dial_position(dial_position, propagate=propagate)
        return self._dial_position

    def _set_dial_position(self, dial_position, propagate=1):
        self._dial_position = dial_position
        self._position = self.to_user_position(dial_position=dial_position)

        if not propagate:
            return
        self.fire_event(EventType("dial_position", priority=propagate), dial_position)
        self.fire_event(EventType("position", priority=propagate), self._position)
    
    position = property(get_position, set_position, doc="motor user position")
    dial_position = property(get_dial_position, doc="motor dial position")
    
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
        old_position = self.position
        old_dial = self.dial_position
        
        step_per_unit, backlash = self._step_per_unit, self._backlash
        
        ctrl = self.controller
        
        # compute dial position
        new_dial = self.to_dial_position(position=new_position)
        
        # add backlash if necessary
        do_backlash = False
        displacement = new_dial - old_dial
        if self.has_backlash() and \
           math.fabs(displacement) > EpsilonError and \
           not ctrl.has_backlash():
           
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
        self.prepare_to_move()
        if not self._simulation_mode:
            items = self.calculate_motion(new_position)
            self.debug("Start motion pos=%f, dial=%f, do_backlash=%s, "
                       "dial_backlash=%f", *items[self])
            self.motion.run(items=items)
    
    def prepare_to_move(self):
        self._aborted = False
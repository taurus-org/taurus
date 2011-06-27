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

__all__ = [ "PoolMotorGroup" ]

__docformat__ = 'restructuredtext'

import math

from poolbase import *
from pooldefs import *
from poolelement import *
from poolmotion import *
from poolmotor import *
from poolmoveable import *

class PhyElement(object):
    
    def __init__(self, pe, user_elem_indexes):
        self.pe = pe
        self.user_elem_indexes = user_elem_indexes

class UserElement(object):
    
    def __init__(self, pe, user_elem_indexes):
        self.pe = pe
        self.user_elem_indexes = user_elem_indexes


class PoolMotorGroup(PoolGroupElement):

    def __init__(self, **kwargs):
        PoolGroupElement.__init__(self, **kwargs)
        self._position = None
        self.set_action_cache(PoolMotion("%s.Motion" % self._name))
    
    def get_type(self):
        return ElementType.MotorGroup
    
    def on_element_changed(self, evt_src, evt_type, evt_value):
        pass
    
    def add_user_element(self, element, index=None):
        if not element.get_type() in (ElementType.Motor, ElementType.PseudoMotor):
            raise Exception("element %s is not a motor" % element.name)
        PoolGroupElement.add_user_element(self, element, index=index)
    
    # --------------------------------------------------------------------------
    # state information
    # --------------------------------------------------------------------------

    def _from_ctrl_state_info(self, state_info):
        state, ls = state_info[:2]
        state, ls = int(state), map(bool, (ls&4,ls&2,ls&1))
        if len(state_info) > 2:
            return state, state_info[2], ls
        return state, '', ls
    
    def _set_state_info(self, state_info, propagate=1):
        PoolElement._set_state_info(self, state_info[:2], propagate=propagate)
        ls = state_info[-1]
        self._set_limit_switches(ls, propagate=propagate)
    
    # --------------------------------------------------------------------------
    # position
    # --------------------------------------------------------------------------
    
    def get_position(self, cache=True, propagate=1):
        if not cache or self._position is None:
            dial_position = self.read_dial_position()
            self._set_dial_position(dial_position, propagate=propagate)
        return self._position
    
    def set_position(self, position):
        self.start_move(position)
    
    def put_position(self, position, propagate=1):
        self._set_position(position, propagate=propagate)
    
    def _set_position(self, position, propagate=1):
        dial_position = (position - self._offset) / self._sign
        self._set_dial_position(dial_position, propagate=propagate)
        
    def read_dial_position(self):
        return self.motion.read_dial_position()[self]
    
    def put_dial_position(self, dial_position, propagate=1):
        self._set_dial_position(dial_position, propagate=propagate)
    
    def get_dial_position(self, cache=True, propagate=1):
        if not cache or self._dial_position is None:
            dial_position = self.read_dial_position()
            self._set_dial_position(dial_position, propagate=propagate)
        return self._dial_position

    def _set_dial_position(self, dial_position, propagate=1):
        self._dial_position = dial_position
        self._position = self.sign * dial_position + self.offset

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
    
    def _calculate_move(self, new_position):
        old_position = self.position
        old_dial = self.dial_position
        
        ctrl = self.controller
        
        # compute dial position
        dial_pos = (new_position - self.offset) / self.sign
        
        # add backlash if necessary
        do_backlash = False
        displacement = dial_pos - old_dial
        if self.has_backlash() and \
           math.fabs(displacement) > pool.EpsilonError and \
           not ctrl.has_backlash():
           
            positive_displacement = displacement > 0
            positive_backlash = self.is_backlash_positive()
            do_backlash = (positive_backlash and not positive_displacement) or \
                          (not positive_backlash and positive_displacement)
            if do_backlash:
                dial_pos = dial_pos - self._backlash / self._step_per_unit
        
        # compute a rounding value if necessary
        if ctrl.wants_rounding():
            nb_step  = round(dial_pos * self._step_per_unit)
            dial_pos = nb_step / self._step_per_unit
        
        backlash_position = dial_pos
        if do_backlash:
            backlash_position = dial_pos + self._backlash / self._step_per_unit
        
        return new_position, dial_pos, do_backlash, backlash_position
    
    def start_move(self, new_position):
        self._aborted = False
        pos, dial, do_backlash, dial_backlash = self._calculate_move(new_position)
        if not self._simulation_mode:
            items = { self : (pos, dial, do_backlash, dial_backlash) }
            self.motion.run(items)
    


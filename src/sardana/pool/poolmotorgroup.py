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

from sardana import State, ElementType
from sardana.sardanaattribute import SardanaAttribute, SardanaSoftwareAttribute
from sardana.sardanaevent import EventType

from poolgroupelement import PoolGroupElement
from poolmotion import PoolMotion

from taurus.core.util import DebugIt


class PhyElement(object):
    
    def __init__(self, pe, user_elem_indexes):
        self.pe = pe
        self.user_elem_indexes = user_elem_indexes


class UserElement(object):
    
    def __init__(self, pe, user_elem_indexes):
        self.pe = pe
        self.user_elem_indexes = user_elem_indexes


class Position(SardanaAttribute):
    pass
    
    
class PoolMotorGroup(PoolGroupElement):

    def __init__(self, **kwargs):
        self._positions = {}
        self._physical_elements = []
        PoolGroupElement.__init__(self, **kwargs)
    
    def _create_action_cache(self):
        motion_name = "%s.Motion" % self._name
        return PoolMotion(self, motion_name)
        
    def get_type(self):
        return ElementType.MotorGroup
    
    def on_element_changed(self, evt_src, evt_type, evt_value):
        name = evt_type.name.lower()
        if name in ('state', 'position'):
            state, status = self._calculate_states()
            if name == 'state':
                propagate_state = evt_type.priority
            else:
                propagate_state = 0
            self.set_state(state, propagate=propagate_state)
            self.set_status(status, propagate=propagate_state)
            if name == 'position':
                self.put_element_position(evt_src, evt_value, propagate=1)
    
    def add_user_element(self, element, index=None):
        elem_type = element.get_type()
        if elem_type == ElementType.Motor:
            pass
        elif elem_type == ElementType.PseudoMotor:
            #TODO: make this happen
            pass
        else:
            raise Exception("element %s is not a motor" % element.name)
            
        PoolGroupElement.add_user_element(self, element, index=index)
    
    # --------------------------------------------------------------------------
    # position
    # --------------------------------------------------------------------------
    
    def get_position(self, cache=True, propagate=1):
        positions = self._positions
        if not cache or positions is None:
            dial_position_infos = self.motion.read_dial_position(serial=True)
            for motion_obj, position_info in dial_position_infos.items():
                motion_obj.put_dial_position(position_info, propagate=propagate)
            positions = {}
            for motion_obj in self.get_user_elements():
                positions[motion_obj] = motion_obj.get_position(propagate=0)
            self._set_position(positions, propagate=propagate)
        return positions

    def set_position(self, positions):
        self.start_move(positions)
    
    def put_position(self, positions, propagate=1):
        self._set_position(positions, propagate=propagate)
    
    def _set_position(self, positions, propagate=1):
        self._positions = positions
        if not propagate:
            return
        self.fire_event(EventType("position", priority=propagate), positions)
    
    def put_element_position(self, element, position, propagate=1):
        self._positions[element] = position
        if not propagate or len(self._positions) < len(self.get_user_elements()):
            return
        self.fire_event(EventType("position", priority=propagate), self._positions)
    
    position = property(get_position, set_position, doc="motor group positions")
    
    # --------------------------------------------------------------------------
    # motion
    # --------------------------------------------------------------------------

    def get_motion(self):
        return self.get_action_cache()
    
    motion = property(get_motion, doc="motion object")

    # --------------------------------------------------------------------------
    # motion calculation
    # --------------------------------------------------------------------------
    
    def start_move(self, new_positions):
        self._aborted = False
        if not self._simulation_mode:
            user_elements = self.get_user_elements()
            items = {}
            for new_position, element in zip(new_positions, user_elements):
                element.calculate_motion(new_position, items=items)
            self.debug("Start motion")
            self.motion.run(items=items)
    


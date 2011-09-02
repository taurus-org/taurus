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

"""This module is part of the Python Pool libray. It defines the PoolPseudoMotor
class"""

__all__ = [ "PoolPseudoMotor" ]

__docformat__ = 'restructuredtext'

from pooldefs import ElementType
from poolevent import EventType
from poolelement import PoolElement
from poolgroupelement import PoolBaseGroup
from poolmotion import PoolMotion


class PoolPseudoMotor(PoolBaseGroup, PoolElement):
    
    def __init__(self, **kwargs):
        self._positions = {}
        self._position = None
        self._wposition = None
        self._siblings = None
        user_elements = kwargs.pop('user_elements')
        PoolElement.__init__(self, **kwargs)
        PoolBaseGroup.__init__(self, user_elements=user_elements)
        motion_name = "%s.Motion" % self._name
        self.set_action_cache(PoolMotion(self.pool, motion_name))
    
    def _get_pool(self):
        return self.pool

    def get_type(self):
        return ElementType.PseudoMotor
    
    def get_siblings(self):
        if self._siblings is None:
            self._siblings = siblings = set()
            for axis, sibling in self.controller.get_element_axis().items():
                if axis == self.axis:
                    continue
                siblings.add(sibling)
        return self._siblings
    
    siblings = property(fget=get_siblings,
                        doc="the siblings for this pseudo motor")
    
    def on_element_changed(self, evt_src, evt_type, evt_value):
        name = evt_type.name
        # always calculate state.
        state, status = self._calculate_states()
        if name == 'state':
            self.set_state(state, propagate=evt_type.priority)
            self.set_status("\n".join(status), propagate=evt_type.priority)
        elif name == 'position':
            self.put_element_position(evt_src, evt_value, propagate=evt_type.priority)
    
    def add_user_element(self, element, index=None):
        elem_type = element.get_type()
        if elem_type == ElementType.Motor:
            pass
        elif elem_type == ElementType.PseudoMotor:
            #TODO: make this happen
            pass
        else:
            raise Exception("element %s is not a motor" % element.name)
            
        PoolBaseGroup.add_user_element(self, element, index=index)
         
    # --------------------------------------------------------------------------
    # position
    # --------------------------------------------------------------------------
    
    def get_w_position(self, with_physical_positions=None):
        if self._wposition is None and with_physical_positions is not None:
            return self.calculate(with_physical_positions)
        return self._wposition
    
    def get_physical_positions(self, cache=True, propagate=1):
        positions = self._positions
        if not cache or positions is None:
            dial_positions = self.motion.read_dial_position(serial=True)
            for motion_obj, motion_pos in dial_positions.items():
                motion_obj.put_dial_position(motion_pos, propagate=propagate)
            self._positions = positions = {}
            for motion_obj in self.get_user_elements():
                positions[motion_obj] = motion_obj.get_position(propagate=0)
        return self._positions
    
    def get_siblings_write_positions(self, with_physical_positions=None):
        positions = {}
        for sibling in self.siblings:
            positions[sibling] = sibling.get_w_position(with_physical_positions=with_physical_positions)
        return positions
    
    def calculate(self, positions=None):
        ctrl = self.controller
        if positions is None:
            positions = self.get_physical_positions()
        user_elements = self.get_user_elements()
        physical_positions = []
        for elem in user_elements:
            physical_positions.append(positions[elem])
        return ctrl.calc_pseudo(self.axis, physical_positions, None)
    
    def get_position(self, cache=True, propagate=1):
        position = self._position
        if cache and position is not None:
            return position
        positions = self.get_physical_positions(cache=cache, propagate=0)
        position = self.calculate(positions)
        self._set_position(position, propagate=propagate)
        return position
    
    def set_position(self, position):
        self._wposition = position
        self.start_move(position)
    
    def put_position(self, position, propagate=1):
        self._set_position(position, propagate=propagate)
    
    def _set_position(self, position, propagate=1):
        self._position = position
        if not propagate:
            return
        self.fire_event(EventType("position", priority=propagate), position)
    
    def put_element_position(self, element, position, propagate=1):
        self._positions[element] = position
        if not propagate or len(self._positions) < len(self.get_user_elements()):
            return
        self._position = self.calculate()
        self.fire_event(EventType("position", priority=propagate), self._position)
    
    position = property(get_position, set_position, doc="pseudo motor position")
    
    # --------------------------------------------------------------------------
    # motion
    # --------------------------------------------------------------------------
    
    def get_motion(self):
        return self.get_action_cache()
    
    motion = property(get_motion, doc="motion object")
    
    # --------------------------------------------------------------------------
    # motion calculation
    # --------------------------------------------------------------------------
    
    def start_move(self, new_position):
        self._aborted = False
        if not self._simulation_mode:
            user_elements = self.get_user_elements()
            physical_positions = self.get_physical_positions()
            ctrl = self.controller
            positions = self.get_siblings_write_positions(physical_positions)
            positions[self] = new_position
            pseudo_positions, curr_physical_positions = len(positions)*[None],[]
            for pseudo, position in positions.items():
                pseudo_positions[pseudo.axis-1] = position
            for user_element in user_elements:
                curr_physical_positions.append(physical_positions[user_element])
            physical_positions = self.controller.calc_all_physical(
                                    pseudo_positions, curr_physical_positions)
            
            items = {}
            for new_position, element in zip(physical_positions, user_elements):
                items[element] = element._calculate_move(new_position)
            self.motion.run(items=items)
    
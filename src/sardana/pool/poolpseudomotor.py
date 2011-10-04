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

from sardana import State
from pooldefs import ElementType, TYPE_PHYSICAL_ELEMENTS
from poolevent import EventType
from poolelement import PoolElement
from poolgroupelement import PoolBaseGroup
from poolmotion import PoolMotion


class PoolPseudoMotor(PoolBaseGroup, PoolElement):
    
    def __init__(self, **kwargs):
        self._physical_positions = {}
        self._low_level_physical_positions = {}
        self._position = None
        self._wposition = None
        self._siblings = None
        user_elements = kwargs.pop('user_elements')
        PoolElement.__init__(self, **kwargs)
        PoolBaseGroup.__init__(self, user_elements=user_elements)
    
    def to_json(self, *args, **kwargs):
        ret = PoolElement.to_json(self, *args, **kwargs)
        elements = [ elem.name for elem in self.get_user_elements() ]
        physical_elements = []
        for elem_list in self.get_physical_elements().values():
            for elem in elem_list:
                physical_elements.append(elem.name)
        cl_name = self.__class__.__name__
        cl_name = cl_name[4:]
        ret['elements'] = elements
        ret['physical_elements'] = physical_elements
        return ret
    
    def _get_pool(self):
        return self.pool
    
    def _create_action_cache(self):
        motion_name = "%s.Motion" % self._name
        return PoolMotion(self.pool, motion_name)

    def get_action_cache(self):
        return self._get_action_cache()
    
    def set_action_cache(self, action_cache):
        self._set_action_cache(action_cache)
        
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
        status_info = self._calculate_states()
        state, status = self.calculate_state_info(status_info=status_info)
        state_propagate = 0
        status_propagate = 0
        if name == 'state':
            state_propagate = evt_type.priority
        elif name == 'status':
            status_propagate = evt_type.priority
        self.set_state(state, propagate=state_propagate)
        self.set_status(status, propagate=status_propagate)
        if name == 'position':
            self.put_physical_element_position(evt_src, evt_value,
                                               propagate=evt_type.priority)
    
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
            return self.calc_pseudo(with_physical_positions)
        return self._wposition
    
    def get_low_level_physical_positions(self, cache=True, propagate=1):
        positions = self._low_level_physical_positions
        if not cache or positions is None:
            dial_positions = self.motion.read_dial_position(serial=True)
            for motion_obj, motion_pos in dial_positions.items():
                motion_obj.put_dial_position(motion_pos, propagate=propagate)
            self._low_level_physical_positions = positions = {}
            for ctrl, motion_objs in self.get_physical_elements().items():
                for motion_obj in motion_objs:
                    positions[motion_obj] = motion_obj.get_position(propagate=0)
        return positions
    
    def get_physical_positions(self, cache=True, propagate=1):
        positions = self._physical_positions
        if cache and positions is not None:
            return positions
        
        ll_positions = self.get_low_level_physical_positions(cache=False,
                            propagate=propagate)
        
        user_elements = self.get_user_elements()
        
        self._physical_positions = positions = {}
        
        for element in user_elements:
            # if the element is a low_level physical (pure motor) then get the
            # position directly from the low level positions, otherwise it must
            # be a pseudo motor, so calculate the positions from the physicals
            if element.get_type() in TYPE_PHYSICAL_ELEMENTS:
                position = ll_positions[element]
            else:
                position = element.calc_pseudo(ll_positions)
            positions[element] = position
        
        return self._physical_positions
    
    def get_siblings_write_positions(self, with_physical_positions=None):
        positions = {}
        for sibling in self.siblings:
            positions[sibling] = sibling.get_w_position(
                with_physical_positions=with_physical_positions)
        return positions
    
    def calc_pseudo(self, physical_positions=None):
        ctrl = self.controller
        if physical_positions is None:
            physical_positions = self.get_physical_positions()
        user_elements = self.get_user_elements()
        phy_positions = [ physical_positions[elem] for elem in user_elements ]
        return ctrl.calc_pseudo(self.axis, phy_positions, None)
    
    def get_position(self, cache=True, propagate=1):
        position = self._position
        if cache and position is not None:
            return position
        positions = self.get_physical_positions(cache=cache, propagate=0)
        position = self.calc_pseudo(positions)
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
    
    def put_physical_element_position(self, element, position, propagate=1):
        self._physical_positions[element] = position
        if not propagate or len(self._physical_positions) < len(self.get_user_elements()):
            return
        self._position = self.calc_pseudo()
        self.fire_event(EventType("position", priority=propagate), self._position)
    
    position = property(get_position, set_position, doc="pseudo motor position")
    
    # --------------------------------------------------------------------------
    # state information
    # --------------------------------------------------------------------------

    _STD_STATUS = "{name} is {state}\n{ctrl_status}"
    def calculate_state_info(self, status_info=None):
        if status_info is None:
            status_info = self._state, self._status
        state, status = status_info
        if state == State.On:
            state_str = "Stopped"
        else:
            state_str = "in " + State[state]
        new_status = self._STD_STATUS.format(name=self.name, state=state_str,
                                             ctrl_status=status)
        return status_info[0], new_status
    
    def read_state_info(self, state_info=None):
        if state_info is None:
            state_info = {}
            action_cache = self.get_action_cache()
            ctrl_state_infos = action_cache.read_state_info(serial=True)
            for motion_obj, ctrl_state_info in ctrl_state_infos.items():
                state_info[motion_obj] = motion_state_info = \
                    motion_obj._from_ctrl_state_info(ctrl_state_info)
                motion_obj.put_state_info(motion_state_info)
        for user_element in self.get_user_elements():
            if user_element.get_type() not in TYPE_PHYSICAL_ELEMENTS:
                motion_state_info = user_element._calculate_states()
                user_element.put_state_info(motion_state_info)
        
        ret = self._calculate_states()
        return ret
    
    # --------------------------------------------------------------------------
    # default acquisition channel
    # --------------------------------------------------------------------------
    
    def get_default_acquisition_channel(self):
        return "position"
    
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
        
        if items is None:
            items = {}
        for new_position, element in zip(physical_positions, user_elements):
            element.calculate_motion(new_position, items=items)
        return items
    
    def start_move(self, new_position):
        self._aborted = False
        self._stopped = False
        if not self._simulation_mode:
            items = self.calculate_motion(new_position)
            self.motion.run(items=items)
    
    # --------------------------------------------------------------------------
    # stop
    # --------------------------------------------------------------------------
    
    def stop(self):
        #surpass the PoolElement.stop because it doesn't do what we want
        PoolBaseElement.stop(self)
        PoolBaseGroup.stop(self)
    
    # --------------------------------------------------------------------------
    # abort
    # --------------------------------------------------------------------------
    
    def abort(self):
        #surpass the PoolElement.abort because it doesn't do what we want
        PoolBaseElement.abort(self)
        PoolBaseGroup.abort(self)

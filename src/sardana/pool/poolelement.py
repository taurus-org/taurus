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

__all__ = [ "PoolBaseElement", "PoolElement", "PoolGroupElement" ]

__docformat__ = 'restructuredtext'

import weakref

from poolbase import *
from pooldefs import *


class PoolBaseElement(PoolObject):
    
    def __init__(self, **kwargs):
        self._simulation_mode = False
        self._state = None
        self._state_event = None
        self._status = None
        self._status_event = None
        self._aborted = False
        self._action_cache = None
        super(PoolBaseElement, self).__init__(**kwargs)
    
    def get_action_cache(self):
        return self._action_cache
    
    # --------------------------------------------------------------------------
    # state
    # --------------------------------------------------------------------------
    
    def get_state(self, cache=True, propagate=1):
        if not cache or self._state is None:
            state_info = self.read_state_info()
            self._set_state_info(state_info, propagate=propagate)
        return self._state
    
    def set_state(self, state, propagate=1):
        self._set_state(state, propagate=propagate)
        
    def _set_state(self, state, propagate=1):
        self._state = state
        if not propagate:
            return
        if state == self._state_event:
            # current state is equal to last state_event. Skip event
            return
        self._state_event = state
        self.fire_event(EventType("state", priority=propagate), state)
    
    def put_state(self, state):
        self._state = state

    # --------------------------------------------------------------------------
    # status
    # --------------------------------------------------------------------------
    
    def get_status(self, cache=True, propagate=1):
        if not cache or self._status is None:
            state_info = self.read_state_info()
            self._set_state_info(state_info, propagate=propagate)
        return self._status
    
    def set_status(self, status, propagate=1):
        self._set_status(status, propagate=propagate)
        
    def _set_status(self, status, propagate=1):
        self._status = status
        if not propagate:
            return
        s_evt = self._status_event
        if s_evt is not None and len(status) == len(s_evt) and status == s_evt:
            # current status is equal to last status_event. Skip event
            return
        self._status_event = status
        self.fire_event(EventType("status", priority=propagate), status)
    
    def put_status(self, status):
        self._status = status
    
    # --------------------------------------------------------------------------
    # state information
    # --------------------------------------------------------------------------

    def set_state_info(self, state_info, propagate=1):
        self._set_state_info(state_info, propagate=propagate)
        
    def _set_state_info(self, state_info, propagate=1):
        state, status = state_info
        self._set_state(state, propagate=propagate)
        self._set_status(status, propagate=propagate)
    
    def read_state_info(self):
        ctrl_state_info = self._action_cache.read_state_info()[self]
        return self._from_ctrl_state_info(ctrl_state_info)
    
    def put_state_info(self, state_info):
        self.put_state(state_info[0])
        self.put_status(state_info[1])
        
    def _from_ctrl_state_info(self, state_info):
        state, status = state_info[:2]
        state = int(state)
        return state, status

    # --------------------------------------------------------------------------
    # abort
    # --------------------------------------------------------------------------
    
    def abort(self):
        self.controller.ctrl.AbortOne(self.axis)
        self._aborted = True
    
    def was_aborted(self):
        return self._aborted
    
    state = property(get_state, set_state, doc="element state")
    

class PoolElement(PoolBaseElement):
    """A Pool element is an Pool object which is controlled by a controller.
       Therefore it contains a _ctrl_id and a _axis (the id of the element in
       the controller)."""
    
    def __init__(self, **kwargs):
        ctrl = kwargs.pop('ctrl')
        self._ctrl = weakref.ref(ctrl)
        self._axis = kwargs.pop('axis')
        self._ctrl_id = ctrl.get_id()
        try:
            instrument = kwargs.pop('instrument')
            self.set_instrument(instrument)
        except KeyError:
            self._instrument = None
        super(PoolElement, self).__init__(**kwargs)
    
    def get_controller(self):
        if self._ctrl is None:
            return None
        return self._ctrl()
    
    def get_controller_id(self):
        return self._ctrl_id
    
    def get_axis(self):
        return self._axis
    
    def set_action_cache(self, action_cache):
        self._action_cache = action_cache
        action_cache.add_element(self)
        
    # --------------------------------------------------------------------------
    # instrument
    # --------------------------------------------------------------------------
    
    def get_instrument(self):
        if self._instrument is None:
            return None
        return self._instrument()
    
    def set_instrument(self, instrument, propagate=1):
        self._set_instrument(instrument, propagate=propagate)
    
    def _set_instrument(self, instrument, propagate=1):
        if self._instrument is not None:
            self._instrument().remove_element(self)
        new_instrument_name = ""
        if instrument is None:
            self._instrument = None
        else:
            self._instrument = weakref.ref(instrument)
            new_instrument_name = instrument.full_name
            instrument.add_element(self)
        if not propagate:
            return
        self.fire_event(EventType("instrument", priority=propagate),
                        new_instrument_name)
    
    axis = property(get_axis, doc="element axis")
    
    controller = property(get_controller, doc="element controller")
    controller_id = property(get_controller_id, doc="element controller id")
    
    instrument = property(get_instrument, set_instrument, doc="element instrument")
    
    
class PoolGroupElement(PoolBaseElement):

    def __init__(self, **kwargs):
        user_elem_ids = kwargs.pop('user_elements')
        super(PoolGroupElement, self).__init__(**kwargs)
        
        pool = self.pool
        self._user_elements = []
        for id in user_elem_ids:
            self.add_user_element(pool.get_element(id=id))

    def get_action_cache(self):
        return self._action_cache
    
    def set_action_cache(self, action_cache):
        if self._action_cache is not None:
            for element in self._user_elements:
                action_cache.remove_element(element)
            
        self._action_cache = action_cache
        
        for element in self._user_elements:
            action_cache.add_element(element)
    
    def get_user_elements(self):
        return self._user_elements
    
    def add_user_element(self, element, index=None):
        if element in self._user_elements:
            raise Exception("Group already contains %s" % element.name)
        if index is None:
            index = len(self._user_elements)
        self._user_elements.insert(index, element)
        if self._action_cache:
            self._action_cache.add_element(element)
        element.add_listener(self.on_element_changed)
        
    def remove_user_element(self, element):
        try:
            idx = self._user_elements.index(element)
        except ValueError:
            raise Exception("Group doesn't contain %s" % element.name)
        element.remove_listener(self.on_element_changed)
        del self._user_elements[idx]

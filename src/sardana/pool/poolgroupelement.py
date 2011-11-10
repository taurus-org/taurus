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

__all__ = [ "PoolBaseGroup", "PoolGroupElement" ]

__docformat__ = 'restructuredtext'

from taurus.core import AttributeNameValidator

from sardana import State, ElementType, TYPE_PHYSICAL_ELEMENTS
from poolelement import PoolBaseElement
from poolexternal import PoolExternalObject
from poolcontainer import PoolContainer


class PoolBaseGroup(PoolContainer):

    def __init__(self, **kwargs):
        self._pending = True
        self._user_element_ids = None
        self._user_elements = None
        self._physical_elements = None
        self.set_user_element_ids(kwargs.pop('user_elements'))
        PoolContainer.__init__(self)
    
    def _get_pool(self):
        raise NotImplementedError
    
    def _create_action_cache(self):
        raise NotImplementedError
    
    def _get_action_cache(self):
        if self._action_cache is None:
            self._action_cache = self._fill_action_cache()
        return self._action_cache
    
    def _set_action_cache(self, action_cache):
        physical_elements = self.get_physical_elements()
        if self._action_cache is not None:
            for ctrl_physical_elements in physical_elements.values():
                for physical_element in ctrl_physical_elements:
                    action_cache.remove_element(physical_element)
        
        self._action_cache = self._fill_action_cache(action_cache)
    
    def _fill_action_cache(self, action_cache=None, physical_elements=None):
        a, b = action_cache is None, physical_elements is None
        if action_cache is None:
            a = True
            action_cache = self._create_action_cache()
        if physical_elements is None:
            physical_elements = self.get_physical_elements()
        
        for ctrl, ctrl_physical_elements in physical_elements.items():
            for physical_element in ctrl_physical_elements:
                action_cache.add_element(physical_element)
        return action_cache
    
    def _calculate_states(self):
        user_elements = self.get_user_elements()
        fault, alarm, on, moving = [], [], [], []
        status = []
        for elem in user_elements:
            if elem.get_type() == ElementType.External:
                continue
            u_state = elem.get_state(propagate=0)
            u_status = elem.get_status(propagate=0).split("\n", 1)[0]
            if u_state == State.Moving:
                moving.append(elem)
            elif u_state == State.On: 
                on.append(elem)
            elif u_state == State.Fault:
                fault.append(elem)
            elif u_state == State.Alarm:
                alarm.append(elem)
            status.append(u_status)
        state = State.On
        if fault:
            state = State.Fault
        elif alarm:
            state = State.Alarm
        elif moving:
            state = State.Moving
        self._state_statistics = { State.On : on, State.Fault : fault,
                                   State.Alarm : alarm, State.Moving : moving }
        return state, "\n".join(status)
    
    def _build_elements(self):
        self._user_elements = user_elements = []
        self._physical_elements = physical_elements = {}
        
        pool = self._get_pool()
        for user_element_id in self._user_element_ids:
            # an internal element
            if type(user_element_id) is int:
                try:
                    user_element = pool.get_element(id=user_element_id)
                except KeyError:
                    self._pending = True
                    self._user_elements = None
                    self._physical_elements = None
                    raise
            # a tango channel
            else:
                validator = AttributeNameValidator()
                params = validator.getParams(user_element_id)
                params['pool'] = self.pool
                user_element = PoolExternalObject(**params)
            self.add_user_element(user_element)
        self._pending = False
    
    def set_user_element_ids(self, new_element_ids):
        self.clear_user_elements()
        self._user_element_ids = new_element_ids
    
    def on_element_changed(self, evt_src, evt_type, evt_value):
        pass
    
    def get_user_elements(self):
        if self._pending:
            self._build_elements()
        return self._user_elements
    
    def get_physical_elements(self):
        if self._pending:
            self._build_elements()
        return self._physical_elements
    
    def add_user_element(self, element, index=None):
        user_elements = self._user_elements
        physical_elements=self._physical_elements
        if element in user_elements:
            raise Exception("Group already contains %s" % element.name)
        if index is None:
            index = len(user_elements)
        user_elements.insert(index, element)
        
        if element.get_type() == ElementType.External:
            return index
        
        self.add_element(element)
        self._find_physical_elements(element,
                                     physical_elements=physical_elements)
        
        action_cache = self._action_cache
        if action_cache is not None:
            self._fill_action_cache(action_cache=action_cache,
                                    physical_elements=physical_elements)
        element.add_listener(self.on_element_changed)
        return index
    
    def _find_physical_elements(self, element, physical_elements=None):
        elem_type = element.get_type()
        if physical_elements is None:
            physical_elements = {}
        if elem_type in TYPE_PHYSICAL_ELEMENTS:
            ctrl = element.controller
            own_elements = physical_elements.get(ctrl)
            if own_elements is None:
                physical_elements[ctrl] = own_elements = set()
            own_elements.add(element)
        else:
            for ctrl, elements in element.get_physical_elements().items():
                own_elements = physical_elements.get(ctrl)
                if own_elements is None:
                    physical_elements[ctrl] = own_elements = set()
                own_elements.update(elements)
        return physical_elements
    
    # TODO: to complicated to implement for now
#    def remove_user_element(self, element):
#        try:
#            idx = self._user_elements.index(element)
#        except ValueError:
#            raise Exception("Group doesn't contain %s" % element.name)
#        action_cache = self.get_action_cache()
#        element.remove_listener(self.on_element_changed)
#        action_cache.remove_element(element)
#        del self._user_elements[idx]
#        del self._user_element_ids[self._user_element_ids.index(element.id)]
#        self.remove_element(element)
    
    def clear_user_elements(self):
        user_elements = self._user_elements
        if user_elements is not None:
            for element in user_elements:
                if element.get_type() != ElementType.External:
                    element.remove_listener(self.on_element_changed)
                    self.remove_element(element)
        self._action_cache = None
        self._pending = True
        self._user_elements = None
        self._user_element_ids = None
        self._physical_elements = None
        
        
    # --------------------------------------------------------------------------
    # stop
    # --------------------------------------------------------------------------
    
    def stop(self):
        for ctrl, elements in self.get_physical_elements().items():
            try:
                ctrl.stop_elements(elements=elements)
            except:
                self.warning("Unable to stop controller %s", ctrl.name)
                self.debug("Unable to stop controller %s. Details:", ctrl.name,
                           exc_info=1)
    
    # --------------------------------------------------------------------------
    # abort
    # --------------------------------------------------------------------------
    
    def abort(self):
        for ctrl, elements in self.get_physical_elements().items():
            self.info("Aborting %s %s", ctrl.name,  [ e.name for e in elements] )
            try:
                ctrl.abort_elements(elements=elements)
            except:
                self.warning("Unable to abort controller %s", ctrl.name)
                self.debug("Unable to abort controller %s. Details:", ctrl.name,
                           exc_info=1)


class PoolGroupElement(PoolBaseElement, PoolBaseGroup):
    
    def __init__(self, **kwargs):
        user_elements = kwargs.pop('user_elements')
        PoolBaseElement.__init__(self, **kwargs)
        PoolBaseGroup.__init__(self, user_elements=user_elements)
    
    def serialize(self, *args, **kwargs):
        kwargs = PoolBaseElement.serialize(self, *args, **kwargs)
        elements = [ elem.name for elem in self.get_user_elements() ]
        physical_elements = []
        for elem_list in self.get_physical_elements().values():
            for elem in elem_list:
                physical_elements.append(elem.name)
        kwargs['elements'] = elements
        kwargs['physical_elements'] = physical_elements
        return kwargs
    
    def _get_pool(self):
        return self.pool
    
    def get_action_cache(self):
        return self._get_action_cache()
    
    def set_action_cache(self, action_cache):
        self._set_action_cache(action_cache)

    # --------------------------------------------------------------------------
    # stop
    # --------------------------------------------------------------------------
    
    def stop(self):
        PoolBaseElement.stop(self)
        PoolBaseGroup.stop(self)
                
    # --------------------------------------------------------------------------
    # abort
    # --------------------------------------------------------------------------
    
    def abort(self):
        PoolBaseElement.abort(self)
        PoolBaseGroup.abort(self)

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

"""This module is part of the Python Pool library. It defines the base classes
for"""

__all__ = [ "PoolBaseGroup"]

__docformat__ = 'restructuredtext'

from taurus.core.taurusvalidator import AttributeNameValidator

from sardana import State, ElementType, TYPE_PHYSICAL_ELEMENTS
from poolexternal import PoolExternalObject
from poolcontainer import PoolContainer

class PoolBaseGroup(PoolContainer):

    def __init__(self, **kwargs):
        self._pending = True
        self._user_element_ids = None
        self._user_elements = None
        self._physical_elements = None
        self._physical_elements_set = None
        self._state_statistics = {}
        self._pool = kwargs.pop('pool')
        self.set_user_element_ids(kwargs.pop('user_elements'))
        PoolContainer.__init__(self)
        try:
            self._build_elements()
        except KeyError:
            self.info("failed to build element information. No problem. " \
                      "Probably one or more underlying elements have not " \
                      "been constructed yet")

    def _get_pool(self):
        return self._pool

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
        if action_cache is None:
            action_cache = self._create_action_cache()
        if physical_elements is None:
            physical_elements = self.get_physical_elements()
        for _, ctrl_physical_elements in physical_elements.items():
            for physical_element in ctrl_physical_elements:
                action_cache.add_element(physical_element)
        return action_cache

    def _calculate_element_state(self, elem, elem_state_info):
        u_state, u_status = elem_state_info
        if u_status is None:
            u_status = '%s is None' % elem.name
        else:
            u_status = u_status.split("\n", 1)[0]
        return u_state, u_status

    def _calculate_states(self, state_info=None):
        user_elements = self.get_user_elements()
        none, unknown = set(), set()
        fault, alarm, on, moving = set(), set(), set(), set()
        status = []
        if state_info is None:
            state_info = {}
            for elem in user_elements:
                if elem.get_type() == ElementType.External:
                    continue
                # cannot call get_state(us) here since it may lead to dead lock!
                si = elem.inspect_state(), elem.inspect_status()
                state_info[elem] = si
        for elem, elem_state_info in state_info.items():
            elem_type = elem.get_type()
            if elem_type == ElementType.External:
                continue
            u_state, u_status = self._calculate_element_state(elem, elem_state_info)
            if u_state == State.Moving:
                moving.add(elem)
            elif u_state == State.On:
                on.add(elem)
            elif u_state == State.Fault:
                fault.add(elem)
            elif u_state == State.Alarm:
                alarm.add(elem)
            elif u_state is State.Unknown:
                unknown.add(elem)
            elif u_state is None:
                none.add(elem)
            status.append(u_status)
        state = State.On
        if none or unknown:
            state = State.Unknown
        if fault:
            state = State.Fault
        elif alarm:
            state = State.Alarm
        elif moving:
            state = State.Moving
        self._state_statistics = { State.On : on, State.Fault : fault,
                                   State.Alarm : alarm, State.Moving : moving,
                                   State.Unknown : unknown, None : none }
        status = "\n".join(status)
        return state, status

    def _is_managed_element(self, element):
        return True

    def _build_elements(self):
        self._user_elements = []
        self._physical_elements =  {}
        self._physical_elements_set = set()
        
        pool = self._get_pool()
        for user_element_id in self._user_element_ids:
            # an internal element
            internal = type(user_element_id) is int
            if internal:
                try:
                    user_element = pool.get_element(id=user_element_id)
                except KeyError:
                    self._pending = True
                    self._user_elements = None

                    self._physical_elements = None
                    self._physical_elements_set = None
                    raise
                internal = self._is_managed_element(user_element)
                if not internal:
                    user_element_id = user_element.get_source()
            # a tango channel or non internal element (ex: ioregister or motor
            # in measurement group)
            if not internal:
                validator = AttributeNameValidator()
                params = validator.getParams(user_element_id)
                params['pool'] = self._get_pool()
                user_element = PoolExternalObject(**params)
            self.add_user_element(user_element)
        self._pending = False

    def on_element_changed(self, evt_src, evt_type, evt_value):
        pass
        
    def set_user_element_ids(self, new_element_ids):
        self.clear_user_elements()
        self._user_element_ids = new_element_ids
    
    def get_user_element_ids(self):
        """Returns the sequence of user element IDs
        
        :return: the sequence of user element IDs
        :rtype: sequence< :obj:`int`>"""         
        return self._user_element_ids
    
    user_element_ids = property(get_user_element_ids)

    def get_user_elements(self):
        """Returns the sequence of user elements
        
        :return: the sequence of user elements
        :rtype: sequence< :class:`~sardana.pool.poolelement.PoolElement`>""" 
        if self._pending:
            self._build_elements()
        return self._user_elements

    def get_user_elements_attribute_iterator(self):
        """Returns an iterator over the main attribute of each user element.
        
        :return: an iterator over the main attribute of each user element.
        :rtype: iter< :class:`~sardana.sardanaattribute.SardanaAttribute` >""" 
        for element in self.get_user_elements():
            yield element.get_default_attribute()

    get_user_elements_attribute = get_user_elements_attribute_iterator
    get_user_elements_attribute.__doc__ = get_user_elements_attribute_iterator.__doc__
    
    def get_user_elements_attribute_sequence(self):
        """Returns a sequence of main attribute of each user element.
        
        In loops use preferably :meth:`get_user_elements_attribute_iterator` for
        performance and memory reasons.
        
        :return: a sequence of main attribute of each user element.
        :rtype: sequence< :class:`~sardana.sardanaattribute.SardanaAttribute` >""" 
        return list(self.get_user_elements_attribute_iterator())
    
    def get_user_elements_attribute_map(self):
        """Returns a dictionary of main attribute of each user element.
        
        :return: a dictionary of main attribute of each user element.
        :rtype: dict< :class:`~sardana.pool.poolelement.PoolElement`, 
                :class:`~sardana.sardanaattribute.SardanaAttribute` >"""
        ret = {}
        for element in self.get_user_elements():
            ret[element] =  element.get_default_attribute()
        return ret
    
    def get_physical_elements(self):
        """Returns a dictionary or physical elements where key is a controller
        object and value is a sequence of pool elements
        
        :return: a dictionary of physical elements
        :rtype: dict< :class:`~sardana.pool.poolcontroller.PoolController,
                sequence<:class:`~sardana.pool.poolelement.PoolElement`>"""            
        if self._pending:
            self._build_elements()
        return self._physical_elements

    def get_physical_elements_iterator(self):
        """Returns an iterator over the physical elements.
        
        .. warning:: The order is non deterministic.
        
        :return: an iterator over the physical elements.
        :rtype: iter<:class:`~sardana.pool.poolelement.PoolElement` >"""         
        for _, elements in self.get_physical_elements().items():
            for element in elements:
                yield element

    def get_physical_elements_attribute_iterator(self):
        """Returns an iterator over the main attribute of each physical element.
        
        .. warning:: The order is non deterministic.
        
        :return: an iterator over the main attribute of each physical element.
        :rtype: iter< :class:`~sardana.sardanaattribute.SardanaAttribute` >"""         
        for element in self.get_physical_elements_iterator():
            yield element.get_default_attribute()

    def get_physical_elements_set(self):
        if self._pending:
            self._build_elements()
        return self._physical_elements_set

    def add_user_element(self, element, index=None):
        user_elements = self._user_elements
        physical_elements = self._physical_elements
        physical_elements_set = self._physical_elements_set
        
        if element in user_elements:
            raise Exception("Group already contains %s" % element.name)
        if index is None:
            index = len(user_elements)
        user_elements.insert(index, element)
        
        if not self._is_managed_element(element):
            return index

        self.add_element(element)
        self._find_physical_elements(element,
                                     physical_elements=physical_elements,
                                     physical_elements_set=physical_elements_set)
        action_cache = self._action_cache
        if action_cache is not None:
            self._fill_action_cache(action_cache=action_cache,
                                    physical_elements=physical_elements)
        element.add_listener(self.on_element_changed)
        return index

    def _find_physical_elements(self, element, physical_elements=None,
                                physical_elements_set=None):
        elem_type = element.get_type()
        if physical_elements is None:
            physical_elements = {}
        if physical_elements_set is None:
            physical_elements_set = set()
            
        if elem_type in TYPE_PHYSICAL_ELEMENTS:
            ctrl = element.controller
            own_elements = physical_elements.get(ctrl)
            if own_elements is None:
                physical_elements[ctrl] = own_elements = set()
            own_elements.add(element)
            physical_elements_set.add(element)
        else:
            for ctrl, elements in element.get_physical_elements().items():
                own_elements = physical_elements.get(ctrl)
                if own_elements is None:
                    physical_elements[ctrl] = own_elements = set()
                own_elements.update(elements)
                physical_elements_set.update(elements)
        return physical_elements

    # TODO: too complicated to implement for now
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
            self.debug("Stopping %s %s", ctrl.name, [e.name for e in elements])
            try:
                ctrl.stop_elements(elements=elements)
            except:
                self.error("Unable to stop controller %s", ctrl.name)
                self.debug("Details:", exc_info=1)

    # --------------------------------------------------------------------------
    # abort
    # --------------------------------------------------------------------------

    def abort(self):
        for ctrl, elements in self.get_physical_elements().items():
            self.debug("Aborting %s %s", ctrl.name, [e.name for e in elements])
            try:
                ctrl.abort_elements(elements=elements)
            except:
                self.error("Unable to abort controller %s", ctrl.name)
                self.debug("Details:", exc_info=1)

    # --------------------------------------------------------------------------
    # involved in an operation
    # --------------------------------------------------------------------------

    def get_operation(self):
        for _, elements in self.get_physical_elements().items():
            for element in elements:
                op = element.get_operation()
                if op is not None:
                    return op
        return None

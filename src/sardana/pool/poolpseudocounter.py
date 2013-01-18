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

"""This module is part of the Python Pool library. It defines the
PoolPseudoCounter class"""

__all__ = [ "PoolPseudoCounter" ]

__docformat__ = 'restructuredtext'

import sys
import time

from sardana import State, ElementType, TYPE_PHYSICAL_ELEMENTS
from sardana.sardanaattribute import SardanaAttribute
from sardana.sardanaexception import SardanaException
from sardana.sardanavalue import SardanaValue

from .poolexception import PoolException
from .poolbasechannel import PoolBaseChannel
from .poolbasegroup import PoolBaseGroup
from .poolacquisition import PoolAcquisition


class Value(SardanaAttribute):
    
    def __init__(self, *args, **kwargs):
        self._exc_info = None
        super(Value, self).__init__(*args, **kwargs)
        for value_attr in self.obj.get_physical_value_attribute_iterator():
            value_attr.add_listener(self.on_change)
    
    def _in_error(self):
        for value_attr in self.obj.get_physical_value_attribute_iterator():
            if value_attr.error:
                return True
        return self._exc_info != None
    
    def _has_value(self):
        for value_attr in self.obj.get_physical_value_attribute_iterator():
            if not value_attr.has_value():
                return False
        return True
    
    def _get_value(self):
        return self.calc().value

    def _set_value(self, value, exc_info=None, timestamp=None, propagate=1):
        raise Exception("Cannot set value for %s" % self.obj.name)

    def _get_write_value(self):
        w_values = self.get_physical_write_values()
        return self.calc_pseudo(physical_values=w_values).value
    
    def _set_write_value(self, w_value, timestamp=None, propagate=1):
        raise Exception("Cannot set write value for %s" % self.obj.name)
    
    def _get_exc_info(self):
        exc_info = self._exc_info
        if exc_info is None:
            for value_attr in self.obj.get_physical_value_attribute_iterator():
                if value_attr.error:
                    return value_attr.get_exc_info()
        return exc_info
    
    def _get_timestamp(self):
        timestamps = [ value_attr.timestamp for value_attr in self.obj.get_physical_value_attribute_iterator() ]
        if not len(timestamps):
            timestamps = self._local_timestamp,
        return max(timestamps)

    def get_physical_write_values(self):
        ret = []
        for value_attr in self.obj.get_physical_value_attribute_iterator():
            if value_attr.has_write_value():
                value = value_attr.w_value
            else:
                if not value_attr.has_value():
                    # if underlying counter doesn't have value yet, it is
                    # because of a cold start
                    value_attr.update(propagate=0)
                if value_attr.in_error():
                    raise PoolException("Cannot get '%' value" % value_attr.obj.name,
                                        exc_info=value_attr.exc_info)
                value = value_attr.value
            ret.append(value)
        return ret
        
    def get_physical_values(self):
        ret = []
        for value_attr in self.obj.get_physical_value_attribute_iterator():
            # if underlying channel doesn't have value yet, it is because
            # of a cold start
            if not value_attr.has_value():
                value_attr.update(propagate=0)
            if value_attr.in_error():
                raise PoolException("Cannot get '%' value" % value_attr.obj.name,
                                    exc_info=value_attr.exc_info)
            ret.append(value_attr.value)
        return ret

    def calc(self, physical_values=None):
        try:
            obj = self.obj
            if physical_values is None:
                physical_values = self.get_physical_values()
            else:
                l_v, l_u = len(physical_values), len(obj.get_user_elements())
                if l_v != l_u:
                    raise IndexError("CalcPseudo(%s): must give %d physical " \
                                     "values (you gave %d)" % (obj.name, l_u, l_v) )
            ctrl, axis = obj.controller, obj.axis    
            result = ctrl.calc(axis, physical_values)
        except SardanaException as se:
            result = SardanaValue(exc_info=se.exc_info)
        except:
            result = SardanaValue(exc_info=sys.exc_info())
        return result    

    def calc_all(self, physical_values=None):
        try:
            obj = self.obj
            if physical_values is None:
                physical_values = self.get_physical_values()
            else:
                l_v, l_u = len(physical_values), len(obj.get_user_elements())
                if l_v != l_u:
                    raise IndexError("CalcAllPseudo(%s): must give %d physical " \
                                     "values (you gave %d)" % (obj.name, l_u, l_v) )
            ctrl, axis = obj.controller, obj.axis    
            result = ctrl.calc_all(axis, physical_values)
        except SardanaException as se:
            result = SardanaValue(exc_info=se.exc_info)
        except:
            result = SardanaValue(exc_info=sys.exc_info())
        return result   
    
    def on_change(self, evt_src, evt_type, evt_value):
        self.fire_read_event(propagate=evt_type.priority)

    def update(self, cache=True, propagate=1):
        if cache:
            for phy_elem_val in self.obj.get_low_level_physical_value_attribute_iterator():
                if not phy_elem_val.has_value():
                    cache = False
                    break
        if not cache:
            values = self.obj.acquisition.read_value(serial=True)
            if not len(values):
                self._local_timestamp = time.time()
            for acq_obj, value in values.items():
                acq_obj.put_value(value, propagate=propagate)


class PoolPseudoCounter(PoolBaseGroup, PoolBaseChannel):
    """A class representing a Pseudo Counter in the Sardana Device Pool"""
    
    ValueAttributeClass = Value
    AcquisitionClass = None
    
    def __init__(self, **kwargs):
        self._siblings = None
        user_elements = kwargs.pop('user_elements')
        kwargs['elem_type'] = ElementType.PseudoCounter
        # don't switch the order of constructors!
        PoolBaseGroup.__init__(self, user_elements=user_elements,
                               pool=kwargs['pool'])
        PoolBaseChannel.__init__(self, **kwargs)

    def serialize(self, *args, **kwargs):
        kwargs = PoolBaseChannel.serialize(self, *args, **kwargs)
        elements = [ elem.name for elem in self.get_user_elements() ]
        physical_elements = []
        for elem_list in self.get_physical_elements().values():
            for elem in elem_list:
                physical_elements.append(elem.name)
        cl_name = self.__class__.__name__
        cl_name = cl_name[4:]
        kwargs['elements'] = elements
        kwargs['physical_elements'] = physical_elements
        return kwargs

    def on_element_changed(self, evt_src, evt_type, evt_value):
        name = evt_type.name.lower()
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
    
    def _create_action_cache(self):
        acq_name = "%s.Acquisition" % self._name
        return PoolAcquisition(self, acq_name)
    
    def get_action_cache(self):
        return self._get_action_cache()
    
    def set_action_cache(self, action_cache):
        self._set_action_cache(action_cache)

    def get_siblings(self):
        if self._siblings is None:
            self._siblings = siblings = set()
            for axis, sibling in self.controller.get_element_axis().items():
                if axis == self.axis:
                    continue
                siblings.add(sibling)
        return self._siblings

    siblings = property(fget=get_siblings,
                        doc="the siblings for this pseudo counter")
    
    # ------------------------------------------------------------------------
    # value
    # ------------------------------------------------------------------------
    
    def calc(self, physical_values=None):
        return self.get_value_attribute().calc(physical_values=physical_values)    

    def calc_all(self, physical_values=None):
        return self.get_value_attribute().calc_all(physical_values=physical_values)    
    
    def get_low_level_physical_value_attribute_iterator(self):
        return self.get_physical_elements_attribute_iterator()
        
    def get_physical_value_attribute_iterator(self):
        return self.get_user_elements_attribute_iterator()
    
    def get_physical_values_attribute_sequence(self):
        return self.get_user_elements_attribute_sequence()
    
    def get_physical_values_attribute_map(self):
        return self.get_user_elements_attribute_map()
    
    def get_physical_values(self, cache=True, propagate=1):
        """Get value for underlying elements.

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
            the physical value
        :rtype:
            dict <PoolElement, :class:`~sardana.sardanaattribute.SardanaAttribute` >"""
        self._value.update(cache=cache, propagate=propagate)
        return self.get_physical_values_attribute_map()

    def get_siblings_values(self, use=None):
        """Get the last values for all siblings.
        
        :param use: the already calculated values. If a sibling is in this
                    dictionary, the value stored here is used instead
        :type use: dict <PoolElement, :class:`~sardana.sardanavalue.SardanaValue` >
        :return: a dictionary with siblings values
        :rtype:
            dict <PoolElement, value(float?) >"""        
        values = {}
        for sibling in self.siblings:
            value_attr = sibling.get_value_attribute() 
            if use and sibling in use:
                pos = use[sibling]
            else:
                pos = value_attr.value
            values[sibling] = pos
        return values
    
    def get_value(self, cache=True, propagate=1):
        """Returns the pseudo counter value.
        
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
            the pseudo counter value
        :rtype:
            :class:`~sardana.sardanaattribute.SardanaAttribute`"""
        value_attr = self._value
        value_attr.update(cache=cache, propagate=propagate)
        return value_attr
    
    def set_value(self, value, propagate=1):
        raise Exception("Not possible to set_value of a pseudo counter")
        
    value = property(get_value, doc="pseudo counter value")

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
            for obj, ctrl_state_info in ctrl_state_infos.items():
                state_info[obj] = state_info = \
                    obj._from_ctrl_state_info(ctrl_state_info)
                obj.put_state_info(state_info)
        for user_element in self.get_user_elements():
            if user_element.get_type() not in TYPE_PHYSICAL_ELEMENTS:
                state_info = user_element._calculate_states()
                user_element.put_state_info(state_info)
        
        ret = self._calculate_states()
        return ret


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

__all__ = ["EventGenerator", "EventType",
           "PoolBaseObject", "PoolObject", "PoolContainer"]

__docformat__ = 'restructuredtext'

import weakref
import operator

from taurus.core.util import CallableRef, BoundMethodWeakref, Logger, CaselessDict

from pooldefs import *


class EventGenerator(object):

    def __init__(self):
        self._listeners = []
    
    def _listener_died(self, weak_listener):
        if self._listeners is None: 
            return
        try:
            self._listeners.remove(weak_listener)
        except Exception,e:
            pass
        
    def _get_callable_ref(self, listener, cb = None):
        meth = getattr(listener, 'event_received', None)
        if meth is not None and operator.isCallable(meth):
            return weakref.ref(listener, cb)
        else:
            return CallableRef(listener, cb)
    
    def add_listener(self, listener):
        if self._listeners is None or listener is None: 
            return False
        
        weak_listener = self._get_callable_ref(listener, self._listener_died)
        if weak_listener in self._listeners:
            return False
        self._listeners.append(weak_listener)
        return True
    
    def remove_listener(self, listener):
        if self._listeners is None: 
            return
        weak_listener = self._getCallableRef(listener)
        try:
            self._listeners.remove(weak_listener)
        except Exception,e:
            return False
        return True
        
    def has_listeners(self):
        """ returns True if anybody is listening to events from this attribute """
        if self._listeners is None: 
            return False
        return len(self._listeners) > 0
        
    def fire_event(self, event_type, event_value, listeners=None):
        """sends an event to all listeners or a specific one"""
        if listeners is None:
            listeners = self._listeners
        if listeners is None:
            return
        if not operator.isSequenceType(listeners):
            listeners = listeners,
        for listener in listeners:
            if isinstance(listener, weakref.ref) or \
               isinstance(listener, BoundMethodWeakref):
                l = listener()
            else:
                l = listener
            if l is None: continue
            meth = getattr(l, 'event_received', None)
            if meth is not None and operator.isCallable(meth):
                l.event_received(self, event_type, event_value)
            elif operator.isCallable(l):
                l(self, event_type, event_value)


class EventType(object):
    
    def __init__(self, name, priority=0):
        self.name = name
        self.priority = priority
    
    def __str__(self):
        return "EventType(name=%s, priority=%s)" % (self.name, self.priority)

    def __repr__(self):
        return "EventType(name=%s, priority=%s)" % (self.name, self.priority)


class PoolBaseObject(EventGenerator, Logger):
    """The Pool most abstract object. It contains only two members:
       - _pool : a weak reference to the pool where it belongs
       - _name : the name"""
       
    def __init__(self, **kwargs):
        EventGenerator.__init__(self)
        self._name = intern(kwargs['name'])
        Logger.__init__(self, self._name)
        self._pool = weakref.ref(kwargs['pool'])
    
    def get_pool(self):
        return self._pool()
    
    def get_name(self):
        return self._name
    
    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self._name)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self._name)

    pool = property(get_pool)
    name = property(get_name)
    

class PoolObject(PoolBaseObject):
    """A Pool object that besides the name and reference to the pool has:
       - _id : the internal identifier
       - _full_name : the name (usually a tango device name, but can be anything else.)
       - _user_full_name : [alias] '('[full_name]')' [class-of_device] [extra_info]"""
       
    def __init__(self, **kwargs):
        self._full_name = kwargs.pop('full_name')
        self._id = kwargs.pop('id')
        super(PoolObject, self).__init__(**kwargs)

    def get_full_name(self):
        return self._full_name

    def get_id(self):
        return self._id

    def get_type(self):
        raise NotImplementedError

    full_name = property(get_full_name)
    id = property(get_id)


class PoolContainer(object):
    """A container class for pool elements"""
    
    def __init__(self):
        
        # map of all elements
        # key - element ID
        # value - pointer to the element object
        self._element_ids = {}

        # map of all elements by name
        # key - element name
        # value - pointer to the element object
        self._element_names = CaselessDict()

        # map of all elements by name
        # key - element full name
        # value - pointer to the element object
        self._element_full_names = CaselessDict()
    
        # map of all elements by type
        # key - element type
        # value - map where:
        #    key - element ID
        #    value - pointer to the element object
        self._element_types = {}
        
    def add_element(self, e):
        """Adds a new :class:`pool.PoolObject` to this container
           
           :param e: the pool element to be added
           :type e: :class:`pool.PoolObject`
        """
        name, full_name, id = e.get_name(), e.get_full_name(), e.get_id()
        elem_type = e.get_type()
        self._element_ids[id] = e
        self._element_names[name] = e
        self._element_full_names[full_name] = e
        type_elems = self._element_types.get(elem_type)
        if type_elems is None:
            self._element_types[elem_type] = type_elems = {}
        type_elems[id] = e
        return e
    
    def remove_element(self, e):
        """Removes the :class:`pool.PoolObject` from this container
           
           :param e: the pool object to be removed
           :type e: :class:`pool.PoolObject`
           
           :throw: KeyError
        """
        name, full_name, id = e.get_name(), e.get_full_name(), e.get_id()
        elem_type = e.get_type()
        del self._element_ids[id]
        del self._element_names[name]
        del self._element_full_names[full_name]
        type_elems = self._element_types.get(elem_type)
        del type_elems[id]
        
    def get_element_id_map(self):
        """Returns a reference to the internal pool object ID map
           
           :return: the internal pool object ID map
           :rtype: dict<id, pool.PoolObject>
        """
        return self._element_ids
    
    def get_element_name_map(self):
        """Returns a reference to the internal pool object name map
           
           :return: the internal pool object name map
           :rtype: dict<str, pool.PoolObject>
        """
        return self._element_names
    
    def get_element_type_map(self):
        """Returns a reference to the internal pool object type map
           
           :return: the internal pool object type map
           :rtype: dict<pool.ElementType, dict<id, pool.PoolObject>>
        """
        return self._element_types
    
    def get_element(self, **kwargs):
        """Returns a reference to the requested pool object
           
           :param kwargs: if key 'id' given: search by ID
                          else if key 'full_name' given: search by full name
                          else if key 'name' given: search by name
           
           :return: the pool object 
           :rtype: pool.PoolObject
           
           :throw: KeyError
        """
        if kwargs.has_key("id"):
            id = kwargs.pop("id")
            return self.get_element_by_id(id, **kwargs)
        
        if kwargs.has_key("full_name"):
            full_name = kwargs.pop("full_name")
            return self.get_element_by_full_name(full_name, **kwargs)
        
        name = kwargs.pop("name")
        return self.get_element_by_name(name, **kwargs)
    
    def get_element_by_name(self, name, **kwargs):
        """Returns a reference to the requested pool object
           
           :param name: pool object name
           :type name: str
           
           :return: the pool object 
           :rtype: pool.PoolObject
           
           :throw: KeyError
        """
        ret = self._element_names.get(name)
        if ret is None:
            raise KeyError("There is no element with name '%s'" % name)
        return ret
    
    def get_element_by_full_name(self, full_name, **kwargs):
        """Returns a reference to the requested pool object
           
           :param name: pool object full name
           :type name: str
           
           :return: the pool object 
           :rtype: pool.PoolObject
           
           :throw: KeyError
        """
        ret = self._element_full_names.get(full_name)
        if ret is None: 
            raise KeyError("There is no element with full name '%s'" % full_name)
        return ret
        
    def get_element_by_id(self, id, **kwargs):
        """Returns a reference to the requested pool object
           
           :param id: pool object ID
           :type id: int
           
           :return: the pool object 
           :rtype: pool.PoolObject
           
           :throw: KeyError
        """
        ret = self._element_ids.get(id)
        if ret is None: 
            raise KeyError("There is no element with ID '%d'" % id)
        return ret
    
    def get_elements_by_type(self, t):
        """Returns a list of all pool objects of the given type
           
           :param t: element type
           :type t: pool.ElementType
           
           :return: list of pool objects
           :rtype: seq<pool.PoolObject>
        """
        elem_types_dict = self._element_types.get(t)
        if elem_types_dict is None:
            return  []
        return elem_types_dict.values()

    def get_element_names_by_type(self, t):
        """Returns a list of all pool object names of the given type
           
           :param t: element type
           :type t: pool.ElementType
           
           :return: list of pool object names
           :rtype: seq<str>
        """
        return [ elem.get_name() for elem in self.get_elements_by_type(t) ]
        
    def rename_element(self, old_name, new_name):
        """Rename a pool object
           
           :param old_name: old pool object name
           :type old_name: str
           :param new_name: new pool object name
           :type new_name: str
        """
        raise NotImplementedError
    
    def get_controller_class(self, **kwargs):
        id = kwargs.get("id")
        if id is not None:
            return self.get_controller_class_by_id(id, **kwargs)
        
        name = kwargs.pop("name")
        self.get_controller_class_by_name(name, **kwargs)
    
    def get_controller_class_by_id(self, id, **kwargs):
        raise NotImplementedError
    
    def get_controller_class_by_name(self, name, **kwargs):
        raise NotImplementedError
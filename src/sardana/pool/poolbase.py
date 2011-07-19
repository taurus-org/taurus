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
           "PoolBaseObject", "PoolObject"]

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

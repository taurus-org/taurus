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
for pool event mechanism"""

__all__ = ["EventGenerator", "EventType"]

__docformat__ = 'restructuredtext'

import weakref
import operator

from taurus.core.util import CallableRef, BoundMethodWeakref


def _get_callable_ref(listener, callback=None):
    """Returns a callable reference for the given listener"""
    meth = getattr(listener, 'event_received', None)
    if meth is not None and operator.isCallable(meth):
        return weakref.ref(listener, callback)
    else:
        return CallableRef(listener, callback)


class EventGenerator(object):
    """A class capable of generating events to their listeners"""
    
    def __init__(self):
        self._listeners = []
    
    def _listener_died(self, weak_listener):
        """Callback executed when a listener dies"""
        if self._listeners is None: 
            return
        try:
            self._listeners.remove(weak_listener)
        except ValueError:
            pass
        
    def add_listener(self, listener):
        """Adds a new listener for this object.
        
        :param listener: a listener"""
        if self._listeners is None or listener is None: 
            return False
        
        weak_listener = _get_callable_ref(listener, self._listener_died)
        if weak_listener in self._listeners:
            return False
        self._listeners.append(weak_listener)
        return True
    
    def remove_listener(self, listener):
        """Removes an existing listener for this object.
        
        :param listener: the listener to be removed
        :return: True is succedded or False otherwise"""
        if self._listeners is None: 
            return
        weak_listener = _get_callable_ref(listener)
        try:
            self._listeners.remove(weak_listener)
        except ValueError:
            return False
        return True
        
    def has_listeners(self):
        """Returns True if anybody is listening to events from this object
        
        :return: True is at least one listener is listening or False otherwise
        """
        if self._listeners is None: 
            return False
        return len(self._listeners) > 0
        
    def fire_event(self, event_type, event_value, listeners=None):
        """Sends an event to all listeners or a specific one"""
        if listeners is None:
            listeners = self._listeners
        if listeners is None:
            return
        if not operator.isSequenceType(listeners):
            listeners = listeners,
        for listener in listeners:
            if isinstance(listener, weakref.ref) or \
               isinstance(listener, BoundMethodWeakref):
                real_listener = listener()
            else:
                real_listener = listener
            if real_listener is None:
                continue
            meth = getattr(real_listener, 'event_received', None)
            if meth is not None and operator.isCallable(meth):
                real_listener.event_received(self, event_type, event_value)
            elif operator.isCallable(real_listener):
                real_listener(self, event_type, event_value)


class EventType(object):
    """Definition of an event type"""
    
    def __init__(self, name, priority=0):
        self.name = name
        self.priority = priority
    
    def __str__(self):
        return "EventType(name=%s, priority=%s)" % (self.name, self.priority)

    def __repr__(self):
        return "EventType(name=%s, priority=%s)" % (self.name, self.priority)

    def get_name(self):
        """Returns this event name
        
        :return: this event name
        :rtype: str"""
        return self.name

    def get_priority(self):
        """Returns this event priority
        
        :return: this event priority
        :rtype: str"""
        return self.priority
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

"""This module is part of the Python Sardana libray. It defines the base classes
for Sardana attributes"""

__all__ = ["SardanaAttribute", "SardanaSoftwareAttribute",
           "ScalarNumberAttribute", "SardanaAttributeConfiguration"]

__docformat__ = 'restructuredtext'

import time
import weakref

from sardanaevent import  EventType
from sardanadefs import ScalarNumberFilter


class SardanaAttribute(object):
    """Class representing an atomic attribute like position of a motor or a
    counter value"""
    
    def __init__(self, obj, name=None, initial_value=None):
        if obj is not None:
            obj = weakref.ref(obj)
        self._obj = obj
        self.name = name or self.__class__.__name__
        #self._r_value = None # read value will be defined first time it is read
        self._last_event_value = None
        self._w_value = None
        self._r_timestamp = None
        self._w_timestamp = None
        self.exc_info = None
        self.error = False
        self.filter = lambda a,b: True
        self.config = SardanaAttributeConfiguration()
        if initial_value is not None:
            self.set_value(initial_value)
    
    def get_obj(self):
        obj = self._obj
        if obj is not None:
            obj = obj()
        return obj
    
    def has_value(self):
        return hasattr(self, '_r_value')
    
    def in_error(self):
        return self.error
    
    def set_value(self, value, exc_info=None, timestamp=None, propagate=1):
        if timestamp is None:
            timestamp = time.time()
        self._r_timestamp = timestamp
        self._r_value = value
        self.exc_info = exc_info
        self.error = exc_info is not None
        self.fire_event(propagate=propagate)
    
    def get_value(self):
        return self._r_value
    
    def set_write_value(self, w_value, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        self._w_value = w_value
        self._w_timestamp = timestamp
    
    def get_write_value(self):
        return self._w_value
    
    def get_exc_info(self):
        return self._r_exc_info
    
    def fire_event(self, propagate=1):
        if propagate < 1:
            return
        if propagate > 1 or self.filter(self._r_value, self._last_event_value):
            obj = self.obj
            if obj is not None:
                self._last_event_value = self._r_value
                obj.fire_event(EventType(self.name, priority=propagate), self)
    
    @property
    def timestamp(self):
        return self._r_timestamp
    
    obj = property(get_obj, "container object for this attribute")
    value = property(get_value, set_value, "current value for this attribute")
    w_value = property(get_write_value, set_write_value,
                       "current write value for this attribute")
    
    def __repr__(self):
        v = None
        if self.in_error():
            v = "<Error>"
        elif self.has_value():
            v = self.value
        return "{0}(value={1})".format(self.name, v)


class SardanaSoftwareAttribute(SardanaAttribute):
    
    get_value = SardanaAttribute.get_value
    
    def set_value(self, value, exc_info=None, timestamp=None, propagate=1):
        SardanaAttribute.set_value(self, value, exc_info=exc_info,
                                   timestamp=timestamp)
        self.set_write_value(value, timestamp=self._r_timestamp)
    
    value = property(get_value, set_value, "current value for this attribute")


class ScalarNumberAttribute(SardanaAttribute):
    
    def __init__(self, *args, **kwargs):
        SardanaAttribute.__init__(self, *args, **kwargs)
        self.filter = ScalarNumberFilter()


class SardanaAttributeConfiguration(object):

    NoRange = float('-inf'), float('inf')
    
    def __init__(self):
        self.range = self.NoRange
        self.alarm = self.NoRange
        self.warning = self.NoRange


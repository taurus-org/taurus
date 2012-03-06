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
        """Returns the object which *owns* this attribute
        
        :return: the object which *owns* this attribute
        :rtype: obj"""
        obj = self._obj
        if obj is not None:
            obj = obj()
        return obj
    
    def has_value(self):
        """Determines if the attribute's read value has been read at least once
        in the lifetime of the attribute.
        
        :return: True if the attribute has a read value stored or False otherwise
        :rtype: bool"""
        return hasattr(self, '_r_value')
    
    def in_error(self):
        """Determines if this attribute is in error state.
        
        :return: True if the attribute is in error state or False otherwise
        :rtype: bool"""
        return self.error
    
    def set_value(self, value, exc_info=None, timestamp=None, propagate=1):
        """Sets the current read value and propagates the event (if
        propagate > 0).
        
        :param value: the new read value for this attribute
        :type value: obj
        :param exc_info: exception information as returned by
                         :func:`sys.exc_info` [default: None, meaning no
                         exception]
        :type exc_info: tuple<3> or None
        :param timestamp: timestamp of attribute readout [default: None, meaning
                          create a 'now' timestamp]
        :type timestamp: float or None
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate: int"""
        if timestamp is None:
            timestamp = time.time()
        self._r_timestamp = timestamp
        self._r_value = value
        self.exc_info = exc_info
        self.error = exc_info is not None
        self.fire_event(propagate=propagate)
    
    def get_value(self):
        """Returns the last read value for this attribute.
        
        :return: the last read value for this attribute
        :rtype: obj
        
        :raises: :exc:`Exception` if no read value has been set yet"""
        if not self.has_value():
            raise Exception("{0}.{1} doesn't have a read value yet".format(
                            self.obj.name, self.name))
        return self._r_value
    
    def set_write_value(self, w_value, timestamp=None):
        """Sets the current write value.
        
        :param w_value: the write read value for this attribute
        :type w_value: obj
        :param timestamp: timestamp of attribute write [default: None, meaning
                          create a 'now' timestamp]
        :type timestamp: float or None"""
        if timestamp is None:
            timestamp = time.time()
        self._w_value = w_value
        self._w_timestamp = timestamp
    
    def get_write_value(self):
        """Returns the last write value for this attribute.
        
        :return: the last write value for this attribute or None if value has
                 not been written yet
        :rtype: obj"""
        return self._w_value
    
    def get_exc_info(self):
        """Returns the exception information (like :func:`sys.exc_info`) about
        last attribute readout or None if last read did not generate an
        exception.
        
        :return: exception information or None
        :rtype: tuple<3> or None"""
        return self.exc_info
    
    def fire_event(self, propagate=1):
        """Fires an event to the listeners of the object which owns this
        attribute.
        
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate: int"""
        if propagate < 1:
            return
        if propagate > 1 or self.filter(self._r_value, self._last_event_value):
            obj = self.obj
            if obj is not None:
                self._last_event_value = self._r_value
                obj.fire_event(EventType(self.name, priority=propagate), self)
    
    @property
    def timestamp(self):
        """Returns the timestamp of the last readout or None if the attribute 
        has never been read before
        
        :return: timestamp of the last readout or None
        :rtype: float or None"""
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
    """Class representing a software attribute. The difference between this and
    :class:`SardanaAttribute` is that, because it is a pure software attribute,
    there is no difference ever between the read and write values."""
    
    get_value = SardanaAttribute.get_value
    
    def set_value(self, value, exc_info=None, timestamp=None, propagate=1):
        """Sets the current read value and propagates the event (if
        propagate > 0).
        
        :param value: the new read value for this attribute
        :type value: obj
        :param exc_info: exception information as returned by
                         :func:`sys.exc_info` [default: None, meaning no
                         exception]
        :type exc_info: tuple<3> or None
        :param timestamp: timestamp of attribute readout [default: None, meaning
                          create a 'now' timestamp]
        :type timestamp: float or None
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate: int"""
        SardanaAttribute.set_value(self, value, exc_info=exc_info,
                                   timestamp=timestamp)
        self.set_write_value(value, timestamp=self._r_timestamp)
    
    value = property(get_value, set_value, "current value for this attribute")


class ScalarNumberAttribute(SardanaAttribute):
    """A :class:`SardanaAttribute` speciallized for numbers"""
    
    def __init__(self, *args, **kwargs):
        SardanaAttribute.__init__(self, *args, **kwargs)
        self.filter = ScalarNumberFilter()


class SardanaAttributeConfiguration(object):
    """Storage class for :class:`SardanaAttribute` information (like ranges)"""
    NoRange = float('-inf'), float('inf')
    
    def __init__(self):
        self.range = self.NoRange
        self.alarm = self.NoRange
        self.warning = self.NoRange


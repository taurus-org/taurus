#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
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

from __future__ import absolute_import

__all__ = ["SardanaAttribute", "SardanaSoftwareAttribute",
           "ScalarNumberAttribute", "SardanaAttributeConfiguration"]

__docformat__ = 'restructuredtext'

import weakref
import datetime

from .sardanaevent import EventGenerator, EventType
from .sardanadefs import ScalarNumberFilter
from .sardanavalue import SardanaValue


class SardanaAttribute(EventGenerator):
    """Class representing an atomic attribute like position of a motor or a
    counter value"""

    def __init__(self, obj, name=None, initial_value=None, **kwargs):
        super(SardanaAttribute, self).__init__(**kwargs)
        if obj is not None:
            obj = weakref.ref(obj)
        self._obj = obj
        self.name = name or self.__class__.__name__
        self._r_value = None
        self._last_event_value = None
        self._w_value = None
        self.filter = lambda a, b: True
        self.config = SardanaAttributeConfiguration()
        if initial_value is not None:
            self.set_value(initial_value)

    def has_value(self):
        """Determines if the attribute's read value has been read at least once
        in the lifetime of the attribute.
        
        :return: True if the attribute has a read value stored or False otherwise
        :rtype: bool"""
        return self._has_value()

    def _has_value(self):
        return not self._r_value is None

    def has_write_value(self):
        """Determines if the attribute's write value has been read at least once
        in the lifetime of the attribute.
        
        :return: True if the attribute has a write value stored or False otherwise
        :rtype: bool"""
        return self._has_write_value()

    def _has_write_value(self):
        return self._w_value is not None

    def get_obj(self):
        """Returns the object which *owns* this attribute
        
        :return: the object which *owns* this attribute
        :rtype: obj"""
        return self._get_obj()

    def _get_obj(self):
        obj = self._obj
        if obj is not None:
            obj = obj()
        return obj

    def in_error(self):
        """Determines if this attribute is in error state.
        
        :return: True if the attribute is in error state or False otherwise
        :rtype: bool"""
        return self._in_error()

    def _in_error(self):
        return self.has_value() and self._r_value.error

    def set_value(self, value, exc_info=None, timestamp=None, propagate=1):
        """Sets the current read value and propagates the event (if
        propagate > 0).
        
        :param value: the new read value for this attribute. If a SardanaValue
                      is given, exc_info and timestamp are ignored (if given)
        :type value: obj or SardanaValue
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
        return self._set_value(value, exc_info=exc_info, timestamp=timestamp,
                               propagate=propagate)

    def _set_value(self, value, exc_info=None, timestamp=None, propagate=1):
        if isinstance(value, SardanaValue):
            rvalue = value
        else:
            rvalue = SardanaValue(value=value, exc_info=exc_info, timestamp=timestamp)
        self._r_value = rvalue
        self.fire_read_event(propagate=propagate)

    def get_value(self):
        """Returns the last read value for this attribute.
        
        :return: the last read value for this attribute
        :rtype: obj
        
        :raises: :exc:`Exception` if no read value has been set yet"""
        return self._get_value()

    def _get_value(self):
        return self.get_value_obj().value

    def get_value_obj(self):
        """Returns the last read value for this attribute.
        
        :return: the last read value for this attribute
        :rtype: :class:`~sardana.sardanavalue.SardanaValue`
        
        :raises: :exc:`Exception` if no read value has been set yet"""
        return self._get_value_obj()

    def _get_value_obj(self):
        if not self.has_value():
            raise Exception("{0}.{1} doesn't have a read value yet".format(
                            self.obj.name, self.name))
        return self._r_value

    def set_write_value(self, w_value, timestamp=None, propagate=1):
        """Sets the current write value.
        
        :param value: the new write value for this attribute. If a SardanaValue
                      is given, timestamp is ignored (if given)
        :type value: obj or SardanaValue
        :param timestamp: timestamp of attribute write [default: None, meaning
                          create a 'now' timestamp]
        :type timestamp: float or None
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate: int"""
        return self._set_write_value(w_value, timestamp=timestamp,
                                     propagate=propagate)

    def _set_write_value(self, w_value, timestamp=None, propagate=1):
        if isinstance(w_value, SardanaValue):
            wvalue = w_value
        else:
            wvalue = SardanaValue(value=w_value, timestamp=timestamp)
        self._w_value = wvalue
        self.fire_write_event(propagate=propagate)

    def get_write_value(self):
        """Returns the last write value for this attribute.
        
        :return: the last write value for this attribute or None if value has
                 not been written yet
        :rtype: obj"""
        return self._get_write_value()

    def _get_write_value(self):
        w_value = self.get_write_value_obj()
        if w_value is not None:
            return w_value.value

    def get_write_value_obj(self):
        """Returns the last write value object for this attribute.
        
        :return: the last write value for this attribute or None if value has
                 not been written yet
        :rtype: :class:`~sardana.sardanavalue.SardanaValue`"""
        return self._get_write_value_obj()

    def _get_write_value_obj(self):
        if self.has_write_value():
            return self._w_value

    def get_exc_info(self):
        """Returns the exception information (like :func:`sys.exc_info`) about
        last attribute readout or None if last read did not generate an
        exception.
        
        :return: exception information or None
        :rtype: tuple<3> or None"""
        return self._get_exc_info()

    def _get_exc_info(self):
        exc_info = None
        if self.has_value():
            exc_info = self._r_value.exc_info
        return exc_info

    def accepts(self, propagate):
        if propagate < 1:
            return False
        if self._last_event_value is None:
            return True
        return propagate > 1 or self.filter(self.get_value(), self._last_event_value.value)

    def get_timestamp(self):
        """Returns the timestamp of the last readout or None if the attribute 
        has never been read before
        
        :return: timestamp of the last readout or None
        :rtype: float or None"""
        return self._get_timestamp()

    def _get_timestamp(self):
        if self.has_value():
            return self._r_value.timestamp

    def get_write_timestamp(self):
        """Returns the timestamp of the last write or None if the attribute 
        has never been written before
        
        :return: timestamp of the last write or None
        :rtype: float or None"""
        return self._get_write_timestamp()

    def _get_write_timestamp(self):
        if self.has_write_value():
            return self._w_value.timestamp

    def fire_write_event(self, propagate=1):
        """Fires an event to the listeners of the object which owns this
        attribute.
        
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate: int"""
        if propagate < 1:
            return
        evt_type = EventType("w_" + self.name, priority=propagate)
        self.fire_event(evt_type, self)

    def fire_read_event(self, propagate=1):
        """Fires an event to the listeners of the object which owns this
        attribute.
        
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate: int"""
        if self.accepts(propagate):
            obj = self.obj
            if obj is not None:
                self._last_event_value = self._r_value
                evt_type = EventType(self.name, priority=propagate)
                self.fire_event(evt_type, self)

    obj = property(get_obj, "container object for this attribute")
    value_obj = property(get_value_obj)
    write_value_obj = property(get_write_value_obj)
    value = property(get_value, set_value, "current read value for this attribute")
    w_value = property(get_write_value, set_write_value,
                       "current write value for this attribute")
    timestamp = property(get_timestamp, doc="the read timestamp")
    w_timestamp = property(get_write_timestamp, doc="the write timestamp")
    error = property(in_error)
    exc_info = property(get_exc_info)

    def __repr__(self):
        v = None
        if self.in_error():
            v = "<Error>"
        elif self.has_value():
            v = self.value
        return "{0}(value={1})".format(self.name, v)

    def __str__(self):
        if self.has_value():
            value = "{0} at {1}".format(self.value, datetime.datetime.fromtimestamp(self.timestamp))
        else:
            value = "-----"
        if self.has_write_value():
            w_value = "{0} at {1}".format(self.w_value, datetime.datetime.fromtimestamp(self.w_timestamp))
        else:
            w_value = "-----"

        ret = """{0.__class__.__name__}(
       name = {0.name}
    manager = {0.obj}
       read = {1}
      write = {2})
""".format(self, value, w_value)
        return ret


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
        self.set_write_value(value, timestamp=self.timestamp)

    value = property(get_value, set_value, "current value for this attribute")


class ScalarNumberAttribute(SardanaAttribute):
    """A :class:`SardanaAttribute` specialized for numbers"""

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


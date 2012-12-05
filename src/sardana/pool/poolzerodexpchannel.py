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
for ZeroDExpChannel"""

__all__ = [ "Pool0DExpChannel" ]

__docformat__ = 'restructuredtext'

import numpy
import time

from sardana import ElementType
from sardana.sardanaevent import EventType
from sardana.sardanaattribute import SardanaAttribute

from .poolbasechannel import PoolBaseChannel
from .poolacquisition import Pool0DAcquisition

class BaseAccumulation(object):

    def __init__(self):
        self.buffer = numpy.zeros(shape=(2,16384), dtype=numpy.float64)
        self.clear()
        
    def clear(self):
        self.nb_points = 0
        self.value = None
    
    def get_value_buffer(self):
        return self.buffer[0][:self.nb_points]
    
    def get_time_buffer(self):
        return self.buffer[1][:self.nb_points]

    def append_value(self, value, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        idx = self.nb_points
        self.nb_points += 1
        self.buffer[0][idx] = value
        self.buffer[1][idx] = timestamp
        self.update_value(value, timestamp)

    def update_value(self, value, timestamp):
        self.value = value
    
    
LastAccumulation = BaseAccumulation

class SumAccumulation(BaseAccumulation):
    
    def clear(self):
        BaseAccumulation.clear(self)
        self.sum = 0.0
    
    def update_value(self, value, timestamp):
        self.sum += value


class AverageAccumulation(SumAccumulation):
    
    def update_value(self, value, timestamp):
        SumAccumulation.update_value(self, value, timestamp)
        self.value = self.sum / self.nb_points


class IntegralAccumulation(BaseAccumulation):

    def clear(self):
        BaseAccumulation.clear(self)
        self.sum = 0.0
        self.last_value = None
        self.start_time = None
    
    def update_value(self, value, timestamp):
        if self.nb_points == 1:
            self.last_value = value, timestamp
            self.start_time = timestamp
            self.value = value
        else:
            last_value, last_timestamp = self.last_value
            dt = timestamp - last_timestamp
            self.sum += dt*(last_value + value) / 2.0
            total_dt = timestamp - self.start_time
            self.value = self.sum / total_dt
            self.last_value = value, timestamp


def get_accumulation_class(ctype):
    return globals()[ctype + "Accumulation"]


class CurrentValue(SardanaAttribute):

    def update(self, cache=True, propagate=1):
        if not cache or not self.has_value():
            value = self.obj.read_current_value()
            self.set_value(value, propagate=propagate)


class Value(SardanaAttribute):

    DefaultAccumulationType = "Average"

    def __init__(self, *args, **kwargs):
        accumulation_type = kwargs.pop('accumulation_type', self.DefaultAccumulationType)
        super(Value, self).__init__(*args, **kwargs)
        self.set_accumulation_type(accumulation_type)
    
    def get_val(self):
        return self.obj.get_value_attribute()
    
    def set_accumulation_type(self, ctype):
        klass = get_accumulation_class(ctype)
        self._accumulation = klass()
    
    def get_accumulation_type(self):
        klass_name = self._accumulation.__class__.__name__
        return klass_name[:klass_name.index("Accumulation")]
    
    def get_accumulation(self):
        return self._accumulation
    
    accumulation = property(get_accumulation)
    
    def _get_value(self):
        value = self._accumulation.value
        if value is None:
            raise Exception("Value not available: no acquisition done so far!")
        return value
    
    def get_value_buffer(self):
        return self.accumulation.get_value_buffer()
    
    def get_time_buffer(self):
        return self.accumulation.get_time_buffer()
        
    def clear_buffer(self):
        self.accumulation.clear()
    
    def append_value(self, value, propagate=1):
        self.accumulation.append_value(value.value, value.timestamp)
        if propagate > 0:
            evt_type = EventType(self.name, priority=propagate)
            self.fire_event(evt_type, self)        
    
        
class Pool0DExpChannel(PoolBaseChannel):
    
    ValueAttributeClass = Value
    AcquisitionClass = Pool0DAcquisition
    
    def __init__(self, **kwargs):
        kwargs['elem_type'] = ElementType.ZeroDExpChannel
        PoolBaseChannel.__init__(self, **kwargs)
        self._current_value = CurrentValue(self, listeners=self.on_change)
        
    # --------------------------------------------------------------------------
    # Accumulation
    # --------------------------------------------------------------------------
                
    def get_accumulation_type(self):
        return self.get_value_attribute().get_accumulation_type()
    
    def get_accumulation(self):
        return self.get_value_attribute().get_accumulation()
    
    def set_accumulation_type(self, ctype):
        return self.get_value_attribute().set_accumulation_type(ctype)
    
    accumulation = property(get_accumulation)
    
    # --------------------------------------------------------------------------
    # value
    # --------------------------------------------------------------------------
    
    def get_accumulated_value_attribute(self):
        """Returns the accumulated value attribute object for this 0D.
        
        :return: the accumulated value attribute
        :rtype: :class:`~sardana.sardanaattribute.SardanaAttribute`"""        
        return self.get_value_attribute()

    def get_current_value_attribute(self):
        """Returns the current value attribute object for this 0D.
        
        :return: the current value attribute
        :rtype: :class:`~sardana.sardanaattribute.SardanaAttribute`"""        
        return self._current_value
            
    def get_accumulated_value(self):
        """Gets the accumulated value for this 0D.

        :return:
            a :class:`~sardana.sardanavalue.SardanaValue` containing the 0D
            value
        :rtype:
            :class:`~sardana.sardanaattribute.SardanaAttribute`
        
        :raises: Exception if no acquisition has been done yet on this 0D"""         
        return self.get_accumulated_value_attribute()
    
    def read_current_value(self):
        """Reads the 0D value from hardware.

        :return:
            a :class:`~sardana.sardanavalue.SardanaValue` containing the counter
            value
        :rtype:
            :class:`~sardana.sardanavalue.SardanaValue`"""        
        return self.acquisition.read_value()[self]    

    def put_current_value(self, value, propagate=1):
        """Sets a value.

        :param value:
            the new value
        :type value:
            :class:`~sardana.sardanavalue.SardanaValue`
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int"""
        curr_val_attr = self.get_current_value_attribute()
        curr_val_attr.set_value(value, propagate=propagate)
        if self.is_in_operation():
            acc_val_attr = self.get_accumulated_value_attribute()
            acc_val_attr.append_value(value, propagate=propagate)
            
    def get_current_value(self, cache=True, propagate=1):
        """Returns the counter value.

        :return:
            the 0D accumulated value
        :rtype:
            :class:`~sardana.sardanaattribute.SardanaAttribute`"""
        curr_val_attr = self.get_current_value_attribute()
        curr_val_attr.update(cache=cache, propagate=propagate)
        return curr_val_attr

    current_value = property(get_current_value, doc="0D value")
    accumulated_value = property(get_accumulated_value, doc="0D value")

    def put_value(self, value, propagate=1):
        return self.put_current_value(value, propagate=propagate)

    def _get_value(self):
        return self.get_current_value()
    
    def append_value(self, value, timestamp=None, propagate=1):
        cumulation = self.cumulation
        cumulation.append_value(value, timestamp)
        if not propagate:
            return
        self.fire_event(EventType("value", priority=propagate), cumulation.value)

    def clear_buffer(self):
        self.get_accumulated_value_attribute().clear_buffer()
            
    # --------------------------------------------------------------------------
    # value buffer
    # --------------------------------------------------------------------------
    
    def get_value_buffer(self):
        return self.get_accumulated_value_attribute().get_value_buffer()
    
    value_buffer = property(get_value_buffer)
    
    # --------------------------------------------------------------------------
    # time buffer
    # --------------------------------------------------------------------------
    
    def get_time_buffer(self):
        return self.get_accumulated_value_attribute().get_time_buffer()
    
    time_buffer = property(get_time_buffer)

    def start_acquisition(self, value=None):
        self._aborted = False
        self.clear_buffer()
        if value is None:
            raise Exception("Invalid integration_time '%s'. Hint set a new value for 'value' first" % value)
        if not self._simulation_mode:
            acq = self.acquisition.run()
    
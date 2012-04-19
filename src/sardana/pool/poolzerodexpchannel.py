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
for ZeroDExpChannel"""

__all__ = [ "Pool0DExpChannel" ]

__docformat__ = 'restructuredtext'

import numpy
import time
import weakref

from taurus.core.util import CaselessDict

from sardana import ElementType
from sardana.sardanaevent import EventType
from poolelement import PoolElement
from poolacquisition import Pool0DAcquisition

class BaseCumulation(object):

    def __init__(self, channel):
        self._channel = weakref.ref(channel)
        self.buffer = numpy.zeros(shape=(2,16384), dtype=numpy.float64)
        self.clear()
        
    def clear(self):
        self.nb_points = 0
        self.value = None
    
    def get_channel(self):
        return self._channel()
        
    channel = property(get_channel)
    
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

LastCumulation = BaseCumulation

class SumCumulation(BaseCumulation):
    
    def clear(self):
        BaseCumulation.clear(self)
        self.sum = 0.0
    
    def update_value(self, value, timestamp):
        self.sum += value


class AverageCumulation(SumCumulation):
    
    def update_value(self, value, timestamp):
        SumCumulation.update_value(self, value, timestamp)
        self.value = self.sum / self.nb_points


class IntegralCumulation(BaseCumulation):

    def clear(self):
        BaseCumulation.clear(self)
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


def get_cumulation_class(ctype):
    return globals()[ctype + "Cumulation"]


class Pool0DExpChannel(PoolElement):
    
    def __init__(self, **kwargs):
        PoolElement.__init__(self, **kwargs)
        self._aborted = False
        self.set_cumulation_type("Average")
        acq_name = "%s.Acquisition" % self._name
        self.set_action_cache(Pool0DAcquisition(self, acq_name))
        
    def get_type(self):
        return ElementType.ZeroDExpChannel
    
    def set_cumulation_type(self, ctype):
        klass = get_cumulation_class(ctype)
        self._cumulation = klass(self)
    
    def get_cumulation_type(self):
        klass_name = self._cumulation.__class__.__name__
        return klass_name[:klass_name.index("Cumulation")]
    
    def get_cumulation(self):
        return self._cumulation
    
    cumulation = property(get_cumulation)
    
    # --------------------------------------------------------------------------
    # value
    # --------------------------------------------------------------------------
    
    def read_value(self):
        return self.acquisition.read_value()[self]
    
    def put_value(self, value, propagate=1):
        self._set_value(value, propagate=propagate)
    
    def get_value(self, propagate=1):
        value = self.cumulation.value
        if value is None:
            raise Exception("Value not available: no acquisition done so far!")
        return value
    
    def set_value(self, value, propagate=1):
        self._set_value(value, propagate=propagate)
    
    def _set_value(self, value, propagate=1):
        if self.is_in_operation():
            self.append_value(value, propagate=propagate)
            return
        if not propagate:
            return
        self.fire_event(EventType("value", priority=propagate), value)
    
    value = property(get_value, set_value, doc="0D value")
    
    def clear_buffer(self):
        self.cumulation.clear()
    
    def append_value(self, value, timestamp=None, propagate=1):
        cumulation = self.cumulation
        cumulation.append_value(value, timestamp)
        if not propagate:
            return
        self.fire_event(EventType("value", priority=propagate), cumulation.value)
    
    # --------------------------------------------------------------------------
    # value buffer
    # --------------------------------------------------------------------------
    
    def get_value_buffer(self):
        return self.cumulation.get_value_buffer()
    
    value_buffer = property(get_value_buffer)
    
    # --------------------------------------------------------------------------
    # time buffer
    # --------------------------------------------------------------------------
    
    def get_time_buffer(self):
        return self.cumulation.get_time_buffer()
    
    time_buffer = property(get_time_buffer)
    
    # --------------------------------------------------------------------------
    # default acquisition channel
    # --------------------------------------------------------------------------
    
    def get_default_acquisition_channel(self):
        return 'value'
    
    # --------------------------------------------------------------------------
    # acquisition
    # --------------------------------------------------------------------------
    
    def get_acquisition(self):
        return self.get_action_cache()
    
    acquisition = property(get_acquisition, doc="acquisition object")
    
    def start_acquisition(self, value=None):
        self._aborted = False
        self.clear_buffer()
        if value is None:
            raise Exception("Invalid integration_time '%s'. Hint set a new value for 'value' first" % value)
        if not self._simulation_mode:
            acq = self.acquisition.run()
    
    def get_source(self):
        return "{0}/value".format(self.full_name)

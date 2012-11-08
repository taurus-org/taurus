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
for TwoDExpChannel"""

__all__ = [ "Pool2DExpChannel" ]

__docformat__ = 'restructuredtext'

from sardana import ElementType
from sardana.sardanaevent import EventType

from poolelement import PoolElement
from poolacquisition import Pool2DAcquisition


class Pool2DExpChannel(PoolElement):

    def __init__(self, **kwargs):
        PoolElement.__init__(self, **kwargs)
        self._data_source = None
        self._value = None
        self._wvalue = None
        acq_name = "%s.Acquisition" % self._name
        self.set_action_cache(Pool2DAcquisition(self, name=acq_name))
    
    def get_type(self):
        return ElementType.TwoDExpChannel

    # --------------------------------------------------------------------------
    # data source
    # --------------------------------------------------------------------------

    def get_data_source(self, cache=True, propagate=1):
        if not cache or self._data_source is None:
            data_source = self.read_data_source()
            self._set_data_source(data_source, propagate=propagate)
        return self._data_source

    def _set_data_source(self, data_source, propagate=1):
        self._data_source = data_source
        if not propagate:
            return
        self.fire_event(EventType("data_source", priority=propagate), data_source)

    def read_data_source(self):
        data_source = self.controller.get_axis_par(self.axis, "data_source")
        return data_source

    data_source = property(get_data_source, doc="source identifier for the 2D data")    
        
    # --------------------------------------------------------------------------
    # value
    # --------------------------------------------------------------------------
    
    def read_value(self):
        return self.acquisition.read_value()[self]
    
    def put_value(self, value, propagate=1):
        self._set_value(value, propagate=propagate)
    
    def get_value(self, cache=True, propagate=1):
        if not cache or self._value is None:
            value, exc_info = self.read_value()
            if exc_info is not None:
                raise exc_info[1]
            self._set_value(value, propagate=propagate)
        return self._value
    
    def get_value_w(self):
        return self._wvalue
    
    def set_value(self, value, propagate=1):
        self._wvalue = value
        self._set_value(value, propagate=propagate)
        
    def _set_value(self, value, propagate=1):
        self._value = value
        if not propagate:
            return
        self.fire_event(EventType("value", priority=propagate), value)
    
    value = property(get_value, set_value, doc="2D value")
    
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
        self._stopped = False
        value = value or self.get_value_w()
        if value is None:
            raise Exception("Invalid integration_time '%s'. Hint set a new value for 'value' first" % value)
        if not self._simulation_mode:
            acq = self.acquisition.run(integ_time=value)
    
    def get_source(self):
        return "{0}/value".format(self.full_name)
    
    

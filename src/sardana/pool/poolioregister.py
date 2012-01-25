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
for """

__all__ = [ "PoolIORegister" ]

__docformat__ = 'restructuredtext'

from sardana import ElementType
from sardana.sardanaevent import EventType

from poolelement import PoolElement
from poolacquisition import PoolIORAcquisition

class PoolIORegister(PoolElement):

    def __init__(self, **kwargs):
        PoolElement.__init__(self, **kwargs)
        self._value = None
        self._wvalue = None
        self._config = None
        acq_name = "%s.Acquisition" % self._name
        self.set_action_cache(PoolIORAcquisition(self.pool, name=acq_name))
    
    def get_type(self):
        return ElementType.IORegister
    
    # --------------------------------------------------------------------------
    # value
    # --------------------------------------------------------------------------
    
    def read_value(self):
        return self.get_action_cache().read_value()[self]
    
    def put_value(self, value, propagate=1):
        self._set_value(value, propagate=propagate)
    
    def get_value(self, cache=True, propagate=1):
        if not cache or self._value is None:
            value , exc_info = self.read_value()
            if exc_info is not None:
                raise exc_info[1]
            self._set_value(value, propagate=propagate)
        return self._value
    
    def get_value_w(self):
        return self._wvalue
    
    def set_value(self, value, propagate=1):
        self._wvalue = value
        self.controller.write_one(self.axis, value)
        self._set_value(value, propagate=propagate)
        
    def _set_value(self, value, propagate=1):
        self._value = value
        if not propagate:
            return
        self.fire_event(EventType("value", priority=propagate), value)
    
    value = property(get_value, set_value, doc="ioregister value")
    
    # --------------------------------------------------------------------------
    # default acquisition channel
    # --------------------------------------------------------------------------
    
    def get_default_acquisition_channel(self):
        return 'value'
    
    def get_source(self):
        return "{0}/value".format(self.full_name)

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

__all__ = [ "PoolMeasurementGroup" ]

__docformat__ = 'restructuredtext'

import math

from poolbase import *
from pooldefs import *
from poolelement import *
from poolacquisition import *


class PoolMeasurementGroupElementItem(object):
    
    def __init__(self, ctrl):
        self.value = None
        self.ctrl = ctrl

class PMGEIMotor(PoolMeasurementGroupElementItem):
    pass

class PMGEICounterTimer(PoolMeasurementGroupElementItem):
    pass

class PMGEITangoAttribute(PoolMeasurementGroupElementItem):
    pass

class PGCtrl(object):
    
    pass


class PoolMeasurementGroup(PoolGroupElement):

    def __init__(self, **kwargs):
        PoolGroupElement.__init__(self, **kwargs)
        self.set_action_cache(PoolAcquisition("%s.Acquisition" % self._name))
    
    def get_type(self):
        return ElementType.MeasurementGroup
    
    def on_element_changed(self, evt_src, evt_type, evt_value):
        pass
    
    # --------------------------------------------------------------------------
    # acquisition
    # --------------------------------------------------------------------------
    
    def acquire(self):
        pass
    
    def get_acquisition(self):
        return self.get_action_cache()
    
    acquisition = property(get_acquisition, doc="acquisition object")
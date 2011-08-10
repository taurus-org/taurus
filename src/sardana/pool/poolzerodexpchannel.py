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

from pooldefs import ElementType
from poolevent import EventType
from poolelement import PoolElement
#from poolacquisition import PoolCTAcquisition

class Pool0DExpChannel(PoolElement):

    def __init__(self, **kwargs):
        PoolElement.__init__(self, **kwargs)
        self._value = None
        self._wvalue = None
        #self.set_action_cache(PoolCTAcquisition("%s.Acquisition" % self._name))
        self._aborted = False
    
    def get_type(self):
        return ElementType.ZeroDExpChannel
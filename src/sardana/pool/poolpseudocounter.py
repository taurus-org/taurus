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

"""This module is part of the Python Pool libray. It defines the
PoolPseudoCounter class"""

__all__ = [ "PoolPseudoCounter" ]

__docformat__ = 'restructuredtext'

from sardana import State, ElementType, TYPE_PHYSICAL_ELEMENTS
from sardana.sardanaevent import EventType

from poolelement import PoolBaseElement, PoolElement
from poolgroupelement import PoolBaseGroup


class PoolPseudoCounter(PoolBaseGroup, PoolElement):
    
    def __init__(self, **kwargs):
        self._physical_positions = {}
        self._low_level_physical_positions = {}
        self._value = None
        self._siblings = None
        user_elements = kwargs.pop('user_elements')
        PoolElement.__init__(self, **kwargs)
        PoolBaseGroup.__init__(self, user_elements=user_elements)
    
    
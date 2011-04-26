#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""Extension of :mod:`guiqwt.builder`"""

__docformat__ = 'restructuredtext'

import guiqwt.builder
from curve import TaurusCurveItem


class TaurusPlotItemBuilder(guiqwt.builder.PlotItemBuilder):
    '''extension of :class:`guiqwt.builder.PlotItemBuilder` to provide tauruscurve and taurusimage items'''
    def __init__(self, *args, **kwargs):
        guiqwt.builder.PlotItemBuilder.__init__(self, *args, **kwargs)
        
    def tauruscurve(self, xmodel, ymodel, **kwargs):
        '''
        Make a tauruscurve `plot item` from xmodel, ymodel model names. For
        valid keyword arguments, see :meth:`curve`
        
        :return: (TaurusCurveItem)
        '''
        pass
    
        
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

"""This package contains a collection of taurus Qt gauge widgets"""

__docformat__ = 'restructuredtext'

try:
    from .taurusgauge import *
except:
    from taurus.core.util.log import debug
    debug("Gauge widgets could not be initialized")
    from taurus.qt.qtgui.display import create_taurus_fallback as __create
    TaurusLinearGauge = __create("TaurusLinearGauge")
    TaurusCircularGauge = __create("TaurusCircularGauge")

from .qmeter import *

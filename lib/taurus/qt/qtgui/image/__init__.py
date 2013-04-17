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

"""This package contains a collection of Qt designed to present 2D data"""

__docformat__ = 'restructuredtext'

try:
    from .taurusqub import *
except:
    from taurus.qt.qtgui.display import create_fallback as __create
    TaurusQubDataImageDisplay = __create("TaurusQubDataImageDisplay")
    import taurus.core.util.log
    _logger = taurus.core.util.log.Logger(__name__)
    _logger.debug("Qub widgets could not be initialized", exc_info=1)

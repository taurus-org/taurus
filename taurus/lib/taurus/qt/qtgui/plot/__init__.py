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

"""
Taurus Widget Plot module
==========================

This module is part of Taurus Widgets. It contains specialized widgets for 2D plotting
in Taurus. It depends on the `PyQwt module <http://pyqwt.sourceforge.net/>`_
"""

from .qwtdialog import *
from .scales import *
from .taurusplot import *
from .taurustrend import *
from .arrayedit import ArrayEditor
from .taurusarrayedit import TaurusArrayEditor
from .curvesAppearanceChooserDlg import CurveAppearanceProperties, CurvesAppearanceChooser
from .curveprops import CurvePropertiesView
from .monitor import TaurusMonitorTiny
from .curveStatsDlg import CurveStatsDialog
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

"""This package contains a collection of Qt based widgets designed to interact with
taurus models. The widgets are generic in the sence that they do not assume any
behavior associated with a specific HW device. They intend to represent only
abstract model data."""

__docformat__ = 'restructuredtext'

import release as Release

from tau.core.utils import Logger

_logger = Logger(__name__)

from colors import QT_DEVICE_STATE_PALETTE, QT_ATTRIBUTE_QUALITY_PALETTE
from taubase import TauBaseWidget, TauBaseComponent
from labels import *
from scalaredit import *
from combobox import TauValueComboBox, TauAttrListComboBox
#from combobox import TauQueryComboBox
from LCD import TauLCDValue
from leds import TauStateLed
from leds import TauBoolLed
from buttons import TauLauncherButton, TauCommandButton
from containers import TauBaseContainer, TauFrame, TauGroupBox
from containers import TauScrollArea, TauWidget
from mainwindow import TauMainWindow
from graphics import TauGraphicsScene
from graphics import TauGraphicsItem, TauGraphicsAttributeItem
from graphics import TauGraphicsStateItem, TauGroupStateItem
from graphics import TauEllipseStateItem, TauRectStateItem, TauPolygonStateItem
from graphics import TauTextStateItem, TauTextAttributeItem
from graphics import AbstractGraphicsFactory
from graphicsview import TauGraphicsView#, TauJDrawSynopticsView
#from led import *
Led = QLed
from limitswitch import TauLimitSwitch
from actionfactory import *
from widgetfactory import TauWidgetFactory
from buttonbox import TauButtonBox
from tauvalue import TauValue, TauValuesFrame
from forms import TauForm, TauAttrForm, TauCommandsForm
from valuestable import TauValuesTable
from logger import TauLoggerTable, TauLoggerWidget
from configuration import BaseConfigurableClass

#from .taubase import *
#
#from taurus.qt.qtcore.configuration import *
#from taurus.qt.qtgui.util import *
#from taurus.qt.qtgui.button import *
#from taurus.qt.qtgui.container import *
#from taurus.qt.qtgui.display import *
#from taurus.qt.qtgui.input import *
#from taurus.qt.qtgui.table import *
#from taurus.qt.qtgui.panel import *
#from taurus.qt.qtgui.gauge import *
#from taurus.qt.qtgui.graphic import *
#
## renamed widgets in taurus 2.0
#TauBaseConfigurableClass = None
#TauClassTable = None
#TauQueryComboBox = None
#Led = QLed
#
#
#try:
#    TauJDrawSynopticsView = TaurusJDrawSynopticsView
#except NameError:
#    pass
#
#try:
#    TauPropTable = TaurusPropTable
#except NameError:
#    pass
#
#try:
#    TauDevTree = TaurusDevTree
#except NameError:
#    pass
#
#try:
#    TauGrid = TaurusGrid
#except NameError:
#    pass



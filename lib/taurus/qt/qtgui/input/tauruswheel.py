#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This module provides a set of basic taurus widgets based on QWheelEdit"""

from __future__ import absolute_import

from taurus.external.qt import Qt

from taurus.core.taurusbasetypes import TaurusEventType
from taurus.qt.qtgui.base import TaurusBaseWritableWidget
from .qwheel import QWheelEdit


__all__ = ["TaurusWheelEdit"]

__docformat__ = 'restructuredtext'


class TaurusWheelEdit(QWheelEdit, TaurusBaseWritableWidget):

    def __init__(self, qt_parent=None, designMode=False):
        name = self.__class__.__name__
        self.call__init__wo_kw(QWheelEdit, qt_parent)
        self.call__init__(TaurusBaseWritableWidget,
                          name, designMode=designMode)
        self.numberChanged.connect(self.notifyValueChanged)
        self.returnPressed.connect(self.writeValue)
        self.valueChangedSignal.connect(self.updatePendingOperations)
        self._configured = False

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_type == TaurusEventType.Config or not self._configured:
            if evt_value is not None:
                obj = self.getModelObj()
                # set decimal digits
                self.setDigitCount(int_nb=None, dec_nb=obj.precision)
                # set min and max values
                min_, max_ = obj.getRange()
                if min_ is not None:
                    self.setMinValue(min_.magnitude)
                if max_ is not None:
                    self.setMaxValue(max_.magnitude)
                self._configured = True

        TaurusBaseWritableWidget.handleEvent(
            self, evt_src, evt_type, evt_value)

    def updateStyle(self):
        TaurusBaseWritableWidget.updateStyle(self)
        if self.hasPendingOperations():
            self.setStyleSheet(
                'QWheelEdit {border: 2px solid; border-radius: 4px; border-color: blue}')
        else:
            self.setStyleSheet(
                'QWheelEdit {border: 2px solid; border-radius: 4px; border-color: rgba(0,0,255,0)}')

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWritableWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.input'
        ret['icon'] = "designer:wheeledit.png"
        return ret

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = Qt.pyqtProperty("QString", TaurusBaseWritableWidget.getModel,
                            TaurusBaseWritableWidget.setModel,
                            TaurusBaseWritableWidget.resetModel)

    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWritableWidget.getUseParentModel,
                                     TaurusBaseWritableWidget.setUseParentModel,
                                     TaurusBaseWritableWidget.resetUseParentModel)

    autoApply = Qt.pyqtProperty("bool", TaurusBaseWritableWidget.getAutoApply,
                                TaurusBaseWritableWidget.setAutoApply,
                                TaurusBaseWritableWidget.resetAutoApply)

    forcedApply = Qt.pyqtProperty("bool", TaurusBaseWritableWidget.getForcedApply,
                                  TaurusBaseWritableWidget.setForcedApply,
                                  TaurusBaseWritableWidget.resetForcedApply)

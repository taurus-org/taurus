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

__all__ = ["TaurusWheelEdit"]

__docformat__ = 'restructuredtext'

import taurus
from taurus.external.qt import Qt

from taurus.core.taurusbasetypes import TaurusEventType
from taurus.qt.qtgui.base import TaurusBaseWritableWidget
from qwheel import QWheelEdit


class TaurusWheelEdit(QWheelEdit, TaurusBaseWritableWidget):

    def __init__(self, qt_parent=None, designMode=False):
        name = self.__class__.__name__
        self.call__init__wo_kw(QWheelEdit, qt_parent)
        self.call__init__(TaurusBaseWritableWidget,
                          name, designMode=designMode)
        self.numberChanged.connect(self.notifyValueChanged)
        self.returnPressed.connect(self.writeValue)
        self.valueChangedSignal.connect(self.updatePendingOperations)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_type == TaurusEventType.Config and evt_value is not None:
            import re
            # match the format string to "%[width][.precision][f_type]"
            obj = self.getModelObj()
            m = re.match(r'%([0-9]+)?(\.([0-9]+))?([df])', obj.format)
            if m is None:
                raise ValueError("'%s' format unsupported" % obj.format)

            width, _, precision, f_type = m.groups()

            if width is None:
                width = self.DefaultIntDigitCount + \
                    self.DefaultDecDigitCount + 1
            else:
                width = int(width)

            if precision is None:
                precision = self.DefaultDecDigitCount
            else:
                precision = int(precision)

            dec_nb = precision

            if dec_nb == 0 or f_type == 'd':
                int_nb = width
            else:
                int_nb = width - dec_nb - 1  # account for decimal sep

            self.setDigitCount(int_nb=int_nb, dec_nb=dec_nb)
            try:
                self.setMinValue(float(obj.min_value))
            except:
                pass
            try:
                self.setMaxValue(float(obj.max_value))
            except:
                pass
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

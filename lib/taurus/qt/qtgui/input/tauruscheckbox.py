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

"""This module provides a set of basic taurus widgets based on QCheckBox"""

__all__ = ["TaurusValueCheckBox"]

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseWritableWidget


class TaurusValueCheckBox(Qt.QCheckBox, TaurusBaseWritableWidget):
    """A QCheckBox connected to a boolean writable attribute model"""

    def __init__(self, qt_parent=None, designMode=False):
        name = "TaurusValueCheckBox"
        self.call__init__wo_kw(Qt.QCheckBox, qt_parent)
        self.call__init__(TaurusBaseWritableWidget,
                          name, designMode=designMode)

        self.setObjectName(name)
        self.updateStyle()
        self.stateChanged.connect(self.notifyValueChanged)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Qt.Key_Return, Qt.Qt.Key_Enter):
            self.writeValue()
            event.accept()
        else:
            Qt.QCheckBox.keyPressEvent(self, event)
            event.ignore()

    def minimumSizeHint(self):
        return Qt.QSize(20, 20)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWritableWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def updateStyle(self):
        TaurusBaseWritableWidget.updateStyle(self)
        # Show text only if it is not specifically hidden
        if self._showText:
            try:
                self.setText(str(self.getModelObj().getConfig().getLabel()))
            except:
                self.setText('----')
        else:
            self.setText('')
        # Update pending operations style
        if self.hasPendingOperations():
            txt = str(self.text()).strip()
            if len(txt) == 0:
                self.setText("!")
            self.setStyleSheet('TaurusValueCheckBox {color: blue;}')
        else:
            if str(self.text()) == "!":
                self.setText(" ")
            self.setStyleSheet('TaurusValueCheckBox {}')
        self.update()

    def setValue(self, v):
        self.setChecked(bool(v))

    def getValue(self):
        return self.isChecked()

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWritableWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.input'
        ret['icon'] = "designer:checkbox.png"
        return ret

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = Qt.pyqtProperty("QString", TaurusBaseWritableWidget.getModel,
                            TaurusBaseWritableWidget.setModel,
                            TaurusBaseWritableWidget.resetModel)

    showText = Qt.pyqtProperty("bool", TaurusBaseWritableWidget.getShowText,
                               TaurusBaseWritableWidget.setShowText,
                               TaurusBaseWritableWidget.resetShowText)

    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWritableWidget.getUseParentModel,
                                     TaurusBaseWritableWidget.setUseParentModel,
                                     TaurusBaseWritableWidget.resetUseParentModel)

    autoApply = Qt.pyqtProperty("bool", TaurusBaseWritableWidget.getAutoApply,
                                TaurusBaseWritableWidget.setAutoApply,
                                TaurusBaseWritableWidget.resetAutoApply)

    forcedApply = Qt.pyqtProperty("bool", TaurusBaseWritableWidget.getForcedApply,
                                  TaurusBaseWritableWidget.setForcedApply,
                                  TaurusBaseWritableWidget.resetForcedApply)

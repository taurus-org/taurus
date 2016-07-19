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

"""This module provides a set of basic taurus widgets based on QLineEdit"""

__all__ = ["TaurusConfigurationPanel", "TangoConfigLineEdit",
           "TaurusConfigLineEdit"]

__docformat__ = 'restructuredtext'

import sys

from taurus.external.qt import Qt
from taurus.qt.qtgui.util import getWidgetsOfType
from taurus.qt.qtgui.util.ui import UILoadable
from taurus.qt.qtgui.base import TaurusBaseWritableWidget
from taurus.core.taurusattribute import TaurusAttribute
from taurus.core.taurusoperation import WriteAttrOperation
from taurus.core.util.log import taurus4_deprecation


class TangoConfigLineEdit(Qt.QLineEdit, TaurusBaseWritableWidget):

    def __init__(self, qt_parent=None, designMode=False):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QLineEdit, qt_parent)
        self.call__init__(TaurusBaseWritableWidget,
                          name, designMode=designMode)

        self.textChanged.connect(self.notifyValueChanged)
        self.returnPressed.connect(self.writeValue)
        self.editingFinished.connect(self._onEditingFinished)

    def _onEditingFinished(self):
        if self._autoApply:
            self.writeValue()

    def handleEvent(self, evt_src, evt_type, evt_value):
        self.notifyValueChanged()

    def getModelClass(self):
        return TaurusAttribute

    def postAttach(self):
        if self.isAttached():
            try:
                v = self._getAttrInfoExMember(self.modelFragmentName)
            except:
                v = None
            self.setValue(v)

    def updatePendingOperations(self):
        model = self.getModelObj()
        try:
            model_value = self.text()
            wigdet_value = self.getValue()
            if model.areStrValuesEqual(model_value, wigdet_value):
                self._operations = []
            else:
                operation = WriteAttrOperation(model, wigdet_value,
                                               self.getOperationCallbacks())
                self._operations = [operation]
        except:
            self._operations = []
        self.updateStyle()

    def setValue(self, v):
        model = self.getModelObj()
        if model is None:
            v_str = str(v)
        else:
            v_str = str(self.getValue())
        self.blockSignals(True)
        self.setText(v_str.strip())
        self.blockSignals(False)

    def _getAttrInfoExMember(self, member):
        model_obj = self.getModelObj()
        attrInfoEx = model_obj.getAttributeInfoEx()
        if '_alarm' in member or '_warning' in member:
            alarms = getattr(attrInfoEx, 'alarms')
            return getattr(alarms, member)
        else:
            return getattr(attrInfoEx, member)

    def _setAttrInfoExMember(self, member, value):
        model_obj = self.getModelObj()
        attrInfoEx = model_obj.getAttributeInfoEx()
        if '_alarm' in member or '_warning' in member:
            alarms = getattr(attrInfoEx, 'alarms')
            setattr(alarms, member, value)
        else:
            setattr(attrInfoEx, member, value)
        model_obj.setConfigEx(attrInfoEx)

    def getValue(self):
        if self.modelFragmentName is None:
            return None
        return self._getAttrInfoExMember(self.modelFragmentName)

    def notifyValueChanged(self):
        if str(self.text()) != str(self.getValue()):
            style = 'TangoConfigLineEdit {color: %s; font-weight: %s}' %\
                    ('blue', 'bold')
            self.setStyleSheet(style)
        else:
            style = 'TangoConfigLineEdit {color: %s; font-weight: %s}' %\
                    ('black', 'normal')
            self.setStyleSheet(style)

    def writeValue(self):
        if self.modelFragmentName is not None:
            self._setAttrInfoExMember(self.modelFragmentName, str(self.text()))
        style = 'TangoConfigLineEdit {color: %s; font-weight: %s}' %\
                ('black', 'normal')
        self.setStyleSheet(style)

    def setModel(self, model):
        TaurusBaseWritableWidget.setModel(self, model)
        self.notifyValueChanged()

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWritableWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.input'
        ret['icon'] = "designer:lineedit.png"
        return ret

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = Qt.pyqtProperty("QString", TaurusBaseWritableWidget.getModel,
                            TaurusBaseWritableWidget.setModel,
                            TaurusBaseWritableWidget.resetModel)

    autoApply = Qt.pyqtProperty("bool", TaurusBaseWritableWidget.getAutoApply,
                                TaurusBaseWritableWidget.setAutoApply,
                                TaurusBaseWritableWidget.resetAutoApply)

    forcedApply = Qt.pyqtProperty("bool", TaurusBaseWritableWidget.getForcedApply,
                                  TaurusBaseWritableWidget.setForcedApply,
                                  TaurusBaseWritableWidget.resetForcedApply)


class TaurusConfigLineEdit(TangoConfigLineEdit):

    @taurus4_deprecation(alt='TangoConfigLineEdit')
    def __init__(self, qt_parent=None, designMode=False):
        TangoConfigLineEdit.__init__(self, qt_parent=None, designMode=False)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None


@UILoadable(with_ui='_ui')
class TaurusConfigurationPanel(Qt.QWidget):

    def __init__(self, parent=None, designMode=False):
        Qt.QWidget.__init__(self, parent)
        self.loadUi()

        self._ui.pushButtonOk.clicked.connect(self._onOk)
        self._ui.pushButtonApply.clicked.connect(self._onApply)
        self._ui.pushButtonCancel.clicked.connect(self._onCancel)
        self._ui.pushButtonRestore.clicked.connect(self._onRestore)

    def _onOk(self):
        self._onApply()
        self._onCancel()

    def _onApply(self):
        widgets = getWidgetsOfType(self, TangoConfigLineEdit)
        for w in widgets:
            param = str(w.text())
            if w.getValue() != param:
                w.writeValue()

    def _onCancel(self):
        self.close()

    def _onRestore(self):
        widgets = getWidgetsOfType(self, TangoConfigLineEdit)
        for w in widgets:
            param = str(w.text())
            if w.getValue() != param:
                w.setText(param)

    def setModel(self, model):
        self._ui.fullNameLineEdit.setText(model)
        model += '#'
        self._ui.labelConfig.setModel(model + 'label')
        self._ui.unitConfig.setModel(model + 'unit')
        self._ui.displayUnitConfig.setModel(model + 'display_unit')
        self._ui.standardUnitConfig.setModel(model + 'standard_unit')
        self._ui.formatConfig.setModel(model + 'format')
        self._ui.descriptionConfig.setModel(model + 'description')
        self._ui.valueMinConfig.setModel(model + 'min_value')
        self._ui.valueMaxConfig.setModel(model + 'max_value')
        self._ui.alarmMinConfig.setModel(model + 'min_alarm')
        self._ui.alarmMaxConfig.setModel(model + 'max_alarm')
        self._ui.warningMinConfig.setModel(model + 'min_warning')
        self._ui.warningMaxConfig.setModel(model + 'max_warning')


def main():
    import sys
    attr_name = sys.argv[1]
    a = Qt.QApplication([])
    w1 = TaurusConfigurationPanel()
    w1._ui.pushButtonOk.setVisible(True)
    w1._ui.pushButtonCancel.setVisible(True)
    w1.setModel(attr_name)
    w1.show()
    return a.exec_()

if __name__ == "__main__":
    sys.exit(main())

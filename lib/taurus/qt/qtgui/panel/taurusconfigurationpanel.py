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

"""This module provides a set of basic taurus widgets based on QLineEdit"""

__all__ = ["TaurusConfigurationPanel"]

__docformat__ = 'restructuredtext'

import sys, traceback
import ui.ui_TaurusConfigurationPanel
from taurus.qt import Qt
from taurus.qt.qtgui.input import TaurusConfigLineEdit
from taurus.qt.qtgui.util import getWidgetsOfType

class TaurusConfigurationPanel(Qt.QWidget):
    def __init__(self, parent=None, designMode=False):
        Qt.QWidget.__init__(self, parent)
        self._ui = ui.ui_TaurusConfigurationPanel.Ui_TaurusConfigurationPanel()
        self._ui.setupUi(self)

        Qt.QObject.connect(self._ui.pushButtonOk, Qt.SIGNAL("clicked()"), self._onOk)
        Qt.QObject.connect(self._ui.pushButtonApply, Qt.SIGNAL("clicked()"), self._onApply)
        Qt.QObject.connect(self._ui.pushButtonCancel, Qt.SIGNAL("clicked()"), self._onCancel)
        Qt.QObject.connect(self._ui.pushButtonRestore, Qt.SIGNAL("clicked()"), self._onRestore)

    def _onOk(self):
	    self._onApply()
	    self._onCancel()

    def _onApply(self):
	    widgets=getWidgetsOfType(self, TaurusConfigLineEdit)
            for w in widgets:
                model = w.getModelObj()
                if w.getValue() != str(model.getParam(w._configParam)):
	            w.writeValue()

    def _onCancel(self):
       self._ui._Form.close()

    def _onRestore(self):
	    widgets=getWidgetsOfType(self, TaurusConfigLineEdit)
            for w in widgets:
                model = w.getModelObj()
                if w.getValue() != str(model.getParam(w._configParam)):
		    w.setText(str(model.getParam(w._configParam)))

    def setModel(self, model):
    	self._ui.fullNameLineEdit.setText(model)
    	model+='?configuration='
        self._ui.labelConfig.setModel(model+'label')
        self._ui.unitConfig.setModel(model+'unit')
        self._ui.displayUnitConfig.setModel(model+'display_unit')
        self._ui.standardUnitConfig.setModel(model+'standard_unit')
        self._ui.formatConfig.setModel(model+'format')
        self._ui.descriptionConfig.setModel(model+'description')
        self._ui.valueMinConfig.setModel(model+'min_value')
        self._ui.valueMaxConfig.setModel(model+'max_value')
        self._ui.alarmMinConfig.setModel(model+'min_alarm')
        self._ui.alarmMaxConfig.setModel(model+'max_alarm')
        self._ui.warningMinConfig.setModel(model+'min_warning')
        self._ui.warningMaxConfig.setModel(model+'max_warning')

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
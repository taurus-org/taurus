#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""
parameditors.py: 
"""

import os

from taurus.external.qt import Qt
from taurus.qt.qtgui.input import TaurusAttrListComboBox

from sardana.taurus.qt.qtgui.extra_macroexecutor import globals
from sardana.taurus.qt.qtgui.extra_macroexecutor.common import MSAttrListComboBox

#@todo: replace by method from common module
def str2bool(text):
    return text in ("True", "1")

class ParamBase:

    def __init__(self, paramModel=None):
        self.setParamModel(paramModel)

    def paramModel(self):
        return self._paramModel

    def setParamModel(self, paramModel):
        self._paramModel = paramModel

    def resetValue(self):
        if self.paramModel() is not None:
            defValue = self.paramModel().defValue()
            self.setValue(defValue)

    def index(self):
        return self._index

    def setIndex(self, index):
        self._index = index
        paramModel = index.model().nodeFromIndex(index)
        self.setParamModel(paramModel)
        self.connect(self, Qt.SIGNAL("modelChanged()"), self.onModelChanged)
        self.setValue(paramModel.value())

    def onModelChanged(self):
        model = self.index().model()
        model.setData(self.index(), Qt.QVariant(self.getValue()))

class ComboBoxBoolean(ParamBase, Qt.QComboBox):
    def __init__(self, parent=None, paramModel=None):
        ParamBase.__init__(self, paramModel)
        Qt.QComboBox.__init__(self, parent)

        self.addItems(['True', 'False'])
        self.connect(self, Qt.SIGNAL("currentIndexChanged(int)"), self.onCurrentIndexChanged)

    def getValue(self):
        return str(self.currentText())

    def setValue(self, value):
        currentIdx = self.currentIndex()
        idx = self.findText(value)
        if currentIdx == idx:
            self.emit(Qt.SIGNAL("currentIndexChanged(int)"), self.currentIndex())
        else:
            self.setCurrentIndex(idx)

    def onCurrentIndexChanged(self):
        self.emit(Qt.SIGNAL("modelChanged()"))

class ComboBoxParam(ParamBase, Qt.QComboBox):

    def __init__(self, parent=None, paramModel=None):
        ParamBase.__init__(self, paramModel)
        Qt.QComboBox.__init__(self, parent)
        self.connect(self, Qt.SIGNAL("currentIndexChanged(int)"), self.onCurrentIndexChanged)

    def getValue(self):
        return str(self.currentText())

    def setValue(self, value):
        currentIdx = self.currentIndex()
        idx = self.findText(value)
        if currentIdx == idx:
            self.emit(Qt.SIGNAL("currentIndexChanged(int)"), self.currentIndex())
        else:
            self.setCurrentIndex(idx)

    def onCurrentIndexChanged(self):
        self.emit(Qt.SIGNAL("modelChanged()"))

class MSAttrListComboBoxParam(ParamBase, MSAttrListComboBox):

    def __init__(self, parent=None, paramModel=None):
        ParamBase.__init__(self, paramModel)
        MSAttrListComboBox.__init__(self, parent)
#        self.setUseParentModel(True)
#        self.setModel("/" + self.paramModel().type() + "List")
        self.connect(self, Qt.SIGNAL("currentIndexChanged(int)"), self.onCurrentIndexChanged)

    def getValue(self):
        return str(self.currentText())

    def setValue(self, value):
        self.setCurrentText(value)

    def onCurrentIndexChanged(self):
        self.emit(Qt.SIGNAL("modelChanged()"))


class AttrListComboBoxParam(ParamBase, TaurusAttrListComboBox):

    def __init__(self, parent=None, paramModel=None):
        ParamBase.__init__(self, paramModel)
        TaurusAttrListComboBox.__init__(self, parent)
        self.setModel("/" + self.paramModel().type() + "List")
#        self.setToolTip(self.paramModel().description())


    def handleEvent(self, src, type, value):
        self.clear()
        if src and value:
            lines = list(value.value)
            items = []
            if self.paramModel().type() == globals.PARAM_CONTROLLER_CLASS:
                for line in lines:
                    items.append(line.split()[4])
            else:
                for line in lines:
                    items.append(line.split()[0])
            items.sort()
            self.addItems(items)
    #        self.updateStyle()

    def getValue(self):
        return str(self.currentText())

#    def resetValue(self):
#        self.setCurrentIndex(0)


class LineEditParam(ParamBase, Qt.QLineEdit):
    def __init__(self, parent=None, paramModel=None):
        ParamBase.__init__(self, paramModel)
        Qt.QLineEdit.__init__(self, parent)
        self.connect(self, Qt.SIGNAL("textChanged(const QString&)"), self.onTextChanged)
#        self.setToolTip(self.paramModel().description())

    def onTextChanged(self):
        self.emit(Qt.SIGNAL("modelChanged()"))

#    def setDefaultValue(self):
#        defVal = self.paramModel().defValue()
#        if not (defVal == "None" or defVal == ""):
#            self.setText(defVal)

    def setValue(self, value):
        self.setText(value)

    def getValue(self):
        return str(self.text())

#    def resetValue(self):
#        self.setText("")
#        self.setDefaultValue()

class CheckBoxParam(ParamBase, Qt.QCheckBox):

    def __init__(self, parent=None, paramModel=None):
        ParamBase.__init__(self, paramModel)
        Qt.QCheckBox.__init__(self, parent)
        self.connect(self, Qt.SIGNAL("stateChanged(int)"), self.onStateChanged)

    def getValue(self):
        return str(self.isChecked())

    def setValue(self, value):
        self.setChecked(str2bool(value))

    def onStateChanged(self):
        self.emit(Qt.SIGNAL("modelChanged()"))


class SpinBoxParam(ParamBase, Qt.QSpinBox):
    def __init__(self, parent=None, paramModel=None):
        ParamBase.__init__(self, paramModel)
        Qt.QSpinBox.__init__(self, parent)
        self.setRange(-999999999, 999999999)
        self.setAccelerated(True)
#        self.setToolTip(self.paramModel().description())

    def getValue(self):
        return str(self.value())

    def setValue(self, value):
        Qt.QSpinBox.setValue(self, int(value))

#    def resetValue(self):
#        self.setValue(0)
#        self.setDefaultValue()

class DoubleSpinBoxParam(ParamBase, Qt.QDoubleSpinBox):
    def __init__(self, parent=None, paramModel=None):
        ParamBase.__init__(self, paramModel)
        Qt.QDoubleSpinBox.__init__(self, parent)
        self.setRange(-999999999.999999, 999999999.999999)
        self.setAccelerated(True)
        self.setDecimals(6)
        self.setSingleStep(0.000001)
#        self.setToolTip(self.paramModel().description())

    def getValue(self):
        return str(self.value())

    def setValue(self, value):
        Qt.QDoubleSpinBox.setValue(self, float(value))

#    def setDefaultValue(self):
#        defVal = self.paramModel().defValue()
#        if not (defVal == "None" or defVal == ""):
#            defVal = defVal.lower()
#            try:
#                val = float(defVal)
#                self.setValue(val)
#            except Error, e:
#                pass
#
#    def resetValue(self):
#        self.setValue(0.0)
#        self.setDefaultValue()

class FileDialogParam(ParamBase, Qt.QWidget):
    def __init__(self, parent=None, paramModel=None):
        ParamBase.__init__(self, paramModel)
        Qt.QWidget.__init__(self, parent)
        self.setToolTip(self.paramModel().description())
        self.layout = Qt.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.filePath = Qt.QLineEdit(self)
        self.layout.addWidget(self.filePath)
        self.button = Qt.QPushButton(self)
        self.button.setText("...")
        self.layout.addWidget(self.button)

        self.text = ""

        Qt.QObject.connect(self.button, Qt.SIGNAL("clicked()"), self._chooseAFile)

    def _chooseAFile(self):
        path = Qt.QFileDialog().getOpenFileName()
        self.filePath.setText(path)

    def _readFileContent(self, path):
        content = ""
        if not os.access(path, os.R_OK):
            return (False, content)
        file = open(path, "r")
        line = "nonempty"
        while(line != ""):
            line = file.readline()
            content = content + line
        file.close()
        return (True, content)

    def getValue(self):
        state, self.text = self._readFileContent(self.filePath.text())
        if state is False:
            self.filePath.setText("Error: couldn't read a file")
        return str(self.text)

    def setValue(self, value):
        self.filePath.setText(value)

class DirPathParam(ParamBase, Qt.QWidget):

    def __init__(self, parent=None, paramModel=None):
        ParamBase.__init__(self, paramModel)
        Qt.QWidget.__init__(self, parent)

        self.layout = Qt.QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.dirPath = Qt.QLineEdit(self)
        self.layout.addWidget(self.dirPath)
        self.button = Qt.QPushButton(self)
        self.button.setText("...")
        self.layout.addWidget(self.button)

        self.connect(self.button, Qt.SIGNAL("clicked()"), self.__chooseDirPath)
        self.connect(self.dirPath, Qt.SIGNAL("textChanged(const QString&)"), self.onDirPathChanged)

    def onDirPathChanged(self):
        self.emit(Qt.SIGNAL("modelChanged()"))

    def __chooseDirPath(self):
        path = Qt.QFileDialog().getExistingDirectory()
        self.setValue(path)

    def getValue(self):
        return str(self.dirPath.text())

    def setValue(self, value):
        self.dirPath.setText(value)



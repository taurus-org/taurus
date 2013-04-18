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

__all__ = ["TaurusValueLineEdit", "TaurusConfigLineEdit"]

__docformat__ = 'restructuredtext'

import sys, PyTango, taurus.core
from taurus.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseWidget, TaurusBaseWritableWidget

_String = str
try:
    _String = Qt.QString
except AttributeError:
    _String = str

class TaurusValueLineEdit(Qt.QLineEdit, TaurusBaseWritableWidget):

    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, qt_parent = None, designMode = False):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QLineEdit, qt_parent)
        self.call__init__(TaurusBaseWritableWidget, name, designMode=designMode)
        self._enableWheelEvent = False
        self.__minAlarm = -float("inf")
        self.__maxAlarm = float("inf")
        self.__minLimit = -float("inf")
        self.__maxLimit = float("inf")

        self.setAlignment(Qt.Qt.AlignRight)
        self.setValidator(None)

        self.connect(self, Qt.SIGNAL('textChanged(const QString &)'), self.valueChanged)
        self.connect(self, Qt.SIGNAL('returnPressed()'), self.writeValue)
        self.connect(self, Qt.SIGNAL('valueChanged'), self.updatePendingOperations)
        self.connect(self, Qt.SIGNAL('editingFinished()'), self._onEditingFinished)

    def _updateValidator(self, attrinfo):
        '''This method sets a validator depending on the data type
        attrinfo is an AttributeInfoEx object'''
        if PyTango.is_int_type(attrinfo.data_type):
            validator = Qt.QIntValidator(self) #initial range is -2147483648 to 2147483647 (and cannot be set larger)
            if validator.bottom() < self.__minLimit < validator.top():
                validator.setBottom(int(self.__minLimit))
            if validator.bottom() < self.__maxLimit < validator.top():
                validator.setTop(int(self.__maxLimit))
            self.setValidator(validator)
            self.debug("IntValidator set with limits=[%d,%d]"%(validator.bottom(), validator.top()))
        elif PyTango.is_float_type(attrinfo.data_type):
            validator= Qt.QDoubleValidator(self)
            validator.setBottom(self.__minLimit)
            validator.setTop(self.__maxLimit)
            #I removed the validation of decimal digits because it was not practical when editing values
#            decimalDigits = self.__decimalDigits(attrinfo.format) 
#            if decimalDigits is not None:
#                validator.setDecimals(decimalDigits)
            self.setValidator(validator)
            self.debug("DoubleValidator set with limits=[%f,%f]"%(self.__minLimit, self.__maxLimit))
        else: #@TODO Other validators can be configured for other types (e.g. with string lengths, tango names,...)
            self.setValidator(None)
            self.debug("Validator disabled")

    def __decimalDigits(self, fmt):
        '''returns the number of decimal digits from a format string
        (or None if they are not defined)''' 
        try:
            if fmt[-1].lower() in ['f','g'] and '.' in fmt:
                return int(fmt[:-1].split('.')[-1])
            else:
                return None
        except:
            return None

    def _onEditingFinished(self):
        '''slot for performing autoapply only when edition is finished'''
        if self._autoApply:
            self.writeValue()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWritableWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def valueChanged(self, *args):
        '''reimplement to avoid autoapply on every partial edition'''
        self.emitValueChanged()

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_type == taurus.core.taurusbasetypes.TaurusEventType.Config:
            if evt_value.min_alarm != taurus.core.taurusconfiguration.TaurusConfiguration.no_min_alarm:
                self.__minAlarm = float(evt_value.min_alarm)
            else:
                self.__minAlarm = -float("inf")
            if evt_value.max_alarm != taurus.core.taurusconfiguration.TaurusConfiguration.no_max_alarm:
                self.__maxAlarm = float(evt_value.max_alarm)
            else:
                self.__maxAlarm = float("inf")
            if evt_value.min_value != taurus.core.taurusconfiguration.TaurusConfiguration.no_min_value:
                self.__minLimit = float(evt_value.min_value)
            else:
                self.__minLimit = -float("inf")
            if evt_value.max_value != taurus.core.taurusconfiguration.TaurusConfiguration.no_max_value:
                self.__maxLimit = float(evt_value.max_value)
            else:
                self.__maxLimit = float("inf")

            self._updateValidator(evt_value)
        TaurusBaseWritableWidget.handleEvent(self, evt_src, evt_type, evt_value)

    def _inAlarm(self, v):
        try: return not(self.__minAlarm < float(v) < self.__maxAlarm)
        except: return False #this will return false for non-numerical values

    def _outOfRange(self, v):
        validator = self.validator()
        if validator:
            return validator.validate(_String(str(v)), 0)[0] != validator.Acceptable
        else: #fallback, only for numeric typess (returns False for other types)
            try: return not(self.__minLimit <= float(v) <=  self.__maxLimit)
            except: return False

    def updateStyle(self):
        TaurusBaseWritableWidget.updateStyle(self)
        color, weight = 'black', 'normal' #default case: the value is in normal range with no pending changes
        v = self.getValue()
        if self._outOfRange(v): #the value is invalid and can't be applied
            color = 'gray'
        elif self._inAlarm(v): #the value is valid but in alarm range...
            color = 'orange'
            if self.hasPendingOperations(): #...and some change is pending
                weight = 'bold'
        elif self.hasPendingOperations(): #the value is in valid range with pending changes
            color, weight= 'blue','bold'
        self.setStyleSheet('TaurusValueLineEdit {color: %s; font-weight: %s}'%(color,weight))

    def wheelEvent(self, evt):
        if not self.getEnableWheelEvent() or Qt.QLineEdit.isReadOnly(self):
            return Qt.QLineEdit.wheelEvent(self, evt)
        model = self.getModelObj()
        if model is None or not model.isNumeric():
            return Qt.QLineEdit.wheelEvent(self, evt)

        evt.accept()
        numDegrees = evt.delta() / 8
        numSteps = numDegrees / 15
        modifiers = evt.modifiers()
        if modifiers & Qt.Qt.ControlModifier:
            numSteps *= 10
        elif (modifiers & Qt.Qt.AltModifier) and model.isFloat():
            numSteps *= .1
        self._stepBy(numSteps)

    def keyPressEvent(self, evt):
        if evt.key() in (Qt.Qt.Key_Return, Qt.Qt.Key_Enter):
            Qt.QLineEdit.keyPressEvent(self, evt)
            evt.accept()
            return
        if Qt.QLineEdit.isReadOnly(self):
            return Qt.QLineEdit.keyPressEvent(self, evt)
        model = self.getModelObj()
        if model is None or not model.isNumeric():
            return Qt.QLineEdit.keyPressEvent(self, evt)

        if evt.key() == Qt.Qt.Key_Up:     numSteps = 1
        elif evt.key() == Qt.Qt.Key_Down: numSteps = -1
        else: return Qt.QLineEdit.keyPressEvent(self, evt)

        evt.accept()
        modifiers = evt.modifiers()
        if modifiers & Qt.Qt.ControlModifier:
            numSteps *= 10
        elif (modifiers & Qt.Qt.AltModifier) and model.isFloat():
            numSteps *= .1
        self._stepBy(numSteps)

    def _stepBy(self, v):
        self.setValue(self.getValue() + v)

    def setValue(self, v):
        model = self.getModelObj()
        if model is None:
            v_str = str(v)
        else:
            v_str = str(model.displayValue(v))
        v_str = v_str.strip()
        self.setText(v_str)

    def getValue(self):
        v_qstr = self.text()
        model = self.getModelObj()
        try:
            return model.encode(v_qstr)
        except:
            return None

    def setEnableWheelEvent(self, b):
        self._enableWheelEvent = b

    def getEnableWheelEvent(self):
        return self._enableWheelEvent

    def resetEnableWheelEvent(self):
        self.setEnableWheelEvent(False)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWritableWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.input'
        ret['icon'] = ":/designer/lineedit.png"
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

    enableWheelEvent = Qt.pyqtProperty("bool", getEnableWheelEvent,
                                       setEnableWheelEvent,
                                       resetEnableWheelEvent)



class TaurusConfigLineEdit(Qt.QLineEdit, TaurusBaseWritableWidget):
    def __init__(self, qt_parent = None, designMode = False):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QLineEdit, qt_parent)
        self.call__init__(TaurusBaseWritableWidget, name, designMode=designMode)

        self.connect(self, Qt.SIGNAL('textChanged(const QString &)'), self.valueChanged)
        self.connect(self, Qt.SIGNAL('returnPressed()'), self.writeValue)
        self.connect(self, Qt.SIGNAL('editingFinished()'), self._onEditingFinished)

    def _onEditingFinished(self):
        if self._autoApply: self.writeValue()

    def handleEvent(self, evt_src, evt_type, evt_value):
        self.valueChanged()

    def getModelClass(self):
        return taurus.core.taurusconfiguration.TaurusConfiguration

    def setValue(self, v):
        model = self.getModelObj()
        cfg = self._configParam
        if model is None or not cfg:
            v_str = str(v)
        else:
            v_str = str(model.getParam(cfg))
        self.blockSignals(True)
        self.setText(v_str.strip())
        self.blockSignals(False)

    def getValue(self):
        v_qstr = self.text()
        model = self.getModelObj()
        try:
            return model.encode(v_qstr)
        except:
            return None

    def setModel(self, model):
        model = str(model)
        try:
            self._configParam = model[model.rfind('=')+1:].lower()
        except:
            self._configParam = ''
        TaurusBaseWritableWidget.setModel(self,model)

    def valueChanged(self):
        model = self.getModelObj()
        if self.getValue() != str(model.getParam(self._configParam)):
            self.setStyleSheet('TaurusConfigLineEdit {color: %s; font-weight: %s}'%('blue','bold'))
        else:
            self.setStyleSheet('TaurusConfigLineEdit {color: %s; font-weight: %s}'%('black','normal'))

    def writeValue(self):
        model = self.getModelObj()
        model.setParam(str(self._configParam), str(self.text()))
        self.setStyleSheet('TaurusConfigLineEdit {color: %s; font-weight: %s}'%('black','normal'))

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWritableWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.input'
        ret['icon'] = ":/designer/lineedit.png"
        return ret

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = Qt.pyqtProperty("QString", TaurusBaseWritableWidget.getModel,
                            setModel, TaurusBaseWritableWidget.resetModel)

    autoApply = Qt.pyqtProperty("bool", TaurusBaseWritableWidget.getAutoApply,
                                TaurusBaseWritableWidget.setAutoApply,
                                TaurusBaseWritableWidget.resetAutoApply)

    forcedApply = Qt.pyqtProperty("bool", TaurusBaseWritableWidget.getForcedApply,
                                  TaurusBaseWritableWidget.setForcedApply,
                                  TaurusBaseWritableWidget.resetForcedApply)

def main():
    import sys
    attr_name = sys.argv[1]
    a = Qt.QApplication([])
    panel = Qt.QWidget()
    l = Qt.QGridLayout()
    w1 = TaurusConfigLineEdit()
    #w1 = TaurusValueLineEdit()
    w1.setModel(attr_name)
    l.addWidget(w1,0,0)
    panel.setLayout(l)
    panel.setVisible(True)
    return a.exec_()

if __name__ == "__main__":
    sys.exit(main())

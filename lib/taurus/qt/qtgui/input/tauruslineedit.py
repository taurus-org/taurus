#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus
## 
## http://taurus-scada.org
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

import sys
import numpy
from taurus.external.qt import Qt
from taurus.external.pint import Quantity
from taurus.qt.qtgui.base import TaurusBaseWritableWidget
from taurus.qt.qtgui.util import PintValidator
from taurus.core import DataType, DataFormat, TaurusEventType
from taurus.core.taurusattribute import TaurusAttribute


class TaurusValueLineEdit(Qt.QLineEdit, TaurusBaseWritableWidget):

    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, qt_parent = None, designMode = False):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QLineEdit, qt_parent)
        self.call__init__(TaurusBaseWritableWidget, name, designMode=designMode)
        self._enableWheelEvent = False
        self.__minAlarm = None
        self.__maxAlarm = None
        self.__minLimit = None
        self.__maxLimit = None
        self.__unit = ''

        self.setAlignment(Qt.Qt.AlignRight)
        self.setValidator(None)

        self.connect(self, Qt.SIGNAL('textChanged(const QString &)'), self.valueChanged)
        self.connect(self, Qt.SIGNAL('returnPressed()'), self.writeValue)
        self.connect(self, Qt.SIGNAL('valueChanged'), self.updatePendingOperations)
        self.connect(self, Qt.SIGNAL('editingFinished()'), self._onEditingFinished)

    def _updateValidator(self, value):
        '''This method sets a validator depending on the data type'''
        if isinstance(value.wvalue, Quantity):
            self.__unit = value.wvalue.units
            validator = PintValidator(self)
            validator.setBottom(self.__minLimit)
            validator.setTop(self.__maxLimit)
            validator.setUnit(self.__unit)
            self.setValidator(validator)
            self.debug("PintValidator set with limits=[%f, %f]",
                       self.__minLimit, self.__maxLimit)
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
        if evt_type == TaurusEventType.Config:
            attr = self.getModelObj()
            self.__minAlarm, self.__maxAlarm = attr.alarms
            self.__minLimit, self.__maxLimit = attr.range
            self._updateValidator(evt_value)
        TaurusBaseWritableWidget.handleEvent(self, evt_src, evt_type, evt_value)

    def __getQuantity(self, v):
        validator = self.validator()
        if validator.validate(str(v), 0)[0] != validator.Acceptable:
            return None
        try:
            q = Quantity(v)
        except:
            return None
        if q.dimensionless:
            q = Quantity(q.magnitude, self.__unit)
        return q

    def _inAlarm(self, v):
        try:
            return v <= self.__minAlarm or v >= self.__maxAlarm
        except:
            return True

    def _outOfRange(self, v):
        try:
            return self.__minLimit > v or self.__maxLimit < v
        except:
            return True

    def updateStyle(self):
        TaurusBaseWritableWidget.updateStyle(self)
        #default case: the value is in normal range with no pending changes
        color, weight = 'black', 'normal'
        v = self.getValue()
        modelObj = self.getModelObj()
        if modelObj is None or v is None:
            color = 'gray'
        elif modelObj.type in [DataType.Integer, DataType.Float]:
            _q = self.__getQuantity(self.text())
            if self._outOfRange(_q):
                #the value is invalid and can't be applied
                color = 'gray'
            elif self._inAlarm(_q):
                #the value is valid but in alarm range...
                color = 'orange'
                if self.hasPendingOperations():
                #...and some change is pending
                    weight = 'bold'
        elif self.hasPendingOperations():
            #the value is in valid range with pending changes
            color, weight= 'blue', 'bold'

        style = 'TaurusValueLineEdit {color: %s; font-weight: %s}' %\
                (color, weight)
        self.setStyleSheet(style)

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
        elif (modifiers & Qt.Qt.AltModifier) and model.type == DataType.Float:
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
        elif (modifiers & Qt.Qt.AltModifier) and model.type == DataType.Float:
            numSteps *= .1
        self._stepBy(numSteps)

    def _stepBy(self, v):
        value = self.getValue()
        self.setValue(value + Quantity(v, value.units))

    def setValue(self, v):
        model = self.getModelObj()
        if model is None:
            v_str = str(v)
        else:
            v_str = str(self.displayValue(v))
        v_str = v_str.strip()
        self.setText(v_str)

    def getValue(self):
        value = self.text()
        model_obj = self.getModelObj()
        if model_obj is None:
            return None
        try:
            model_type = model_obj.type
            model_format = model_obj.data_format
            if model_type in [DataType.Integer, DataType.Float]:
                value = self.__getQuantity(value)
            elif model_type == DataType.Boolean:
                if model_format == DataFormat._0D:
                    value = bool(int(eval(value)))
                else:
                    value = numpy.array(eval(value), dtype=int).astype(bool)
            elif model_type == DataType.String:
                if model_format == DataFormat._0D:
                    value = str(value)
                else:
                    value = numpy.array(eval(value), dtype=str).tolist()
            elif model_type == DataType.Bytes:
                value = bytes(value)
            else:
                self.debug('Unsupported model type "%s"', model_type)
                value = None
        except:
            value = None
        return value

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
        return TaurusAttribute

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
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication()

    form = Qt.QWidget()
    layout = Qt.QVBoxLayout()
    form.setLayout(layout)
    for m in ('sys/tg_test/1/double_scalar',
              'sys/tg_test/1/double_scalar'
              ):
        w = TaurusValueLineEdit()
        w.setModel(m)
        layout.addWidget(w)
    form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    sys.exit(main())

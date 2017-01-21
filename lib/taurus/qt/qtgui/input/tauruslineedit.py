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

__all__ = ["TaurusValueLineEdit"]

__docformat__ = 'restructuredtext'

import sys
import numpy
from taurus.external.qt import Qt
from taurus.external.pint import Quantity
from taurus.qt.qtgui.base import TaurusBaseWritableWidget
from taurus.qt.qtgui.util import PintValidator
from taurus.core import DataType, DataFormat, TaurusEventType


class TaurusValueLineEdit(Qt.QLineEdit, TaurusBaseWritableWidget):

    def __init__(self, qt_parent=None, designMode=False):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QLineEdit, qt_parent)
        self.call__init__(TaurusBaseWritableWidget,
                          name, designMode=designMode)
        self._enableWheelEvent = False

        self.setAlignment(Qt.Qt.AlignRight)
        self.setValidator(None)

        self.textChanged.connect(self.notifyValueChanged)
        self.returnPressed.connect(self.writeValue)
        self.valueChangedSignal.connect(self.updatePendingOperations)
        self.editingFinished.connect(self._onEditingFinished)

    def _updateValidator(self, value):
        '''This method sets a validator depending on the data type'''
        if isinstance(value.wvalue, Quantity):
            val = self.validator()
            if not isinstance(val, PintValidator):
                val = PintValidator(self)
                self.setValidator(val)
            attr = self.getModelObj()
            bottom, top = attr.range
            if bottom != val.bottom:
                val.setBottom(bottom)
            if top != val.top:
                val.setTop(top)
            units = value.wvalue.units
            if units != val.units:
                val.setUnits(units)

        # @TODO Other validators can be configured for other types (e.g. with string lengths, tango names,...)
        else:
            self.setValidator(None)
            self.debug("Validator disabled")

    def __decimalDigits(self, fmt):
        '''returns the number of decimal digits from a format string
        (or None if they are not defined)'''
        try:
            if fmt[-1].lower() in ['f', 'g'] and '.' in fmt:
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
    def notifyValueChanged(self, *args):
        '''reimplement to avoid autoapply on every partial edition'''
        self.emitValueChanged()

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_type in (TaurusEventType.Change, TaurusEventType.Periodic):
            self._updateValidator(evt_value)
        TaurusBaseWritableWidget.handleEvent(
            self, evt_src, evt_type, evt_value)

    def isTextValid(self):
        """
        Validates current text

        :return: (bool) Returns False if there is a validator and the current
                 text is not Acceptable. Returns True otherwise.
        """
        val = self.validator()
        if val is None:
            return True
        return val.validate(str(self.text()), 0)[0] == val.Acceptable

    def updateStyle(self):
        TaurusBaseWritableWidget.updateStyle(self)

        value = self.getValue()

        if value is None or not self.isTextValid():
            # invalid value
            color, weight = 'gray', 'normal'
        else:
            # check if there are pending operations
            if self.hasPendingOperations():
                color, weight = 'blue', 'bold'
            else:
                color, weight = 'black', 'normal'
            # also check alarms (if applicable)
            modelObj = self.getModelObj()
            if modelObj and modelObj.type in [DataType.Integer, DataType.Float]:
                min_, max_ = modelObj.alarms
                if value < min_ or value > max_:
                    color = 'orange'
        # apply style
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

        if evt.key() == Qt.Qt.Key_Up:
            numSteps = 1
        elif evt.key() == Qt.Qt.Key_Down:
            numSteps = -1
        else:
            return Qt.QLineEdit.keyPressEvent(self, evt)

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
        text = self.text()
        model_obj = self.getModelObj()
        if model_obj is None:
            return None
        val = self.validator()
        try:
            model_type = model_obj.type
            model_format = model_obj.data_format
            if model_type in [DataType.Integer, DataType.Float]:
                try:
                    q = Quantity(text)
                    # allow implicit units (assume wvalue.units implicitly)
                    if q.dimensionless:
                        q = Quantity(q.magnitude, val.units)
                    return q
                except:
                    return None
            elif model_type == DataType.Boolean:
                if model_format == DataFormat._0D:
                    return bool(int(eval(text)))
                else:
                    return numpy.array(eval(text), dtype=int).astype(bool)
            elif model_type == DataType.String:
                if model_format == DataFormat._0D:
                    return str(text)
                else:
                    return numpy.array(eval(text), dtype=str).tolist()
            elif model_type == DataType.Bytes:
                return bytes(text)
            else:
                raise TypeError('Unsupported model type "%s"', model_type)
        except Exception, e:
            self.warning('Cannot return value for "%s". Reason: %r', text, e)
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
        ret['icon'] = "designer:lineedit.png"
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

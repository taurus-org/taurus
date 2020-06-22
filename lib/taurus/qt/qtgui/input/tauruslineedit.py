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

"""
This module provides a set of basic taurus widgets based on QLineEdit
"""

from builtins import bytes
from builtins import str
import sys
import numpy
from taurus.external.qt import Qt
from taurus.core.units import Quantity
from taurus.qt.qtgui.base import TaurusBaseWritableWidget
from taurus.qt.qtgui.util import PintValidator
from taurus.core import DataType, DataFormat, TaurusEventType

__all__ = ["TaurusValueLineEdit"]

__docformat__ = 'restructuredtext'


class TaurusValueLineEdit(Qt.QLineEdit, TaurusBaseWritableWidget):
    """
    A taurus-aware ``QLineEdit``. It will display the value (or fragment
    of the value) referenced by its model. It is a
    :class:`~taurus.qt.qtgui.base.TaurusBaseWritableWidget`
    and as such it does not apply the changes straight away to the model
    (unless ``autoApply`` is enabled), but instead shows that there are pending
    operations which can be applied by pressing "ENTER".

    When used with numerical value Attributes as its model, it provides some
    extended behaviour:

    - It represents out-of-limit values using different colours (for warning,
      range, invalid,...)
    - It uses a validator that is range-aware
    - The mouse wheel and keyboard arrows can be enabled for doing value
      increments

    .. note::
        when used with models whose value is a pint `Quantity`, the text
        is parsed by pint and therefore one can write e.g. `2 3 mm` which is
        equivalent to `6 mm` !

    """

    _bytesEncoding = sys.stdin.encoding

    def __init__(self, qt_parent=None, designMode=False):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QLineEdit, qt_parent)
        self.call__init__(TaurusBaseWritableWidget,
                          name, designMode=designMode)
        self._enableWheelEvent = False
        self._last_value = None
        self._singleStep = 1.
        self._allow_auto_enable = True

        self.setAlignment(Qt.Qt.AlignRight)
        self.setValidator(None)

        self.textChanged.connect(self.notifyValueChanged)
        self.returnPressed.connect(self.writeValue)
        self.valueChangedSignal.connect(self.updatePendingOperations)
        self.editingFinished.connect(self._onEditingFinished)

    def _updateValidator(self, value):
        """This method sets a validator depending on the data type"""
        val = None
        if value is not None and isinstance(value.wvalue, Quantity):
            val = self.validator()
            if not isinstance(val, PintValidator):
                val = PintValidator(self)
                self.setValidator(val)
            attr = self.getModelObj()
            if attr is not None:
                bottom, top = attr.range
                if bottom != val.bottom:
                    val.setBottom(bottom)
                if top != val.top:
                    val.setTop(top)
            units = value.wvalue.units
            if units != val.units:
                val.setUnits(units)

        # @TODO Other validators can be configured for other types
        #       (e.g. with string lengths, tango names,...)
        else:
            self.setValidator(None)
            self.debug("Validator disabled")
        return val

    def __decimalDigits(self, fmt):
        """returns the number of decimal digits from a format string
        (or None if they are not defined)"""
        try:
            if fmt[-1].lower() in ['f', 'g'] and '.' in fmt:
                return int(fmt[:-1].split('.')[-1])
            else:
                return None
        except:
            return None

    def _onEditingFinished(self):
        """slot for performing autoapply only when edition is finished"""
        if self._autoApply:
            self.writeValue()

    # ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
    # TaurusBaseWritableWidget overwriting
    # ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
    def notifyValueChanged(self, *args):
        """reimplement to avoid autoapply on every partial edition"""
        self.emitValueChanged()

    def handleEvent(self, evt_src, evt_type, evt_value):

        # handle the case in which the line edit is not yet initialized
        if self._last_value is None:
            try:
                value = self.getModelObj().read(cache=True)
                self._updateValidator(value)
                self.setValue(value.wvalue)
            except Exception as e:
                self.info('Failed attempt to initialize value: %r', e)

        if self._allow_auto_enable:
            # use QLineEdit.setEnabled in order to avoid changing
            # _allow_auto_enable status
            Qt.QLineEdit.setEnabled(self, evt_type != TaurusEventType.Error)

        if evt_type in (TaurusEventType.Change, TaurusEventType.Periodic):
            self._updateValidator(evt_value)

        TaurusBaseWritableWidget.handleEvent(
            self, evt_src, evt_type, evt_value)

        if evt_type == TaurusEventType.Error:
            self.updateStyle()

    def setEnabled(self, enabled):
        """Reimplement from :class:`QLineEdit` to avoid autoenabling if the
        widget is explicitly disabled (but allow auto-disabling if the
        widget is explicitly enabled)
        """
        self._allow_auto_enable = enabled
        return Qt.QLineEdit.setEnabled(self, enabled)

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
        """Reimplemented from :class:`TaurusBaseWritableWidget`"""
        TaurusBaseWritableWidget.updateStyle(self)

        value = self.getValue()
        
        if value is None or not self.isTextValid() or not self.isEnabled():
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
            if modelObj and modelObj.type in [DataType.Integer,
                                              DataType.Float]:
                min_, max_ = modelObj.alarms
                if ((min_ is not None and value < min_) or
                        (max_ is not None and value > max_)):
                    color = 'orange'
        # apply style
        style = ('TaurusValueLineEdit {color: %s; font-weight: %s}' %
                 (color, weight))
        self.setStyleSheet(style)

    def wheelEvent(self, evt):
        """Wheel event handler"""
        if not self.getEnableWheelEvent() or Qt.QLineEdit.isReadOnly(self):
            return Qt.QLineEdit.wheelEvent(self, evt)
        model = self.getModelObj()
        if model is None or not model.isNumeric():
            return Qt.QLineEdit.wheelEvent(self, evt)

        evt.accept()
        numDegrees = evt.delta() // 8
        numSteps = numDegrees // 15
        self._stepBy(numSteps)

    def keyPressEvent(self, evt):
        """Key press event handler"""
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
        self._stepBy(numSteps)

    def _stepBy(self, steps):
        value = self.getValue()
        self.setValue(value + Quantity(steps * self._singleStep, value.units))

        if self.getAutoApply():
            self.editingFinished.emit()
        else:
            kmods = Qt.QCoreApplication.instance().keyboardModifiers()
            controlpressed = bool(kmods & Qt.Qt.ControlModifier)
            if controlpressed:
                self.writeValue(forceApply=True)

    def setValue(self, v):
        """Set the displayed text from a given value object"""
        # Support displaying the value without units (enabled by fragment)
        # Other fragments are ignored by setValue
        if self.modelFragmentName == "wvalue.magnitude":
            try:
                validator = self.validator()
                if validator is None:
                    value = self.getModelValueObj()
                    validator = self._updateValidator(value)
                units = validator.units
                v = v.to(units).magnitude
            except Exception as e:
                self.debug('Cannot enforce fragment. Reason: %r', e)
        self._last_value = v
        self.setText(str(self.displayValue(v)).strip())

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
                    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    # workaround for https://github.com/hgrecco/pint/issues/614
                    text = text.lstrip('0') or '0'
                    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    q = Quantity(text)
                    # allow implicit units (assume wvalue.units implicitly)
                    if q.unitless:
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
                return bytes(text, self._bytesEncoding)
            else:
                raise TypeError('Unsupported model type "%s"' % model_type)
        except Exception as e:
            msg = 'Cannot return value for "%s". Reason: %r'
            if text in (str(None), self.getNoneValue()):
                self.debug(msg, text, e)
            else:
                self.warning(msg, text, e)
            return None

    def setEnableWheelEvent(self, b):
        self._enableWheelEvent = b

    def getEnableWheelEvent(self):
        return self._enableWheelEvent

    def resetEnableWheelEvent(self):
        self.setEnableWheelEvent(False)

    def getSingleStep(self):
        return self._singleStep

    def setSingleStep(self, step):
        self._singleStep = step

    def resetSingleStep(self):
        self.setSingleStep(1.0)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWritableWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.input'
        ret['icon'] = "designer:lineedit.png"
        return ret

    # ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
    # QT properties
    # ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~

    model = Qt.pyqtProperty("QString", TaurusBaseWritableWidget.getModel,
                            TaurusBaseWritableWidget.setModel,
                            TaurusBaseWritableWidget.resetModel)

    useParentModel = Qt.pyqtProperty(
        "bool", TaurusBaseWritableWidget.getUseParentModel,
        TaurusBaseWritableWidget.setUseParentModel,
        TaurusBaseWritableWidget.resetUseParentModel)

    autoApply = Qt.pyqtProperty("bool", TaurusBaseWritableWidget.getAutoApply,
                                TaurusBaseWritableWidget.setAutoApply,
                                TaurusBaseWritableWidget.resetAutoApply)

    forcedApply = Qt.pyqtProperty("bool",
                                  TaurusBaseWritableWidget.getForcedApply,
                                  TaurusBaseWritableWidget.setForcedApply,
                                  TaurusBaseWritableWidget.resetForcedApply)

    enableWheelEvent = Qt.pyqtProperty("bool", getEnableWheelEvent,
                                       setEnableWheelEvent,
                                       resetEnableWheelEvent)


def main():
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication

    app = Application.instance()
    owns_app = app is None

    if owns_app:
        import taurus.core.util.argparse
        parser = taurus.core.util.argparse.get_taurus_parser()
        parser.usage = "%prog [options] <full_attribute_name(s)>"
        app = Application(sys.argv, cmd_line_parser=parser,
                          app_name="Taurus lineedit demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")

    args = app.get_command_line_args()

    form = Qt.QWidget()
    layout = Qt.QVBoxLayout()
    form.setLayout(layout)
    if len(args) == 0:
        models = ['sys/tg_test/1/double_scalar', 'sys/tg_test/1/double_scalar']
    else:
        models = args
    for model in models:
        w = TaurusValueLineEdit()
        w.setModel(model)
        layout.addWidget(w)
    form.resize(300, 50)
    form.show()

    if owns_app:
        sys.exit(app.exec_())
    else:
        return form


if __name__ == "__main__":
    sys.exit(main())

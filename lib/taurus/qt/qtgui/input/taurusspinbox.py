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
This module provides a set of basic taurus widgets based on QAbstractSpinBox
"""

from __future__ import absolute_import

from taurus.external.qt import Qt

from .tauruslineedit import TaurusValueLineEdit
from taurus.qt.qtgui.icon import getStandardIcon
from taurus.core.units import Quantity
from taurus.qt.qtgui.util import PintValidator


__all__ = ["TaurusValueSpinBox", "TaurusValueSpinBoxEx"]

__docformat__ = 'restructuredtext'


class TaurusValueSpinBox(Qt.QAbstractSpinBox):

    modelChanged = Qt.pyqtSignal('const QString &')

    def __init__(self, qt_parent=None, designMode=False):
        Qt.QAbstractSpinBox.__init__(self, qt_parent)

        # Overwrite not to show quality by default
        self._showQuality = False

        lineEdit = TaurusValueLineEdit(designMode=designMode)
        lineEdit.setValidator(PintValidator(self))
        lineEdit.setEnableWheelEvent(True)
        self.setLineEdit(lineEdit)
        self.setAccelerated(True)

    def __getattr__(self, name):
        return getattr(self.lineEdit(), name)

    def setValue(self, v):
        self.lineEdit().setValue(v)

    def getValue(self):
        return self.lineEdit().getValue()

    def keyPressEvent(self, evt):
        return self.lineEdit().keyPressEvent(evt)

    def wheelEvent(self, evt):
        return self.lineEdit().wheelEvent(evt)

    # ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
    # Mandatory overload from QAbstractSpinBox
    # ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~

    def stepBy(self, steps):
        return self.lineEdit()._stepBy(steps)

    def stepEnabled(self):
        ret = Qt.QAbstractSpinBox.StepEnabled(Qt.QAbstractSpinBox.StepNone)
        if self.getModelObj() is None:
            return ret
        if self.getModelObj().getValueObj() is None:
            return ret

        curr_val = self.getValue()

        if curr_val is None:
            return ret

        ss = self._getSingleStepQuantity()

        if self.validate(str(curr_val + ss), 0)[0] == Qt.QValidator.Acceptable:
            ret |= Qt.QAbstractSpinBox.StepUpEnabled
        if self.validate(str(curr_val - ss), 0)[0] == Qt.QValidator.Acceptable:
            ret |= Qt.QAbstractSpinBox.StepDownEnabled
        return ret

    # ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
    # Overload from QAbstractSpinBox
    # ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~

    def validate(self, input, pos):
        """Overloaded to use the current validator from the TaurusValueLineEdit,
        instead of the default QAbstractSpinBox validator. If no validator is
        set in the LineEdit, it falls back to the original behaviour
        """
        val = self.lineEdit().validator()
        if val is None:
            return Qt.QAbstractSpinBox.validate(self, input, pos)
        return val.validate(input, pos)

    # ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
    # Model related methods
    # ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~

    def setModel(self, model):
        self.lineEdit().setModel(model)

    def getModel(self):
        return self.lineEdit().getModel()

    def resetModel(self):
        return self.lineEdit().resetModel()

    def setUseParentModel(self, model):
        self.lineEdit().setUseParentModel(model)

    def getUseParentModel(self):
        return self.lineEdit().getUseParentModel()

    def resetUseParentModel(self):
        return self.lineEdit().resetUseParentModel()

    def setAutoApply(self, model):
        self.lineEdit().setAutoApply(model)

    def getAutoApply(self):
        return self.lineEdit().getAutoApply()

    def resetAutoApply(self):
        return self.lineEdit().resetAutoApply()

    def setForcedApply(self, model):
        self.lineEdit().setForcedApply(model)

    def getForcedApply(self):
        return self.lineEdit().getForcedApply()

    def resetForcedApply(self):
        return self.lineEdit().resetForcedApply()

    def getSingleStep(self):
        return self.lineEdit().getSingleStep()

    @Qt.pyqtSlot(float)
    def setSingleStep(self, step):
        self.lineEdit().setSingleStep(step)

    def resetSingleStep(self):
        self.lineEdit().resetSingleStep()

    def _getSingleStepQuantity(self):
        """
        :return: (Quantity) returns a single step with the units of the current
                 value
        """
        value = self.getValue()
        if value is None:
            return None
        return Quantity(self.getSingleStep(), value.units)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return {
            'group': 'Taurus Input',
            'icon': 'designer:spinbox.png',
            'module': 'taurus.qt.qtgui.input',
            'container': False}

    singleStep = Qt.pyqtProperty("double", getSingleStep, setSingleStep,
                                 resetSingleStep)

    model = Qt.pyqtProperty("QString", getModel, setModel, resetModel)

    useParentModel = Qt.pyqtProperty("bool", getUseParentModel,
                                     setUseParentModel, resetUseParentModel)

    autoApply = Qt.pyqtProperty("bool", getAutoApply, setAutoApply,
                                resetAutoApply)

    forcedApply = Qt.pyqtProperty("bool", getForcedApply, setForcedApply,
                                  resetForcedApply)


_S = """
QSpinBox::up-button {
    border-width: 0px;
}
QPushButton {
    min-width: 6px;
    min-height: 10px;
    /*border-style: solid;
    border-width: 1px;
    border-color: black;
    border-top-right-radius: 2px;
    border-bottom-right-radius: 2px;*/
    margin: 0px;
    padding: 0px;
}
"""


class TaurusValueSpinBoxEx(Qt.QWidget):

    def __init__(self, qt_parent=None, designMode=False):
        Qt.QWidget.__init__(self, qt_parent)
        layout = Qt.QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.setStyleSheet(_S)
        self.__dict__['spinBox'] = spin = TaurusValueSpinBox(
            qt_parent=self, designMode=designMode)
        self.__dict__['sliderButton1'] = b1 = Qt.QToolButton(self)
        self.__dict__['sliderButton2'] = b2 = Qt.QToolButton(self)
        b1.setIcon(getStandardIcon(Qt.QStyle.SP_TitleBarShadeButton, b1))
        b2.setIcon(getStandardIcon(Qt.QStyle.SP_TitleBarUnshadeButton, b2))
        layout.addWidget(spin, 0, 0, 2, 1)
        layout.addWidget(b1, 0, 1, 1, 1, Qt.Qt.AlignBottom)
        layout.addWidget(b2, 1, 1, 1, 1, Qt.Qt.AlignTop)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 0)

        policy = self.sizePolicy()
        policy.setHorizontalPolicy(Qt.QSizePolicy.Minimum)
        policy.setVerticalPolicy(Qt.QSizePolicy.Fixed)
        self.setSizePolicy(policy)

    def __getattr__(self, name):
        return getattr(self.spinBox, name)

    def __setattr__(self, name, value):
        setattr(self.spinBox, name, value)


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
                          app_name="Taurus spinbox demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")

    args = app.get_command_line_args()

    if len(args) == 0:
        w = TaurusValueSpinBox()
        w.setModel('sys/tg_test/1/double_scalar')
        w.resize(300, 50)
    else:
        w = Qt.QWidget()
        layout = Qt.QGridLayout()
        w.setLayout(layout)
        for model in args:
            label = TaurusValueSpinBox()
            label.setModel(model)
            layout.addWidget(label)
        w.resize(300, 50)
    w.show()

    if owns_app:
        sys.exit(app.exec_())
    else:
        return w


if __name__ == "__main__":
    main()
#     import sys
#     from taurus.qt.qtgui.application import TaurusApplication
#     app = TaurusApplication(cmd_line_parser=None)

#     w = TaurusValueSpinBox()
#     w.setModel('sys/tg_test/1/double_scalar')
#     w.resize(300, 50)
#     w.show()

#     sys.exit(app.exec_())

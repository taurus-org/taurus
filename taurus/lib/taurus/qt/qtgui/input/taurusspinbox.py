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

"""This module provides a set of basic taurus widgets based on QAbstractSpinBox"""

__all__ = ["TaurusValueSpinBox", "TaurusValueSpinBoxEx" ]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt

from taurus.qt.qtgui.base import TaurusBaseWritableWidget
from tauruslineedit import TaurusValueLineEdit
from taurus.qt.qtgui.resource import getStandardIcon

class TaurusValueSpinBox(Qt.QAbstractSpinBox):

    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, qt_parent = None, designMode = False):
        Qt.QAbstractSpinBox.__init__(self, qt_parent)
        
        # Overwrite not to show quality by default
        self._showQuality = False
        
        self._singleStep = 1.0
        
        self.setLineEdit(TaurusValueLineEdit(designMode=designMode))
        self.setAccelerated(True)

    def __getattr__(self, name):
        return getattr(self.lineEdit(), name)

    # The minimum size of the widget (a limit for the user)
    #def minimumSizeHint(self):
    #    return Qt.QSize(20, 20)
    
    # The default size of the widget
    #def sizeHint(self):
    #    return Qt.QSize(80, 24)
        
    def setValue(self, v):
        self.lineEdit().setValue(v)

    def getValue(self):
        return self.lineEdit().getValue()
    
    def keyPressEvent(self, event):
        if event.key() in (Qt.Qt.Key_Return, Qt.Qt.Key_Enter):
            self.lineEdit().writeValue()
            event.accept()
        else:
            Qt.QAbstractSpinBox.keyPressEvent(self,event)
            event.ignore()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Mandatory overload from QAbstractSpinBox
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def stepBy(self, steps):
        #validator = self.lineEdit().validator()
        self.setValue(self.getValue() + self.getSingleStep()*steps)

        if self.lineEdit().getAutoApply():
            self.lineEdit().emit(Qt.SIGNAL('editingFinished()'))
        else:
            kmods = Qt.QCoreApplication.instance().keyboardModifiers()
            controlpressed = bool(kmods&Qt.Qt.ControlModifier)
            if controlpressed:
                self.lineEdit().writeValue(forceApply=True)
    
    def stepEnabled(self):
        le, curr_val, ss = self.lineEdit(), self.getValue(), self.getSingleStep()
        ret = Qt.QAbstractSpinBox.StepEnabled(Qt.QAbstractSpinBox.StepNone)
        
        if curr_val == None:
            return ret
        
        if not le._outOfRange(curr_val + ss):
            ret |= Qt.QAbstractSpinBox.StepUpEnabled
        if not le._outOfRange(curr_val - ss):
            ret |= Qt.QAbstractSpinBox.StepDownEnabled
        return ret
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Model related methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
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
        return self._singleStep
    
    def setSingleStep(self, step):
        self._singleStep = step
    
    def resetSingleStep(self):
        self.setSingleStep(1.0)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return { 
            'group'     : 'Taurus Input',
            'icon'      : ':/designer/spinbox.png',
            'module'    : 'taurus.qt.qtgui.input',
            'container' : False }
    
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

    def __init__(self, qt_parent = None, designMode = False):
        Qt.QWidget.__init__(self, qt_parent)
        layout = Qt.QGridLayout()
        layout.setMargin(0)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.setLayout(layout)
        self.setStyleSheet(_S)
        self.__dict__['spinBox'] = spin = TaurusValueSpinBox(qt_parent=self, designMode=designMode)
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
    
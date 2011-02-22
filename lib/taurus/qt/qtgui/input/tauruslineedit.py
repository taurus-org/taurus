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

from PyQt4 import Qt

import sys
import PyTango

import taurus.core
from taurus.qt.qtgui.base import TaurusBaseWidget, TaurusBaseWritableWidget

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
            decimalDigits = self.__decimalDigits(attrinfo.format)
            if decimalDigits is not None:
                validator.setDecimals(decimalDigits)
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
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWritableWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_type == taurus.core.TaurusEventType.Config:
            if evt_value.min_alarm != taurus.core.TaurusConfiguration.no_min_alarm:
                self.__minAlarm = float(evt_value.min_alarm)
            else:
                self.__minAlarm = -float("inf")
            if evt_value.max_alarm != taurus.core.TaurusConfiguration.no_max_alarm:
                self.__maxAlarm = float(evt_value.max_alarm)
            else:
                self.__maxAlarm = float("inf")
            if evt_value.min_value != taurus.core.TaurusConfiguration.no_min_value:
                self.__minLimit = float(evt_value.min_value)
            else:
                self.__minLimit = -float("inf")
            if evt_value.max_value != taurus.core.TaurusConfiguration.no_max_value:
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
            return validator.validate(Qt.QString(str(v)),0)[0] != validator.Acceptable
        else: #fallback, only for numeric types (returns False for other types)
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


## TaurusConfigLineEdit has been marked as obsolete because it is not adapted to new 
## event handling and it is not clear wether anyone is interested in keeping it
## If you want to use it, contact cpascual@cells.es or tcoutinho@cells.es
class TaurusConfigLineEdit(Qt.QLineEdit, TaurusBaseWidget):

    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, qt_parent = None, designMode = False):
        
        raise DeprecationWarning('TaurusConfigLineEdit is deprecated. It does not integrate well with latest taurus features')
        
        name = self.__class__.__name__
        self._lastValueByUser = ''
        self.call__init__wo_kw(Qt.QLineEdit, qt_parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        
        self.setObjectName(name)
        
        self._dftShadow = self.palette().shadow()
        self._dftHighlight = self.palette().highlight()
        self._dftButton = self.palette().button()
        
        self.defineStyle()
        
        self.connect(self, Qt.SIGNAL('textChanged(QString)'),self.emitValueChanged)
        
    def defineStyle(self):
        self.setAlignment(Qt.Qt.AlignRight)
        self.updateStyle()
        
    # The minimum size of the widget (a limit for the user)
    def minimumSizeHint(self):
        return Qt.QSize(20, 20)
    
    # The default size of the widget
    def sizeHint(self):
        return Qt.QSize(60, 24)
                
    def focusInEvent(self,focusEvent):
        Qt.QLineEdit.focusInEvent(self,focusEvent)
        self.updateStyle()

    def focusOutEvent(self,focusEvent):
        Qt.QLineEdit.focusOutEvent(self,focusEvent)
        self.updateStyle()
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def getModelClass(self):
        return taurus.core.TaurusConfiguration
    
    def preAttach(self):
        TaurusBaseWidget.preAttach(self)
        Qt.QObject.connect(self, Qt.SIGNAL("returnPressed()"), 
                               self.writeTextValue)
        Qt.QObject.connect(self, Qt.SIGNAL("textChanged(QString)"), 
                               self.userChangedValue)

    def postAttach(self):
        TaurusBaseWidget.postAttach(self)

        # Set an initial value if necessary
        if self.isAttached() and not self.isReadOnly():
            value_str = self.getDisplayValue()
            self._lastValueByUser = value_str
            self.emit(Qt.SIGNAL('valueChangedDueToEvent(QString)'), 
                      Qt.QString(value_str))

    def postDetach(self):
        TaurusBaseWidget.postDetach(self)
        Qt.QObject.disconnect(self, Qt.SIGNAL("returnPressed()"), 
                                  self.writeTextValue)
        Qt.QObject.disconnect(self, Qt.SIGNAL("textChanged(QString)"), 
                                  self.userChangedValue)

    def getConfigurationAttributeValue(self):
        """Helper method to get the proper parameter value from the configuration"""
        model = self.getModelObj()
        if model is None:
            return None
        try:
            return getattr(model, str(self._configParam))
        except:
            self.debug("Invalid configuration parameter %s" % self._configParam)
            return None
        
    def getDisplayValue(self):
        cfg_value = self.getConfigurationAttributeValue()
        if cfg_value is None:
            cfg_value = self.getNoneValue()
        else:
            cfg_value = str(cfg_value)
        return cfg_value

    def isValueChangedByUser(self):
        localValue = str(self.text())
        return not localValue == self._lastValueByUser

    def updateStyle(self):
        p = self.palette()
        
        p.setBrush(Qt.QPalette.Base, Qt.Qt.white)
        p.setBrush(Qt.QPalette.Text,Qt.Qt.black)
        
        if not self.isReadOnly() and self.isValueChangedByUser():
            if self.hasFocus():
                p.setBrush(Qt.QPalette.Highlight, Qt.Qt.blue)
            else:
                p.setBrush(Qt.QPalette.Shadow, Qt.Qt.blue)
                p.setBrush(Qt.QPalette.Button, Qt.Qt.blue)
        else:
            p.setBrush(Qt.QPalette.Shadow, self._dftShadow)
            p.setBrush(Qt.QPalette.Button, self._dftButton)
            p.setBrush(Qt.QPalette.Highlight, self._dftHighlight)
        self.updatePendingOpsStyle()
        self.update()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
   
    @Qt.pyqtSignature("setModel(QString)")
    def setModel(self, model):
        model = str(model)
        try:
            self._configParam = model[model.rfind('=')+1:].lower()
        except:
            self._configParam = ''
        TaurusBaseWidget.setModel(self,model)

    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel, setModel,
                            TaurusBaseWidget.resetModel)
                                
    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWidget.getUseParentModel,
                                     TaurusBaseWidget.setUseParentModel, 
                                     TaurusBaseWidget.resetUseParentModel)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT signal handlers
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @Qt.pyqtSignature("textChanged(QString)")
    def userChangedValue(self,qstr):
        self.updateStyle()
    
    @Qt.pyqtSignature("returnPressed(QString)")
    def writeTextValue(self):
        model = self.getModelObj()
        if not self.isReadOnly() and model:
            try:
                new_value = str(self.text())
                model.setParam(self._configParam, new_value)
                self._lastValueByUser = new_value
                self.updateStyle()
            except PyTango.DevFailed, e:
                ret = Qt.QMessageBox.warning(self, "Write error",e[0]['desc'],
                                             Qt.QMessageBox.Ok)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        # Disable designer plugin
        return None


def main():
    import sys
    attr_name = sys.argv[1]
    a = Qt.QApplication([])
    panel = Qt.QWidget()
    l = Qt.QGridLayout()
    w1 = TaurusValueLineEdit()
    w1.setModel(attr_name)
    l.addWidget(w1,0,0)
    
    panel.setLayout(l)
    panel.setVisible(True)
    return a.exec_()

if __name__ == "__main__":
    sys.exit(main())

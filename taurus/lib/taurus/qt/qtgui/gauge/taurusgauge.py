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

"""This module contains a collection of taurus Qt gauge widgets based on ELECTTRA's
qtcontrols library"""

import qtcontrols

__all__ = ['TaurusLinearGauge', 'TaurusCircularGauge']

__docformat__ = 'restructuredtext'

import math

from taurus.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseWidget

class TaurusLinearGauge(qtcontrols.ELinearGauge, TaurusBaseWidget):

    __pyqtSignals__ = ("modelChanged(const QString &)",)
    
    def __init__(self, parent = None, designMode = False):
        name = self.__class__.__name__
        self.call__init__wo_kw(qtcontrols.ELinearGauge, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)

    def sizeHint(self):
        return Qt.QSize(100, 200)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwritting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def getModelClass(self):
        import taurus.core
        return taurus.core.taurusattribute.TaurusAttribute

    def handleEvent(self, evt_src, evt_type, evt_value):
        v, v_ref = None, None
        
        model = self.getModelObj()
        v = self.getModelValueObj()
        
        if model is None or v is None:
            self.setEnabled(False)
        else:
            self.setEnabled(True)

        if not v is None:
            v_ref = v.w_value or self.minValue()
            v = v.value
        else:
            v = v_ref = self.minValue()

        self.setValue(v)
        self.setReference(v_ref)

        if model is None:
            # no information available
            # keep the old values
            pass
        else:
            try:
                minW, maxW = int(model.getMinWarning()), int(model.getMaxWarning())
                self.setLowWarning(minW)
                self.setHighWarning(maxW)
            except:
                pass
            try:
                minV, maxV = int(model.getMinValue()), int(model.getMaxValue())
                self.setMinValue(minV)
                self.setMaxValue(maxV)
            except:
                pass
            try:
                minA, maxA = int(model.getMinAlarm()), int(model.getMaxAlarm())
                self.setLowError(minA)
                self.setHighError(maxA)
            except:
                pass
        
        self.setToolTip(self.getFormatedToolTip())

    def isReadOnly(self):
        return True

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['group'] = 'Taurus Display'
        ret['module'] = 'taurus.qt.qtgui.gauge'
        ret['icon'] = ":/designer/vertical_linear_gauge.png"
        return ret
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-  

    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel,
                            TaurusBaseWidget.setModel,
                            TaurusBaseWidget.resetModel)
                                
    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWidget.getUseParentModel,
                                     TaurusBaseWidget.setUseParentModel,
                                     TaurusBaseWidget.resetUseParentModel)


class TaurusCircularGauge(qtcontrols.ECircularGauge, TaurusBaseWidget):

    __pyqtSignals__ = ("modelChanged(const QString &)",)
    
    def __init__(self, parent = None, designMode = False):
        name = self.__class__.__name__
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        self.call__init__wo_kw(qtcontrols.ECircularGauge, parent)
        
        self._logScale = False

    def sizeHint(self):
        return Qt.QSize(100, 100)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwritting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def getModelClass(self):
        import taurus.core
        return taurus.core.taurusattribute.TaurusAttribute

    def handleEvent(self, evt_src, evt_type, evt_value):
        v, v_ref = None, None
        
        model = self.getModelObj()
        v = self.getModelValueObj()
        
        if model is None or v is None:
            self.setEnabled(False)
        else:
            self.setEnabled(True)

        if not v is None:
            v_ref = v.w_value or self.minValue()
            v = v.value
        else:
            v = v_ref = self.minValue()

        if self._logScale:
            v = math.log(v, 10)
                
        self.setValue(v)
        self.setReference(v_ref)

        if model is None:
            # no information available
            # keep the old values
            pass
        else:
            fmt = model.getFormat() or self.valueFormat()
            self.setValueFormat(fmt)
            try:
                minW, maxW = int(model.getMinWarning()), int(model.getMaxWarning())
                if self._logScale: minW, maxW = math.log(minW, 10), math.log(maxW, 10)
                self.setLowWarning(minW)
                self.setHighWarning(maxW)
            except:
                pass
            try:
                minV, maxV = int(model.getMinValue()), int(model.getMaxValue())
                if self._logScale: minV, maxV = math.log(minV, 10), math.log(maxV, 10)
                self.setMinValue(minV)
                self.setMaxValue(maxV)
            except:
                pass
            try:
                minA, maxA = int(model.getMinAlarm()), int(model.getMaxAlarm())
                if self._logScale: minA, maxA = math.log(minA, 10), math.log(maxA, 10)
                self.setLowError(minA)
                self.setHighError(maxA)
            except:
                pass
        
        self.setToolTip(self.getFormatedToolTip())

    def isReadOnly(self):
        return True
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-  
    
    def getLogScale(self):
        return self._logScale

    @Qt.pyqtSignature("setLogScale(bool)")
    def setLogScale(self, val):
        self._logScale = bool(val)
        self.updateStyle()

    def resetLogScale(self):
        self._logScale = False
        self.updateStyle()

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['group'] = 'Taurus Display'
        ret['module'] = 'taurus.qt.qtgui.gauge'
        ret['icon'] = ":/designer/circular_gauge.png"
        return ret
    
    logScale  = Qt.pyqtProperty("bool", getLogScale, setLogScale, resetLogScale)
    
    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel,
                            TaurusBaseWidget.setModel, TaurusBaseWidget.resetModel)
                                
    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWidget.getUseParentModel,
                                     TaurusBaseWidget.setUseParentModel,
                                     TaurusBaseWidget.resetUseParentModel)

def main():
    import sys
    import taurus
    attr_name = sys.argv[1]
    attr = taurus.Attribute(attr_name)
    
    a = Qt.QApplication([])
    panel = Qt.QWidget()
    l = Qt.QGridLayout()
    w1 = TaurusCircularGauge()
    w2 = TaurusLinearGauge()
    w1.setModel(attr_name)
    w2.setModel(attr_name)
    
    l.addWidget(w1,0,0)
    l.addWidget(w2,1,0)
    panel.setLayout(l)
    panel.setVisible(True)
    a.exec_()

if __name__ == "__main__":
    main()

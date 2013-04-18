#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""This module provides a set of basic Taurus widgets based on QLabel"""

__all__ = ["TaurusBoolLed"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt

# ugly
import PyTango

import taurus.core.util
from taurus.qt.qtgui.base import TaurusBaseWidget
from qled import LedStatus, LedColor, LedSize
from qled import QLedOld as QLed
    
class TaurusBoolLed(QLed, TaurusBaseWidget):
    """
       A led widget displaying the boolean tango attribute value
       
       .. deprecated:: 2.0
           Use :class:`taurus.qt.qtgui.display.TaurusLed` instead.
    """

    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, parent = None, designMode = False):
        self._ledColor = 'GREEN'
        self._ledColorOff = 'GREENOFF'
        self._ledSize = 24
        self._ledColorPixmap = None
        self._ledColorOffPixmap = None
        self._boolIndex = 0
        
        self.call__init__wo_kw(QLed, parent)
        self.call__init__(TaurusBaseWidget, str(self.objectName()), designMode=designMode)

        self.setLedColor(self._ledColor)
        self.setLedColorOff(self._ledColorOff)
        
        self.setEventFilters([taurus.core.util.eventfilters.IGNORE_CONFIG]) #This widget does not need to attend to config events

    def sizeHint(self):
        return Qt.QSize(24, 24)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwritting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getModelClass(self):
        return taurus.core.taurusattribute.TaurusAttribute

    def isReadOnly(self):
        return True

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getLedColor(self):
        return self._ledColor

    @Qt.pyqtSignature("setLedColor(QString)")
    def setLedColor(self, lc):
        self._ledColor = str(lc)

        status = LedStatus.ON
        color = self._ledColor
        if color.endswith('OFF'):
            status = LedStatus.OFF
            color = color[:-3]
        color = LedColor[color]
        file_name = self.toCompleteLedName(self.ledsize, status, color)
        self._ledColorPixmap = Qt.QPixmap(file_name)
        
    def resetLedColor(self,lc):
        self.setLedColor('GREEN')

    def getLedColorOff(self):
        return self._ledColorOff

    @Qt.pyqtSignature("setLedColorOff(QString)")
    def setLedColorOff(self, lc):
        self._ledColorOff = str(lc)

        status = LedStatus.ON
        color = self._ledColorOff
        if color.endswith('OFF'):
            status = LedStatus.OFF
            color = color[:-3]

        color = LedColor[color]
        file_name = self.toCompleteLedName(self.ledsize, status, color)
        self._ledColorOffPixmap = Qt.QPixmap(file_name)
        
    def resetLedColorOff(self,lc):
        self.setLedColorOff('GREENOFF')

    def getLedSize(self):
        return self._ledSize

    @Qt.pyqtSignature("setLedSize(int)")
    def setLedSize(self,size):
        self._ledSize = size
        try:
            getattr(LedSize,str(self._ledSize))
            self.changeSize(self._ledSize)
        except:
            pass

    def resetLedSize(self,size):
        self.setLedSize(24)

    def getBoolIndex(self):
        return self._boolIndex

    @Qt.pyqtSignature("setBoolIndex(int)")
    def setBoolIndex(self,i):
        self._boolIndex = i
        try:
            getattr(BoolIndex,str(self._boolIndex))
            self.changeSize(self._boolIndex)
        except:
            pass

    def resetBoolIndex(self):
        self.setBoolIndex(0)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
#        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
#        ret['module'] = 'taurus.qt.qtgui.display'
#        ret['group'] = 'Taurus Widgets [Old]'
#        ret['icon'] = ":/designer/ledgreen.png"
#        return ret
        
    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel,
                            TaurusBaseWidget.setModel,
                            TaurusBaseWidget.resetModel)

    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWidget.getUseParentModel,
                                     TaurusBaseWidget.setUseParentModel,
                                     TaurusBaseWidget.resetUseParentModel)

    ledColor = Qt.pyqtProperty("QString", getLedColor, setLedColor, resetLedColor,
                               doc='valid values are (case insensitive) "BLUE", "GREEN", "RED", "YELLOW", "ORANGE", "BLUEOFF", "GREENOFF", "REDOFF", "YELLOWOFF", "ORANGEOFF"')

    ledColorOff = Qt.pyqtProperty("QString", getLedColorOff, setLedColorOff,
                                  resetLedColorOff,
                                  doc='valid values are (case insensitive) "BLUE", "GREEN", "RED", "YELLOW", "ORANGE", "BLUEOFF", "GREENOFF", "REDOFF", "YELLOWOFF", "ORANGEOFF"')

    ledSize = Qt.pyqtProperty("int", getLedSize, setLedSize, resetLedSize,
                              doc='valid values as 24 and 48')

    boolIndex = Qt.pyqtProperty("int", getBoolIndex, setBoolIndex, resetBoolIndex,)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT signal handlers
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_value is None:
            return
        if evt_type == taurus.core.taurusbasetypes.TaurusEventType.Error:
            self._setProblemsBackground(True)
            self.updateStyle()
            return
        self._setProblemsBackground(False)

        if evt_value.data_format == PyTango.AttrDataFormat.SCALAR:
            v = evt_value.value
        elif evt_value.data_format == PyTango.AttrDataFormat.SPECTRUM:
            v = evt_value.value[self.boolIndex]

        if v is True: #we know that evt_value will always be a DeviceAttribute because we filter out Config events
            self.setPixmap(self._ledColorPixmap)
        else:
            self.setPixmap(self._ledColorOffPixmap)
        self.updateStyle()


if __name__ == "__main__":
    import sys
    app = Qt.QApplication(sys.argv)
    
    model = 'sys/tg_test/1/boolean_scalar'
    if len(sys.argv)>1: model=sys.argv[1]
    
    w = TaurusBoolLed()
    w.setModel(model)
    w.setVisible(True)
    
    sys.exit(app.exec_())


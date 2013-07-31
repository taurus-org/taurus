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

__all__ = ["TaurusStateLed"]

__docformat__ = 'restructuredtext'

# ugly
import PyTango

from taurus.core.taurusbasetypes import TaurusEventType
from taurus.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseWidget
from qled import LedStatus, LedColor
from qled import QLedOld as QLed


class TaurusStateLed(QLed, TaurusBaseWidget):
    """
       A led widget displaying the state tango attribute value
    
       .. deprecated:: 2.0
           Use :class:`taurus.qt.qtgui.display.TaurusLed` instead.
    """

    __pyqtSignals__ = ("modelChanged(const QString &)",)

    DEVICE_STATE_DATA = {
        PyTango.DevState.ON      : (LedStatus.ON,   LedColor.GREEN),
        PyTango.DevState.OFF     : (LedStatus.OFF,  LedColor.GREEN),
        PyTango.DevState.CLOSE   : (LedStatus.ON,   LedColor.GREEN),
        PyTango.DevState.OPEN    : (LedStatus.ON,   LedColor.GREEN),
        PyTango.DevState.INSERT  : (LedStatus.ON,   LedColor.GREEN),
        PyTango.DevState.EXTRACT : (LedStatus.ON,   LedColor.GREEN),
        PyTango.DevState.MOVING  : (LedStatus.ON,   LedColor.BLUE),
        PyTango.DevState.STANDBY : (LedStatus.ON,   LedColor.YELLOW),
        PyTango.DevState.FAULT   : (LedStatus.ON,   LedColor.RED),
        PyTango.DevState.INIT    : (LedStatus.ON,   LedColor.YELLOW),
        PyTango.DevState.RUNNING : (LedStatus.ON,   LedColor.BLUE),
        PyTango.DevState.ALARM   : (LedStatus.ON,   LedColor.ORANGE),
        PyTango.DevState.DISABLE : (LedStatus.OFF,  LedColor.ORANGE),
        PyTango.DevState.UNKNOWN : (LedStatus.OFF,  LedColor.BLUE),
        None                     : (LedStatus.OFF,  LedColor.RED)}

    def __init__(self, parent = None, designMode = False):
        name = self.__class__.__name__
        self._boolIndex = 0
        self.call__init__wo_kw(QLed, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)

    # The default size of the widget
    def sizeHint(self):
        return Qt.QSize(24, 24)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwritting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getModelClass(self):
        import taurus.core
        return taurus.core.taurusattribute.TaurusAttribute

    def isReadOnly(self):
        return True

    def getFormatedToolTip(self, cache=True):
        """ The tooltip should refer to the device and not the state attribute.
            That is why this method is being rewritten
        """
        if self.modelObj is None:
            return self.getNoneValue()
        parent = self.modelObj.getParentObj()
        if parent is None:
            return self.getNoneValue()
        return self.toolTipObjToStr( parent.getDisplayDescrObj() )

    def handleEvent(self, evt_src, evt_type, evt_value):

        if evt_type == TaurusEventType.Error:
            self._setProblemsBackground(True)
            self.updateStyle()
            return
        self._setProblemsBackground(False)
    
        v = getattr(evt_value, 'value',                                  
                    getattr(self.getModelValueObj(), 'value', None)) #tries to get the value from the event itself, and asks if not

        if evt_value.data_format == PyTango.AttrDataFormat.SPECTRUM:
            v = v[self.boolIndex]

        onOff,state = TaurusStateLed.DEVICE_STATE_DATA[v]
        if onOff == LedStatus.OFF:
            self.off()
        else:
            self.on()
        self.changeColor(state)
        
        #update tooltip
        self.setToolTip(self.getFormatedToolTip())
        
        #TODO: update whatsThis
        
        #update appearance
        self.updateStyle()

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
#        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
#        ret['group'] = 'Taurus Widgets [Old]'
#        ret['module'] = 'taurus.qt.qtgui.display'
#        ret['icon'] = ":/designer/ledred.png"
#        return ret
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getBoolIndex(self):
        return self._boolIndex

    @Qt.pyqtSignature("setBoolIndex(int)")
    def setBoolIndex(self,i):
        self._boolIndex = i

    def resetBoolIndex(self):
        self.setBoolIndex(0)
        
    def getLedSize(self):
        return self.ledsize

    @Qt.pyqtSignature("setLedSize(QString)")
    def setLedSize(self,size):
        self.changeSize(size)

    def resetLedSize(self,size):
        self.changeSize('24')

    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel,
                            TaurusBaseWidget.setModel,
                            TaurusBaseWidget.resetModel)

    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWidget.getUseParentModel,
                                     TaurusBaseWidget.setUseParentModel,
                                     TaurusBaseWidget.resetUseParentModel)

    ledSize = Qt.pyqtProperty("int", getLedSize, setLedSize, resetLedSize,
                              doc='valid values as 24 and 48')

    boolIndex = Qt.pyqtProperty("int", getBoolIndex, setBoolIndex, resetBoolIndex)


if __name__ == "__main__":
    import sys
    app = Qt.QApplication(sys.argv)
    
    model = 'sys/tg_test/1/state'
    if len(sys.argv)>1: model=sys.argv[1]
    
    w = TaurusStateLed()
    w.setModel(model)    
    w.setVisible(True)
    
    sys.exit(app.exec_())


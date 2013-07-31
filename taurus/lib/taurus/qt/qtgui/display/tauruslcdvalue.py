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

"""This module provides a set of basic Taurus widgets based on QLCDNumber"""

__all__ = ["TaurusLCDValue"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt
from taurus.qt.qtgui.util import QT_ATTRIBUTE_QUALITY_PALETTE
from taurus.qt.qtgui.base import TaurusBaseWidget


class TaurusLCDValue(Qt.QLCDNumber, TaurusBaseWidget):
    """
       A LCD widget displaying a tango attribute value
       
       .. deprecated:: 2.0
           Use :class:`taurus.qt.qtgui.display.TaurusLCD` instead.
    """

    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, parent = None, designMode = False):
        name = self.__class__.__name__

        self.call__init__wo_kw(Qt.QLCDNumber, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        
        self.defineStyle()
    
    def defineStyle(self):
        self.setFrameShape(Qt.QFrame.Panel)
        self.setFrameShadow(Qt.QFrame.Raised)
        self.setSmallDecimalPoint(True)
        self.setMode(Qt.QLCDNumber.Dec)
        self.setSegmentStyle(Qt.QLCDNumber.Filled)
        self.updateStyle()
    
    # The minimum size of the widget (a limit for the user)
    def minimumSizeHint(self):
        return Qt.QSize(80, 40)
    
    # The default size of the widget
    #def sizeHint(self):
    #    return Qt.QSize(100, 32)
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget over writing
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def getModelClass(self):
        import taurus.core
        return taurus.core.taurusattribute.TaurusAttribute
        
    def isReadOnly(self):
        return True
        
    def getCharsToDisplayFromFormat(self,fmt):
        n = ''
        for c in fmt:
            if c == '.':
                break
            if c.isdigit():
                n += c
        return int(n)
    
    def updateStyle(self):
        n = 6
        model = self.getModelObj()
        if not model is None:
            fmt = model.getFormat()
            if fmt:
                n = self.getCharsToDisplayFromFormat(fmt)
        
        if n != self.numDigits():
            self.setNumDigits(n)
        
        self.setAutoFillBackground(self.getShowQuality())
        
        if self.getShowQuality():
            v = self.getModelValueObj()
            quality = None
            if v:
                quality = v.quality
            bg_brush, fg_brush = QT_ATTRIBUTE_QUALITY_PALETTE.qbrush(quality)
            palette = self.palette()
            palette.setBrush(Qt.QPalette.Window,bg_brush)
            palette.setBrush(Qt.QPalette.WindowText,fg_brush)
        else:
            palette = self.palette()
            palette.setBrush(Qt.QPalette.Window, Qt.Qt.white)
            palette.setBrush(Qt.QPalette.WindowText, Qt.Qt.black)
        self.update()

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
#        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
#        ret['module'] = 'taurus.qt.qtgui.display'
#        ret['group'] = 'Taurus Widgets [Old]'
#        ret['icon'] = ":/designer/lcdnumber.png"
#        return ret

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel,
                            TaurusBaseWidget.setModel,
                            TaurusBaseWidget.resetModel)
                                
    useParentModel = Qt.pyqtProperty("bool", TaurusBaseWidget.getUseParentModel,
                                     TaurusBaseWidget.setUseParentModel,
                                     TaurusBaseWidget.resetUseParentModel)
    
    showQuality = Qt.pyqtProperty("bool", TaurusBaseWidget.getShowQuality, 
                                  TaurusBaseWidget.setShowQuality,
                                  TaurusBaseWidget.resetShowQuality)

def main():
    """hello"""
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication
    
    app = Application.instance()
    owns_app = app is None
    
    if owns_app:
        import taurus.core.util.argparse
        parser = taurus.core.util.argparse.get_taurus_parser()
        parser.usage = "%prog [options] <full_attribute_name>"
        app = Application(sys.argv, cmd_line_parser=parser)
        
    args = app.get_command_line_args()

    if len(args) > 0:
        args = map(str.lower, args)
    else:
        args = [ 'sys/tg_test/1/double_scalar' ]

    w = Qt.QWidget()
    w.setAutoFillBackground(True)
    layout = Qt.QGridLayout()
    layout.setContentsMargins(0,0,0,0)
    layout.setSpacing(0)
    w.setLayout(layout)
    lcd = TaurusLCDValue(w)
    lcd.model = args[0]
    layout.addWidget(lcd)
    w.show()
    
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w
        
if __name__ == "__main__":
    main()
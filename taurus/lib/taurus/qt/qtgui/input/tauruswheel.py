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

"""This module provides a set of basic taurus widgets based on QWheelEdit"""

__all__ = ["TaurusWheelEdit" ]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt

import taurus.core
from taurus.qt.qtgui.base import TaurusBaseWritableWidget
from qwheel import QWheelEdit

class TaurusWheelEdit(QWheelEdit, TaurusBaseWritableWidget):
    __pyqtSignals__ = ('modelChanged(const QString &)',)

    def __init__(self, qt_parent = None, designMode = False):
        name = self.__class__.__name__
        self.call__init__wo_kw(QWheelEdit, qt_parent)
        self.call__init__(TaurusBaseWritableWidget, name, designMode=designMode)
        self.connect(self, Qt.SIGNAL(QWheelEdit.NumberChangedStr), self.valueChanged)
        self.connect(self, Qt.SIGNAL('returnPressed()'), self.writeValue)
        self.connect(self, Qt.SIGNAL('valueChanged'), self.updatePendingOperations)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
        
    def handleEvent(self, evt_src, evt_type, evt_value):
        if evt_type == taurus.core.taurusbasetypes.TaurusEventType.Config and not evt_value is None:
            f = evt_value.format.lower()
            if f[-1] not in ('d', 'f', 'g'):
                raise ValueError("'%s' format unsupported" % f)
            f = f.replace('g','f')
            if 'd' == f[-1]:
                dec_nb = 0
                try: total = int(f[1:-1])
                except: total = 6
            else:
                f = map(int, f[1:-1].split('.', 1))
                total = f[0]
                if len(f)>1:
                    dec_nb = f[1]
                else:
                    dec_nb = 2
            int_nb = total-dec_nb
            self.setDigitCount(int_nb=int_nb, dec_nb=dec_nb)
            try: self.setMinValue(float(evt_value.min_value))
            except: pass
            try: self.setMaxValue(float(evt_value.max_value))
            except: pass
        TaurusBaseWritableWidget.handleEvent(self, evt_src, evt_type, evt_value)
    
    def updateStyle(self):
        TaurusBaseWritableWidget.updateStyle(self)
        if self.hasPendingOperations():
            self.setStyleSheet('QWheelEdit {border: 2px solid; border-radius: 4px; border-color: blue}')
        else:
            self.setStyleSheet('QWheelEdit {border: 2px solid; border-radius: 4px; border-color: rgba(0,0,255,0)}')

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWritableWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.input'
        ret['icon'] = ":/designer/wheeledit.png"
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
    
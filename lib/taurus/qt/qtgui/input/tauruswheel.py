#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus
## 
## http://taurus-scada.org
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

import taurus
from taurus.external.qt import Qt

from  taurus.core.taurusbasetypes import TaurusEventType
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
        if evt_type == TaurusEventType.Config and evt_value is not None:
            int_part = 0
            dec_part = 1
            warning = False
            # get the minimal valid format
            format_value = self.getFormatFromValue(self._value)
            f = evt_value.format.lower()
            if f[-1] not in ('d', 'f', 'g'):
                raise ValueError("'%s' format unsupported" % f)
            f = f.replace('g','f')
            if 'd' == f[-1]:
                dec_nb = 0
                try: int_nb = int(f[1:-1])
                except: int_nb = 6
            else:
                fmap = map(int, f[1:-1].split('.', 1))
                int_nb = fmap[int_part]
                if len(fmap)>1:
                    dec_nb = fmap[dec_part]
                else:
                    dec_nb = 2
                if dec_nb < format_value[dec_part]:
                    warning = True
                    dec_nb = format_value[dec_part]

            if int_nb < format_value[int_part]:
                warning = True
                int_nb = format_value[int_part]

            if warning:
                msg = ('Invalid format for the current value '
                       '(hint: use "%s.%s%s" or more)'
                       %(int_nb, dec_nb, f[-1]))
                taurus.warning(msg)

            self.setDigitCount(int_nb=int_nb, dec_nb=dec_nb)
            try:
                self.setMinValue(float(evt_value.min_value))
            except:
                pass
            try:
                self.setMaxValue(float(evt_value.max_value))
            except:
                pass
        TaurusBaseWritableWidget.handleEvent(self, evt_src, evt_type, evt_value)

    def getFormatFromValue(self, value):
        int_part = 0
        dec_part = 1
        str_value = str(value)
        int_dec = str_value.split('.')
        int_nb = len(int_dec[int_part])
        try:
            dec_nb = len(int_dec[dec_part])
        except:
            dec_nb = 0
        return int_nb, dec_nb

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
    
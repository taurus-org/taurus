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

"""
taurusvaluestable.py: 
"""

__all__ = ["TaurusValuesTable_OLD"]

__docformat__ = 'restructuredtext'

import numpy

from taurus.qt import Qt

import PyTango

import taurus.core
from taurus.core.util.colors import ATTRIBUTE_QUALITY_PALETTE
from taurus.qt.qtgui.base import TaurusBaseWidget

class TaurusValuesTable_OLD(Qt.QTableWidget, TaurusBaseWidget):
    '''This widget gets spectra or images as model and shows a table containing
    the values in the model
    
    .. warning:: this is an old Read-only implementation of `TaurusValuesTable`. 
                 Use the newer implentation (which allows editing).
                 This one is here only for compatibility and will be eventually 
                 removed.
    '''
    
    __pyqtSignals__ = ("modelChanged(const QString &)",)
    
    def __init__(self, parent = None, designMode = False):
        name = self.__class__.__name__
        self.call__init__wo_kw(Qt.QTableWidget, parent)
        self.call__init__(TaurusBaseWidget, name, designMode=designMode)
        #@TODO add event filter once the backwards compatibility is not needed
        self.setEditTriggers(self.NoEditTriggers) #the table is non-editable by default
        self.setShowQuality(False) #by default it does not show the quality on background
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def getModelClass(self):
        return taurus.core.taurusattribute.TaurusAttribute

    def isReadOnly(self):
        return True
        
    def handleEvent(self, src, evt_type, val):
        if evt_type in [taurus.core.taurusbasetypes.TaurusEventType.Change, taurus.core.taurusbasetypes.TaurusEventType.Periodic] and val is not None:            
            values=numpy.array(val.value)
            #reshape the table
            if val.data_format == PyTango.AttrDataFormat.SPECTRUM:
                rows, columns = values.size, 1
            elif val.data_format == PyTango.AttrDataFormat.IMAGE:
                rows, columns = values.shape
            else:
                self.warning('unsupported data format %s'%str(val.data_format))
                return
            self.setRowCount(rows)
            self.setColumnCount(columns)
            
            #fill the table
            values = values.reshape(rows,columns) #make sure it is in matrix form (not a vector)
            for j in xrange(columns):
                for i in xrange(rows):
                    self.setItem(i,j,Qt.QTableWidgetItem(str(values[i,j])) ) #extremely inefficient!! #@TODO
            self.updateStyle()
            
    def eventHandle(self, *args):
        '''Only here for backwards compatibility. It will disapear soon. Not supported'''
        self.info('using deprecated event handling methods.')
        model = self.getModelObj()
        val = model.getValueObj()
        self.handleEvent(model, taurus.core.taurusbasetypes.TaurusEventType.Change, val)
        
    def updateStyle(self):
        if self.getShowQuality():
            val = self.getModelValueObj()
            quality = getattr(val, 'quality', None)
            stylesheet = "TaurusValuesTable {%s}"%ATTRIBUTE_QUALITY_PALETTE.qtStyleSheet(quality)
        else:
            stylesheet = "TaurusValuesTable {}"
        self.setStyleSheet(stylesheet)
        self.resizeColumnsToContents()
        self.horizontalHeader().setStretchLastSection(True)

    def setModel(self, model):
        if isinstance(model, Qt.QAbstractItemModel):
            return Qt.QTableWidget.setModel(self, model)
        return TaurusBaseWidget.setModel(self, model)

#    @classmethod
#    def getQtDesignerPluginInfo(cls):
#        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
#        ret['module'] = 'taurus.qt.qtgui.table'
#        ret['group'] = 'Taurus Views'
#        ret['icon'] = ":/designer/table.png"
#        return ret
                
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT property definition
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = Qt.pyqtProperty("QString", TaurusBaseWidget.getModel, 
                                TaurusBaseWidget.setModel, 
                                TaurusBaseWidget.resetModel)
    
    useParentModel = Qt.pyqtProperty("bool", 
                                         TaurusBaseWidget.getUseParentModel, 
                                         TaurusBaseWidget.setUseParentModel,
                                         TaurusBaseWidget.resetUseParentModel)
    
    showQuality = Qt.pyqtProperty("bool", 
                                      TaurusBaseWidget.getShowQuality,
                                      TaurusBaseWidget.setShowQuality,
                                      TaurusBaseWidget.resetShowQuality)


if __name__ == '__main__':
    import sys
    app = Qt.QApplication([])
    
    if len(sys.argv) == 2:
        model = sys.argv[1]
    else:
        model = 'bl97/pysignalsimulator/1/value1'
     
    w = TaurusValuesTable()
        
    w.setModel(model)
    w.setShowQuality(True)
    w.show()
    sys.exit(app.exec_())
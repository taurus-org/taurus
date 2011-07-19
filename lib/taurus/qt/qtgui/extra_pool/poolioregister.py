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
ioregisterWidgets.py: 
"""
__all__=["PoolIORegister","PoolIORegisterTV"]
from PyQt4 import Qt

from taurus.qt.qtgui.display import TaurusLabel
from taurus.core.util.eventfilters import EventValueMap
from taurus.qt.qtgui.input import TaurusValueComboBox

from taurus.qt.qtgui.panel import TaurusValue
from taurus.qt.qtgui.container import TaurusWidget
from poolmotor import LabelWidgetDragsDeviceAndAttribute
import taurus

class PoolIORegister(TaurusWidget):
    ''' A widget that displays and controls a pool IORegister device
    '''
    def __init__(self, parent = None, designMode = False):
        TaurusWidget.__init__(self, parent)
        
        self.setLayout(Qt.QHBoxLayout())
        
        #put a widget with a TaurusValue
        w = Qt.QWidget()
        w.setLayout(Qt.QGridLayout())
        self._TaurusValue = TaurusValue(parent = w, designMode = designMode)
        self._TaurusValue.setLabelWidgetClass(LabelWidgetDragsDeviceAndAttribute)
        self._TaurusValue.setLabelConfig('dev_alias')
        self._TaurusValue.setWriteWidgetClass(TaurusValueComboBox)        
        self.layout().addWidget(w)
        
        self.connect(self, Qt.SIGNAL('modelChanged(const QString &)'),self._updateTaurusValue )
        
    def _updateTaurusValue(self):
        model = self.getModelName()
        self._TaurusValue.setModel("%s/value" % model)

        # Get the labels from the device
        labels = 'VERY_BAD:10 BAD:30 NORMAL:50 GOOD:70 VERY_GOOD:90'
        labels = self.getModelObj().getAttribute('Labels').read().value
        print labels
        labels_list = labels.split(' ')

        # Update the mappings for the read and write widgets
        self.readEventValueMap = EventValueMap()
        self.writeValueNames = []
        
        for label_and_value in labels_list:
            label, value = label_and_value.split(':')
            self.readEventValueMap[value] = label
            self.writeValueNames.append((label, value))
        
        self._TaurusValue.readWidget().setEventFilters([self.readEventValueMap])
        self._TaurusValue.writeWidget().clear()
        self._TaurusValue.writeWidget().addValueNames(self.writeValueNames)

        # Make sure autoapply is set
        self._TaurusValue.writeWidget().setAutoApply(True)

        print type(self.getModelObj())
        print type(self.getModelObj().getHWObj())

if __name__ == '__main__':
    import sys
    app = Qt.QApplication(sys.argv)
    
    form = PoolIORegister()

    model = 'tango://controls02:10000/ioregister/gc_tgiorctrl/1'
    if len(sys.argv)>1:
        model = sys.argv[1]
    form.setModel(model)
    
     
    form.show()
    sys.exit(app.exec_())

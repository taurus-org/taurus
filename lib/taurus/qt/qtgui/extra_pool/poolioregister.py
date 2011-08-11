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
poolioregister.py: 
"""
__all__=["PoolIORegister"]
from PyQt4 import Qt

from taurus.qt.qtgui.display import TaurusLabel
from taurus.core.util.eventfilters import EventValueMap
from taurus.qt.qtgui.input import TaurusValueComboBox

from taurus.qt.qtgui.panel import TaurusValue
from taurus.qt.qtgui.container import TaurusWidget
from poolmotor import LabelWidgetDragsDeviceAndAttribute
import taurus

class PoolIORegisterReadWidget(TaurusLabel):
    ''' This class is intended to be used as a read widget of a TaurusValue with IORegister devices.
    After setting the model, it gets the Labels and creates a filter to show them instead of the values.
    '''
    def __init__(self, parent=None, designMode=False):
        TaurusLabel.__init__(self, parent, designMode)

    def setModel(self, model):
        TaurusLabel.setModel(self, '%s/value' % model) #@todo: change this (it assumes tango naming!)

        try: ior_dev = taurus.Device(model)
        except: return
        labels = ior_dev.getAttribute('Labels').read().value
        labels_list = labels.split(' ')

        # Update the mapping
        self.readEventValueMap = EventValueMap()
        for label_and_value in labels_list:
            label, value = label_and_value.split(':')
            self.readEventValueMap[int(value)] = label
        self.setEventFilters([self.readEventValueMap])

class PoolIORegisterWriteWidget(TaurusValueComboBox):
    ''' This class is intended to be used as a write widget of a TaurusValue with IORegister devices.
    After setting the model, it gets the Labels and populates the combobox. It has AutoApply set to True.
    '''
    def __init__(self, parent=None, designMode=False):
        TaurusValueComboBox.__init__(self, parent, designMode)
        self.setAutoApply(True)

    def setModel(self, model):
        TaurusValueComboBox.setModel(self, '%s/value' % model) #@todo: change this (it assumes tango naming!)

        try: ior_dev = taurus.Device(model)
        except: return

        labels = ior_dev.getAttribute('Labels').read().value
        labels_list = labels.split(' ')
            
        # Update the mapping
        self.writeValueNames = []
        for label_and_value in labels_list:
            label, value = label_and_value.split(':')
            self.writeValueNames.append((label, value))

        self.setValueNames(self.writeValueNames)

class PoolIORegister(TaurusValue):
    ''' A widget that displays and controls a pool channel device.  It
    behaves as a TaurusValue.
    '''
    def __init__(self, parent = None, designMode = False):
        TaurusValue.__init__(self, parent = parent, designMode = designMode)
        self.setLabelWidgetClass(LabelWidgetDragsDeviceAndAttribute)
        self.setLabelConfig('dev_alias')
        self.setReadWidgetClass(PoolIORegisterReadWidget)
        self.setWriteWidgetClass(PoolIORegisterWriteWidget)


if __name__ == '__main__':
    import sys
    app = Qt.QApplication(sys.argv)
    
    from taurus.qt.qtgui.panel import TaurusForm
    tgclass_map = {'IORegister':PoolIORegister}
    form = TaurusForm()
    form.setCustomWidgetMap(tgclass_map)
    model = 'tango://controls02:10000/ioregister/gc_tgiorctrl/1'
    if len(sys.argv)>1:
        model = sys.argv[1]

    form.setModel([model])
    form.show()

    sys.exit(app.exec_())

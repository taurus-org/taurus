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

from ui_poolioregisterbuttons import Ui_PoolIORegisterButtons
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

    # FILTERS ARE NOT WORKING AS OF SVN:17541
    # SO I RE-IMPLEMENT getFormatedToolTip for this purpose
    def getFormatedToolTip(self, cache=True):
        taurus_label_tooltip = TaurusLabel.getFormatedToolTip(self, cache)
        value = int(self.getDisplayValue())
        label = self.readEventValueMap[value]
        extended_tooltip = '%d: %s' % (value, label)
        return taurus_label_tooltip + '<HR>' + extended_tooltip

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
    ''' A widget that displays and controls a pool IORegister device.  It
    behaves as a TaurusValue.
    '''
    def __init__(self, parent = None, designMode = False):
        TaurusValue.__init__(self, parent = parent, designMode = designMode)
        self.setLabelWidgetClass(LabelWidgetDragsDeviceAndAttribute)
        self.setLabelConfig('dev_alias')
        self.setReadWidgetClass(PoolIORegisterReadWidget)
        self.setWriteWidgetClass(PoolIORegisterWriteWidget)



from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtgui.display import TaurusConfigLabel

class PoolIORegisterButtons(TaurusWidget):
    ''' A widget that displays and controls a pool IORegister device.
    It reads the value and provides buttons to switch between values.
    NOTE: It would be nice to provide 'ABORT' button if the device allows it.
    NOTE: It would be nice to set icons for each possible value label.
    '''
    def __init__(self, parent = None, designMode = False):
        TaurusWidget.__init__(self, parent, designMode)

        self.ui = Ui_PoolIORegisterButtons()
        self.ui.setupUi(self)

        self.alias_label = TaurusConfigLabel()
        self.value_label = PoolIORegisterReadWidget()
        self.button_value_dict = {}

        policy = self.value_label.sizePolicy()
        policy.setHorizontalPolicy(Qt.QSizePolicy.Expanding)
        self.value_label.setSizePolicy(policy)

        self.ui.lo_state_read.addWidget(self.alias_label)
        self.ui.lo_state_read.addWidget(self.value_label)

        self.ior_dev = None


    def setModel(self, model):
        self.ior_dev = None
        try: self.ior_dev = taurus.Device(model)
        except: return

        self.alias_label.setModel('%s/State?configuration=dev_alias' % model)
        self.value_label.setModel(model)

        # Empty previous buttons
        #self.ui.lo_buttons_write.
        for button in self.button_value_dict.keys():
            self.disconnect(button, Qt.SIGNAL('clicked'), self.writeValue)
            button.deleteLater()
        self.button_value_dict = {}

        labels = self.ior_dev.getAttribute('Labels').read().value
        labels_list = labels.split(' ')
        # Update the mapping
        for label_and_value in labels_list:
            label, value = label_and_value.split(':')
            button = Qt.QPushButton(label)
            self.button_value_dict[button] = value
            self.ui.lo_buttons_write.addWidget(button)
            self.connect(button, Qt.SIGNAL('clicked()'), self.writeValue)

    def writeValue(self):
        if self.ior_dev is None:
            return
        button = self.sender()
        value = self.button_value_dict[button]
        self.ior_dev.getAttribute('Value').write(value)


def test_form():
    from taurus.qt.qtgui.panel import TaurusForm
    tgclass_map = {'IORegister':PoolIORegister}
    form = TaurusForm()
    form.setCustomWidgetMap(tgclass_map)
    model = 'tango://controls02:10000/ioregister/gc_tgiorctrl/1'
    if len(sys.argv)>1:
        model = sys.argv[1]

    form.setModel([model])
    form.show()
    
def test_buttons():
    w = PoolIORegisterButtons()
    model = 'tango://controls02:10000/ioregister/gc_tgiorctrl/1'
    if len(sys.argv)>1:
        model = sys.argv[1]

    w.setModel(model)
    w.show()

if __name__ == '__main__':
    import sys
    app = Qt.QApplication(sys.argv)

    #test_form()
    test_buttons()

    sys.exit(app.exec_())

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
channelWidgets.py: 
"""
__all__=["PoolChannel","PoolChannelTV"]
from taurus.qt import Qt

from taurus.qt.qtgui.panel import TaurusValue, TaurusDevButton
from taurus.qt.qtgui.container import TaurusWidget
from poolmotor import LabelWidgetDragsDeviceAndAttribute
import taurus

       
class _ParentDevButton(TaurusDevButton):
    '''A TaurusDevButton that receives an attribute name but sets 
    the corresponding device as model. **For internal use only** '''
    def __init__(self, **kwargs):
        TaurusDevButton.__init__(self, **kwargs)
        self.setText('')
        self.setSizePolicy(Qt.QSizePolicy.Preferred, Qt.QSizePolicy.Maximum)
        
    def setModel(self, model):
        try: attr = taurus.Attribute(model)
        except: return
        dev = attr.getParentObj()
        devname = dev.getFullName()
        TaurusDevButton.setModel(self, devname)
        
        
class PoolChannelTV(TaurusValue):
    ''' A widget that displays and controls a pool channel device.
    It differs from :class:`PoolChannel` in that it behaves as a TaurusValue 
    (i.e., it allows its subwidgets to be aligned in columns in a TaurusForm)`
    '''
    def __init__(self, parent = None, designMode = False):
        TaurusValue.__init__(self, parent = parent, designMode = designMode)
        self.setLabelWidgetClass("LabelWidgetDragsDeviceAndAttribute")
        self.setLabelConfig('dev_alias')
    
    def getDefaultExtraWidgetClass(self):
        return _ParentDevButton
        
    def setModel(self,model):
        if model is not None:
            model = "%s/value"%model #@todo: change this (it assumes tango naming!)
        TaurusValue.setModel(self, model)

    def showEvent(self, event):
        TaurusValue.showEvent(self, event)
        try: self.getModelObj().getParentObj().getAttribute('Value').enablePolling(force=True)
        except: pass

    def hideEvent(self, event):
        TaurusValue.hideEvent(self, event)
        try: self.getModelObj().getParentObj().getAttribute('Value').disablePolling()
        except: pass



class PoolChannel(TaurusWidget):
    ''' A widget that displays and controls a pool channel device
    
    .. seealso:: :class:`PoolChannelTV`
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
        self.layout().addWidget(w)
        
        #...and a dev button next to the widget
        self._devButton = TaurusDevButton(parent = self, designMode = designMode)
        self._devButton.setText('')
        self.layout().addWidget(self._devButton)
        
        self.connect(self, Qt.SIGNAL('modelChanged(const QString &)'),self._updateTaurusValue )
        
    def _updateTaurusValue(self):
        m=self.getModelName()
        self._TaurusValue.setModel("%s/value"%m)
        self._devButton.setModel(m)
        

#if __name__ == '__main__':
#    import sys
#    app = Qt.QApplication(sys.argv)
#    
#    form = PoolChannel()
#
#    #model = 'tango://controls02:10000/expchan/bl97_simucotictrl_1/1'
#    model = 'ct_cp1_1'
#    if len(sys.argv)>1:
#        model = sys.argv[1]
#    form.setModel(model)
#    
#     
#    form.show()
#    sys.exit(app.exec_())

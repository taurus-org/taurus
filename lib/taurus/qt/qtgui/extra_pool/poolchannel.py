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

from PyQt4 import Qt

from taurus.qt.qtgui.panel import TaurusValue, TaurusDevButton
from taurus.qt.qtgui.container import TaurusWidget
from poolmotor import LabelWidgetDragsDeviceAndAttribute


class PoolChannel(TaurusWidget):
    ''' A widget that displays and controls a pool channel device'''
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
        

if __name__ == '__main__':
    import sys
    app = Qt.QApplication(sys.argv)
    
    form = PoolChannel()

    model = 'tango://controls02:10000/expchan/bl97_simucotictrl_1/1'
    if len(sys.argv)>1:
        model = sys.argv[1]
    form.setModel(model)
    
     
    form.show()
    sys.exit(app.exec_())
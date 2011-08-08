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

"""This module provides a base widget that can be used to display a taurus 
model in a table widget"""

__all__ = ["MntGrpChannelEditor", "MntGrpChannelPanel"]

__docformat__ = 'restructuredtext'

from PyQt4 import Qt

from taurus.qt.qtcore.model import TaurusBaseTreeItem
from taurus.qt.qtgui.resource import getIcon, getThemeIcon
from expdescription import ChannelCollectionModel, ChannelCollectionEditor

class MntGrpUnitItem(TaurusBaseTreeItem):
    pass

class MntGrpChannelModel(ChannelCollectionModel):
    
    def setDataSource(self, mg):
        if self._data_src is not None:
            Qt.QObject.disconnect(self._data_src, Qt.SIGNAL('configurationChanged'), self.configurationChanged)
        if mg is not None:
            Qt.QObject.connect(mg, Qt.SIGNAL('configurationChanged'), self.configurationChanged)
        ChannelCollectionModel.setDataSource(self, mg)

    def configurationChanged(self):
        self.refresh()

    def setupModelData(self, mg):
        if mg is None:
            return
            
        # create a local editable copy of the configuration
        cfg = dict(self.getSourceData())
#        from taurus.qt.qtcore.tango.sardana.macroserver import  DUMMY_MNGRPCFG_1
#        cfg = dict(DUMMY_MNGRPCFG_1)
        
        root = self._rootItem #@The root could eventually be changed for each unit or controller
        channelNodes = {}
        for ctrl_name, ctrl_data in cfg['controllers'].items():
            for unit_id, unit_data in ctrl_data['units'].items():
                ChannelCollectionModel.setupModelData(self, unit_data['channels'], root=root)
        self._localData = cfg
    
    def writeSourceData(self):
        mg = self.dataSource()
        if mg is not None and self._localData is not None: 
            mg.setConfiguration(self._localData)
    
    def getSourceData(self):
        """Gets data from the dataSource"""
        mg = self.dataSource()
        if mg is not None:
            return mg.getConfiguration()


class MntGrpChannelEditor(ChannelCollectionEditor):
    """
    """
    KnownPerspectives = {
        "Channel" : {
            "label"   : "Channels",
            "icon"    : "system-shutdown",
            "tooltip" : "View by channel",
            "model"   : [MntGrpChannelModel,],
        },
    }


class MntGrpChannelPanel(Qt.QWidget):
    
    def __init__(self, parent=None):
        Qt.QWidget.__init__(self, parent)
        l = Qt.QVBoxLayout()
        l.setContentsMargins(0,0,0,0)
        self.setLayout(l)
        self._editor = ChannelCollectionEditor(parent=self)
#        self._editor = MntGrpChannelEditor(parent=self)
        self.connect(self._editor.getQModel(),
                     Qt.SIGNAL("dataChanged(const QModelIndex &, const QModelIndex &)"),
                     self.onDataChanged)
        self.connect(self._editor.getQModel(),
                     Qt.SIGNAL("modelReset()"),
                     self.onDataReset)
        self._editor.show()
        l.addWidget(self._editor, 1)
        BB = Qt.QDialogButtonBox
        bts = BB.Ok | BB.Cancel | BB.Reset | BB.Apply
        bb = self._buttonBox = Qt.QDialogButtonBox(bts, Qt.Qt.Horizontal, self)
        self.connect(bb, Qt.SIGNAL("clicked(QAbstractButton *)"),
                     self.onDialogButtonClicked)
        l.addWidget(self._buttonBox, 0, Qt.Qt.AlignRight)

    def getEditor(self):
        return self._editor

    def setModel(self, m):
        self.getEditor().setModel(m)
    
    def getEditorQModel(self):
        return self.getEditor().getQModel()

    def onDialogButtonClicked(self, button):
        role = self._buttonBox.buttonRole(button)
        qmodel = self.getEditorQModel()
        if role == Qt.QDialogButtonBox.ApplyRole:
            qmodel.writeSourceData()
        elif role == Qt.QDialogButtonBox.ResetRole:
            qmodel.refresh()

    def onDataChanged(self, i1, i2):
        self._updateButtonBox()
    
    def onDataReset(self):
        self._updateButtonBox()
    
    def _updateButtonBox(self):
        qmodel = self.getEditorQModel()
        changed = qmodel.isDataChanged()
        bb = self._buttonBox
        for button in bb.buttons():
            role = bb.buttonRole(button)
            if role == Qt.QDialogButtonBox.ApplyRole:
                button.setEnabled(changed)
            elif role == Qt.QDialogButtonBox.ResetRole:
                button.setEnabled(changed)


def main_MntGrpChannelPanel(mg, perspective="Channel"):
    w = MntGrpChannelPanel()
    w.setWindowIcon(getThemeIcon("system-shutdown"))
    w.setWindowTitle("A Taurus Sardana measurement group Example")
    w.setModel(mg)
    w.show()
    return w


def demo(model="mg2"):
    """Table panels"""
    w = main_MntGrpChannelPanel(model)
    return w


def main():
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication
    
    app = Application.instance()
    owns_app = app is None
    
    if owns_app:
        app = Application(app_name="Meas. group channel demo", app_version="1.0",
                          org_domain="Sardana", org_name="Tango community")
    
    args = app.get_command_line_args()
    if len(args)==1:
        w = demo(model=args[0])
    else:
        w = demo()
    w.show()
    
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w
    
if __name__ == "__main__":
    main()

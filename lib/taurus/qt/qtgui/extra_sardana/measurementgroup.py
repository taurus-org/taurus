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

import taurus
from taurus.core import TaurusElementType
from taurus.core.util import Enumeration
from taurus.qt.qtcore.model import *
from taurus.qt.qtgui.model import TaurusBaseModelWidget, EditorToolBar
from taurus.qt.qtgui.resource import getIcon, getThemeIcon
from taurus.qt.qtgui.util import ActionFactory
from taurus.qt.qtgui.table import TaurusBaseTableWidget

ChannelView = Enumeration("ChannelView", ("Channel", "Enabled", "Output", "Plottable", "Unknown"))

PlotAxis = Enumeration("PlotAxis", ("y1", "y2", "x"))
                       
def getElementTypeIcon(t):
    if t == ChannelView.Channel:
        return getThemeIcon("system-shutdown")
    elif t == ChannelView.Enabled:
        return getIcon(":/status/true.svg")
    elif t == ChannelView.Output:
        return getThemeIcon("utilities-terminal")
    elif t == ChannelView.Plottable:
        return getThemeIcon("utilities-system-monitor")
        
    return getIcon(":/tango.png")
    
def getElementTypeSize(t):
    if t == ChannelView.Channel:
        return Qt.QSize(200,24)
    elif t == ChannelView.Enabled:
        return Qt.QSize(50,24)
    elif t == ChannelView.Output:
        return Qt.QSize(50,24)
    elif t == ChannelView.Plottable:
        return Qt.QSize(50,24)
    return Qt.QSize(50,24)

def getElementTypeToolTip(t):
    """Wrapper to prevent loading qtgui when this module is imported"""
    if t == ChannelView.Channel:
        return "Channel"
    elif t == ChannelView.Enabled:
        return "Channel active or not"
    elif t == ChannelView.Output:
        return "Channel output active or not"
    elif t == ChannelView.Plottable:
        return "Channel plotting configuration"
    return "Unknown"

class MntGrpBaseChannelItem(TaurusBaseTreeItem):
    """ """
    def data(self, index):
        """Returns the data of this node for the given index
        
        :return: (object) the data for the given index
        """
        return self._itemData
    
    def role(self):
        """Returns the prefered role for the item.
        This implementation returns taurus.core.TaurusElementType.Unknown
        
        This method should be able to return any kind of python object as long
        as the model that is used is compatible.
        
        :return: (MacroView) the role in form of element type"""
        return ChannelView.Unknown


class MntGrpUnitItem(TaurusBaseTreeItem):
    pass


class MntGrpChannelItem(MntGrpBaseChannelItem):
    
    def data(self, index):
        """Returns the data of this node for the given index
        
        :return: (object) the data for the given index
        """
        taurus_role = index.model().role(index.column())
        ch_name, ch_data = self.itemData()
        
        if taurus_role == ChannelView.Channel:
            return ch_data['label']
        elif taurus_role == ChannelView.Enabled:
            return ch_data['enabled']
        elif taurus_role == ChannelView.Output:
            return ch_data['output']
        elif taurus_role == ChannelView.Plottable:
            return ch_data['plottable']

    def setData(self, index, data):
        taurus_role = index.model().role(index.column())
        ch_name, ch_data = self.itemData()
        
        if taurus_role == ChannelView.Channel:
            ch_data['label'] = str(data)
        elif taurus_role == ChannelView.Enabled:
            ch_data['enabled'] = data
        elif taurus_role == ChannelView.Output:
            ch_data['output'] = data
        elif taurus_role == ChannelView.Plottable:
            ch_data['plottable'] = data

    def role(self):
        return ChannelView.Channel

    def toolTip(self, index):
        return "Channel " + self._itemData[0]

    def icon(self, index):
        taurus_role = index.model().role(index.column())
        if taurus_role == ChannelView.Channel:
            return getThemeIcon("system-shutdown")
        

class MntGrpChannelModel(TaurusBaseModel):

    ColumnNames = "Channel", "", "", ""
    ColumnRoles = (ChannelView.Channel, ChannelView.Channel), ChannelView.Enabled, ChannelView.Output, ChannelView.Plottable

    def __init__(self, parent=None, data=None):
        TaurusBaseModel.__init__(self, parent=parent, data=data)
        self._config = None
        self._dirty = False
        
    def setDataSource(self, mg):
        if self._data_src is not None:
            Qt.QObject.disconnect(self._data_src, Qt.SIGNAL('configurationChanged'), self.configurationChanged)
        if mg is not None:
            Qt.QObject.connect(mg, Qt.SIGNAL('configurationChanged'), self.configurationChanged)
        TaurusBaseModel.setDataSource(self, mg)

    def configurationChanged(self):
        self.refresh()

    def createNewRootItem(self):
        return MntGrpBaseChannelItem(self, self.ColumnNames)

    def roleIcon(self, taurus_role):
        return getElementTypeIcon(taurus_role)

    def roleSize(self, taurus_role):
        return getElementTypeSize(taurus_role)

    def roleToolTip(self, taurus_role):
        return getElementTypeToolTip(taurus_role)

    def setupModelData(self, mg):
        if mg is None:
            return
        root = self._rootItem
        
        # create a local editable copy of the configuration
        self._config = cfg = dict(self.getSourceData())
        self._dirty = False
        
        channelNodes = {}
        for ctrl_name, ctrl_data in cfg['controllers'].items():
            for unit_id, unit_data in ctrl_data['units'].items():
                for channel_name, channel_data in unit_data['channels'].items():
                    channelNode = MntGrpChannelItem(self, (channel_name, channel_data), root)
                    channelNodes[channel_data['index']] = channelNode
        
        for channel_id in sorted(channelNodes):
            root.appendChild(channelNodes[channel_id])

    def setData(self, index, qvalue, role=Qt.Qt.EditRole):
        ret = self._setData(index, qvalue, role)
        if ret is True:
            self._dirty = True
            self.emit(Qt.SIGNAL("dataChanged(const QModelIndex &, const QModelIndex &)"),
                      index, index)
        return ret
    
    def flags(self, index):
        flags = TaurusBaseModel.flags(self, index)
        flags |= Qt.Qt.ItemIsEditable
        return flags

    def getSourceData(self):
        """Gets data from the dataSource"""
        mg = self.dataSource()
        if mg is not None:
            return mg.getConfiguration()

    def getLocalData(self):
        """Gets the local data (may be different from the one in the data source
        (server) since it may have been modified by the user)"""
        return self._config
    
    def isDataChanged(self):
        """Tells if the local data has been modified since it was last refreshed
        from the data source (server)"""
        return self._dirty
    
    def writeSourceData(self):
        mg = self.dataSource()
        if mg is not None and self._config is not None: 
            mg.setConfiguration(self._config)


class ChannelDelegate(Qt.QStyledItemDelegate):
    
    def createEditor(self, parent, option, index):
        taurus_role = index.model().role(index.column())
        t = Qt.QVariant.Bool
        if taurus_role == ChannelView.Channel:
            t = Qt.QVariant.String
        return self.itemEditorFactory().createEditor(t, parent)
    
    def setEditorData(self, editor, index):
        model = index.model()
        data = model.data(index, Qt.Qt.EditRole)
        pydata = data.toPyObject()
        taurus_role = model.role(index.column())
        if taurus_role == ChannelView.Channel:
            editor.setText(pydata)
        else:
            if pydata:
                editor.setCurrentIndex(1)
            else:
                editor.setCurrentIndex(0)
        
    def setModelData(self, editor, model, index):
        Qt.QStyledItemDelegate.setModelData(self, editor, model, index)


class MntGrpChannelEditor(TaurusBaseTableWidget):
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

    DftPerspective = "Channel"
    
    def createViewWidget(self):
        tableView = TaurusBaseTableWidget.createViewWidget(self)
        self._delegate = ChannelDelegate(self)
        self._delegate.setItemEditorFactory(Qt.QItemEditorFactory())
        tableView.setItemDelegate(self._delegate)
        tableView.setSortingEnabled(False)
        return tableView

    def createToolArea(self):
        ta = TaurusBaseTableWidget.createToolArea(self)
        e_bar = self._editorBar = EditorToolBar(self, self)
        ta.append(e_bar)
        return ta

    def getModelClass(self):
        return taurus.core.TaurusDevice
    
    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseTableWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.extra_sardana'
        ret['group'] = 'Taurus Extra Sardana'
        ret['icon'] = ":/designer/table.png"
        return ret


class MntGrpChannelPanel(Qt.QWidget):
    
    def __init__(self, parent=None):
        Qt.QWidget.__init__(self, parent)
        l = Qt.QVBoxLayout()
        l.setContentsMargins(0,0,0,0)
        self.setLayout(l)
        self._editor = MntGrpChannelEditor(parent=self)
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
    

def main_MntGrpChannelEditor(mg, perspective="Channel"):
    w = MntGrpChannelEditor(perspective=perspective)
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
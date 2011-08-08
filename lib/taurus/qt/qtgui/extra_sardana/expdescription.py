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

"""This module provides widget for configuring the data acquisition and display of an experiment"""

__all__ = ["ChannelCollectionEditor", "ExpDescriptionPanel"]

__docformat__ = 'restructuredtext'

from PyQt4 import Qt

import taurus
from taurus.core.util import Enumeration
from taurus.qt.qtcore.model import TaurusBaseTreeItem, TaurusBaseModel
from taurus.qt.qtgui.model import EditorToolBar
from taurus.qt.qtgui.resource import getIcon, getThemeIcon
from taurus.qt.qtgui.table import TaurusBaseTableWidget


#===============================================================================
# some dummydict for developing the "Experimental Configuration widget"
# This block is to be removed and the dictionaries will be defined and 
# initialized in Sardana's Door code  


# dict <str, obj> with (at least) keys:
#    - 'timer' : the timer channel name / timer channel id
#    - 'monitor' : the monitor channel name / monitor channel id
#    - 'controllers' : dict<Controller, dict> where:
#        - key: ctrl
#        - value: dict<str, dict> with (at least) keys:
#            - 'units': dict<str, dict> with (at least) keys:
#                - 'id' : the unit ID inside the controller
#                - 'timer' : the timer channel name / timer channel id
#                - 'monitor' : the monitor channel name / monitor channel id
#                - 'trigger_type' : 'Gate'/'Software'
#                - 'channels' where value is a dict<str, obj> with (at least) keys:
#                    - 'index' : int indicating the position of the channel in the measurement group
#                    - 'id' : the channel name ( channel id )
#                    optional keys:
#                    - 'enabled' : True/False (default is True)
#                    any hints:
#                    - 'output' : True/False (default is True)
#                    - 'plot_type' : 'No'/'1D'/'2D' (default is 'No')
#                    - 'plot_axes' : list<str> 'where str is channel name/'step#/'index#' (default is [])
#                    - 'label' : prefered label (default is channel name)
#                    - 'scale' : <float, float> with min/max (defaults to channel
#                                range if it is defined
#                    - 'plot_color' : int representing RGB
#    optional keys:
#    - 'label' : measurement group label (defaults to measurement group name)
#    - 'description' : measurement group description

DUMMY_CHANNELCFG_1 = {u'index': 0, 
                      u'plot_type': u'No', 
                      u'enabled': True, 
                      u'label': u'BL96_CT1', 
                      u'plot_axes': [], 
                      u'output': True}

DUMMY_CHANNELCFG_2 = {u'index': 1, 
                      u'plot_type': u'2D', 
                      u'enabled': True, 
                      u'label': u'BL96_CT2', 
                      u'plot_axes': [], 
                      u'output': True}

DUMMY_CHANNELCONFIGS = {u'BL96_CT1': DUMMY_CHANNELCFG_1, 
                        u'BL96_CT2': DUMMY_CHANNELCFG_2
                       } 
 
DUMMY_MNGRPCFG_1 = \
{u'monitor': u'BL96_CT1',
 u'description': u'General purpose measurement group', 
 u'timer': u'BL96_CT1', 
 u'label': u'bl96_mntgrp1',
 u'controllers': {u'BL96_DummyCounterTimerController1': {u'units': {u'0': {u'monitor': u'BL96_CT1', 
                                                                           u'id': 0, 
                                                                           u'timer': u'BL96_CT1', 
                                                                           u'trigger_type': 0,
                                                                           u'channels': DUMMY_CHANNELCONFIGS 
                                                                           }}}}
 }


DUMMY_MNTGRPCONFIGS = {'bl96_mntgrp1':DUMMY_MNGRPCFG_1}

DUMMY_EXP_CONF = {'ScanDir':'/tmp/scandir',
                  'ScanFile':'dummyscan.h5',
                  'ActiveMntGrp':'bl96_mntgrp1',
                  'MntGrpConfigs': DUMMY_MNTGRPCONFIGS
                  }
#
#===============================================================================

ChannelView = Enumeration("ChannelView", ("Channel", "Enabled", "Output", "PlotType", "PlotAxes", "Unknown"))

PlotType = Enumeration("PlotType", ("No", "1D", "2D"))

                       
def getElementTypeIcon(t):
    if t == ChannelView.Channel:
        return getThemeIcon("system-shutdown")
    elif t == ChannelView.Enabled:
        return getIcon(":/status/true.svg")
    elif t == ChannelView.Output:
        return getThemeIcon("utilities-terminal")
    elif t == ChannelView.PlotType:
        return getThemeIcon("utilities-system-monitor")
        
    return getIcon(":/tango.png")

    
def getElementTypeSize(t):
    if t == ChannelView.Channel:
        return Qt.QSize(200,24)
    elif t == ChannelView.Enabled:
        return Qt.QSize(50,24)
    elif t == ChannelView.Output:
        return Qt.QSize(50,24)
    elif t == ChannelView.PlotType:
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
    elif t == ChannelView.PlotType:
        return "Plot type for this channel "
    elif t == ChannelView.PlotAxes:
        return "Independent variables to be used in the plot of this channel"
    return "Unknown"


class BaseChannelCollectionItem(TaurusBaseTreeItem):
    """ """
    def data(self, index):
        """Returns the data of this node for the given index
        
        :return: (object) the data for the given index
        """
        return self._itemData
    
    def role(self):
        """Returns the prefered role for the item.
        This implementation returns ChannelView.Unknown
        
        This method should be able to return any kind of python object as long
        as the model that is used is compatible.
        
        :return: (MacroView) the role in form of element type"""
        return ChannelView.Unknown


class ChannelCollectionItem(BaseChannelCollectionItem):
    
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
        elif taurus_role == ChannelView.PlotType:
            return ch_data['plot_type']
        elif taurus_role == ChannelView.PlotAxes:
            if ch_data['plot_type'] == PlotType.No:
                return None
            return "foo"#ch_data['plot_axes']

    def setData(self, index, data):
        taurus_role = index.model().role(index.column())
        ch_name, ch_data = self.itemData()
        
        if taurus_role == ChannelView.Channel:
            ch_data['label'] = str(data)
        elif taurus_role == ChannelView.Enabled:
            ch_data['enabled'] = data
        elif taurus_role == ChannelView.Output:
            ch_data['output'] = data
        elif taurus_role == ChannelView.PlotType:
            ch_data['plot_type'] = data
        elif taurus_role == ChannelView.PlotAxes:
            ch_data['plot_axes'] = data

    def role(self):
        return ChannelView.Channel

    def toolTip(self, index):
        return "Channel " + self._itemData[0]

    def icon(self, index):
        taurus_role = index.model().role(index.column())
        if taurus_role == ChannelView.Channel:
            return getThemeIcon("system-shutdown")
        
        
class ChannelCollectionModel(TaurusBaseModel):
    ColumnNames = "Channel", "enabled", "output", "Plot Type", "Plot Axes"
    ColumnRoles = (ChannelView.Channel, ChannelView.Channel), ChannelView.Enabled, ChannelView.Output, ChannelView.PlotType, ChannelView.PlotAxes

    def __init__(self, parent=None, data=None):
        TaurusBaseModel.__init__(self, parent=parent, data=data)
        self._config = None
        self._dirty = False    
    
    def createNewRootItem(self):
        return BaseChannelCollectionItem(self, self.ColumnNames)
    
    def roleIcon(self, taurus_role):
        return getElementTypeIcon(taurus_role)

    def roleSize(self, taurus_role):
        return getElementTypeSize(taurus_role)

    def roleToolTip(self, taurus_role):
        return getElementTypeToolTip(taurus_role)
    
    def setupModelData(self, channelsdata, root=None):
        if channelsdata is None:
            return
        if root is None:
            root = self._rootItem
        # create a local editable copy of the data
        self._localData = localData = dict(channelsdata)
        self._dirty = False
        channelNodes = {}
        for channel_name, channel_data in localData.items():
            channelNode = ChannelCollectionItem(self, (channel_name, channel_data), root)
            channelNodes[channel_data['index']] = channelNode
                
        for channel_id in sorted(channelNodes):
            root.appendChild(channelNodes[channel_id])
    
    def getLocalData(self):
        """Gets the local data (may be different from the one in the data source
        since it may have been modified by the user)"""
        return self._localData
    
    def isDataChanged(self):
        """Tells if the local data has been modified since it was last refreshed
        set by a setupModelData call"""
        return self._dirty

    def flags(self, index):
        flags = TaurusBaseModel.flags(self, index)
        flags |= Qt.Qt.ItemIsEditable
        return flags
    
    def setData(self, index, qvalue, role=Qt.Qt.EditRole):
        ret = self._setData(index, qvalue, role)
        if ret is True:
            self._dirty = True
            self.emit(Qt.SIGNAL("dataChanged(const QModelIndex &, const QModelIndex &)"),
                      index, index)
        return ret

    
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


class ChannelDelegate(Qt.QStyledItemDelegate):
    
    def createEditor(self, parent, option, index):
        taurus_role = index.model().role(index.column())
        if taurus_role == ChannelView.Channel:
            t = Qt.QVariant.String
            ret = self.itemEditorFactory().createEditor(t, parent)
        elif  taurus_role == ChannelView.PlotType:
            ret = Qt.QComboBox(parent)
            ret.addItems(PlotType.keys())
        else:
            t = Qt.QVariant.Bool 
            ret = self.itemEditorFactory().createEditor(t, parent)
        ret.setAutoFillBackground(True)
        return ret
    
    def setEditorData(self, editor, index):
        model = index.model()
        data = model.data(index, Qt.Qt.EditRole)
        
        pydata = data.toPyObject()
        taurus_role = model.role(index.column())
        if taurus_role == ChannelView.Channel:
            editor.setText(pydata)
        elif taurus_role == ChannelView.PlotType:
            pass #@todo
        else:
            if pydata:
                editor.setCurrentIndex(1)
            else:
                editor.setCurrentIndex(0)
        
    def setModelData(self, editor, model, index):
        taurus_role = model.role(index.column())
        if taurus_role == ChannelView.PlotType:
            data = Qt.QVariant(editor.currentText())
            model.setData(index, data)
        else:
            Qt.QStyledItemDelegate.setModelData(self, editor, model, index)


class ChannelCollectionEditor(TaurusBaseTableWidget):
    """
    """
    
    KnownPerspectives = {
        "Channel" : {
            "label"   : "Channels",
            "icon"    : "system-shutdown",
            "tooltip" : "View by channel",
            "model"   : [ChannelCollectionModel,],
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


def main_ChannelEditor(perspective="Channel"):
    w = ChannelCollectionEditor( perspective=perspective)
    w.setWindowTitle("A Taurus Sardana channel editor example")
    #data=DUMMY_MNGRPCFG_1['controllers']['BL96_DummyCounterTimerController1']['units']['0']['channels']
    w.getQModel().setDataSource(DUMMY_CHANNELCONFIGS)
    w.show()
    return w
  
            
def demo(model="mydoor"):
    """Table panels"""
    w = main_ChannelEditor()
    return w


def main():
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication
    
    app = Application.instance()
    owns_app = app is None
    
    if owns_app:
        app = Application(app_name="Exp. Description demo", app_version="1.0",
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

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
import copy
import taurus
from taurus.core.util import Enumeration
from taurus.qt.qtcore.model import TaurusBaseTreeItem, TaurusBaseModel
from taurus.qt.qtgui.base import TaurusBaseWidget
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

def createChannelDict(name, index=None, **kwargs):
    ret = {'label': name, #channel label
           'enabled': True,  # bool. Whether this channel is enabled (if not enabled, it won't be used for output or plot)
           'output': True,   # bool. Whether to show output in the stdout 
           'plot_type': 'No', # one of the PlotType enumeration members (as string)
           'timer': '', #should contain a channel name
           'monitor': '', #should contain a channel name
           'trigger': '', #should contain a channel name
           'conditioning': '', #this is a python expresion to be evaluated for conditioning the data. The data for this channel can be referred as 'x' and data from other channels can be referred by channel name
           'normalization': 'No', # one of the Normalization enumeration members (as string)
           'nexus_path': '' #string indicating the location of the data of this channel within the nexus tree
           }
    ret.update(kwargs) 
    if index is not None:
        ret['index']= index  #an integer used for ordering the channel in this measurement group
    if 'plot_axes' not in ret: 
        default_axes = {'No':'', '1D':'<idx>', '2D':'<idx>:<idx>'}
        ret['plot_axes'] = default_axes[ret['plot_type']] # a string defining a colon-separated list of axis names. An axis can be a channel name or "<idx>". This shares the syntax of the NeXus @axes attribute  
    return ret


      

DUMMY_CHANNELCONFIGS = {u'BL96_CT1': createChannelDict('BL96_CT1',index=0), 
                        u'BL96_CT2': createChannelDict('BL96_CT2',index=1)
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
                                                                           u'channels': copy.deepcopy(DUMMY_CHANNELCONFIGS) 
                                                                           }}}}
 }

DUMMY_MNGRPCFG_2 = \
{u'monitor': u'BL96_CT1',
 u'description': u'General purpose measurement group', 
 u'timer': u'BL96_CT1', 
 u'label': u'bl96_mntgrp2',
 u'controllers': {u'BL96_DummyCounterTimerController1': {u'units': {u'0': {u'monitor': u'BL96_CT1', 
                                                                           u'id': 0, 
                                                                           u'timer': u'BL96_CT1', 
                                                                           u'trigger_type': 0,
                                                                           u'channels': copy.deepcopy(DUMMY_CHANNELCONFIGS) 
                                                                           }}}}
 }

DUMMY_MNTGRPCONFIGS = {'bl96_mntgrp1':DUMMY_MNGRPCFG_1,
                       'bl96_mntgrp2':DUMMY_MNGRPCFG_2}

DUMMY_EXP_CONF = {'ScanDir':'/tmp/scandir',
                  'ScanFile':'dummyscan.h5',
                  'ActiveMntGrp':'bl96_mntgrp1',
                  'MntGrpConfigs': DUMMY_MNTGRPCONFIGS
                  }
#
#===============================================================================

ChannelView = Enumeration("ChannelView", ("Channel", "Enabled", "Output", "PlotType", "PlotAxes", "Timer", "Monitor", "Trigger", "Conditioning", "Normalization","NXPath","Unknown"))

PlotType = Enumeration("PlotType", ("No", "1D", "2D"))
Normalization = Enumeration("Normalization", ("No", "Avg", "Integ"))

                       
def getElementTypeIcon(t):
    if t == ChannelView.Channel:
        return getIcon(":/actions/system-shutdown.svg")
    elif t == ChannelView.Enabled:
        return getIcon(":/status/true.svg")
    elif t == ChannelView.Output:
        return getThemeIcon("utilities-terminal")
    elif t == ChannelView.PlotType:
        return getIcon(":/apps/utilities-system-monitor.svg")
    elif t == ChannelView.PlotAxes:
        return getIcon(":/apps/utilities-system-monitor.svg")
    elif t == ChannelView.Timer:
        return getIcon(":/status/flag-green-clock.svg")
    elif t == ChannelView.Monitor:
        return getIcon(":/status/flag-green.svg")
    elif t == ChannelView.Trigger:
        return getIcon(":/actions/system-shutdown.svg")
    elif t == ChannelView.NXPath:
        return getThemeIcon("document-save-as")
        
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
    elif t == ChannelView.Timer:
        return "The channel to be used as the timer"
    elif t == ChannelView.Monitor:
        return "The channel to be used as a monitor for stopping the acquisition"
    elif t == ChannelView.Trigger:
        return "The channel to be used for triggering the acquisition"
    elif t == ChannelView.Conditioning:
        return "An expresion to evaluate on the data when displaying it"
    elif t == ChannelView.Normalization:
        return "Normalization mode for the data"
    elif t == ChannelView.NXPath:
        return "Location of the data of this channel within the nexus tree"
    return "Unknown"


class BaseMntGrpChannelItem(TaurusBaseTreeItem):
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


class MntGrpChannelItem(BaseMntGrpChannelItem):
    
    itemdata_keys_map = {ChannelView.Channel:'label',
                         ChannelView.Enabled:'enabled',
                         ChannelView.Output:'output',
                         ChannelView.PlotType:'plot_type',
                         ChannelView.PlotAxes:'plot_axes',
                         ChannelView.Timer:'timer',
                         ChannelView.Monitor:'monitor',
                         ChannelView.Trigger:'trigger',
                         ChannelView.Conditioning:'conditioning',
                         ChannelView.Normalization:'normalization',
                         ChannelView.NXPath:'nexus_path'
                         }
    
    def data(self, index):
        """Returns the data of this node for the given index
        
        :return: (object) the data for the given index
        """
        taurus_role = index.model().role(index.column())
        ch_name, ch_data = self.itemData()
        
        key = self.itemdata_keys_map[taurus_role]
        return ch_data[key]        
#        if taurus_role == ChannelView.Channel:
#            return ch_data['label']
#        elif taurus_role == ChannelView.Enabled:
#            return ch_data['enabled']
#        elif taurus_role == ChannelView.Output:
#            return ch_data['output']
#        elif taurus_role == ChannelView.PlotType:
#            return ch_data['plot_type']
#        elif taurus_role == ChannelView.PlotAxes:
#            if ch_data['plot_type'] == PlotType.No:
#                return None
#            return ch_data['plot_axes']

    def setData(self, index, data):
        taurus_role = index.model().role(index.column())
        ch_name, ch_data = self.itemData()
        key = self.itemdata_keys_map[taurus_role]
        ch_data[key] = data
#        if taurus_role == ChannelView.Channel:
#            ch_data['label'] = str(data)
#        elif taurus_role == ChannelView.Enabled:
#            ch_data['enabled'] = data
#        elif taurus_role == ChannelView.Output:
#            ch_data['output'] = data
#        elif taurus_role == ChannelView.PlotType:
#            ch_data['plot_type'] = data
#        elif taurus_role == ChannelView.PlotAxes:
#            ch_data['plot_axes'] = data
#        else:
#            print 'MntGrpChannelItem.setData does not support the role "%s"'%repr(ChannelView.whatis(taurus_role))

    def role(self):
        return ChannelView.Channel

    def toolTip(self, index):
        return "Channel " + self._itemData[0]

    def icon(self, index):
        taurus_role = index.model().role(index.column())
        if taurus_role == ChannelView.Channel:
            return getIcon(":/actions/system-shutdown.svg")
        

class MntGrpUnitItem(TaurusBaseTreeItem):
    pass


class BaseMntGrpChannelModel(TaurusBaseModel):
    ColumnNames = ("Channel", "enabled", "output", "Plot Type", "Plot Axes", "Timer", 
                  "Monitor", "Trigger", "Conditioning", "Normalization","NeXus Path")
    ColumnRoles = ((ChannelView.Channel, ChannelView.Channel), ChannelView.Enabled, 
                  ChannelView.Output, ChannelView.PlotType,
                  ChannelView.PlotAxes, ChannelView.Timer, ChannelView.Monitor,
                  ChannelView.Trigger, ChannelView.Conditioning,
                  ChannelView.Normalization, ChannelView.NXPath)
    DftFont = Qt.QFont()

    def __init__(self, parent=None, data=None):
        TaurusBaseModel.__init__(self, parent=parent, data=data)
        self._config = None
        self._dirty = False    
    
    def createNewRootItem(self):
        return BaseMntGrpChannelItem(self, self.ColumnNames)
    
    def roleIcon(self, taurus_role):
        return getElementTypeIcon(taurus_role)

    def roleSize(self, taurus_role):
        return getElementTypeSize(taurus_role)

    def roleToolTip(self, taurus_role):
        return getElementTypeToolTip(taurus_role)
    
    def getChannelConfigs(self, mgconfig, ctrls=None, units=None):
        '''
        gets a list of channel configurations by flattening the controllers and
        units levels of the given measurement group configuration. It optionally
        filters to those channels matching given lists of controller and unit
        names.
        
        :return: (list<tuple>) A list of channelname,channeldata pairs. The list
                 is ordered by channel index (if given in channeldata) and then by
                 channelname.
        '''
        chconfigs = []
        for ctrl_name, ctrl_data in mgconfig['controllers'].items():
            if ctrls is None or ctrl_name in ctrls: 
                for unit_id, unit_data in ctrl_data['units'].items():
                    if units is None or unit_id in units:
                        chconfigs.extend(unit_data['channels'].items())
        #sort the channel configs by index (primary sort) and then by channel name.         
        chconfigs = sorted(chconfigs, key=lambda c:c[0]) #sort by channel_name
        chconfigs = sorted(chconfigs, key=lambda c:c[1].get('index',1e16)) #sort by index (give a very large index for those which don't have it)
        return chconfigs
    
    def setupModelData(self, mgconfig):
        if mgconfig is None:
            return
        root = self._rootItem #@The root could eventually be changed for each unit or controller
        channelNodes = [MntGrpChannelItem(self, chcfg, root) for chcfg in self.getChannelConfigs(mgconfig)]
        for ch in channelNodes:
            root.appendChild(ch)

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


class MntGrpChannelModel(BaseMntGrpChannelModel):
    '''A BaseMntGrpChannelModel that communicates with a MntGrp device for setting and reading the configuration
    ''' 
    
    def setDataSource(self, mg):
        if self._data_src is not None:
            Qt.QObject.disconnect(self._data_src, Qt.SIGNAL('configurationChanged'), self.configurationChanged)
        if mg is not None:
            Qt.QObject.connect(mg, Qt.SIGNAL('configurationChanged'), self.configurationChanged)
        BaseMntGrpChannelModel.setDataSource(self, mg)

    def configurationChanged(self):
        self.refresh()

    def setupModelData(self, mg):
        if mg is None:
            return
        mgconfig = self.getSourceData()  
        self._localData = copy.deepcopy(mgconfig)
        BaseMntGrpChannelModel.setupModelData(self, self._localData)

    def writeSourceData(self):
        mg = self.dataSource()
        if mg is not None and self._localData is not None: 
            mg.setConfiguration(self._localData)
    
    def getSourceData(self):
        """Gets data from the dataSource"""
        mg = self.dataSource()
        if mg is not None:
            return mg.getConfiguration()
    
    def getLocalData(self):
        """Gets the local data (may be different from the one in the data source
        since it may have been modified by the user)"""
        return self._localData
    
    def isDataChanged(self):
        """Tells if the local data has been modified since it was last refreshed
        set by a setupModelData call"""
        return self.getSourceData() != self.getLocalData()


class ChannelDelegate(Qt.QStyledItemDelegate):
    availableChannels = {}
    
    def createEditor(self, parent, option, index):
        taurus_role = index.model().role(index.column())
        if taurus_role in (ChannelView.Channel, ChannelView.PlotType, ChannelView.Timer, 
                           ChannelView.Monitor, ChannelView.Trigger, ChannelView.Normalization):
            ret = Qt.QComboBox(parent)
        else:
            ret = Qt.QStyledItemDelegate.createEditor(self, parent, option, index)
        ret.setAutoFillBackground(True)
        return ret
    
    def setEditorData(self, editor, index):
        model = index.model()
        data = model.data(index, Qt.Qt.EditRole)
        pydata = data.toPyObject()
        taurus_role = model.role(index.column())
        if taurus_role == ChannelView.Channel:
            editor.addItems(sorted(self.availableChannels.keys()))
            editor.setCurrentIndex(editor.findText(pydata))
        elif taurus_role == ChannelView.PlotType:
            editor.addItems(PlotType.keys())
            editor.setCurrentIndex(editor.findText(pydata))
        elif taurus_role == ChannelView.Normalization:
            editor.addItems(Normalization.keys())
            editor.setCurrentIndex(editor.findText(pydata))
        elif taurus_role in (ChannelView.Timer, ChannelView.Monitor, ChannelView.Trigger):
            ##IF we want to offer oonly certain channels (e.g. those sharing the controller), use the code commented below
            ##find the controller of this item
            #item = index.internalPointer()
            #ch_name,ch_data = item.itemData()
            #ctrl_name = self.availableChannels.get(ch_name,{}).get('_ctrl_name',None)
            #ctrl_filterlist = (ctrl_name,)  #find the channels already in the mntgrp that share the same controller
            ctrl_filterlist = None
            selectables = [n for n,d in model.getChannelConfigs(model.dataSource(), ctrls=ctrl_filterlist)] 
            editor.addItems(selectables)
        else:
            Qt.QStyledItemDelegate.setEditorData(self, editor, index)
    
    def setModelData(self, editor, model, index):
        taurus_role = model.role(index.column())
        if taurus_role in (ChannelView.Channel, ChannelView.PlotType, ChannelView.Timer, 
                           ChannelView.Monitor, ChannelView.Trigger, ChannelView.Normalization):
            data = Qt.QVariant(editor.currentText())
            model.setData(index, data)
        else:
            Qt.QStyledItemDelegate.setModelData(self, editor, model, index)


class MntGrpChannelEditor(TaurusBaseTableWidget):
    """
    """
    
    KnownPerspectives = {
        "Channel" : {
            "label"   : "Channels",
            "icon"    : ":/actions/system-shutdown.svg",
            "tooltip" : "View by channel",
            "model"   : [BaseMntGrpChannelModel,],
        },
    }

    DftPerspective = "Channel"
    
    def createViewWidget(self):
        tableView = TaurusBaseTableWidget.createViewWidget(self)
        self._delegate = ChannelDelegate(self)
        self._delegate.setItemEditorFactory(Qt.QItemEditorFactory())
        tableView.setItemDelegate(self._delegate)
        tableView.setSortingEnabled(False)
        self.connect(self._editorBar, Qt.SIGNAL("addTriggered"), self.addChannel)
        return tableView

    def createToolArea(self):
        ta = TaurusBaseTableWidget.createToolArea(self)
        e_bar = self._editorBar = EditorToolBar(self, self)
        ta.append(e_bar)
        return ta

    def getModelClass(self):
        return taurus.core.TaurusDevice
    
    def setAvailableChannels(self,cdict):
        self._delegate.availableChannels = cdict
        
    def getAvailableChannels(self):
        return self._delegate.availableChannels
    
    def addChannel(self, channel=None):
        qmodel = self.getQModel()
        if channel is None:
            shown = [n for n,d in qmodel.getChannelConfigs(qmodel.dataSource())]
            clist = [c for c in self.getAvailableChannels() if c not in shown]
            chname,ok = Qt.QInputDialog.getItem(self, "New Channel", "Choose channel:", sorted(clist), 0, False)
            if not ok:
                return
        
        #NOTE: THIS WILL BE UNNECESSARY WHEN WE USE PROPER *TAURUS* SARDANA DEVICES
        chname = str(chname)
        desc = self.getAvailableChannels()[chname]
        ctrlname = desc['_ctrl_name']
        unitname = desc.get('_unit_name','0') #@fixme: at the moment of writing, the unit info cannot be obtained from desc
        
        #update the internal data 
        qmodel.beginResetModel() #we are altering the internal data here, so we need to protect it
        ctrlsdict = qmodel.dataSource()['controllers']
        if not ctrlsdict.has_key(ctrlname): ctrlsdict[ctrlname] = {'units':{}}
        unitsdict = ctrlsdict[ctrlname]['units']
        if not unitsdict.has_key(unitname): unitsdict[unitname] = {'channels':{}}
        channelsdict = unitsdict[unitname]['channels']
        if channelsdict.has_key(chname):
            self.error('Channel "%s" is already in the measurement group. It will not be added again'%chname)
            return
        
        channelsdict[chname] = createChannelDict(chname)
        qmodel.endResetModel() #we are altering the internal data here, so we need to protect it
        qmodel.refresh() #note that another reset will be done here... 
        
        #newchannels = [(chname,chdata)]
        #qmodel.insertChannels(newchannels)
        
        self.emit(Qt.SIGNAL("channelsChanged"))
        
    def getLocalConfig(self):
        return self.getQModel().getLocalData()
        
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


def main_MntGrpChannelEditor(perspective="Channel"):
    w = MntGrpChannelEditor( perspective=perspective)
    w.setWindowTitle("A Taurus Measurement Group editor example")
    w.getQModel().setDataSource(DUMMY_MNGRPCFG_1)
    w.resize(1200,500)
    return w

def main_MntGrpChannelPanel(mg, perspective="Channel"):
    w = MntGrpChannelPanel()
    w.setWindowIcon(getIcon(":/actions/system-shutdown.svg"))
    w.setWindowTitle("A Taurus Sardana measurement group Example")
    w.setModel(mg)
    w.show()
    return w


def demo(model="mg2"):
    """Table panels"""
#    w = main_MntGrpChannelPanel(model)
    w = main_MntGrpChannelEditor()
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

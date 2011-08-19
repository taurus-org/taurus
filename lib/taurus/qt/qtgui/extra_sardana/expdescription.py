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

__all__ = ["ExpDescriptionEditor"]

from PyQt4 import Qt
import copy
import taurus
from taurus.qt.qtgui.base import TaurusBaseWidget

class ExpDescriptionEditor(Qt.QWidget, TaurusBaseWidget):
    '''
    A widget for editing the configuration of a experiment (measurement groups,
    plot and storage parameters, etc).
    
    It receives a Sardana Door name as its model and gets/sets the configuration
    using the `ExperimentConfiguration` environmental variable for that Door.
    '''
    def __init__(self, parent=None, door=None):
        Qt.QWidget.__init__(self, parent)
        TaurusBaseWidget.__init__(self, 'ExpDescriptionEditor')
        from ui.ui_ExpDescriptionEditor import Ui_ExpDescriptionEditor
        self.ui = Ui_ExpDescriptionEditor()
        self.ui.setupUi(self)
        BB = Qt.QDialogButtonBox
        self.ui.buttonBox.setStandardButtons(BB.Ok | BB.Cancel | BB.Reset | BB.Apply)
        
        self._localConfig = None
        self._originalConfiguration = None
        self.connect(self.ui.activeMntGrpCB, Qt.SIGNAL('currentIndexChanged (QString)'), self.onActiveMntGrpChanged)
        
        if door is not None:
            self.setModel(door)
        self.connect(self.ui.buttonBox, Qt.SIGNAL("clicked(QAbstractButton *)"), self.onDialogButtonClicked)
        
    def onActiveMntGrpChanged(self, activeMntGrpName):
        activeMntGrpName = str(activeMntGrpName)
        if self._localConfig is None: return
        if activeMntGrpName not in self._localConfig['MntGrpConfigs']: return
#        if self.ui.channelEditor.getQModel().isDataChanged():
#            previous = self._localConfig['ActiveMntGrp']
#            op = Qt.QMessageBox.question(self, "Save changes", 'The measurement group "%S" has unsaved info. Do you want to save it?'%previous, Qt.QMessageBox.Save|Qt.QMessageBox.Discard, Qt.QMessageBox.Save)
#            if op == Qt.QMessageBox.Save:
#                
#                for chname,chdata in channels:
#                    self._localConfig['MntGrpConfigs'][previous]['__channelsFlatDict__'] = chdata 
#                    self._localConfig['MntGrpConfigs'][previous]['controllers'].update()
#                
#                             
# 
        self._localConfig['ActiveMntGrp'] = activeMntGrpName
        mgconfig = self._localConfig['MntGrpConfigs'][activeMntGrpName]
        self.ui.channelEditor.getQModel().setDataSource(mgconfig)
        
#    def updateMntGrp(self, mntgrpname, channels=None):
#        if channels is None:
#            channels = self.ui.channelEditor.getLocalConfig()
#            ## IMHO, THE FOLLOWING COMMENTED LINES SHOULD BE THE WAY TO GO WHEN SARDANA SUPPORT IN TAURUS IS MORE ADVANCED
#            #chobj = taurus.Device(chname) #this should return a taurus.core.tango.sardana.ExpChan, not just a TangoDevice
#            #ctrl, unit = chobj.getControllerName(), chobj.getUnitName()
#            ctrl, unit = self.__getChannelControllerAndUnit(chname) #this is just a temporary workaround
#            self._localConfig['MntGrpConfigs'][activeMntGrpName]['__channelsFlatDict__'] = channels
                
    def getModelClass(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        return taurus.core.TaurusDevice
        
    def onDialogButtonClicked(self, button):
        role = self.ui.buttonBox.buttonRole(button)
        #qmodel = self.ui.channelEditor.getQModel()
        if role == Qt.QDialogButtonBox.AcceptRole:
            print self.isDataChanged(), self.getLocalConfig()
        elif role == Qt.QDialogButtonBox.ApplyRole:
            localconf = self.getLocalConfig()
            print self.isDataChanged(), localconf
            #qmodel.writeSourceData()
        elif role == Qt.QDialogButtonBox.ResetRole:
            self._reloadConf()
            #qmodel.refresh()
    
    def setModel(self, model):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        TaurusBaseWidget.setModel(self, model)
        self._reloadConf(force=True)
        
    def _reloadConf(self, force=False):
        if not force:
            op = Qt.QMessageBox.question(self, "Reload info from door", 
                                    "If you reload, all current experiment configuration changes will be lost. Reload?", 
                                    Qt.QMessageBox.Yes|Qt.QMessageBox.Cancel)
            if op != Qt.QMessageBox.Yes: 
                return
        door = self.getModelObj()
        if door is None: return
        conf = door.getExperimentConfiguration()
        self._originalConfiguration = conf
        self.setLocalConfig(conf)
        #set a list of available channels
        from taurus.core.tango.sardana.pool import ExpChannel
        avail = {}
        for s in door.macro_server.ExpChannelList:
            d = ExpChannel.match(s)
            avail[d['_alias']] = d
            
        self.ui.channelEditor.setAvailableChannels(avail)
        
    def isDataChanged(self):
        """Tells if the local data has been modified since it was last refreshed
        """
        return self._originalConfiguration != self.getLocalConfig()

    def setLocalConfig(self, conf):
        '''gets a ExpDescription dictionary and sets up the widget'''
        self._localConfig = conf
        mgcfgs = conf['MntGrpConfigs']
        self.ui.activeMntGrpCB.clear()
        self.ui.activeMntGrpCB.addItems(sorted(mgcfgs.keys()))
        idx = self.ui.activeMntGrpCB.findText(self._localConfig['ActiveMntGrp'])
        self.ui.activeMntGrpCB.setCurrentIndex(idx)
        
        
#    def _createChannelPerspective(self, orig):
#        '''
#        gets a configuration dict as it comes from the door and adds a new item
#        ('__channelsFlatDict__') containing a flat view of the channels (it
#        flattens the controllers and units level). Note that the channel
#        dictionaries are just referenced -not copied-, so they can be accessed
#        and edited indistinctly from both the flat or the original branch.
#        '''
#        ret = copy.deepcopy(orig)
#        for mgname,mgdict in ret['MntGrpConfigs'].items():
#            mgdict['__channelsFlatDict__'] = channelsflatdict = {} 
#            for ctrlname,ctrldict in mgdict['controllers'].items():
#                for unitname,unitdict in ctrldict['units'].items():
#                    for chname, chdict in unitdict['channels'].items():
#                        channelsflatdict[chname] = chdict
##        print "!!!RET ", sorted(ret['MntGrpConfigs'][ret['ActiveMntGrp']].keys())
##        print "!!!ORIG",  sorted(orig['MntGrpConfigs'][ret['ActiveMntGrp']].keys())
##        print ret['MntGrpConfigs'][ret['ActiveMntGrp']]['__channelsFlatDict__'].keys()
#        return ret
    
    def getLocalConfig(self):
        return self._localConfig
        
            


  
            
def demo(model="mydoor"):
    """Table panels"""
    #w = main_ChannelEditor()
    w = ExpDescriptionEditor(door=model)
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

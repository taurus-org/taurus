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
tauruspanel.py: 
"""

__all__ = ["TaurusDevPanel"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt

import taurus.core
from taurus.qt.qtgui.container import TaurusMainWindow

def filterNonExported(obj):
    if not isinstance(obj,taurus.core.TaurusDevInfo) or obj.exported():
        return obj
    return None
    
class TaurusDevPanel(TaurusMainWindow):
    '''
    TaurusDevPanel is a Taurus Application inspired in Jive and Atk Panel.
    
    It Provides a Device selector and several dockWidgets for interacting and
    displaying information from the selected device.
    '''
    def __init__(self, parent=None, designMode = False):
        TaurusMainWindow.__init__(self, parent, designMode=designMode)
        
        import taurus.qt.qtgui.ui.ui_TaurusDevPanel
        self._ui = taurus.qt.qtgui.ui.ui_TaurusDevPanel.Ui_TaurusDevPanel()
        self._ui.setupUi(self)
        
        #setting up the device Tree. 
        #@todo: This should be done in the ui file when the TaurusDatabaseTree Designer plugin is available
        import taurus.qt.qtgui.tree
        TaurusDbTreeWidget = taurus.qt.qtgui.tree.TaurusDbTreeWidget

        self.deviceTree = TaurusDbTreeWidget(perspective=taurus.core.TaurusElementType.Device)
        self.deviceTree.getQModel().setSelectables([taurus.core.TaurusElementType.Member])
        #self.deviceTree.insertFilter(filterNonExported)
        self.setCentralWidget(self.deviceTree)        
        
        #needed because of a limitation in when using the useParentModel
        #property from designer and taurus parents are not the same as Qt Parents
        self._ui.taurusAttrForm.recheckTaurusParent()
        self._ui.taurusCommandsForm.recheckTaurusParent()
        
        #Add StateLed to statusBar
#        self.devStateLed = TaurusStateLed()
#        self.statusbar.addPermanentWidget(self.devStateLed)
#        self.devStateLed.setModel('/state')
#        self.devStateLed.setUseParentModel(True)
        
        #register subwidgets for configuration purposes 
        #self.registerConfigDelegate(self.taurusAttrForm)
        #self.registerConfigDelegate(self.deviceTree)
        self.registerConfigDelegate(self._ui.taurusCommandsForm)
        
        self.loadSettings()
        self.createActions()
        
        #self.addToolBar(self.basicTaurusToolbar())
        
        self.connect(self.deviceTree, Qt.SIGNAL("currentItemChanged"),self.onItemSelectionChanged)
                
        self.updatePerspectivesMenu()
        if not designMode:
            self.splashScreen().finish(self)
    
    def createActions(self):
        '''create actions '''
        #View Menu
        self.showAttrAction = self.viewMenu.addAction(self._ui.attrDW.toggleViewAction())
        self.showCommandsAction = self.viewMenu.addAction(self._ui.commandsDW.toggleViewAction())
        self.showTrendAction = self.viewMenu.addAction(self._ui.trendDW.toggleViewAction())
        
    def setTangoHost(self, host):
        '''extended from :class:setTangoHost'''
        TaurusMainWindow.setTangoHost(self, host)
        self.deviceTree.setModel(host)
        #self.deviceTree.insertFilter(filterNonExported)
        
    def onItemSelectionChanged(self, current, previous):
        itemData = current.itemData()
        if isinstance(itemData, taurus.core.TaurusDevInfo):
            self.onDeviceSelected(itemData)
        
    def onDeviceSelected(self, devinfo):
        devname = devinfo.name()
        msg = 'Connecting to "%s"...'%devname
        self.statusBar().showMessage(msg)
        #abort if the device is not exported
        if not devinfo.exported():
            msg = 'Connection to "%s" failed (not exported)'%devname
            self.statusBar().showMessage(msg)
            self.info(msg)
            Qt.QMessageBox.warning(self, "Device unreachable", msg)
            self.setModel('')
            return
        self.setDevice(devname)
        
    def setDevice(self,devname):
        #try to connect with the device
        self.setModel(devname)
        dev = self.getModelObj()
        state = dev.getSWState()
        #test the connection
        if state == taurus.core.TaurusSWDevState.Running:
            msg = 'Connected to "%s"'%devname
            self.statusBar().showMessage(msg)
            self._ui.attrDW.setWindowTitle('Attributes - %s'%devname)
            self._ui.commandsDW.setWindowTitle('Commands - %s'%devname)
        else:
            #reset the model if the connection failed
            msg = 'Connection to "%s" failed (state = %s)'%(devname, taurus.core.TaurusSWDevState.whatis(state))
            self.statusBar().showMessage(msg)
            self.info(msg)
            Qt.QMessageBox.warning(self, "Device unreachable", msg)
            self.setModel('')
            
    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusMainWindow.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.panel'
        return ret

    
def TaurusPanelMain():
    '''A launcher for TaurusPanel.'''
    ## NOTE: DON'T PUT TEST CODE HERE.
    ## THIS IS CALLED FROM THE LAUNCHER SCRIPT (<taurus>/scripts/tauruspanel)
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.core.util import argparse
    import sys
    
    parser = argparse.get_taurus_parser()
    parser.set_usage("%prog [options] [devname]")
    parser.set_description("Taurus Application inspired in Jive and Atk Panel")
    app = TaurusApplication(cmd_line_parser=parser,app_name="tauruspanel",
                            app_version=taurus.Release.version)
    args = app.get_command_line_args()
    options = app.get_command_line_options()
    
    w = TaurusDevPanel()
    
    if options.tango_host is None:
        options.tango_host = taurus.Database().getNormalName()
    w.setTangoHost(options.tango_host)
    if len(args) == 1: 
        w.setDevice(args[0])
    
    w.show()
    
    sys.exit(app.exec_()) 
    
if __name__ == "__main__":
    TaurusPanelMain() 
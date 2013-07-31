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
###########################################################################

"""
This module provides an object that can be added to a TaurusGui manage the
widgets for: 
- setting preferences in the sardana control system for data I/O 
- displaying results of macro executions, including creating/removing panels for
  plotting results of scans
"""

__all__=['MacroBroker']
__docformat__ = 'restructuredtext'


#import os, sys
import datetime
import taurus
from taurus.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseComponent
from taurus.qt.qtgui.resource import getThemeIcon, getIcon
#from taurus.qt.qtgui.taurusgui.utils import PanelDescription
from taurus.core.tango.sardana import PlotType
from taurus.core.tango.sardana.pool import getChannelConfigs
from taurus.core.util.containers import CaselessList

class ChannelFilter(object):
    def __init__(self,chlist):
        self.chlist = tuple(chlist)
    def __call__(self, x):
        return x in self.chlist

class MacroBroker(Qt.QObject, TaurusBaseComponent):
    def __init__(self, parent):
        '''Passing the parent object (the main window) is mandatory'''
        Qt.QObject.__init__(self, parent)
        TaurusBaseComponent.__init__(self, self.__class__.__name__)
        
        self._createPermanentPanels()
        self._trends1d={}
        self._trends2d={}
        #connect the broker to shared data
        Qt.qApp.SDM.connectReader("doorName", self.setModel)
        Qt.qApp.SDM.connectReader("expConfChanged", self.onExpConfChanged)
        Qt.qApp.SDM.connectWriter("shortMessage", self, 'newShortMessage')
        
    def setModel(self, doorname):
        TaurusBaseComponent.setModel(self, doorname)
        self._onDoorChanged(doorname)
        
    def _onDoorChanged(self, doorname):
        ''' Slot to be called when the door has changed. It updates connections of the door.
        
        :param doorname: (str) the tango name of the door device 
        '''
        if getattr(self, '__qdoor',None) is not None: #disconnect it from *all* shared data providing
            Qt.qApp.SDM.disconnectWriter("macroStatus", self.__qdoor, "macroStatusUpdated")
            Qt.qApp.SDM.disconnectWriter("doorOutputChanged", self.__qdoor, "outputUpdated")
            Qt.qApp.SDM.disconnectWriter("doorInfoChanged", self.__qdoor, "infoUpdated")
            Qt.qApp.SDM.disconnectWriter("doorWarningChanged", self.__qdoor, "warningUpdated")
            Qt.qApp.SDM.disconnectWriter("doorErrorChanged", self.__qdoor, "errorUpdated")
            Qt.qApp.SDM.disconnectWriter("doorDebugChanged", self.__qdoor, "debugUpdated")
            Qt.qApp.SDM.disconnectWriter("doorResultChanged", self.__qdoor, "resultUpdated")
            Qt.qApp.SDM.disconnectWriter("expConfChanged", self.__qdoor, "experimentConfigurationChanged")
             
        if doorname == "": return #@todo send signal with doorName to macroExecutorWidget in case of "" also send it to disconnect doorstateled
        door = taurus.Device(doorname)
        if not isinstance(door, Qt.QObject):
            msg= "cannot connect to door %s"%doorname
            Qt.QMessageBox.critical(self.parent(),'Door connection error', msg)
            return
        self.__qdoor = door
        Qt.qApp.SDM.connectWriter("macroStatus", self.__qdoor, "macroStatusUpdated")
        Qt.qApp.SDM.connectWriter("doorOutputChanged", self.__qdoor, "outputUpdated")
        Qt.qApp.SDM.connectWriter("doorInfoChanged", self.__qdoor, "infoUpdated")
        Qt.qApp.SDM.connectWriter("doorWarningChanged", self.__qdoor, "warningUpdated")
        Qt.qApp.SDM.connectWriter("doorErrorChanged", self.__qdoor, "errorUpdated")
        Qt.qApp.SDM.connectWriter("doorDebugChanged", self.__qdoor, "debugUpdated")
        Qt.qApp.SDM.connectWriter("doorResultChanged", self.__qdoor, "resultUpdated")
        Qt.qApp.SDM.connectWriter("expConfChanged", self.__qdoor, "experimentConfigurationChanged")
        
        expconf = self.__qdoor.getExperimentConfiguration()
        self.onExpConfChanged(expconf) 
        
        #check if JsonRecorder env var is set
        if 'JsonRecorder' not in self.__qdoor.getEnvironment():
            msg = 'JsonRecorder environment variable is not set, but it is needed for displaying trend plots. \nEnable it globally for %s?'%doorname
            result = Qt.QMessageBox.question(self.parent(),'JsonRecorder not set', msg, Qt.QMessageBox.Yes|Qt.QMessageBox.No)
            if result == Qt.QMessageBox.Yes:
                self.__qdoor.putEnvironment('JsonRecorder',True)
                self.info('JsonRecorder Enabled for %s'%doorname)
                
        #@todo: connect as a writer of other data as well
        
    def _createPermanentPanels(self):
        '''creates panels on the main window'''
        from taurus.qt.qtgui.extra_macroexecutor import TaurusMacroExecutorWidget, TaurusSequencerWidget,  TaurusMacroConfigurationDialog, \
                                                     TaurusMacroDescriptionViewer, DoorOutput, DoorDebug, DoorResult

        from taurus.qt.qtgui.extra_sardana import ExpDescriptionEditor, SardanaEditor
        
        mainwindow = self.parent()
        
        #Create macroconfiguration dialog & action
        self.__macroConfigurationDialog = TaurusMacroConfigurationDialog(mainwindow)
        self.macroConfigurationAction = mainwindow.taurusMenu.addAction(getThemeIcon("preferences-system-session"), "Macro execution configuration...", self.__macroConfigurationDialog.show)
        Qt.qApp.SDM.connectReader("macroserverName", self.__macroConfigurationDialog.selectMacroServer)
        Qt.qApp.SDM.connectReader("doorName", self.__macroConfigurationDialog.selectDoor)
        Qt.qApp.SDM.connectWriter("macroserverName", self.__macroConfigurationDialog, 'macroserverNameChanged')
        Qt.qApp.SDM.connectWriter("doorName", self.__macroConfigurationDialog, 'doorNameChanged')
        
        #Create ExpDescriptionEditor dialog
        self.__expDescriptionEditor = ExpDescriptionEditor()
        Qt.qApp.SDM.connectReader("doorName", self.__expDescriptionEditor.setModel)
        mainwindow.createPanel(self.__expDescriptionEditor, 'Experiment Config', registerconfig=True,
                               icon = getThemeIcon('preferences-system'), permanent=True)
        ###############################
        #@todo: These lines can be removed once the door does emit "experimentConfigurationChanged" signals
        Qt.qApp.SDM.connectWriter("expConfChanged", self.__expDescriptionEditor, "experimentConfigurationChanged")
        ################################
        
        #put a Macro Executor
        self.__macroExecutor = TaurusMacroExecutorWidget()
        Qt.qApp.SDM.connectReader("macroserverName", self.__macroExecutor.setModel)
        Qt.qApp.SDM.connectReader("doorName", self.__macroExecutor.onDoorChanged)
        Qt.qApp.SDM.connectReader("macroStatus", self.__macroExecutor.onMacroStatusUpdated)
        Qt.qApp.SDM.connectWriter("macroName", self.__macroExecutor, "macroNameChanged")
        Qt.qApp.SDM.connectWriter("executionStarted", self.__macroExecutor, "macroStarted")
        Qt.qApp.SDM.connectWriter("plotablesFilter", self.__macroExecutor, "plotablesFilterChanged")
        Qt.qApp.SDM.connectWriter("shortMessage", self.__macroExecutor, "shortMessageEmitted")
        mainwindow.createPanel(self.__macroExecutor, 'Macros', registerconfig=True, permanent=True)
        
        #put a Sequencer
        self.__sequencer = TaurusSequencerWidget()
        Qt.qApp.SDM.connectReader("macroserverName", self.__sequencer.setModel)
        Qt.qApp.SDM.connectReader("doorName", self.__sequencer.onDoorChanged)
        Qt.qApp.SDM.connectReader("macroStatus", self.__sequencer.onMacroStatusUpdated)
        Qt.qApp.SDM.connectWriter("macroName", self.__sequencer.tree, "macroNameChanged")
        Qt.qApp.SDM.connectWriter("macroName", self.__sequencer, "macroNameChanged")
        Qt.qApp.SDM.connectWriter("executionStarted", self.__sequencer, "macroStarted")
        Qt.qApp.SDM.connectWriter("plotablesFilter", self.__sequencer, "plotablesFilterChanged")
        Qt.qApp.SDM.connectWriter("shortMessage", self.__sequencer, "shortMessageEmitted")
        mainwindow.createPanel(self.__sequencer, 'Sequences', registerconfig=True, permanent=True)
        
        #puts a macrodescriptionviewer
        self.__macroDescriptionViewer = TaurusMacroDescriptionViewer()
        Qt.qApp.SDM.connectReader("macroserverName", self.__macroDescriptionViewer.setModel)
        Qt.qApp.SDM.connectReader("macroName", self.__macroDescriptionViewer.onMacroNameChanged)
        mainwindow.createPanel(self.__macroDescriptionViewer, 'MacroDescription', registerconfig=True, permanent=True)
        
        #puts a doorOutput
        self.__doorOutput = DoorOutput()
        Qt.qApp.SDM.connectReader("doorOutputChanged", self.__doorOutput.onDoorOutputChanged)
        Qt.qApp.SDM.connectReader("doorInfoChanged", self.__doorOutput.onDoorInfoChanged)
        Qt.qApp.SDM.connectReader("doorWarningChanged", self.__doorOutput.onDoorWarningChanged)
        Qt.qApp.SDM.connectReader("doorErrorChanged", self.__doorOutput.onDoorErrorChanged)
        mainwindow.createPanel(self.__doorOutput, 'DoorOutput', registerconfig=False, permanent=True)
        
        #puts doorDebug
        self.__doorDebug = DoorDebug()
        Qt.qApp.SDM.connectReader("doorDebugChanged", self.__doorDebug.onDoorDebugChanged)
        mainwindow.createPanel(self.__doorDebug, 'DoorDebug', registerconfig=False, permanent=True)
        
        #puts doorResult
        self.__doorResult = DoorResult(mainwindow)
        Qt.qApp.SDM.connectReader("doorResultChanged", self.__doorResult.onDoorResultChanged)
        mainwindow.createPanel(self.__doorResult, 'DoorResult', registerconfig=False, permanent=True)
        
        #puts sardanaEditor
        self.__sardanaEditor = SardanaEditor()
        Qt.qApp.SDM.connectReader("macroserverName", self.__sardanaEditor.setModel)
        mainwindow.createPanel(self.__sardanaEditor, 'SardanaEditor', registerconfig=False, permanent=True)

        #add panic button for aborting the door
        self.doorAbortAction = mainwindow.jorgsBar.addAction(getIcon(":/actions/process-stop.svg"), "Panic Button: stops the pool (double-click for abort)", self.__onDoorAbort)
        self.__lastAbortTime = datetime.datetime(1,1,1) #beginning of times
        self.__doubleclickInterval = datetime.timedelta(0,0,1000*Qt.qApp.doubleClickInterval()) #doubleclick interval translated into a timedelta
        
    def __onDoorAbort(self):
        '''slot to be called when the abort action is triggered. 
        It sends stop command to the pools (or abort if the action
        has been triggered twice in less than self.__doubleclickInterval
        
        .. note:: An abort command is always preceded by an stop command 
        '''
        #decide whether to send stop or abort
        now = datetime.datetime.now()
        if now-self.__lastAbortTime < self.__doubleclickInterval:
            cmd = 'abort'
        else:
            cmd = 'stop'
        #abort the door
        self.__qdoor.command_inout('abort')
        #send stop/abort to all pools
        pools = self.__qdoor.macro_server.getElementsOfType('Pool')
        for pool in pools.values():
            self.info('Sending %s command to %s'%(cmd,pool.getFullName()))
            try:
                pool.getObj().command_inout(cmd)
            except:
                self.info('%s command failed on %s',cmd,pool.getFullName(), exc_info=1)
        self.emit(Qt.SIGNAL("newShortMessage"),"%s command sent to all pools"%cmd)      
        self.__lastAbortTime = now
        
    def onExpConfChanged(self, expconf):
        '''
        slot to be called when experimental configuration changes. It should
        remove the temporary panels and create the new ones needed.
        
        :param expconf: (dict) An Experiment Description dictionary. See 
                        :meth:`taurus.qt.qtcore.tango.sardana.QDoor.getExperimentDescription` 
                        for more details 
        '''
        #print "@@@@@@@@", expconf
        if expconf['ActiveMntGrp'] is None: 
            return
        mgconfig = expconf['MntGrpConfigs'][expconf['ActiveMntGrp']]
        channels = dict(getChannelConfigs(mgconfig, sort=False))
        #classify by type of plot:
        trends1d = {}
        trends2d = {}
        plots1d = {}
        images = {}
        
        for chname,chdata in channels.items():
            ptype = chdata['plot_type']
            if ptype == PlotType.No:
                continue
            elif ptype == PlotType.Spectrum:
                axes = tuple(chdata['plot_axes'])
                ndim = chdata.get('ndim',0) #@todo: hardcoded default for testing, but it should be obtained from the channel.
                if ndim == 0: #this is a trend
                    if axes in trends1d:
                        trends1d[axes].append(chname)
                    else:
                        trends1d[axes] = CaselessList([chname])
                elif ndim == 1:
                    pass
                else:
                    self.warning('Cannot create plot for %s', chname)
                    
            elif ptype == PlotType.Image:
                axes = tuple(chdata['plot_axes'])
                ndim = chdata.get('ndim',1) #@todo: hardcoded default for testing, but it should be obtained from the channel.
                if ndim == 0:
                    pass
                elif ndim == 1: #a 2d trend
                    if axes in trends2d:
                        trends2d[axes].append(chname)
                    else:
                        trends2d[axes] = CaselessList([chname])
                elif ndim == 2:
                    pass
                else:
                    self.warning('Cannot create plot for %s', chname)
                    
        new1d,removed1d = self._updateTemporaryTrends1D(trends1d)
        self.emit(Qt.SIGNAL("newShortMessage"),"Changed panels (%i new, %i removed)"%(len(new1d),len(removed1d)))
#        self._updateTemporaryTrends2D(trends2d)
        
    def _updateTemporaryTrends1D(self, trends1d):
        '''adds necessary trend1D panels and removes no longer needed ones
        
        :param trends1d: (dict) A dict whose keys are tuples of axes and 
                         whose values are list of model names to plot
        
        :returns: (tuple) two lists new,rm:new contains the names of the new
                  panels and rm contains the names of the removed panels  
        '''
        
        from taurus.qt.qtgui.plot import TaurusTrend
        mainwindow = self.parent()
        newpanels = []                
        for axes,plotables in trends1d.items():
            if not axes:
                continue
            if axes not in self._trends1d:     
                w = TaurusTrend()
                w.setXIsTime(False)
                w.setScanDoor(self.__qdoor.name())
                w.setScansXDataKey(axes[0]) #@todo: use a standard key for <idx> and <mov>
                pname = u'Trend1D - %s'%":".join(axes)
                panel = mainwindow.createPanel(w, pname, registerconfig=False, permanent=False)
                panel.raise_()
                self._trends1d[axes] = pname
                newpanels.append(pname)
            else:
                panel = mainwindow.getPanel(self._trends1d[axes])
            flt = ChannelFilter(plotables)
            panel.widget().onScanPlotablesFilterChanged(flt)
        
        #remove trends that aren no longer configured 
        removedpanels = [name for axes,name in self._trends1d.items() if axes not in trends1d]
        self.removeTemporaryPanels(removedpanels)
        return newpanels,removedpanels
         
            
    def _updateTemporaryTrends2D(self, trends2d):
        try:
            from taurus.qt.qtgui.extra_guiqwt.taurustrend2d import TaurusTrend2DDialog
            from taurus.qt.qtgui.extra_guiqwt.image import TaurusTrend2DScanItem
        except:
            self.info('guiqwt extension cannot be loaded. 2D Trends will not be created')
            raise
            return
        mainwindow = self.parent()
        for axes,plotables in trends2d.items():
            for chname in plotables:
                pname =  u'Trend2D - %s'%chname
                if pname in self._trends2d:
                    self._trends2d[pname].widget().trendItem.clearTrend()
                else:
                    axis = axes[0]
                    w = TaurusTrend2DDialog(stackMode='event')
                    plot = w.get_plot()
                    t2d = TaurusTrend2DScanItem(chname, axis, self.__qdoor.name())
                    plot.add_item(t2d)
                    mainwindow.createPanel(w, pname, registerconfig=False, permanent=False)
                    self._trends2d[(axes,chname)] = pname
    
    def removeTemporaryPanels(self, names=None):
        if names is None: 
            names = self._trends1d.values() + self._trends2d.values()#@todo: the same for other temporary panels
        mainwindow = self.parent()
        for pname in names:
            mainwindow.removePanel(pname)
            
                
        
#class Trend1DDescription(PanelDescription):
#    def __init__(self, ):      

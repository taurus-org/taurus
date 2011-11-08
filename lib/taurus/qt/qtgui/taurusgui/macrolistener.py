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


import os, sys
import taurus
from taurus.qt import Qt
from taurus.qt.qtgui.base import TaurusBaseComponent
from taurus.qt.qtgui.resource import getThemeIcon
from taurus.qt.qtgui.taurusgui.utils import PanelDescription

class MacroBroker(Qt.QObject, TaurusBaseComponent):
    def __init__(self, parent):
        '''Passing the parent object (the main window) is mandatory'''
        Qt.QObject.__init__(self, parent)
        TaurusBaseComponent.__init__(self, self.__class__.__name__)
        
        self._createPermanentPanels()
        
        #connect the broker to shared data
        Qt.qApp.SDM.connectReader("doorName", self.setModel)
        Qt.qApp.SDM.connectReader("expConfChanged", self.onExpConfChanged)
        
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
            Qt.QMessageBox.critical(self,'Door connection error', msg)
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
        self.onExpConfChanged(expconf) #@todo: we may be able to remove this once the experimentConfigurationChanged signals from the door is implemented
        #@todo: connect as a writer of other data as well
        
    def _createPermanentPanels(self):
        '''creates panels on the main window'''
        from taurus.qt.qtgui.extra_macroexecutor import TaurusMacroExecutorWidget, TaurusSequencerWidget,  TaurusMacroConfigurationDialog, \
                                                     TaurusMacroDescriptionViewer, DoorOutput, DoorDebug, DoorResult

        from taurus.qt.qtgui.extra_sardana import ExpDescriptionEditor
        
        
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
                               icon = getThemeIcon('preferences-system'))
        
        #put a Macro Executor
        self.__macroExecutor = TaurusMacroExecutorWidget()
        Qt.qApp.SDM.connectReader("macroserverName", self.__macroExecutor.setModel)
        Qt.qApp.SDM.connectReader("doorName", self.__macroExecutor.onDoorChanged)
        Qt.qApp.SDM.connectReader("macroStatus", self.__macroExecutor.onMacroStatusUpdated)
        Qt.qApp.SDM.connectWriter("macroName", self.__macroExecutor, "macroNameChanged")
        Qt.qApp.SDM.connectWriter("executionStarted", self.__macroExecutor, "macroStarted")
        Qt.qApp.SDM.connectWriter("plotablesFilter", self.__macroExecutor, "plotablesFilterChanged")
        Qt.qApp.SDM.connectWriter("shortMessage", self.__macroExecutor, "shortMessageEmitted")
        mainwindow.createPanel(self.__macroExecutor, 'Macros', registerconfig=True)
        
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
        mainwindow.createPanel(self.__sequencer, 'Sequences', registerconfig=True)
        
        #puts a macrodescriptionviewer
        self.__macroDescriptionViewer = TaurusMacroDescriptionViewer()
        Qt.qApp.SDM.connectReader("macroserverName", self.__macroDescriptionViewer.setModel)
        Qt.qApp.SDM.connectReader("macroName", self.__macroDescriptionViewer.onMacroNameChanged)
        mainwindow.createPanel(self.__macroDescriptionViewer, 'MacroDescription', registerconfig=True)
        
        #puts a doorOutput
        self.__doorOutput = DoorOutput()
        Qt.qApp.SDM.connectReader("doorOutputChanged", self.__doorOutput.onDoorOutputChanged)
        Qt.qApp.SDM.connectReader("doorInfoChanged", self.__doorOutput.onDoorInfoChanged)
        Qt.qApp.SDM.connectReader("doorWarningChanged", self.__doorOutput.onDoorWarningChanged)
        Qt.qApp.SDM.connectReader("doorErrorChanged", self.__doorOutput.onDoorErrorChanged)
        mainwindow.createPanel(self.__doorOutput, 'DoorOutput', registerconfig=False)
        
        #puts doorDebug
        self.__doorDebug = DoorDebug()
        Qt.qApp.SDM.connectReader("doorDebugChanged", self.__doorDebug.onDoorDebugChanged)
        mainwindow.createPanel(self.__doorDebug, 'DoorDebug', registerconfig=False)
        
        #puts doorResult
        self.__doorResult = DoorResult(mainwindow)
        Qt.qApp.SDM.connectReader("doorResultChanged", self.__doorResult.onDoorResultChanged)
        mainwindow.createPanel(self.__doorResult, 'DoorResult', registerconfig=False)
        
    def onExpConfChanged(self, expconf):
        '''
        slot to be called when experimental configuration changes. It should
        remove the temporary panels and create the new ones needed.
        
        :param expconf: (dict) An Experiment Description dictionary. See 
                        :meth:`taurus.qt.qtcore.tango.sardana.QDoor.getExperimentDescription` 
                        for more details 
        '''
        mainwindow = self.parent()
        
        #extract the info of what to plot from the expconf (segregated by type of plot)
          #for each trend1d, create a taurustrend and set the x and the plotablesfilter
          #for each plot1d, create a taurusplot and set its source
          #for each imageplot, create a taurusimage and set its source
        
        #puts a TaurusTrend connected to the door for showing scan trends
        from taurus.qt.qtgui.plot import TaurusTrend
        self.__scanTrend = TaurusTrend()
        self.__scanTrend.setXIsTime(False)
        self.__scanTrend.setScansAutoClear(False)
        Qt.qApp.SDM.connectReader("doorName", self.__scanTrend.setScanDoor)
        Qt.qApp.SDM.connectReader("plotablesFilter", self.__scanTrend.onScanPlotablesFilterChanged)
        mainwindow.createPanel(self.__scanTrend, '1D Scans', registerconfig=True)
        
        
#class Trend1DDescription(PanelDescription):
#    def __init__(self, ):      

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
sequenceeditor.py: 
"""

import sys
from copy import deepcopy
from PyQt4 import Qt
import PyTango

from taurus import Device
from taurus.qt.qtgui.container import TaurusWidget, TaurusMainWindow
from taurus.qt.qtgui.display import TaurusLed

from favouriteseditor import FavouritesMacrosEditor
from common import MacroComboBox, MacroExecutionWindow, standardPlotablesFilter
from taurus.qt.qtgui.extra_macroexecutor.macroparameterseditor import ParamEditorManager, ParamEditorModel, StandardMacroParametersEditor
from taurus.core.tango.macroserver import macro


from taurus.qt.qtgui.resource import getThemeIcon

        
class MacroProgressBar(Qt.QProgressBar):
    
    def __init__(self, parent=None):
        Qt.QProgressBar.__init__(self, parent)
        
class SpockCommandWidget(Qt.QLineEdit):
    
    def __init__(self, parent=None):
        Qt.QLineEdit.__init__(self, parent)
        self._model = None 
        self.setFont(Qt.QFont("Courier",9))
        self.setReadOnly(True)
        palette = Qt.QPalette()
        palette.setColor(Qt.QPalette.Base, Qt.QColor('yellow'))
        self.setPalette(palette)
        
    def setCommand(self):
        command = self._model.toSpockCommand()
        self.setText(command)
        
    def setModel(self, model):
        self._model = model
        self.connect(self._model, Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.setCommand)
        self.connect(self._model, Qt.SIGNAL("modelReset()"), self.setCommand)
        
    def model(self):
        return self._model
        
class TaurusMacroExecutorWidget(TaurusWidget):
    
    def __init__(self, parent = None, designMode = False):
        TaurusWidget.__init__(self, parent, designMode)
        self.setObjectName(self.__class__.__name__)
        
        self._doorName = ""
        self._macroId = None
        self.setLayout(Qt.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        
        self.addToFavouritesAction = Qt.QAction(getThemeIcon("software-update-available"), "Add to favourites", self)
        self.connect(self.addToFavouritesAction, Qt.SIGNAL("triggered()"), self.onAddToFavourites)
        self.addToFavouritesAction.setToolTip("Add to favourites")
        self.stopMacroAction = Qt.QAction(getThemeIcon("media-playback-stop"), "Stop", self)
        self.connect(self.stopMacroAction, Qt.SIGNAL("triggered()"), self.onStopMacro)
        self.stopMacroAction.setToolTip("Stop")
        self.pauseMacroAction = Qt.QAction(getThemeIcon("media-playback-pause"), "Pause", self)
        self.connect(self.pauseMacroAction, Qt.SIGNAL("triggered()"), self.onPauseMacro)
        self.pauseMacroAction.setToolTip("Pause")
        self.playMacroAction = Qt.QAction(getThemeIcon("media-playback-start"), "Play", self)
        self.connect(self.playMacroAction, Qt.SIGNAL("triggered()"), self.onPlayMacro)
        self.playMacroAction.setToolTip("Play")
        
        actionsLayout = Qt.QHBoxLayout()
        actionsLayout.setContentsMargins(0,0,0,0)
        addToFavouritsButton = Qt.QToolButton()
        addToFavouritsButton.setDefaultAction(self.addToFavouritesAction)
        self.addToFavouritesAction.setEnabled(False)
        actionsLayout.addWidget(addToFavouritsButton)
        self.macroComboBox = MacroComboBox()
        self.macroComboBox.setUseParentModel(True)
        self.macroComboBox.setModel("/MacroList")
        self.macroComboBox.setModelColumn(0)        
        actionsLayout.addWidget(self.macroComboBox)
        stopMacroButton = Qt.QToolButton()
        stopMacroButton.setDefaultAction(self.stopMacroAction)
        actionsLayout.addWidget(stopMacroButton)
        pauseMacroButton = Qt.QToolButton()
        pauseMacroButton.setDefaultAction(self.pauseMacroAction)
        actionsLayout.addWidget(pauseMacroButton)
        self.playMacroButton = Qt.QToolButton()
        self.playMacroButton.setDefaultAction(self.playMacroAction)
        actionsLayout.addWidget(self.playMacroButton)
        self.disableControlActions()
        self.doorStateLed = TaurusLed(self)
        actionsLayout.addWidget(self.doorStateLed)
        self.layout().addLayout(actionsLayout)
        
        self._paramEditorModel = ParamEditorModel()
        self.stackedWidget = Qt.QStackedWidget(self)
        self.standardMacroParametersEditor = StandardMacroParametersEditor(self.stackedWidget)
        self.stackedWidget.addWidget(self.standardMacroParametersEditor)
        self.customMacroParametersEditor = None
        
        self._favouritesBuffer = None
        self.favouritesMacrosEditor = FavouritesMacrosEditor(self)
        self.registerConfigDelegate(self.favouritesMacrosEditor)
        self.favouritesMacrosEditor.setUseParentModel(True)
        self.favouritesMacrosEditor.setFocusPolicy(Qt.Qt.NoFocus)
        
        splitter = Qt.QSplitter(self)
        splitter.setOrientation(Qt.Qt.Vertical)
        splitter.addWidget(self.stackedWidget)
        splitter.addWidget(self.favouritesMacrosEditor) 
        self.layout().addWidget(splitter)
        
        self.macroProgressBar = MacroProgressBar(self)
        self.layout().addWidget(self.macroProgressBar)
        
        spockCommandLabel = Qt.QLabel("Spock command:", self)
        spockCommandLabel.setFont(Qt.QFont("Courier",9))
        self.spockCommand = SpockCommandWidget(self)
        self.spockCommand.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Minimum)
        spockCommandLayout = Qt.QHBoxLayout()
        spockCommandLayout.setContentsMargins(0,0,0,0)
        spockCommandLayout.addWidget(spockCommandLabel)
        spockCommandLayout.addWidget(self.spockCommand)
        self.layout().addLayout(spockCommandLayout)
        
        self.connect(self.macroComboBox,Qt.SIGNAL("currentIndexChanged(QString)"), self.onMacroComboBoxChanged)
        self.connect(self.favouritesMacrosEditor.list, Qt.SIGNAL("favouriteSelected"), self.onFavouriteSelected)
        
    def macroId(self):
        return self._macroId
    
    def setMacroId(self, macroId):
        self._macroId = macroId
        
    def doorName(self):
        return self._doorName
    
    def setDoorName(self, doorName):
        self._doorName = doorName
        
    def setFavouritesBuffer(self, favouritesMacro):
        self._favouritesBuffer = favouritesMacro
        
    def favouritesBuffer(self):
        return self._favouritesBuffer
    
    def paramEditorModel(self):
        return self._paramEditorModel
    
    def setParamEditorModel(self, paramEditorModel):
        self._paramEditorModel = paramEditorModel
            
    def onMacroComboBoxChanged(self, macroName):
        macroName = str(macroName)
        if macroName == "":
            macroName, macroNode = None, None
#            macroNode = macro.MacroNode(name="")
            self.playMacroAction.setEnabled(False)
            self.addToFavouritesAction.setEnabled(False)
        else:
            macroNode = self.favouritesBuffer()
            self.setFavouritesBuffer(None)
    
            if macroNode is None:
                macroNode = self.getModelObj().getMacroNodeObj(macroName)
            
            self.playMacroAction.setEnabled(True)
            self.addToFavouritesAction.setEnabled(True)
                
        self.paramEditorModel().setRoot(macroNode)
        self.spockCommand.setModel(self.paramEditorModel())        
        if self.stackedWidget.count() == 2:
            self.stackedWidget.removeWidget(self.customMacroParametersEditor) 
            self.customMacroParametersEditor.setParent(None)
        self.customMacroParametersEditor = ParamEditorManager().getMacroEditor(macroName, self.stackedWidget)
        if self.customMacroParametersEditor:
            self.customMacroParametersEditor.setModel(self.paramEditorModel())
            self.stackedWidget.addWidget(self.customMacroParametersEditor)
            self.stackedWidget.setCurrentWidget(self.customMacroParametersEditor)
        else:    
            self.standardMacroParametersEditor.setModel(self.paramEditorModel())
        
        self.emit(Qt.SIGNAL("macroNameChanged"), macroName)
        
    def onFavouriteSelected(self, macroNode):   
        self.setFavouritesBuffer(macroNode)
        name = ""
        if not macroNode is None: 
            name = macroNode.name()
        self.macroComboBox.selectMacro(name)
            
    def onAddToFavourites(self):
        self.favouritesMacrosEditor.addMacro(deepcopy(self.paramEditorModel().root()))
        
    def onDoorChanged(self, doorName):
        self.setDoorName(doorName)
        if self.doorName() == "":
            self.doorStateLed.setModel(None)
            return
        self.doorStateLed.setModel(self.doorName() + "/State")
        
    def onPlayMacro(self):
        door = Device(self.doorName())
        if door.getState() == PyTango.DevState.ON:
            paramEditorModel = self.paramEditorModel() 
            macroNode = paramEditorModel.root()
            id = macroNode.assignId()
            self.setMacroId(id)
            params, alerts = macroNode.toRun()
            xmlString = paramEditorModel.toXmlString()
            if len(alerts) > 0:
                Qt.QMessageBox.warning(self,"Macro parameters warning", alerts)
                return
            door.runMacro(xmlString)
#            door.runMacro(str(macroNode.name()), params)
        else:
            Qt.QMessageBox.warning(self,"Error while starting macro", 
                                   "It was not possible to start macro, because state of the door was different than ON")
    
    def onResumeMacro(self):
        door = Device(self.doorName())
        if door.getState() == PyTango.DevState.STANDBY:
            door.command_inout("ResumeMacro")
        else:
            Qt.QMessageBox.warning(self,"Error while resuming macro", 
                                   "It was not possible to resume macro, because state of the door was different than STANDBY") 
            
    def onStopMacro(self):
        door = Device(self.doorName())
        if door.getState() == PyTango.DevState.RUNNING or door.getState() == PyTango.DevState.STANDBY:
            door.command_inout("Abort")
        else:
            Qt.QMessageBox.warning(self,"Error while stopping macro", 
                                   "It was not possible to stop macro, because state of the door was different than RUNNING or STANDBY")
    
    def onPauseMacro(self):
        door = Device(self.doorName())
        if door.getState() == PyTango.DevState.RUNNING:
            door.command_inout("PauseMacro")
        else:
            Qt.QMessageBox.warning(self,"Error while pausing macro", 
                                   "It was not possible to pause macro, because state of the door was different than RUNNING")
            
    #@Qt.pyqtSignature("macroStatusUpdated")
    def onMacroStatusUpdated(self, data):
        macro = data[0]
        data = data[1]
        if macro is None: return
        data = data[0]
        state, range, step, id = data["state"], data["range"], data["step"], data["id"]
        id = int(id)
        if id != self.macroId(): return
        elif state == "start":
            self.emit(Qt.SIGNAL("macroStarted"), "DoorOutput")
            self.macroProgressBar.setRange(range[0], range[1])
            self.playMacroAction.setEnabled(False)
            self.pauseMacroAction.setEnabled(True)
            self.stopMacroAction.setEnabled(True)
            self.emit(Qt.SIGNAL("plotablesFilterChanged"), None)
            self.emit(Qt.SIGNAL("plotablesFilterChanged"), standardPlotablesFilter)
        elif state == "pause":
            self.playAction2resumeAction()
            self.playMacroAction.setEnabled(True)
            self.pauseMacroAction.setEnabled(False)
        elif state == "resume":
            self.resumeAction2playAction()
            self.playMacroAction.setEnabled(False)
            self.pauseMacroAction.setEnabled(True)
        elif state == "stop":
            self.playMacroAction.setEnabled(True)
            self.pauseMacroAction.setEnabled(False)
            self.stopMacroAction.setEnabled(False)
        self.macroProgressBar.setValue(step)

    def disableControlActions(self):
        self.pauseMacroAction.setEnabled(False)
        self.stopMacroAction.setEnabled(False)
        self.playMacroAction.setEnabled(False)
        
    def playAction2resumeAction(self):
        Qt.QObject.disconnect(self.playMacroAction,
                                      Qt.SIGNAL("triggered()"),
                                      self.onPlayMacro)
        Qt.QObject.connect(self.playMacroAction,
                                      Qt.SIGNAL("triggered()"),
                                      self.onResumeMacro)
        self.playMacroAction.setToolTip("Resume macro")
        self.playMacroAction.setStatusTip("Resume macro")
        self.playMacroAction.setText("Resume macro")
            
    def resumeAction2playAction(self):
        Qt.QObject.disconnect(self.playMacroAction,
                                      Qt.SIGNAL("triggered()"),
                                      self.onResumeMacro)
        Qt.QObject.connect(self.playMacroAction,
                                      Qt.SIGNAL("triggered()"),
                                      self.onPlayMacro)
        self.playMacroAction.setToolTip("Play macro")
        self.playMacroAction.setStatusTip("Play macro")
        self.playMacroAction.setText("Play macro")

    def setModel(self, model):
        TaurusWidget.setModel(self, model)
    
    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.extra_macroexecutor'
        ret['container'] = False
        return ret
    
    
class TaurusMacroExecutor(MacroExecutionWindow):
    
    def __init__(self, parent=None, designMode=False):
        MacroExecutionWindow.__init__(self, parent, designMode)
        
    def initComponents(self):
        self.taurusMacroExecutorWidget = TaurusMacroExecutorWidget(self)
        self.registerConfigDelegate(self.taurusMacroExecutorWidget)
        self.taurusMacroExecutorWidget.setUseParentModel(True)
        self.setCentralWidget(self.taurusMacroExecutorWidget)
                
    def setCustomMacroEditorPaths(self, customMacroEditorPaths):
        MacroExecutionWindow.setCustomMacroEditorPaths(self, customMacroEditorPaths)
        ParamEditorManager().parsePaths(customMacroEditorPaths)
        ParamEditorManager().browsePaths()
            
    def loadSettings(self):
        TaurusMainWindow.loadSettings(self)
        self.emit(Qt.SIGNAL("doorChanged"), self.doorName())
        
    def onDoorChanged(self, doorName):
        MacroExecutionWindow.onDoorChanged(self, doorName)
        if self._qDoor:
            Qt.QObject.disconnect(self._qDoor, Qt.SIGNAL("macroStatusUpdated"), self.taurusMacroExecutorWidget.onMacroStatusUpdated)
        if doorName == "": return
        self._qDoor = Device(doorName)
        Qt.QObject.connect(self._qDoor, Qt.SIGNAL("macroStatusUpdated"), self.taurusMacroExecutorWidget.onMacroStatusUpdated)
        self.taurusMacroExecutorWidget.onDoorChanged(doorName)
        
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None
            
    
def createMacroExecutorWidget(args):
    macroExecutor = TaurusMacroExecutorWidget()
    macroExecutor.setModelInConfig(True)
    Qt.QObject.connect(macroExecutor, Qt.SIGNAL("doorChanged"), macroExecutor.onDoorChanged)
    if len(args) == 2:
        macroExecutor.setModel(args[0])
        macroExecutor.emit(Qt.SIGNAL('doorChanged'),args[1])
    return macroExecutor

def createMacroExecutor(args):
    macroExecutor = TaurusMacroExecutor()
    macroExecutor.setCustomMacroEditorPaths("/home/zreszela/workspace/Taurus/lib/taurus/qt/qtgui/extra_macroexecutor/macroparameterseditor/customeditors")
    macroExecutor.setModelInConfig(True)
    Qt.QObject.connect(macroExecutor, Qt.SIGNAL("doorChanged"), macroExecutor.onDoorChanged)
    if len(args) == 2:
        macroExecutor.setModel(args[0])
        macroExecutor.emit(Qt.SIGNAL('doorChanged'),args[1])
    macroExecutor.loadSettings()
    return macroExecutor
    
        
if __name__ == "__main__": 
    from taurus.qt.qtgui.application import TaurusApplication  
    
    app = TaurusApplication(sys.argv)
    args = app.get_command_line_args()    
    
    app.setOrganizationName("Taurus")
    app.setApplicationName("macroexecutor")
    macroExecutor = createMacroExecutor(args)
    macroExecutor.show()
    sys.exit(app.exec_())
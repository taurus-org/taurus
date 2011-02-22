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

from PyQt4 import Qt
import PyTango
import taurus
from taurus.qt.qtgui.input import TaurusAttrListComboBox
from taurus.qt.qtgui.container import TaurusMainWindow

from taurus.qt.qtgui.resource import getThemeIcon

def str2bool(text):
    return text in ("True", "1")

class MSAttrListComboBox(TaurusAttrListComboBox):
    
    def __init__(self, parent=None):
        TaurusAttrListComboBox.__init__(self, parent)
        
    def prepareAttrList(self, value):
        lines = list(value)
        items = []
        for line in lines:
            items.append(line.split()[0])
        items.sort()       
        return items
        
    def setModel(self, model):
        TaurusAttrListComboBox.setModel(self, model)
        valueObj = self.getModelObj().getValueObj()
        #@todo: remove this condition when MS is fixed to return empty list as a value in case of empty attribute
        if valueObj.is_empty:
            value = []
        else:
            value = getattr(valueObj, "value", [])
        items = self.prepareAttrList(value)
        self.addItems(items) 
    
    def handleEvent(self, evt_src, evt_type, evt_value):
        text = self.currentText()
        self.clear()
        if evt_src and evt_value:
            value = evt_value.value
            if value is None: 
                return
            items = self.prepareAttrList(value)
            items.sort()       
            self.addItems(items)
        self.setCurrentText(text)
    
    def setCurrentText(self, text):
        idx = self.findText(text)
        self.setCurrentIndex(idx)


class MacroComboBox(TaurusAttrListComboBox):
    """Combobox with inherited from TaurusAttrListComboBox for MacroList attribute 
       of the MacroServer with one special blank item at the beginning"""
       
    def __init__(self, parent=None):
        TaurusAttrListComboBox.__init__(self, parent)
        self.setSizeAdjustPolicy(Qt.QComboBox.AdjustToContentsOnFirstShow)
        self.setToolTip("Choose a macro name...")
        
    def addBlankField(self):
        """This method adds an extra empty field in the combobox"""
        self.insertItem(0,"")
        self.setCurrentIndex(0)
        
    def selectMacro(self, macroName):
        currentIdx = self.currentIndex()
        index = self.findText(macroName)
        self.setCurrentIndex(index)
        if currentIdx == index:
            self.emit(Qt.SIGNAL("currentIndexChanged(QString)"), macroName)
        
    def handleEvent(self, src, type, value):
        TaurusAttrListComboBox.handleEvent(self, src, type, value)
        self.addBlankField() 

class TaurusMacroConfigurationDialog(Qt.QDialog):
    
    def __init__(self, parent=None, initMacroServer=None, initDoor=None):
        Qt.QDialog.__init__(self,parent)
        self.initMacroServer = initMacroServer
        self.initDoor = initDoor
        configureAction = Qt.QAction(getThemeIcon("folder-open"), "Change custom macro editors paths", self)
        self.connect(configureAction, Qt.SIGNAL("triggered()"), self.onReloadMacroServers)
        configureAction.setToolTip("Change custom macro editors paths")
        configureAction.setShortcut("F11")
        self.refreshMacroServersAction = Qt.QAction(getThemeIcon("view-refresh"), "Reload macroservers", self)
        self.connect(self.refreshMacroServersAction, Qt.SIGNAL("triggered()"), self.onReloadMacroServers)
        self.refreshMacroServersAction.setToolTip("This will reload list of all macroservers from Tango DB")
        self.refreshMacroServersAction.setShortcut("F5")
        self.initComponents()
        
    def initComponents(self):
        self.setModal(True)
        macroServerLabel = Qt.QLabel("MacroServer:", self)
        self.macroServerComboBox = Qt.QComboBox()
        ms_stateIcons = self.__retriveMacroServersFromDB()
        self.__fillMacroServerComboBox(ms_stateIcons, self.macroServerComboBox)
        refreshMacroServersButton = Qt.QToolButton()
        refreshMacroServersButton.setDefaultAction(self.refreshMacroServersAction)
        doorLabel = Qt.QLabel("Door:", self)
        self.doorComboBox = TaurusAttrListComboBox(self) 
        self.doorComboBox.setModel(self.macroServerComboBox.currentText() + "/doorList")
        
        self.buttonBox = Qt.QDialogButtonBox(Qt.QDialogButtonBox.Ok|
                                                Qt.QDialogButtonBox.Cancel)
        gridLayout = Qt.QGridLayout()
        gridLayout.addWidget(macroServerLabel,0,0)
        gridLayout.addWidget(self.macroServerComboBox,0,1)
        gridLayout.addWidget(refreshMacroServersButton,0,2)
        gridLayout.addWidget(doorLabel,1,0)
        gridLayout.addWidget(self.doorComboBox,1,1)
        
        self.setLayout(Qt.QVBoxLayout())
        self.layout().addLayout(gridLayout)
        self.layout().addWidget(self.buttonBox)
        self.adjustSize()
        
        self.connect(self.buttonBox, Qt.SIGNAL("accepted()"), self, Qt.SLOT("accept()"))
        self.connect(self.buttonBox, Qt.SIGNAL("rejected()"), self, Qt.SLOT("reject()"))
        self.connect(self.macroServerComboBox, Qt.SIGNAL("currentIndexChanged(const QString&)"),self.onMacroServerComboBoxChanged)
        self.selectMacroServer(self.initMacroServer)
        self.selectDoor(self.initDoor)
        
    def accept(self):
        self.emit(Qt.SIGNAL("macroserverNameChanged"), str(self.macroServerComboBox.currentText()))
        self.emit(Qt.SIGNAL("doorNameChanged"), str(self.doorComboBox.currentText()))
        Qt.QDialog.accept(self)
    
    def __retriveMacroServersFromDB(self):
        ms_stateIcons = []
        db = taurus.Database()
        macroServerList = db.getValueObj().get_device_name('*','MacroServer')
        for macroServer in macroServerList:
            #state = Device(macroServer).getState()
            state = None
            try:
                state = PyTango.DeviceProxy(macroServer).state()
            except:
                pass
            icon = None
            if state == PyTango.DevState.ON:
                icon = Qt.QIcon(":/leds/images24/ledgreen.png")
            elif state == PyTango.DevState.FAULT:
                icon = Qt.QIcon(":/leds/images24/ledred.png")
            elif state == None:
                icon = Qt.QIcon(":/leds/images24/ledredoff.png")
            ms_stateIcons.append((macroServer,icon))
        return ms_stateIcons
    
    def onReloadMacroServers(self):
        ms_stateIcons = self.__retriveMacroServersFromDB()
        self.__fillMacroServerComboBox(ms_stateIcons, self.macroServerComboBox)
    
    def onMacroServerComboBoxChanged(self, macroServerName):
        self.doorComboBox.setModel(macroServerName + "/doorList")
        
    def onMacroServerNameChanged(self, macroServerName):
        self.__selectMacroServer(macroServerName)
        
    def onDoorNameChanged(self, doorName):
        self.__selectDoor(doorName)
        
    def __fillMacroServerComboBox(self, ms_stateIcons, comboBox):
        comboBox.clear()
        for ms_stateIcon in ms_stateIcons:
            macroServer = ms_stateIcon[0]
            icon = ms_stateIcon[1]
            comboBox.addItem(icon, macroServer)
            
    def selectDoor(self, doorName):
        if doorName is None:
            return
        #@todo: Change that it will be able to handle also full device names
        "/".join(doorName.split("/")[-3:])    
        index = self.doorComboBox.findText(doorName) 
        if index != -1:
            self.doorComboBox.setCurrentIndex(index)
        
    def selectMacroServer(self, macroServerName):
        if macroServerName is None:
            return
        #@todo: Change that it will be able to handle also full device names
        "/".join(macroServerName.split("/")[-3:])
        index = self.macroServerComboBox.findText(macroServerName) 
        if index != -1:
            self.macroServerComboBox.setCurrentIndex(index)
    
class MacroExecutionWindow(TaurusMainWindow):
    
    def __init__(self, parent=None, designMode=False):
        TaurusMainWindow.__init__(self, parent, designMode)
        self.setModelInConfig(True)
        self._doorName = ""
        self.registerConfigProperty("doorName", "setDoorName", "doorName")
        self._customMacroEditorPaths = ""
        self.registerConfigProperty("customMacroEditorPaths", "setCustomMacroEditorPaths", "customMacroEditorPaths")
        self._qDoor = None
        self.setWindowIcon(Qt.QIcon(":/apps/preferences-system-session.svg"))
        toolBar = self.basicTaurusToolbar()
        toolBar.setIconSize(Qt.QSize(24,24))
        self.configureAction = self.createConfigureAction()
        toolBar.addAction(self.configureAction)
        self.taurusMenu.addAction(self.configureAction)
        self.customMacroEditorsPathsAction = self.createCustomMacroEditorPathsAction()
        self.taurusMenu.addAction(self.customMacroEditorsPathsAction)
        self.addToolBar(toolBar)
        self.initComponents()
        self.splashScreen().finish(self)
        self.connect(self, Qt.SIGNAL("doorChanged"), self.onDoorChanged)
    
    def doorName(self):
        return self._doorName
    
    def setDoorName(self, doorName):
        self._doorName = doorName
        
    def onDoorChanged(self, doorName):
        self.setDoorName(doorName)
        
    def customMacroEditorPaths(self):
        return self._customMacroEditorPaths
    
    def setCustomMacroEditorPaths(self, customMacroEditorPaths):
        self._customMacroEditorPaths = customMacroEditorPaths
#        ParamEditorManager().parsePaths(customMacroEditorPaths)
#        ParamEditorManager().browsePaths()
        
    def onCustomMacroEditorPaths(self):
        paths = str(Qt.QInputDialog.getText(self, 
                                "Edition of custom macro editors paths", 
                                "Paths:", Qt.QLineEdit.Normal, 
                                str(self.customMacroEditorPaths()))[0])
        self.setCustomMacroEditorPaths(paths)
        
    def initComponents(self):
        pass
        
    def setModel(self, model):
        """Sets new model for application, and change window title witn new macroserver name."""
        TaurusMainWindow.setModel(self, model)
        self.setWindowTitle(Qt.QApplication.applicationName() + ": " + model)
        
    def createConfigureAction(self):
        configureAction = Qt.QAction(getThemeIcon("preferences-system-session"), "Change configuration", self)
        self.connect(configureAction, Qt.SIGNAL("triggered()"), self.changeConfiguration)
        configureAction.setToolTip("Configuring MacroServer and Door")
        configureAction.setShortcut("F10")
        return configureAction
    
    def createCustomMacroEditorPathsAction(self):
        configureAction = Qt.QAction(getThemeIcon("folder-open"), "Change custom macro editors paths", self)
        self.connect(configureAction, Qt.SIGNAL("triggered()"), self.onCustomMacroEditorPaths)
        configureAction.setToolTip("Change custom macro editors paths")
        configureAction.setShortcut("F11")
        return configureAction

    def changeConfiguration(self):
        """This method is used to change macroserver as a model of application.
           It shows dialog with list of all macroservers on tango host, if the user
           Cancel dialog it doesn't do anything."""
        dialog = TaurusMacroConfigurationDialog(self, self.modelName, self.doorName())
        if dialog.exec_():
            self.setModel(str(dialog.macroServerComboBox.currentText()))
            self.emit(Qt.SIGNAL("doorChanged"), str(dialog.doorComboBox.currentText()))
        else:
            return
                    
if __name__ == "__main__": 
    import sys    
    app = Qt.QApplication(sys.argv)
    dialog = MacroExecutionWindow()
    dialog.show()
    sys.exit(app.exec_())
        
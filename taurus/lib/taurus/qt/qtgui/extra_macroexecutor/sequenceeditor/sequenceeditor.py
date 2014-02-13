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
import os, sys

from taurus.qt import Qt
import PyTango

from lxml import etree
from taurus.qt.qtgui.extra_macroexecutor.common import MacroExecutionWindow, MacroComboBox, standardPlotablesFilter
from taurus import Device

from taurus.qt.qtgui.container import TaurusMainWindow, TaurusWidget
from taurus.qt.qtcore.configuration import BaseConfigurableClass
from taurus.qt.qtgui.display import TaurusLed
from taurus.qt.qtgui.dialog import TaurusMessageBox

from taurus.qt.qtgui.extra_macroexecutor.macroparameterseditor import ParamEditorManager, StandardMacroParametersEditor
from taurus.qt.qtgui.extra_macroexecutor.macroparameterseditor.delegate import ParamEditorDelegate
from taurus.core.tango.sardana.macro import MacroRunException, MacroNode
from model import MacroSequenceTreeModel, MacroSequenceProxyModel, MacroParametersProxyModel
from delegate import SequenceEditorDelegate
from taurus.qt.qtgui.extra_macroexecutor import globals

from taurus.qt.qtgui.resource import getIcon, getThemeIcon


class HookAction(Qt.QAction):
    
    def __init__(self, text, parent, macroNode):
        Qt.QAction.__init__(self, text, parent)
        self.setCheckable(True)
        self.setMacroNode(macroNode)
        if text in self.macroNode().hookPlaces():
            self.setChecked(True)
        self.setToolTip("This macro will be executed as a %s" % text)
        self.connect(self, Qt.SIGNAL('toggled(bool)'), self.onToggle)
    
    def macroNode(self):
        return self._macroNode
    
    def setMacroNode(self, macroNode):
        self._macroNode = macroNode
        
    def onToggle(self, trueFalse):
        if trueFalse:
            self.macroNode().addHookPlace(str(self.text()))
        else:
            self.macroNode().removeHookPlace(str(self.text()))

class MacroSequenceTree(Qt.QTreeView, BaseConfigurableClass):
    
    def __init__(self, parent=None):
        Qt.QTreeView.__init__(self, parent)
        BaseConfigurableClass.__init__(self)
        self._idIndexDict = {}
        
        self.setSelectionBehavior(Qt.QTreeView.SelectRows)
        self.setSelectionMode(Qt.QTreeView.SingleSelection)
        self.setRootIsDecorated(False)
#        self.setItemsExpandable(False)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setTabKeyNavigation(True)
        self.setEditTriggers(Qt.QAbstractItemView.EditKeyPressed | Qt.QAbstractItemView.CurrentChanged)
        self.setDropIndicatorShown(True)

        self.deleteAction = Qt.QAction(getThemeIcon("list-remove"), "Remove macro", self)
        self.connect(self.deleteAction, Qt.SIGNAL("triggered()"), self.deleteMacro)
        self.deleteAction.setToolTip("Clicking this button will remove current macro.")
           
        self.moveUpAction = Qt.QAction(getThemeIcon("go-up"), "Move up", self)
        self.connect(self.moveUpAction, Qt.SIGNAL("triggered()"), self.upMacro)
        self.moveUpAction.setToolTip("Clicking this button will move current macro up.")
        
        self.moveDownAction = Qt.QAction(getThemeIcon("go-down"), "Move down", self)
        self.connect(self.moveDownAction, Qt.SIGNAL("triggered()"), self.downMacro)
        self.moveDownAction.setToolTip("Clicking this button will move current macro down.")
        
        self.moveLeftAction = Qt.QAction(getThemeIcon("go-previous"), "Move left", self)
        self.connect(self.moveLeftAction, Qt.SIGNAL("triggered()"), self.leftMacro)
        self.moveLeftAction.setToolTip("Clicking this button will move current macro to the left.")
        
        self.moveRightAction = Qt.QAction(getThemeIcon("go-next"), "Move right", self)
        self.connect(self.moveRightAction, Qt.SIGNAL("triggered()"), self.rightMacro)
        self.moveRightAction.setToolTip("Clicking this button will move current macro to the right.")
                
    def disableActions(self):
        self.deleteAction.setEnabled(False)
        self.moveUpAction.setEnabled(False)
        self.moveDownAction.setEnabled(False)
        self.moveLeftAction.setEnabled(False)
        self.moveRightAction.setEnabled(False)
   
    def contextMenuEvent(self, event):
        contextMenu = Qt.QMenu()
        proxyIndex = self.indexAt(event.pos())
        node = self.model().nodeFromIndex(proxyIndex)
        #this is in case if we right click on an empty field of tree
        if not isinstance(node, MacroNode): return
        parentNode = node.parent()
        #this is in case if we right click on a top level macro
        if not isinstance(parentNode, MacroNode): return
        allowedHooks = parentNode.allowedHookPlaces()
        if allowedHooks:
            hookPlacesSubmenu = contextMenu.addMenu("Hook places")
            for allowedHook in allowedHooks:
                action = HookAction(allowedHook, self, node)
                hookPlacesSubmenu.addAction(action)
        contextMenu.exec_(event.globalPos())

#    def setHint(self, add):
#        action = self.sender()
#        hookText = action.text()
#        macroNode = action.macroNode()
#        if add:
#            macroNode.addHook(hookText)
#        else:
#            macroNode.removeHook(hookText)
#        pass
            
    def selectionChanged(self, selected, deselected):       
        self.disableActions()
        macroName = None
        node, proxyIndex = self.selectedNodeAndIndex()
        if node is not None:
            macroName = node.name()
            self.deleteAction.setEnabled(True)
            self.moveUpAction.setEnabled(node.isAllowedMoveUp())
            self.moveDownAction.setEnabled(node.isAllowedMoveDown())
            self.moveLeftAction.setEnabled(node.isAllowedMoveLeft())
            self.moveRightAction.setEnabled(node.isAllowedMoveRight()) 
            sourceIndex = self.model().mapToSource(proxyIndex)
            self.emit(Qt.SIGNAL("macroChanged"), sourceIndex)
        self.emit(Qt.SIGNAL("macroNameChanged"), macroName)
        
    def expanded(self):
        for column in range(self.model().columnCount(Qt.QModelIndex())):
            self.resizeColumnToContents(column)
    
    def clearTree(self):
        self.model().clearSequence()
        
    def toXmlString(self, pretty=False, withId=True):
        return self.model().toXmlString(pretty=pretty, withId=withId)
            
    def fromXmlString(self, xmlString):
        newRoot = self.model().fromXmlString(xmlString)
        self.expandAll()
        self.expanded()
        return newRoot
    
    def fromPlainText(self, plainText):
        newRoot = self.model().fromPlainText(plainText)
        self.expandAll()
        self.expanded()
        return newRoot
    
    def root(self):
        return self.model().root()
    
    def setRoot(self, root):
        self.model().setRoot(root)
        self.model().reset()

    def addMacro(self, macroNode):
        node, proxyIndex = self.selectedNodeAndIndex()
        if node == None or not node.isAllowedHooks():
            proxyIndex = self.rootIndex()
        sourceIndex = self.model().mapToSource(proxyIndex)
        newSourceIndex = self.model()._insertRow(sourceIndex, macroNode)
        newProxyIndex = self.model().mapFromSource(newSourceIndex)
#        persistentProxyIndex = Qt.QPersistentModelIndex(newProxyIndex)
#        self._idIndexDict[macroNode.id()] = persistentProxyIndex
        self.setCurrentIndex(newProxyIndex)
        self.expandAll()
        self.expanded()

    def deleteMacro(self):
        node, proxyIndex = self.selectedNodeAndIndex()
        sourceIndex = self.model().mapToSource(proxyIndex)
        self.model()._removeRow(sourceIndex)
#        self._idIndexDict.pop(node.id())
        self.expandAll()
        self.expanded()
    
    def upMacro(self):
        node, proxyIndex = self.selectedNodeAndIndex()
        sourceIndex = self.model().mapToSource(proxyIndex)
        newSourceIndex = self.model()._upRow(sourceIndex)
        newProxyIndex = self.model().mapFromSource(newSourceIndex)
#        persistentProxyIndex = Qt.QPersistentModelIndex(newProxyIndex)
#        self._idIndexDict[node.id()] = persistentProxyIndex 
        self.setCurrentIndex(newProxyIndex)
        self.expandAll()
#        self.expanded()
        
    def downMacro(self):
        node, proxyIndex = self.selectedNodeAndIndex()
        sourceIndex = self.model().mapToSource(proxyIndex)
        newSourceIndex = self.model()._downRow(sourceIndex)
        newProxyIndex = self.model().mapFromSource(newSourceIndex)
#        persistentProxyIndex = Qt.QPersistentModelIndex(newProxyIndex)
#        self._idIndexDict[node.id()] = persistentProxyIndex 
        self.setCurrentIndex(newProxyIndex)
        self.expandAll()
#        self.expanded()
        
    def leftMacro(self):
        node, proxyIndex = self.selectedNodeAndIndex()
        sourceIndex = self.model().mapToSource(proxyIndex)
        newSourceIndex = self.model()._leftRow(sourceIndex)
        newProxyIndex = self.model().mapFromSource(newSourceIndex)
#        persistentProxyIndex = Qt.QPersistentModelIndex(newProxyIndex)
#        self._idIndexDict[node.id()] = persistentProxyIndex 
        self.setCurrentIndex(newProxyIndex)
        self.expandAll()
        self.expanded()
    
    def rightMacro(self):
        node, proxyIndex = self.selectedNodeAndIndex()
        sourceIndex = self.model().mapToSource(proxyIndex)
        newSourceIndex = self.model()._rightRow(sourceIndex)
        newProxyIndex = self.model().mapFromSource(newSourceIndex)
#        persistentProxyIndex = Qt.QPersistentModelIndex(newProxyIndex)
#        self._idIndexDict[node.id()] = persistentProxyIndex
        self.setCurrentIndex(newProxyIndex)
        self.expandAll()
        self.expanded()
        
    def prepareMacroIds(self):
        model = self.model()
        ids = model.assignIds()
        firstId = model.firstMacroId()
        lastId = model.lastMacroId()
        return firstId, lastId, ids
        
    def prepareMacroProgresses(self):
        self._idIndexDict = self.model().createIdIndexDictionary()
        for macroId in self._idIndexDict.iterkeys():
            self.setProgressForMacro(macroId, 0) 
        
    def setProgressForMacro(self, macroId, progress):
        persistentIndex = self._idIndexDict.get(macroId, None)
        if persistentIndex == None: return 
        progressIndex = persistentIndex.sibling(persistentIndex.row(),2)
        index = Qt.QModelIndex(progressIndex)
        self.model().setData(index, Qt.QVariant(progress))
        
    def setRangeForMacro(self, macroId, range):
        persistentIndex = self._idIndexDict.get(macroId, None)
        if persistentIndex == None: return
        index = Qt.QModelIndex(persistentIndex)
        node = self.model().nodeFromIndex(index)
        node.setRange(range)
        
    def selectedNodeAndIndex(self):
        """Returns a tuple with selected internal model node object and QModelIndex 
        from current model."""
        for idx in self.selectedIndexes():
            if idx.column() == 0:
                node = self.model().nodeFromIndex(idx)
                break
        else:
            node, idx = None, None
        return node, idx
    
    def dropEvent(self, event):
        Qt.QTreeView.dropEvent(self, event)
        self.expandAll()
                   

class TaurusSequencerWidget(TaurusWidget):
    
    def __init__(self, parent = None, designMode = False):
        TaurusWidget.__init__(self, parent, designMode)
        self._macroIds = [] #list representing all macros ids (all from sequence) currently executed  
        self._sequencesPath = str(Qt.QDir.homePath())
        self._sequenceModel = MacroSequenceTreeModel()
        
        self.registerConfigProperty("sequencesPath", "setSequencesPath", "sequencesPath")
        
        self.setLayout(Qt.QVBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        splitter = Qt.QSplitter()
        self.layout().addWidget(splitter)
        splitter.setOrientation(Qt.Qt.Vertical)

        sequenceEditor = TaurusWidget()
        splitter.addWidget(sequenceEditor)
        sequenceEditor.setUseParentModel(True)
        sequenceEditor.setLayout(Qt.QVBoxLayout())
        sequenceEditor.layout().setContentsMargins(0,0,0,0)
        
        self.tree = MacroSequenceTree(sequenceEditor)        
        self.sequenceProxyModel = MacroSequenceProxyModel()
        self.sequenceProxyModel.setSourceModel(self._sequenceModel)
        self.tree.setModel(self.sequenceProxyModel)
        self.tree.setItemDelegate(SequenceEditorDelegate(self.tree))
        
        actionsLayout = Qt.QHBoxLayout()
        actionsLayout.setContentsMargins(0,0,0,0)
        self.newSequenceAction = Qt.QAction(getThemeIcon("document-new"), "New", self)
        self.connect(self.newSequenceAction, Qt.SIGNAL("triggered()"), self.onNewSequence)
        self.newSequenceAction.setToolTip("New sequence")
        self.newSequenceAction.setEnabled(False)
        newSequenceButton = Qt.QToolButton()
        newSequenceButton.setDefaultAction(self.newSequenceAction)
        actionsLayout.addWidget(newSequenceButton)
        
        self.openSequenceAction = Qt.QAction(getThemeIcon("document-open"), "Open...", self)
        self.connect(self.openSequenceAction, Qt.SIGNAL("triggered()"), self.onOpenSequence)
        self.openSequenceAction.setToolTip("Open sequence...")
        openSequenceButton = Qt.QToolButton()
        openSequenceButton.setDefaultAction(self.openSequenceAction)
        actionsLayout.addWidget(openSequenceButton)
        
        self.saveSequenceAction = Qt.QAction(getThemeIcon("document-save"), "Save...", self)
        self.connect(self.saveSequenceAction, Qt.SIGNAL("triggered()"), self.onSaveSequence)
        self.saveSequenceAction.setToolTip("Save sequence...")
        self.saveSequenceAction.setEnabled(False)        
        saveSequenceButton = Qt.QToolButton()
        saveSequenceButton.setDefaultAction(self.saveSequenceAction)
        actionsLayout.addWidget(saveSequenceButton)
        
        self.stopSequenceAction = Qt.QAction(getIcon(":/actions/media_playback_stop.svg"), "Stop", self)
        self.connect(self.stopSequenceAction, Qt.SIGNAL("triggered()"), self.onStopSequence)
        self.stopSequenceAction.setToolTip("Stop sequence")
        stopSequenceButton = Qt.QToolButton()
        stopSequenceButton.setDefaultAction(self.stopSequenceAction)
        actionsLayout.addWidget(stopSequenceButton)
        
        self.pauseSequenceAction = Qt.QAction(getIcon(":/actions/media_playback_pause.svg"), "Pause", self)
        self.connect(self.pauseSequenceAction, Qt.SIGNAL("triggered()"), self.onPauseSequence)
        self.pauseSequenceAction.setToolTip("Pause sequence")
        pauseSequenceButton = Qt.QToolButton()
        pauseSequenceButton.setDefaultAction(self.pauseSequenceAction)
        actionsLayout.addWidget(pauseSequenceButton)
        
        self.playSequenceAction = Qt.QAction(getIcon(":/actions/media_playback_start.svg"), "Play", self)
        self.connect(self.playSequenceAction, Qt.SIGNAL("triggered()"), self.onPlaySequence)
        self.playSequenceAction.setToolTip("Play sequence")
        playSequenceButton = Qt.QToolButton()
        playSequenceButton.setDefaultAction(self.playSequenceAction)
        actionsLayout.addWidget(playSequenceButton)
        
        self.doorStateLed = TaurusLed(self)
        actionsLayout.addWidget(self.doorStateLed)
        
        #@todo this feature will be replaced by checkboxes in the sequence tree view 
        #indicating clearing of the plot after execution 
        self.fullSequencePlotCheckBox = Qt.QCheckBox("Full sequence plot", self)
        self.connect(self.fullSequencePlotCheckBox, Qt.SIGNAL("toggled(bool)"), self.setFullSequencePlot)
        self.fullSequencePlotCheckBox.setChecked(True)
        actionsLayout.addWidget(self.fullSequencePlotCheckBox)
        
        spacerItem = Qt.QSpacerItem(0,0,Qt.QSizePolicy.Expanding,Qt.QSizePolicy.Fixed)
        actionsLayout.addItem(spacerItem)
        
        sequenceEditor.layout().addLayout(actionsLayout)

        macroLayout = Qt.QHBoxLayout()
        macroLayout.setContentsMargins(0,0,0,0)
        macroLabel = Qt.QLabel("Macro:")
        macroLayout.addWidget(macroLabel)
        self.macroComboBox = MacroComboBox(self)
        self.macroComboBox.setUseParentModel(True)
        self.macroComboBox.setModelColumn(0)
        self.macroComboBox.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Minimum)
        macroLayout.addWidget(self.macroComboBox)
        
        self.addMacroAction = Qt.QAction(getThemeIcon("list-add"), "Add macro...", self)
        self.connect(self.addMacroAction, Qt.SIGNAL("triggered()"), self.onAdd)
        self.addMacroAction.setToolTip("Clicking this button will add selected macro")
        self.addMacroAction.setEnabled(False)
        addButton = Qt.QToolButton()
        addButton.setDefaultAction(self.addMacroAction)
        macroLayout.addWidget(addButton)
        
        sequenceEditor.layout().addLayout(macroLayout)
        
        sequenceLayout = Qt.QHBoxLayout()
        sequenceLayout.addWidget(self.tree)
        
        layout = Qt.QVBoxLayout()
        delButton = Qt.QToolButton()
        delButton.setDefaultAction(self.tree.deleteAction)
        delButton.setEnabled(False)
        layout.addWidget(delButton)
        upButton = Qt.QToolButton()
        upButton.setDefaultAction(self.tree.moveUpAction)
        upButton.setEnabled(False)
        layout.addWidget(upButton)
        downButton = Qt.QToolButton()
        downButton.setDefaultAction(self.tree.moveDownAction)
        downButton.setEnabled(False)
        layout.addWidget(downButton)
        leftButton = Qt.QToolButton()
        leftButton.setDefaultAction(self.tree.moveLeftAction)
        leftButton.setEnabled(False)
        layout.addWidget(leftButton)
        rightButton = Qt.QToolButton()
        rightButton.setDefaultAction(self.tree.moveRightAction)
        rightButton.setEnabled(False)
        layout.addWidget(rightButton)
        spacerItem = Qt.QSpacerItem(0,40,Qt.QSizePolicy.Fixed,Qt.QSizePolicy.Expanding)
        layout.addItem(spacerItem)
        sequenceLayout.addLayout(layout)
        sequenceEditor.layout().addLayout(sequenceLayout)
        
        self.parametersProxyModel = MacroParametersProxyModel()
        self.parametersProxyModel.setSourceModel(self._sequenceModel)
        
        self.stackedWidget = Qt.QStackedWidget()
        splitter.addWidget(self.stackedWidget)
        self.standardMacroParametersEditor = StandardMacroParametersEditor(self.stackedWidget)
        self.standardMacroParametersEditor.setModel(self.parametersProxyModel)
        self.standardMacroParametersEditor.tree.setItemDelegate(ParamEditorDelegate(self.standardMacroParametersEditor.tree))
        self.stackedWidget.addWidget(self.standardMacroParametersEditor)
        self.customMacroParametersEditor = None
        
        self.connect(self.macroComboBox, Qt.SIGNAL("currentIndexChanged(QString)"), self.onMacroComboBoxChanged)
        self.connect(self.tree, Qt.SIGNAL("macroChanged"), self.setMacroParametersRootIndex)


    def contextMenuEvent(self,event):
        menu = Qt.QMenu()
        action = menu.addAction(getThemeIcon("view-refresh"), "Check door state", self.checkDoorState)
        menu.exec_(event.globalPos())
    
    def checkDoorState(self):
        '''Method used by "Check door state" action (available in the context
        menu). It is a workaround for situations when the event notification
        about the macro status does not reach the sequencer widget.'''

        door = Device(self.doorName())
        doorState = door.state()
        if doorState == PyTango.DevState.RUNNING:
            self.playSequenceAction.setEnabled(False)
            self.pauseSequenceAction.setEnabled(True)
            self.stopSequenceAction.setEnabled(True)
        elif doorState in (PyTango.DevState.ON, PyTango.DevState.ALARM):
            self.playSequenceAction.setEnabled(True)
            self.pauseSequenceAction.setEnabled(False)
            self.stopSequenceAction.setEnabled(False)
        elif doorState == PyTango.DevState.STANDBY:
            self.playSequenceAction.setEnabled(True)
            self.pauseSequenceAction.setEnabled(False)
            self.stopSequenceAction.setEnabled(True)
    
    
    def doorName(self):
        return self._doorName
        
    def setDoorName(self, doorName):
        self._doorName = doorName
        
    def firstMacroId(self):
        return self._firstMacroId
    
    def setFirstMacroId(self, firstMacroId):
        self._firstMacroId = firstMacroId
        
    def lastMacroId(self):
        return self._lastMacroId
    
    def setLastMacroId(self, lastMacroId):
        self._lastMacroId = lastMacroId
        
    def macroIds(self):
        return self._macroIds
    
    def setMacroIds(self, macroIds):
        self._macroIds = macroIds
        
    def emitExecutionStarted(self):
        return self._emitExecutionStarted
    
    def setEmitExecutionStarted(self, yesNo):
        self._emitExecutionStarted = yesNo
        
    def sequencesPath(self):
        return self._sequencesPath
    
    def setSequencesPath(self, sequencesPath):
        self._sequencesPath = sequencesPath
        
    def isFullSequencePlot(self):
        return self._fullSequencePlot
    
    def setFullSequencePlot(self, fullSequencePlot):
        self._fullSequencePlot = fullSequencePlot
                
    def onNewSequence(self):
        if Qt.QMessageBox.question(self,
                                   "New sequence", 
                                   "Do you want to save existing sequence?",
                                   Qt.QMessageBox.Yes,
                                   Qt.QMessageBox.No) == Qt.QMessageBox.Yes:
            self.onSaveSequence()
        self.tree.clearTree()
        self.newSequenceAction.setEnabled(False)
        self.saveSequenceAction.setEnabled(False)
        self.emit(Qt.SIGNAL("currentMacroChanged"), None)
    
    def onOpenSequence(self):
        if not self._sequenceModel.isEmpty():
            if Qt.QMessageBox.question(self,
                                       "Open sequence", 
                                       "Do you want to save existing sequence?",
                                       Qt.QMessageBox.Yes,
                                       Qt.QMessageBox.No) == Qt.QMessageBox.Yes:
                self.onSaveSequence()
                self.tree.clearTree()
                
        sequencesPath = self.sequencesPath()
        fileName = str(Qt.QFileDialog.getOpenFileName(self,
                                                     "Choose a sequence to open...",
                                                     sequencesPath,
                                                     "*"))
        if fileName == "": return
        #@todo: reset macroComboBox to index 0
        try: 
            file = open(fileName,'r')
            string = file.read()
            if fileName.endswith('.xml'):
                root = self.fromXmlString(string)
            else:
                root = self.fromPlainText(string)
            self._sequenceModel.setRoot(root)
            self.sequenceProxyModel.invalidateFilter()
            self.tree.expandAll()
            self.tree.expanded()
            self.parametersProxyModel.setMacroIndex(None)
            self.parametersProxyModel.invalidateFilter()
            
            if not self._sequenceModel.isEmpty():
                self.newSequenceAction.setEnabled(True)
                self.saveSequenceAction.setEnabled(True)
                self.playSequenceAction.setEnabled(True)
        except IOError:
            Qt.QMessageBox.warning(self,"Error while loading macros sequence", "There was a problem while reading from file: %s" % fileName)
            self.tree.clearTree()
            self.newSequenceAction.setEnabled(False)
            self.saveSequenceAction.setEnabled(False)
        except:
            self.tree.clearTree()
            self.playSequenceAction.setEnabled(False)
            self.newSequenceAction.setEnabled(False)
            self.saveSequenceAction.setEnabled(False)
            raise
        finally:
            if not file is None: file.close()
            self.setSequencesPath(str.join("/", fileName.rsplit("/")[:-1]))
        
        self.emit(Qt.SIGNAL("currentMacroChanged"), None)

    def onSaveSequence(self):
        sequencesPath = self.sequencesPath() 
        if sequencesPath == "":
            sequencesPath = str(Qt.QDir.homePath())
            
        sequencesPath = os.path.join(sequencesPath, "Untitled.xml")
        fileName = str(Qt.QFileDialog.getSaveFileName(self,
                                                     "Choose a sequence file name...",
                                                     sequencesPath,
                                                     "*.xml"))
        if fileName == "": return
        try:
            file = open(fileName, "w")
            file.write(self.tree.toXmlString(pretty=True, withId=False))
            self.setSequencesPath(str.join("/", fileName.rsplit("/")[:-1]))
        except Exception, e:
            Qt.QMessageBox.warning(self,"Error while saving macros sequence", "There was a problem while writing to the file: %s" % fileName)
            print e
        finally:
            if not file is None: file.close()
            
    def onPlaySequence(self):
        door = Device(self.doorName())
        doorState = door.state()
        if doorState == PyTango.DevState.ON or doorState == PyTango.DevState.ALARM:
            first, last, ids = self.tree.prepareMacroIds()
            self.setFirstMacroId(first)
            self.setLastMacroId(last)
            self.setMacroIds(ids)
            self.tree.prepareMacroProgresses()
            self.setEmitExecutionStarted(True)
            door.runMacro(self.tree.toXmlString())
        elif doorState == PyTango.DevState.STANDBY:
            door.command_inout("ResumeMacro")
        else:
            Qt.QMessageBox.warning(self,"Error while starting/resuming sequence", 
                                   "It was not possible to start/resume sequence, because state of the door was different than ON/STANDBY")
    
    def onStopSequence(self):
        door = Device(self.doorName())
        doorState = door.state() 
        if doorState in (PyTango.DevState.RUNNING,PyTango.DevState.STANDBY):
            door.command_inout("StopMacro")
        else:
            Qt.QMessageBox.warning(self,"Error while stopping sequence", 
                                   "It was not possible to stop sequence, because state of the door was different than RUNNING or STANDBY")
    
    def onPauseSequence(self):
        door = Device(self.doorName())
        doorState = door.state()
        if doorState == PyTango.DevState.RUNNING:
            door.command_inout("PauseMacro")
        else:
            Qt.QMessageBox.warning(self,"Error while pausing sequence", 
                                   "It was not possible to pause sequence, because state of the door was different than RUNNING") 
        
    def onMacroStatusUpdated(self, data):
        macro = data[0]
        if macro is None: return
        data = data[1][0]
        state, range, step, id = str(data["state"]), data["range"], data["step"], data["id"]
        if id is None: return
        id = int(id)
        if not id in self.macroIds(): return
        macroName = macro.name
        shortMessage = ""
        if state == "start":
            #@todo: Check this signal because it doesn't work, emitExecutionStarted is not set!!!
            if self.emitExecutionStarted(): 
                self.emit(Qt.SIGNAL("macroStarted"), "DoorOutput")
            self.tree.setRangeForMacro(id, range)
            self.playSequenceAction.setEnabled(False)
            self.pauseSequenceAction.setEnabled(True)
            self.stopSequenceAction.setEnabled(True)
            if id == self.firstMacroId():            
                self.emit(Qt.SIGNAL("plotablesFilterChanged"), None)
                self.emit(Qt.SIGNAL("plotablesFilterChanged"), standardPlotablesFilter)
                shortMessage = "Sequence started."
            elif not self.isFullSequencePlot():
                self.emit(Qt.SIGNAL("plotablesFilterChanged"), None)
            shortMessage += " Macro %s started." % macroName
        elif state == "pause":
            self.playSequenceAction.setText("Resume sequence")
            self.playSequenceAction.setToolTip("Resume sequence")
            self.playSequenceAction.setEnabled(True)
            self.pauseSequenceAction.setEnabled(False)
            shortMessage = "Macro %s paused." % macroName
        elif state == "resume":
            self.playSequenceAction.setText("Start sequence")
            self.playSequenceAction.setToolTip("Start sequence")
            self.playSequenceAction.setEnabled(False)
            self.pauseSequenceAction.setEnabled(True)
            shortMessage = "Macro %s resumed." % macroName
        elif state == "stop" or state == "finish":
            shortMessage = "Macro %s finished." % macroName
            if id == self.lastMacroId():
                self.playSequenceAction.setEnabled(True)
                self.pauseSequenceAction.setEnabled(False)
                self.stopSequenceAction.setEnabled(False)
                shortMessage += " Sequence finished."
        elif state == 'exception':
            self.playSequenceAction.setEnabled(True)
            self.pauseSequenceAction.setEnabled(False)
            self.stopSequenceAction.setEnabled(False)
            shortMessage = "Macro %s error." % macroName
            exc_value, exc_stack = data['exc_value'], data['exc_stack']
            exceptionDialog = TaurusMessageBox(MacroRunException, exc_value, exc_stack)
            exceptionDialog.exec_()
        elif state == 'abort':
            self.playSequenceAction.setText("Start sequence")
            self.playSequenceAction.setToolTip("Start sequence")
            self.playSequenceAction.setEnabled(True)
            self.pauseSequenceAction.setEnabled(False)
            self.stopSequenceAction.setEnabled(False)
            shortMessage = "Macro %s stopped." % macroName 
        elif state == "step":
            shortMessage = "Macro %s at %d %% of progress." % (macroName, step) 
        self.emit(Qt.SIGNAL("shortMessageEmitted"), shortMessage)    
        self.tree.setProgressForMacro(id, step)

    def onDoorChanged(self, doorName):
        self.setDoorName(doorName)
        if self.doorName() == "":
            self.doorStateLed.setModel(None)
            return
        self.doorStateLed.setModel(self.doorName() + "/State")
        doorState = Device(doorName).state()
        if doorState == PyTango.DevState.ON:
            self.playSequenceAction.setText("Start sequence")
            self.playSequenceAction.setToolTip("Start sequence")
            self.playSequenceAction.setEnabled(False)
            self.pauseSequenceAction.setEnabled(False)
            self.stopSequenceAction.setEnabled(False)
        elif doorState == PyTango.DevState.STANDBY:
            self.playSequenceAction.setText("Resume sequence")
            self.playSequenceAction.setToolTip("Resume sequence")
            self.playSequenceAction.setEnabled(True)
            self.pauseSequenceAction.setEnabled(False)
            self.stopSequenceAction.setEnabled(True)
        
    def setMacroParametersRootIndex(self, sourceIndex):
        parametersModel = self.standardMacroParametersEditor.tree.model()
        parametersModel.setMacroIndex(sourceIndex)
        parametersModel.invalidateFilter()
        proxyIndex = parametersModel.mapFromSource(sourceIndex)
        
        macroNode = sourceIndex.internalPointer()
        macroName = macroNode.name()
        
        if self.stackedWidget.count() == 2:
            self.stackedWidget.removeWidget(self.customMacroParametersEditor) 
            self.customMacroParametersEditor.setParent(None)
        self.customMacroParametersEditor = ParamEditorManager().getMacroEditor(macroName)        
        if self.customMacroParametersEditor:
            self.customMacroParametersEditor.setModel(parametersModel)
            self.customMacroParametersEditor.setRootIndex(proxyIndex)
            self.stackedWidget.addWidget(self.customMacroParametersEditor)
            self.stackedWidget.setCurrentWidget(self.customMacroParametersEditor)
        else:        
            self.standardMacroParametersEditor.tree.setRootIndex(proxyIndex)
            self.standardMacroParametersEditor.tree.expandAll()    
        
    def onMacroComboBoxChanged(self):
        macroName = str(self.macroComboBox.currentText())
        if macroName == "":
            self.addMacroAction.setEnabled(False)
        else:
            self.addMacroAction.setEnabled(True)
        self.emit(Qt.SIGNAL("macroNameChanged"), macroName)
        
    def onAdd(self):
        macroName = str(self.macroComboBox.currentText())
        macroNode = self.getModelObj().getMacroNodeObj(macroName)
        self.tree.addMacro(macroNode)
        self.saveSequenceAction.setEnabled(True)
        self.playSequenceAction.setEnabled(True)
        
    def isEmptySequence(self):
        return len(self.tree.root()) == 0
    
    def isMacroSelected(self):
        return len(self.tree.selectedIndexes()) == 2
    
    def emptySequence(self):
        self.tree.clearTree()
        self.disableButtons()
        self.emit(Qt.SIGNAL("currentMacroChanged"), None)
        self.emit(Qt.SIGNAL("sequenceEmpty"))
      
    def fromXmlString(self, xmlString):
        newRoot = self.tree.fromXmlString(xmlString)
        macroServerObj = self.getModelObj()
        for macroNode in newRoot.allMacros():
            macroServerObj.fillMacroNodeAdditionalInfos(macroNode)
        return newRoot
    
    def fromPlainText(self, plainText):
        newRoot = self.tree.fromPlainText(plainText)
        macroServerObj = self.getModelObj()
        for macroNode in newRoot.allMacros():
            macroServerObj.recreateMacroNodeAndFillAdditionalInfos(macroNode)
        return newRoot
    
    def setModel(self, model):
        oldModelObj = self.getModelObj()
        if oldModelObj is not None:
            self.disconnect(oldModelObj,Qt.SIGNAL("macrosUpdated"), self.macroComboBox.onMacrosUpdated)
        TaurusWidget.setModel(self, model)
        newModelObj = self.getModelObj()
        self.connect(newModelObj, Qt.SIGNAL("macrosUpdated"), self.macroComboBox.onMacrosUpdated)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return {'container': False, 
                'group': 'Taurus Sardana', 
                'module': 'taurus.qt.qtgui.extra_macroexecutor', 
                'icon': ':/designer/frame.png'}


class TaurusSequencer(MacroExecutionWindow):
    
    def __init__(self, parent = None, designMode = False):
        MacroExecutionWindow.__init__(self)
        
    def initComponents(self):
        #@todo: take care about storing model 
        self.setModelInConfig(True)
        self.taurusSequencerWidget = TaurusSequencerWidget(self)
        self.taurusSequencerWidget.setUseParentModel(True)
        self.registerConfigDelegate(self.taurusSequencerWidget)
        self.setCentralWidget(self.taurusSequencerWidget)
        self.connect(self.taurusSequencerWidget, Qt.SIGNAL('shortMessageEmitted'), self.onShortMessage)
        self.statusBar().showMessage("Sequencer ready")
        
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
            Qt.QObject.disconnect(self._qDoor, Qt.SIGNAL("macroStatusUpdated"), self.taurusSequencerWidget.onMacroStatusUpdated)
        if doorName == "": return
        self._qDoor = Device(doorName)
        Qt.QObject.connect(self._qDoor, Qt.SIGNAL("macroStatusUpdated"), self.taurusSequencerWidget.onMacroStatusUpdated)
        self.taurusSequencerWidget.onDoorChanged(doorName)
    
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None

        
def createSequencerWidget(args):
    sequencer = TaurusSequencerWidget()
    sequencer.setModelInConfig(True)
    Qt.QObject.connect(sequencer, Qt.SIGNAL("doorChanged"), sequencer.onDoorChanged)
    if len(args) == 2:
        sequencer.setModel(args[0])
        sequencer.emit(Qt.SIGNAL('doorChanged'), args[1])
    return sequencer

def createSequencer(args):
    sequencer = TaurusSequencer()
    sequencer.setModelInConfig(True)
    Qt.QObject.connect(sequencer, Qt.SIGNAL("doorChanged"), sequencer.onDoorChanged)
    if len(args) == 2:
        sequencer.setModel(args[0])
        sequencer.emit(Qt.SIGNAL('doorChanged'), args[1])
    sequencer.loadSettings()
    return sequencer
      
def main():      
    from taurus.qt.qtgui.application import TaurusApplication
    import taurus
#    from rfoo.utils import rconsole
#    rconsole.spawn_server()
    
    app = TaurusApplication(sys.argv, app_version=taurus.Release.version)
    args = app.get_command_line_args()

    app.setOrganizationName(globals.ORGANIZATION_NAME)
    app.setApplicationName(globals.SEQUENCER_APPLICATION_NAME)
    sequencer = createSequencer(args)
    sequencer.show()
    sys.exit(app.exec_())  
    
if __name__ == "__main__":
    main()

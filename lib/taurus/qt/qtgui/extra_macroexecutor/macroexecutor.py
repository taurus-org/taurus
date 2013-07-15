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

import PyTango

from taurus.qt import Qt
from taurus import Device
from taurus.qt.qtgui.container import TaurusWidget, TaurusMainWindow, TaurusBaseContainer
from taurus.qt.qtgui.display import TaurusLed
from taurus.qt.qtgui.dialog import TaurusMessageBox

from favouriteseditor import FavouritesMacrosEditor, HistoryMacrosViewer
from common import MacroComboBox, MacroExecutionWindow, standardPlotablesFilter
from taurus.qt.qtgui.extra_macroexecutor.macroparameterseditor import ParamEditorManager, ParamEditorModel, StandardMacroParametersEditor
from taurus.core.tango.sardana.macro import MacroRunException
from taurus.core.tango.sardana import macro


from taurus.qt.qtgui.resource import getIcon, getThemeIcon

        
class MacroProgressBar(Qt.QProgressBar):
    
    def __init__(self, parent=None):
        Qt.QProgressBar.__init__(self, parent)
        
class SpockCommandWidget(Qt.QLineEdit, TaurusBaseContainer):
    def __init__(self, name, parent=None, designMode = False):
        #self.newValue - is used as a flag to indicate whether a controlUp controlDown actions are used to iterate existing element or put new one
        #self.disableEditMode - flag, used to disable edition, when user enters name of the macro which is not valid (not allowed to edit in the yellow line)
        #                   switches off validation
        #disableSpockCommandUpdate - flag, it disables updates of the model when macro is edited by macroEditor
        
        Qt.QLineEdit.__init__(self, parent)
        TaurusBaseContainer.__init__(self, name, parent, designMode)

        self._model = None 
        self.setFont(Qt.QFont("Courier",9))
        palette = Qt.QPalette()
        palette.setColor(Qt.QPalette.Base, Qt.QColor('yellow'))
        self.setPalette(palette)
        self.currentIndex = Qt.QModelIndex()
        self.newValue = False
        self.disableSpockCommandUpdate = False
        self.disableEditMode = True
        self.setEnabled(False)
        
        self.setActions()
        self.connect(self,Qt.SIGNAL("textChanged(const QString &)"), self.textChanged)
        self.connect(self,Qt.SIGNAL("returnPressed()"), self.returnPressed)
        
    def setActions(self):
        self._downAction = Qt.QAction("downAction", self)
        self._upAction = Qt.QAction("upAction", self)
        self._ctrlDownAction = Qt.QAction("controlDownAction", self)
        self._ctrlUpAction = Qt.QAction("controlUpAction", self)
        
        self._ctrlDownAction.setShortcut(Qt.QKeySequence(Qt.Qt.CTRL + Qt.Qt.Key_Down))
        self._ctrlUpAction.setShortcut(Qt.QKeySequence(Qt.Qt.CTRL + Qt.Qt.Key_Up))
        self._downAction.setShortcuts([Qt.Qt.Key_Down])
        self._upAction.setShortcuts([Qt.Qt.Key_Up])
        
        self._ctrlDownAction.setShortcutContext (Qt.Qt.WidgetShortcut)
        self._ctrlUpAction.setShortcutContext (Qt.Qt.WidgetShortcut)
        self._downAction.setShortcutContext (Qt.Qt.WidgetShortcut)
        self._upAction.setShortcutContext (Qt.Qt.WidgetShortcut)
        
        self.addAction(self._ctrlDownAction)
        self.addAction(self._ctrlUpAction)
        self.addAction(self._downAction)
        self.addAction(self._upAction)
        self.connect(self._downAction, Qt.SIGNAL("triggered()"), self.downAction)
        self.connect(self._upAction, Qt.SIGNAL("triggered()"), self.upAction)
        self.connect(self._ctrlDownAction, Qt.SIGNAL("triggered()"), self.controlDownAction)
        self.connect(self._ctrlUpAction, Qt.SIGNAL("triggered()"), self.controlUpAction)
        
    def setCommand(self):
        command = self._model.toSpockCommand()
        command = command.replace("None", "").strip()
        if not self.disableSpockCommandUpdate:
            self.setText(command)
        
    def setModel(self, model):
        enable = bool(model)
        self.disableEditMode = not enable
        self.setEnabled(enable)
        self._model = model
        self.connect(self._model, Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.setCommand)
        self.connect(self._model, Qt.SIGNAL("modelReset()"), self.setCommand)
        
    def model(self):
        return self._model

    def getIndex(self, elementNumber = -1):
        #Returns QModelIndex of the required element (number of single parameter). If the elementNumber == -1 next single parameter index is returned.
        if elementNumber == -1:
            ix = self.currentIndex
            elementNumber = 1
        elif elementNumber == 0:
            return Qt.QModelIndex()
        else:
            ix=Qt.QModelIndex()
        
        (col, row, parentIdx)=(ix.column(), ix.row(), ix.parent())
        #to start from second column
        if col == -1 and row == -1:
            ix = self.forwardIdx(0, 1, ix)
        for i in range (0, elementNumber):
            #This condition in case we start tabbing with cursor on first column
            if col == 0:
                currentNode = self.model().nodeFromIndex(ix)
                if isinstance(currentNode, macro.SingleParamNode):
                    nextIdx = self.forwardIdx(row, 1, parentIdx)
                else:
                    nextIdx = self.forwardIdx(0, 1, ix)
            else:
                nextIdx = self.forwardIdx(row + 1, 1, parentIdx)
            #this condition in case there is no next index and we want to pass focus 
            #to next widget in parent obj
            if nextIdx == "term":
                return Qt.QModelIndex()
            ix = nextIdx
            (col, row, parentIdx)=(ix.column(), ix.row(), ix.parent())
        return ix
    
    def forwardIdx(self, row, col, parentIdx):
        #This method is moving down the tree to get next SingleParamNode index.
        try:
            proposalIdx = self.model().index(row, col, parentIdx)
        except AssertionError:

            if parentIdx.row() == -1:
                return Qt.QModelIndex() 
            grandParentIdx = parentIdx.parent()
            return self.forwardIdx(parentIdx.row() + 1, col, grandParentIdx)

        proposalNode = self.model().nodeFromIndex(proposalIdx)

        if isinstance(proposalNode, macro.SingleParamNode):
            return proposalIdx
        elif isinstance(proposalNode, macro.RepeatNode):
            return self.forwardIdx(0, 1, proposalIdx)
        elif isinstance(proposalNode, macro.RepeatParamNode):
            if len(proposalNode) > 0:
                return self.forwardIdx(0, 1, proposalIdx)
            else:
                return self.forwardIdx(row + 1, col, proposalIdx)

        elif not proposalIdx.isValid():
            proposalIdx = parentIdx.sibling(parentIdx.row()+1, 0)
            
            if proposalIdx.isValid():
                proposalIdx = proposalIdx.child(0,1)
            else:
                while not proposalIdx.isValid():
                    parentIdx = parentIdx.parent()
                    if not parentIdx.isValid():

                        return Qt.QModelIndex()
                    proposalIdx = parentIdx.sibling(parentIdx.row()+1, 1)

            return proposalIdx
   
    def validateAllExpresion(self, secValidation = False):
        #This method is responsible for full validation of the macro. It is executed whenever the text is changed (when user edits values).
        #Validation starts with checking if the macro (name) is valid.
        #Next steps:
        #1. Validates every SingleParamNode and counts how many there are in the macro.
        #2. If there are more SingleParamNodes than entered values it will check if there is RepeatParamNode.
        #   If there is RepeatParamNode it will check if its RepeatNodes can be deleted.
        #3. If there are more values entered than SingleParamNodes in macro it will check if there is RepeatParamNode.
        #   If there is it will try to add new RepeatNode.
        
        if self.model() is None:
            raise RuntimeError('Door must be set in order to use the macroexecutor.')
            
        self.currentIndex = Qt.QModelIndex()
        mlist = str(self.text()).split()
        problems = []
        try:
            if str(mlist[0]) != str(self.model().root().name()):
                try:
                    self.getModelObj().validateMacroName(str(mlist[0]))
                    self.validateMacro(mlist[0])
                    self.updateMacroEditor(mlist[0])
                    if not secValidation:
                        self.validateAllExpresion(True)
                    
                except Exception as e:
                    if self.disableEditMode:
                        self.updateMacroEditor(mlist[0])
                        raise Exception(e)
                    message = e[0]
                    #raise Exception(e)
                    problems.append(message)
                
        except IndexError:
                problems.append("<b>Macro<\b> is missing!")
                self.setStyleSheet("")
                self.setToolTip('<br>'.join(problems))
                return
            
        self.currentIndex = Qt.QModelIndex()
        ix = self.getIndex()
        self.currentIndex = ix
        counter = 1
        while not ix == Qt.QModelIndex():
            try:
                propValue = mlist[counter]
                try:
                    self.validateOneValue(propValue)     
                    self.model().setData(self.currentIndex, Qt.QVariant(propValue))
                except Exception as e:
                    self.model().setData(self.currentIndex, Qt.QVariant('None'))
                    txt = str(Qt.from_qvariant(ix.sibling(ix.row(),0).data(), str))
                    message = "<b>" + txt + "</b> " + e[0]
                    problems.append(message)
            except IndexError:
                txt = str(Qt.from_qvariant(ix.sibling(ix.row(),0).data(), str))
                problems.append("<b>" + txt + "</b> is missing!")
                
                data = str(Qt.from_qvariant(ix.data(), str))
                if data != 'None':
                    self.model().setData(self.currentIndex, Qt.QVariant('None'))
            counter+=1
            ix = self.getIndex()
            self.currentIndex = ix

        if len(mlist) > counter: #if there are more values than parameters 
            repeatNode = None
            for i in self.model().root().params():
                repeatNode = i
                if isinstance(repeatNode, macro.RepeatParamNode):
                    index = self.findParamRepeat(i)
                    self.currentIndex = self.model()._insertRow(index)
                    nn = self.model().nodeFromIndex(self.currentIndex)
                    self.emit(Qt.SIGNAL("expandTree"))
                    ix = self.getIndex()
                    if not secValidation:
                        self.validateAllExpresion(True)
                        return 

                repeatNode = None
            if repeatNode == None:
                problems.append("Too many values.")
        
        elif counter - len(mlist) >= 1:
            repeatNode = None
            node = None
            for i in self.model().root().params():
                repeatNode = i
                if isinstance(repeatNode, macro.RepeatParamNode):
                    index = self.findParamRepeat(i)
                    node = self.model().nodeFromIndex(index)
                    sub = len(node.child(0))
                    break
                repeatNode = None
                
            if repeatNode is not None:
                while counter - len(mlist) > sub-1:
                    if len(node.children()) == 1 and node.isReachedMin():
                        break
                    self.model()._removeRow(index.child(len(node.children())-1,0))
                    counter -= sub
                    
                if not secValidation:
                    self.validateAllExpresion(True)
                    return
            
        if len(problems) == 0:
            self.setStyleSheet('SpockCommandWidget {background-color: %s; color: %s; border: %s; border-radius: %s}'%('yellow', 'black','3px solid green','5px'))
            self.setToolTip("")
        else:
            self.setStyleSheet("")
            self.setToolTip('<br>'.join(problems))   
        return 

    def findParamRepeat(self, repeatNode):
        #Method which finds index of given ParamRepeatNode in the macro.
        children = self.model().root().children()
        occ = children.count(repeatNode)
        idx = 0
        for i in range(0,occ):
            idx = children.index(repeatNode, idx)
        index = self.model().index(idx ,0, Qt.QModelIndex())
        return index

    def validateOneValue(self, value):
        #Validates value of a SingleParamNode of a currentIndex
        paramNode = deepcopy(self.model().nodeFromIndex(self.currentIndex))
        paramNode.setValue(value)
        return self.getModelObj().validateSingleParam(paramNode)
    
    def returnPressed(self):
        #SLOT called when return is pressed
        if self.toolTip() == "":
            self.emit(Qt.SIGNAL("pressedReturn"))
        else:
            raise Exception("Cannot start macro. Please correct following mistakes: <br>"+self.toolTip())
            
    def textChanged(self, strs):
        #SLOT called when QLineEdit text is changed
        if strs == "":
            self.updateMacroEditor("")
        
        if not self.disableEditMode and self.disableSpockCommandUpdate:
            self.validateAllExpresion()
        else:
            txt_parts = str(self.text()).split()
            if len(txt_parts) == 0:
                return
            try:
                if self.validateMacro(txt_parts[0]):
                    self.validateAllExpresion()
            except:
                self.setToolTip("Read Mode")
        
    def validateMacro(self, value):
        #Method which ivestigates if the macro can be edited using yellow line.
        #It cannot be executed when: 1. there are more than 1 ParamRepeatNodes,
        #2. There is a ParamRepeatNode inside ParamRepeatNodem
        #3. After ParamRepeatNode there are other nodes
        
        macroNode = self.getModelObj().getMacroNodeObj(str(value))
        if macroNode is None: return False
        t = [child for child in macroNode.children() if isinstance(child, macro.RepeatParamNode)]
        if len(t) > 1:
            self.disableEditMode = True
            raise Exception('Macro <b> %s </b> cannot be edited using yellow line.<br>It contains more than 1 paramRepeat node. <br>Please use Macro Editor Widget to edit and execute this macro.' %str(value))
        elif len(t) == 1:
            if len([child for child in t[0].children() if isinstance(child, macro.RepeatParamNode)]) > 0:
                self.disableEditMode = True
                raise Exception('Macro <b> %s </b> cannot be edited using yellow line.<br>It contains paramRepeat node inside paramRepeat node. <br>Please use Macro Editor Widget to edit and execute this macro.' %str(value))
            else:
                if macroNode.children().index(t[0]) != len(macroNode.children()) -1 :
                    self.disableEditMode = True
                    raise Exception('Macro <b> %s </b> cannot be edited using yellow line.<br>It contains paramRepeat node but not as a last parameter. <br>Please use Macro Editor Widget to edit and execute this macro.' %str(value))
        self.disableEditMode = False
        return True
    
    def downAction(self):
        #Goes down in the history list of executed macros.
        #self.disableSpockCommandUpdate flag is used to allow updating yellow line when model is changed. (when new row in history is chosen)
        
        self.disableSpockCommandUpdate = False
        self.emit(Qt.SIGNAL("elementDown"))
        text = str(self.text()).split()
        if len(text) > 0:
            self.validateMacro(text[0])
        self.disableSpockCommandUpdate = True
        
    def upAction(self):
        self.disableSpockCommandUpdate = False
        self.emit(Qt.SIGNAL("elementUp"))
        text = str(self.text()).split()
        if len(text) > 0:
            self.validateMacro(text[0])
        self.disableSpockCommandUpdate = True
        
    def controlDownAction(self):
        c = self.cursorPosition()
        newValue = False
        try:
            if self.text()[c] ==" " and self.text()[c-1] == " ":
                newValue = True
        except IndexError:
            if c == 0:
                newValue = True
            elif len(self.text()) == self.cursorPosition() and self.text()[c-1] == " ":
                newValue = True
        try:
            txt = str(self.text())
            txt = txt[:txt.find(" ",c)]
        except IndexError:
            txt = str(self.text())[:c]
        elementsNum = txt.split()
        
        if newValue:
            self.insert("0")
            self.currentIndex = self.getIndex(len(elementsNum))
            if not self.currentIndex.isValid():
                if len(elementsNum) > 0:
                    self.backspace()
                    return
            value = self.prevValue("")
            self.backspace()
            self.insert(value)
            self.model().setData(self.currentIndex, Qt.QVariant(value))
        else:
            self.currentIndex = self.getIndex(len(elementsNum)-1)
            if not self.currentIndex.isValid():
                if len(elementsNum) > 1:
                    return
            value = self.prevValue(elementsNum[len(elementsNum)-1])
            sel = self.measureSelection(self.cursorPosition())
            self.setSelection(sel[0], sel[1])
            c = c - (sel[1] - len(str(value)))
            self.insert(value)
            self.setCursorPosition(c)
            self.model().setData(self.currentIndex, Qt.QVariant(value))
            
    def controlUpAction(self):
        c = self.cursorPosition()
        newValue = False
        try:
            if self.text()[c] ==" " and self.text()[c-1] == " ":
                newValue = True
        except IndexError:
            if c == 0:
                newValue = True
            elif len(self.text()) == self.cursorPosition() and self.text()[c-1] == " ":
                newValue = True       
        try:
            txt = str(self.text())
            txt = txt[:txt.find(" ",c)]
        except IndexError:
            txt = str(self.text())[:c]
        elementsNum = txt.split()
        
        if newValue:
            self.insert("0")
            self.currentIndex = self.getIndex(len(elementsNum))
            if not self.currentIndex.isValid():
                if len(elementsNum) > 0:
                    self.backspace()
                    return
            value = self.nextValue("")
            self.backspace()
            self.insert(value)
            self.model().setData(self.currentIndex, Qt.QVariant(value))
        else:
            self.currentIndex = self.getIndex(len(elementsNum)-1)
            if not self.currentIndex.isValid():
                if len(elementsNum) > 1:
                    return
            value = self.nextValue(elementsNum[len(elementsNum)-1])
            sel = self.measureSelection(self.cursorPosition())
            self.setSelection(sel[0], sel[1])
            c = c - (sel[1] - len(str(value)))
            self.insert(value)
            self.setCursorPosition(c)
            self.model().setData(self.currentIndex, Qt.QVariant(value))

    def getParamItems(self, index):
        #Returns list of items that can be chosen for the node corresponding to the given index. Used by {next,prev}Value methods
        
        node = self.model().nodeFromIndex(index)
        if isinstance(node, macro.MacroNode):
            return None
        type = node.type()
        ms = self.getParentModelObj()
        items = ms.getElementsWithInterface(type).keys()
        return items, type
    
    def nextValue(self, current):
        current = str(current)
        if self.currentIndex.isValid():
            items, type = self.getParamItems(self.currentIndex)
            items = sorted(items)
        else:
            items = self.getParentModelObj().getMacroStrList()
            items = sorted(items)
            type = "Macro"
        
        if type == "Float":
            value = float(current) + 0.1
        elif type == "Integer":
            value = int(current) + 1
        elif type == "Boolean":
            value = True
        else:
            try:
                textindex = items.index(current)
                value = items[textindex-1]
            except:
                tmpitems = [s for s in items if s.startswith(current)]
                if len(tmpitems) > 0:
                    value = tmpitems[0]
                else:
                    value = items[0]
        return str(value)
    
    def prevValue(self, current):
        current = str(current)
        if self.currentIndex.isValid():
            items, type = self.getParamItems(self.currentIndex)
            items = sorted(items)
        else:
            items = self.getParentModelObj().getMacroStrList()
            items = sorted(items)
            type = "Macro"
        
        if type == "Float":
            value = float(current) - 0.1
        elif type == "Integer":
            value = int(current) - 1
        elif type == "Boolean":
            value = True
        else:
            try:
                textindex = items.index(current)
                value = items[textindex+1]
            except:
                tmpitems = [s for s in items if s.startswith(current)]
                if len(tmpitems)>0:
                    value = tmpitems[0]
                else:
                    value = items[0]
        return str(value)
    
    def updateMacroEditor(self, macroName):
        #I had to make the macroname lowered as macros in comboBox (with macros), has names with all letter low.
        #Because of that sometimes it was not loading macros in MacroEditor
        #TO FIX
        self.emit(Qt.SIGNAL("spockComboBox"), str(macroName).lower())
    
    def measureSelection(self, position):
        s = str(self.text())+" "
        try:
            if s[position] == " ":
                position-=1
        except IndexError:
            position -=1
        end = s.find(' ', position)
        beg = s.rfind(' ',0, position+1)
        if end == -1:
            end = s.length()-1
        return beg+1, end-beg-1 #returns the start and length of the value

    def focusInEvent(self, event):
        self.disableSpockCommandUpdate = True
        Qt.QLineEdit.focusInEvent(self,event)
    
    def focusOutEvent(self, event):
        self.disableSpockCommandUpdate = False
        Qt.QLineEdit.focusOutEvent(self, event)
        
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
        self.stopMacroAction = Qt.QAction(getIcon(":/actions/media_playback_stop.svg"), "Stop macro", self)
        self.connect(self.stopMacroAction, Qt.SIGNAL("triggered()"), self.onStopMacro)
        self.stopMacroAction.setToolTip("Stop macro")
        self.pauseMacroAction = Qt.QAction(getIcon(":/actions/media_playback_pause.svg"), "Pause macro", self)
        self.connect(self.pauseMacroAction, Qt.SIGNAL("triggered()"), self.onPauseMacro)
        self.pauseMacroAction.setToolTip("Pause macro")
        self.playMacroAction = Qt.QAction(getIcon(":/actions/media_playback_start.svg"), "Start macro", self)
        self.connect(self.playMacroAction, Qt.SIGNAL("triggered()"), self.onPlayMacro)
        self.playMacroAction.setToolTip("Start macro")
        actionsLayout = Qt.QHBoxLayout()
        actionsLayout.setContentsMargins(0,0,0,0)
        addToFavouritsButton = Qt.QToolButton()
        addToFavouritsButton.setDefaultAction(self.addToFavouritesAction)
        self.addToFavouritesAction.setEnabled(False)
        actionsLayout.addWidget(addToFavouritsButton)
        
        self.macroComboBox = MacroComboBox(self)
        self.macroComboBox.setUseParentModel(True)
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
        
        splitter = Qt.QSplitter(self)
        self.layout().addWidget(splitter)
        splitter.setOrientation(Qt.Qt.Vertical)
        
        self._paramEditorModel = ParamEditorModel()
        self.stackedWidget = Qt.QStackedWidget()
        self.standardMacroParametersEditor = StandardMacroParametersEditor(self.stackedWidget)
        self.stackedWidget.addWidget(self.standardMacroParametersEditor)
        self.customMacroParametersEditor = None
        splitter.addWidget(self.stackedWidget)
        
        self._favouritesBuffer = None
        self.favouritesMacrosEditor = FavouritesMacrosEditor(self)
        self.registerConfigDelegate(self.favouritesMacrosEditor)
        self.favouritesMacrosEditor.setUseParentModel(True)
        self.favouritesMacrosEditor.setFocusPolicy(Qt.Qt.NoFocus)
        
        self._historyBuffer = None
        self.historyMacrosViewer = HistoryMacrosViewer(self)
        self.registerConfigDelegate(self.historyMacrosViewer)
        self.historyMacrosViewer.setUseParentModel(True)
        self.historyMacrosViewer.setFocusPolicy(Qt.Qt.NoFocus)
        
        self.tabMacroListsWidget = Qt.QTabWidget(self)
        self.tabMacroListsWidget.addTab(self.favouritesMacrosEditor, "Favourite list")
        self.tabMacroListsWidget.addTab(self.historyMacrosViewer, "History Viewer")
        splitter.addWidget(self.tabMacroListsWidget)
    
        self._isHistoryMacro = False
        self.macroProgressBar = MacroProgressBar(self)
        self.layout().addWidget(self.macroProgressBar)
        
        #spockCommandLabel = Qt.QLabel("Spock command:", self)
        #spockCommandLabel.setFont(Qt.QFont("Courier",9))
        self.spockCommand = SpockCommandWidget("Spock", self)
        self.spockCommand.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Minimum)
        self.spockCommand.setUseParentModel(True)
        spockCommandLayout = Qt.QHBoxLayout()
        spockCommandLayout.setContentsMargins(0,0,0,0)
        #spockCommandLayout.addWidget(spockCommandLabel)
        spockCommandLayout.addWidget(self.spockCommand)
        self.layout().addLayout(spockCommandLayout)
        self.connect(self.macroComboBox,Qt.SIGNAL("currentIndexChanged(QString)"), self.onMacroComboBoxChanged)
        self.connect(self.favouritesMacrosEditor.list, Qt.SIGNAL("favouriteSelected"), self.onFavouriteSelected)
        self.connect(self.historyMacrosViewer.list, Qt.SIGNAL("historySelected"), self.onHistorySelected)
        
        self.connect(self.spockCommand, Qt.SIGNAL("pressedReturn"), self.onPlayMacro)
        self.connect(self.spockCommand, Qt.SIGNAL("spockComboBox"), self.setComboBoxItem)
        self.connect(self.spockCommand, Qt.SIGNAL("elementUp"), self.setHistoryUp)
        self.connect(self.spockCommand, Qt.SIGNAL("elementDown"), self.setHistoryDown)
        self.connect(self.spockCommand, Qt.SIGNAL("setHistoryFocus"), self.setHistoryFocus)
        self.connect(self.spockCommand, Qt.SIGNAL("expandTree"), self.standardMacroParametersEditor.tree.expandAll)

    def macroId(self):
        return self._macroId
    
    def contextMenuEvent(self,event):
        menu = Qt.QMenu()
        action = menu.addAction(getThemeIcon("view-refresh"), "Check door state", self.checkDoorState)
        menu.exec_(event.globalPos())
    
    def checkDoorState(self):
        door = Device(self.doorName())
        doorState = door.state()
        if doorState == PyTango.DevState.RUNNING:
            self.playMacroAction.setEnabled(False)
            self.pauseMacroAction.setEnabled(True)
            self.stopMacroAction.setEnabled(True)
        elif doorState == PyTango.DevState.ON or doorState == PyTango.DevState.ALARM:
            self.playMacroAction.setEnabled(True)
            self.pauseMacroAction.setEnabled(False)
            self.stopMacroAction.setEnabled(False)
        elif doorState == PyTango.DevState.STANDBY:
            self.playMacroAction.setEnabled(True)
            self.pauseMacroAction.setEnabled(False)
            self.stopMacroAction.setEnabled(True)
        
    def setMacroId(self, macroId):
        self._macroId = macroId
        
    def doorName(self):
        return self._doorName
    
    def setDoorName(self, doorName):
        self._doorName = doorName
        
    def setFavouritesBuffer(self, favouritesMacro):
        self._favouritesBuffer = favouritesMacro
        
    #History Widget
    def setHistoryUp(self):
        self.setHistoryFocus()
        self.historyMacrosViewer.listElementUp()
        
    def setHistoryDown(self):
        self.setHistoryFocus()
        self.historyMacrosViewer.listElementDown()
        
    def setHistoryFocus(self):
        self.tabMacroListsWidget.setCurrentWidget(self.historyMacrosViewer)
        #self.historyMacrosViewer.setFocus()
    
    def historyBuffer(self):
        return self._historyBuffer
    
    def setHistoryBuffer(self, favouritesMacro):
        self._historyBuffer = favouritesMacro
        
    def favouritesBuffer(self):
        return self._favouritesBuffer
        
    def paramEditorModel(self):
        return self._paramEditorModel
    
    def setParamEditorModel(self, paramEditorModel):
        self._paramEditorModel = paramEditorModel

    def setComboBoxItem(self, macroName):
        self.macroComboBox.selectMacro(macroName)

    def onMacroComboBoxChanged(self, macroName):
        macroName = str(macroName)
        if macroName == "":
            macroName, macroNode = None, None
#            macroNode = macro.MacroNode(name="")
            self.playMacroAction.setEnabled(False)
            self.addToFavouritesAction.setEnabled(False)
        else:
            if self._isHistoryMacro:
                macroNode = self.historyBuffer()
                self.setHistoryBuffer(None)
                self.favouritesMacrosEditor.list.clearSelection()
            else:
                macroNode = self.favouritesBuffer()
                self.setFavouritesBuffer(None)
                self.historyMacrosViewer.list.clearSelection()
            self._isHistoryMacro = False
    
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
        self._isHistoryMacro = False
        self.macroComboBox.selectMacro(name)
        
    def onHistorySelected(self, macroNode):
        self.setHistoryBuffer(macroNode)
        name = ""
        if not macroNode is None: 
            name = macroNode.name()
        self._isHistoryMacro = True
        self.macroComboBox.selectMacro(name)
    
    def onAddToFavourites(self):
        self.favouritesMacrosEditor.addMacro(deepcopy(self.paramEditorModel().root()))
    
    def addToHistory(self):
        self.historyMacrosViewer.addMacro(deepcopy(self.paramEditorModel().root()))
        
    def onDoorChanged(self, doorName):
        self.setDoorName(doorName)
        if self.doorName() == "":
            self.doorStateLed.setModel(None)
            return
        self.doorStateLed.setModel(self.doorName() + "/State")
        doorState = Device(doorName).state()
        if doorState == PyTango.DevState.ON:
            self.playMacroAction.setText("Start macro")
            self.playMacroAction.setToolTip("Start macro")
        elif doorState == PyTango.DevState.STANDBY:
            self.playMacroAction.setText("Resume macro")
            self.playMacroAction.setToolTip("Resume macro")
        
    def onPlayMacro(self):
        door = Device(self.doorName())
        doorState = door.state()
        if doorState == PyTango.DevState.ON or doorState == PyTango.DevState.ALARM:
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
            self.addToHistory()
#            door.runMacro(str(macroNode.name()), params)
        elif doorState == PyTango.DevState.STANDBY:
            door.command_inout("ResumeMacro")
        else:
            Qt.QMessageBox.warning(self,"Error while starting/resuming macro", 
                                   "It was not possible to start/resume macro, because state of the door was different than ON/STANDBY") 
            
    def onStopMacro(self):
        door = Device(self.doorName())
        doorState = door.state()
        
        if doorState in (PyTango.DevState.RUNNING, PyTango.DevState.STANDBY):
            door.command_inout("StopMacro")
        else:
            Qt.QMessageBox.warning(self,"Error while stopping macro", 
                                   "It was not possible to stop macro, because state of the door was different than RUNNING or STANDBY")
    
    def onPauseMacro(self):
        door = Device(self.doorName())
        doorState = door.state()
        
        if doorState == PyTango.DevState.RUNNING:
            door.command_inout("PauseMacro")
        else:
            Qt.QMessageBox.warning(self,"Error while pausing macro", 
                                   "It was not possible to pause macro, because state of the door was different than RUNNING")
            
    def onMacroStatusUpdated(self, data):
        macro = data[0]
        if macro is None: return        
        data = data[1][0]
        state, range, step, id = data["state"], data["range"], data["step"], data["id"]
        if id is None: return
        id = int(id)
        if id != self.macroId(): return
        macroName = macro.name
        shortMessage = ""
        if state == "start":
            self.emit(Qt.SIGNAL("macroStarted"), "DoorOutput")
            self.macroProgressBar.setRange(range[0], range[1])
            self.playMacroAction.setEnabled(False)
            self.pauseMacroAction.setEnabled(True)
            self.stopMacroAction.setEnabled(True)
            self.emit(Qt.SIGNAL("plotablesFilterChanged"), None)
            self.emit(Qt.SIGNAL("plotablesFilterChanged"), standardPlotablesFilter)
            shortMessage = "Macro %s started." % macroName
        elif state == "pause":
            self.playMacroAction.setText("Resume macro")
            self.playMacroAction.setToolTip("Resume macro")
            self.playMacroAction.setEnabled(True)
            self.pauseMacroAction.setEnabled(False)
            shortMessage = "Macro %s paused." % macroName
        elif state == "resume":
            self.playMacroAction.setText("Start macro")
            self.playMacroAction.setToolTip("Start macro")
            self.playMacroAction.setEnabled(False)
            self.pauseMacroAction.setEnabled(True)
            shortMessage = "Macro %s resumed." % macroName
        elif state == "stop" or state == "finish":
            self.playMacroAction.setEnabled(True)
            self.pauseMacroAction.setEnabled(False)
            self.stopMacroAction.setEnabled(False)
            shortMessage = "Macro %s finished." % macroName
        elif state == "exception":
            self.playMacroAction.setEnabled(True)
            self.pauseMacroAction.setEnabled(False)
            self.stopMacroAction.setEnabled(False)
            shortMessage = "Macro %s error." % macroName
            exc_value, exc_stack = data['exc_value'], data['exc_stack']
            exceptionDialog = TaurusMessageBox(MacroRunException, exc_value, exc_stack)
            exceptionDialog.exec_()
        elif state == "abort":
            self.playMacroAction.setText("Start macro")
            self.playMacroAction.setToolTip("Start macro")
            self.playMacroAction.setEnabled(True)
            self.pauseMacroAction.setEnabled(False)
            self.stopMacroAction.setEnabled(False)
            shortMessage = "Macro %s stopped." % macroName
        elif state == "step":
            shortMessage = "Macro %s at %d %% of progress." % (macroName, step) 
        self.emit(Qt.SIGNAL("shortMessageEmitted"), shortMessage)    
        self.macroProgressBar.setValue(step)

    def disableControlActions(self):
        self.pauseMacroAction.setEnabled(False)
        self.stopMacroAction.setEnabled(False)
        self.playMacroAction.setEnabled(False)

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
    
    
class TaurusMacroExecutor(MacroExecutionWindow):
    
    def __init__(self, parent=None, designMode=False):
        MacroExecutionWindow.__init__(self, parent, designMode)
        
    def initComponents(self):
        self.taurusMacroExecutorWidget = TaurusMacroExecutorWidget(self)
        self.registerConfigDelegate(self.taurusMacroExecutorWidget)
        self.taurusMacroExecutorWidget.setUseParentModel(True)
        self.setCentralWidget(self.taurusMacroExecutorWidget)
        self.connect(self.taurusMacroExecutorWidget, Qt.SIGNAL('shortMessageEmitted'), self.onShortMessage)
        self.statusBar().showMessage("MacroExecutor ready")
                
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
    macroExecutor.setModelInConfig(True)
    Qt.QObject.connect(macroExecutor, Qt.SIGNAL("doorChanged"), macroExecutor.onDoorChanged)
    if len(args) == 2:
        macroExecutor.setModel(args[0])
        macroExecutor.emit(Qt.SIGNAL('doorChanged'),args[1])
    macroExecutor.loadSettings()
    return macroExecutor
    
def main():
    from taurus.qt.qtgui.application import TaurusApplication
    import taurus
    
    app = TaurusApplication(sys.argv, app_version=taurus.Release.version)
    args = app.get_command_line_args()    
    
    app.setOrganizationName("Taurus")
    app.setApplicationName("macroexecutor")
    macroExecutor = createMacroExecutor(args)
    macroExecutor.show()
    sys.exit(app.exec_())
        
if __name__ == "__main__": 
    main()

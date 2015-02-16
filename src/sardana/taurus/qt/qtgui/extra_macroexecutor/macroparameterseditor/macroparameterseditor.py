#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""
macroparameterseditor.py: 
"""
import sys, inspect, glob

from taurus.external.qt import Qt
from taurus.core.util.singleton import Singleton
from taurus.qt.qtgui.resource import getThemeIcon

from sardana.taurus.core.tango.sardana import macro
from sardana.taurus.qt.qtgui.extra_macroexecutor.macroparameterseditor.delegate import ParamEditorDelegate


class MacroParametersEditor(object):

    def __init__(self):
        pass
#        self._macroModel = None

#    def setMacroModel(self, model):
#        self._macroModel = model
#        self.connect(self._macroModel, Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.onDataChanged)
#        self.connect(self._macroModel, Qt.SIGNAL("modelReset()"), self.onModelReset)
#
#    def onDataChanged(self):
#        pass
#
#    def onModelReset(self):
#        self.onDataChanged()

class StandardMacroParametersEditor(Qt.QWidget, MacroParametersEditor):

    def __init__(self, parent=None, macroNode=None):
        Qt.QWidget.__init__(self, parent)
        self.initComponents()

    def initComponents(self):
        self.setLayout(Qt.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.tree = MacroParametersTree(self)
        self.delegate = ParamEditorDelegate(self.tree)
        self.tree.setItemDelegate(self.delegate)
        self.tree.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
        self.layout().addWidget(self.tree)

        actionLayout = Qt.QVBoxLayout()
        actionLayout.setContentsMargins(0, 0, 0, 0)
        addButton = Qt.QToolButton()
        addButton.setDefaultAction(self.tree.addAction)
        actionLayout.addWidget(addButton)
        deleteButton = Qt.QToolButton()
        deleteButton.setDefaultAction(self.tree.deleteAction)
        actionLayout.addWidget(deleteButton)
        moveUpButton = Qt.QToolButton()
        moveUpButton.setDefaultAction(self.tree.moveUpAction)
        actionLayout.addWidget(moveUpButton)
        moveDownButton = Qt.QToolButton()
        moveDownButton.setDefaultAction(self.tree.moveDownAction)
        actionLayout.addWidget(moveDownButton)
        spacerItem = Qt.QSpacerItem(0, 0, Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Expanding)
        actionLayout.addItem(spacerItem)

        self.layout().addLayout(actionLayout)

    def setModel(self, model):
        self.tree.setModel(model)
        self.tree.expandAll()

    def macroNode(self):
        return self.tree.macroNode()

    def setMacroNode(self, macroNode):
        self.tree.setMacroNode(macroNode)

class MacroParametersTree(Qt.QTreeView):

    def __init__(self, parent=None, designMode=False):
        Qt.QTreeView.__init__(self, parent)
        self.setSelectionBehavior(Qt.QTreeView.SelectItems)
        self.setRootIsDecorated(False)
#        self.setTabKeyNavigation(True)
        self.setEditTriggers(Qt.QAbstractItemView.AllEditTriggers)

        self.addAction = Qt.QAction(getThemeIcon("list-add"), "Add new repetition", self)
        self.connect(self.addAction, Qt.SIGNAL("triggered()"), self.onAddRepeat)
        self.addAction.setToolTip("Clicking this button will add new repetition to current parameter.")

        self.deleteAction = Qt.QAction(getThemeIcon("list-remove"), "Remove repetition", self)
        self.connect(self.deleteAction, Qt.SIGNAL("triggered()"), self.onDelRepeat)
        self.deleteAction.setToolTip("Clicking this button will remove current repetition.")

        self.moveUpAction = Qt.QAction(getThemeIcon("go-up"), "Move up", self)
        self.connect(self.moveUpAction, Qt.SIGNAL("triggered()"), self.onUpRepeat)
        self.moveUpAction.setToolTip("Clicking this button will move current repetition up.")

        self.moveDownAction = Qt.QAction(getThemeIcon("go-down"), "Move down", self)
        self.connect(self.moveDownAction, Qt.SIGNAL("triggered()"), self.onDownRepeat)
        self.moveDownAction.setToolTip("Clicking this button will move current repetition down.")

        self.disableActions()


    def disableActions(self):
        self.addAction.setEnabled(False)
        self.deleteAction.setEnabled(False)
        self.moveUpAction.setEnabled(False)
        self.moveDownAction.setEnabled(False)

    def manageActions(self, currentIndex):
        self.disableActions()
        if currentIndex is None:
            return
        node = self.model().nodeFromIndex(currentIndex)
        if isinstance(node, macro.RepeatNode):
            self.deleteAction.setEnabled(not node.parent().isReachedMin())
            self.addAction.setEnabled(False)
            self.moveUpAction.setEnabled(node.isAllowedMoveUp())
            self.moveDownAction.setEnabled(node.isAllowedMoveDown())
        elif isinstance(node, macro.RepeatParamNode):
            self.addAction.setEnabled(not node.isReachedMax())
            self.deleteAction.setEnabled(False)


    def currentChanged(self, current, previous):
        self.manageActions(current)
        Qt.QTreeView.currentChanged(self, current, previous)

    #def focusInEvent(self, event):
    #    reason = event.reason()
    #    if (reason == Qt.Qt.TabFocusReason) | (reason == Qt.Qt.BacktabFocusReason):
    #        if reason == Qt.Qt.TabFocusReason:
    #            idx = self.forwardIdx(0, 1, Qt.QModelIndex())
    #        elif reason == Qt.Qt.BacktabFocusReason:
    #            idx = self.backwardIdx(len(self.root()) - 1, 1, Qt.QModelIndex())
    #        self.setCurrentIndex(idx)
    #        self.edit(idx)
    #    else:
    #        Qt.QTreeView.focusInEvent(self, event)
    #
    #def forwardIdx(self, row, col, parentIdx):
    #    try:
    #        proposalIdx = self.model().index(row, col, parentIdx)
    #    except AssertionError:
    #        if parentIdx.row() == -1:
    #            return Qt.QModelIndex()
    #        grandParentIdx = parentIdx.parent()
    #        return self.forwardIdx(parentIdx.row() + 1, col, grandParentIdx)
    #
    #    proposalNode = self.model().nodeFromIndex(proposalIdx)
    #
    #    if isinstance(proposalNode, macro.SingleParamNode):
    #        return proposalIdx
    #    elif isinstance(proposalNode, macro.RepeatNode):
    #        return self.forwardIdx(0, 1, proposalIdx)
    #    elif isinstance(proposalNode, macro.RepeatParamNode):
    #        if len(proposalNode) > 0:
    #            return self.forwardIdx(0, 1, proposalIdx)
    #        else:
    #            return self.forwardIdx(row + 1, col, proposalIdx)
    #    elif not proposalIdx.isValid():
    #        proposalIdx = parentIdx.sibling(parentIdx.row()+1, 0)
    #        if proposalIdx.isValid():
    #            proposalIdx = proposalIdx.child(0,1)
    #        else:
    #            while not proposalIdx.isValid():
    #                parentIdx = parentIdx.parent()
    #                if not parentIdx.isValid():
    #                    return Qt.QModelIndex()
    #                proposalIdx = parentIdx.sibling(parentIdx.row()+1, 1)
    #
    #        return proposalIdx
    #
    #    elif isinstance(proposalNode, macro.MacroNode):
    #        ##self.model().setRoot(proposalNode)
    #        return self.forwardIdx(0,1,proposalIdx)
    #
    #def backwardIdx(self, row, col, parentIdx):
    #    try:
    #        proposalIdx = self.model().index(row, col, parentIdx)
    #    except AssertionError:
    #        if parentIdx.row() == -1:
    #            return Qt.QModelIndex()
    #        grandParentIdx = parentIdx.parent()
    #        return self.backwardIdx(parentIdx.row() - 1, col, grandParentIdx)
    #    proposalNode = self.model().nodeFromIndex(proposalIdx)
    #    if isinstance(proposalNode, macro.SingleParamNode):
    #        return proposalIdx
    #    elif isinstance(proposalNode, macro.RepeatNode):
    #        return self.backwardIdx(self.model().rowCount(proposalIdx) - 1, 1, proposalIdx)
    #    elif isinstance(proposalNode, macro.RepeatParamNode):
    #        return self.backwardIdx(self.model().rowCount(proposalIdx) - 1, 1, proposalIdx)
    #
    #    elif not proposalIdx.isValid():
    #        proposalIdx = parentIdx.sibling(parentIdx.row()-1, 0)
    #        if proposalIdx.isValid():
    #            tempRow = 0
    #            proposalIdx = proposalIdx.child(tempRow,1)
    #            while proposalIdx.sibling(tempRow+1, 1).isValid():
    #                proposalIdx = proposalIdx.sibling(tempRow+1, 1)
    #                tempRow +=1
    #        else:
    #            while not proposalIdx.isValid():
    #                parentIdx = parentIdx.parent()
    #                if not parentIdx.isValid():
    #                    return Qt.QModelIndex()
    #                proposalIdx = parentIdx.sibling(parentIdx.row()-1, 1)
    #
    #        return proposalIdx
    #
    #def moveCursor (self, cursorAction, modifiers):
    #    ix=self.currentIndex()
    #    self.manageActions(ix)
    #    (col, row, parentIdx)=(ix.column(), ix.row(), ix.parent())
    #    #to start from second column
    #    if col == -1 and row == -1:
    #        if cursorAction == Qt.QAbstractItemView.MoveNext:
    #            return self.forwardIdx(0, 1, parentIdx)
    #        elif cursorAction == Qt.QAbstractItemView.MovePrevious:
    #            return self.backwardIdx(self.model().rowCount(parentIdx) - 1, 1, parentIdx)
    #    if (cursorAction == Qt.QAbstractItemView.MoveNext and
    #        modifiers == Qt.Qt.NoModifier):
    #        #This condition in case we start tabbing with cursor on first column
    #        if col == 0:
    #            currentNode = self.model().nodeFromIndex(ix)
    #            if isinstance(currentNode, macro.SingleParamNode):
    #                nextIdx = self.forwardIdx(row, 1, parentIdx)
    #            else:
    #                nextIdx = self.forwardIdx(0, 1, ix)
    #        else:
    #            nextIdx = self.forwardIdx(row + 1, 1, parentIdx)
    #        #this condition in case there is no next index and we want to pass focus
    #        #to next widget in parent obj
    #
    #        if nextIdx == "term":
    #            self.focusNextPrevChild(True)
    #            return Qt.QModelIndex()
    #
    #        if not nextIdx.isValid():
    #            self.parent().focusNextChild()
    #        #this condition in case the next index is valid and we want to
    #        #refresh state of buttons
    #        else:
    #            self.manageActions(nextIdx)
    #        return nextIdx
    #
    #    elif (cursorAction == Qt.QAbstractItemView.MovePrevious and
    #        modifiers == Qt.Qt.NoModifier):
    #        backwardIdx = self.backwardIdx(row - 1, 1, parentIdx)
    #        #this contion in case there is no previous index and we want to pass focus
    #        #to previous widget in parent obj
    #        if backwardIdx == "term":
    #            self.focusNextPrevChild(False)
    #            return Qt.QModelIndex()
    #
    #        if not backwardIdx.isValid():
    #            self.parent().focusPreviousChild()
    #        else:
    #            self.manageActions(backwardIdx)
    #        return backwardIdx
    #
    #def expanded(self):
    #    for column in range(self.model().columnCount(Qt.QModelIndex())):
    #        self.resizeColumnToContents(column)

    def onAddRepeat(self):
        index = self.currentIndex()
        if isinstance(self.model(), Qt.QSortFilterProxyModel):
            sourceIndex = self.model().mapToSource(index)
            newSourceIndex = self.model()._insertRow(sourceIndex)
            newIndex = self.model().mapFromSource(newSourceIndex)
        else:
            newIndex = self.model()._insertRow(index)
        self.setCurrentIndex(newIndex)
        self.expandAll()

    def onDelRepeat(self):
        index = self.currentIndex()
        if isinstance(self.model(), Qt.QSortFilterProxyModel):
            index = self.model().mapToSource(index)
        self.model()._removeRow(index)
        self.expandAll()

    def onUpRepeat(self):
        index = self.currentIndex()
        if isinstance(self.model(), Qt.QSortFilterProxyModel):
            sourceIndex = self.model().mapToSource(index)
            newSourceIndex = self.model()._upRow(sourceIndex)
            newIndex = self.model().mapFromSource(newSourceIndex)
        else:
            newIndex = self.model()._upRow(index)
        self.setCurrentIndex(newIndex)
        self.expandAll()

    def onDownRepeat(self):
        index = self.currentIndex()
        if isinstance(self.model(), Qt.QSortFilterProxyModel):
            sourceIndex = self.model().mapToSource(index)
            newSourceIndex = self.model()._downRow(sourceIndex)
            newIndex = self.model().mapFromSource(newSourceIndex)
        else:
            newIndex = self.model()._downRow(index)
        self.setCurrentIndex(newIndex)
        self.expandAll()

class ParamEditorManager(Singleton):

    def init(self):
        self._paths = []
        self._macroEditorsDict = {}

    def paths(self):
        return self._paths

    def setPaths(self, paths):
        self._paths = paths

    def appendPath(self, path):
        self._paths.append()

    def parsePaths(self, pathsString):
        self.setPaths(pathsString.split(":"))

    def browsePaths(self):
        for path in self.paths():
            modulePaths = glob.glob("%s/*.py" % path)
            if not modulePaths:
                continue

            sys.path.insert(0, path)
            for modulePath in modulePaths:
                if modulePath.endswith("__init__.py"):
                    continue
                modulePathAsArray = modulePath.split("/")
                moduleFileName = modulePathAsArray[-1]
                moduleName = moduleFileName[:-3]

                try:
                    module = __import__(moduleName)
                except ImportError:
                    continue
                klass = getattr(module, "CUSTOM_EDITOR", None)
#                for name, klass in inspect.getmembers(module, inspect.isclass):
#                    if issubclass(klass, MacroParametersEditor):
                self._macroEditorsDict[moduleName] = klass

    def getMacroEditor(self, macroName=None, parent=None):
        editorClass = self._macroEditorsDict.get(macroName, None)
        try:
            return editorClass(parent=parent)
        except:
            return None



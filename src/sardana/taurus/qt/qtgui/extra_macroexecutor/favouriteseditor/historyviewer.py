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
historyviewer.py: 
"""
import copy

from taurus.external.qt import Qt
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtcore.configuration import BaseConfigurableClass
from model import MacrosListModel

class HistoryMacrosViewer(TaurusWidget):
    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, parent=None, designMode=False):
        TaurusWidget.__init__(self, parent, designMode)
        self.setObjectName(self.__class__.__name__)
        self.registerConfigProperty("toXmlString", "fromXmlString", "history")
        self.initComponents()

    def initComponents(self):
        self.setLayout(Qt.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.list = HistoryMacrosList(self)
        self._model = MacrosListModel()
        self.list.setModel(self._model)

#####        self.registerConfigDelegate(self.list)
        self.layout().addWidget(self.list)

        actionBar = self.createActionBar()
        self.layout().addLayout(actionBar)

    def createActionBar(self):
        layout = Qt.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        deleteAllButton = Qt.QToolButton()
        deleteAllButton.setDefaultAction(self.list.removeAllAction)
        layout.addWidget(deleteAllButton)
        spacerItem = Qt.QSpacerItem(0, 0, Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Expanding)
        layout.addItem(spacerItem)
        return layout

    def listElementUp(self):
        indexPos = self.list.currentIndex()
        if indexPos.isValid() and indexPos.row() >= 1:
            self.list.setCurrentIndex(indexPos.sibling(indexPos.row() - 1, indexPos.column()))
        else:
            self.selectFirstElement()

    def listElementDown(self):
        indexPos = self.list.currentIndex()
        if indexPos.isValid() and indexPos.row() < self._model.rowCount() - 1:
            self.list.setCurrentIndex(indexPos.sibling(indexPos.row() + 1, indexPos.column()))
        elif indexPos.row() == self._model.rowCount() - 1:
            return
        else:
            self.selectFirstElement()

    def addMacro(self, macroNode):
        self.list.insertMacro(macroNode)

    def toXmlString(self):
        return self.list.toXmlString()

    def fromXmlString(self, xmlString):
        self.list.fromXmlString(xmlString)
        historyList = self.list.model().list
        macroServerObj = self.getModelObj()
        if macroServerObj is None:
            return

        for macroNode in historyList:
            macroServerObj.fillMacroNodeAdditionalInfos(macroNode)

    def selectFirstElement(self):
        self.list.removeAllAction.setEnabled(True)
        self.list.setCurrentIndex(self._model.index(0))


    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None


class HistoryMacrosList(Qt.QListView, BaseConfigurableClass):

    def __init__(self, parent):
        Qt.QListView.__init__(self, parent)
        self.setSelectionMode(Qt.QListView.SingleSelection)
        self.removeAllAction = Qt.QAction(Qt.QIcon(":/places/user-trash.svg"), "Remove all from history", self)
        self.connect(self.removeAllAction, Qt.SIGNAL("triggered()"), self.removeAllMacros)
        self.removeAllAction.setToolTip("Clicking this button will remove all macros from history.")
        self.removeAllAction.setEnabled(False)

    def currentChanged(self, current, previous):
        macro = copy.deepcopy(self.currentIndex().internalPointer())
        self.emit(Qt.SIGNAL("historySelected"), macro)
        Qt.QListView.currentChanged(self, current, previous)

    def mousePressEvent(self, e):
        clickedIndex = self.indexAt(e.pos())
        if clickedIndex.isValid():
            macro = copy.deepcopy(self.currentIndex().internalPointer())
            self.emit(Qt.SIGNAL("historySelected"), macro)
            self.removeAllAction.setEnabled(True)
        Qt.QListView.mousePressEvent(self, e)

    def focusInEvent(self, e):
        if self.model().rowCount() > 0:
            self.removeAllAction.setEnabled(True)
        else:
            self.removeAllAction.setEnabled(False)

    def insertMacro(self, macroNode):
        idx = self.model().insertRow(macroNode)
        self.setCurrentIndex(idx)
        self.removeAllAction.setEnabled(True)

    def removeAllMacros(self):
        self.selectAll()
        slist = sorted(self.selectedIndexes(), key=lambda index: index.row(), reverse=True)
        for index in slist:
            self.model().removeRow(index.row())
        self.removeAllAction.setEnabled(False)

    def toXmlString(self):
        return self.model().toXmlString()

    def fromXmlString(self, xmlString):
        self.model().fromXmlString(xmlString)


def test():
    import sys, taurus, time
    from  taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(sys.argv)

    historyViewer = HistoryMacrosViewer()

    args = app.get_command_line_args()
    historyViewer.setModel(args[0])
    time.sleep(1)
    macroNode = historyViewer.getModelObj().getMacroNodeObj(str(args[1]))
    historyViewer.addMacro(macroNode)
    historyViewer.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    test()

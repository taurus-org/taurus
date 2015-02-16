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
favouriteseditor.py: 
"""
import copy

from taurus.external.qt import Qt
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtcore.configuration import BaseConfigurableClass
from model import MacrosListModel

class FavouritesMacrosEditor(TaurusWidget):
    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, parent=None, designMode=False):
        TaurusWidget.__init__(self, parent, designMode)
        self.setObjectName(self.__class__.__name__)
        self.registerConfigProperty("toXmlString", "fromXmlString", "favourites")
        self.initComponents()

    def initComponents(self):
        self.setLayout(Qt.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.list = FavouritesMacrosList(self)
        self._model = MacrosListModel()
        self.list.setModel(self._model)

#        self.registerConfigDelegate(self.list)
        self.layout().addWidget(self.list)

        actionBar = self.createActionBar()
        self.layout().addLayout(actionBar)

    def createActionBar(self):
        layout = Qt.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        deleteButton = Qt.QToolButton()
        deleteButton.setDefaultAction(self.list.removeAction)
        layout.addWidget(deleteButton)
        deleteAllButton = Qt.QToolButton()
        deleteAllButton.setDefaultAction(self.list.removeAllAction)
        layout.addWidget(deleteAllButton)
        moveUpButton = Qt.QToolButton()
        moveUpButton.setDefaultAction(self.list.moveUpAction)
        layout.addWidget(moveUpButton)
        moveDownButton = Qt.QToolButton()
        moveDownButton.setDefaultAction(self.list.moveDownAction)
        layout.addWidget(moveDownButton)
        spacerItem = Qt.QSpacerItem(0, 0, Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Expanding)
        layout.addItem(spacerItem)
        return layout

    def addMacro(self, macroNode):
        self.list.insertMacro(macroNode)

    def toXmlString(self):
        return self.list.toXmlString()

    def fromXmlString(self, xmlString):
        self.list.fromXmlString(xmlString)
        favouritesList = self.list.model().list
        macroServerObj = self.getModelObj()
        if macroServerObj is None:
            self.debug("MS IS NONE")
            return

        for macroNode in favouritesList:
            macroServerObj.fillMacroNodeAdditionalInfos(macroNode)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None


class FavouritesMacrosList(Qt.QListView, BaseConfigurableClass):

    def __init__(self, parent):
        Qt.QListView.__init__(self, parent)

        self.setSelectionMode(Qt.QListView.ExtendedSelection)

        self.removeAction = Qt.QAction(Qt.QIcon(":/actions/list-remove.svg"), "Remove from favourites", self)
        self.connect(self.removeAction, Qt.SIGNAL("triggered()"), self.removeMacros)
        self.removeAction.setToolTip("Clicking this button will remov selected macros from favourites.")

        self.removeAllAction = Qt.QAction(Qt.QIcon(":/places/user-trash.svg"), "Remove all from favourites", self)
        self.connect(self.removeAllAction, Qt.SIGNAL("triggered()"), self.removeAllMacros)
        self.removeAllAction.setToolTip("Clicking this button will remove all macros from favourites.")

        self.moveUpAction = Qt.QAction(Qt.QIcon(":/actions/go-up.svg"), "Move up", self)
        self.connect(self.moveUpAction, Qt.SIGNAL("triggered()"), self.upMacro)
        self.moveUpAction.setToolTip("Clicking this button will move the macro up in the favourites hierarchy.")

        self.moveDownAction = Qt.QAction(Qt.QIcon(":/actions/go-down.svg"), "Move up", self)
        self.connect(self.moveDownAction, Qt.SIGNAL("triggered()"), self.downMacro)
        self.moveDownAction.setToolTip("Clicking this button will move the macro down in the favourites hierarchy.")

        self.disableActions()

    def currentChanged(self, current, previous):
        macro = copy.deepcopy(self.currentIndex().internalPointer())
        self.emit(Qt.SIGNAL("favouriteSelected"), macro)
        Qt.QListView.currentChanged(self, current, previous)

    def selectionChanged(self, old, new):
        macro = None
        if self.currentIndex().isValid():
            self.removeAllAction.setEnabled(True)
            self.isIndexSelected()
        else:
            self.disableActions()
        Qt.QListView.selectionChanged(self, old, new)
        if len(self.selectedIndexes()) > 1:
            self.moveUpAction.setEnabled(False)
            self.moveDownAction.setEnabled(False)

    def isIndexSelected(self):
        if len(self.selectedIndexes()) > 0:
            self.removeAction.setEnabled(True)
            self.moveUpAction.setEnabled(self.model().isUpRowAllowed(self.currentIndex()))
            self.moveDownAction.setEnabled(self.model().isDownRowAllowed(self.currentIndex()))
        else:
            self.removeAction.setEnabled(False)
            self.moveUpAction.setEnabled(False)
            self.moveDownAction.setEnabled(False)

    def mousePressEvent(self, e):
        clickedIndex = self.indexAt(e.pos())
        if clickedIndex.isValid():
            macro = copy.deepcopy(self.currentIndex().internalPointer())
            self.emit(Qt.SIGNAL("favouriteSelected"), macro)
        Qt.QListView.mousePressEvent(self, e)

    def disableActions(self):
        self.removeAction.setEnabled(False)
        self.removeAllAction.setEnabled(False)
        self.moveUpAction.setEnabled(False)
        self.moveDownAction.setEnabled(False)

    def insertMacro(self, macroNode):
        idx = self.model().insertRow(macroNode)
        self.setCurrentIndex(idx)

    def removeMacros(self):
        slist = sorted(self.selectedIndexes(), key=lambda index: index.row(), reverse=True)
        for index in slist:
            row = index.row()
            idx = self.model().removeRow(row)
        self.setCurrentIndex(idx)

    def removeAllMacros(self):
        self.selectAll()
        slist = sorted(self.selectedIndexes(), key=lambda index: index.row(), reverse=True)
        for index in slist:
            self.model().removeRow(index.row())

    def upMacro(self):
        row = self.currentIndex().row()
        idx = self.model().upRow(row)
        self.setCurrentIndex(idx)

    def downMacro(self):
        row = self.currentIndex().row()
        idx = self.model().downRow(row)
        self.setCurrentIndex(idx)

    def toXmlString(self):
        return self.model().toXmlString()

    def fromXmlString(self, xmlString):
        self.model().fromXmlString(xmlString)


def test():
    import sys, taurus, time
    from  taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(sys.argv)

    favouritesEditor = FavouritesMacrosEditor()

    args = app.get_command_line_args()
    favouritesEditor.setModel(args[0])
    time.sleep(1)
    macroNode = favouritesEditor.getModelObj().getMacroNodeObj(str(args[1]))
    favouritesEditor.addMacro(macroNode)
    favouritesEditor.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    test()

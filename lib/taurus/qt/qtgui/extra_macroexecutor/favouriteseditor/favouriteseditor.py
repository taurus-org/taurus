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
favouriteseditor.py: 
"""
import copy

from PyQt4 import Qt
from taurus.qt.qtgui.container import TaurusWidget
from taurus.qt.qtcore.configuration import BaseConfigurableClass
from model import MacrosListModel

class FavouritesMacrosEditor(TaurusWidget):
    __pyqtSignals__ = ("modelChanged(const QString &)",)
    
    def __init__(self, parent=None, designMode = False):
        TaurusWidget.__init__(self, parent, designMode)
        self.setObjectName(self.__class__.__name__)
        self.registerConfigProperty("toXmlString", "fromXmlString", "favourites")
        self.initComponents()
        
    def initComponents(self):
        self.setLayout(Qt.QHBoxLayout())
        self.layout().setContentsMargins(0,0,0,0)
        
        self.list = FavouritesMacrosList(self)
        self._model = MacrosListModel()
        self.list.setModel(self._model)
        
#        self.registerConfigDelegate(self.list)
        self.layout().addWidget(self.list)
                
        actionBar = self.createActionBar()
        self.layout().addLayout(actionBar)    
                
    def createActionBar(self):
        layout = Qt.QVBoxLayout()    
        layout.setContentsMargins(0,0,0,0)
        deleteButton = Qt.QToolButton()
        deleteButton.setDefaultAction(self.list.removeAction)
        layout.addWidget(deleteButton)
        moveUpButton = Qt.QToolButton()
        moveUpButton.setDefaultAction(self.list.moveUpAction)
        layout.addWidget(moveUpButton)
        moveDownButton = Qt.QToolButton()
        moveDownButton.setDefaultAction(self.list.moveDownAction)
        layout.addWidget(moveDownButton)
        spacerItem = Qt.QSpacerItem(0,0,Qt.QSizePolicy.Fixed,Qt.QSizePolicy.Expanding)
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
            return
        
        for macroNode in favouritesList:
            macroServerObj.fillMacroNodeAdditionalInfos(macroNode)
    
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return None

    
class FavouritesMacrosList(Qt.QListView, BaseConfigurableClass):
    
    def __init__(self, parent):
        Qt.QListView.__init__(self, parent)
        
        self.setSelectionMode(Qt.QListView.SingleSelection)
        
        self.removeAction = Qt.QAction(Qt.QIcon(":/actions/list-remove.svg"), "Remove from favourites", self)
        self.connect(self.removeAction, Qt.SIGNAL("triggered()"), self.removeMacro)
        self.removeAction.setToolTip("Clicking this button will remove the macro from favourites.")
            
        self.moveUpAction = Qt.QAction(Qt.QIcon(":/actions/go-up.svg"), "Move up", self)
        self.connect(self.moveUpAction, Qt.SIGNAL("triggered()"), self.upMacro)
        self.moveUpAction.setToolTip("Clicking this button will move the macro up in the favourites hierarchy.")
        
        self.moveDownAction = Qt.QAction(Qt.QIcon(":/actions/go-down.svg"), "Move up", self)
        self.connect(self.moveDownAction, Qt.SIGNAL("triggered()"), self.downMacro)
        self.moveDownAction.setToolTip("Clicking this button will move the macro down in the favourites hierarchy.")
        
        self.disableActions()
        
    def currentChanged(self, current, previous):
        macro = None
        if current.isValid():            
            self.removeAction.setEnabled(True)  
            self.moveUpAction.setEnabled(self.model().isUpRowAllowed(current))
            self.moveDownAction.setEnabled(self.model().isDownRowAllowed(current))
            macro = copy.deepcopy(current.internalPointer())
        else: 
            self.disableActions()
        self.emit(Qt.SIGNAL("favouriteSelected"), macro)
        Qt.QListView.currentChanged(self, current, previous)
        
    def disableActions(self):
        self.removeAction.setEnabled(False)
        self.moveUpAction.setEnabled(False)
        self.moveDownAction.setEnabled(False)
        
    def insertMacro(self, macroNode):
        idx = self.model().insertRow(macroNode)
        self.setCurrentIndex(idx)
            
    def removeMacro(self):
        row = self.currentIndex().row()
        idx = self.model().removeRow(row)
        self.setCurrentIndex(idx)
    
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
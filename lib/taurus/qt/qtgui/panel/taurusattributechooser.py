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
AttributeChooser.py: widget for choosing (a list of) attributes from a tango DB
"""

__all__ = ["TaurusAttributeChooser"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt

from taurus.qt.qtgui.base import TaurusBaseWidget
from taurus.core.util.containers import CaselessList

from .ui.ui_AttributeChooser import *

class TaurusAttributeChooser(Qt.QWidget, TaurusBaseWidget):
    
    __pyqtSignals__ = ("modelChanged(const QString &)",) ##
    
    def __init__(self, parent = None, designMode = False):
        """Initialize the MainWindow"""
        ##
        self.call__init__wo_kw(Qt.QWidget, parent)
        self.call__init__(TaurusBaseWidget, str(self.objectName()))
        ##
        self.ui = Ui_AttrCh()
        self.ui.setupUi(self)
        #Create global variables
        self.dev_name = ""
        self.selectedItems = CaselessList([])
        self.selectedItemsComplete = CaselessList([])
        #self.ui.attrList.setSortingEnabled(True)
        self._singleAttrMode = False
        
        #set icons
        self.ui.addButton.setIcon(Qt.QIcon(":/actions/go-down.svg"))
        self.ui.removeButton.setIcon(Qt.QIcon(":/actions/go-up.svg"))
        self.ui.cancelButton.setIcon(Qt.QIcon(":/actions/edit-clear.svg"))
        self.ui.updateButton.setIcon(Qt.QIcon(":/actions/view-refresh.svg"))
        
        #Connect the ui.lineEdit
        self.connect(self.ui.lineEdit, Qt.SIGNAL("returnPressed () "), self.setDevName)
        self.connect(self.ui.lineEdit, Qt.SIGNAL("textChanged (const QString&)"), self.setDevName_new)

        #Connect the addButton
        self.connect(self.ui.addButton,Qt.SIGNAL( "clicked()"), self.addButtonClicked)
        
        #Select an attribute with double click
        self.connect(self.ui.attrList,Qt.SIGNAL( "itemDoubleClicked (QListWidgetItem *)"), self.addButtonClicked)

        #Connect the button to cancel the selection
        self.connect(self.ui.cancelButton,Qt.SIGNAL( "clicked()"), self.cancelButtonClicked)

        #Connect the removeButton
        self.connect(self.ui.removeButton,Qt.SIGNAL( "clicked()"), self.removeButtonClicked)
        
        #Connect the updateButton
        self.connect(self.ui.updateButton,Qt.SIGNAL( "clicked()"), self.updateButtonClicked)
        
        self.setDevName_new()
    
    def setSingleAttrMode(self, single):
        '''sets whether the selection should be limited to just one attribute
        (single=True) or not (single=False)'''
        if single == self._singleAttrMode: return
        self._singleAttrMode = single
        
        if single:
            self.ui.attrList.setSelectionMode(Qt.QAbstractItemView.SingleSelection)
        else:
            self.ui.attrList.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection)
        
    def isSingleAttrMode(self):
        return self._singleAttrMode
    
    def resetSingleAttrMode(self):
        self.setSingleAttrMode(self, False)
    
        
    def updateList(self, attrList ):
        self.selectedItemsComplete=CaselessList(attrList)
        self.ui.final_List.clear()
        self.ui.final_List.addItems(self.selectedItemsComplete)

    def getDb(self):
        return self.getTaurusFactory().getDatabase()

    def setDevName(self):
        """Fill the devices list"""

        device= str(self.ui.lineEdit.text())
        
        try:
            items = list(self.getDb().get_device_exported(device))

        except Exception,e:
            self.warning('Unable to contact with device %s: %s'%(device,str(e)))
            items=[]

        self.ui.devList.clear()
        self.ui.devList.addItems(items)
        #self.connect(self.ui.devList, Qt.SIGNAL("itemClicked ( QListWidgetItem * )"), self.setAttributes)
        self.connect(self.ui.devList, Qt.SIGNAL("itemSelectionChanged ()"), self.setAttributes)

    def setDevName_new(self):
        """Fill the devices list"""

        device= str(self.ui.lineEdit.text())
        device += '*'
        
        try:
            items = list(self.getDb().get_device_exported(device))

        except Exception,e:
            self.warning('Unable to contact with device %s: %s'%(device,str(e)))
            items=[]

        self.ui.devList.clear()
        self.ui.devList.addItems(items)
        #self.connect(self.ui.devList, Qt.SIGNAL("itemClicked ( QListWidgetItem * )"), self.setAttributes)
        self.connect(self.ui.devList, Qt.SIGNAL("itemSelectionChanged ()"), self.setAttributes)

    def setAttributes(self):
        """Fill the attributes list"""
        import PyTango
        
        self.ui.attrList.clear()
        self.dev_name = str(self.ui.devList.currentItem().text())
        
        try:
            items=[str(a.name) for a in PyTango.DeviceProxy(self.dev_name).attribute_list_query()]
            
        except Exception,e:
            self.warning('Unable to contact with device %s: %s'%(self.dev_name,str(e)))
            items=[]
        
        items.sort(key=lambda x:x.lower()) #sort the attributes (case insensitive!)
        
        for i in range(len(items)):
            self.ui.attrList.addItem(items[i])

    def addButtonClicked(self):
        """Put all the items in the selectedItems list into the selectedItemsComplete list, with the device name"""
        
        if self.isSingleAttrMode():  #if we are in single attr mode, we want to replace instead of adding attributes
            self.selectedItemsComplete = CaselessList([])
            self.ui.final_List.clear()
            
        #print self.ui.attrList.selectedItems()
        self.selectedItems = self.ui.attrList.selectedItems()
        for i in range(len(self.selectedItems)):
            aux = str(self.dev_name) + "/" + str(self.selectedItems[i].text())
            if (aux not in self.selectedItemsComplete):
                self.selectedItemsComplete.append(aux)

        self.updateList(self.selectedItemsComplete)


    def cancelButtonClicked(self):
        """Cancel all the selected items and clear all the lists"""

        self.selectedItemsComplete = CaselessList([])
        self.selectedItems = CaselessList([])
        self.ui.attrList.clearSelection()
        self.ui.final_List.clear()

    def removeButtonClicked(self):
        """Remove selected items of the final list """
        for item in self.ui.final_List.selectedItems():
            self.selectedItemsComplete.remove(str(item.text()))
        self.updateList(self.selectedItemsComplete)
        

    def updateButtonClicked(self):
        """Return the final Attributes list """
        
        self.emit(Qt.SIGNAL("UpdateAttrs"), self.selectedItemsComplete)
        
        
def main(args):
    app=Qt.QApplication(args)
    win=TaurusAttributeChooser()
    win.show()
    app.connect(app, Qt.SIGNAL("lastWindowClosed()"),app,Qt.SLOT("quit()"))

    return app.exec_()

if __name__=="__main__":
    import sys
    sys.exit(main(sys.argv))

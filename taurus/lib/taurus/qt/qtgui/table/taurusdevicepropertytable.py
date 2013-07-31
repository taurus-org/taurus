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
taurusdevicepropertytable.py: 
"""

__all__ = ["TaurusPropTable"]

from taurus.qt import Qt, QtCore, QtGui
from taurus.qt.qtgui.base import TaurusBaseWidget
import taurus.core
import PyTango

class TaurusPropTable(QtGui.QTableWidget, TaurusBaseWidget):
    ''' 
    This widget will show a list of properties of device and the list of values.
    @todo add a frame for Add, Delete and Refresh buttons!
    '''
    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, parent=None, designMode = False):
        try:
            name = "TaurusPropTable"
            self._useParentModel = True
            self._localModel = ''
            self.call__init__wo_kw(QtGui.QTableWidget, parent)
            self.call__init__(TaurusBaseWidget, name, designMode=designMode)
            self.setObjectName(name)
            #self.setItemDelegate(Delegate(self))
            #self.setModelCheck('controls01:10000') 
            self.defineStyle()
            
        except Exception,e:
            self.traceback()
            
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget over writing methods 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def sizeHint(self):
        return QtGui.QTableWidget.sizeHint(self)

    def minimumSizeHint(self):
        return QtGui.QTableWidget.minimumSizeHint(self)

    def getModelClass(self):
        return taurus.core.taurusdatabase.TaurusDatabase

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.table'
        ret['group'] = 'Taurus Views'
        ret['icon'] = ":/designer/table.png"
        return ret
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = QtCore.pyqtProperty("QString", TaurusBaseWidget.getModel, 
                                TaurusBaseWidget.setModel, 
                                TaurusBaseWidget.resetModel)
    
    useParentModel = QtCore.pyqtProperty("bool", 
                                         TaurusBaseWidget.getUseParentModel, 
                                         TaurusBaseWidget.setUseParentModel,
                                         TaurusBaseWidget.resetUseParentModel)                

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # My methods 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    @QtCore.pyqtSignature("setTable(QString)")  
    def setTable(self,dev_name):
        ''' 
        This method is used to connect TaurusPropTable widget with TaurusClassTable widget
        This method fill the table with the names of properties and values for the device selected in the TaurusClassTable
        '''
        QtCore.QObject.disconnect(self,QtCore.SIGNAL("cellChanged(int,int)"),self.valueChanged)
        self.db = PyTango.Database()
        dev_name = str(dev_name)
        self.list_prop = list(self.db.get_device_property_list(dev_name,'*'))
        self.setRowCount(len(self.list_prop))
        for i in range(0,len(self.list_prop)):
            elem = self.list_prop[i]
            self.setText(elem,i,0)
            self.dictionary=self.db.get_device_property(dev_name,self.list_prop)
            self.debug('Getting %s properties: %s -> %s'%(dev_name,self.list_prop,self.dictionary))
            value=self.dictionary[elem]
            self.debug('TaurusPropsTable: property %s is type %s'%(elem,type(value)))
            USE_TABLES=False
            if USE_TABLES: self.setPropertyValue(value,i,1)
            else:
                if not isinstance(value,str): #not something like an string
                    #if isinstance(value,list):#type(value) is list: 
                    heigh1 = len(value)
                    value = '\n'.join(str(v) for v in value) # adding new lines in between elements in the list
                self.setText(str(value),i,1)
        
        self.updateStyle()
        self.dev_name = dev_name
        self.setWindowTitle('%s Properties'%dev_name)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()        
        ##Signals @todo
        ## Commented as it didn't work really well (many pop-ups open!)
        #QtCore.QObject.connect(self,QtCore.SIGNAL("cellDoubleClicked(int,int)"),self.valueDoubleClicked)
        #QtCore.QObject.connect(self,QtCore.SIGNAL("cellChanged(int,int)"),self.valueChanged)    

    def defineStyle(self):
        """ Defines the initial style for the widget """
        self.setWindowTitle('Properties')
        self.setColumnCount(2)
        self.setRowCount(0)
        self.setGeometry(QtCore.QRect(0,0,400,500))

        self.setColumnWidth(0,124)
        self.setColumnWidth(1,254)

        headerItem = QtGui.QTableWidgetItem()
        headerItem.setText(QtGui.QApplication.translate("PLCTabWidget", "Property Name", None, QtGui.QApplication.UnicodeUTF8))
        self.setHorizontalHeaderItem(0,headerItem)

        headerItem1 = QtGui.QTableWidgetItem()
        headerItem1.setText(QtGui.QApplication.translate("PLCTabWidget", "Value", None, QtGui.QApplication.UnicodeUTF8))
        self.setHorizontalHeaderItem(1,headerItem1)
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents) #.Stretch)

    def updateStyle(self):
        self.resizeRowsToContents()
        self.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents) #.Stretch)
        #self.resizeColumnsToContents()
        pass
        
    def contextMenuEvent(self,event):
        ''' This function is called when right clicking on qwt plot area. A pop up menu will be
        shown with the available options. '''
        self.info('TaurusPropTable.contextMenuEvent()')
        menu = Qt.QMenu(self)
        configDialogAction = menu.addAction("Add new property")
        self.connect(configDialogAction, QtCore.SIGNAL("triggered()"), self.addProperty)
        configDialogAction = menu.addAction("Delete property")
        self.connect(configDialogAction, QtCore.SIGNAL("triggered()"), self.deleteProperty) 
        configDialogAction = menu.addAction("Edit property")
        self.connect(configDialogAction, QtCore.SIGNAL("triggered()"), self.editProperty)       
        menu.addSeparator()
        menu.exec_(event.globalPos())
        del menu        

    def setText(self,value,i,j):
        item = QtGui.QTableWidgetItem()
        item.setFlags(Qt.Qt.ItemIsEnabled)
        item.setText(QtGui.QApplication.translate("PLCTabWidget", value, None, QtGui.QApplication.UnicodeUTF8))
        self.setItem(i,j,item)
        return
    
    def valueDoubleClicked(self,x,y):
        self.info('TaurusPropTable.valueDoubleClicked(%s,%s)' % (x,y))
        ## opens a dialog for multiline edition
        self.editProperty()    
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    ## @name Property Edition
    # @{
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def addProperty(self):
        text, ok = QtGui.QInputDialog.getText(self,'New Property','Property name:')
        if ok:
            text1 = unicode(text)
            new_prop_name = str(text1)
            new_prop_value = '0'
            dict1= {new_prop_name: [new_prop_value]}
            self.db.put_device_property(self.dev_name,dict1)
            self.setTable(self.dev_name)

    def deleteProperty(self):
        row = self.currentRow()
        prop_name = self.item(row,0).text()
        list = [str(prop_name)]
        yes = QtGui.QMessageBox.Ok
        no = QtGui.QMessageBox.Cancel
        result = QtGui.QMessageBox.question(self,"Removing property","Would you like to delete property  '"+ prop_name +"'  ?",yes, no)
        if result == yes:
            self.db.delete_device_property(self.dev_name,list)
            self.setTable(self.dev_name)

    def editProperty(self):
        row = self.currentRow()
        col = self.currentColumn()

        item1 = QtGui.QTableWidgetItem()
        item1 = self.item(row,0)
        prop_name = item1.text()
        prop_name = str(prop_name)
        self.prop_name2 = prop_name
        self.info('TaurusPropsTable.editProperty(%s)'%prop_name)

        item2 = QtGui.QTableWidgetItem()
        item2 = self.item(row,1)
        prop_value = item2.text()
        prop_value = str(prop_value)

        if col == 0:
            new_text, ok = QtGui.QInputDialog.getText(self,'Rename','Write new name of property:')
            if ok:
                new_text = unicode(new_text)
                new_text = str(new_text)
                list = [prop_name]
                dict= {new_text: [prop_value]}
                self.db.delete_device_property(self.dev_name,list)#usuwanie musze umiescic gdzies wczesniej bo inaczej usuwam juz zmieniana nazwe z listy property 
                self.db.put_device_property(self.dev_name,dict)
                self.setTable(self.dev_name)
        elif col == 1:
            #Create the dilog to edit multiply text
            dialogx = EditTextDialog(self) 
            dialogx.setText(prop_value) 
            dialogx.exec_() 
            ok = dialogx.getResult() #OK or Cancel
            if ok:
                new_text = dialogx.getNewText() #method of dialog to get the changed text
                self.setNewPropertyValue(new_text)

    def setNewPropertyValue(self,new_text):
        new_text = unicode(new_text)
        new_text = str(new_text)
        values = {self.prop_name2: new_text.replace('\r','').split('\n')}
        self.db.put_device_property(self.dev_name,values)
        self.setTable(self.dev_name)
        self.updateStyle()
    ##@}
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Methods  for database commands
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def get_device_property_names(self,dev_name,wildcard='*'):
        return self.db.get_device_property_list(dev_name,wildcard)

    def put_device_property(self,dev_name,dict):
        return self.db.put_device_property(dev_name,dict)
                                         
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    ## @name DEPRECATED METHODS
    # @{
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-        
        
    def valueChanged(self):
        ''' @deprecated valueChanged THIS DOES NOTHING! '''
        row = self.currentRow()
        #item = QtGui.QTableWidgetItem()
        item = self.item(row,0)
        prop_name = item.text()
        prop_name = str(prop_name)
        #item_2 = QtGui.QTableWidgetItem()
        item_2 = self.item(row,1)
        prop_value = item_2.text()
        prop_value = str(prop_value)
        dict = {prop_name: [prop_value]}
        list = [self.prop_name]
        self.db.delete_device_property(self.dev_name,list)
        self.db.put_device_property(self.dev_name,dict)
        
    def setPropertyValue(self,value,i,j):
        ''' This method inserts a new table widget inside the cell 
        @deprecated ... use setText() and editProperty() event call instead!!!
        '''
        if len(value)==1 and isinstance(value[0],str):
            value = value[0]
        if isinstance(value,str):# and '\n' in value: 
            value = value.split('\n')
        if False:#isinstance(value,str):
            item = QtGui.QTableWidgetItem()
            item.setText(QtGui.QApplication.translate("PLCTabWidget", value, None, QtGui.QApplication.UnicodeUTF8))
            self.setItem(i,j,item)
        else:
            item = QtGui.QTableWidget(len(value),1)
            item.setItemDelegate(Delegate(item))
            item.horizontalHeader().hide()
            item.verticalHeader().hide()
            #item.setGridStyle(Qt.Qt.DashLine)
            for k,v in enumerate(value):
                cell = QtGui.QTableWidgetItem()
                cell.setText(QtGui.QApplication.translate("PLCTabWidget", v, None, QtGui.QApplication.UnicodeUTF8))
                item.setItem(k,0,cell) 
            item.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.MinimumExpanding)
            self.setCellWidget(i,j,item)
            self.resizeColumnsToContents()
            self.resizeRowsToContents()
        return       
    
    ##@}                                         

class EditTextDialog(QtGui.QDialog):
    """ This class create the dialog using to edit multiply text """

    def __init__(self, parent = None):
        print ('In EditTextDialog.__init__()')
        QtGui.QDialog.__init__(self,parent)
        self.setModal(1)
        self.initComponents()
        self.show()
        self.result = 0
        #Signals
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.pressOK)
        QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.close)   

    def initComponents(self):
        widgetLayout = QtGui.QVBoxLayout(self)
        widgetLayout.setContentsMargins(10,10,10,10)
        self.editText = QtGui.QTextEdit()
        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
        widgetLayout.addWidget(self.editText)
        widgetLayout.addWidget(self.buttonBox)

    def pressOK(self):
        print ('In EditTextDialog.pressOk()')
        self.new_text = self.editText.toPlainText()  
        self.result = 1
        self.close()

    def setText(self,text):
        self.editText.setText(text)
        self.new_text = text

    def getNewText(self):
        return self.new_text

    def getResult(self):
        return self.result     
       
class Delegate(QtGui.QItemDelegate):
    ''' Usage:
            table = QtGui.QTableWidget()
        table.setItemDelegate(Delegate(table))
    '''
    
    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self,parent)
        
    def sizeHint(self, option, index):
        table = self.parent()
        widget = table.cellWidget(index.row(),index.column())
        if not widget: widget = table.itemAt(index.row(),index.column())
        size = widget.sizeHint()
        return size       
    
if __name__ == '__main__':
    import sys,os
    app = QtGui.QApplication([])
    widget = TaurusPropTable()
    args = sys.argv[1:]
    if not args: args = ['tango/admin/%s'%(os.environ['TANGO_HOST'].split(':')[0])] 
    widget.setTable(sys.args)
    widget.show()
    app.exec_()
		

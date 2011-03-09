import os, sys, wiz, re
import taurus.qt.qtgui.resource, pool_editor_UI
import pool_editor_UI
#, ms_editor_UI
from PyQt4 import QtGui, QtCore, Qt
from taurus.core.util import Enumeration
from taurus.core.tango.sardana import SardanaManager


class NewSardanaIntroPage(wiz.SardanaIntroBasePage):

    def __init__(self, parent = None):
        wiz.SardanaIntroBasePage.__init__(self, parent)
        self.sardana_name=None
    
    def getIntroText(self):
        return """This wizard will guide you through the creation of the new instance of Sardana"""
    
    def setNextPageId(self, id):
        self._nextPageId = id


class SelectTangoHostPage(wiz.SardanaBasePage):
    
    def __init__(self, parent = None):
        wiz.SardanaBasePage.__init__(self, parent)
    
        self.setSubTitle('Please select the Tango Host')
        self._valid = False
        
        self._regExp0 = QtCore.QRegExp("^[0-9a-zA-Z]{,50}")
        self._regValid0 = QtGui.QRegExpValidator(self._regExp0, self)
        
        self._regExp1 = QtCore.QRegExp("^[0-9]{,50}")
        self._regValid1 = QtGui.QRegExpValidator(self._regExp1, self)
        
        self._panel = self.getPanelWidget()
        
        layout = QtGui.QFormLayout()
        self.hostEdit = QtGui.QLineEdit()
        self.hostEdit.setValidator(self._regValid0)
        
        self.portEdit = QtGui.QLineEdit()
        self.portEdit.setValidator(self._regValid1)
        self.checkButton = QtGui.QPushButton("Check")

        layout.addRow("&Host", self.hostEdit)
        layout.addRow("&Port", self.portEdit)
        layout.addRow("", self.checkButton)
        self.checkButton.hide()
        host, port = self.get_default_tango_host()
    
        self.hostEdit.setText(host)
        self.portEdit.setText(port)
    
        self._panel.setLayout(layout)

        self['db'] = self._getDatabase
        self['port'] = self._getPort
        self['host'] = self._getHost
    
        self.connect(self.hostEdit,QtCore.SIGNAL('textEdited(const QString &)'), self._letterChanged)
        self.connect(self.portEdit, QtCore.SIGNAL('textEdited(const QString &)'),self._letterChanged)
        self.connect(self.checkButton, QtCore.SIGNAL('clicked()'), self.checkData )
        
        self.checkData()
    
    def get_default_tango_host(self):
        tg = os.environ.get('TANGO_HOST','')
        if not tg or tg.count(':') != 1: return '',''
        return tg.split(':')

    def _letterChanged(self):
        self._valid = False
        self.setStatus('please click the ''Check'' button')
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.checkButton.show()
                    
    def checkData(self):
        try:
            db = self.db()
            if not db is None:
                self.setStatus('please click the ''Next'' button')
                self._valid = True
                self.emit(QtCore.SIGNAL('completeChanged()'))
        except Exception, e:
                self.setStatus('Invalid database')
                self._valid = False
        self.checkButton.hide()

    def _getPort(self):
        return str(self.portEdit.text().toLower())
    
    def _getHost(self):
        return str(self.hostEdit.text().toLower())
    
    def _getDatabase(self):
        host = str(self.hostEdit.text().toLower())
        port = str(self.portEdit.text())
        
        return taurus.Database("%s:%s" % (host, port))
    
    def host(self):
        return self.wizard()['host']
    
    def port(self):
        return self.wizard()['port']
    
    def db(self):
        return self.wizard()['db']
    
    def isComplete(self):
        return self._valid

    def setNextPageId(self, id):
        self._nextPageId = id
    
    def nextId(self):
        return self._nextPageId
    
    def initializePage(self):
        wiz.SardanaBasePage.initializePage(self)
        self.checkData()

    
class AddSardanaBasePage(wiz.SardanaBasePage):

    def __init__(self, parent = None):
        wiz.SardanaBasePage.__init__(self, parent)
        self.setSubTitle('Please type the name for the new Sardana instance')
        self._valid = False
    
        panel = self.getPanelWidget()
    
        layout = QtGui.QFormLayout()
        
        self.nameEdit = QtGui.QLineEdit()
        self.nameEdit.setText("MySardana")
        
        self._regExp = QtCore.QRegExp("^[0-9a-zA-Z]{,50}")
        self._regValid = QtGui.QRegExpValidator(self._regExp, self)
        
        self.nameEdit.setValidator(self._regValid)
        
        self.checkButton = QtGui.QPushButton("Check")
        self.checkButton.hide()

        layout.addRow("&Name", self.nameEdit)
        layout.addRow("", self.checkButton)

        panel.setLayout(layout)
        
        self.connect(self.nameEdit,QtCore.SIGNAL('textEdited(const QString &)'), self._letterChanged)
        self.connect(self.checkButton, QtCore.SIGNAL('clicked()'), self.checkData )
        
    def _getSardana(self):
         sardana = str(self.nameEdit.text())
         return sardana

    def _letterChanged(self):
        self._valid = False
        self.emit(QtCore.SIGNAL('completeChanged()'))
        self.setStatus('please click the ''Check'' button')
        self.checkButton.show()

    def sardana(self):
        return self.wizard()['sardana']

    def db(self):
        return self.wizard()['db']
    
    def checkData(self):
        if self.nameEdit.text() == "":
            self.setStatus('Please type the name')
            self._valid = False
        else:
             if self.nameEdit.text() not in self._getSardanas():
                 self.setStatus('please click the ''Next'' button')
                 self._valid = True
                 self.emit(QtCore.SIGNAL('completeChanged()'))
             else:
                 self.setStatus('The name already exists in the database')
                 self._valid = False
        self.checkButton.hide()
    
    def isComplete(self):
        return self._valid

    def _getSardanas(self):
        db = self.db()
        services = db.get_service_list('Sardana.*')
        service_instances = []
        for service in services:
            service_instances.append(service.split('/', 1)[1])
        return service_instances
        
    def initializePage(self):
        wiz.SardanaBasePage.initializePage(self)
        self.wizard().__setitem__("sardana",self._getSardana)
        self.checkData()
        
    def setNextPageId(self, id):
        self._nextPageId = id
    
    def nextId(self):
        return self._nextPageId 
           

class Item(object):

    def __init__(self,instanceName="", hostName="", level=None):
        self._instanceName=str(instanceName)
        self._hostName=str(hostName)
        self._level=level
    def setInstanceName(self, name):
        self._instanceName=str(name)
    def getInstanceName(self):
        return self._instanceName
    def setHostName(self, name):
        self._hostName=str(name)
    def getHostName(self):
        return self._hostName
    def setLevel(self, level):
        self._level=level
    def getLevel(self):
        return self._level
    
class SimpleEditorBasePage(wiz.SardanaBasePage):
   
    def __init__(self, parent = None):
        wiz.SardanaBasePage.__init__(self, parent)
        
        self.setSubTitle('SubTitle')
        
        panel = self.getPanelWidget()
        self._valid = True

      
        self.horizontalLayout = QtGui.QHBoxLayout(panel)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.horizontalLayout.addWidget(self.tableWidget)
        self._setTableHeaders()
        self.tableWidget.horizontalHeader().resizeSection( 0, 125 )
        self.tableWidget.horizontalHeader().resizeSection( 1, 120 )
        self.tableWidget.horizontalHeader().resizeSection( 2, 55 )
        self.tableWidget.verticalHeader().setVisible(False)
        
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.addButton = QtGui.QPushButton(self)
        self.addButton.setText(QtGui.QApplication.translate("Form", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.addButton.setObjectName("addButton")
        self.addButton.setIcon(taurus.qt.qtgui.resource.getThemeIcon("list-add"))
        self.verticalLayout.addWidget(self.addButton)
        
        self.editButton = QtGui.QPushButton(self)
        self.editButton.setText(QtGui.QApplication.translate("Form", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.editButton.setObjectName("editButton")
        self.editButton.setIcon(taurus.qt.qtgui.resource.getThemeIcon("preferences-system"))
        self.verticalLayout.addWidget(self.editButton)
        
        self.removeButton = QtGui.QPushButton(self)
        self.removeButton.setText(QtGui.QApplication.translate("Form", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.removeButton.setObjectName("removeButton")
        self.removeButton.setIcon(taurus.qt.qtgui.resource.getThemeIcon("list-remove"))
        self.verticalLayout.addWidget(self.removeButton)
        
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)
        #spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        #self.horizontalLayout.addItem(spacerItem1)
        self.listOfItems = []
        self._comboList = []
        self._spinList = []
        
    def _setTableHeaders(self):
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem("name"))
        self.tableWidget.setHorizontalHeaderItem(1,  QtGui.QTableWidgetItem("host"))
        self.tableWidget.setHorizontalHeaderItem(2, QtGui.QTableWidgetItem("level"))
    
    def openEditor (self, item = None):
        pass
    
    def checkName(self, name, id = None):
        i=0
        for item in self.listOfItems:
            if i!=id:
                if name == item.getInstanceName():
                    return False
            i+=1
        return True
    
    def addItem (self, item):
        if item.getLevel() == None:
            item.setLevel("1")
        item.setHostName(self._getHostList()[0])
        self.listOfItems.append(item)
        self._fillList()
        self.checkData()
        return True
    
    def editItem (self,item,id):
        if item.getLevel() == None:
            item.setLevel("1")
        self.listOfItems[id] = item
        self._fillList()
        
    def removeItem(self, id):
        self.listOfItems.remove(self.listOfItems[id])
        self._fillList()
        self.checkData()
        return True
    
    def hostChanged(self,hostId=None):
        name = str(self.sender().objectName())
        id = int(name[name.index('_')+1:])
        if self.sender().currentText() == "None":
            self.listOfItems[id].setHostName("")
        else:
            self.listOfItems[id].setHostName(self.sender().currentText())
        self._fillList()
        
    def levelChanged(self, id=None):
        name = str(self.sender().objectName())
        id = int(name[name.index('_')+1:])
        self.listOfItems[id].setLevel( str(self.sender().value()) ) 
        
    def checkData(self):
        self._valid=True
        
    def _getItemList(self):
        return self.listOfItems[:]
    
    def isComplete(self):
        return self._valid

    def _fillList(self):
        self._comboList=[]
        self._spinList=[]
        self.tableWidget.clear()
        self._setTableHeaders()
        
        self.tableWidget.setRowCount(len(self.listOfItems))
        self.tableWidget.clearSelection()
        #self.tableWidget.setItemSelected(None)
        
        #self.tableWidget.selectRow(-1)
        
        self.editButton.setObjectName("editButton")
        i=0
        for item in self.listOfItems:
            self.tableWidget.setCellWidget(i,0, QtGui.QLabel(item.text()))
            self._comboList.append(QtGui.QComboBox())
            self._comboList[i].setObjectName("hostComboBox_%d" % i)
            if item.getHostName() == "":
                self._comboList[i].addItem("None")
            else:
                self._comboList[i].addItem(item.getHostName())
            self._comboList[i].addItems(self._hostList)
            self._comboList[i].addItem("None")
            self._comboList[i].insertSeparator(len(self._hostList)+1)
            QtCore.QObject.connect(self._comboList[i], QtCore.SIGNAL("currentIndexChanged(int)"), self.hostChanged)
            self.tableWidget.setCellWidget(i,1, self._comboList[i])
            self._spinList.append(QtGui.QSpinBox())
            self._spinList[i].setRange(*SardanaManager().get_level_range())
            self._spinList[i].setObjectName("levelSpinBox_%d" % i)
            QtCore.QObject.connect(self._spinList[i], QtCore.SIGNAL("valueChanged(int)"), self.levelChanged)
            self.tableWidget.setCellWidget(i,2, self._spinList[i]) 
           
            if (item.getHostName()=="") or (item.getHostName()==None):
                self._spinList[i].setDisabled(True)
                self._spinList[i].setValue(0)
            else:     
                self._spinList[i].setValue( int( item.getLevel() ) )
            i+=1
            
    def initializePage(self):
        wiz.SardanaBasePage.initializePage(self)
        self._hostList = self._getHostList()
        self._fillList()
        self.checkData()
        
    
    def setNextPageId(self, id):
        self._nextPageId = id
        
    def db(self):
        return self.wizard()['db']
    
    def _getHostList(self):
        return SardanaManager().get_hosts()
    
    def getPoolServerList(self):
        return [ s[s.index('/')+1:] for s in self.db().get_server_list() if s.startswith('Pool/') ]
        

class Pool(Item):
    def __init__(self,instanceName="", hostName="", level=None, poolDeviceName="", alias="", poolVersion="", poolPath=[]):
        
        Item.__init__(self, instanceName, hostName, level)
        self._poolDeviceName=str(poolDeviceName)
        self._alias=str(alias)
        self._poolVersion=str(poolVersion)
        self._poolPath=map(str, poolPath)

    def setPoolDeviceName(self,name):
        self._poolDeviceName=str(name)
    def getPoolDeviceName(self):
        return str(self._poolDeviceName)
    def setAlias(self,alias):
        self._alias=str(alias)
    def getAlias(self):
        return self._alias
    def setPoolVersion(self, poolVersion):
        self._poolVersion=str(poolVersion)
    def getPoolVersion(self):
        return self._poolVersion
    def setPoolPath(self, path):
        self._poolPath = map(str, path)
    def getPoolPath(self):
        return self._poolPath
    def text(self):
        return str(self._instanceName)
    def copy(self):
        return Pool(self._instanceName, self._hostName, self._level,self._poolDeviceName, self._alias, self._poolVersion, self._poolPath[:])



class AddPoolBasePage(SimpleEditorBasePage):
   
    def __init__(self, parent = None):
        self._editor = None
        SimpleEditorBasePage.__init__(self, parent)
        self._editor = PoolEditor(parent = self)
        

        self.selectedItem=None
        self.item_id=None
        
        self.setSubTitle('You can use this manager if you would like to Add, Edit or Delete Pool entries in the database.')
        
        self.addButton.setText(QtGui.QApplication.translate("Form", "Add Pool", None, QtGui.QApplication.UnicodeUTF8))
        self.editButton.setText(QtGui.QApplication.translate("Form", "Edit Pool", None, QtGui.QApplication.UnicodeUTF8))
        self.removeButton.setText(QtGui.QApplication.translate("Form", "Remove Pool", None, QtGui.QApplication.UnicodeUTF8))
        
        QtCore.QObject.connect(self.addButton, QtCore.SIGNAL("clicked()"), self.openAddEditor)
        QtCore.QObject.connect(self.editButton, QtCore.SIGNAL("clicked()"), self.openItemEditor)
        QtCore.QObject.connect(self.removeButton, QtCore.SIGNAL("clicked()"), self.delete)
        QtCore.QObject.connect(self.tableWidget, QtCore.SIGNAL("cellDoubleClicked(int,int)"), self.openItemEditor)
        
    def delete (self):
        if len(self.tableWidget.selectedIndexes())>0:
            msgBox = QtGui.QMessageBox()
            msgBox.setText("The list of Pools has been modified.")
            self.item_id=self.tableWidget.selectedIndexes()[0].row()
            self.selectedItem = self.listOfItems[self.item_id]
            msgBox.setInformativeText("Do you want to delete Pool?:\n"+self.selectedItem.text())
            msgBox.setStandardButtons(QtGui.QMessageBox().Ok | QtGui.QMessageBox().Cancel)
            msgBox.setDefaultButton(QtGui.QMessageBox().Cancel);
            msgBox.setIcon(QtGui.QMessageBox.Question)
            ret = msgBox.exec_()
            if ret == QtGui.QMessageBox().Ok:
                self.removeItem(self.item_id)
            if ret == QtGui.QMessageBox().Cancel:
                pass
        
    def openAddEditor (self):
        self.item_id=None
        self.selectedItem=None
        SimpleEditorBasePage.openEditor(self)
        self._editor.showEditor(item=None, item_id=None)

        
    def openItemEditor (self):
        if len(self.tableWidget.selectedIndexes())>0:
            self.item_id=self.tableWidget.selectedIndexes()[0].row()
            self.selectedItem = self.listOfItems[self.item_id]
            SimpleEditorBasePage.openEditor(self)
            self._editor.showEditor(item= self.selectedItem, item_id=self.item_id)

    def checkData(self):
        if len(self.listOfItems) >0:
            self._valid=True
            self.emit(QtCore.SIGNAL('completeChanged()'))
        else:
            self._valid=False
            self.emit(QtCore.SIGNAL('completeChanged()'))
 
    def isComplete(self):
        return self._valid
    
    def initializePage(self):
        SimpleEditorBasePage.initializePage(self)
        self.wizard().__setitem__("poolList",self._getItemList)
        if len(self.listOfItems) == 0:
            sardana = self.wizard()["sardana"]
            _pool= Pool()
            _pool.setInstanceName(sardana)
            _pool.setLevel("1")
            _pool.setPoolDeviceName("pool/"+sardana+"/1")
            _pool.setAlias("Pool_"+sardana)
            _pool.setPoolVersion("0.3.0")
            _pool.setPoolPath(SardanaManager.get_default_pool_path())
            self.addItem(_pool.copy())
        
        
class PoolEditor(object):
    
    def __init__(self,parent = None):

        self._parent=parent
        self._isEditorOpened=False
        self._pool= Pool()
        self.poolEditor = QtGui.QDialog()
        self.ui = pool_editor_UI.Ui_PoolEditor()
        self.poolEditor.setModal(True)
        self.ui.setupUi(self.poolEditor)

        self._regExp = QtCore.QRegExp("^[0-9a-zA-Z_/]{,50}")
        self._regValid = QtGui.QRegExpValidator(self._regExp, self.poolEditor)
        
        self._regExp2 = QtCore.QRegExp("^[0-9.]{,50}")
        self._versionValid = QtGui.QRegExpValidator(self._regExp2, self.poolEditor)
        
        self._regExp3 = QtCore.QRegExp("^[0-9a-zA-Z_/]{,100}")
        self._deviceNameValid = QtGui.QRegExpValidator(self._regExp3, self.poolEditor)
        
        self.ui.instanceNameLineEdit.setValidator(self._regValid)
        self.ui.poolDeviceNameLineEdit.setValidator(self._deviceNameValid)
        self.ui.aliasLineEdit.setValidator(self._regValid)
        self.ui.poolVersionLineEdit.setValidator(self._versionValid)
        
        self._item_id=None
        self._path_id=None
        
        self.ui.addButton.setIcon(taurus.qt.qtgui.resource.getThemeIcon("list-add"))
        self.ui.removeButton.setIcon(taurus.qt.qtgui.resource.getThemeIcon("list-remove"))
        self.ui.upButton.setIcon(taurus.qt.qtgui.resource.getThemeIcon("go-up"))
        self.ui.downButton.setIcon(taurus.qt.qtgui.resource.getThemeIcon("go-down"))
        
        QtCore.QObject.connect(self.ui.createButton, QtCore.SIGNAL("clicked()"), self._createPool)
        QtCore.QObject.connect(self.ui.addButton, QtCore.SIGNAL("clicked()"), self._addPath)
        QtCore.QObject.connect(self.ui.removeButton, QtCore.SIGNAL("clicked()"), self._removePath)
        QtCore.QObject.connect(self.ui.upButton, QtCore.SIGNAL("clicked()"), self._moveUp)
        QtCore.QObject.connect(self.ui.downButton, QtCore.SIGNAL("clicked()"), self._moveDown)
        QtCore.QObject.connect(self.ui.instanceNameLineEdit,QtCore.SIGNAL('textEdited(const QString &)'), self._letterChanged)
        
        QtCore.QObject.connect(self.ui.poolDeviceNameCheckBox, QtCore.SIGNAL("toggled(bool)"), self._letterChanged)
        QtCore.QObject.connect(self.ui.aliasCheckBox, QtCore.SIGNAL("toggled(bool)"), self._letterChanged)
        QtCore.QObject.connect(self.ui.poolVersionCheckBox, QtCore.SIGNAL("toggled(bool)"), self._letterChanged)       
        
        QtCore.QObject.connect(self.ui.poolPathList, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self._editPath)       
        
        
    def _letterChanged(self):
        if self.ui.poolDeviceNameCheckBox.isChecked():
            self.ui.poolDeviceNameLineEdit.setText("pool/"+self.ui.instanceNameLineEdit.text()+"/1")
        if self.ui.aliasCheckBox.isChecked():
            self.ui.aliasLineEdit.setText("Pool_"+self.ui.instanceNameLineEdit.text())
        if self.ui.poolVersionCheckBox.isChecked():
            self.ui.poolVersionLineEdit.setText("0.3.0")
                
    def _addPath (self):
        text, ok = QtGui.QInputDialog.getText(self.poolEditor, 'Input Dialog', 'Type directory to be added:')
        if ( ok and len(text)>0 ):
            self._pool.getPoolPath().append(str(text))
            self._refreshPathList()
    
    def _editPath (self):
        if len(self.ui.poolPathList.selectedIndexes())>0:
            self._path_id=self.ui.poolPathList.selectedIndexes()[0].row()
            text, ok = QtGui.QInputDialog.getText(self.poolEditor, 'Input Dialog', 'Edit selected directory:',QtGui.QLineEdit.Normal,self._pool.getPoolPath()[self._path_id])
            if ( ok and len(text)>0 ):
                self._pool.getPoolPath()[self._path_id]=text
        self._refreshPathList()
            
    def _removePath(self):
        if len(self.ui.poolPathList.selectedIndexes())>0:
            self._path_id=self.ui.poolPathList.selectedIndexes()[0].row()
            self._pool.getPoolPath().remove(self._pool.getPoolPath()[self._path_id])
            self._refreshPathList()
            
    def _moveUp(self):
        if len(self.ui.poolPathList.selectedIndexes())>0:
            self._path_id=self.ui.poolPathList.selectedIndexes()[0].row()
            if self._path_id > 0:
                tmp =  self._pool.getPoolPath()[self._path_id]
                self._pool.getPoolPath()[self._path_id]=self._pool.getPoolPath()[self._path_id-1]
                self._pool.getPoolPath()[self._path_id-1]=tmp
                self._refreshPathList()
                self.ui.poolPathList.setCurrentIndex(self.ui.poolPathList.indexFromItem(self.ui.poolPathList.item(self._path_id-1) ))
                
    def _moveDown(self):
        if len(self.ui.poolPathList.selectedIndexes())>0:
            self._path_id=self.ui.poolPathList.selectedIndexes()[0].row()
            if self._path_id < self.ui.poolPathList.count()-1:
                tmp =  self._pool.getPoolPath()[self._path_id]
                self._pool.getPoolPath()[self._path_id]=self._pool.getPoolPath()[self._path_id+1]
                self._pool.getPoolPath()[self._path_id+1]=tmp
                self._refreshPathList()
                self.ui.poolPathList.setCurrentIndex(self.ui.poolPathList.indexFromItem(self.ui.poolPathList.item(self._path_id+1) ))
                
    def _refreshPathList(self):
        self.ui.poolPathList.clear()
        for path in self._pool.getPoolPath():
            self.ui.poolPathList.addItem(path)
            
    def _validate(self):
        err=0
        warnMess=""
        
        if self.ui.instanceNameLineEdit.text() == "":
            err=1
            warnMess+="Please type the Instance Name\n"
        else:
            if self._parent.checkName(self.ui.instanceNameLineEdit.text(), id = self._item_id):
                pass
            else:
               err=1
               warnMess+="The Instance Name already exist in the DataBase\n" 

        pdn = str(self.ui.poolDeviceNameLineEdit.text())    
        allowed = re.compile("^.{1,}/.{1,}/.{1,}$")
        if not ( (len(pdn)>0)  and (allowed.match(pdn)) and (pdn.count("/")==2) ):
            err=1
            warnMess+="The Pool Device Name is not valid\n"
                 
        #if self.ui.aliasLineEdit.text() == "":
        #    err=1
        #    warnMess+="Please type the Alias\n"
        
        if self.ui.poolVersionLineEdit.text() == "":
            err=1
            warnMess+="Please type the Pool Version\n"            
        
        if err == 1:
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Warning !!!")
            msgBox.setStandardButtons(QtGui.QMessageBox().Ok)
            msgBox.setInformativeText(warnMess)
            msgBox.setIcon(QtGui.QMessageBox.Warning)
            ret = msgBox.exec_()
            return False
        else:
            self._pool.setInstanceName(self.ui.instanceNameLineEdit.text())
            self._pool.setPoolDeviceName(self.ui.poolDeviceNameLineEdit.text())
            self._pool.setAlias(self.ui.aliasLineEdit.text())
            self._pool.setPoolVersion(self.ui.poolVersionLineEdit.text())
            return True
    
    def _createPool(self):
        if self._item_id == None:
            if self._validate():
                self._parent.addItem(self._pool.copy())
        else:
            if self._validate():
                self._parent.editItem(item= self._pool.copy(),id=self._item_id)         
  
    
    def showEditor(self, item=None, item_id=None):
        
        self._pool= Pool()
        if item == None:
            self._pool.setPoolPath(SardanaManager.get_default_pool_path())
            self._refreshPathList()
            self.poolEditor.setWindowTitle("Create New Pool")
            self.ui.instanceNameLineEdit.setText("")
            self.ui.poolDeviceNameLineEdit.setText("")
            self.ui.poolDeviceNameLineEdit.setEnabled(False)
            self.ui.poolDeviceNameCheckBox.setChecked(True)
            self.ui.aliasLineEdit.setText("")
            self.ui.aliasLineEdit.setEnabled(False)
            self.ui.aliasCheckBox.setChecked(True)
            self.ui.poolVersionLineEdit.setText("")
            self.ui.poolVersionLineEdit.setEnabled(False)
            self.ui.poolVersionCheckBox.setChecked(True)
            self.ui.createButton.setText("Create")
            self._item_id=None
            self.poolEditor.setModal(True)
            self.poolEditor.exec_()   
        else:
            self._pool.setPoolPath(item.getPoolPath()[:])
            self._pool.setHostName(item.getHostName())
            self._pool.setLevel(item.getLevel())
            self._refreshPathList()
            self.poolEditor.setWindowTitle("Edit Pool")
            self.ui.instanceNameLineEdit.setText(item.getInstanceName())
            self.ui.poolDeviceNameLineEdit.setText(item.getPoolDeviceName())
            self.ui.poolDeviceNameLineEdit.setEnabled(True)
            self.ui.poolDeviceNameCheckBox.setChecked(False)
            self.ui.aliasLineEdit.setText(item.getAlias())
            self.ui.aliasLineEdit.setEnabled(True)
            self.ui.aliasCheckBox.setChecked(False)
            self.ui.poolVersionLineEdit.setText(item.getPoolVersion())
            self.ui.poolVersionLineEdit.setEnabled(True)
            self.ui.poolVersionCheckBox.setChecked(False)
            self.ui.createButton.setText("Edit")
            self._item_id=item_id
            self.poolEditor.setModal(True)
            self.poolEditor.exec_()
    
    
def addSardana():
    #import addMSBasePage, sardanaCommitBasePage, sardanaOutroBasePage
    
    app = QtGui.QApplication([])
    QtCore.QResource.registerResource(wiz.get_resources())
    
    Pages = Enumeration('Pages', ('IntroPage', 'TangoPage', 'SardanaPage', 'PoolPage', 'MSPage','CommitPage','OutroPage'))
    w = wiz.SardanaBaseWizard()
    
    intro = NewSardanaIntroPage()
    w.setPage(Pages.IntroPage, intro)
    intro.setNextPageId(Pages.TangoPage)
    
    tg_host_page = SelectTangoHostPage()
    w.setPage(Pages.TangoPage, tg_host_page)
    tg_host_page.checkData()
    tg_host_page.setNextPageId(Pages.SardanaPage)
    
    sardana_page = AddSardanaBasePage()
    w.setPage(Pages.SardanaPage, sardana_page)
    sardana_page.setNextPageId(Pages.PoolPage)
    
    pool_page = AddPoolBasePage()
    w.setPage(Pages.PoolPage, pool_page) 
    pool_page.setNextPageId(Pages.MSPage)
    
#    ms_page = addMSBasePage.AddMSBasePage()
#    w.setPage(Pages.MSPage, ms_page) 
#    ms_page.setNextPageId(Pages.CommitPage)
#    
#    commit_page = sardanaCommitBasePage.SardanaCommitBasePage()
#    w.setPage(Pages.CommitPage, commit_page)
#    commit_page.setNextPageId(Pages.OutroPage)
#    
#    outro_page = sardanaOutroBasePage.SardanaOutroBasePage()
#    w.setPage(Pages.OutroPage, outro_page) 
#    w.setOption (QtGui.QWizard.CancelButtonOnLeft , True)
    
    
    #Qt.QObject.connect(w, Qt.SIGNAL("done()"), done)
    w.show()
    sys.exit(app.exec_())

    
    
  
if __name__ == "__main__":
    addSardana()
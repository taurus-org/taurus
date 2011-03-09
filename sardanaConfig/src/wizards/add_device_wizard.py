import os, sys, wx, copy, taurus, settings_widget, simple_tree_model, wiz
import taurus.qt.qtgui.resource
from PyQt4 import QtGui, QtCore, Qt
from types import *
from taurus.core.util import Enumeration
from taurus.core.tango.sardana import SardanaManager

    
class SelectSardanaPoolBasePage(wiz.SardanaBasePage):
    def __init__(self, sardana=None, pool=None, parent = None):
        wiz.SardanaBasePage.__init__(self, parent)
        self._sardana = sardana
        self._pool = pool
        
        self.setSubTitle('Please select the Pool from existing Sardana')
        self._valid = True
        self._panel = self.getPanelWidget()
        layout = QtGui.QGridLayout()
        self._sardanaNameCB= QtGui.QComboBox()
        self._poolNameCB= QtGui.QComboBox()
        layout.addItem(QtGui.QSpacerItem(60, 60, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum),0,0)
        layout.addWidget(QtGui.QLabel("Sardana"),0,1)
        layout.addItem(QtGui.QSpacerItem(60, 60, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum),0,3)
        layout.addWidget(self._sardanaNameCB,0,2)
        layout.addWidget(QtGui.QLabel("Pool"),1,1)
        layout.addWidget(self._poolNameCB,1,2)
        layout.addItem(QtGui.QSpacerItem(200, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum),2,2)
        self._panel.setLayout(layout)
        self.setStatus("Select the instances of Sardana and Pool, and click Next to continue")
        
        self['sardana'] = self._getSardana
        self['pool'] = self._getPool
        self.connect(self._sardanaNameCB,QtCore.SIGNAL('currentIndexChanged(int)'), self._fillPoolNameCB)
    
    def initializePage(self):
        wiz.SardanaBasePage.initializePage(self)
        self._isSardanaProper=False
        if (self._sardana) and (self._sardana in self._getSardanas()):
            self._sardanaNameCB.addItem(self._sardana)
            self._sardanaNameCB.setEnabled(False)
            self._isSardanaProper=True
        else:
            self._fillSardanaNameCB()
        
        self._isPoolProper=False
        if (self._pool) and (self._isSardanaProper): 
            for pool in self._getSardana().get_pools():
                if self._pool == pool.get_name():
                    self._isPoolProper=True
        
        if self._isPoolProper:
            self._poolNameCB.addItem(self._pool)
            self._poolNameCB.setEnabled(False)
        else:
            self._fillPoolNameCB()
         
    def isComplete(self):
        return self._valid

    def setNextPageId(self, id):
        self._nextPageId = id
    
    def nextId(self):
        return self._nextPageId
    
    def _fillSardanaNameCB(self):
        self._sardanaNameCB.clear()
        for item in self._getSardanas():
            self._sardanaNameCB.addItem(item)
    
    def _fillPoolNameCB(self, int= None):
        sardana = self._getSardana()
        self._poolNameCB.clear()
        for item in sardana.get_pools():
            self._poolNameCB.addItem(item.get_name())
    
    def _getSardanas(self):
        return SardanaManager().get_sardanas()
    
    def _getSardana(self):
        return self._getSardanas()[str(self._sardanaNameCB.currentText())]
    
    def _getPool(self):
        for pool in self._getSardana().get_pools():
            if str(self._poolNameCB.currentText()) == pool.get_name():
                return pool
        return None
    
    
class SimpleTreeView(QtGui.QTreeView):

    def __init__(self, parent=None):
        super(SimpleTreeView, self).__init__(parent)
        self.setSelectionBehavior(QtGui.QTreeView.SelectItems)
        self.setUniformRowHeights(True)
#            
        self.connect(self, QtCore.SIGNAL("activated(QModelIndex)"),
                     self.activated)
        self.connect(self, QtCore.SIGNAL("expanded(QModelIndex)"),
                     self.expanded)
        self.expanded()

    def currentFields(self):
        return self.model().asData(self.currentIndex())

    def activated(self, index):
        self.emit(QtCore.SIGNAL("activated"), self.model().asRecord(index))


    def expanded(self):
        if not self.model()==None: 
            for column in range(self.model().columnCount(
                                QtCore.QModelIndex())):
                self.resizeColumnToContents(column)
                
                
class HardwareSettings(Qt.QWidget):
    def __init__(self, parent = None):
        Qt.QWidget.__init__(self, parent)
        self._layout = QtGui.QGridLayout(self)
        self.setLayout(self._layout)
        self.setupUi()
    
    def setupUi(self):
        self.setVisible(False)
        self._nameLabel = Qt.QLabel("Name:")
        self._nameLineEdit = Qt.QLineEdit()
        self._nameLineEdit.setMinimumSize(200, 25)
        self._layout.addWidget(self._nameLabel,0,0,1,1)
        self._layout.addWidget(self._nameLineEdit,0,1,1,1)
        self._monitorLabel = Qt.QLabel("Monitor List:")
        self._axisLabel = Qt.QLabel("Axis:")
        self._axisLineEdit = Qt.QLineEdit()
        self._axisLineEdit.setMinimumSize(200, 25)
        self._axisLineEdit.setValidator(QtGui.QIntValidator(self._axisLineEdit))
        self._layout.addWidget(self._axisLabel,1,0,1,1)
        self._layout.addWidget(self._axisLineEdit,1,1,1,1)

        self._spacerItem1 = Qt.QSpacerItem(10, 0, Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Expanding)
        self._layout.addItem(self._spacerItem1,4,0,1,1,Qt.Qt.AlignCenter)
        
        
class NewDeviceBasePage(wiz.SardanaBasePage):
   
    def __init__(self, parent = None):
        wiz.SardanaBasePage.__init__(self, parent)
        self._valid = False
        QtGui.QWizardPage.__init__(self, parent)
        self._layout = QtGui.QGridLayout(self)
        self.setupUi()
        self.setLayout(self._layout)
        self.setTitle('Selecting device')
        self.connect(self._treeView, QtCore.SIGNAL("activated"),
             self.activated)
        self._currentItem=None
        self._currentItemIndex=None
        
    def getProperties(self):
        if self._settings is not None:
            return self._settings.getProperties()
        else:
            return None
        
    def checkData(self):
        if self.picked():
            properties, name, values = self.getProperties()
            if len(name):
                self.setStatus("Editing: "+ self.picked().get_name())
                self._valid = True
            else:
                self.setStatus('The name is invalid')
                self._valid = False
        else:
            self.setStatus('Please select a device')
            self._valid = False
            
        self.emit(QtCore.SIGNAL('completeChanged()'))
        
    def keyPressEvent(self,event):
        wiz.SardanaBasePage.keyPressEvent(self,event)
        if self._tabWidget.currentIndex() ==0:
            undo = (event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Z)
            redo = (event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Y)
            if (undo):
                self._settings.undo()
            if (redo):
                self._settings.redo()
    
    def initializePage(self):
        wiz.SardanaIntroBasePage.initializePage(self)
        self.wizard().__setitem__("properties",self.getProperties)
        # resizing application
        self._previousPageSize = copy.deepcopy([self.wizard().size().width(), self.wizard().size().height()])
        preferedSize = [800,600]
        desktopRect = QtGui.QApplication.desktop().availableGeometry(self)
        center = desktopRect.center()
        if (not self.wizard().isMaximized()) and (self.wizard().size().height () < preferedSize[1]) and (self.wizard().size().width() < preferedSize[0]):
            self.wizard().resize(preferedSize[0],preferedSize[1])
            self.wizard().move(center.x()-self.wizard().width()*0.5, center.y()-self.wizard().height()*0.5)
        self._pool = self.wizard()["pool"]
        self._loadTreeModel()
        self.checkData()
        
    def cleanupPage(self):
        wiz.SardanaIntroBasePage.cleanupPage(self)
        preferedSize = copy.deepcopy(self._previousPageSize) # setUp size for previous page
        desktopRect = QtGui.QApplication.desktop().availableGeometry(self)
        center = desktopRect.center()
        
        if (not self.wizard().isMaximized()) and (self.wizard().size().height () > preferedSize[1]) and (self.wizard().size().width() > preferedSize[0]):
            self.wizard().resize(preferedSize[0],preferedSize[1])
            self.wizard().move(center.x()-self.wizard().width()*0.5, center.y()-self.wizard().height()*0.5)
        
    def _loadTreeModel(self):
        
        self.model = simple_tree_model.SimpleTreeModel(self)
        controllerinfos = self._pool.get_controller_class_infos()
        controllers = self._pool.get_controller_infos()
        self.model.sort(-1)
        
        for item in controllerinfos:
            self.model.addRecord(["Controller",taurus.core.tango.sardana.PoolElementType[item.get_controller_type()] ,item.get_name()], item , False)

        elementTypeList =  taurus.core.tango.sardana.PoolElementType.keys()
        elementTypeList.sort()
        for type in elementTypeList:
            self.model.addNodes([type], False)
        for item in controllers:
            self.model.addRecord([taurus.core.tango.sardana.PoolElementType[item.get_controller_type()], item.get_name() ], item , False)

        self._treeView.setModel(self.model)
        
    def setupUi(self):
        self._treeView =SimpleTreeView(self)
        self._treeView.setSizePolicy(QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum)
        self._layout.addWidget(self._treeView,0,0,1,1)
        self._tabWidget = QtGui.QTabWidget(self)
        self._settingsTab = QtGui.QWidget(self)
        self._horizontalLayout_2 = QtGui.QHBoxLayout(self._settingsTab)
        self._scrollArea = QtGui.QScrollArea(self._settingsTab)
        self._scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self._scrollArea.setWidgetResizable(True)
        self._scrollAreaWidgetContents = QtGui.QWidget(self._scrollArea)
        self._scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 263, 316))
        self._gridLayout_2 = QtGui.QGridLayout(self._scrollAreaWidgetContents)
        self._settings = settings_widget.SettingsWidget()
        self._hardwareSettings = HardwareSettings()
        self._gridLayout_2.addWidget(self._settings)
        self._scrollArea.setWidget(self._scrollAreaWidgetContents)
        self._horizontalLayout_2.addWidget(self._scrollArea)
        self._tabWidget.addTab(self._settingsTab, "Settings")
        self._descriptionTab = QtGui.QWidget()
        self._horizontalLayout = QtGui.QHBoxLayout(self._descriptionTab)
        self._scrollArea_2 = QtGui.QScrollArea(self._descriptionTab)
        self._scrollArea_2.setFrameShape(QtGui.QFrame.NoFrame)
        self._scrollArea_2.setWidgetResizable(True)
        self._scrollAreaWidgetContents_2 = QtGui.QWidget(self._scrollArea_2)
        self._gridLayout_3 = QtGui.QGridLayout(self._scrollAreaWidgetContents_2)
        self._description = DescriptionWidget()
        self._gridLayout_3.addWidget(self._description)
        self._scrollArea_2.setWidget(self._scrollAreaWidgetContents_2)
        self._horizontalLayout.addWidget(self._scrollArea_2)
        self._tabWidget.addTab(self._descriptionTab, "Description")
        self._tabWidget.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        
        self._layout.addWidget(self._tabWidget,0,1,1,2)
        self._tabWidget.setCurrentIndex(0)
        self._status_label = QtGui.QLabel()
        self._status_label.setAutoFillBackground(True)
        palette = self._status_label.palette()
        gradient = QtGui.QLinearGradient(0, 0, 0, 15)
        gradient.setColorAt(0.0, Qt.QColor.fromRgb( 60, 150, 255))
        gradient.setColorAt(0.5, Qt.QColor.fromRgb(  0,  85, 227))
        gradient.setColorAt(1.0, Qt.QColor.fromRgb( 60, 150, 255))
        gradient.setSpread(QtGui.QGradient.RepeatSpread)
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(gradient))
        palette.setBrush(QtGui.QPalette.WindowText, Qt.Qt.white)
        self._layout.addWidget(self._status_label,1,0,1,3)
        self._description.setVisible(False)
        self._settings.setVisible(False)
    
    def setStatus(self, text):
        self._status_label.setText(text)
        
    def picked(self):
        return self._treeView.currentFields()

    def activated(self, name):
        

        if (self.picked() is not None) and (self.picked() !=self._currentItem):
            ret = QtGui.QMessageBox().Yes
            if self._settings.isEdited():
                msgBox = QtGui.QMessageBox()
                msgBox.setText("Confirmation              ")
                msgBox.setStandardButtons(QtGui.QMessageBox().No | QtGui.QMessageBox().Yes )
                msgBox.setInformativeText("Do you want to leave the editor of %s without saving the changes?" % self._currentItem.get_name() )
                msgBox.setIcon(QtGui.QMessageBox.Question)
                ret = msgBox.exec_()
                
            if ret == QtGui.QMessageBox().Yes:
                self._settings.setEdited(False)
                self._currentItem = self.picked()
                self._currentItemIndex = self._treeView.currentIndex()
                
                if type(self._currentItem) == taurus.core.tango.sardana.sardana.ControllerClassInfo:
                    
                    self._gridLayout_2.addWidget(self._settings)
                    self._settings.setVisible(True)
                    self._gridLayout_2.removeWidget(self._hardwareSettings)
                    self._hardwareSettings.setVisible(False)
                    self._description.setVisible(True)
                    self._tabWidget.setTabEnabled(1,True)
                    self.setStatus("Editing: "+ self.picked().get_name())
                    
                    
                    self._settings.setProperties(self.picked().get_properties())
                    QtCore.QObject.connect(self._settings, QtCore.SIGNAL("propertyValueChanged()"), self.checkData)
                    self._description.setOrganization(self.picked().get_organization())
                    self._description.setFamily(self.picked().get_family())
                    self._description.setModel(self.picked().get_model())
                    self._description.setDescription(self.picked().get_description())
                    self._description.setImage(None)
                    
                if type(self._currentItem) == taurus.core.tango.sardana.sardana.ControllerInfo:
                    
                    self._gridLayout_2.removeWidget(self._settings)
                    self._settings.setVisible(False)
                    self._gridLayout_2.addWidget(self._hardwareSettings)
                    self._hardwareSettings.setVisible(True)
                    self._tabWidget.setTabEnabled(1,False)
                    self.setStatus("Editing: "+ self.picked().get_name())   
            else:
                self._treeView.selectionModel().setCurrentIndex(self._currentItemIndex, QtGui.QItemSelectionModel.SelectCurrent)
                
        self.checkData()
            
    def setNextPageId(self, id):
        self._nextPageId = id
        
    def isComplete(self):
        return self._valid
    
    
class NewDeviceCommitBasePage(wiz.SardanaIntroBasePage):
    
    def __init__(self, parent = None):
        QtGui.QWizardPage.__init__(self, parent)
        self.setPixmap(QtGui.QWizard.WatermarkPixmap, QtGui.QPixmap(":/watermark.jpg"))
        self._layout = QtGui.QFormLayout()
        self.setCommitPage(True)
        self.setTitle('Confirmation')
        
    def next(self):
        QWizard.next(self)
        
    def _set_style(self, w):
        f = w.font()
        f.setBold(True)
        w.setFont(f)
        return w
        
    def initializePage(self):
        wiz.SardanaIntroBasePage.initializePage(self)
        self._previousPageSize = copy.deepcopy([self.wizard().size().width(),self.wizard().size().height()])
        self.setPixmap(QtGui.QWizard.WatermarkPixmap, QtGui.QPixmap(":/watermark.jpg"))
        self._spacerItem1 = QtGui.QSpacerItem(800, 600, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)  
        self._layout.addItem(self._spacerItem1)
        preferedSize = [600,600] # prefered size for this page
        desktopRect = QtGui.QApplication.desktop().availableGeometry(self)
        center = desktopRect.center()
        if (not self.wizard().isMaximized()):
            self.wizard().resize(preferedSize[0],preferedSize[1])
            self.wizard().move(center.x()-self.wizard().width()*0.5, center.y()-self.wizard().height()*0.5)
        
            # and (self.wizard().size().height () > preferedSize[1]) and (self.wizard().size().width() > preferedSize[0]):
        
    def cleanupPage(self):
        wiz.SardanaIntroBasePage.cleanupPage(self)
        self.setPixmap(QtGui.QWizard.WatermarkPixmap, QtGui.QPixmap())
        preferedSize = copy.deepcopy(self._previousPageSize) # setUp size for previous page
        desktopRect = QtGui.QApplication.desktop().availableGeometry(self)
        center = desktopRect.center()
        if (not self.wizard().isMaximized()) and (self.wizard().size().height () < preferedSize[1]) and (self.wizard().size().width() < preferedSize[0]):
            self.wizard().move(center.x()-preferedSize[0]*0.5, center.y()-preferedSize[1]*0.5)
            self.wizard().resize(preferedSize[0],preferedSize[1])

    def setNextPageId(self, id):
        self._nextPageId = id


class DescriptionWidget(QtGui.QWidget):
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.setupUi()
        
    def setupUi(self):
        self._imageSize = [100,100]
        self._formLayout = QtGui.QFormLayout(self)
        self._organizationLabel = QtGui.QLabel("Organization:")
        self._formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self._organizationLabel)
        self._organizationLabelText = QtGui.QLabel(self)
        self._organizationLabelText.setFrameShape(QtGui.QFrame.Panel)
        self._organizationLabelText.setFrameShadow(QtGui.QFrame.Sunken)
        self._organizationLabelText.setWordWrap(False)
        self._formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self._organizationLabelText)
        self._familyLabel = QtGui.QLabel("Family:")
        self._formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self._familyLabel)
        self._familyLabelText = QtGui.QLabel(self)
        self._familyLabelText.setFrameShape(QtGui.QFrame.Panel)
        self._familyLabelText.setFrameShadow(QtGui.QFrame.Sunken)
        self._familyLabelText.setWordWrap(False)
        self._formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self._familyLabelText)
        self._modelLabel = QtGui.QLabel("Model:")
        self._formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self._modelLabel)
        self._modelLabelText = QtGui.QLabel(self)
        self._modelLabelText.setFrameShape(QtGui.QFrame.Panel)
        self._modelLabelText.setFrameShadow(QtGui.QFrame.Sunken)
        self._modelLabelText.setWordWrap(False)
        self._formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self._modelLabelText)
        self._descriptionLabel = QtGui.QLabel("Description:")
        self._formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self._descriptionLabel)
        self._descriptionLabelText = QtGui.QLabel(self)
        self._descriptionLabelText.setFrameShape(QtGui.QFrame.Panel)
        self._descriptionLabelText.setFrameShadow(QtGui.QFrame.Sunken)
        self._descriptionLabelText.setWordWrap(True)
        self._descriptionLabelText.setAlignment(QtCore.Qt.AlignTop)
        self._formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self._descriptionLabelText)
        self._imageLabel = QtGui.QLabel("Image:")
        self._formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self._imageLabel)
        self._deviceLogo = QtGui.QLabel(self)
        self._deviceLogo.setPixmap(taurus.qt.qtgui.resource.getThemePixmap("image-missing").scaled(*self._imageSize))
        self._deviceLogo.pixmap()
        self._deviceLogo.setAlignment(QtCore.Qt.AlignHCenter)
        self._formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self._deviceLogo)
        
    def setOrganization(self, name):
        self._organizationLabelText.setText(name)
    
    def setFamily(self,name):
        self._familyLabelText.setText(name)
        
    def setModel(self, name):
        self._modelLabelText.setText(name)
        
    def setDescription(self, text):
        self._descriptionLabelText.setText(text)
        
    def setImage(self, image):
        if type(image)==QtGui.QPixmap:
            self._deviceLogo.setPixmap(image.scaled(*self._imageSize))
        elif type(image)==QtGui.QImage:
            self._deviceLogo.setPixmap(QtGui.QPixmap().fromImage(image).scaled(*self._imageSize))
        else:
            self._deviceLogo.setPixmap(taurus.qt.qtgui.resource.getThemePixmap("image-missing").scaled(50,50))
    

def addDevice(Sardana=None, Pool=None):
    app = QtGui.QApplication([])
    QtCore.QResource.registerResource(get_resources())
    Pages = Enumeration('Pages', ('SelectSardanaPool', 'NewDevice','CommitPage','OutroPage'))
    w = wiz.SardanaBaseWizard()
    w.setWindowTitle("Add New Hardware Wizard")
    selectPool = SelectSardanaPoolBasePage(Sardana,Pool)
    w.setPage(Pages.SelectSardanaPool, selectPool)
    selectPool.setNextPageId(Pages.NewDevice)
    newDevice = NewDeviceBasePage()
    w.setPage(Pages.NewDevice, newDevice)
    newDevice.setNextPageId(Pages.CommitPage)
    commit_page = NewDeviceCommitBasePage()
    w.setPage(Pages.CommitPage, commit_page)
    commit_page.setNextPageId(Pages.OutroPage)
    w.show()
    sys.exit(app.exec_())

def get_resources():
    res_fname = os.path.abspath(__file__)
    res_fname = os.path.splitext(res_fname)[0] + '.rcc'
    return res_fname
      
if __name__ == "__main__":
    addDevice()

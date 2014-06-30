import os, sys, wx, copy, taurus, settings_widget, simple_tree_model, wiz
import taurus.qt.qtgui.resource
from PyQt4 import QtGui, QtCore, Qt
from types import *
from taurus.core.util.enumeration import Enumeration
from sardana.taurus.core.tango.sardana import SardanaManager
from sardana.taurus.core.tango.sardana import PoolElementType

"""This wizard is created for adding new devices. At the moment it has 4 pages:

- SelectSardanaPool
- NewDevice
- CommitPage
- OutroPage
"""

class SelectSardanaPoolBasePage(wiz.SardanaBasePage):
    """Page for selecting Sardana and Pool
    
    Selected values are saved in
    
    self['sardana']
    self['pool']
    
    """

    def __init__(self, sardana=None, pool=None, parent=None):
        wiz.SardanaBasePage.__init__(self, parent)
        self._sardana = sardana
        self._pool = pool

        self.setSubTitle('Please select the Pool from existing Sardana')
        self._valid = True
        self._panel = self.getPanelWidget()
        layout = QtGui.QGridLayout()
        self._sardanaNameCB = QtGui.QComboBox()
        self._poolNameCB = QtGui.QComboBox()
        layout.addItem(QtGui.QSpacerItem(60, 60, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum), 0, 0)
        layout.addWidget(QtGui.QLabel("Sardana"), 0, 1)
        layout.addItem(QtGui.QSpacerItem(60, 60, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum), 0, 3)
        layout.addWidget(self._sardanaNameCB, 0, 2)
        layout.addWidget(QtGui.QLabel("Pool"), 1, 1)
        layout.addWidget(self._poolNameCB, 1, 2)
        layout.addItem(QtGui.QSpacerItem(200, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum), 2, 2)
        self._panel.setLayout(layout)
        self.setStatus("Select the instances of Sardana and Pool, and click Next to continue")

        self['sardana'] = self._getSardana
        self['pool'] = self._getPool
        self.connect(self._sardanaNameCB, QtCore.SIGNAL('currentIndexChanged(int)'), self._fillPoolNameCB)

    def initializePage(self):
        wiz.SardanaBasePage.initializePage(self)
        self._isSardanaProper = False
        if (self._sardana) and (self._sardana in self._getSardanas()):
            self._sardanaNameCB.addItem(self._sardana)
            self._sardanaNameCB.setEnabled(False)
            self._isSardanaProper = True
        else:
            self._fillSardanaNameCB()

        self._isPoolProper = False
        if (self._pool) and (self._isSardanaProper):
            for pool in self._getSardana().get_pools():
                if self._pool == pool.get_name():
                    self._isPoolProper = True

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

    def _fillPoolNameCB(self, int=None):
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
    """
        extended version of QTreeView that is emitting signals of activation and expansion
    """

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
        if not self.model() == None:
            for column in range(self.model().columnCount(
                                QtCore.QModelIndex())):
                self.resizeColumnToContents(column)

class AxisSteper(Qt.QSpinBox):
    """ Object of this class is a Spin box that can jumps from 1 to the total number 
        of axis while skipping busy values
    """
    def __init__(self, controllerInfo=None, busyValues=[], parent=None):
        Qt.QSpinBox.__init__(self, parent)
        self._busyValues = busyValues
        self._controllerInfo = controllerInfo
        self.setControllerInfo(controllerInfo)
        QtCore.QObject.connect(self.lineEdit(), QtCore.SIGNAL("editingFinished()"), self._textEdited)

    def _textEdited(self):
        axis = int(self.value())
        if not self._controllerInfo.is_axis_free(axis):
            self._findFreeAxis()

    def getValue(self):
        return self.value()

    def setControllerInfo(self, controllerInfo):
        self._controllerInfo = controllerInfo
        if self._controllerInfo:
            self.setMaximum(self._controllerInfo.get_max_elements() - 1)
            self._findFreeAxis()

    def _findFreeAxis(self):
        for axis in range(self._controllerInfo.get_max_elements()):
            if self.is_axis_free(axis):
                self.setValue(axis)
                break

    def is_axis_free(self, axis):
        if self._controllerInfo.is_axis_free(axis):
            for busyAxis in self._busyValues:
                if axis == busyAxis:
                    return False
            return True
        else:
            return False

    def stepBy(self, step):
        i = 1
        while True:
            axis = self.value() + i * step
            if self.is_axis_free(self.value() + i * step):
                break
            i += 1
        if axis >= 0 and axis < self._controllerInfo.get_max_elements():
            self.setValue(axis)


class SingleAxisWidget(Qt.QWidget):
    """
        Widget for selecting name and axis for the device 
    """
    def __init__(self, parent=None):
        Qt.QWidget.__init__(self, parent)
        self._layout = QtGui.QGridLayout(self)
        self.setLayout(self._layout)
        self.setupUi()
        self._controllerInfo = None
        self._edited = False

    def setupUi(self):
        self._nameLabel = Qt.QLabel("Name:")
        self._nameLineEdit = Qt.QLineEdit()
        self._nameLineEdit.setMinimumSize(200, 25)
        self._layout.addWidget(self._nameLabel, 0, 0, 1, 1)
        self._layout.addWidget(self._nameLineEdit, 0, 1, 1, 1)
        self._monitorLabel = Qt.QLabel("Monitor List:")
        self._axisLabel = Qt.QLabel("Axis:")
        self._axisSpinBox = AxisSteper()
        self._layout.addWidget(self._axisLabel, 1, 0, 1, 1)
        self._layout.addWidget(self._axisSpinBox, 1, 1, 1, 1)
        QtCore.QObject.connect(self._axisSpinBox.lineEdit(), QtCore.SIGNAL("textEdited(QString)"), self._textEdited)
        QtCore.QObject.connect(self._nameLineEdit, QtCore.SIGNAL("textEdited(QString)"), self._textEdited)

    def _textEdited(self, str):
        self._edited = True

    def setControllerInfo(self, controllerInfo):
        self._nameLineEdit.setText("")
        self._edited = False
        self._controllerInfo = controllerInfo
        self._axisSpinBox.setControllerInfo(self._controllerInfo)

    def isEdited(self):
        return self._edited

    def getValue(self):
        return None


class NameEditorWidget(QtGui.QLineEdit):
    """
        for editing the name, it has to check the name if it exist in the sardana .. but it does
    """

    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.setValue(self.getDefaultValue())

    def setValue(self, value):
        if value is None:
            value = self.getDefaultValue()
        self.setText(str(value))
        self._actualValue = self.getValue()

    def getValue(self):
        return str(self.text())

    def textChanged(self, string):
        QtGui.QLineEdit.textChanged(self, string)

    def focusOutEvent (self, event):  #QFocusEvent
        QtGui.QLineEdit.focusOutEvent(self, event)
        self.valueChanged()

    def valueChanged(self):
        if not (self.getValue() == self._actualValue):
            self.emit(QtCore.SIGNAL("valueChanged"), self._actualValue, self.getValue())
        self._actualValue = self.getValue()
        self.setValue(self.getValue())  # if value is not valid

    @classmethod
    def getDefaultValue(self):
        return ""

class TableAxisDelegate(QtGui.QItemDelegate):
    """
    Item delegate for Table Axis Widget
    """

    def __init__(self, parent=None):
        QtGui.QItemDelegate.__init__(self, parent)

    def setControllerInfo(self, controllerInfo):
        self._controllerInfo = controllerInfo

    def createEditor(self, parent, option, index):
        if index.column() == 0:
            editor = NameEditorWidget(parent)
            editor.installEventFilter(self)
        if index.column() == 1:
            editor = AxisSteper(self._controllerInfo, self.parent().parent().getAxisList(), parent=parent)
            editor.installEventFilter(self)

        return editor

    def setEditorData(self, editor, index):
        if index.column() == 0:
            value = index.model().data(index, QtCore.Qt.DisplayRole)
            editor.setValue(value.toString())
        if index.column() == 1:
            value = index.model().data(index, QtCore.Qt.DisplayRole)
            int , bool = value.toInt()
            editor.setValue(int)

    def setModelData(self, editor, model, index):
        self.emit(QtCore.SIGNAL("editorValueChanged"), editor.getValue(), index.row(), index.column())
        value = editor.getValue()
        if index.column() == 0:  #name
            model.setData(index
                    , QtCore.QVariant(value))
        if index.column() == 1:  #axis
            if editor.is_axis_free(int(value)):
                model.setData(index , QtCore.QVariant(value))

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class TableAxisWidget (QtGui.QWidget):
    """
    Table for selecting multiple axis
    """
    def __init__(self, value=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self._controllerInfo = None
        self._layout = QtGui.QHBoxLayout(self)
        self.setLayout(self._layout)
        self._tableView = QtGui.QTableView()
        self._tableView.mousePressEvent = self.mousePressEvent
        self._tableView.setSelectionMode(QtGui.QTableView.SingleSelection)
        self._layout.addWidget(self._tableView)
        self._verticalLayout = QtGui.QVBoxLayout()
        self._addRowButton = QtGui.QPushButton(self)
        self._addRowButton.setIcon(taurus.qt.qtgui.resource.getThemeIcon("list-add"))
        self._addRowButton.setText("Add Device       ")
        self._verticalLayout.addWidget(self._addRowButton)
        self._removeRowButton = QtGui.QPushButton(self)
        self._removeRowButton.setIcon(taurus.qt.qtgui.resource.getThemeIcon("list-remove"))
        self._removeRowButton.setText("Remove Device    ")
        self._verticalLayout.addWidget(self._removeRowButton)
        self._upButton = QtGui.QPushButton(self)
        self._upButton.setIcon(taurus.qt.qtgui.resource.getThemeIcon("go-up"))
        self._upButton.setText("Move Up   ")
        self._verticalLayout.addWidget(self._upButton)
        self._downButton = QtGui.QPushButton(self)
        self._downButton.setIcon(taurus.qt.qtgui.resource.getThemeIcon("go-down"))
        self._downButton.setText("Move Down")
        self._verticalLayout.addWidget(self._downButton)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self._verticalLayout.addItem(spacerItem)
        QtCore.QObject.connect(self._addRowButton, QtCore.SIGNAL("clicked()"), self._addRow)
        QtCore.QObject.connect(self._removeRowButton, QtCore.SIGNAL("clicked()"), self._removeRow)
        QtCore.QObject.connect(self._upButton, QtCore.SIGNAL("clicked()"), self._moveUp)
        QtCore.QObject.connect(self._downButton, QtCore.SIGNAL("clicked()"), self._moveDown)
        self._layout.addLayout(self._verticalLayout)
        self._delegate = TableAxisDelegate(self._tableView)
        #QtCore.QObject.connect(self._delegate, QtCore.SIGNAL("editorValueChanged"), self._valueChanged)
        self._tableView.setItemDelegate(self._delegate)
        QtCore.QObject.connect(self._delegate, QtCore.SIGNAL("editorValueChanged"), self._textEdited)
        #self._tableView.setItemDelegate(self._delegate)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        self._tableView.setSizePolicy(sizePolicy)
        self._tableView.horizontalHeader().setDefaultSectionSize(80)
        self._tableView.horizontalHeader().setVisible(True)
        self._tableView.horizontalHeader().setStretchLastSection(True)
        self._tableView.setMinimumSize(QtCore.QSize(150, 150))
        self._edited = False

    def _textEdited(self, str=None):
        self._edited = True

    def isEdited(self):
        return self._edited

    def getAxisList(self):
        list = []
        for row in self.getValue():
            list.append(row[1])
        return list

    def _findFreeAxis(self):
        for axis in range(self._controllerInfo.get_max_elements()):
            if self.is_axis_free(axis):
                return axis

        return None

    def is_axis_free(self, axis):
        if self._controllerInfo.is_axis_free(axis):
            for busyAxis in self.getAxisList():
                if axis == busyAxis:
                    return False
            return True
        else:
            return False

    def setControllerInfo(self, controllerInfo):
        self.setValue([])
        self._controllerInfo = controllerInfo
        self._delegate.setControllerInfo(self._controllerInfo)
        self._edited = False

    def _getSelectedIndex(self):
        if len (self._tableView.selectedIndexes()):
            row = self._tableView.selectedIndexes()[0].row()
            column = self._tableView.selectedIndexes()[0].column()
        else:
            row = None
            column = None
        return [row, column]

    def _addRow(self):
        value = self.getValue()  # stored table
        rows = len(value)

        if rows < self._controllerInfo.get_max_elements():
            rowIndex = self._getSelectedIndex()[0]
            if rowIndex is None:
                rowIndex = rows
            value.insert(rowIndex, ["", self._findFreeAxis()])
            self.setValue(value)
            self._textEdited()

        if self._findFreeAxis() is None:
            self._addRowButton.setEnabled(False)

    def _removeRow(self):
        rowIndex = self._getSelectedIndex()[0]
        if rowIndex is not None:
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Confirmation              ")
            msgBox.setStandardButtons(QtGui.QMessageBox().No | QtGui.QMessageBox().Yes)
            msgBox.setInformativeText("Remove device {%i} ?" % (rowIndex + 1))
            msgBox.setIcon(QtGui.QMessageBox.Question)
            ret = msgBox.exec_()
        if ret == QtGui.QMessageBox().Yes:
           value = self.getValue()
           self.setValue(value[:rowIndex] + value[rowIndex + 1:])
           self._textEdited()
           self._addRowButton.setEnabled(True)

    def _moveUp(self):
        value = self.getValue()  # stored table
        rows = len(value)
        rowIndex = self._getSelectedIndex()[0]
        if (rows > 1) and (rowIndex is not None) and (rowIndex > 0) :
            x = value.pop(rowIndex)
            value.insert(rowIndex - 1, x)
            self.setValue(value)
            self._tableView.setCurrentIndex(self._tableView.model().index(rowIndex - 1, 0))
            self._textEdited()

    def _moveDown(self):
        value = self.getValue()  # stored table
        rows = len(value)
        rowIndex = self._getSelectedIndex()[0]
        if (rows > 1) and (rowIndex is not None) and (rowIndex < rows - 1) :
            x = value.pop(rowIndex)
            value.insert(rowIndex + 1, x)
            self.setValue(value)
            self._tableView.setCurrentIndex(self._tableView.model().index(rowIndex + 1, 0))
            self._textEdited()

    def setValue(self, value):
        rows = len(value)
        columns = 2
        self._model = QtGui.QStandardItemModel(rows, columns)
        for row in range(rows):
            for column in range(columns):
                index = self._model.index(row, column, QtCore.QModelIndex())
                self._model.setData(index, QtCore.QVariant(value[row][column]))
        self._model.setHeaderData(0, Qt.Qt.Horizontal, Qt.QVariant("Name"))
        self._model.setHeaderData(1, Qt.Qt.Horizontal, Qt.QVariant("Axis"))
        self._tableView.setModel(self._model)
        self._tableView.horizontalHeader().setVisible(True)
        self._tableView.horizontalHeader().setStretchLastSection(True)

    def getValue(self):
        rows = self._model.rowCount()
        result = []
        for row in range(rows):
            records = []
            index = self._model.index(row, 0)
            name = self._model.data(index).toString()
            index = self._model.index(row, 1)
            axis, bool = self._model.data(index).toInt()
            result.append([name, axis])

        return copy.deepcopy(result)


class MultipleAxisWidget(Qt.QWidget):
    """
    Wizard for selecting multiple axis
    Method getValue() returns two dimensional array
        where the first column is name and the second is axis 
    """

    def __init__(self, parent=None):
        Qt.QWidget.__init__(self, parent)
        self._layout = QtGui.QGridLayout(self)
        self.setLayout(self._layout)
        self.setupUi()
        self._controllerInfo = None
        self._edited = False

    def setupUi(self):
        self._tableAxisWidget = TableAxisWidget()
        self._layout.addWidget(self._tableAxisWidget, 0, 0, 1, 1)

    def setControllerInfo(self, controllerInfo):
        self._edited = False
        self._controllerInfo = controllerInfo
        self._tableAxisWidget.setControllerInfo(self._controllerInfo)

    def isEdited(self):
        return self._tableAxisWidget.isEdited()

    def getValue(self):
        return self._tableAxisWidget.getValue()


class HardwareSettings(Qt.QWidget):
    """
    Page for editing single or multiple axis devices
    """

    def __init__(self, parent=None):
        Qt.QWidget.__init__(self, parent)
        self._layout = QtGui.QGridLayout(self)
        self.setLayout(self._layout)
        self.setupUi()
        self._controllerInfo = None
        self._edited = False
        self._changeView()

    def setupUi(self):
        self.setVisible(False)
        self._singleButton = QtGui.QRadioButton(self)
        self._singleButton.setText("Single")
        self._singleButton.setChecked(True)
        self._layout.addWidget(self._singleButton, 0, 0)
        self._multipleButton = QtGui.QRadioButton(self)
        self._multipleButton.setText("Multiple")
        self._layout.addWidget(self._multipleButton, 0, 1)
        self._singleAxisWidget = SingleAxisWidget()
        self._layout.addWidget(self._singleAxisWidget, 1, 0, 1, 2)
        self._multipleAxisWidget = MultipleAxisWidget()
        self._layout.addWidget(self._multipleAxisWidget, 2, 0, 1, 2)

        QtCore.QObject.connect(self._singleButton, QtCore.SIGNAL("clicked()"), self._changeView)
        QtCore.QObject.connect(self._multipleButton, QtCore.SIGNAL("clicked()"), self._changeView)
        self._spacerItem1 = Qt.QSpacerItem(10, 0, Qt.QSizePolicy.Fixed, Qt.QSizePolicy.Expanding)
        self._layout.addItem(self._spacerItem1, 4, 0, 1, 1, Qt.Qt.AlignCenter)

    def _changeView(self):
        if self._singleButton.isChecked():
            self._singleAxisWidget.setVisible(True)
            self._multipleAxisWidget.setVisible(False)
        else:
            self._singleAxisWidget.setVisible(False)
            self._multipleAxisWidget.setVisible(True)

    def setControllerInfo(self, controllerInfo):
        self._controllerInfo = controllerInfo
        self._singleAxisWidget.setControllerInfo(self._controllerInfo)
        self._multipleAxisWidget.setControllerInfo(self._controllerInfo)

    def isEdited(self):
        return self._singleAxisWidget.isEdited() or self._multipleAxisWidget.isEdited()


class NewDeviceBasePage(wiz.SardanaBasePage):
    """
    Base Page for selecting and editing Devices
   """

    def __init__(self, parent=None):
        wiz.SardanaBasePage.__init__(self, parent)
        self._valid = False
        QtGui.QWizardPage.__init__(self, parent)
        self._layout = QtGui.QGridLayout(self)
        self.setupUi()
        self.setLayout(self._layout)
        self.setTitle('Selecting device')
        self.connect(self._treeView, QtCore.SIGNAL("activated"),
             self.activated)
        self._currentItem = None
        self._currentItemIndex = None

    def getProperties(self):
        if self._settings is not None:
            return self._settings.getProperties()
        else:
            return None

    def checkData(self):
        if self.picked():
            properties, name, values = self.getProperties()
            if len(name):
                self.setStatus("Editing: " + self.picked().get_name())
                self._valid = True
            else:
                self.setStatus('The name is invalid')
                self._valid = False
        else:
            self.setStatus('Please select a device')
            self._valid = False

        self.emit(QtCore.SIGNAL('completeChanged()'))

    def keyPressEvent(self, event):
        wiz.SardanaBasePage.keyPressEvent(self, event)
        if self._tabWidget.currentIndex() == 0:
            undo = (event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Z)
            redo = (event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Y)
            if (undo):
                self._settings.undo()
            if (redo):
                self._settings.redo()

    def initializePage(self):
        wiz.SardanaIntroBasePage.initializePage(self)
        self.wizard().__setitem__("properties", self.getProperties)
        # resizing application
        self._previousPageSize = copy.deepcopy([self.wizard().size().width(), self.wizard().size().height()])
        preferedSize = [800, 600]
        desktopRect = QtGui.QApplication.desktop().availableGeometry(self)
        center = desktopRect.center()
        if (not self.wizard().isMaximized()) and (self.wizard().size().height () < preferedSize[1]) and (self.wizard().size().width() < preferedSize[0]):
            self.wizard().resize(preferedSize[0], preferedSize[1])
            self.wizard().move(center.x() - self.wizard().width() * 0.5, center.y() - self.wizard().height() * 0.5)
        self._pool = self.wizard()["pool"]
        self._loadTreeModel()
        self.checkData()

    def cleanupPage(self):
        wiz.SardanaIntroBasePage.cleanupPage(self)
        preferedSize = copy.deepcopy(self._previousPageSize)  # setUp size for previous page
        desktopRect = QtGui.QApplication.desktop().availableGeometry(self)
        center = desktopRect.center()

        if (not self.wizard().isMaximized()) and (self.wizard().size().height () > preferedSize[1]) and (self.wizard().size().width() > preferedSize[0]):
            self.wizard().resize(preferedSize[0], preferedSize[1])
            self.wizard().move(center.x() - self.wizard().width() * 0.5, center.y() - self.wizard().height() * 0.5)

    def _loadTreeModel(self):

        self.model = simple_tree_model.SimpleTreeModel(self)
        controllerinfos = self._pool.get_controller_class_infos()
        controllers = self._pool.get_controller_infos()
        self.model.sort(-1)

        for item in controllerinfos:
            self.model.addRecord(["Controller", PoolElementType[item.get_controller_type()] , item.get_name()], item , False)

        elementTypeList = PoolElementType.keys()
        elementTypeList.sort()
        for type in elementTypeList:
            self.model.addNodes([type], False)
        for item in controllers:
            self.model.addRecord([PoolElementType[item.get_controller_type()], item.get_name() ], item , False)

        self._treeView.setModel(self.model)

    def setupUi(self):
        self._treeView = SimpleTreeView(self)
        self._treeView.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self._layout.addWidget(self._treeView, 0, 0, 1, 1)
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
        self._tabWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self._layout.addWidget(self._tabWidget, 0, 1, 1, 2)
        self._tabWidget.setCurrentIndex(0)
        self._status_label = QtGui.QLabel()
        self._status_label.setAutoFillBackground(True)
        palette = self._status_label.palette()
        gradient = QtGui.QLinearGradient(0, 0, 0, 15)
        gradient.setColorAt(0.0, Qt.QColor.fromRgb(60, 150, 255))
        gradient.setColorAt(0.5, Qt.QColor.fromRgb(0, 85, 227))
        gradient.setColorAt(1.0, Qt.QColor.fromRgb(60, 150, 255))
        gradient.setSpread(QtGui.QGradient.RepeatSpread)
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(gradient))
        palette.setBrush(QtGui.QPalette.WindowText, Qt.Qt.white)
        self._layout.addWidget(self._status_label, 1, 0, 1, 3)
        self._description.setVisible(False)
        self._settings.setVisible(False)

    def setStatus(self, text):
        self._status_label.setText(text)

    def picked(self):
        return self._treeView.currentFields()

    def activated(self, name):

        if (self.picked() is not None) and (self.picked() != self._currentItem):
            ret = QtGui.QMessageBox().Yes
            if self._settings.isEdited() or self._hardwareSettings.isEdited():
                msgBox = QtGui.QMessageBox()
                msgBox.setText("Confirmation              ")
                msgBox.setStandardButtons(QtGui.QMessageBox().No | QtGui.QMessageBox().Yes)
                msgBox.setInformativeText("Do you want to leave the editor of %s without saving the changes?" % self._currentItem.get_name())
                msgBox.setIcon(QtGui.QMessageBox.Question)
                ret = msgBox.exec_()

            if ret == QtGui.QMessageBox().Yes:
                self._settings.setEdited(False)
                self._hardwareSettings.setControllerInfo(None)
                self._currentItem = self.picked()
                self._currentItemIndex = self._treeView.currentIndex()

                if type(self._currentItem) == taurus.core.tango.sardana.sardana.ControllerClassInfo:

                    self._gridLayout_2.addWidget(self._settings)
                    self._settings.setVisible(True)
                    self._gridLayout_2.removeWidget(self._hardwareSettings)
                    self._hardwareSettings.setVisible(False)
                    self._description.setVisible(True)
                    self._tabWidget.setTabEnabled(1, True)
                    self.setStatus("Editing: " + self.picked().get_name())


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
                    self._hardwareSettings.setControllerInfo(self._currentItem)
                    self._tabWidget.setTabEnabled(1, False)
                    self.setStatus("Editing: " + self.picked().get_name())
            else:
                self._treeView.selectionModel().setCurrentIndex(self._currentItemIndex, QtGui.QItemSelectionModel.SelectCurrent)


        self.checkData()

    def setNextPageId(self, id):
        self._nextPageId = id

    def isComplete(self):
        return self._valid


class NewDeviceCommitBasePage(wiz.SardanaIntroBasePage):
    """
    The last commiting page on the wizard, doesn't work at the moment
    """

    def __init__(self, parent=None):
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
        self._previousPageSize = copy.deepcopy([self.wizard().size().width(), self.wizard().size().height()])
        self.setPixmap(QtGui.QWizard.WatermarkPixmap, QtGui.QPixmap(":/watermark.jpg"))
        self._spacerItem1 = QtGui.QSpacerItem(800, 600, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self._layout.addItem(self._spacerItem1)
        preferedSize = [600, 600]  # prefered size for this page
        desktopRect = QtGui.QApplication.desktop().availableGeometry(self)
        center = desktopRect.center()
        if (not self.wizard().isMaximized()):
            self.wizard().resize(preferedSize[0], preferedSize[1])
            self.wizard().move(center.x() - self.wizard().width() * 0.5, center.y() - self.wizard().height() * 0.5)
            # and (self.wizard().size().height () > preferedSize[1]) and (self.wizard().size().width() > preferedSize[0]):

    def cleanupPage(self):
        wiz.SardanaIntroBasePage.cleanupPage(self)
        self.setPixmap(QtGui.QWizard.WatermarkPixmap, QtGui.QPixmap())
        preferedSize = copy.deepcopy(self._previousPageSize)  # setUp size for previous page
        desktopRect = QtGui.QApplication.desktop().availableGeometry(self)
        center = desktopRect.center()
        if (not self.wizard().isMaximized()) and (self.wizard().size().height () < preferedSize[1]) and (self.wizard().size().width() < preferedSize[0]):
            self.wizard().move(center.x() - preferedSize[0] * 0.5, center.y() - preferedSize[1] * 0.5)
            self.wizard().resize(preferedSize[0], preferedSize[1])

    def setNextPageId(self, id):
        self._nextPageId = id


class DescriptionWidget(QtGui.QWidget):
    """
    The part of the wizard that shows the object description (text + picture)
    """

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi()

    def setupUi(self):
        self._imageSize = [100, 100]
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

    def setFamily(self, name):
        self._familyLabelText.setText(name)

    def setModel(self, name):
        self._modelLabelText.setText(name)

    def setDescription(self, text):
        self._descriptionLabelText.setText(text)

    def setImage(self, image):
        if type(image) == QtGui.QPixmap:
            self._deviceLogo.setPixmap(image.scaled(*self._imageSize))
        elif type(image) == QtGui.QImage:
            self._deviceLogo.setPixmap(QtGui.QPixmap().fromImage(image).scaled(*self._imageSize))
        else:
            self._deviceLogo.setPixmap(taurus.qt.qtgui.resource.getThemePixmap("image-missing").scaled(50, 50))


def addDevice(Sardana=None, Pool=None):
    app = QtGui.QApplication([])
    QtCore.QResource.registerResource(get_resources())
    Pages = Enumeration('Pages', ('SelectSardanaPool', 'NewDevice', 'CommitPage', 'OutroPage'))
    w = wiz.SardanaBaseWizard()
    w.setWindowTitle("Add New Hardware Wizard")
    selectPool = SelectSardanaPoolBasePage(Sardana, Pool)
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

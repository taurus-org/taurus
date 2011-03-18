from PyQt4 import QtCore, QtGui, Qt
import sys
from types import *
import taurus.qt.qtgui.resource
from abc import abstractmethod
import copy

############## FAKE ######################################

class PropertyInfo(object):
    def __init__(self, name, type, format, default_value=None):
        self._name = name
        self._type = type
        self._format = format
        self._default_value=default_value
        
    def get_name(self):
        return self._name

    def get_type(self):
        return self._type
    
    def get_format(self):
        return self._format
    
    def get_default_value(self):
        return self._default_value

#######################################################



########################## BASIC INPUT WIDGETS #################

class InputWidget (object):
    
    @abstractmethod
    def setValue(self, value, undo=False):
        pass
    
    @abstractmethod       
    def getValue(self):
        return None
    
    @abstractmethod      
    def valueChanged(self):
        pass
    
    def deselectWidget(self):
        pass
    


class BooleanWidget(QtGui.QWidget, InputWidget):
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent)
        self._formLayout = QtGui.QHBoxLayout(self)
        self.trueButton = QtGui.QRadioButton(self)
        self._formLayout.addWidget(self.trueButton)
        self.falseButton = QtGui.QRadioButton(self)
        self._formLayout.addWidget(self.falseButton)
        self.trueButton.setText("True")
        self.falseButton.setText("False")
        QtCore.QObject.connect(self.trueButton, QtCore.SIGNAL("clicked()"), self.valueChanged)
        QtCore.QObject.connect(self.falseButton, QtCore.SIGNAL("clicked()"), self.valueChanged)
        self.setValue(self.getDefaultValue(), undo=False)

    def valueChanged(self):
        if not (self.trueButton.isChecked() == self._actualValue):
            self.emit(QtCore.SIGNAL("valueChanged"),self._actualValue,not self._actualValue)
        self._actualValue = self.trueButton.isChecked()
    
    def setValue(self, value, undo=False):
        if value is None:
            value = self.getDefaultValue()
        self.trueButton.setChecked(value)
        self.falseButton.setChecked(not value)
        self._actualValue = value
       
    def getValue(self):
        return self.trueButton.isChecked()
    
    @classmethod 
    def getDefaultValue(self):
        return True
    
    
class BooleanComboWidget(QtGui.QComboBox, InputWidget):
    
    def __init__(self, parent=None):
        QtGui.QComboBox.__init__(self,parent)
        self.addItems(["True","False"])
        self.setValue(self.getDefaultValue(), undo=False)

    def setValue(self, value, undo=False):
        if value is None:
            value = self.getDefaultValue()
            
        if value is True:
            self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(1)

    def getValue(self):
        return not self.currentIndex()
    
    def valueChanged(self):
        pass
    
    @classmethod 
    def getDefaultValue(self):
        return True
    
    
class IntegerWidget(QtGui.QLineEdit, InputWidget):
    
    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self,parent)
        self.setValidator(QtGui.QIntValidator(self))
        self.setValue(self.getDefaultValue(), undo=False)
        
    def setValue(self, value, undo=False):
        if value is None:
            value = self.getDefaultValue()
        self.setText(str(value))
        self._actualValue = value
       
    def getValue(self):
        try:
            return int(self.text())
        except:
            return self.getDefaultValue()
        
    def focusOutEvent (self, event): #QFocusEvent
        QtGui.QLineEdit.focusOutEvent(self,event)
        self.valueChanged()
                
    def valueChanged(self):
        if not (self.getValue() == self._actualValue):
            self.emit(QtCore.SIGNAL("valueChanged"),self._actualValue, self.getValue() )
        self._actualValue = self.getValue()
        self.setValue(self.getValue(), undo=False) # if value is not valid
    
    @classmethod    
    def getDefaultValue(self):
        return 0
    
    
    
class FloatWidget(QtGui.QLineEdit, InputWidget):
    
    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self,parent)
        self.setValidator(QtGui.QDoubleValidator(self))
        self.setValue(self.getDefaultValue(), undo=False)
        
    def setValue(self, value, undo=False):
        if (value is None):
            value = self.getDefaultValue()
        self.setText(str(value))
        self._actualValue = value
       
    def getValue(self):
        try:
             return float(self.text())
        except:
            return self.getDefaultValue()
    
    def focusOutEvent (self, event): #QFocusEvent
        QtGui.QLineEdit.focusOutEvent(self,event)
        self.valueChanged()
                
    def valueChanged(self):
        if not (self.getValue() == self._actualValue):
            self.emit(QtCore.SIGNAL("valueChanged"),self._actualValue, self.getValue() )
        self._actualValue = self.getValue()
        self.setValue(self.getValue(), undo=False) # if value is not valid
    
    @classmethod 
    def getDefaultValue(self):
        return 0.0


class StringWidget(QtGui.QLineEdit, InputWidget):
    
    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self,parent)
        self.setValue(self.getDefaultValue(), undo=False)
        
    def setValue(self, value, undo=False):
        if value is None:
            value = self.getDefaultValue()
        self.setText(str(value))
        self._actualValue = value
       
    def getValue(self):
        return str(self.text())
    
    def textChanged(self, string):
        QtGui.QLineEdit.textChanged(self, string)
       
    def focusOutEvent (self, event): #QFocusEvent
        QtGui.QLineEdit.focusOutEvent(self,event)
        self.valueChanged()
                
    def valueChanged(self):
        if not (self.getValue() == self._actualValue):
            self.emit(QtCore.SIGNAL("valueChanged"),self._actualValue, self.getValue() )
        self._actualValue = self.getValue()
        self.setValue(self.getValue(), undo=False) # if value is not valid
    
    @classmethod
    def getDefaultValue(self):
        return ""

############################## TABLE WIDGET ############################


class TableWidget (QtGui.QWidget):
    
    def __init__(self, value, format, type, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self._actualValue =self.getDefaultValue()
        self._layout = QtGui.QHBoxLayout(self)
        self.setLayout(self._layout)
        self._tableView = QtGui.QTableView()
        self._tableView.mousePressEvent = self.mousePressEvent
        self._tableView.setSelectionMode(QtGui.QTableView.SingleSelection)
        self._layout.addWidget(self._tableView)
        self._format = format
        self._type = type
        self._verticalLayout = QtGui.QVBoxLayout()
        self._addRowButton = QtGui.QPushButton(self)
        self._addRowButton.setIcon(taurus.qt.qtgui.resource.getThemeIcon("list-add"))
        self._addRowButton.setText("Add Row       ")
        self._verticalLayout.addWidget(self._addRowButton)
        self._removeRowButton = QtGui.QPushButton(self)
        self._removeRowButton.setIcon(taurus.qt.qtgui.resource.getThemeIcon("list-remove"))
        self._removeRowButton.setText("Remove Row    ")
        self._verticalLayout.addWidget(self._removeRowButton)
        self._addColumnButton = QtGui.QPushButton(self)
        self._addColumnButton.setIcon(taurus.qt.qtgui.resource.getThemeIcon("list-add"))
        self._addColumnButton.setText("Add Column")
        self._verticalLayout.addWidget(self._addColumnButton)
        self._removeColumnButton = QtGui.QPushButton(self)
        self._removeColumnButton.setIcon(taurus.qt.qtgui.resource.getThemeIcon("list-remove"))
        self._removeColumnButton.setText("Remove Column")
        self._verticalLayout.addWidget(self._removeColumnButton)
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
        QtCore.QObject.connect(self._addColumnButton, QtCore.SIGNAL("clicked()"), self._addColumn)
        QtCore.QObject.connect(self._removeRowButton, QtCore.SIGNAL("clicked()"), self._removeRow)
        QtCore.QObject.connect(self._removeColumnButton, QtCore.SIGNAL("clicked()"), self._removeColumn)
        QtCore.QObject.connect(self._upButton, QtCore.SIGNAL("clicked()"), self._moveUp)
        QtCore.QObject.connect(self._downButton, QtCore.SIGNAL("clicked()"), self._moveDown) 
        self._layout.addLayout(self._verticalLayout)
        
        if self._type == "boolean":
            self._delegate = BooleanTableDelegate(self._tableView)
        elif self._type == "integer":
            self._delegate = IntegerTableDelegate(self._tableView)
        elif self._type == "float":
            self._delegate = FloatTableDelegate(self._tableView)
        else:
            self._delegate = StringTableDelegate(self._tableView)
        
        QtCore.QObject.connect(self._delegate, QtCore.SIGNAL("editorValueChanged"), self._valueChanged)
        self._tableView.setItemDelegate(self._delegate)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        self._tableView.setSizePolicy(sizePolicy)
        self._tableView.horizontalHeader().setDefaultSectionSize(80)
        if self._format == "1D":
            self._tableView.horizontalHeader().setVisible(False)
            self._tableView.horizontalHeader().setStretchLastSection(True)
            self._tableView.setMinimumSize(QtCore.QSize(150, 150))
            self._addColumnButton.hide()
            self._removeColumnButton.hide()
        elif self._format == "2D":
            self._tableView.setMinimumSize(QtCore.QSize(150, 250))
            self._upButton.hide()
            self._downButton.hide()


    def mousePressEvent(self, event):
        if (event.button() == QtCore.Qt.LeftButton):
            index = self._tableView.indexAt(event.pos())
            if (index.isValid()):
                if index in self._tableView.selectedIndexes():
                    QtGui.QTableView.mousePressEvent(self._tableView, event)
                    self._tableView.clearSelection()
                else:
                    self.emit(Qt.SIGNAL("selected"))
                    QtGui.QTableView.mousePressEvent(self._tableView, event)
            else:
                self._tableView.clearSelection()
        else:
            QtGui.QTableView.mousePressEvent(self._tableView, event)
            
    def deselectWidget(self):
        self._tableView.clearSelection()
        
                
    def _addRow(self):
        value = self.getValue() # stored table
        defaultCellsValue = self._delegate.getDefaultValue() # default value for every new item in the table
        
        rows = len(value)
        if (self._format == "2D"):
            if (rows>0):
                columns = len(value[0])
            else:
                columns=1

        rowIndex = self._getSelectedIndex()[0]
        
        if rowIndex is None:
            rowIndex = rows
            
        if (self._format == "1D"):
            value.insert(rowIndex, defaultCellsValue)
          
        if (self._format == "2D"):
            row = []
            for i in range(columns):
                row.append(defaultCellsValue)
            value.insert(rowIndex, row)
        
        self.setValue(value, undo=True)

        
    def _getSelectedIndex(self):
        if len (self._tableView.selectedIndexes()):
            row = self._tableView.selectedIndexes()[0].row()
            column = self._tableView.selectedIndexes()[0].column()
        else:
            row = None
            column = None
        
        return [row,column]

    
    def _removeRow(self):
        rowIndex = self._getSelectedIndex()[0]
        if rowIndex is not None:
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Confirmation              ")
            msgBox.setStandardButtons(QtGui.QMessageBox().No | QtGui.QMessageBox().Yes )
            msgBox.setInformativeText("Remove row {%i} ?" % (rowIndex+1) )
            msgBox.setIcon(QtGui.QMessageBox.Question)
            ret = msgBox.exec_()
        if ret == QtGui.QMessageBox().Yes:
           value = self.getValue()
           self.setValue(value[:rowIndex] + value[rowIndex+1:], undo=True) 


    def _addColumn(self):
        value = self.getValue() # stored table
        defaultCellsValue = self._delegate.getDefaultValue() # default value for every new item in the table
        rows = len(value)
        
        if (rows>0):
            
            columns = len(value[0])
            columnIndex = self._getSelectedIndex()[1]
            if columnIndex is None:
                columnIndex = columns
            for row in value:
                row.insert(columnIndex, defaultCellsValue)
            self.setValue(value, undo=True)
        else:
            self._addRow() 

    
    def _removeColumn(self):
        value = self.getValue() # stored table
        rows = len(value)
        columnIndex = self._getSelectedIndex()[1]
        
        if columnIndex is not None:
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Confirmation                ")
            msgBox.setStandardButtons(QtGui.QMessageBox().No | QtGui.QMessageBox().Yes )
            msgBox.setInformativeText("Remove column {%i} ?" % (columnIndex+1) )
            msgBox.setIcon(QtGui.QMessageBox.Question)
            ret = msgBox.exec_()

        if (rows>0) and (columnIndex is not None) and (ret ==QtGui.QMessageBox().Yes):
            columns = len(value[0])
            if columns == 1:
                self.setValue([], undo=False)
            else:
                for i in range(len(value)):
                    value[i] =  value[i][:columnIndex] + value[i][columnIndex+1:]
                    
                self.setValue(value, undo=True)
                    
            
    def _moveUp(self):
        value = self.getValue() # stored table
        rows = len(value)
        rowIndex = self._getSelectedIndex()[0]
        
        if (rows>1) and (rowIndex is not None) and (rowIndex>0) :
            x = value.pop(rowIndex)
            value.insert(rowIndex-1,x)
            self.setValue(value, undo=True)
            self._tableView.setCurrentIndex(self._tableView.model().index(rowIndex-1, 0 ))

                    
    def _moveDown(self):
        value = self.getValue() # stored table
        rows = len(value)
        rowIndex = self._getSelectedIndex()[0]
        
        if (rows>1) and (rowIndex is not None) and (rowIndex<rows-1) :
            x = value.pop(rowIndex)
            value.insert(rowIndex+1,x)
            self.setValue(value, undo=True)
            self._tableView.setCurrentIndex(self._tableView.model().index(rowIndex+1, 0 ))
            
            
    def setValue(self, value, undo=False):
        if not self._actualValue == value:
            if undo:
                self.emit(QtCore.SIGNAL("valueChanged"),copy.deepcopy(self._actualValue), copy.deepcopy(value) )
            self._actualValue = copy.deepcopy(value)
        
        rows = len(value)
        if (self._format == "2D") and (rows>0):
            columns = len(value[0])
        else:
            columns = 1 
        
        self._model = QtGui.QStandardItemModel(rows, columns)
        for row in range(rows):
            for column in range(columns):
        
                index = self._model.index(row, column, QtCore.QModelIndex())
                if (self._format == "1D"):
                    self._model.setData(index, QtCore.QVariant(value[row]))
                if (self._format == "2D"):
                    self._model.setData(index, QtCore.QVariant(value[row][column]))
        self._tableView.setModel(self._model)
        
       
    def getValue(self):
        rows = self._model.rowCount()
        columns = self._model.columnCount()
        result = []
        for row in range(rows):
            records = []
            for column in range(columns):
                index =  self._model.index(row, column)
                if self._type == "integer":
                    val, bool = self._model.data(index).toInt()
                    records.append( val )
                elif self._type == "float":
                    val, bool =self._model.data(index).toDouble()
                    records.append(val )
                elif self._type == "boolean":
                    records.append( self._model.data(index).toBool() )
                else:
                    records.append( str(self._model.data(index).toString()) )
            
            if (self._format == "1D"):
                result.append(records[0])
            if (self._format == "2D"):
                result.append(records)
        
        return copy.deepcopy(result)
    
    
    def _valueChanged(self, value, row, column):
        if (self._format == "1D"):
            if not (value == self._actualValue[row]):
                self._actualValue[row] = value
                self.emit(QtCore.SIGNAL("valueChanged"),self.getValue()[:], self._actualValue[:] )
                
                
        if (self._format == "2D"):
            if not (value == self._actualValue[row][column]):
                self._actualValue[row][column] = value
                self.emit(QtCore.SIGNAL("valueChanged"),self.getValue()[:], self._actualValue[:] )
    
                
    @classmethod
    def getDefaultValue(self):
        return []

########### DELGATES ##################

class TableDelegate(QtGui.QItemDelegate):

    def __init__(self, parent = None):
        QtGui.QItemDelegate.__init__(self, parent)
        
    @abstractmethod
    def createEditor(self, parent, option, index):
        return None
    
    @abstractmethod
    def setEditorData( self, editor, index ):
        pass
    
    @abstractmethod
    def getDefaultValue(self):
        return None

    def setModelData(self, editor, model, index):
        self.emit(QtCore.SIGNAL("editorValueChanged"),editor.getValue(),index.row(),index.column())
        value = editor.getValue()
        model.setData( index
                , QtCore.QVariant( value ) )

    def updateEditorGeometry( self, editor, option, index ):
        editor.setGeometry(option.rect)
        

class BooleanTableDelegate(TableDelegate):
    
    def createEditor(self, parent, option, index):
        editor = BooleanComboWidget( parent )
        Qt.QObject.connect(editor, Qt.SIGNAL("currentIndexChanged(int)"), self.updateValue)
        editor.installEventFilter(self)
        return editor
    
    def updateValue(self, int):
        self.emit(QtCore.SIGNAL("closeEditor()") )
    
    def setEditorData( self, editor, index ):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setValue(value.toBool(), undo=True)
        
    def getDefaultValue(self):
        return BooleanComboWidget.getDefaultValue()
    
class IntegerTableDelegate(TableDelegate):
    
    def createEditor(self, parent, option, index):
        editor = IntegerWidget( parent )
        editor.installEventFilter(self)
        return editor
    
    def setEditorData( self, editor, index ):
        value, ok = index.model().data(index, QtCore.Qt.DisplayRole).toInt()
        editor.setValue(value, undo=True)

    def getDefaultValue(self):
        return IntegerWidget.getDefaultValue()
    
class FloatTableDelegate(TableDelegate):
    
    def createEditor(self, parent, option, index):
        editor = FloatWidget( parent )
        editor.installEventFilter(self)
        return editor
    
    def setEditorData( self, editor, index ):
        value,ok = index.model().data(index, QtCore.Qt.DisplayRole).toDouble()
        editor.setValue(value, undo=True)

    def getDefaultValue(self):
        return FloatWidget.getDefaultValue()
    
class StringTableDelegate(TableDelegate):
    
    def createEditor(self, parent, option, index):
        editor = StringWidget( parent )
        editor.installEventFilter(self)
        return editor
    
    def setEditorData( self, editor, index ):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setValue(value.toString(), undo=True)
    
    def getDefaultValue(self):
        return StringWidget.getDefaultValue()   


################## MAIN CLASS ####################   
class Save (object):
    def __init__ (self, object = None,prevValue = None, nextValue = None):
        self._object = object
        self._prevValue = prevValue
        self._nextValue = nextValue
        
    def getObject(self):
        return self._object
    
    def getPrevValue(self):    
        return self._prevValue
    
    def getNextValue(self):
        return self._nextValue    


class SettingsWidget(QtGui.QWidget):
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self,parent)
        self._formLayout = QtGui.QGridLayout(self)
        self.setUndoHistoryStack(20)
        self._inputWidgts=[]
        self._edited = False
        self._properties = None
        
    def clearLayout(self, layout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            if not item:
                continue
            w = item.widget()
            if w:
                w.deleteLater()    
        
    def _valueChanged(self,value1,value2):
        self._edited = True
        self._undoHistoryStack.append( Save( self.sender(), copy.deepcopy(value1), copy.deepcopy(value2) )   )
        if len(self._undoHistoryStack)> self._historySize:
            self._undoHistoryStack.pop(0)
        item , position  =self._historyStackPointer
        if len(self._undoHistoryStack)-1 >=0:
            for i in range (item+1, len(self._undoHistoryStack)-1):
                self._undoHistoryStack.pop(item+1)
        self._historyStackPointer = ( len(self._undoHistoryStack)-1 , 1 )
        
        self.emit(Qt.SIGNAL("propertyValueChanged()"))
        
    def setUndoHistoryStack(self, size):
        self._undoHistoryStack = []
        self._historySize = size
        self._historyStackPointer = (-1,1) # item, position
        
    def undo(self):
        item , position  =self._historyStackPointer
        if position ==1:
            item = item
            position = 0
        else:
            if item > 0:
                item = item -1
                position =0
        
        self._historyStackPointer = (item,position)
        if (item >=0) and(item < len(self._undoHistoryStack)):
            self._undoHistoryStack[item].getObject().setValue(self._undoHistoryStack[item].getPrevValue(), undo=False)
        
    def redo(self):    
        item , position  =self._historyStackPointer
        if position ==0:
            item = item
            position = 1
        else:
            if item < len(self._undoHistoryStack)-1:
                item = item +1
                position =1
                
        self._historyStackPointer = (item,position)
        
        if (item >=0) and(item < len(self._undoHistoryStack)):
            self._undoHistoryStack[item].getObject().setValue(self._undoHistoryStack[item].getNextValue(), undo=False)

#    def keyPressEvent(self, event):
#        QtGui.QWidget.keyPressEvent(self, event)
#        undo = (event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Z)
#        redo = (event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Y)
#        if (undo):
#            self.undo()
#        if (redo):
#            self.redo()

    def setEdited(self, value):
        self._edited=value 

    def isEdited(self):
        return self._edited        
           
    def deselect(self):
        for widget in self._inputWidgts:
            if widget != self.sender():
                widget.deselectWidget()
                         
    def getProperties(self):
        values=[]
        name = "noName"
        properties = self._properties
        if len(self._inputWidgts)>=1:
            for inputWidget in self._inputWidgts:
                 values.append(inputWidget.getValue())
            name = values.pop(0)
            
        return (properties, name, values)
        
    def _nameChanged(self):
        self.emit(Qt.SIGNAL("propertyValueChanged()"))
            
    def setProperties(self, properties):
        
        # clean memory
        for item in self._inputWidgts:
            QtCore.QObject.disconnect(item, QtCore.SIGNAL("valueChanged"), self._valueChanged)
        self._inputWidgts=[]
        self.clearLayout(self._formLayout)
        self.setUndoHistoryStack(self._historySize)
        self._edited = False

        # create new set of properties
        
        self._properties = properties
        
        if properties is not None:
            self._inputWidgts = []
            i=0
            for property in properties:
                self._nameLabel = QtGui.QLabel(property.get_name())
                #self._formLayout.setWidget(i, QtGui.QFormLayout.LabelRole, self._nameLabel)
                self._formLayout.addWidget(self._nameLabel,i,0)
                
                if property.get_format() == "0D":
                    if property.get_type() == "boolean":
                        self._inputWidgts.append( BooleanWidget() )
                    elif property.get_type() == "integer":
                        self._inputWidgts.append( IntegerWidget() )
                    elif property.get_type() == "float":
                        self._inputWidgts.append( FloatWidget() )
                    else:
                        self._inputWidgts.append( StringWidget() )
                        
                    spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
                    self._formLayout.addWidget(self._inputWidgts[i], i,1)
                    self._formLayout.addItem(spacerItem,i,2)
                            
                elif (property.get_format() == "1D") or (property.get_format() == "2D"):
                    self._inputWidgts.append(  TableWidget(property.get_default_value(), property.get_format() ,property.get_type()  ) )
                    self._formLayout.addWidget(self._inputWidgts[i], i,1,1,10)
                    Qt.QObject.connect(self._inputWidgts[i], Qt.SIGNAL("selected"), self.deselect)
                    
                self._inputWidgts[i].setValue(property.get_default_value())
                QtCore.QObject.connect(self._inputWidgts[i], QtCore.SIGNAL("valueChanged"), self._valueChanged)
                i=i+1
            
        QtCore.QObject.connect(self._inputWidgts[0], QtCore.SIGNAL("textChanged(QString)"), self._nameChanged)
                    
                
        
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    properties = []
    properties.append(PropertyInfo("name", "string", "0D", "deviceName"))
    properties.append(PropertyInfo("number0", "integer", "0D", 5))
    properties.append(PropertyInfo("boollll0", "boolean", "0D", False))    
    properties.append(PropertyInfo("number1", "float", "0D", 3.5))
    properties.append(PropertyInfo("string2", "string", "0D", "hehe"))
    properties.append(PropertyInfo("table0", "integer", "1D", [1,2,3]))
    properties.append(PropertyInfo("tablestringD1", "float", "1D", [1.5]))
    properties.append(PropertyInfo("tablestringD1", "string", "1D", ["aaaa","bbb","ccc"]))
    properties.append(PropertyInfo("tablefloatD1", "float", "1D", [1.0,2.5,3.6]))
    properties.append(PropertyInfo("tablebooleanD1", "boolean", "1D", [True,False,True]))
    properties.append(PropertyInfo("tableboointD1", "integer", "1D", [1,2,3]))
    properties.append(PropertyInfo("tablestringD2", "string", "2D",[ ["aaaa","bbb","ccc"],["aaaa2","bbb2","ccc2"],["aaaa3","bbb3","ccc3"] ]))
    
    
    nds=SettingsWidget()
    nds.setProperties(properties)
    nds.show()
    sys.exit(app.exec_())
    
    
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

__all__ = ["TaurusValuesTable"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt
import numpy

import sys

import taurus.core
from taurus.core.taurusbasetypes import DataFormat
from taurus.qt.qtgui.base import TaurusBaseWidget, TaurusBaseWritableWidget
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.resource import getThemeIcon, getThemePixmap
from taurus.qt.qtgui.container import TaurusWidget
from taurus.core.util.enumeration import Enumeration

TableRWState = Enumeration("TableRWState", ("Read", "Write"))

class TaurusValuesIOTableModel(Qt.QAbstractTableModel):
    typeCastingMap = {'f':float, 'b':bool, 'u':int, 'i':int, 'S':str, 'U':unicode}
    # Need to have an array
    def __init__(self, size, parent=None):
        Qt.QAbstractTableModel.__init__(self, parent)
        self._rtabledata = []
        self._wtabledata = []
        self._rowCount = size [0]
        self._columnCount = size[1]
        self._modifiedDict = {}
        self._attr = None
        self._attrConfig = None
        self.editedIndex = None
        self._editable = False
        self._writeMode = False
        
    def isDirty(self):
        '''returns True if there are user changes. False Otherwise'''
        return bool(self._modifiedDict)
        
    #To be implemented ----- 
    def rowCount(self, index = Qt.QModelIndex()):
        '''see :meth:`Qt.QAbstractTableModel.rowCount`'''
        if self._rowCount == 0:
            self._rowCount = 1
        return self._rowCount
    
    def columnCount(self, index = Qt.QModelIndex()):
        '''see :meth:`Qt.QAbstractTableModel.columnCount`'''
        if self._columnCount == 0:
            self._columnCount = 1
        return self._columnCount
    
    def data(self, index, role = Qt.Qt.DisplayRole):
        '''see :meth:`Qt.QAbstractTableModel.data`'''
        if self._writeMode == False:
            tabledata = self._rtabledata
        else:
            tabledata = self._wtabledata
        if not index.isValid() or not (0 <=index.row() < len(tabledata)):
            return Qt.QVariant()
        elif role == Qt.Qt.DisplayRole:
            value = None
            rc = (index.row(), index.column())
            if self._writeMode and rc in self._modifiedDict:
                return self._modifiedDict[rc]
            else:
                value = tabledata[rc]
            #cast the value to a standard python type
            value = self.typeCastingMap[tabledata.dtype.kind](value)
            return Qt.QVariant(value)
        elif role == Qt.Qt.DecorationRole:
            status = self.getStatus(index)
            if (self._modifiedDict.has_key((index.row(), index.column()))) and (self._writeMode):
                float_data = Qt.from_qvariant(self._modifiedDict[(index.row(), index.column())], float)
                if self.inAlarmRange(float_data):
                    icon = getThemeIcon('document-save')
                    #return Qt.QVariant(Qt.QColor('blue'))
                else:
                    icon = getThemeIcon('emblem-important')
                    #return Qt.QVariant(Qt.QColor('orange'))
                return Qt.QVariant(icon)
        elif role == Qt.Qt.EditRole:
            value = None
            if self._modifiedDict.has_key((index.row(), index.column())) and (self._writeMode):
                value = self._modifiedDict[(index.row(), index.column())]
            else:
                value = tabledata[index.row(),index.column()]
                if tabledata.dtype == bool:
                    value = bool(value)
            return Qt.QVariant(value)
        elif role == Qt.Qt.BackgroundRole:
            if self._writeMode:
                return Qt.QVariant(Qt.QColor(22,223,21,50))
            else:
                return Qt.QVariant(Qt.QColor('white'))
        elif role == Qt.Qt.ForegroundRole:
            if self._modifiedDict.has_key((index.row(), index.column())) and (self._writeMode):
                float_data = Qt.from_qvariant(self._modifiedDict[(index.row(), index.column())], float)
                if self.inAlarmRange(float_data):
                    return Qt.QVariant(Qt.QColor('blue'))
                else:
                    return Qt.QVariant(Qt.QColor('orange'))
            return Qt.QVariant(Qt.QColor('black'))
        elif role == Qt.Qt.FontRole:
            if self._modifiedDict.has_key((index.row(), index.column())) and (self._writeMode):
                return Qt.QVariant(Qt.QFont("Arial", 10, Qt.QFont.Bold))
        elif role == Qt.Qt.ToolTipRole:
            if self._modifiedDict.has_key((index.row(), index.column())) and (self._writeMode):
                float_data = Qt.from_qvariant(self._modifiedDict[index.row(), index.column()], float)
                return Qt.QVariant('Original value: %d.\nNew value that will be saved: %d' 
                                   %(tabledata[index.row(), index.column()], float_data))
        return Qt.QVariant()
    
    def setAttr(self, attr):
        '''
        Updated the internal table data from an attribute value
        
        :param attr: (DeviceAttribute)
        '''
        self._attr = attr
        values = numpy.array(attr.value)
        wvalues = numpy.array(attr.w_value)
        #reshape the table
        if attr.data_format == DataFormat._1D:
            rows, columns = values.size, 1
        elif attr.data_format == DataFormat._2D:
            rows, columns = values.shape
        else:
            raise TypeError('Unsupported data format "%s"'%repr(attr.data_format))
        
        if (self._rowCount != rows) or (self._columnCount != columns):
            self.reset()
        
        self._rowCount = rows
        self._columnCount = columns
        values = values.reshape(rows,columns) #make sure it is in matrix form (not a vector)
        self._rtabledata = values            
        self.emit(Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"),self.createIndex(0,0), self.createIndex(rows-1,columns-1))
    
    def setConfig(self, config):
        '''
        Handles configuration events
        
        :param attr: (TaurusConfiguration)
        '''
        self._attrConfig = config
        self._editable = config.isWritable()
        
    def getConfig(self):
        '''
        Returns the configuration object for the data
        
        :returns:  (taurus.core.taurusconfiguration.TaurusConfiguration)
        '''
        return self._attrConfig
    
    def getStatus(self, index):
        '''
        Returns Status of the variable
        
        :returns:  (taurus.core.taurusbasetypes.AttrQuality) 
        '''
        return self._attr.quality
    
    def getType(self):
        '''
        Returns the table data type.
        
        :returns:  (numpy.dtype)
        '''
        return self._rtabledata.dtype
    
    def addValue(self, index, value):
        '''adds a value to the dictionary of modified cell values
        
        :param index: (QModelIndex) table index
        :param value: (object)
        '''
        self._modifiedDict[(index.row(), index.column())] = value
        
    def removeValue(self, index):
        '''
        Removes index from dictionary
           
        :param index:  (QModelIndex) table index
        '''
        if self._modifiedDict.has_key((index.row(), index.column())):
            self._modifiedDict.pop((index.row(), index.column()))
    
    def flags(self, index):
        '''see :meth:`Qt.QAbstractTableModel`'''
        if not index.isValid():
            return Qt.Qt.ItemIsEnabled
        if self._editable:
            return Qt.Qt.ItemFlags(Qt.Qt.ItemIsEnabled | Qt.Qt.ItemIsEditable | Qt.Qt.ItemIsSelectable)
        else:
            return Qt.Qt.ItemFlags(Qt.Qt.ItemIsEnabled | Qt.Qt.ItemIsSelectable)
    
    def getModifiedWriteData(self):        
        '''
        returns an array for the write data that includes the user modifications
        
        :return: (numpy.array) The write values including user modifications.
        '''
        table = self._wtabledata
        kind = table.dtype.kind
        if kind in 'SU':
            table = table.tolist() #we want to allow the strings to be larger than the original ones
            for (r,c),v in self._modifiedDict.items():
                table[r][c] = Qt.from_qvariant(v, str)
            table = numpy.array(table)
        else:        
            for k,v in self._modifiedDict.items():
                if kind == 'f':
                    table[k] = Qt.from_qvariant(v, float)
                elif kind in 'iu':
                    table[k] = Qt.from_qvariant(v, int)
                elif kind == 'b':
                    table[k] = Qt.from_qvariant(v, bool)
                else:
                    raise TypeError('Unknown data type "%s"'%kind)
        #reshape if needed
        if self._attr.data_format == DataFormat._1D:
            table = table.flatten()
        return table    
     
    def clearChanges(self):
        '''clears the dictionary of changed values'''
        self._modifiedDict.clear()
        self.emit(Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"),self.createIndex(0,0), self.createIndex(self.rowCount()-1,self.columnCount()-1))

    def inAlarmRange(self, value):
        '''
        Checkes if value is in alarm range.
           
        :param value:  (float/int) user entered value
        :returns:  (bool) True if value in alarm range, False if valid
            
        '''
        try:
            if float(self._attrConfig.getMinAlarm()) <= value <= float(self._attrConfig.getMaxAlarm()):
                return True
            else:
                return False
        except:
            return True
    
    def inRange(self, value):
        '''
        Checks if value is in range.
           
        :param value:  (float/int) user entered value
        :returns:  (bool) True if value in range, False if valid
            
        '''
        try:
            if float(self._attrConfig.getMinValue()) <= value <= float(self._attrConfig.getMaxValue()):
                return True
            else:
                return False
        except:
            return True
        
    def setWriteMode(self, isWrite):
        '''Changes the write state
        
        :param isWrite: (bool)
        '''
        self._writeMode = isWrite
        if isWrite and not self.isDirty():
            #refresh the write data (unless it is dirty)
            wvalues=numpy.array(self._attr.w_value)
            #reshape the table
            if self._attr.data_format == DataFormat._1D:
                rows, columns = wvalues.size, 1
            elif self._attr.data_format == DataFormat._2D:
                rows, columns = wvalues.shape
            else:
                self.warning('unsupported data format %s'%str(val.data_format))
            wvalues = wvalues.reshape(rows,columns)
            #In version 4.6 of Qt when whole table is updated it is recommended to use beginReset()
            self._wtabledata = wvalues
        self.emit(Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"),self.createIndex(0,0), self.createIndex(self.rowCount()-1,self.columnCount()-1))
    
    def getModifiedDict(self):
        '''
        Returns dictionary.

        :returns:  (dictionary) dictionary containing modified indexes and values
        '''
        return self._modifiedDict
    
    def getReadValue(self, index):
        '''
        Returns read value for a given index.
           
        :param index:  (QModelIndex) table model index
        :returns:  (string/int/float/bool) read table value for a given cell
        '''
        return self._rtabledata[index.row(), index.column()]


class TaurusValuesIOTable(Qt.QTableView):
    def __init__(self, parent = None):
        name = self.__class__.__name__
        Qt.QTableView.__init__(self, parent)
        self._showQuality = True
        self._attr = None
        self._value = None
        self.setSelectionMode(Qt.QAbstractItemView.SingleSelection)
        self.horizontalHeader().setResizeMode(Qt.QHeaderView.Stretch)
        itemDelegate = TaurusValuesIOTableDelegate(self)
        self.setItemDelegate(itemDelegate)
        #self.setStyleSheet('TaurusValuesIOTable { selection-background-color: violet;} ')

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
        
    def setModel(self,shape):
        '''
        Creates an instance of QTableModel and sets a QT model.
           
        :param shape:  (tuple<int>) shape of the model table to be set
            
        '''
        qmodel = TaurusValuesIOTableModel(shape, parent=self)
        Qt.QTableView.setModel(self, qmodel)
        
    def cancelChanges(self):        
        '''
        Cancels all table modifications.
        '''
        self.model().clearChanges()
        
    def removeChange(self):        
        '''
        If the cell was modified it restores the original write value.
        '''
        self.model().removeValue(self.selectedIndexes()[0])
    
    def showHelp(self):
        '''
        Shows QMessageBox help window. It contains explanations of used icons.
        '''
        buttonBox = Qt.QMessageBox(self)
        buttonBox.setLayout(Qt.QGridLayout(self))
        icon = getThemePixmap('document-save')
        l = Qt.QLabel()
        l.setPixmap(icon)
        buttonBox.layout().addWidget(l,0,0)
        buttonBox.layout().addWidget(Qt.QLabel('- value is valid and will be saved if changes will be accepted'),0,1)
        icon = getThemePixmap('dialog-warning')
        l = Qt.QLabel()
        l.setPixmap(icon)
        buttonBox.layout().addWidget(l,1,0)
        buttonBox.layout().addWidget(Qt.QLabel('- value is in alarm range and will be saved if changes will be accepted'),1,1)
        buttonBox.exec_()
    

class TaurusValuesIOTableDelegate(Qt.QStyledItemDelegate):

    def __init__(self, parent = None):
        Qt.QStyledItemDelegate.__init__(self, parent)
        self._initialText = ""
    
    def createEditor(self,parent,option,index):
        '''
        Creates a custom editor for a table delagate.
        
        see :meth:`Qt.QStyledItemDelegate.createEditor`
        '''
        if index.model().getType() == bool:
            #editor = Qt.QStyledItemDelegate.createEditor(self,parent,option,index)
            editor = Qt.QComboBox(parent)
        else:
            editor = TableInlineEdit(parent)
            editor._updateValidator(index.model().getConfig(), index.model().getType())
        self.emit(Qt.SIGNAL('editorCreated'))
        return editor
    
    def setEditorData(self, editor, index):
        '''
        see :meth:`Qt.QStyledItemDelegate.setEditorData`
        '''
        if index.model().editedIndex == (index.row(), index.column()):
            return
        index.model().editedIndex = (index.row(), index.column())
        self._initialText = None
        if index.model().getType() == bool:
            editor.addItems(['true', 'false'])
            a = str(Qt.from_qvariant(index.data(), bool)).lower()
            self._initialText = a
            editor.setCurrentIndex(editor.findText(a))
        else:
            data = index.model().data(index, Qt.Qt.EditRole)
            self._initialText = Qt.from_qvariant(data, str)
            editor.setText(self._initialText)
    
    def setModelData(self, editor, model,index):
        '''
        see :meth:`Qt.QStyledItemDelegate.setModelData`
        '''
        #if editor text changed, then don't mark as updated.
        try:
            if not model.inRange(float(editor.text())):
                return
        except:
            pass
        if index.model().getType() == bool:
            text = editor.currentText()
        else:
            text = editor.text()
            
        if(text != self._initialText) & (text != ""):
            model.addValue(index, Qt.QVariant(text))
            self.parent().resizeColumnsToContents()
        index.model().editedIndex = None
                    
                    
class TableInlineEdit(Qt.QLineEdit):
    '''
    TableInLineEdit is used to validate the content of the new value, also to paint the text: blue - valid, orange - in alarm, grey - invalid.
    '''
    def __init__(self, parent = None):
        super(Qt.QLineEdit, self).__init__(parent)
        self.connect(self, Qt.SIGNAL('textEdited(const QString &)'), self.textEdited)
        self.connect(self, Qt.SIGNAL('focusLost(const QString &)'), self.textEdited)
        self._attrConfig = None
        self.__minAlarm = -float("inf")
        self.__maxAlarm = float("inf")
        self.__minLimit = -float("inf")
        self.__maxLimit = float("inf")
        self.setValidator(None)

    def textEdited (self):
        '''
        Paints the text while typing.
        
        see :meth:`Qt.QLineEdit.textEdited`
        '''
        color, weight = 'gray', 'normal' #default case: the value is in normal range with no pending changes
        try:
            v = float(self.displayText())
        except:
            v = 0.0
        try:
            if float(self._attrConfig.getMinAlarm()) <= v <= float(self._attrConfig.getMaxAlarm()): #the value is invalid and can't be applied
                color = 'blue'
            elif float(self._attrConfig.getMinValue()) <= v <= float(self._attrConfig.getMaxValue()): #the value is valid but in alarm range...
                color = 'orange'
        except:
            color = 'orange'

        weight = 'bold'
        self.setStyleSheet('TableInlineEdit {color: %s; font-weight: %s}'%(color,weight))

    
    def _updateValidator(self, attrinfo, datatype):
        '''This method sets a validator depending on the data type
        
        :param attrinfo: (AttributeInfoEx)
        :datatype: (numpy.dtype) type of the data being edited
        '''
        self._attrConfig = attrinfo
        if numpy.issubdtype(datatype, int):
            validator = Qt.QIntValidator(self) #initial range is -2147483648 to 2147483647 (and cannot be set larger)
            if validator.bottom() < self.__minLimit < validator.top(): 
                validator.setBottom(int(self.__minLimit))
            if validator.bottom() < self.__maxLimit < validator.top():
                validator.setTop(int(self.__maxLimit))
            self.setValidator(validator)
        elif numpy.issubdtype(datatype, float):
            validator= Qt.QDoubleValidator(self)
            validator.setBottom(self.__minLimit)
            validator.setTop(self.__maxLimit)
            self.setValidator(validator)
        else: 
            self.setValidator(None)
    
    def __decimalDigits(self, fmt):
        '''returns the number of decimal digits from a format string
        (or None if they are not defined)''' 
        try:
            if fmt[-1].lower() in ['f','g'] and '.' in fmt:
                return int(fmt[:-1].split('.')[-1])
            else:
                return None
        except:
            return None
    
    
class TaurusValuesTable(TaurusWidget):
    '''
    A table for displaying and/or editing 1D/2D Taurus attributes 
    '''
    _showQuality = False
    _writeMode = False
    
    def __init__(self, parent = None, designMode = False, defaultWriteMode=None):
        TaurusWidget.__init__(self, parent = parent, designMode = designMode)
        self._tableView = TaurusValuesIOTable()
        l = Qt.QGridLayout()
        l.addWidget(self._tableView,1,0)
        self.connect(self._tableView.itemDelegate(), Qt.SIGNAL("editorCreated"), self._onEditorCreated)
        
        if defaultWriteMode is None:
            self.defaultWriteMode = self._writeMode
        else:
            self.defaultWriteMode = defaultWriteMode
        
        self._label = TaurusLabel()
        self._label.setBgRole('quality')
        self._label.setFgRole('quality')
        
        self._applyBT = Qt.QPushButton('Apply')
        self._cancelBT = Qt.QPushButton('Cancel')
        self.connect(self._applyBT,Qt.SIGNAL("clicked()"),self.okClicked)
        self.connect(self._cancelBT,Qt.SIGNAL("clicked()"),self.cancelClicked)
        
        self._rwModeCB = Qt.QCheckBox()
        self._rwModeCB.setText('Write mode')
        self.connect(self._rwModeCB, Qt.SIGNAL("toggled(bool)"),self.setWriteMode)
        
        l.addWidget(self._label,2,0)
        l.addWidget(self._rwModeCB,0,0)
        lv = Qt.QHBoxLayout()
        lv.addWidget(self._applyBT)
        lv.addWidget(self._cancelBT)
        l.addLayout(lv,3,0)
        self.setLayout(l)
        self._initActions()
        
    def _initActions(self):
        """Initializes the actions for this widget (currently, the pause action.)
        """
        self._pauseAction = Qt.QAction("&Pause", self)
        self._pauseAction.setShortcuts([Qt.Qt.Key_P,Qt.Qt.Key_Pause])
        self._pauseAction.setCheckable(True)
        self._pauseAction.setChecked(False)
        self.addAction(self._pauseAction)
        self.connect(self._pauseAction, Qt.SIGNAL("toggled(bool)"), self.setPaused)
        self.chooseModelAction = Qt.QAction("Choose &Model", self)
        self.chooseModelAction.setEnabled(self.isModifiableByUser())
        self.addAction(self.chooseModelAction)
        self.connect(self.chooseModelAction, Qt.SIGNAL("triggered()"), self.chooseModel)
    
    def getModelClass(self):
        '''see :meth:`TaurusWidget.getModelClass`'''
        return taurus.core.taurusattribute.TaurusAttribute    
    
    def setModel(self, model):
        '''Reimplemented from :meth:`TaurusWidget.setModel`'''
        TaurusWidget.setModel(self, model)
        value = self.getModelValueObj()
        if value is not None:
            try: 
                dim_x,dim_y = value.dim_x, value.dim_y #@this is tango-centric. dim_x and dim_y attribute is not present in TaurusConfiguration
            except:
                v = numpy.array(value.value)
                if v.ndim == 1:
                    dim_x, dim_y = v.shape[0], 1
                elif v.ndim == 2:
                    dim_x,dim_y = v.shape
                else:
                    self.error('Cannot display %i-dimensional data', v.ndim)
                    return
            self._tableView.setModel([dim_x, dim_y]) 
        self._label.setModel(model)

    def handleEvent(self, evt_src, evt_type, evt_value):
        '''see :meth:`TaurusWidget.handleEvent`'''
        #@fixme: in some situations, we may miss some config event because of the qmodel not being set. The whole handleEvent Method and setModel method should be re-thought
        model = self._tableView.model()
        if model is None:
            return
        if evt_type in (taurus.core.taurusbasetypes.TaurusEventType.Change, taurus.core.taurusbasetypes.TaurusEventType.Periodic) and evt_value is not None:            
            model.setAttr(evt_value)
            self._tableView.resizeColumnsToContents()
        elif evt_type == taurus.core.taurusbasetypes.TaurusEventType.Config:
            #force a read to set an attr
            model.setAttr(self.getModelValueObj())
            model.setConfig(evt_src)
            writable = bool(evt_value.writable)
            self.resetWriteMode()
            self._rwModeCB.setVisible(writable)
    
    def contextMenuEvent(self, event):
        '''Reimplemented from :meth:`QWidget.contextMenuEvent`'''
        menu = Qt.QMenu()
        globalPos = event.globalPos()
        menu.addAction(self.chooseModelAction)        
        menu.addAction(self._pauseAction)
        if self._writeMode:
            index = self._tableView.selectedIndexes()[0]
            if index.isValid():
                val = self._tableView.model().getReadValue(index)
                if self._tableView.model().getModifiedDict().has_key((index.row(), index.column())):
                    menu.addAction(getThemeIcon('edit-undo'),"Reset to original value (%s) "%repr(val), self._tableView.removeChange)
                    menu.addSeparator()
                menu.addAction(getThemeIcon('process-stop'), "Reset all table", self.askCancel)
                menu.addSeparator()
                menu.addAction(getThemeIcon('help-browser') ,"Help", self._tableView.showHelp)
        menu.exec_(globalPos)
        event.accept()       
    
    def applyChanges(self):        
        '''
        Writes table modifications to the device server.
        '''
        tab = self._tableView.model().getModifiedWriteData()
        attr = self.getModelObj()
        #attr.write(tab)
        attr.write(tab.tolist()) #@fixme If I don't convert this to a list it segfaults when writing arrays of strings 
        self._tableView.model().clearChanges()
    
        
    def okClicked(self):
        """This is a SLOT that is being triggered when ACCEPT button is clicked.
        
        .. note:: This SLOT is called, when user wants to apply table modifications. 
                  When no cell was modified it will not be called. When
                  modifications have been done, they will be writen to w_value
                  of an attribute.
        """
        if self._tableView.model().isDirty():
            self.applyChanges()
            self.resetWriteMode()
        
    def cancelClicked(self):
        """This is a SLOT that is being triggered when CANCEL button is clicked.
        
        .. note:: This SLOT is called, when user does not want to apply table 
                  modifications. When no cell was modified it will not be called.
        """
        if self._tableView.model().isDirty():
            self.askCancel()
    
    def askCancel(self):        
        '''
        Shows a QMessageBox, asking if user wants to cancel all changes. Triggered when user clicks Cancel button.
        '''
        result = Qt.QMessageBox.warning(self,'Your changes will be lost!', 
                                        'Do you want to cancel changes done to the whole table?',
                                         Qt.QMessageBox.Ok | Qt.QMessageBox.Cancel)
        if result == Qt.QMessageBox.Ok:
            self._tableView.cancelChanges()
            self.resetWriteMode()
    
    def _onEditorCreated(self):
        '''slot called when an editor has been created'''
        self.setWriteMode(True)
    
    def getWriteMode(self):
        '''whether the widget is showing the read or write values
        
        :return: (bool)'''
        return self._writeMode
        
    def setWriteMode(self, isWrite):
        '''
        Triggered when the read mode is changed to write mode. 
        
        :param isWrite: (bool)
        '''
        if isWrite == self._writeMode: return
        self._writeMode = isWrite
        
        if isWrite:
            valueObj = self.getModelValueObj()
            w_value = valueObj.w_value
            value = valueObj.value
            if numpy.array(w_value).shape != numpy.array(value).shape:
                ta = self.getModelObj()
                v = ta.read()
                ta.write(v.value) #@fixme: this is ugly! we should not be writing into the attribute without asking first...
                
        self._tableView.model().setWriteMode(isWrite)
        self._label.setVisible(isWrite)
        self._applyBT.setVisible(isWrite)
        self._cancelBT.setVisible(isWrite)
        self._rwModeCB.setChecked(isWrite)
    
    def resetWriteMode(self):
        '''equivalent to self.setWriteMode(self.defaultWriteMode)'''       
        self.setWriteMode(self.defaultWriteMode)
        
    @classmethod
    def getQtDesignerPluginInfo(cls):
        '''Reimplemented from :meth:`TaurusWidget.getQtDesignerPluginInfo`'''
        ret = TaurusWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.table'
        ret['group'] = 'Taurus Views'
        ret['icon'] = ":/designer/table.png"
        return ret
    
    def chooseModel(self):
        '''shows a model chooser'''
        from taurus.qt.qtgui.panel import  TaurusModelChooser
        selectables=[taurus.core.taurusbasetypes.TaurusElementType.Attribute]
        models, ok = TaurusModelChooser.modelChooserDlg(selectables=selectables, singleModel=True)
        if ok and len(models)==1:
            self.setModel(models[0])
            
    def setModifiableByUser(self, modifiable):
        '''Reimplemented from :meth:`TaurusWidget.setModifiableByUser`'''
        self.chooseModelAction.setEnabled(modifiable)
        TaurusWidget.setModifiableByUser(self, modifiable)
        
    def isReadOnly(self):
        '''Reimplemented from :meth:`TaurusWidget.isReadOnly`'''
        return False
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT property definition
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = Qt.pyqtProperty("QString", TaurusWidget.getModel, 
                                    setModel, 
                                    TaurusWidget.resetModel)
    writeMode = Qt.pyqtProperty("bool", getWriteMode, setWriteMode, resetWriteMode)
    

def taurusTableMain():
    '''A launcher for TaurusValuesTable.'''

    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.core.util import argparse
    import sys, os
    
    parser = argparse.get_taurus_parser()
    parser.set_usage("%prog [options] [model]]")
    parser.set_description("A table for viewing and editing 1D and 2D attribute values")
    app = TaurusApplication(cmd_line_parser=parser,
                            app_name="TaurusValuesTable",
                            app_version=taurus.Release.version)
    args = app.get_command_line_args()

    dialog = TaurusValuesTable()
    dialog.setModifiableByUser(True)
    dialog.setWindowTitle(app.applicationName())
    
    #set a model list from the command line or launch the chooser  
    if len(args)==1:
        model=args[0]
        dialog.setModel(model)
    else:
        dialog.chooseModel()
        #model = 'sys/tg_test/1/string_spectrum'
        #model = 'sys/tg_test/1/wave'
        #dialog.setModel(model)

    dialog.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    taurusTableMain()
    
    
    

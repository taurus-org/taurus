#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

from builtins import str

from taurus.external.qt import Qt
from taurus.core.units import Quantity

import numpy

import taurus.core
from taurus.core.taurusbasetypes import (DataFormat, DataType, TaurusEventType,
                                         TaurusElementType)
from taurus.qt.qtgui.util import PintValidator
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.container import TaurusWidget
from taurus.core.util.enumeration import Enumeration


__all__ = ["TaurusValuesTable"]

__docformat__ = 'restructuredtext'


def _value2Quantity(value, units):
    '''
    Creates a Quantity from value and forces units if the vaule is unitless

    :param value: (int, float or str) a number or a string from which a quantity
                  can be created
    :param units: (str or Pint units) Units to use if the value is unitless
    :return: (Quantity)
    '''
    q = Quantity(value)
    if q.unitless:
        q = Quantity(q, units)
    return q


class TaurusValuesIOTableModel(Qt.QAbstractTableModel):
    typeCastingMap = {'f': float, 'b': bool,
                      'u': int, 'i': int, 'S': str, 'U': str}
    # Need to have an array

    dataChanged = Qt.pyqtSignal('QModelIndex', 'QModelIndex')

    def __init__(self, size, parent=None):
        Qt.QAbstractTableModel.__init__(self, parent)
        self._parent = parent
        self._rtabledata = []
        self._wtabledata = []
        self._rowCount = size[0]
        self._columnCount = size[1]
        self._modifiedDict = {}
        self._attr = None
        self.editedIndex = None
        self._editable = False
        self._writeMode = False

    def isDirty(self):
        '''returns True if there are user changes. False Otherwise'''
        return bool(self._modifiedDict)

    # To be implemented -----
    def rowCount(self, index=Qt.QModelIndex()):
        '''see :meth:`Qt.QAbstractTableModel.rowCount`'''
        if self._rowCount == 0:
            self._rowCount = 1
        return self._rowCount

    def columnCount(self, index=Qt.QModelIndex()):
        '''see :meth:`Qt.QAbstractTableModel.columnCount`'''
        if self._columnCount == 0:
            self._columnCount = 1
        return self._columnCount

    def data(self, index, role=Qt.Qt.DisplayRole):
        '''see :meth:`Qt.QAbstractTableModel.data`'''
        if self._writeMode == False:
            tabledata = self._rtabledata
        else:
            tabledata = self._wtabledata
        if not index.isValid() or not (0 <= index.row() < len(tabledata)):
            return None
        elif role == Qt.Qt.DisplayRole:
            value = None
            rc = (index.row(), index.column())
            if self._writeMode and rc in self._modifiedDict:
                if self.getAttr().type in [DataType.Integer, DataType.Float]:
                    return str(self._modifiedDict[rc])
                else:
                    return self._modifiedDict[rc]
            else:
                value = tabledata[rc]
                if isinstance(value, Quantity):
                    value = value.magnitude
            # cast the value to a standard python type
            value = self.typeCastingMap[tabledata.dtype.kind](value)
            return value
        elif role == Qt.Qt.DecorationRole:
            if ((index.row(), index.column()) in self._modifiedDict
                    and self._writeMode):
                if self.getAttr().type in [DataType.Integer, DataType.Float]:
                    value = self._modifiedDict[(index.row(), index.column())]
                    if not self.inAlarmRange(value):
                        icon = Qt.QIcon.fromTheme('document-save')
                    else:
                        icon = Qt.QIcon.fromTheme('emblem-important')
                else:
                    icon = Qt.QIcon.fromTheme('document-save')
                return icon
        elif role == Qt.Qt.EditRole:
            value = None
            if ((index.row(), index.column()) in self._modifiedDict
                    and self._writeMode):
                value = self._modifiedDict[(index.row(), index.column())]
            else:
                value = tabledata[index.row(), index.column()]
                if tabledata.dtype == bool:
                    value = bool(value)
            return value
        elif role == Qt.Qt.BackgroundRole:
            if self._writeMode:
                return Qt.QColor(22, 223, 21, 50)
            else:
                return Qt.QColor('white')
        elif role == Qt.Qt.ForegroundRole:
            if ((index.row(), index.column()) in self._modifiedDict
                    and self._writeMode):
                if self.getAttr().type in [DataType.Integer, DataType.Float]:
                    value = self._modifiedDict[(index.row(), index.column())]
                    if not self.inAlarmRange(value):
                        return Qt.QColor('blue')
                    else:
                        return Qt.QColor('orange')
                else:
                    return Qt.QColor('blue')
            return Qt.QColor('black')
        elif role == Qt.Qt.FontRole:
            if ((index.row(), index.column()) in self._modifiedDict
                    and self._writeMode):
                return Qt.QFont("Arial", 10, Qt.QFont.Bold)
        elif role == Qt.Qt.ToolTipRole:
            if ((index.row(), index.column()) in self._modifiedDict
                    and self._writeMode):
                value = str(self._modifiedDict[(index.row(), index.column())])
                msg = 'Original value: %s.\nNew value that will be saved: %s' %\
                      (str(tabledata[index.row(), index.column()]), value)
                return msg
        return None

    def getAttr(self):
        return self._attr

    def setAttr(self, attr):
        '''
        Updated the internal table data from an attribute value

        :param attr: (DeviceAttribute)
        '''
        self._attr = attr
        rvalue = attr.rvalue
        if attr.type not in [DataType.Float, DataType.Integer]:
            rvalue = numpy.array(attr.rvalue)
        # reshape the table
        if attr.data_format == DataFormat._1D:
            rows, columns = len(rvalue), 1
        elif attr.data_format == DataFormat._2D:
            rows, columns = numpy.shape(rvalue)
        else:
            raise TypeError('Unsupported data format "%s"' %
                            repr(attr.data_format))

        if (self._rowCount != rows) or (self._columnCount != columns):
            self.beginResetModel()
            self.endResetModel()

        self._rowCount = rows
        self._columnCount = columns
        rvalue = rvalue.reshape(rows, columns)
        if attr.type in [DataType.Integer, DataType.Float]:
            units = self._parent.getCurrentUnits()
            rvalue = rvalue.to(units)
        self._rtabledata = rvalue
        self._editable = False
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(rows - 1, columns - 1))

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
        rtable_value = self._rtabledata[index.row()][index.column()]
        if self._attr.getType() in [DataType.Float, DataType.Integer]:
            units = self._parent.getCurrentUnits()
            value = _value2Quantity(value, units)
            equals = numpy.allclose(rtable_value, value.to(units))
        else:
            equals = bool(rtable_value == value)
        if not equals:
            self._modifiedDict[(index.row(), index.column())] = value
        else:
            self.removeValue(index)

    def removeValue(self, index):
        '''
        Removes index from dictionary

        :param index:  (QModelIndex) table index
        '''
        if (index.row(), index.column()) in self._modifiedDict:
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
            table = table.tolist()  # we want to allow the strings to be larger than the original ones
            for (r, c), v in self._modifiedDict.items():
                table[r][c] = v
            table = numpy.array(table, dtype=str)
        else:
            for k, v in self._modifiedDict.items():
                if kind in ['f', 'i', 'u']:
                    units = self._parent.getCurrentUnits()
                    q = _value2Quantity(v, units)
                    table[k] = q
                elif kind == 'b':
                    if str(v) == "true":
                        table[k] = True
                    else:
                        table[k] = False
                else:
                    raise TypeError('Unknown data type "%s"' % kind)
        # reshape if needed
        if self._attr.data_format == DataFormat._1D:
            table = table.flatten()
        return table

    def clearChanges(self):
        '''clears the dictionary of changed values'''
        self._modifiedDict.clear()
        self.dataChanged.emit(self.createIndex(
            0, 0), self.createIndex(self.rowCount() - 1, self.columnCount() - 1))

    def inAlarmRange(self, value):
        '''
        Checkes if value is in alarm range.

        :param value:  Quantity value
        :returns:  (bool) True if value in alarm range, False if valid

        '''
        try:
            min_alarm, max_alarm = self._attr.alarms
            if min_alarm >= value or value >= max_alarm:
                return True
            else:
                return False
        except:
            return True

    def inRange(self, value):
        '''
        Checks if value is in range.

        :param value:  Quantity value
        :returns:  (bool) True if value in range, False if valid

        '''
        try:
            min_range, max_range = self._attr.range
            if min_range <= value <= max_range:
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
        if isWrite and not self.isDirty() and self._attr is not None:
            # refresh the write data (unless it is dirty)
            wvalue = self._attr.wvalue

            # reshape the table
            if self._attr.type == DataType.String:
                wvalue = numpy.array(wvalue)
            elif self._attr.type in [DataType.Integer, DataType.Float]:
                units = self._parent.getCurrentUnits()
                wvalue = wvalue.to(units)
            if self._attr.data_format == DataFormat._1D:
                rows, columns = numpy.shape(wvalue)[0], 1
                if rows == 0:
                    # TODO: Ask to the user for a default shape
                    rows = 3
            elif self._attr.data_format == DataFormat._2D:
                try:
                    rows, columns = numpy.shape(wvalue)
                except ValueError:
                    # TODO: Ask to the user for a default shape
                    rows = 3
                    columns = 3
                    wvalue = numpy.array((rows, columns))
            else:
                self.warning('unsupported data format %s' %
                             str(wvalue.data_format))
            wvalue = wvalue.reshape(rows, columns)
            # In version 4.6 of Qt when whole table is updated it is
            # recommended to use beginReset()
            self._wtabledata = wvalue
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount() - 1,
                                                           self.columnCount() - 1))

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

    def __init__(self, parent=None):
        self._parent = parent
        name = self.__class__.__name__
        Qt.QTableView.__init__(self, parent)
        self._showQuality = True
        self._attr = None
        self._value = None
        self.setSelectionMode(Qt.QAbstractItemView.SingleSelection)
        itemDelegate = TaurusValuesIOTableDelegate(self)
        self.setItemDelegate(itemDelegate)
        #self.setStyleSheet('TaurusValuesIOTable { selection-background-color: violet;} ')

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget overwriting
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def setModel(self, shape):
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
        icon = Qt.QIcon.fromTheme('document-save').pixmap(48, 48)
        l = Qt.QLabel()
        l.setPixmap(icon)
        buttonBox.layout().addWidget(l, 0, 0)
        buttonBox.layout().addWidget(Qt.QLabel(
            '- value is valid and will be saved if changes will be accepted'), 0, 1)
        icon = Qt.QIcon.fromTheme('ddialog-warning').pixmap(48, 48)
        l = Qt.QLabel()
        l.setPixmap(icon)
        buttonBox.layout().addWidget(l, 1, 0)
        buttonBox.layout().addWidget(Qt.QLabel(
            '- value is in alarm range and will be saved if changes will be accepted'), 1, 1)
        buttonBox.exec_()

    def getCurrentUnits(self):
        try:
            return str(self._parent._units.currentText())
        except:
            return ''


class TaurusValuesIOTableDelegate(Qt.QStyledItemDelegate):

    editorCreated = Qt.pyqtSignal()

    def __init__(self, parent=None):
        Qt.QStyledItemDelegate.__init__(self, parent)
        self._parent = parent
        self._initialText = ""

    def createEditor(self, parent, option, index):
        '''
        Creates a custom editor for a table delagate.

        see :meth:`Qt.QStyledItemDelegate.createEditor`
        '''
        if index.model().getType() == bool:
            #editor = Qt.QStyledItemDelegate.createEditor(self,parent,option,index)
            editor = Qt.QComboBox(parent)
        else:
            editor = TableInlineEdit(parent)
            editor._updateValidator(index.model().getAttr())
        self.editorCreated.emit()
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
            a = str(index.data()).lower()
            self._initialText = a

            editor.setCurrentIndex(editor.findText(a))
        else:
            data = index.model().data(index, Qt.Qt.EditRole)
            self._initialText = data
            editor.setText(str(self._initialText))

    def setModelData(self, editor, model, index):
        '''
        see :meth:`Qt.QStyledItemDelegate.setModelData`
        '''
        # if editor text changed, then don't mark as updated.
        isNumeric = False
        if self._parent._attr.type in [DataType.Integer, DataType.Float]:
            units = self._parent.getCurrentUnits()
            q = _value2Quantity(editor.text(), units)
            isNumeric = True
            if not model.inRange(q):
                return
        if index.model().getType() == bool:
            text = editor.currentText()
        else:
            if isNumeric:
                text = q
            else:
                text = editor.text()
            text = str(text)
        if(text != self._initialText) & (text != ""):
            model.addValue(index, text)
            hh = self.parent().horizontalHeader()
            if hh.length() > 0:
                try:
                    hh.setSectionResizeMode(hh.Fixed)
                except AttributeError:  # PyQt4
                    hh.setResizeMode(hh.Fixed)
            vh = self.parent().verticalHeader()
            if vh.length() > 0:
                try:
                    vh.setSectionResizeMode(vh.Fixed)
                except AttributeError:  # PyQt4
                    hh.setResizeMode(vh.Fixed)

        index.model().editedIndex = None


class TableInlineEdit(Qt.QLineEdit):
    '''
    TableInLineEdit is used to validate the content of the new value, also to paint the text: blue - valid, orange - in alarm, grey - invalid.
    '''

    def __init__(self, parent=None):
        super(Qt.QLineEdit, self).__init__(parent)
        self.textEdited.connect(self.onTextEdited)
        self.setValidator(None)
        self._min_range = None
        self._max_range = None
        self._min_alarm = None
        self._max_alarm = None
        self._default_unit = None

    def onTextEdited(self):
        """
        Paints the text while typing.

        Slot for the `Qt.QLineEdit.textEdited` signal
        """
        # default case: the value is in normal range with no pending changes
        color, weight = 'gray', 'normal'
        try:
            value = self.displayText()
            q = _value2Quantity(value, self._default_unit)
        except:
            q = 0.0
        try:
            if self._min_alarm < q < self._max_alarm:
                color = 'blue'
            elif self._min_range <= q <= self._max_range:
                # the value is valid but in alarm range...
                color = 'orange'
            else:
                # the value is invalid and can't be applied
                color = 'gray'
        except:
            color = 'gray'

        weight = 'bold'
        self.setStyleSheet('TableInlineEdit {color: %s; font-weight: %s}' %
                           (color, weight))

    def _updateValidator(self, attr):
        '''This method sets a validator depending on the data type

        :param attr: TaurusAttribute
        '''
        data_type = attr.getType()
        if data_type in [DataType.Integer, DataType.Float]:
            self._min_range, self._max_range = attr.range
            self._min_alarm, self._max_alarm = attr.alarms
            self._default_unit = attr.wvalue.units
            validator = PintValidator()
            validator.setBottom(self._min_range)
            validator.setTop(self._max_range)
            validator.setUnits(self._default_unit)
            self.setValidator(validator)
        else:
            self.setValidator(None)

    def __decimalDigits(self, fmt):
        '''returns the number of decimal digits from a format string
        (or None if they are not defined)'''
        try:
            if fmt[-1].lower() in ['f', 'g'] and '.' in fmt:
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

    def __init__(self, parent=None, designMode=False,
                 defaultWriteMode=None):
        TaurusWidget.__init__(self, parent=parent, designMode=designMode)
        self._tableView = TaurusValuesIOTable(self)
        l = Qt.QGridLayout()
        l.addWidget(self._tableView, 1, 0)
        self._tableView.itemDelegate().editorCreated.connect(self._onEditorCreated)

        if defaultWriteMode is None:
            self.defaultWriteMode = "rw"
        else:
            self.defaultWriteMode = defaultWriteMode

        self._label = TaurusLabel()
        self._label.setBgRole('quality')
        self._label.setFgRole('quality')

        self._units = Qt.QComboBox()

        self._applyBT = Qt.QPushButton('Apply')
        self._cancelBT = Qt.QPushButton('Cancel')
        self._applyBT.clicked.connect(self.okClicked)
        self._cancelBT.clicked.connect(self.cancelClicked)

        self._rwModeCB = Qt.QCheckBox()
        self._rwModeCB.setText('Write mode')
        self._rwModeCB.toggled.connect(self.setWriteMode)

        lv = Qt.QHBoxLayout()
        lv.addWidget(self._label)
        lv.addWidget(self._units)
        l.addLayout(lv, 2, 0)
        l.addWidget(self._rwModeCB, 0, 0)
        lv = Qt.QHBoxLayout()
        lv.addWidget(self._applyBT)
        lv.addWidget(self._cancelBT)
        l.addLayout(lv, 3, 0)
        self._writeMode = False
        self.setLayout(l)
        self._initActions()

    def _initActions(self):
        """Initializes the actions for this widget (currently, the pause action.)
        """
        self._pauseAction = Qt.QAction("&Pause", self)
        self._pauseAction.setShortcuts([Qt.Qt.Key_P, Qt.Qt.Key_Pause])
        self._pauseAction.setCheckable(True)
        self._pauseAction.setChecked(False)
        self.addAction(self._pauseAction)
        self._pauseAction.toggled.connect(self.setPaused)
        self.chooseModelAction = Qt.QAction("Choose &Model", self)
        self.chooseModelAction.setEnabled(self.isModifiableByUser())
        self.addAction(self.chooseModelAction)
        self.chooseModelAction.triggered.connect(self.chooseModel)

    def getModelClass(self):
        '''see :meth:`TaurusWidget.getModelClass`'''
        return taurus.core.taurusattribute.TaurusAttribute

    def setModel(self, model):
        '''Reimplemented from :meth:`TaurusWidget.setModel`'''
        TaurusWidget.setModel(self, model)
        model_obj = self.getModelObj()

        if model_obj.isWritable() and self.defaultWriteMode != "r":
            self._writeMode = True
        else:
            self.defaultWriteMode = "r"

        if model_obj is not None:
            self._tableView._attr = model_obj
            if model_obj.type in [DataType.Integer, DataType.Float]:
                if self._writeMode:
                    try:
                        default_unit = str(model_obj.wvalue.units)
                    except AttributeError:
                        default_unit = ''
                else:
                    default_unit = str(model_obj.rvalue.units)
                # TODO: fill the combobox with the compatible units
                self._units.addItem("%s" % default_unit)
                self._units.setCurrentIndex(self._units.findText(default_unit))
                self._units.setEnabled(False)
            else:
                self._units.setVisible(False)
            raiseException = False
            if model_obj.data_format == DataFormat._2D:
                try:
                    dim_x, dim_y = numpy.shape(model_obj.rvalue)
                except ValueError:
                    raiseException = True
            elif model_obj.data_format == DataFormat._1D:
                try:
                    dim_x, dim_y = len(model_obj.rvalue), 1
                except ValueError:
                    raiseException = True
            else:
                raiseException = True
            if raiseException:
                raise Exception('rvalue is invalid')
            self._tableView.setModel([dim_x, dim_y])
        self.setWriteMode(self._writeMode)
        self._label.setModel(model)

    def handleEvent(self, evt_src, evt_type, evt_value):
        '''see :meth:`TaurusWidget.handleEvent`'''
        #@fixme: in some situations, we may miss some config event because of the qmodel not being set. The whole handleEvent Method and setModel method should be re-thought
        model = self._tableView.model()
        if model is None:
            return
        if evt_type in (TaurusEventType.Change,
                        TaurusEventType.Periodic)\
                and evt_value is not None:
            attr = self.getModelObj()
            model.setAttr(attr)
            model.setWriteMode(self._writeMode)

            hh = self._tableView.horizontalHeader()
            if hh.length() > 0:
                try:
                    hh.setSectionResizeMode(hh.Fixed)
                except AttributeError:  # PyQt4
                    hh.setResizeMode(hh.Fixed)
            vh = self._tableView.verticalHeader()
            if vh.length() > 0:
                try:
                    vh.setSectionResizeMode(vh.Fixed)
                except AttributeError:  # PyQt4
                    hh.setResizeMode(vh.Fixed)
            if self.defaultWriteMode == "r":
                isWritable = False
            else:
                isWritable = True
            writable = isWritable and self._writeMode and\
                attr.isWritable()
            self.setWriteMode(writable)
        elif evt_type == TaurusEventType.Config:
            # force a read to set an attr
            attr = self.getModelObj()
            model.setAttr(attr)

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
                if (index.row(), index.column()) in self._tableView.model().getModifiedDict():
                    menu.addAction(Qt.QIcon.fromTheme(
                        'edit-undo'), "Reset to original value (%s) " % repr(val), self._tableView.removeChange)
                    menu.addSeparator()
                menu.addAction(Qt.QIcon.fromTheme('process-stop'),
                               "Reset all table", self.askCancel)
                menu.addSeparator()
                menu.addAction(Qt.QIcon.fromTheme('help-browser'),
                               "Help", self._tableView.showHelp)
        menu.exec_(globalPos)
        event.accept()

    def applyChanges(self):
        '''
        Writes table modifications to the device server.
        '''
        tab = self._tableView.model().getModifiedWriteData()
        attr = self.getModelObj()
        if attr.type == DataType.String:
            # String arrays has to be converted to a list
            tab = tab.tolist()
        attr.write(tab)
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
        result = Qt.QMessageBox.warning(self, 'Your changes will be lost!',
                                        'Do you want to cancel changes done to the whole table?',
                                        Qt.QMessageBox.Ok | Qt.QMessageBox.Cancel)
        if result == Qt.QMessageBox.Ok:
            self._tableView.cancelChanges()
            self.resetWriteMode()

    def _onEditorCreated(self):
        '''slot called when an editor has been created'''
        self.setWriteMode(self._writeMode)

    def getWriteMode(self):
        '''whether the widget is showing the read or write values

        :return: (bool)'''
        return self._writeMode

    def setWriteMode(self, isWrite):
        '''
        Triggered when the read mode is changed to write mode.

        :param isWrite: (bool)
        '''
        self._applyBT.setVisible(isWrite)
        self._cancelBT.setVisible(isWrite)
        self._rwModeCB.setChecked(isWrite)
        if self.defaultWriteMode in ("rw", "wr"):
            self._rwModeCB.setVisible(True)
        else:
            self._rwModeCB.setVisible(False)

        table_view_model = self._tableView.model()
        if table_view_model is not None:
            table_view_model.setWriteMode(isWrite)
            table_view_model._editable = isWrite
        if isWrite == self._writeMode:
            return
        self._writeMode = isWrite
        valueObj = self.getModelValueObj()
        if isWrite and valueObj is not None:
            w_value = valueObj.wvalue
            value = valueObj.rvalue
            if numpy.array(w_value).shape != numpy.array(value).shape:
                ta = self.getModelObj()
                v = ta.read()
                # @fixme: this is ugly! we should not be writing into the attribute without asking first...
                ta.write(v.rvalue)

    def resetWriteMode(self):
        '''equivalent to self.setWriteMode(self.defaultWriteMode)'''
        if self.defaultWriteMode == "r":
            isWritable = False
        else:
            isWritable = True
        self.setWriteMode(isWritable)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        '''Reimplemented from :meth:`TaurusWidget.getQtDesignerPluginInfo`'''
        ret = TaurusWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.table'
        ret['group'] = 'Taurus Views'
        ret['icon'] = "designer:table.png"
        return ret

    def chooseModel(self):
        '''shows a model chooser'''
        from taurus.qt.qtgui.panel import TaurusModelChooser
        selectables = [TaurusElementType.Attribute]
        models, ok = TaurusModelChooser.modelChooserDlg(
            selectables=selectables, singleModel=True)
        if ok and len(models) == 1:
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
    writeMode = Qt.pyqtProperty(
        "bool", getWriteMode, setWriteMode, resetWriteMode)


def taurusTableMain():
    '''A launcher for TaurusValuesTable.'''

    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.core.util import argparse
    import sys
    import os

    parser = argparse.get_taurus_parser()
    parser.set_usage("%prog [options] [model]]")
    parser.set_description(
        "A table for viewing and editing 1D and 2D attribute values")
    app = TaurusApplication(cmd_line_parser=parser,
                            app_name="TaurusValuesTable",
                            app_version=taurus.Release.version)
    args = app.get_command_line_args()

    dialog = TaurusValuesTable()
    dialog.setModifiableByUser(True)
    dialog.setWindowTitle(app.applicationName())

    # set a model list from the command line or launch the chooser
    if len(args) == 1:
        model = args[0]
        dialog.setModel(model)
    else:
        dialog.chooseModel()
        #model = 'sys/tg_test/1/boolean_spectrum'
        # model = 'sys/tg_test/1/boolean_image'
        # model = 'sys/tg_test/1/string_spectrum'
        # model = 'sys/tg_test/1/float_image'
        # model = 'sys/tg_test/1/double_image'
        # model = 'sys/tg_test/1/double_image_ro'
        # model = 'sys/tg_test/1/wave'
        # dialog.setModel(model)

    dialog.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    taurusTableMain()

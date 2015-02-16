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

from taurus.external.qt import Qt
from taurus import Database
from taurus.core.taurusbasetypes import TaurusElementType
from taurus.core.taurusdatabase import TaurusAttrInfo
from taurus.qt.qtgui.input import TaurusAttrListComboBox
from taurus.qt.qtgui.tree import TaurusDbTreeWidget
from taurus.qt.qtgui.resource import getThemeIcon
from sardana.taurus.qt.qtgui.extra_macroexecutor.macroparameterseditor.macroparameterseditor import MacroParametersEditor
from sardana.taurus.qt.qtgui.extra_macroexecutor.macroparameterseditor.parameditors import LineEditParam, ParamBase, ComboBoxParam, CheckBoxParam, DirPathParam, MSAttrListComboBoxParam
from sardana.taurus.qt.qtgui.extra_macroexecutor.macroparameterseditor.model import ParamEditorModel
from sardana.taurus.qt.qtgui.extra_macroexecutor.common import MSAttrListComboBox


class SenvEditor(Qt.QWidget, MacroParametersEditor):

    def __init__(self, parent=None):
        Qt.QWidget.__init__(self, parent)
        MacroParametersEditor.__init__(self)
        self.valueWidget = None

    def initComponents(self):
        self.setLayout(Qt.QFormLayout())

        self.layout().addRow(Qt.QLabel("Setting environment variable:", self))

        self.nameComboBox = ComboBoxParam(self)
        self.nameComboBox.addItems(["ActiveMntGrp", "ExtraColumns", "JsonRecorder", "ScanFile", "ScanDir"])
        self.nameComboBox.setEditable(True)
        self.connect(self.nameComboBox, Qt.SIGNAL("currentIndexChanged(int)"), self.onNameComboBoxChanged)
        self.layout().addRow("name:", self.nameComboBox)

        nameIndex = self.model().index(0, 1, self.rootIndex())
        self.nameComboBox.setIndex(nameIndex)

    def setRootIndex(self, rootIndex):
        self._rootIndex = rootIndex
        self.initComponents()

    def rootIndex(self):
        return self._rootIndex

    def model(self):
        return self._model

    def setModel(self, model):
        self._model = model
        if isinstance(model, ParamEditorModel):
            self.setRootIndex(Qt.QModelIndex())

    def onNameComboBoxChanged(self, index):
        text = str(self.nameComboBox.currentText())
        if self.valueWidget is not None:
            label = self.layout().labelForField(self.valueWidget)
            if label is not None:
                self.layout().removeWidget(label)
                label.setParent(None)
                label = None

            self.layout().removeWidget(self.valueWidget)
            self.valueWidget.resetValue()
            self.valueWidget.setParent(None)
            self.valueWidget = None

        self.valueWidget, label = getSenvValueEditor(text, self)

        paramRepeatIndex = self.model().index(1, 0, self.rootIndex())
        repeatIndex = paramRepeatIndex.child(0, 0)
        valueIndex = repeatIndex.child(0, 1)
        self.valueWidget.setIndex(valueIndex)

        if label:
            self.layout().addRow(label, self.valueWidget)
        else:
            self.layout().addRow(self.valueWidget)

def getSenvValueEditor(envName, parent):
    """Factory method, requires: string, and QWidget as a parent for returned editor.
    Factory returns a tuple of widget and a label for it.
    
    :return: (Qt.QWidget, str) """
    label = "value:"
    if envName == "ActiveMntGrp":
        editor = MSAttrListComboBoxParam(parent)
        editor.setUseParentModel(True)
        editor.setModel("/MeasurementGroupList")
    elif envName == "ExtraColumns":
        editor = ExtraColumnsEditor(parent)
        label = None
    elif envName == "JsonRecorder":
        editor = CheckBoxParam(parent)
    elif envName == "ScanDir":
        editor = DirPathParam(parent)
    elif envName == "ScanFile":
        editor = LineEditParam(parent)
    else:
        editor = LineEditParam(parent)
    return editor, label

class ExtraColumnsEditor(ParamBase, Qt.QWidget):

    def __init__(self, parent=None, paramModel=None):
        ParamBase.__init__(self, paramModel)
        Qt.QWidget.__init__(self, parent)
        self.setLayout(Qt.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        addNewColumnButton = Qt.QPushButton(getThemeIcon("list-add") , "Add new column...", self)
        removeSelectedColumnsButton = Qt.QPushButton(getThemeIcon("list-remove") , "Remove selected...", self)
        buttonsLayout = Qt.QHBoxLayout()
        buttonsLayout.addWidget(addNewColumnButton)
        buttonsLayout.addWidget(removeSelectedColumnsButton)
        self.layout().addLayout(buttonsLayout)

        self.extraColumnsTable = ExtraColumnsTable(self)
        self.extraColumnsModel = ExtraColumnsModel()
        self.extraColumnsTable.setModel(self.extraColumnsModel)
        self.extraColumnsTable.setItemDelegate(ExtraColumnsDelegate(self.extraColumnsTable))

        self.layout().addWidget(self.extraColumnsTable)

        self.connect(addNewColumnButton, Qt.SIGNAL("clicked()"), self.onAddNewColumn)
        self.connect(removeSelectedColumnsButton, Qt.SIGNAL("clicked()"), self.onRemoveSelectedColumns)
        self.connect(self.extraColumnsModel, Qt.SIGNAL("dataChanged (const QModelIndex&,const QModelIndex&)"), self.onExtraColumnsChanged)
        self.connect(self.extraColumnsModel, Qt.SIGNAL("modelReset()"), self.onExtraColumnsChanged)

    def getValue(self):
        return repr(self.extraColumnsTable.model().columns())

    def setValue(self, value):
        try:
            columns = eval(value)
        except:
            columns = []
        self.extraColumnsTable.setColumns(columns)

    def onAddNewColumn(self):
        self.extraColumnsTable.insertRows()
        self.emit(Qt.SIGNAL("modelChanged()"))

    def onRemoveSelectedColumns(self):
        self.extraColumnsTable.removeRows()
        self.emit(Qt.SIGNAL("modelChanged()"))

    def onExtraColumnsChanged(self):
        self.emit(Qt.SIGNAL("modelChanged()"))


class ExtraColumnsTable(Qt.QTableView):

    def __init__(self, parent):
        Qt.QTableView.__init__(self, parent)
        self.setSelectionBehavior(Qt.QAbstractItemView.SelectRows)
        self.setSelectionMode(Qt.QAbstractItemView.ExtendedSelection)

    def setColumns(self, columns):
        if columns == None: columns = []
        self.model().setColumns(columns)
        self.resizeColumnsToContents()

    def insertRows(self):
        self.model().insertRows(self.model().rowCount())

    def removeRows(self):
        rows = [index.row() for index in self.selectedIndexes()]
        rows = list(set(rows))
        rows.sort(reverse=True)
        for row in rows:
            self.model().removeRows(row)


class ExtraColumnsDelegate(Qt.QItemDelegate):

    def __init__(self, parent=None):
        Qt.QItemDelegate.__init__(self, parent)
        db = Database()
        self.host = db.getNormalName()

    def createEditor(self, parent, option, index):
        if index.column() == 1:
            self.combo_attr_tree_widget = TaurusDbTreeWidget(perspective=TaurusElementType.Device)
            self.combo_attr_tree_widget.setModel(self.host)
            treeView = self.combo_attr_tree_widget.treeView()
            qmodel = self.combo_attr_tree_widget.getQModel()
            editor = Qt.QComboBox(parent)
            editor.setModel(qmodel)
            editor.setMaxVisibleItems(20)
            editor.setView(treeView)
        elif index.column() == 2:
            editor = MSAttrListComboBox(parent)
            editor.setUseParentModel(True)
            editor.setModel("/InstrumentList")
        else:
            editor = Qt.QItemDelegate.createEditor(self, parent, option, index)
        return editor

    def setEditorData(self, editor, index):
        if index.column() == 2:
            text = Qt.from_qvariant(index.model().data(index, Qt.Qt.DisplayRole), str)
            editor.setCurrentText(text)
        else:
            Qt.QItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        column = index.column()
        if column == 1:
            selectedItems = self.combo_attr_tree_widget.selectedItems()
            if not len(selectedItems) == 1: return
            taurusTreeAttributeItem = selectedItems[0]
            itemData = taurusTreeAttributeItem.itemData()
            if isinstance(itemData, TaurusAttrInfo):
                model.setData(index, Qt.QVariant(itemData.fullName()))
        elif column == 2:
            model.setData(index, Qt.QVariant(editor.currentText()))
        else:
            Qt.QItemDelegate.setModelData(self, editor, model, index)

    def sizeHint(self, option, index):
        if index.column() == 0:
            fm = option.fontMetrics
            text = Qt.from_qvariant(index.model().data(index, Qt.Qt.DisplayRole), str)
            document = Qt.QTextDocument()
            document.setDefaultFont(option.font)
            document.setHtml(text)
            size = Qt.QSize(document.idealWidth() + 5, fm.height())
        elif index.column() == 1:
            editor = self.createEditor(self.parent(), option, index)
            if editor is None:
                size = Qt.QItemDelegate.sizeHint(self, option, index)
            else:
                size = editor.sizeHint()
                editor.hide()
                editor.setParent(None)
#                editor.destroy()
        else:
            size = Qt.QItemDelegate.sizeHint(self, option, index)
        return size

class ExtraColumnsModel(Qt.QAbstractTableModel):


    def __init__(self, columns=None):
        if columns is None: columns = []
        Qt.QAbstractItemModel.__init__(self)
        self.__columns = columns

    def setColumns(self, columns):
        self.__columns = columns
        self.reset()

    def columns(self):
        return self.__columns

    def rowCount(self, index=Qt.QModelIndex()):
        return len(self.__columns)

    def columnCount(self, index=Qt.QModelIndex()):
        return 3

    def data(self, index, role=Qt.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return Qt.QVariant()
        row = index.row()
        column = index.column()
        #Display Role
        if role == Qt.Qt.DisplayRole:
            if column == 0: return Qt.QVariant(Qt.QString(self.__columns[row]['label']))
            elif column == 1: return Qt.QVariant(Qt.QString(self.__columns[row]['model']))
            elif column == 2: return Qt.QVariant(Qt.QString(self.__columns[row]['instrument']))
        return Qt.QVariant()

    def headerData(self, section, orientation, role=Qt.Qt.DisplayRole):
        if role == Qt.Qt.TextAlignmentRole:
            if orientation == Qt.Qt.Horizontal:
                return Qt.QVariant(int(Qt.Qt.AlignLeft | Qt.Qt.AlignVCenter))
            return Qt.QVariant(int(Qt.Qt.AlignRight | Qt.Qt.AlignVCenter))
        if role != Qt.Qt.DisplayRole:
            return Qt.QVariant()
        #So this is DisplayRole...
        if orientation == Qt.Qt.Horizontal:
            if section == 0: return Qt.QVariant("Label")
            elif section == 1: return Qt.QVariant("Attribute")
            elif section == 2: return Qt.QVariant("Instrument")
            return Qt.QVariant()
        else:
            return Qt.QVariant(Qt.QString.number(section + 1))

    def flags(self, index):
        flags = Qt.Qt.ItemIsEnabled | Qt.Qt.ItemIsSelectable
        if index.isValid():
            column = index.column()
            if column in (0, 1, 2):
                flags |= Qt.Qt.ItemIsEditable
        return flags

    def setData(self, index, value=None, role=Qt.Qt.EditRole):
        if index.isValid() and (0 <= index.row() < self.rowCount()):
            row = index.row()
            column = index.column()
            value = Qt.from_qvariant(value, str)
            if column == 0: self.__columns[row]['label'] = value
            elif column == 1: self.__columns[row]['model'] = value
            elif column == 2: self.__columns[row]['instrument'] = value
            self.emit(Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
            return True
        return False

    def insertRows(self, row, rows=1, parentindex=None):
        if parentindex is None: parentindex = Qt.QModelIndex()
        first = row
        last = row + rows - 1
        self.beginInsertRows(parentindex, first, last)
        for row in range(first, last + 1):
            self.insertRow(row)
        self.endInsertRows()
        return True

    def insertRow(self, row, parentIndex=None):
        self.__columns.insert(row, {'label':'', 'model':'', 'instrument':''})

    def removeRows(self, row, rows=1, parentindex=None):
        if parentindex is None: parentindex = Qt.QModelIndex()
        first = row
        last = row + rows - 1
        self.beginRemoveRows(parentindex, first, last)
        for row in range(first, last + 1):
            self.removeRow(row)
        self.endRemoveRows()
        return True

    def removeRow(self, row, parentIndex=None):
        self.__columns.pop(row)

CUSTOM_EDITOR = SenvEditor

if __name__ == "__main__":
    import sys
    import taurus
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(sys.argv)
    args = app.get_command_line_args()
    editor = SenvEditor()
    macroServer = taurus.Device(args[0])
    macroInfoObj = macroServer.getMacroInfoObj("senv")
    macroNode = MacroNode()
    editor.setMacroNode(macroNode)
    editor.show()

    sys.exit(app.exec_())

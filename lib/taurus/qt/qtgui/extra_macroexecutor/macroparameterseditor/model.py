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
model.py:
"""
from taurus.qt import Qt
from lxml import etree
from taurus.core.tango.sardana import macro
from taurus.qt.qtgui.extra_macroexecutor import globals


class ParamEditorModel(Qt.QAbstractItemModel):

    def __init__(self, parent=None):
        Qt.QAbstractItemModel.__init__(self, parent)
        self.columns = 2
        self.setRoot()
        self.headers = ["Parameter","Value"]

    def root(self):
        return self._root

    def setRoot(self, node=None):
        if node == None: node = macro.MacroNode()
        self._root = node
        self.reset()

    def flags(self, index):
        if index.column() == 0:
            return Qt.Qt.ItemIsEnabled | Qt.Qt.ItemIsSelectable

        node = self.nodeFromIndex(index)

        if (index.column() == 1 and
            isinstance(node, macro.SingleParamNode) and
            not node.type() in globals.EDITOR_NONEDITABLE_PARAMS):
            return Qt.Qt.ItemIsEnabled | Qt.Qt.ItemIsEditable
        return Qt.Qt.ItemIsEnabled

    def _insertRow(self, parentIndex, node=None, row=-1):
        parentNode = self.nodeFromIndex(parentIndex)

        if row == -1: row = len(parentNode)

        if node == None: node = parentNode.newRepeat()

        self.beginInsertRows(parentIndex, row, row)
        row = parentNode.insertChild(node, row)
        self.endInsertRows()

        return self.index(row, 0, parentIndex)

    def _removeRow(self, index):
        """This method is used remove macro (pased via index)"""
        node = self.nodeFromIndex(index)
        parentIndex = index.parent()
        parentNode = self.nodeFromIndex(parentIndex)
        row = parentNode.rowOfChild(node)
        self.beginRemoveRows(parentIndex, row, row)
        parentNode.removeChild(node)
        self.endRemoveRows()

    def _upRow(self, index):
        node = self.nodeFromIndex(index)
        parentIndex = index.parent()
        parentNode = self.nodeFromIndex(parentIndex)
        row = parentNode.rowOfChild(node)
        self._removeRow(index)
        newIndex = self._insertRow(parentIndex, node, row - 1)
        parentNode.arrangeIndexes()
        return newIndex

    def _downRow(self, index):
        node = self.nodeFromIndex(index)
        parentIndex = index.parent()
        parentNode = self.nodeFromIndex(parentIndex)
        row = parentNode.rowOfChild(node)
        self._removeRow(index)
        newIndex = self._insertRow(parentIndex, node, row + 1)
        parentNode.arrangeIndexes()
        return newIndex


    def addRepeat(self, index, callReset=True):
        paramRepeatNode = self.nodeFromIndex(index)
        paramRepeatNode.addRepeat()
        if callReset:
            self.reset()

    def delRepeat(self, index, callReset=True):
        branchIndex = self.parent(index)
        branch = self.nodeFromIndex(branchIndex)
        child = self.nodeFromIndex(index)
        branch.removeChild(child)
        if callReset:
            self.reset()

    def upRepeat(self, index, callReset=True):
        branchIndex = self.parent(index)
        branch = self.nodeFromIndex(branchIndex)
        child = self.nodeFromIndex(index)
        branch.upChild(child)
        if callReset:
            self.reset()

    def downRepeat(self, index, callReset=True):
        branchIndex = self.parent(index)
        branch = self.nodeFromIndex(branchIndex)
        child = self.nodeFromIndex(index)
        branch.downChild(child)
        if callReset:
            self.reset()

    def rowCount(self, index):
        node = self.nodeFromIndex(index)
        if node is None or isinstance(node, macro.SingleParamNode):
            return 0
        return len(node)

    def columnCount(self, parent):
        return self.columns

    def data(self, index, role):
        if not index.isValid() or not (0 <= index.row() < self.rowCount(index.parent())):
            return Qt.QVariant()

        if role == Qt.Qt.DisplayRole:
            node = self.nodeFromIndex(index)
            if index.column() == 0:
                return Qt.QVariant(node.name())
            elif index.column() == 1:
                return Qt.QVariant(node.value())

        return Qt.QVariant()


    def setData (self, index, value, role=Qt.Qt.EditRole):
        node = self.nodeFromIndex(index)
#        if index.isValid() and 0 <= index.row() < len(node.parent()):
        if index.column() == 1:
            node.setValue(Qt.from_qvariant(value, str))
            self.emit(Qt.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
            return True
        return False

    def headerData(self, section, orientation, role):
        if orientation == Qt.Qt.Horizontal and role == Qt.Qt.DisplayRole:
            return Qt.QVariant(self.headers[section])
        return Qt.QVariant()

    def index(self, row, column, parent):
        if not parent.isValid():
            parentNode = self.root();
        else:
            parentNode = parent.internalPointer()
        childNode = parentNode.child(row)
        if childNode is None:
            return Qt.QModelIndex();
        else:
            return self.createIndex(row, column, childNode);


    def parent(self, child):
        node = self.nodeFromIndex(child)
        if node is None:
            return Qt.QModelIndex()
        parent = node.parent()
        if parent is None or isinstance(parent, macro.SequenceNode):
            return Qt.QModelIndex()
        grandparent = parent.parent()
        if grandparent is None:
            return Qt.QModelIndex()
        row = grandparent.rowOfChild(parent)
        return self.createIndex(row, 0, parent)

    def nodeFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        else:
            return self.root()

    def toSpockCommand(self):
        """
        Converts root obj (MacroNode) to string representing spock command and returns it.

        :return: (etree.Element)
        """

        return self.root().toSpockCommand()

    def toXmlString(self):
        """
        Converts root obj (MacroNode) to xml string and returns it.

        :return: (etree.Element)
        """

        xmlElement = self.root().toXml()
        return etree.tostring(xmlElement)

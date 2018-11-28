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

"""This module provides base taurus tree item and a base tree model"""

from builtins import object

from taurus.external.qt import Qt
from taurus.core.taurusbasetypes import TaurusElementType
from taurus.core.util.log import Logger, deprecation_decorator

QtQt = Qt.Qt

__all__ = ["TaurusBaseTreeItem", "TaurusBaseModel", "TaurusBaseProxyModel"]

__docformat__ = 'restructuredtext'


class TaurusBaseTreeItem(object):
    """A generic node"""

    DisplayFunc = str

    def __init__(self, model, data, parent=None):
        self._model = model
        self._itemData = data
        self._parentItem = parent
        self._childItems = []
        self._depth = self._calcDepth()

    def itemData(self):
        """The internal itemData object

        :return: (object) object holding the data of this item
        """
        return self._itemData

    def depth(self):
        """Depth of the node in the hierarchy

        :return: (int) the node depth
        """
        return self._depth

    def appendChild(self, child):
        """Adds a new child node

        :param child: (TaurusTreeBaseItem) child to be added
        """
        self._childItems.append(child)

    def child(self, row):
        """Returns the child in the given row

        :return: (TaurusTreeBaseItem) the child node for the given row"""
        return self._childItems[row]

    def childCount(self):
        """Returns the number of childs for this node

        :return: (int) number of childs for this node
        """
        return len(self._childItems)

    def hasChildren(self):
        return len(self._childItems) > 0

    def data(self, index):
        """Returns the data of this node for the given index

        :return: (object) the data for the given index
        """
        return self._itemData[index.column()]

    def icon(self, index):
        return None

    def toolTip(self, index):
        return self.data(index)

    def setData(self, index, data):
        """Sets the node data

        :param data: (object) the data to be associated with this node
        """
        self._itemData = data

    def parent(self):
        """Returns the parent node or None if no parent exists

        :return: (TaurusTreeBaseItem) the parent node
        """
        return self._parentItem

    def row(self):
        """Returns the row for this node

        :return: (int) row number for this node
        """
        if self._parentItem is None:
            return 0
        return self._parentItem._childItems.index(self)

    def _calcDepth(self):
        d = 0
        n = self.parent()
        while n is not None:
            n = n.parent()
            d += 1
        return d

    def display(self):
        """Returns the display string for this node

        :return: (str) the node's display string"""
        if not hasattr(self, "_display"):
            if self._itemData is None:
                return None
            self._display = self.DisplayFunc(self._itemData)
        return self._display

    @deprecation_decorator(alt='display', rel='4.5')
    def qdisplay(self):
        return str(self.display())

    def mimeData(self, index):
        return self.data(index)

    def role(self):
        """Returns the prefered role for the item.
        This implementation returns taurus.core.taurusbasetypes.TaurusElementType.Unknown

        This method should be able to return any kind of python object as long
        as the model that is used is compatible.

        :return: (taurus.core.taurusbasetypes.TaurusElementType) the role in form of element type"""
        return TaurusElementType.Unknown

    def __str__(self):
        return self.display()


class TaurusBaseModel(Qt.QAbstractItemModel, Logger):
    """The base class for all Taurus Qt models."""

    ColumnNames = ()
    ColumnRoles = (),

    DftFont = Qt.QFont("Mono", 8)

    def __init__(self, parent=None, data=None):
        Qt.QAbstractItemModel.__init__(self, parent)
        Logger.__init__(self)
        self._data_src = None
        self._rootItem = None
        self._filters = []
        self._selectables = [self.ColumnRoles[0][-1]]
        self.setDataSource(data)

    def __getattr__(self, name):
        return getattr(self.dataSource(), name)

    def createNewRootItem(self):
        return TaurusBaseTreeItem(self, self.ColumnNames)

    def refresh(self, refresh_source=False):
        self.beginResetModel()
        self._rootItem = self.createNewRootItem()
        self.setupModelData(self.dataSource())
        self.endResetModel()

    def setupModelData(self, data):
        raise NotImplementedError("setupModelData must be implemented "
                                  "in %s" % self.__class__.__name__)

    def roleIcon(self, role):
        raise NotImplementedError("roleIcon must be implemented "
                                  "in %s" % self.__class__.__name__)

    def roleSize(self, role):
        raise NotImplementedError("roleSize must be implemented "
                                  "in %s" % self.__class__.__name__)

    def roleToolTip(self, role):
        raise NotImplementedError("roleToolTip must be implemented "
                                  "in %s" % self.__class__.__name__)

    def setDataSource(self, data_src):
        self._data_src = data_src
        self.refresh()

    def dataSource(self):
        return self._data_src

    def setSelectables(self, seq_elem_types):
        self._selectables = seq_elem_types

    def selectables(self):
        return self._selectables

    def role(self, column, depth=0):
        cr = self.ColumnRoles
        if column == 0:
            return cr[0][depth]
        return self.ColumnRoles[column]

    def columnCount(self, parent=Qt.QModelIndex()):
        return len(self.ColumnRoles)

    def columnIcon(self, column):
        return self.roleIcon(self.role(column))

    def columnToolTip(self, column):
        return self.roleToolTip(self.role(column))

    def columnSize(self, column):
        role = self.role(column)
        s = self.roleSize(role)
        return s

    def pyData(self, index, role=QtQt.DisplayRole):
        if not index.isValid():
            return None

        item = index.internalPointer()

        ret = None
        if role == QtQt.DisplayRole or role == QtQt.EditRole:
            ret = item.data(index)
#        elif role == QtQt.CheckStateRole:
#            data = item.data(index)
#            if type(data) != bool:
#                data = str(data).lower() == 'true'
#            ret = QtQt.Unchecked
#            if data == True:
#                ret = QtQt.Checked
        elif role == QtQt.DecorationRole:
            ret = item.icon(index)
        elif role == QtQt.ToolTipRole:
            ret = item.toolTip(index)
        # elif role == QtQt.SizeHintRole:
        #    ret = self.columnSize(column)
        elif role == QtQt.FontRole:
            ret = self.DftFont
        elif role == QtQt.UserRole:
            ret = item
        return ret

    def data(self, index, role=QtQt.DisplayRole):
        ret = self.pyData(index, role)
        return ret

    def _setData(self, index, qvalue, role=QtQt.EditRole):
        item = index.internalPointer()
        item.setData(index, qvalue)
        return True

    def flags(self, index):
        if not index.isValid():
            return 0

        ret = QtQt.ItemIsEnabled | QtQt.ItemIsDragEnabled

        item = index.internalPointer()
        column, depth = index.column(), item.depth()
        taurus_role = self.role(column, depth)

        if taurus_role in self.selectables():
            ret |= QtQt.ItemIsSelectable
        return ret

    def headerData(self, section, orientation, role=QtQt.DisplayRole):
        ret = None
        if orientation == QtQt.Horizontal:
            if role == QtQt.TextAlignmentRole:
                ret = int(QtQt.AlignLeft | QtQt.AlignVCenter)
            elif role == QtQt.DisplayRole:
                ret = self.ColumnNames[section]
            elif role == QtQt.SizeHintRole:
                ret = Qt.QSize(self.columnSize(section))
                ret.setHeight(24)
            elif role == QtQt.ToolTipRole:
                ret = self.columnToolTip(section)
            elif role == QtQt.DecorationRole:
                ret = self.columnIcon(section)

        return ret

    def index(self, row, column, parent=Qt.QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return Qt.QModelIndex()
        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        return Qt.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return Qt.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem is None or parentItem == self._rootItem:
            return Qt.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=Qt.QModelIndex()):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()
        if parentItem is None:
            return 0
        return parentItem.childCount()

    def hasChildren(self, parent=Qt.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            parentItem = self._rootItem
        else:
            parentItem = parent.internalPointer()

        if parentItem is None:
            return False
        return parentItem.hasChildren()


class TaurusBaseProxyModel(Qt.QSortFilterProxyModel):
    """A taurus base Qt filter & sort model"""

    def __init__(self, parent=None):
        Qt.QSortFilterProxyModel.__init__(self, parent)

        # filter configuration
        self.setFilterCaseSensitivity(QtQt.CaseInsensitive)
        self.setFilterKeyColumn(0)
        self.setFilterRole(QtQt.DisplayRole)

        # sort configuration
        self.setSortCaseSensitivity(QtQt.CaseInsensitive)
        self.setSortRole(QtQt.DisplayRole)

        # general configuration
        self.setDynamicSortFilter(True)

    def __getattr__(self, name):
        return getattr(self.sourceModel(), name)

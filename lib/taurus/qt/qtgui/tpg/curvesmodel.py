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

"""
curvesmodel Model and view for new CurveItem configuration

.. warning:: this is Work-in-progress. The API may change.
             Do not rely on current API of this module
"""
__all__ = ['TaurusCurveItemTableModel', 'TaurusItemConf', 'TaurusItemConfDlg']

import copy

from taurus.external.qt import Qt

import taurus
from taurus.core import TaurusElementType
from taurus.qt.qtcore.mimetypes import (TAURUS_MODEL_LIST_MIME_TYPE,
                                        TAURUS_ATTR_MIME_TYPE)
from taurus.qt.qtgui.util.ui import UILoadable


# columns:
NUMCOLS = 3
X, Y, TITLE = range(NUMCOLS)
SRC_ROLE = Qt.Qt.UserRole + 1


class Component(object):

    def __init__(self, src):
        self.display = ''
        self.icon = Qt.QIcon()
        self.ok = True
        self.processSrc(src)

    def processSrc(self, src):
        """
        processes the src and sets the values of display, icon and ok
        attributes
        """
        if src is None:
            self.display, self.icon, self.ok = '', Qt.QIcon(), True
            return
        src = str(src).strip()
        # empty
        if src == '':
            self.display, self.icon, self.ok = '', Qt.QIcon(), True
            return
        # for taurus attributes
        if taurus.isValidName(src, etypes=[TaurusElementType.Attribute]):
            self.display, self.icon, self.ok = (
                src, Qt.QIcon('logos:taurus.png'), True)
            return

        # if not caught before, it is unsupported
        self.display, self.icon, self.ok = (
            src, Qt.QIcon.fromTheme('dialog-warning'), False)


class TaurusItemConf(object):
    """An object to hold an item of the TaurusCurveItemTableModel"""

    def __init__(self, YModel=None, XModel=None, name=None):
        self.x = Component(XModel)
        self.y = Component(YModel)
        self.xModel = XModel
        self.yModel = YModel
        self.curveLabel = name

    def __repr__(self):
        ret = "TaurusItemConf(xModel='%s', yModel='%s')" % (
            self.xModel, self.yModel)
        return ret


class TaurusCurveItemTableModel(Qt.QAbstractTableModel):
    """ A Qt data model for describing curves"""

    dataChanged = Qt.pyqtSignal('QModelIndex', 'QModelIndex')

    def __init__(self, taurusItems=None):
        super(TaurusCurveItemTableModel, self).__init__()
        self.ncolumns = NUMCOLS
        self.taurusItems = taurusItems

    def dumpData(self):
        return copy.copy(self.taurusItems)

    def rowCount(self, index=Qt.QModelIndex()):
        return len(self.taurusItems)

    def columnCount(self, index=Qt.QModelIndex()):
        return self.ncolumns

    def data(self, index, role=Qt.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return None
        row = index.row()
        column = index.column()
        # Display Role
        if role == Qt.Qt.DisplayRole:
            if column == X:
                return str(self.taurusItems[row].x.display)
            elif column == Y:
                return str(self.taurusItems[row].y.display)
            elif column == TITLE:
                return str(self.taurusItems[row].curveLabel)
            else:
                return None
        elif role == Qt.Qt.DecorationRole:
            if column == X:
                return self.taurusItems[row].x.icon
            elif column == Y:
                return self.taurusItems[row].y.icon
            else:
                return None
        elif role == Qt.Qt.TextColorRole:
            if column == X:
                    Qt.QColor(self.taurusItems[row].x.ok and 'green' or 'red')
            elif column == Y:
                    Qt.QColor(self.taurusItems[row].y.ok and 'green' or 'red')
            else:
                return None
        elif role == SRC_ROLE:
            if column == X:
                return str(self.taurusItems[row].xModel)
            elif column == Y:
                return str(self.taurusItems[row].yModel)
            else:
                return None
        elif role == Qt.Qt.ToolTipRole:
            if column == X:
                return str(self.taurusItems[row].xModel)
            elif column == Y:
                return str(self.taurusItems[row].yModel)
            else:
                return None
        if role == Qt.Qt.EditRole:
            if column == X:
                return str(self.taurusItems[row].xModel)
            elif column == Y:
                return str(self.taurusItems[row].yModel)
            elif column == TITLE:
                return str(self.taurusItems[row].curveLabel)
            else:
                return None
        return None

    def headerData(self, section, orientation, role=Qt.Qt.DisplayRole):
        if role == Qt.Qt.TextAlignmentRole:
            if orientation == Qt.Qt.Horizontal:
                return int(Qt.Qt.AlignLeft | Qt.Qt.AlignVCenter)
            return int(Qt.Qt.AlignRight | Qt.Qt.AlignVCenter)
        if role != Qt.Qt.DisplayRole:
            return None
        # So this is DisplayRole...
        if orientation == Qt.Qt.Horizontal:
            if section == X:
                return "X source"
            elif section == Y:
                return "Y Source"
            elif section == TITLE:
                return "Title"
            return None
        else:
            return str(section + 1)

    def flags(self, index):
        # use this to set the editable flag when fix is selected
        if not index.isValid():
            return Qt.Qt.ItemIsEnabled
        column = index.column()
        if column in (X, Y):
            return Qt.Qt.ItemFlags(Qt.Qt.ItemIsEnabled |
                                   Qt.Qt.ItemIsEditable |
                                   Qt.Qt.ItemIsDragEnabled |
                                   Qt.Qt.ItemIsDropEnabled |
                                   Qt.Qt.ItemIsSelectable
                                   )
        elif column == TITLE:
            return Qt.Qt.ItemFlags(Qt.Qt.ItemIsEnabled |
                                   Qt.Qt.ItemIsEditable |
                                   Qt.Qt.ItemIsDragEnabled
                                   )
        return Qt.Qt.ItemFlags(Qt.Qt.ItemIsEnabled |
                               Qt.Qt.ItemIsEditable |
                               Qt.Qt.ItemIsDragEnabled
                               )

    def setData(self, index, value=None, role=Qt.Qt.EditRole):
        if index.isValid() and (0 <= index.row() < self.rowCount()):
            row = index.row()
            curve = self.taurusItems[row]
            column = index.column()
            if column == X:
                curve.xModel = value
                curve.x.processSrc(value)
            elif column == Y:
                curve.yModel = value
                curve.y.processSrc(value)
            elif column == TITLE:
                curve.curveLabel = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertRows(self, position=None, rows=1, parentindex=None):
        if position is None:
            position = self.rowCount()
        if parentindex is None:
            parentindex = Qt.QModelIndex()
        self.beginInsertRows(parentindex, position, position + rows - 1)
        slice = [TaurusItemConf() for i in range(rows)]
        self.taurusItems = (self.taurusItems[:position] + slice +
                            self.taurusItems[position:]
                            )
        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, parentindex=None):
        if parentindex is None:
            parentindex = Qt.QModelIndex()
        self.beginRemoveRows(parentindex, position, position + rows - 1)
        self.taurusItems = (self.taurusItems[:position] +
                            self.taurusItems[position + rows:]
                            )
        self.endRemoveRows()
        self.reset()
        return True

    def clearAll(self):
        self.removeRows(0, self.rowCount())

    def mimeTypes(self):
        result = list(Qt.QAbstractTableModel.mimeTypes(self))
        result += [TAURUS_ATTR_MIME_TYPE, 'text/plain']
        return result

    def dropMimeData(self, data, action, row, column, parent):
        if row == -1:
            if parent.isValid():
                row = parent.row()
            else:
                row = parent.rowCount()
        if column == -1:
            if parent.isValid():
                column = parent.column()
            else:
                column = parent.columnCount()
        if data.hasFormat(TAURUS_ATTR_MIME_TYPE):
            self.setData(self.index(row, column),
                         value=str(data.data(TAURUS_ATTR_MIME_TYPE)))
            return True
        elif data.hasFormat(TAURUS_MODEL_LIST_MIME_TYPE):
            models = str(data.data(TAURUS_MODEL_LIST_MIME_TYPE)).split()
            if len(models) == 1:
                self.setData(self.index(row, column),
                             value=models[0])
                return True
            else:
                self.insertRows(row, len(models))
                for i, m in enumerate(models):
                    self.setData(self.index(row + i, column),
                                 value=m)
                return True
        elif data.hasText():
            self.setData(self.index(row, column), data.text())
            return True
        return False

    def mimeData(self, indexes):
        mimedata = Qt.QAbstractTableModel.mimeData(self, indexes)
        if len(indexes) == 1:
            #            mimedata.setData(TAURUS_ATTR_MIME_TYPE, data)
            data = self.data(indexes[0], role=SRC_ROLE)
            mimedata.setText(data)
        return mimedata
        # mimedata.setData()


@UILoadable(with_ui='ui')
class TaurusItemConfDlg(Qt.QWidget):
    """ A configuration dialog for creating new CurveItems.

    Provides a TaurusModelBrowser for Taurus models and an editable
    table for the sources and title of data
    """

    dataChanged = Qt.pyqtSignal('QModelIndex', 'QModelIndex')
    applied = Qt.pyqtSignal()

    def __init__(self, parent=None, taurusItemsConf=None, showXcol=True):
        super(TaurusItemConfDlg, self).__init__(parent)
        self.loadUi()
        self._showXcol = showXcol

        if taurusItemsConf is None:
            taurusItemsConf = [
                TaurusItemConf(YModel=None, XModel=None, name=None)
            ]

        self.ui.tangoTree.setButtonsPos(Qt.Qt.RightToolBarArea)

        # @todo: The action for this button is not yet implemented
        self.ui.reloadBT.setEnabled(False)

        self.model = TaurusCurveItemTableModel(taurusItemsConf)

        table = self.ui.curvesTable
        table.setModel(self.model)
        table.setColumnHidden(X, not self._showXcol)

        # -------------------------------------------------------------------
        # I get "UnboundLocalError: local variable 'taurus' referenced before
        # assignment" if I don't import taurus again here
        # TODO: check if this workaround is really needed
        import taurus
        # -------------------------------------------------------------------

        try:  # TODO: Tango-centric!
            host = taurus.Factory('tango').getAuthority().getFullName()
            self.ui.tangoTree.setModel(host)
        except Exception as e:
            taurus.info('Cannot populate Tango Tree: %r', e)

        # Connections
        self.ui.applyBT.clicked.connect(self.onApply)
        self.ui.reloadBT.clicked.connect(self.onReload)
        self.ui.cancelBT.clicked.connect(self.close)
        self.ui.tangoTree.addModels.connect(self.onModelsAdded)
        self.ui.curvesTable.customContextMenuRequested.connect(
            self.onTableContextMenu)

    def onTableContextMenu(self, pos):
        index = self.ui.curvesTable.indexAt(pos)
        row = index.row()
        menu = Qt.QMenu(self.ui.curvesTable)
        if row >= 0:
            removeThisAction = menu.addAction(Qt.QIcon.fromTheme(
                'list-remove'), 'Remove this curve', self._onRemoveThisAction)
        removeAllAction = menu.addAction(Qt.QIcon.fromTheme(
            'edit-clear'), 'Clear all', self.model.clearAll)
        addRowAction = menu.addAction(Qt.QIcon.fromTheme(
            'list-add'), 'Add new row', self.model.insertRows)

        menu.exec_(Qt.QCursor.pos())

    def _onRemoveThisAction(self):
        row = self.ui.curvesTable.currentIndex().row()
        self.model.removeRows(row)

    def onModelsAdded(self, models):
        nmodels = len(models)
        rowcount = self.model.rowCount()
        self.model.insertRows(rowcount, nmodels)
        for i, m in enumerate(models):
            self.model.setData(self.model.index(
                rowcount + i, Y), value=m)
            title = self.model.data(self.model.index(
                rowcount + i, Y))  # the display data

            # print type(title), title
            self.model.setData(self.model.index(
                rowcount + i, TITLE), value=title)

    def getItemConfs(self):
        return self.model.dumpData()

    @staticmethod
    def showDlg(parent=None, taurusItemConf=None, showXCol=True):
        """
        Static method that launches a modal dialog containing a
        TaurusItemConfDlg.

        For the parameters, see :class:`TaurusItemConfDlg`

        :return: (list,bool) Returns a models,ok tuple
                 models is a list of models.
                 ok is True if the dialog was accepted (by clicking on the
                 "update" button) and False otherwise
        """
        dlg = Qt.QDialog(parent)
        dlg.setWindowTitle('Curves Selection')
        layout = Qt.QVBoxLayout()
        w = TaurusItemConfDlg(parent=parent, taurusItemsConf=taurusItemConf,
                              showXcol=showXCol)
        layout.addWidget(w)
        dlg.setLayout(layout)
        w.applied.connect(dlg.accept)
        w.ui.cancelBT.clicked.connect(dlg.close)
        dlg.exec_()
        return w.getItemConfs(), (dlg.result() == dlg.Accepted)

    def onApply(self):
        self.applied.emit()

    def onReload(self):
        # TODO
        print "RELOAD!!! (todo)"


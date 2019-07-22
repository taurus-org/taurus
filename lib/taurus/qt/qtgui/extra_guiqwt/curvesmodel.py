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
"""

from __future__ import print_function
from builtins import next
from builtins import str
from builtins import bytes
from builtins import range
from builtins import object

__all__ = ['TaurusCurveItemTableModel', 'CurveItemConf', 'CurveItemConfDlg']

#raise UnimplementedError('Under Construction!')

import copy

from taurus.external.qt import Qt
from guiqwt.styles import CurveParam, AxesParam, update_style_attr
from guiqwt.builder import make

import taurus
from taurus.core.taurusexception import TaurusException
from taurus.qt.qtcore.mimetypes import TAURUS_MODEL_LIST_MIME_TYPE, TAURUS_ATTR_MIME_TYPE
from taurus.qt.qtgui.util.ui import UILoadable
from taurus.qt.qtgui.extra_guiqwt.styles import TaurusCurveParam

import guiqwt
__guiqwt_version = list(map(int, guiqwt.__version__.split('.')[:3]))
if __guiqwt_version <= [2, 3, 1]:
    import taurus.external.qt.Qwt5 as qwt
else:
    import qwt

AXIS_ID2NAME = {qwt.QwtPlot.yLeft: 'left', qwt.QwtPlot.yRight: 'right',
                qwt.QwtPlot.xBottom: 'bottom', qwt.QwtPlot.xTop: 'top'}

# set some named constants
# columns:
NUMCOLS = 3
X, Y, TITLE = list(range(NUMCOLS))
SRC_ROLE = Qt.Qt.UserRole + 1


class Component(object):

    def __init__(self, src):
        self.display = ''
        self.icon = Qt.QIcon()
        self.ok = True
        self.processSrc(src)

    def processSrc(self, src):
        '''processes the src and sets the values of display, icon and ok attributes'''
        if src is None:
            self.display, self.icon, self.ok = '(Use indices)', Qt.QIcon(
            ), True
            return
        src = str(src).strip()
        # empty
        if src == '':
            self.display, self.icon, self.ok = '(Use indices)', Qt.QIcon(
            ), True
            return
        # for formulas
        if src.startswith('='):
            #@todo: evaluate/validate the expression
            self.display, self.icon, self.ok = src[
                1:].strip(), Qt.QIcon.fromTheme('accessories-calculator'), True
            return
        # for tango attributes
        try:
            attr = taurus.Attribute(src)
            dev = attr.getParentObj()
        except TaurusException:
            self.display, self.icon, self.ok = src, Qt.QIcon.fromTheme(
                'dialog-warning'), False
            return
        if not dev.isValidDev():
            self.display, self.icon, self.ok = src, Qt.QIcon.fromTheme(
                'network-error'), False
            return
        self.display, self.icon, self.ok = attr.getSimpleName(),\
                                           Qt.QIcon('logos:taurus.png'), True


class CurveItemConf(object):

    def __init__(self, taurusparam=None, curveparam=None, axesparam=None):
        if taurusparam is None:
            taurusparam = TaurusCurveParam()
        self.taurusparam = taurusparam
        if curveparam is None:
            curveparam = CurveParam()
            style = next(make.style)  # cycle through colors and linestyles
            update_style_attr(style, curveparam)
            curveparam.line.width = 2
        self.curveparam = curveparam
        self.axesparam = axesparam
        self.x = Component(taurusparam.xModel)
        self.y = Component(taurusparam.yModel)
        if not self.curveparam.label:
            self.curveparam.label = taurusparam.xModel

    def __repr__(self):
        ret = "CurveItemConf(xModel='%s', yModel='%s')" % (
            self.taurusparam.xModel, self.taurusparam.yModel)
        return ret

    @staticmethod
    def fromTaurusCurveItem(item):
        plot = item.plot()
        if plot is not None:
            axesparam = AxesParam()
            axesparam.update_param(item)
        return CurveItemConf(taurusparam=item.taurusparam, curveparam=item.curveparam, axesparam=axesparam)

    @staticmethod
    def fromAny(obj):
        '''return a CurveItemConf from whatever given in input (if possible).
        Raises ValueError if not possible'''
        if isinstance(obj, CurveItemConf):
            return copy.deepcopy(obj)
        try:
            return CurveItemConf.fromTaurusCurveItem(obj)
        except:
            raise
        try:
            return CurveItemConf(*obj)
        except:
            pass
        raise ValueError('Cannot convert %s into a CurveItemConf' % repr(obj))


class TaurusCurveItemTableModel(Qt.QAbstractTableModel):
    ''' A Qt data model for describing curves
    '''

    dataChanged = Qt.pyqtSignal('QModelIndex', 'QModelIndex')

    def __init__(self, curves=None):
        if curves is None:
            curves = []
        curves = [CurveItemConf.fromAny(c) for c in curves]  # convert curves
        super(TaurusCurveItemTableModel, self).__init__()
        self.ncolumns = NUMCOLS
        self.curves = curves

    def dumpData(self):
        return copy.deepcopy(self.curves)

    def rowCount(self, index=Qt.QModelIndex()):
        return len(self.curves)

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
                return str(self.curves[row].x.display)
            elif column == Y:
                return str(self.curves[row].y.display)
            elif column == TITLE:
                return str(self.curves[row].curveparam.label)
            else:
                return None
        elif role == Qt.Qt.DecorationRole:
            if column == X:
                return self.curves[row].x.icon
            elif column == Y:
                return self.curves[row].y.icon
            else:
                return None
        elif role == Qt.Qt.TextColorRole:
            if column == X:
                Qt.QColor(self.curves[row].x.ok and 'green' or 'red')
            elif column == Y:
                Qt.QColor(self.curves[row].y.ok and 'green' or 'red')
            else:
                return None
        elif role == SRC_ROLE:
            if column == X:
                return str(self.curves[row].taurusparam.xModel)
            elif column == Y:
                return str(self.curves[row].taurusparam.yModel)
            else:
                return None
        elif role == Qt.Qt.ToolTipRole:
            if column == X:
                return str(self.curves[row].taurusparam.xModel)
            elif column == Y:
                return str(self.curves[row].taurusparam.yModel)
            else:
                return None
        if role == Qt.Qt.EditRole:
            if column == X:
                return str(self.curves[row].taurusparam.xModel)
            elif column == Y:
                return str(self.curves[row].taurusparam.yModel)
            elif column == TITLE:
                return str(self.curves[row].curveparam.label)
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

    def flags(self, index):  # use this to set the editable flag when fix is selected
        if not index.isValid():
            return Qt.Qt.ItemIsEnabled
        column = index.column()
        if column in (X, Y):
            return Qt.Qt.ItemFlags(Qt.Qt.ItemIsEnabled | Qt.Qt.ItemIsEditable | Qt.Qt.ItemIsDragEnabled | Qt.Qt.ItemIsDropEnabled | Qt.Qt.ItemIsSelectable)
        elif column == TITLE:
            return Qt.Qt.ItemFlags(Qt.Qt.ItemIsEnabled | Qt.Qt.ItemIsEditable | Qt.Qt.ItemIsDragEnabled)
        return Qt.Qt.ItemFlags(Qt.Qt.ItemIsEnabled | Qt.Qt.ItemIsEditable | Qt.Qt.ItemIsDragEnabled)

    def setData(self, index, value=None, role=Qt.Qt.EditRole):
        if index.isValid() and (0 <= index.row() < self.rowCount()):
            row = index.row()
            curve = self.curves[row]
            column = index.column()
            if column == X:
                curve.taurusparam.xModel = value
                curve.x.processSrc(value)
            elif column == Y:
                curve.taurusparam.yModel = value
                curve.y.processSrc(value)
            elif column == TITLE:
                curve.curveparam.label = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertRows(self, position=None, rows=1, parentindex=None):
        if position is None:
            position = self.rowCount()
        if parentindex is None:
            parentindex = Qt.QModelIndex()
        self.beginInsertRows(parentindex, position, position + rows - 1)
        slice = [CurveItemConf() for i in range(rows)]
        self.curves = self.curves[:position] + slice + self.curves[position:]
        self.endInsertRows()
        return True

    def removeRows(self, position, rows=1, parentindex=None):
        if parentindex is None:
            parentindex = Qt.QModelIndex()
        self.beginResetModel()
        self.beginRemoveRows(parentindex, position, position + rows - 1)
        self.curves = self.curves[:position] + self.curves[position + rows:]
        self.endRemoveRows()
        self.endResetModel()
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
            model = bytes(data.data(TAURUS_ATTR_MIME_TYPE)).decode("utf-8")
            self.setData(self.index(row, column), value=model)
            return True
        elif data.hasFormat(TAURUS_MODEL_LIST_MIME_TYPE):
            d = bytes(data.data(TAURUS_MODEL_LIST_MIME_TYPE))
            models = d.decode("utf-8").split()
            if len(models) == 1:
                self.setData(self.index(row, column), value=models[0])
                return True
            else:
                self.insertRows(row, len(models))
                for i, m in enumerate(models):
                    self.setData(self.index(row + i, column), value=m)
                return True
        elif data.hasText():
            self.setData(self.index(row, column), data.text())
            return True
        return False

    def mimeData(self, indexes):
        mimedata = Qt.QAbstractTableModel.mimeData(self, indexes)
        if len(indexes) == 1:
            data = self.data(indexes[0], role=SRC_ROLE)
            # mimedata.setData(TAURUS_ATTR_MIME_TYPE, data)
            mimedata.setText(data)
        return mimedata
        # mimedata.setData()


@UILoadable(with_ui='ui')
class CurveItemConfDlg(Qt.QWidget):
    ''' A configuration dialog for creating new CurveItems.

    Provides a browser for Taurus models and an editable table for the sources
    and title of data
    '''

    dataChanged = Qt.pyqtSignal('QModelIndex', 'QModelIndex')
    applied = Qt.pyqtSignal()

    def __init__(self, parent=None, curves=None, showXcol=True):
        super(CurveItemConfDlg, self).__init__(parent)
        self.loadUi()
        self._showXcol = showXcol

        if curves is None:
            curves = [CurveItemConf()]
        # add the NeXusWidget if extra_nexus is available
        try:
            from taurus.qt.qtgui.extra_nexus import TaurusNeXusBrowser
            nexusWidget = TaurusNeXusBrowser()
            self.ui.tabWidget.addTab(nexusWidget, 'NeXus')
        except:
            import taurus.core.util.log
            _logger = taurus.core.util.log.Logger('CurveItemConfDlg')
            _logger.warning('TaurusNeXusBrowser not available')
            self.traceback()

        self.ui.tangoTree.setButtonsPos(Qt.Qt.RightToolBarArea)

        # @todo: The action for this button is not yet implemented
        self.ui.reloadBT.setEnabled(False)

        self.model = TaurusCurveItemTableModel(curves)

        table = self.ui.curvesTable
        table.setModel(self.model)
        table.setColumnHidden(X, not self._showXcol)

#        #adjust the column widths
#        table.resizeColumnsToContents()
#        availableSpace = table.viewport().width()
#        for col in xrange(self.model.columnCount()):
#            availableSpace -= table.columnWidth(col)
#        if availableSpace > 0:
#            extraSpace = availableSpace / self.model.columnCount()
#            for col in xrange(self.model.columnCount()):
#                table.setColumnWidth(col, table.columnWidth(col)+extraSpace)

        # host

        import taurus  # @todo: I get "UnboundLocalError: local variable 'taurus' referenced before assignment" if I don't import taurus again here ????
        host = taurus.Authority().getNormalName()
        self.ui.tangoTree.setModel(host)

        # Connections
        self.ui.applyBT.clicked.connect(self.onApply)
        self.ui.reloadBT.clicked.connect(self.onReload)
        self.ui.cancelBT.clicked.connect(self.close)
        self.ui.tangoTree.addModels.connect(self.onModelsAdded)
        self.ui.curvesTable.customContextMenuRequested.connect(self.onTableContextMenu)

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
        if row >= 0:
            editParsAction = menu.addAction(Qt.QIcon.fromTheme(
                'preferences-system'), 'Edit parameters of this curve...', self._onEditParsAction)

        menu.exec_(Qt.QCursor.pos())

    def _onRemoveThisAction(self):
        row = self.ui.curvesTable.currentIndex().row()
        self.model.removeRows(row)

    def _onEditParsAction(self):
        row = self.ui.curvesTable.currentIndex().row()
        if row >= 0:
            c = self.model.curves[row]
            params = [p for p in (c.curveparam, c.axesparam,
                                  c.taurusparam) if p is not None]
            if params:
                from guidata.dataset.datatypes import DataSetGroup
                group = DataSetGroup(
                    params, "Parameters for curve %s" % c.curveparam.label)
                group.edit()
                c.x.processSrc(c.taurusparam.xModel)
                c.y.processSrc(c.taurusparam.yModel)
                self.dataChanged.emit(
                        self.model.index(row, 0),
                        self.model.index(row, self.model.rowCount() - 1)
                )

    def onModelsAdded(self, models):
        nmodels = len(models)
        rowcount = self.model.rowCount()
        self.model.insertRows(rowcount, nmodels)
        for i, m in enumerate(models):
            self.model.setData(self.model.index(rowcount + i, Y), value=m)
            title = self.model.data(self.model.index(
                rowcount + i, Y))  # the display data
            self.model.setData(self.model.index(
                rowcount + i, TITLE), value=title)

    def getCurveItemConfs(self):
        return self.model.dumpData()

    @staticmethod
    def showDlg(parent=None, curves=None):
        '''Static method that launches a modal dialog containing a CurveItemConfDlg

        :param parent: (QObject) parent for the dialog

        :return: (list,bool or QMimeData,bool) Returns a models,ok tuple. models can be
                 either a list of models or a QMimeData object, depending on
                 `asMimeData`. ok is True if the dialog was accepted (by
                 clicking on the "update" button) and False otherwise
        '''
        dlg = Qt.QDialog(parent)
        dlg.setWindowTitle('Curves Selection')
        layout = Qt.QVBoxLayout()
        w = CurveItemConfDlg(parent=parent, curves=curves)
        layout.addWidget(w)
        dlg.setLayout(layout)
        w.applied.connect(dlg.accept)
        w.ui.cancelBT.clicked.connect(dlg.close)
        dlg.exec_()
        return w.getCurveItemConfs(), (dlg.result() == dlg.Accepted)

    def onApply(self):
        self.applied.emit()

    def onReload(self):
        print("RELOAD!!! (todo)")


#
#
# def test2():
#    from taurus.qt.qtgui.application import TaurusApplication
#    app = TaurusApplication(app_name="CurvesSelection", app_version=taurus.Release.version)
#
#    print CurveItemConfDlg.showDlg(curves= curves)
#
#    sys.exit()
#
#
# if __name__ == "__main__":
#    import sys
#    test2()

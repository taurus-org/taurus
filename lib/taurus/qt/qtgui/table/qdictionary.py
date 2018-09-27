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

"""This module provides basic python dictionary/list editor widgets"""
from __future__ import print_function

import sys
from future.utils import string_types

from taurus.core.util.containers import SortedDict
from taurus.external.qt import Qt
from taurus.qt.qtgui.container import TaurusBaseContainer, TaurusWidget
from taurus.qt.qtcore.util.properties import join, djoin


__all__ = ["QDictionaryEditor", "QListEditor"]

__docformat__ = 'restructuredtext'

###############################################################################
# Methods borrowed from fandango modules


def isString(seq):
    if isinstance(seq, string_types):
        return True  # It matches most python str-like classes
    if any(s in str(type(seq)).lower() for s in ('vector', 'array', 'list',)):
        return False
    if 'qstring' == str(type(seq)).lower():
        return True  # It matches QString
    return False


def isSequence(seq, INCLUDE_GENERATORS=True):
    """ It excludes Strings, dictionaries but includes generators"""
    if any(isinstance(seq, t) for t in (list, set, tuple)):
        return True
    if isString(seq):
        return False
    if hasattr(seq, 'items'):
        return False
    if INCLUDE_GENERATORS:
        if hasattr(seq, '__iter__'):
            return True
    elif hasattr(seq, '__len__'):
        return True
    return False


def isDictionary(seq):
    """ It includes dicts and also nested lists """
    if isinstance(seq, dict):
        return True
    if hasattr(seq, 'items') or hasattr(seq, 'iteritems'):
        return True
    if seq and isSequence(seq) and isSequence(seq[0]):
        if seq[0] and not isSequence(seq[0][0]):
            return True  # First element of tuple must be hashable
    return False


def dict2array(dct):
    """ Converts a dictionary in a table of data, lists are unnested columns """
    data, table = {}, []
    data['nrows'], data['ncols'] = 0, 2 if isDictionary(dct) else 1

    def expand(d, level):  # ,nrows=nrows,ncols=ncols):
        # self.debug('\texpand(%s(%s),%s)'%(type(d),d,level))
        items = list(d.items()) if isinstance(d, SortedDict) else sorted(
            list(d.items()) if hasattr(d, 'items') else d)
        for k, v in items:
            zero = data['nrows']
            data[(data['nrows'], level)] = k
            if isDictionary(v):
                data['ncols'] += 1
                expand(v, level + 1)
            else:
                if not isSequence(v):
                    v = [v]
                for t in v:
                    data[(data['nrows'], level + 1)] = t
                    data['nrows'] += 1
            #for i in range(zero+1,nrows): data[(i,level)] = None
    expand(dct, 0)
    [table.append([]) for r in range(data.pop('nrows'))]
    [table[r].append(None) for c in range(data.pop('ncols'))
     for r in range(len(table))]
    for coord, value in data.items():
        table[coord[0]][coord[1]] = value
    return table


def array2dict(table):
    """ Converts a table in a dictionary of left-to-right nested date, unnested columns are lists"""
    nrows, ncols = len(table), len(table[0])
    r, c = 0, 0

    def expand(r, c, end):
        print('expand(%s,%s,%s)' % (r, c, end))
        i0, t0 = r, table[r][c]
        if not t0:
            return t0
        if c + 1 < ncols and (table[r][c + 1] or not c):
            d = {}
            keys = []
            new_end = r + 1
            for i in range(r + 1, end + 1):
                t = table[i][c] if i < end else None
                if t or i >= end:
                    # start,name,stop for each key
                    keys.append((i0, t0, new_end))
                    t0, i0 = t, i
                new_end = i + 1
            for i, key, new_end in keys:
                nd = expand(i, c + 1, new_end)
                d[key] = nd if key not in d else djoin(d.get(key), nd)
            print('expand(%s to %s,%s): %s' % (r, end, c, d))
            return d
        else:
            d = [table[i][c] for i in range(r, end)]
            print('expand(%s to %s,%s): %s' % (r, end, c, d))
            return d
    data = expand(0, 0, nrows)
    return data

###############################################################################


class QBaseDictionaryEditor(Qt.QDialog, TaurusBaseContainer):

    def __init__(self, parent=None, designMode=None, title=None):
        self.data = {}  # An {(x,y):value} array
        self.title = title
        self.dctmodel = SortedDict()
        self.callback = None
        self.call__init__wo_kw(Qt.QDialog, parent)
        self.call__init__(TaurusBaseContainer, type(
            self).__name__, designMode=designMode)  # defineStyle called from here

    @classmethod
    def main(klass, args=None, title='', modal=False, callback=None):
        dialog = klass()
        dialog.setModal(modal)
        dialog.setCallback(callback)
        dialog.setModifiableByUser(True)
        dialog.setWindowTitle(title or klass.title or klass.__name__)
        if args:
            dialog.setModel(args)  # [0] if isSequence(args) else args)
        dialog.show()
        return dialog

    def defineStyle(self):
        self.info('QBaseDictionaryEditor.defineStyle()')
        # self.setWindowTitle('DictionaryEditor')
        self.label = Qt.QLabel(
            'Dictionary as a nested tree: {key1:[val1,val2],key2:[val3]')
        #self.value = Qt.QLabel()
        self.table = Qt.QTableWidget()  # TaurusBaseTable()
        self.table.horizontalHeader().setStretchLastSection(True)
        # self.table.verticalHeader().setStretchLastSection(True)
        self.baccept = Qt.QPushButton('Apply')
        self.bcancel = Qt.QPushButton('Cancel')
        self.baddColumn = Qt.QPushButton()
        self.baddRow = Qt.QPushButton()
        [(b.setFixedSize(Qt.QSize(20, 20)), b.setIcon(Qt.Qicon(
            'designer:plus.png'))) for b in (self.baddColumn, self.baddRow)]
        self.setLayout(Qt.QGridLayout())
        self.layout().addWidget(self.label, 0, 0, 1, 5)
        # self.layout().addWidget(self.value,1,0,1,3)
        self.layout().addWidget(self.baddColumn, 2, 5, 1, 1)
        self.layout().addWidget(self.table, 2, 0, 5, 5)
        self.layout().addWidget(self.baddRow, 7, 0, 1, 1)
        self.layout().addWidget(self.baccept, 8, 3, 1, 1)
        self.layout().addWidget(self.bcancel, 8, 4, 1, 1)
        self.baccept.clicked.connect(self.save)
        self.bcancel.clicked.connect(self.close)
        self.baddRow.clicked.connect(self.addRow)
        self.baddColumn.clicked.connect(self.addColumn)
        self.reject.connect(self.close)

    def addRow(self):
        self.table.setRowCount(self.table.rowCount() + 1)
        self.table.resizeRowsToContents()
        self.table.update()

    def addColumn(self):
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setColumnCount(self.table.columnCount() + 1)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.update()

    def setCallback(self, callback):
        self.callback = callback

    def getCellText(self, row, column):
        if row >= self.table.rowCount() or column >= self.table.columnCount():
            v = None
        else:
            i = self.table.item(row, column)
            if i is None:
                v = i
            else:
                v = str(i.text()).strip()
        self.debug('getCellText(%s,%s): %s' % (row, column, v))
        return v

    def setCellText(self, row, column, value, bold=False, italic=False):
        i = self.table.item(row, column) or Qt.QTableWidgetItem()
        i.setText(str(value if value is not None else ''))
        if bold or italic:
            f = i.font()
            if bold:
                f.setBold(True)
            if italic:
                f.setItalic(True)
            i.setFont(f)
        self.table.setItem(row, column, i)

    def setModel(self, model):
        raise Exception('setModel(self,model)!')

    def updateStyle(self):
        raise Exception('updateStyle(self)!')

    def getValues(self):
        raise Exception('getValues(self)!')

    def save(self):
        raise Exception('save(self)!')

###############################################################################


class QDictionaryEditor(QBaseDictionaryEditor):

    def setModel(self, model):
        self.info('DictionaryEditor.setModel(%s(%s))' % (type(model), model))
        self.dctmodel = eval(model) if isString(model) else model
        # self.updateStyle() called from the property setter
        TaurusBaseContainer.setModel(self, model)

    def getModelClass(self):
        return dict

    def updateStyle(self):
        # self.value.setText(str(self.dctmodel))
        data = dict2array(self.dctmodel)
        self.nrows, self.ncols = len(data), len(data[0])
        self.info(data)
        self.table.setRowCount(self.nrows)
        self.table.setColumnCount(self.ncols)
        for r in range(self.nrows):
            for c in range(self.ncols):
                self.setCellText(r, c, data[r][c],
                                 bold=(not c), italic=(c == 1))
        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()
        self.update()

    def getValues(self):
        nrows, ncols = self.table.rowCount(), self.table.columnCount()
        table = [[self.getCellText(r, c) for c in range(ncols)]
                 for r in range(nrows)]
        self.data = array2dict(table)  # It returns a SortedDict
        self.info('getValues(): %s' % str(self.data))
        return self.data

    def save(self):
        self.getValues()
        self.info('DictionaryEditor.save(): %s' % self.data)
        if self.callback:
            self.callback(self.data)
        elif self.dctmodel is None:
            self.dctmodel = self.data
        else:  # Overwriting dctmodel
            self.dctmodel.clear()
            self.dctmodel.update(self.data)
        if self.callback:
            self.callback(self.data)  # A SortedDict is passed here
        self.updateStyle()

###############################################################################


class QListEditor(QBaseDictionaryEditor):

    def defineStyle(self):
        QBaseDictionaryEditor.defineStyle(self)
        self.table.setColumnCount(1)
        self.baddColumn.hide()

    def setModel(self, model):
        self.info('DictionaryEditor.setModel(%s(%s))' % (type(model), model))
        if isString(model):
            try:
                self.dctmodel = list(eval(model)) if any(
                    c in model for c in ('{', '[', '(')) else [model]
            except:
                self.dctmodel = [model]
        else:
            self.dctmodel = model
        # self.updateStyle() called from the property setter
        TaurusBaseContainer.setModel(self, model)

    def getModelClass(self):
        return list

    def updateStyle(self):
        # self.value.setText(str(self.dctmodel))
        data = list(self.dctmodel)
        self.nrows, self.ncols = len(data), 1
        self.table.setRowCount(self.nrows)
        self.table.setColumnCount(self.ncols)
        for r in range(self.nrows):
            self.setCellText(r, 0, data[r])
        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.update()

    def getValues(self):
        nrows = self.table.rowCount()
        self.data = [self.getCellText(r, 0)for r in range(nrows)]
        return self.data

    def save(self):
        self.getValues()
        self.info('DictionaryEditor.save(%s(%s)): %s' %
                  (type(self.data), self.data, self.callback))
        if self.callback:
            self.callback(self.data)
        elif self.dctmodel is None:
            self.dctmodel = self.data
        else:  # Overwriting dctmodel
            if isSequence(self.dctmodel):
                while len(self.dctmodel):
                    self.dctmodel.pop(0)
                self.dctmodel.extend(self.data)
            elif isDictionary(self.dctmodel):
                self.dctmodel.clear()
                self.dctmodel = djoin(self.dctmodel, self.data)
        return self.data


###############################################################################

def prepare():
    from taurus.qt.qtgui.application import TaurusApplication
    app = TaurusApplication(app_name='DictionaryEditor')
    args = app.get_command_line_args()
    return app, args

if __name__ == '__main__':
    app, args = prepare()
    dialog = QDictionaryEditor.main(args)
    sys.exit(app.exec_())

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

"""This module provides Qt table widgets which display logging messages from the
python :mod:`logging` module"""

__all__ = ["QLoggingTableModel", "QLoggingTable", "QLoggingWidget"]

__docformat__ = 'restructuredtext'

import operator
import logging
import datetime
from taurus.qt import Qt

import taurus.core.util
from taurus.qt.qtgui.resource import getIcon, getThemeIcon

def getBrushForLevel(level):
    if level <= taurus.Trace      : return Qt.QBrush(Qt.Qt.lightGray), Qt.QBrush(Qt.Qt.black)
    elif level <= taurus.Debug    : return Qt.QBrush(Qt.Qt.green), Qt.QBrush(Qt.Qt.black)
    elif level <= taurus.Info     : return Qt.QBrush(Qt.Qt.blue), Qt.QBrush(Qt.Qt.white)
    elif level <= taurus.Warning  : return Qt.QBrush(Qt.QColor(255,165,0)), Qt.QBrush(Qt.Qt.black)
    elif level <= taurus.Error    : return Qt.QBrush(Qt.Qt.red), Qt.QBrush(Qt.Qt.black)
    elif level <= taurus.Critical : return Qt.QBrush(Qt.QColor(160,32,240)), Qt.QBrush(Qt.Qt.white)
    return Qt.QBrush(Qt.Qt.FDiagPattern), Qt.QBrush(Qt.Qt.black)

LEVEL, TYPE, TIME, MSG, NAME, THREAD, LOCALT = range(7)
HORIZ_HEADER = 'Level','Type','Time','Message','Object','Thread','App time'

class QLoggingTableModel(Qt.QAbstractTableModel, logging.Handler):
    
    DftOddRowBrush = Qt.QBrush(Qt.QColor(220,220,220)), Qt.QBrush(Qt.Qt.black)
    DftEvenRowBrush = Qt.QBrush(Qt.QColor(255,255,255)), Qt.QBrush(Qt.Qt.black)
    DftFont = Qt.QFont("Mono", 8)
    DftColSize = Qt.QSize(90, 20), Qt.QSize(50, 20), Qt.QSize(90, 20), \
                 Qt.QSize(250, 20), Qt.QSize(130, 20), Qt.QSize(90, 20), \
                 Qt.QSize(90, 20)
    
    def __init__(self, capacity=500000, freq=0.25):
        super(Qt.QAbstractTableModel, self).__init__()
        logging.Handler.__init__(self)
        self._capacity = capacity
        self._records = []
        self._accumulated_records = []
        taurus.core.util.Logger.addRootLogHandler(self)
        self.startTimer(freq*1000)

    # ---------------------------------
    # Qt.QAbstractTableModel overwrite
    # ---------------------------------
    
    def sort(self, column, order = Qt.Qt.AscendingOrder):
        if column == LEVEL:
            f = lambda a,b: cmp(a.levelno,b.levelno)
        elif column == TYPE:
            def f(a,b):
                if not operator.isMappingType(a) or not operator.isMappingType(b):
                    return 0
                return cmp(a.args.get('type','taurus'), b.args.get('type','taurus'))
        elif column == TIME:
            f = lambda a,b: cmp(a.created,b.created)
        elif column == MSG:
            f = lambda a,b: cmp(a.msg,b.msg)
        elif column == NAME:
            f = lambda a,b: cmp(a.name,b.name)
        elif column == THREAD:
            f = lambda a,b: cmp(a.threadName,b.threadName)
        elif column == LOCALT:
            f = lambda a,b: cmp(a.relativeCreated,b.relativeCreated)
        self._records = sorted(self._records, cmp=f,reverse= order == Qt.Qt.DescendingOrder)
        #self.reset()
    
    def rowCount(self, index=Qt.QModelIndex()):
        return len(self._records)

    def columnCount(self, index=Qt.QModelIndex()):
        return 7
    
    def data(self, index, role=Qt.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._records)):
            return Qt.QVariant()
        record = self._records[index.row()]
        column = index.column()
        if role == Qt.Qt.DisplayRole:
            if column == LEVEL:
                return Qt.QVariant(record.levelname)
            elif column == TYPE:
                try:
                    t = record.args['type']
                except:
                    t = 'taurus'
                return Qt.QVariant(t)
            elif column == TIME:
                dt = datetime.datetime.fromtimestamp(record.created)
                return Qt.QVariant(str(dt))
                #return Qt.QVariant(dt.strftime("%H:%M:%S"))
            elif column == MSG:
                return Qt.QVariant(record.getMessage())
            elif column == NAME:
                return Qt.QVariant(record.name)
            elif column == THREAD:
                return Qt.QVariant(record.threadName)
            elif column == LOCALT:
                dt = datetime.datetime.fromtimestamp(record.relativeCreated)
                return Qt.QVariant(dt.strftime("%H:%M:%S"))
        elif role == Qt.Qt.TextAlignmentRole:
            if column in (LEVEL, MSG):
                return Qt.QVariant(Qt.Qt.AlignLeft|Qt.Qt.AlignVCenter)
            return Qt.QVariant(Qt.Qt.AlignRight|Qt.Qt.AlignVCenter)
        elif role == Qt.Qt.BackgroundRole:
            if column == LEVEL:
                bg = getBrushForLevel(record.levelno)[0]
            else:
                if index.row() % 2:
                    bg = self.DftOddRowBrush[0]
                else:
                    bg = self.DftEvenRowBrush[0]
            return Qt.QVariant(bg)
        elif role == Qt.Qt.ForegroundRole:
            if column == LEVEL:
                fg = getBrushForLevel(record.levelno)[1]
            else:
                if index.row() % 2:
                    fg = self.DftOddRowBrush[1]
                else:
                    fg = self.DftEvenRowBrush[1]
            return Qt.QVariant(fg)
        elif role == Qt.Qt.ToolTipRole:
            if column == LEVEL:
                return Qt.QVariant(record.levelname)
            elif column == TYPE:
                return Qt.QVariant("log type")
            elif column == TIME:
                dt = datetime.datetime.fromtimestamp(record.created)
                return Qt.QVariant(str(dt))
            elif column == MSG:
                return Qt.QVariant("log message")
            elif column == NAME:
                return Qt.QVariant("object who recorded the log")
            elif column == THREAD:
                return Qt.QVariant("%s [%s]" % (record.processName, record.threadName))
            elif column == LOCALT:
                dt = datetime.datetime.fromtimestamp(record.relativeCreated)
                return Qt.QVariant(str(dt))
        elif role == Qt.Qt.SizeHintRole:
            return self._getSizeHint(column)
        #elif role == Qt.Qt.StatusTipRole:
        #elif role == Qt.Qt.CheckStateRole:
        elif role == Qt.Qt.FontRole:
            return Qt.QVariant(self.DftFont)
        return Qt.QVariant()

    def _getSizeHint(self, column):
        return Qt.QVariant(QLoggingTableModel.DftColSize[column])

    def headerData(self, section, orientation, role=Qt.Qt.DisplayRole):
        if role == Qt.Qt.TextAlignmentRole:
            if orientation == Qt.Qt.Horizontal:
                return Qt.QVariant(int(Qt.Qt.AlignLeft | Qt.Qt.AlignVCenter))
            return Qt.QVariant(int(Qt.Qt.AlignRight | Qt.Qt.AlignVCenter))
        elif role == Qt.Qt.SizeHintRole:
            if orientation == Qt.Qt.Vertical:
                return Qt.QVariant(Qt.QSize(50, 20))
            else:
                return self._getSizeHint(section)
        elif role == Qt.Qt.FontRole:
            return Qt.QVariant(Qt.QFont("Mono", 8))
        elif role == Qt.Qt.ToolTipRole:
            if section == LEVEL:
                return Qt.QVariant("log level")
            elif section == TYPE:
                return Qt.QVariant("log type")
            elif section == TIME:
                return Qt.QVariant("log time stamp")
            elif section == MSG:
                return Qt.QVariant("log message")
            elif section == NAME:
                return Qt.QVariant("object who recorded the log")
            elif section == THREAD:
                return Qt.QVariant("the thread where the log was executed from")
            elif section == LOCALT:
                return Qt.QVariant("application relative log time stamp")
        if role != Qt.Qt.DisplayRole:
            return Qt.QVariant()
        if orientation == Qt.Qt.Horizontal:
            return Qt.QVariant(HORIZ_HEADER[section])
        return Qt.QVariant(int(section+1))
    
    def insertRows(self, position, rows=1, index=Qt.QModelIndex()):
        self.beginInsertRows(Qt.QModelIndex(), position, position+rows-1)
        self.endInsertRows()
    
    def removeRows(self, position, rows=1, index=Qt.QModelIndex()):
        self.beginRemoveRows(Qt.QModelIndex(), position, position+rows-1)
        self.endRemoveRows()
    

    #def setData(self, index, value, role=Qt.Qt.DisplayRole):
    #    pass
    
    #def flags(self, index)
    #    pass
        
    #def insertColumns(self):
    #    pass
    
    #def removeColumns(self):
    #    pass
    
    # --------------------------
    # logging.Handler overwrite
    # --------------------------

    def timerEvent(self, evt):
        self.updatePendingRecords()

    def updatePendingRecords(self):
        if not self._accumulated_records:
            return
        row_nb = self.rowCount()
        records = self._accumulated_records
        self._accumulated_records = []
        self._records.extend(records)
        self.insertRows(row_nb, len(records))
        if len(self._records) > self._capacity:
            start = len(self._records) - self._capacity
            self._records = self._records[start:]
            self.removeRows(0, start)
        
    def emit(self, record):
        self._accumulated_records.append(record)
            
    def flush(self):
        pass

    def close(self):
        self.flush()
        del self._records[:]
        logging.Handler.close(self)


class QLoggingTable(Qt.QTableView):
    
    DftScrollLock = False
    
    """A Qt table that displays the taurus logging messages"""
    def __init__(self, parent=None, model=None, designMode=False):
        super(QLoggingTable, self).__init__(parent)
        self.setShowGrid(False)
        
        self.resetScrollLock()
        model = model or QLoggingTableModel()
        self.setModel(model)
        hh = self.horizontalHeader()
        hh.setResizeMode(MSG, Qt.QHeaderView.Stretch)
        self.setSortingEnabled(True)
        self.sortByColumn(TIME, Qt.Qt.AscendingOrder)
        if designMode:
            taurus.disableLogOutput()
            for i in xrange(10): taurus.info("Hello world %04d" % i)
        
    def rowsInserted(self, index, start, end):
        """Overwrite of slot rows inserted to do proper resize and scroll to 
        bottom if desired
        """
        for i in xrange(start,end+1):
            self.resizeRowToContents(i)
        if start == 0:
            self.resizeColumnsToContents()
        if not self._scrollLock:
            self.scrollToBottom()

    def setScrollLock(self, scrollLock):
        """Sets the state for scrollLock"""
        self._scrollLock = scrollLock
    
    def getScrollLock(self):
        """Returns wheater or not the scrollLock is active"""
        return self._scrollLock

    def resetScrollLock(self):
        self.setScrollLock(QLoggingTable.DftScrollLock)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return { 
            'module'    : 'taurus.qt.qtgui.table',
            'group'     : 'Taurus Views',
            'icon'      : ':/designer/table.png',
            'container' : False }


    #: Tells wheater the table should scroll automatically to the end each
    #: time a record is added or not
    autoScroll = Qt.pyqtProperty("bool", getScrollLock, setScrollLock, resetScrollLock)


class QLoggingWidget(Qt.QWidget):
    
    def __init__(self, parent=None, model=None, designMode=False):
        super(QLoggingWidget, self).__init__(parent)
        self._model = model or QLoggingTableModel()
        self.init(designMode)
        
    def init(self, designMode):
        l = Qt.QGridLayout()
        l.setContentsMargins(0,0,0,0)
        l.setVerticalSpacing(2)
        self.setLayout(l)
        
        table = self._logtable = QLoggingTable(model = self._model, designMode=designMode)
        tb = self._toolbar = Qt.QToolBar("Taurus logger toolbar")
        tb.setFloatable(False)
        
        self._scrollLockButton = Qt.QPushButton(getIcon(":/emblems/lock.svg"),"")
        self._scrollLockButton.setCheckable(True)
        self._scrollLockButton.setChecked(table.getScrollLock())
        self._scrollLockButton.setToolTip('Scroll lock')
        self._scrollLockButton.setFlat(True)
        Qt.QObject.connect(self._scrollLockButton, Qt.SIGNAL("toggled(bool)"), table.setScrollLock)
        
        self._updateButton = Qt.QPushButton("Update")
        self._updateButton.setCheckable(True)
        self._levelFilterComboBox = Qt.QComboBox()
        self._levelFilterComboBox.addItems([">=Trace",">=Debug",">=Info",">=Warning",">=Error",">=Critical"])
        tb.addWidget(self._scrollLockButton)
        tb.addWidget(self._updateButton)
        tb.addWidget(self._levelFilterComboBox)
        l.addWidget(tb, 0, 0)
        l.addWidget(table, 1, 0)
        l.setColumnStretch(0,1)
        l.setRowStretch(1,1)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return { 
            'module'    : 'taurus.qt.qtgui.table',
            'group'     : 'Taurus Views',
            'icon'      : ':/designer/table.png',
            'container' : False }

def fill_log():
    import time
    import random
    
    for i in xrange(10):
        taurus.info("Hello world %04d" % i)
    
    i = 0
    while True:
        time.sleep(random.random())
        level = random.randint(taurus.Trace, taurus.Critical)
        taurus.log(level, "EXTRA %04d" % i)
        i +=1
    
def main():
    import sys
    
    app = Qt.QApplication(sys.argv)
    
    w = QLoggingWidget()
    taurus.setLogLevel(taurus.Trace)
    taurus.disableLogOutput()
    
    taurus.trace("trace message")
    taurus.debug("debug message")
    taurus.info("Hello world")
    taurus.warning("Warning message")
    taurus.error("error message")
    taurus.critical("critical message")
    w.setMinimumSize(1024,400)
    w.setVisible(True)

    import threading
    t = threading.Thread(name="Filler", target=fill_log)
    t.daemon = True
    t.start()

    app.exec_()

if __name__ == '__main__':
    main()

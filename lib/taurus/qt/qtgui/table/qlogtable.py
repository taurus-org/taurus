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

"""This module provides Qt table widgets which display logging messages from the
python :mod:`logging` module"""

from __future__ import absolute_import

from operator import attrgetter
from builtins import range

import logging
import logging.handlers
import datetime
import threading
import socket
import click

import taurus
from taurus.core.util.log import Logger
from taurus.core.util.remotelogmonitor import LogRecordStreamHandler, \
    LogRecordSocketReceiver
from taurus.core.util.decorator.memoize import memoized

from taurus.external.qt import Qt
from taurus.qt.qtgui.model import FilterToolBar
from taurus.qt.qtgui.util import ActionFactory
import taurus.cli.common

from .qtable import QBaseTableWidget


__all__ = ["QLoggingTableModel", "QLoggingTable", "QLoggingWidget",
           "QRemoteLoggingTableModel"]

__docformat__ = 'restructuredtext'

LEVEL, TIME, MSG, NAME, ORIGIN = list(range(5))
HORIZ_HEADER = 'Level', 'Time', 'Message', 'By', 'Origin'

__LEVEL_BRUSH = {
    taurus.Trace: (Qt.Qt.lightGray, Qt.Qt.black),
    taurus.Debug: (Qt.Qt.green, Qt.Qt.black),
    taurus.Info: (Qt.Qt.blue, Qt.Qt.white),
    taurus.Warning: (Qt.QColor(255, 165, 0), Qt.Qt.black),
    taurus.Error: (Qt.Qt.red, Qt.Qt.black),
    taurus.Critical: (Qt.QColor(160, 32, 240), Qt.Qt.white),
}


def getBrushForLevel(level):
    elevel = taurus.Trace
    if level <= taurus.Trace:
        elevel = taurus.Trace
    elif level <= taurus.Debug:
        elevel = taurus.Debug
    elif level <= taurus.Info:
        elevel = taurus.Info
    elif level <= taurus.Warning:
        elevel = taurus.Warning
    elif level <= taurus.Error:
        elevel = taurus.Error
    elif level <= taurus.Critical:
        elevel = taurus.Critical
    f, g = list(map(Qt.QBrush, __LEVEL_BRUSH[elevel]))
    return f, g


gethostname = memoized(socket.gethostname)


def _get_record_origin(rec):
    host = getattr(rec, 'hostName', "?" + gethostname() + "?")
    procName = getattr(rec, 'processName', "?process?")
    procID = getattr(rec, 'process', "?PID?")
    threadName = getattr(rec, 'threadName', "?thread?")
    threadID = getattr(rec, 'thread', "?threadID?")
    return host, procName, procID, threadName, threadID


def _get_record_trace(rec):
    pathname = getattr(rec, 'pathname', '')
    filename = getattr(rec, 'filename', '')
    modulename = getattr(rec, 'module', '')
    funcname = getattr(rec, 'funcName', '')
    lineno = getattr(rec, 'lineno', '')
    return pathname, filename, modulename, funcname, lineno


def _get_record_origin_str(rec):
    return "{0}.{1}.{3}".format(*_get_record_origin(rec))


def _get_record_origin_tooltip(rec):

    host, procName, procID, threadName, threadID = _get_record_origin(rec)
    pathname, filename, modulename, funcname, lineno = _get_record_trace(rec)
    timestamp = str(datetime.datetime.fromtimestamp(rec.created))
    bgcolor, fgcolor = list(map(Qt.QBrush.color, getBrushForLevel(rec.levelno)))
    bgcolor = "#%02x%02x%02x" % (
        bgcolor.red(), bgcolor.green(), bgcolor.blue())
    fgcolor = "#%02x%02x%02x" % (
        fgcolor.red(), fgcolor.green(), fgcolor.blue())

    return """<html><font face="monospace" size="1">
<table border="0" cellpadding="0" cellspacing="0">
<tr><td>Level:</td><td><font color="{level_bgcolor}">{level}</font></td></tr>
<tr><td>Time:</td><td>{timestamp}</td></tr>
<tr><td>Message:</td><td>{message}</td></tr>
<tr><td>By:</td><td>{name}</td></tr>
<tr><td>Host:</td><td>{host}</td></tr>
<tr><td>Process:</td><td>{procname}({procID})</td></tr>
<tr><td>Thread:</td><td>{threadname}({threadID})</td></tr>
<tr><td>From:</td><td>File pathname({filename}), line {lineno}, in {funcname}</td></tr>
</table></font></html>
""".format(level=rec.levelname, level_fgcolor=fgcolor, level_bgcolor=bgcolor,
           timestamp=timestamp, message=rec.getMessage(),
           name=rec.name, host=host, procname=procName, procID=procID,
           threadname=threadName, threadID=threadID,
           pathname=pathname, filename=filename, funcname=funcname,
           lineno=lineno)


class QLoggingTableModel(Qt.QAbstractTableModel, logging.Handler):

    DftFont = Qt.QFont("Mono", 8)
    DftColSize = Qt.QSize(80, 20), Qt.QSize(200, 20), \
        Qt.QSize(300, 20), Qt.QSize(180, 20), Qt.QSize(240, 20),

    def __init__(self, parent=None, capacity=500000, freq=0.25):
        super(Qt.QAbstractTableModel, self).__init__()
        logging.Handler.__init__(self)
        self._capacity = capacity
        self._records = []
        self._accumulated_records = []
        Logger.addRootLogHandler(self)
        self.startTimer(freq * 1000)

    # ---------------------------------
    # Qt.QAbstractTableModel overwrite
    # ---------------------------------

    def sort(self, column, order=Qt.Qt.AscendingOrder):
        column2key_map = {LEVEL: attrgetter('levelno'),
                          TIME: attrgetter('created'),
                          MSG: attrgetter('msg'),
                          NAME: attrgetter('name'),
                          ORIGIN: attrgetter('process', 'thread', 'name'),
        }
        self._records = sorted(self._records, key=column2key_map[column],
                               reverse=order == Qt.Qt.DescendingOrder)

    def rowCount(self, index=Qt.QModelIndex()):
        return len(self._records)

    def columnCount(self, index=Qt.QModelIndex()):
        return len(HORIZ_HEADER)

    def getRecord(self, index):
        return self._records[index.row()]

    def data(self, index, role=Qt.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._records)):
            return None
        record = self.getRecord(index)
        column = index.column()
        if role == Qt.Qt.DisplayRole:
            if column == LEVEL:
                return record.levelname
            elif column == TIME:
                dt = datetime.datetime.fromtimestamp(record.created)
                return str(dt)
                # return dt.strftime("%Y-%m-%d %H:%m:%S.%f")
            elif column == MSG:
                return record.getMessage()
            elif column == NAME:
                return record.name
            elif column == ORIGIN:
                return _get_record_origin_str(record)
        elif role == Qt.Qt.TextAlignmentRole:
            if column in (LEVEL, MSG):
                return Qt.Qt.AlignLeft | Qt.Qt.AlignVCenter
            return Qt.Qt.AlignRight | Qt.Qt.AlignVCenter
        elif role == Qt.Qt.BackgroundRole:
            if column == LEVEL:
                return getBrushForLevel(record.levelno)[0]
        elif role == Qt.Qt.ForegroundRole:
            if column == LEVEL:
                return getBrushForLevel(record.levelno)[1]
        elif role == Qt.Qt.ToolTipRole:
            return _get_record_origin_tooltip(record)
        elif role == Qt.Qt.SizeHintRole:
            return self._getSizeHint(column)
        # elif role == Qt.Qt.StatusTipRole:
        # elif role == Qt.Qt.CheckStateRole:
        elif role == Qt.Qt.FontRole:
            return self.DftFont
        return None

    def _getSizeHint(self, column):
        return QLoggingTableModel.DftColSize[column]

    def headerData(self, section, orientation, role=Qt.Qt.DisplayRole):
        if role == Qt.Qt.TextAlignmentRole:
            if orientation == Qt.Qt.Horizontal:
                return int(Qt.Qt.AlignLeft | Qt.Qt.AlignVCenter)
            return int(Qt.Qt.AlignRight | Qt.Qt.AlignVCenter)
        elif role == Qt.Qt.SizeHintRole:
            if orientation == Qt.Qt.Vertical:
                return Qt.QSize(50, 20)
            else:
                return self._getSizeHint(section)
        elif role == Qt.Qt.FontRole:
            return Qt.QFont("Mono", 8)
        elif role == Qt.Qt.ToolTipRole:
            if section == LEVEL:
                return "log level"
            elif section == TIME:
                return "log time stamp"
            elif section == MSG:
                return "log message"
            elif section == NAME:
                return "object who recorded the log"
            elif section == ORIGIN:
                return ("the host, process and thread where the"
                        + " log was executed from")
        if role != Qt.Qt.DisplayRole:
            return None
        if orientation == Qt.Qt.Horizontal:
            return HORIZ_HEADER[section]
        return int(section + 1)

    def insertRows(self, position, rows=1, index=Qt.QModelIndex()):
        self.beginInsertRows(Qt.QModelIndex(), position, position + rows - 1)
        self.endInsertRows()

    def removeRows(self, position, rows=1, index=Qt.QModelIndex()):
        self.beginRemoveRows(Qt.QModelIndex(), position, position + rows - 1)
        self.endRemoveRows()

    # def setData(self, index, value, role=Qt.Qt.DisplayRole):
    #    pass

    # def flags(self, index)
    #    pass

    # def insertColumns(self):
    #    pass

    # def removeColumns(self):
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


class _LogRecordStreamHandler(LogRecordStreamHandler):

    def handleLogRecord(self, record):
        self.server.data.get('model').emit(record)


class QRemoteLoggingTableModel(QLoggingTableModel):
    """A remote Qt table that displays the taurus logging messages"""

    def connect_logging(self, host='localhost',
                        port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                        handler=_LogRecordStreamHandler):
        self.log_receiver = LogRecordSocketReceiver(host=host, port=port,
                                                    handler=handler, model=self)
        self.log_thread = threading.Thread(
            target=self.log_receiver.serve_until_stopped)
        self.log_thread.daemon = False
        self.log_thread.start()

    def disconnect_logging(self):
        if not hasattr(self, 'log_receiver') or self.log_receiver is None:
            return
        self.log_receiver.stop()
        self.log_thread.join()
        del self.log_receiver


class QLoggingTable(Qt.QTableView):
    """A Qt table that displays the taurus logging messages"""

    scrollLock = False

    def rowsInserted(self, index, start, end):
        """Overwrite of slot rows inserted to do proper resize and scroll to
        bottom if desired"""
        Qt.QTableView.rowsInserted(self, index, start, end)
        for i in range(start, end + 1):
            self.resizeRowToContents(i)
        if start == 0:
            self.resizeColumnsToContents()
        if not self.scrollLock:
            self.scrollToBottom()

    def setScrollLock(self, scrollLock):
        """Sets the state for scrollLock"""
        self.scrollLock = scrollLock

    def getScrollLock(self):
        """Returns wheater or not the scrollLock is active"""
        return self.scrollLock

    def resetScrollLock(self):
        self.setScrollLock(QLoggingTable.ScrollLock)


class LoggingToolBar(FilterToolBar):

    scrollLockToggled = Qt.pyqtSignal(bool)

    def __init__(self, view=None, parent=None, designMode=False):
        FilterToolBar.__init__(self, view=view, parent=parent,
                               designMode=designMode)
        self.getFilterLineEdit().setToolTip("Quick filter by log name")

        self._logLevelComboBox = logLevelComboBox = Qt.QComboBox()
        levels = "Trace", "Debug", "Info", "Warning", "Error", "Critical"
        for level in levels:
            logLevelComboBox.addItem(level, getattr(taurus, level))
        logLevelComboBox.setCurrentIndex(0)
        logLevelComboBox.currentIndexChanged.connect(self.onLogLevelChanged)
        logLevelComboBox.setToolTip("Filter by log level")

        self._filterLevelAction = self.addWidget(logLevelComboBox)
        self.addSeparator()

        af = ActionFactory()
        self._scrollLockAction = af.createAction(self, "Refresh",
                                                 icon=Qt.QIcon.fromTheme(
                                                     "system-lock-screen"),
                                                 tip="Scroll lock",
                                                 toggled=self.onToggleScrollLock)

        self.addAction(self._scrollLockAction)

    def onToggleScrollLock(self, yesno):
        self.scrollLockToggled.emit(yesno)

    def onLogLevelChanged(self, index):
        self.onFilterChanged()

    def getLogLevelComboBox(self):
        return self._logLevelComboBox

    def getLogLevel(self):
        combo = self.getLogLevelComboBox()
        return combo.itemData(combo.currentIndex())

    def setLogLevel(self, level):
        combo = self.getLogLevelComboBox()
        for i in range(combo.count()):
            l = combo.itemData(i)
            if l == level:
                combo.setCurrentIndex(i)


class QLoggingFilterProxyModel(Qt.QSortFilterProxyModel):
    """A filter by log record object name"""

    def __init__(self, parent=None):
        Qt.QSortFilterProxyModel.__init__(self, parent)
        self._logLevel = taurus.Trace

        # filter configuration
        self.setFilterCaseSensitivity(Qt.Qt.CaseInsensitive)
        self.setFilterKeyColumn(0)
        self.setFilterRole(Qt.Qt.DisplayRole)

        # sort configuration
        # self.setSortCaseSensitivity(Qt.Qt.CaseInsensitive)
        # self.setSortRole(Qt.Qt.DisplayRole)

        # general configuration

    def setFilterLogLevel(self, level):
        self._logLevel = level

    def __getattr__(self, name):
        return getattr(self.sourceModel(), name)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        sourceModel = self.sourceModel()
        idx = sourceModel.index(sourceRow, NAME, sourceParent)
        record = self.getRecord(idx)
        if record.levelno < self._logLevel:
            return False
        name = str(sourceModel.data(idx))
        regexp = self.filterRegExp()
        if regexp.indexIn(name) != -1:
            return True
        return False


_W = "Warning: Switching log perspective will erase previous log messages " \
     "from current perspective!"


class QLoggingWidget(QBaseTableWidget):

    KnownPerspectives = {
        'Standard': {
            "label": "Local",
            "icon": "computer",
            "tooltip": "Local logging.\n" + _W,
            "model": [QLoggingFilterProxyModel, QLoggingTableModel, ],
        },
        'Remote': {
            "label": "Remote",
            "icon": "network-server",
            "tooltip": "Monitor remote logs.\n" + _W,
            "model": [QLoggingFilterProxyModel, QRemoteLoggingTableModel, ],
        },
    }

    DftPerspective = 'Standard'

    def __init__(self, parent=None, designMode=False,
                 with_filter_widget=LoggingToolBar,
                 with_selection_widget=True, with_refresh_widget=True,
                 perspective=None, proxy=None):
        QBaseTableWidget.__init__(self, parent=parent, designMode=designMode,
                                  with_filter_widget=with_filter_widget,
                                  with_selection_widget=False, with_refresh_widget=False,
                                  perspective=perspective, proxy=proxy)

    def createViewWidget(self, klass=None):
        if klass is None:
            klass = QLoggingTable
        view = QBaseTableWidget.createViewWidget(self, klass=klass)
        hh = view.horizontalHeader()
        if hh.length() > 0:
            try:
                hh.setSectionResizeMode(MSG, Qt.QHeaderView.Stretch)
            except AttributeError:  # PyQt4
                hh.setResizeMode(MSG, Qt.QHeaderView.Stretch)
        view.setShowGrid(False)
        view.sortByColumn(TIME, Qt.Qt.AscendingOrder)
        return view

    def createToolArea(self):
        tb = QBaseTableWidget.createToolArea(self)
        filterBar = self.getFilterBar()
        filterBar.scrollLockToggled.connect(self.onScrollLockToggled)
        return tb

    def onScrollLockToggled(self, yesno):
        self.viewWidget().setScrollLock(yesno)

    def onFilterChanged(self, filter):
        if not self.usesProxyQModel():
            return
        proxy_model = self.getQModel()
        level = self.getFilterBar().getLogLevel()
        proxy_model.setFilterLogLevel(level)
        return QBaseTableWidget.onFilterChanged(self, filter)

    def onSwitchPerspective(self, perspective):
        self.stop_logging()
        if perspective == "Remote":
            if hasattr(self, 'hostName') and hasattr(self, 'port'):
                host, port = self.hostName, self.port
            else:
                isValid = False
                dft = "%s:%d" % (socket.gethostname(),
                                 logging.handlers.DEFAULT_TCP_LOGGING_PORT)
                while not isValid:
                    txt, res = Qt.QInputDialog.getText(self,
                                                       "Please input remote logging host and port",
                                                       "Location (<host>:<port>):", Qt.QLineEdit.Normal, dft)
                    if not res:
                        return
                    try:
                        host, port = str(txt).split(":", 1)
                        port = int(port)
                        isValid = True
                    except:
                        Qt.QMessageBox.information(self, "Invalid name",
                                                   "Please type a valid <host>:<port>")
            ret = QBaseTableWidget.onSwitchPerspective(self, perspective)
            qmodel = self.getQModel()
            qmodel.connect_logging(host=host, port=port)
        else:
            ret = QBaseTableWidget.onSwitchPerspective(self, perspective)
        return ret

    def destroy(self, destroyWindow=True, destroySubWindows=True):
        self.stop_logging()
        return QBaseTableWidget.destroy(self, destroyWindow, destroySubWindows)

    def stop_logging(self):
        model = self.getBaseQModel()
        if hasattr(model, 'disconnect_logging'):
            model.disconnect_logging()

    @classmethod
    def getQtDesignerPluginInfo(cls):
        return {
            'module': 'taurus.qt.qtgui.table',
            'group': 'Taurus Views',
            'icon': 'designer:table.png',
            'container': False}


def fill_log():
    import time
    import random

    for i in range(10):
        taurus.info("Hello world %04d" % i)

    loggers = ["Object%02d" % (i + 1) for i in range(10)]
    i = 0
    while True:
        time.sleep(random.random())
        logger = logging.getLogger(random.choice(loggers))
        level = random.randint(taurus.Trace, taurus.Critical)
        logger.log(level, "log message %04d" % i)
        i += 1


def main():
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication

    app = Application.instance()
    owns_app = app is None

    if owns_app:
        app = Application(app_name="Logging demo", app_version="1.0",
                          org_domain="Taurus", org_name="Taurus community")

    taurus.setLogLevel(taurus.Trace)
    taurus.disableLogOutput()
    w = QLoggingWidget()

    taurus.trace("trace message")
    taurus.debug("debug message")
    taurus.info("Hello world")
    taurus.warning("Warning message")
    taurus.error("error message")
    taurus.critical("critical message")
    w.setMinimumSize(1200, 600)
    w.show()
    app.exec_()
    w.stop_logging()


@click.command('qlogmon')
@click.option(
    '--port', 'port', type=int,
    default=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
    show_default=True,
    help='Port where log server is running',
)
@click.option(
    '--log-name', 'log_name',
    default=None,
    help='Filter specific log object',
)
@taurus.cli.common.log_level
def qlogmon_cmd(port, log_name, log_level):
    """Show the Taurus Remote Log Monitor"""
    import taurus
    host = socket.gethostname()
    level = getattr(taurus, log_level.capitalize(), taurus.Trace)

    from taurus.qt.qtgui.application import TaurusApplication
    app = TaurusApplication(cmd_line_parser=None,
                            app_name="Taurus remote logger")
    w = QLoggingWidget(perspective="Remote")
    w.setMinimumSize(1024, 600)

    filterbar = w.getFilterBar()
    filterbar.setLogLevel(level)
    if log_name is not None:
        filterbar.setFilterText(log_name)
    w.getPerspectiveBar().setEnabled(False)
    w.getQModel().connect_logging(host, port)
    w.show()
    app.exec_()
    w.getQModel().disconnect_logging()


if __name__ == '__main__':
    main()
    # qlogmon_cmd

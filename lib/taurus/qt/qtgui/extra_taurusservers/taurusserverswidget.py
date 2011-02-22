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
taurusserverswidget.py: 
"""

from PyQt4 import QtGui, QtCore, Qt
from PyTango_utils.servers import ServersDict
from PyTango import DevState
from taurus.core.util import DEVICE_STATE_PALETTE

from ui_taurusserverswidget import Ui_TaurusServersWidget

class TaurusServersWidget(QtGui.QWidget):
    """This widget shows the state of device servers and allows the user
    to start/stop/restart them. The interaction with the servers is done
    using the ServersDict object from PyTango_utils module.

    There is an internal QTimer that takes
    care of updating the server states values. The device server 'qlabels'
    have a background color compatible with Taurus widgets and they are
    presented inside a grid with a fixed number of columns which can be
    set with setGridColumns(int).

    It is also possible to start/stop/restart a single device server with
    the context popup menu at each device server qlabel."""

    def __init__(self, parent):
        """Just create the grid layout and by default hide buttons to
        start/stop/restart all device servers."""
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_TaurusServersWidget()
        self.ui.setupUi(self)

        grid_layout = QtGui.QGridLayout()
        grid_layout.setContentsMargins (1, 1, 1, 1)
        grid_layout.addWidget(self)
        #self.setLayout(grid_layout)
        self.hideButtons()

        self.servers_dict = None
        self.servers_by_level = {}
        self.label_by_server = {}
        self.resetGridColumns()
        self.resetServerNames()
        self.resetShowButtons()

        self.updateStatesTimer = Qt.QTimer(self)
        self.makeConnections()
        self.updateStatesTimer.start(1000)

    def makeConnections(self):
        """Let's be aware of the QtCore signals."""
        QtCore.QObject.connect(self.ui.btnStartAll, QtCore.SIGNAL('pressed()'),
                               self.startAll)
        QtCore.QObject.connect(self.ui.btnStopAll, QtCore.SIGNAL('pressed()'),
                               self.stopAll)
        QtCore.QObject.connect(self.ui.btnRestartAll, QtCore.SIGNAL('pressed()'),
                               self.restartAll)
        QtCore.QObject.connect(self.updateStatesTimer, QtCore.SIGNAL("timeout()"),
                               self.updateServerStates)

    def updateServerNames(self):
        """It receives a list of server/instance and creates uses de
        ServerDict object from PyTango_utils to get the states and the
        levels.  The server qlabels are displayed inside a grid with
        'gridColumns' amount of columns and for each run level a new
        'section' is created.  At each grid cell, there is a custom
        QLabel widget which knows how to set it's background color
        according to the device server state. It is also possible with
        a popup context menu to start/stop/restart a single device
        server."""
        self.servers_dict = None
        self.servers_by_level = {}
        self.label_by_server = {}

        self.servers_dict = ServersDict(servers_list=self.dsNames)
        self.servers_dict.update_states()
        
        self.server_states = self.servers_dict.get_server_states()
        for server in self.server_states.keys():
            state = self.server_states[server]
            level = self.servers_dict.get_server_level(server)
            l = level[1]
            server_label = ServerLabel(server, self)
            if not self.servers_by_level.has_key(l):
                self.servers_by_level[l] = []
            self.servers_by_level.get(l).append(server)
            self.label_by_server[server] = server_label

        NO_LEVEL = ' '
        if self.ui.frDSStates.layout() is None:
            grid_layout = QtGui.QGridLayout()
            grid_layout.setContentsMargins(1, 1, 1, 1)
            self.ui.frDSStates.setLayout(grid_layout)
        grid_layout = self.ui.frDSStates.layout()

        for child in self.ui.frDSStates.children():
            if isinstance(child,QtGui.QLabel) or isinstance(child,QtGui.QFrame):
                grid_layout.removeWidget(child)
                child.setParent(None)

        row = 0
        levels = self.servers_by_level.keys()
        levels.sort()
        for l in levels:
            if l != NO_LEVEL:
                if self.dsGridColumns > 1:
                    line1 = QtGui.QFrame()
                    line1.setFrameShape(QtGui.QFrame.HLine)
                    grid_layout.addWidget(line1, row, 0)
                grid_layout.addWidget(QtGui.QLabel("Level "+l), row , 1 % self.dsGridColumns,
                                      Qt.Qt.AlignHCenter)
                if self.dsGridColumns > 2:
                    line2 = QtGui.QFrame()
                    line2.setFrameShape(QtGui.QFrame.HLine)
                    grid_layout.addWidget(line2, row, 2, 1, self.dsGridColumns - 2)
                row += 1
                col = 0
                servers = self.servers_by_level.get(l)
                for server in servers:
                    if col % self.dsGridColumns == 0:
                        col = 0
                        row += 1
                    server_label = self.label_by_server[server]
                    grid_layout.addWidget(server_label, row, col)
                    col += 1
                row += 1
        if self.servers_by_level.has_key(NO_LEVEL):
            l = NO_LEVEL
            if self.dsGridColumns > 1:
                line1 = QtGui.QFrame()
                line1.setFrameShape(QtGui.QFrame.HLine)
                grid_layout.addWidget(line1, row, 0)
            grid_layout.addWidget(QtGui.QLabel("No Level"), row, 1 % self.dsGridColumns,
                                  Qt.Qt.AlignHCenter)
            if self.dsGridColumns > 2:
                line2 = QtGui.QFrame()
                line2.setFrameShape(QtGui.QFrame.HLine)
                grid_layout.addWidget(line2, row, 2, 1, self.dsGridColumns - 2)
            row += 1
            col = 0
            servers = self.servers_by_level.get(l)
            for server in servers:
                if col % self.dsGridColumns == 0:
                    col = 0
                    row += 1
                server_label = self.label_by_server[server]
                grid_layout.addWidget(server_label, row, col)
                col += 1

    def updateServerStates(self):
        """When it is time, the values of the states and qlables are updated."""
        if self.servers_dict != None:
            self.servers_dict.update_states()
            self.server_states = self.servers_dict.get_server_states()
            for label in self.label_by_server.values():
                label.updateServerState()

    def getServerState(self, server):
        """Return the state for a given server."""
        return self.server_states[server]

    #############################################################################
    ## PUBLIC QT SLOTS ##########################################################

    @QtCore.pyqtSignature('hideButtons()')
    def hideButtons(self):
        """Do not show the buttons to start/stop/restart all device servers."""
        self.ui.frButtons.setVisible(False)

    @QtCore.pyqtSignature('startAll()')
    def startAll(self):
        """Start all device servers from the lower level to the higher
        and not controlled at the end."""
        QtGui.QApplication.instance().setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        NO_LEVEL = ' '
        levels = self.servers_by_level.keys()
        levels.sort()
        exceptions = []
        for l in levels:
            if l != NO_LEVEL:
                servers = self.servers_by_level.get(l)
                try:
                    self.servers_dict.start_servers(servers, wait=0)
                except Exception, e:
                    msg = 'Starting servers: %s.\nCatched exception:(%s)' % (servers, e)
                    exceptions.append(msg)
        if self.servers_by_level.has_key(NO_LEVEL):
            servers = self.servers_by_level.get(NO_LEVEL)
            try:
                self.servers_dict.start_servers(servers, wait=0)
            except Exception, e:
                msg = 'Starting servers: %s.\nCatched exception:(%s)' % (servers, e)
                exceptions.append(msg)

        if len(exceptions)>0:
            print "Some exceptions found", exceptions

        QtGui.QApplication.instance().restoreOverrideCursor()


    @QtCore.pyqtSignature('stopAll()')
    def stopAll(self):
        """Stop all device servers from the higher level to the lower
        and not controlled at the end."""
        QtGui.QApplication.instance().setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        NO_LEVEL = ' '
        levels = self.servers_by_level.keys()
        levels.reverse()
        exceptions = []
        for l in levels:
            if l != NO_LEVEL:
                servers = self.servers_by_level.get(l)
                try:
                    self.servers_dict.stop_servers(servers)
                except Exception, e:
                    msg = 'Stopping servers: %s.\nCatched exception:(%s)' % (servers, e)
                    exceptions.append(msg)
        if self.servers_by_level.has_key(NO_LEVEL):
            servers = self.servers_by_level.get(NO_LEVEL)
            try:
                self.servers_dict.stop_servers(servers)
            except Exception, e:
                msg = 'Stopping servers: %s.\nCatched exception:(%s)' % (servers, e)
                exceptions.append(msg)

        if len(exceptions)>0:
            print "Some exceptions found", exceptions

        QtGui.QApplication.instance().restoreOverrideCursor()


    @QtCore.pyqtSignature('restartAll()')
    def restartAll(self):
        """First stop all, then start all."""
        self.stopAll()
        self.startAll()

    @QtCore.pyqtSignature('startServer(QString)')
    def startServer(self, server):
        """Start just the given server."""
        try:
            self.servers_dict.start_servers([server])
        except Exception, e:
            print "Some exception found when starting server %s.\nCatched exception(%s)"%(server, e)

    @QtCore.pyqtSignature('stopServer(QString)')
    def stopServer(self, server):
        """Stop just the given server."""
        try:
            self.servers_dict.stop_servers([server])
        except Exception, e:
            print "Some exception found when stopping server %s.\nCatched exception(%s)"%(server, e)

    @QtCore.pyqtSignature('restartServer(QString)')
    def restartServer(self, server):
        """Retart just the given server."""
        try:
            self.servers_dict.restart_servers([server])
        except Exception, e:
            print "Some exception found when restarting server %s.\nCatched exception(%s)"%(server, e)


    #############################################################################
    ## PUBLIC PyQt PROPERTIES ###################################################

    @QtCore.pyqtSignature('getGridColumns()')
    def getGridColumns(self):
        """Get the grid columns count."""
        return self.dsGridColumns

    @QtCore.pyqtSignature('setGridColumns(int)')
    def setGridColumns(self, columns):
        """Set the grid columns count."""
        self.dsGridColumns = columns
        if self.servers_dict is not None:
            self.updateServerNames()

    @QtCore.pyqtSignature('resetGridColumns()')
    def resetGridColumns(self):
        """Reset the grid columns count."""
        self.setGridColumns(6)

    gridColumns = QtCore.pyqtProperty("int", getGridColumns, setGridColumns,
                                      resetGridColumns, doc='Columns to be used in the dss grid.')

    @QtCore.pyqtSignature('getServerNames()')
    def getServerNames(self):
        """Get the serverNames."""
        return ','.join(self.dsNames)

    @QtCore.pyqtSignature('setServerNames(QString)')
    def setServerNames(self, serverNames):
        """Set the serverNames."""
        self.dsNames = []
        for serverName in serverNames.split(','):
            s = str(serverName).strip()
            if s != '':
                self.dsNames.append(s)
        self.updateServerNames()

    @QtCore.pyqtSignature('resetServerNames()')
    def resetServerNames(self):
        """Reset the serverNames count."""
        self.setServerNames('')

    serverNames = QtCore.pyqtProperty("QString", getServerNames, setServerNames,
                                      resetServerNames, doc='Server names to be used in the frame.')

    @QtCore.pyqtSignature('getShowButtons()')
    def getShowButtons(self):
        """Show the buttons to start/stop/restart all device servers."""
        return self.ui.frButtons.isVisible()

    @QtCore.pyqtSignature('setShowButtons(bool)')
    def setShowButtons(self, visible):
        """Show the buttons to start/stop/restart all device servers."""
        self.ui.frButtons.setVisible(visible)

    @QtCore.pyqtSignature('setShowButtons()')
    def resetShowButtons(self):
        """Show the buttons to start/stop/restart all device servers."""
        self.setShowButtons(False)

    showButtons = QtCore.pyqtProperty("bool", getShowButtons, setShowButtons,
                                      resetShowButtons, doc='Show or hide the buttons to start/stop/restart device servers.')


class ServerLabel(QtGui.QLabel):
    """This class represents the state of a given device server. It
    offers a context popup menu in order to be able to
    start/stop/restart just one device server."""
    def __init__(self, server, parent):
        """Just prepare everything to be used."""
        QtGui.QLabel.__init__(self, server, parent)
        self.server = server
        self.myParent = parent
        self.setText(self.server)
        self.setupContextMenu()
        self.updateServerState()

    def setupContextMenu(self):
        """Set up the custom context menu signal-slot connection."""
        self.setContextMenuPolicy(Qt.Qt.CustomContextMenu)
        QtCore.QObject.connect(self, QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
                               self.buildContextMenu)

    def updateServerState(self):
        """When required, get the latest state of the server and
        update the GUI interface accordingly."""
        state = self.myParent.getServerState(self.server)
        self.setToolTip("%s is in state %s" % (self.server, state))

        # FOR NOW THE ServersDict RETURNS STRINGS WHICH ARE NOT DevState COMPATIBLE
        # POSSIBLE VALUES ARE: DEAD, ZOMBIE, ALIVE
        color = "grey"
        if state in ['ALIVE', 'Alive', 'alive'] or state == DevState.ON:
            color = DEVICE_STATE_PALETTE.rgb(DevState.ON)
        elif state in ['DEAD', 'Dead', 'dead'] or state == DevState.OFF:
            color = DEVICE_STATE_PALETTE.rgb(DevState.OFF)
        else:
            color = DEVICE_STATE_PALETTE.rgb(DevState.UNKNOWN)

        color_rgb_str = "rgb"+str(color)
        self.setStyleSheet('QWidget { background-color: '+color_rgb_str+'}')

    def buildContextMenu(self, point):
        """Offer the options to start/stop/restart the device server."""
        menu = Qt.QMenu(self.parent())
        menu.addAction("Start server", self.startServer)
        menu.addAction("Stop server", self.stopServer)
        menu.addAction("Restart server", self.restartServer)
        menu.popup(self.cursor().pos())

    def startServer(self):
        """Make the device server start."""
        self.myParent.startServer(self.server)

    def stopServer(self):
        """Make the device server stop."""
        self.myParent.stopServer(self.server)

    def restartServer(self):
        """Make the device server restart."""
        self.myParent.restartServer(self.server)

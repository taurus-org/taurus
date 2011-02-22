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
command.py: Bundles the Tau widgets for command handling.
"""

import warnings

warnings.warn('Usage of tau.widget.command is deprecated since taurus 2.0. Please use taurus.qt.button instead', DeprecationWarning)

from PyTango import ConnectionFailed, DevFailed, DevVoid
from PyQt4 import QtCore, QtGui, Qt
from PyQt4.QtGui import QWidget, QLabel, QGridLayout, QHBoxLayout, QTextEdit, QScrollArea, QFrame, QLineEdit, QListView
import tau
#from tau.widget.ui.command_ui import Ui_Command
from colors import QT_DEVICE_STATE_PALETTE
from tau.core import DeviceFactory, TauBaseWidget
from tau.widget import getIcon, style_connected, style_disconnected, style_error
from PyQt4.QtGui import QSizePolicy

COMMAND_TO_STATE = {
    "MOVE" : "MOVING",
    "RUN"  : "RUNNING"
}

class TauCommandBase(QtGui.QPushButton, TauBaseWidget):

    """CommandLabel

    """

    # We define two signals that are used to indicate changes to the status
    # of the widget.
    __pyqtSignals__ = ("stateChanged(const QString &)")

    def __init__(self, parent = None):
        QtGui.QPushButton.__init__(self, parent)
        TauBaseWidget.__init__(self, parent)
        self._command_base_name = ""
        self._device = ""
        QtCore.QObject.connect(self, QtCore.SIGNAL('clicked(bool)'), self.click)
        # The minimum size of the widget (a limit for the user)

    def connect(self):
        try:
            if self._connected:
                return True

            if self._input_widget!=None:
                self._input_widget.show()

            info = self._device.command_query(self._command_base_name)

            if self._input_widget!=None and info.in_type==DevVoid:
                self._input_widget.hide()

            # output widget is always shown
            if self._output_widget !=None and info.out_type == DevVoid:
                self._output_widget.hide()
            else:
                self._output_widget.show()


            if info.out_type != DevVoid:
                self._connected = True

        except ConnectionFailed, e:
                self.handleException(e)
                return False

        return self._connected

    def getCommand(self):
        return str(self._device)+"/"+self._command_base_name

    @QtCore.pyqtSignature("setCommand(QString)")
    def setCommand(self, cmd_name):
        rx = cmd_name.rindex("/")
        dev_name = cmd_name[0:rx]
        self.setDevice(dev_name)
        self._command_base_name = cmd_name[rx+1:]
        self.setText(self._command_base_name)

        cmd_base = self._command_base_name.upper()
        if COMMAND_TO_STATE.has_key(cmd_base):
            state_name = COMMAND_TO_STATE[cmd_base]
        else:
            state_name = cmd_base

        if QT_DEVICE_STATE_PALETTE.has(state_name):
            (bg, fg) = QT_DEVICE_STATE_PALETTE.qcolor(state_name)
            pal = self.palette()
            pal.setColor(QtGui.QPalette.Background, bg)
            pal.setColor(QtGui.QPalette.Foreground, fg)

        icon = getIcon('command', self._command_base_name)
        if icon!=None:
            self.setIcon(icon)

        self.connect()

    def getCommandBaseName(self):
        return self._command_base_name

    def setDevice(self, dev_name):
        self._device = DeviceFactory().getDevice(dev_name)

    def getDevice(self, dev_name):
        return self._device

    Device = QtCore.pyqtProperty("QString", getCommand, setCommand)

    @QtCore.pyqtSignature("setInputWidgetName(QString)")
    def setInputWidgetName(self, name):
        self._input_widget_name = name
        self._input_widget = eval("self._parent." + name)

    def getInputWidgetName(self):
        return self._input_widget_name

    @QtCore.pyqtSignature("setOutputWidgetName(QString)")
    def setOutputWidgetName(self, name):
        self._output_widget_name = name
        self._output_widget = eval("self._parent." + name)

    def getOutputWidgetName(self):
        return self._output_widget_name

    InputWidgetName = QtCore.pyqtProperty("QString", getInputWidgetName, setInputWidgetName)
    OutputWidgetName = QtCore.pyqtProperty("QString", getOutputWidgetName, setOutputWidgetName)


    def click(self):
        if not self._connected:
            self.connect()

        try:
            if self._device:
                val = getattr(self._device, self._command_base_name)()
                if self._output_widget!=None:
                    style_connected(self._output_widget)
                    self._output_widget.setText(str(val))
            return val

        except ConnectionFailed, e:
            self._connected = False
            if self._output_widget:
                style_error(self._output_widget)
                msg = "Connection Failed!\n" + str(e[0]["desc"]) + "\n(in " + str(e[0]["origin"]) + ")"
                self._output_widget.setText(msg)

        except DevFailed, e:
            if self._output_widget:
                style_error(self._output_widget)
                self._output_widget.setText(str(e[0]["reason"]) + "\n" + str(e[0]["desc"]))

    def setColor(self, color):
        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(color))

    def eventReceived(self, EventSource, EventType, EventValue):
        self.emit(QtCore.SIGNAL('changeText(QString)'), str(EventValue.value))



class TauCommand(QtGui.QWidget, TauBaseWidget):
    def __init__(self, parent=None):
        TauBaseWidget.__init__(self)
        QWidget.__init__(self, parent)
        self._layout = QGridLayout()

        # create widgets
        self._input = QLineEdit(self)
        self._input.setText("")
        self._input.setMinimumSize(QtCore.QSize(100,10))
        self._output = QLabel(self)
        self._output.setWordWrap(False)
        self._output.setText("")
        self._output.setAlignment(QtCore.Qt.AlignTop)

        self._command_base = TauCommandBase(self)
        self._command_base.setInputWidgetName("_input")
        self._command_base.setOutputWidgetName("_output")


        # layout the widgets
        self._layout.addWidget(self._input, 0,0, 1,1, QtCore.Qt.AlignTop)
        self._layout.addWidget(self._command_base, 0,1, QtCore.Qt.AlignTop)
        self._layout.addWidget(self._output, 0,2)
        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(2, 2)
        self.setLayout(self._layout)

    def setCommand(self, cmd):
        self._command_base.setCommand(cmd)

    def connect(self):
        self._command_base.connect()



class TauCommandList(QtGui.QSplitter, TauBaseWidget):
    """If you select another command, the input index should be automatically adapted. The input list should have an <new> entry."""
    def __init__(self, parent=None):
        TauBaseWidget.__init__(self)
        QWidget.__init__(self, parent)
        self._layout = QGridLayout()

        # create widgets
        self._splitter = self
##        self._splitter = QtGui.QSplitter(self)
        self._input = QListView(self)
        self._input.addItem()

        self._output = QLabel()
        self._output.setWordWrap(True)
        scrollarea = QScrollArea()
        scrollarea.setWidget(self._output)
        scrollarea.setWidgetResizable (True)
        self._output.setMinimumHeight(60)
        scrollarea.setMinimumHeight(60)
        self._output.setAlignment(QtCore.Qt.AlignTop)
        q1 = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        q1.setHorizontalStretch(10)
        q1.setVerticalStretch(1)
        scrollarea.setSizePolicy(q1)
        self._output.setSizePolicy(q1)

        self._command_list = QListView()
        self._command_list.setViewMode(QListView.ListMode)
##        self._command_list.setInputWidgetName("_input")
##        self._command_list.setOutputWidgetName("_output")

        # layout the widgets
        self._splitter.addWidget(self._input)
        self._splitter.addWidget(self._command_list)
        self._splitter.addWidget(scrollarea)

    @QtCore.pyqtSignature("setDeviceName(QString)")
    def setDeviceName(self, name):
        self._device = name

    def getDeviceName(self):
        return self._device

    def getCommandFilter(self):
        return self._command_filter

    @QtCore.pyqtSignature("setCommandFilter(QString)")
    def setCommandFilter(self, filter):
        self._command_filter = filter

    def getCommandListReadOnly(self):
        return self._ro

    @QtCore.pyqtSignature("setCommandReadOnly(QString)")
    def setCommandListReadOnly(self, ro):
        self._ro = str(ro)


    Device = QtCore.pyqtProperty("QString", getDeviceName, setDeviceName)
    CommandFilter = QtCore.pyqtProperty("QString", getCommandFilter, setCommandFilter)
    CommandListReadOnly = QtCore.pyqtProperty("QString", getCommandListReadOnly, setCommandListReadOnly)

    def connect(self):
        self._device = DeviceFactory().getDevice(self.getDeviceName())
        device = self._device
        info_list = device.command_list_query()

        # when successful (re)built list of programs
        filter_fun = lambda x: True
        self._command_info_list = []
        for inf in filter(filter_fun, info_list):
            #print inf
            self._command_info_list.append(inf)
        #print [ c.cmd_name for c in self._command_info_list ]

        """
        connect to device
        fetch and filter list of commands

        prepare list
        figure out if the input widget or the output widget is needed
        add input widget as neccessary
        """
if __name__ == "__main__":
##    tau.widget.app(TauCommandBase, TauCommandBase.setCommand)
##    tau.widget.app(TauCommandList, TauCommandList.setCommand)
    tau.widget.app(TauCommandList, TauCommandList.setDeviceName)
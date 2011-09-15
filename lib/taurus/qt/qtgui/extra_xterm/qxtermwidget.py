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
QXTermWidget.py: 
"""

import sys
from taurus.qt import QtCore, QtGui, Qt

class QXTermWidget(QtGui.QWidget):

    __pyqtSignals__ = ("commandFinished(int)")

    def __init__(self, parent = None, designMode = False):
        QtGui.QWidget.__init__(self,parent)
        self._command = ""
        self._fontSize = 7
        layout = QtGui.QVBoxLayout(self)
        
        self._proc = None
        if not designMode:
            self._proc = QtCore.QProcess(self)
            QtCore.QObject.connect(self._proc,QtCore.SIGNAL("finished(int, QProcess::ExitStatus)"),self._commandFinished)


    def closeEvent(self, event):
        self._endTheProcess()
        event.accept()


    @QtCore.pyqtSignature("commandFinished(int,QProcess::ExitStatus)")
    def _commandFinished(self,exitCode,exitStatus):
        self.emit(QtCore.SIGNAL("commandFinished(int)"),exitCode)
        if exitStatus == 0:
            self._restartTheProcess()


    def _endTheProcess(self):
        if self._proc is not None:
            self._proc.kill()
            self._proc.waitForFinished()


    def _restartTheProcess(self):
        if self._proc is None:
            return
        size = self.size()
        width = (size.width()/self._fontSize-2)-3
        height = size.height()/(self._fontSize*2)
        xt_cmd = "xterm"
        xt_cmd = xt_cmd + " -fn -*-fixed-medium-*-*-*-*-*-*-*-*-"+str(self._fontSize*10)+"-*-*"
        xt_cmd = xt_cmd + " -geometry "+str(width)+"x"+str(height)
        xt_cmd = xt_cmd + " -into "+str(self.winId())

        if self._command != "":
            xt_cmd = xt_cmd + " -e "+self._command
        
        try:
            self._endTheProcess()
            self._proc.start(xt_cmd)
        except Exception,e:
            print sys.exc_info()


    def resizeEvent(self,e):
        self._restartTheProcess()
        e.accept()


    def sizeHint(self):
        return QtCore.QSize(300, 150)


    def getCommand(self):
        return self._command


    @QtCore.pyqtSignature("setCommand(QString)")
    def setCommand(self,value):
        self._command = value
        self._restartTheProcess()


    def resetCommand(self):
        self.setCommand("")


    command = QtCore.pyqtProperty("QString", getCommand, setCommand,
                                  resetCommand, doc='The command to be executed within the XTerm')


    def getFontSize(self):
        return self._fontSize


    @QtCore.pyqtSignature("setFontSize(int)")
    def setFontSize(self,value):
        self._fontSize = value
        self._restartTheProcess()


    def resetFontSize(self):
        self.setFontSize(7)


    def destroy(self, destroyWindow = True, destroySubWindows = True):
        self._endTheProcess()
        self._proc = None
        QtGui.QWidget.destroy(self, destroyWindow, destroySubWindows)


    def __del__(self):
        self._endTheProcess()
        self._proc = None

    fontSize = QtCore.pyqtProperty("int", getFontSize, setFontSize,
                                  resetFontSize, doc='The fontSize to be used by the XTerm')

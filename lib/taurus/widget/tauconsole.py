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

import sys
import os.path
import traceback

import PyQt4.Qt as Qt

from spyderlib.utils.qthelpers import qapplication
from spyderlib.widgets.externalshell.pythonshell import ExternalPythonShell
from spyderlib.widgets.externalshell.systemshell import ExternalSystemShell
import spyderlib

class Console(Qt.QPlainTextEdit):
    def __init__(self, prompt='$> ', startup_message='', parent=None):
        Qt.QPlainTextEdit.__init__(self, parent)
        self.prompt = prompt
        self.history = []
        self.namespace = {}
        self.construct = []

        self.setGeometry(50, 75, 600, 400)
        self.setWordWrapMode(Qt.QTextOption.WrapAnywhere)
        self.setUndoRedoEnabled(False)
        self.document().setDefaultFont(Qt.QFont("monospace", 10, Qt.QFont.Normal))
        self.showMessage(startup_message)

    def updateNamespace(self, namespace):
        self.namespace.update(namespace)

    def showMessage(self, message):
        self.appendPlainText(message)
        self.newPrompt()

    def newPrompt(self):
        if self.construct:
            prompt = '.' * len(self.prompt)
        else:
            prompt = self.prompt
        self.appendPlainText(prompt)
        self.moveCursor(Qt.QTextCursor.End)

    def getCommand(self):
        doc = self.document()
        curr_line = unicode(doc.findBlockByLineNumber(doc.lineCount() - 1).text())
        curr_line = curr_line.rstrip()
        curr_line = curr_line[len(self.prompt):]
        return curr_line

    def setCommand(self, command):
        if self.getCommand() == command:
            return
        self.moveCursor(Qt.QTextCursor.End)
        self.moveCursor(Qt.QTextCursor.StartOfLine, Qt.QTextCursor.KeepAnchor)
        for i in range(len(self.prompt)):
            self.moveCursor(Qt.QTextCursor.Right, Qt.QTextCursor.KeepAnchor)
        self.textCursor().removeSelectedText()
        self.textCursor().insertText(command)
        self.moveCursor(Qt.QTextCursor.End)

    def getConstruct(self, command):
        if self.construct:
            prev_command = self.construct[-1]
            self.construct.append(command)
            if not prev_command and not command:
                ret_val = '\n'.join(self.construct)
                self.construct = []
                return ret_val
            else:
                return ''
        else:
            if command and command[-1] == (':'):
                self.construct.append(command)
                return ''
            else:
                return command

    def getHistory(self):
        return self.history

    def setHisory(self, history):
        self.history = history

    def addToHistory(self, command):
        if command and (not self.history or self.history[-1] != command):
            self.history.append(command)
        self.history_index = len(self.history)

    def getPrevHistoryEntry(self):
        if self.history:
            self.history_index = max(0, self.history_index - 1)
            return self.history[self.history_index]
        return ''

    def getNextHistoryEntry(self):
        if self.history:
            hist_len = len(self.history)
            self.history_index = min(hist_len, self.history_index + 1)
            if self.history_index < hist_len:
                return self.history[self.history_index]
        return ''

    def getCursorPosition(self):
        return self.textCursor().columnNumber() - len(self.prompt)

    def setCursorPosition(self, position):
        self.moveCursor(Qt.QTextCursor.StartOfLine)
        for i in range(len(self.prompt) + position):
            self.moveCursor(Qt.QTextCursor.Right)

    def runCommand(self):
        command = self.getCommand()
        self.addToHistory(command)

        command = self.getConstruct(command)

        if command:
            tmp_stdout = sys.stdout

            class stdoutProxy():
                def __init__(self, write_func):
                    self.write_func = write_func
                    self.skip = False

                def write(self, text):
                    if not self.skip:
                        stripped_text = text.rstrip('\n')
                        self.write_func(stripped_text)
                        Qt.QCoreApplication.processEvents()
                    self.skip = not self.skip

            sys.stdout = stdoutProxy(self.appendPlainText)
            try:
                try:
                    result = eval(command, self.namespace, self.namespace)
                    if result != None:
                        self.appendPlainText(repr(result))
                except SyntaxError:
                    exec command in self.namespace
            except SystemExit:
                self.close()
            except:
                traceback_lines = traceback.format_exc().split('\n')
                # Remove traceback mentioning this file, and a linebreak
                for i in (3,2,1,-1):
                    traceback_lines.pop(i)
                self.appendPlainText('\n'.join(traceback_lines))
            sys.stdout = tmp_stdout
        self.newPrompt()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Qt.Key_Enter, Qt.Qt.Key_Return):
            self.runCommand()
            return
        if event.key() == Qt.Qt.Key_Home:
            self.setCursorPosition(0)
            return
        if event.key() == Qt.Qt.Key_PageUp:
            return
        elif event.key() in (Qt.Qt.Key_Left, Qt.Qt.Key_Backspace):
            if self.getCursorPosition() == 0:
                return
        elif event.key() == Qt.Qt.Key_Up:
            self.setCommand(self.getPrevHistoryEntry())
            return
        elif event.key() == Qt.Qt.Key_Down:
            self.setCommand(self.getNextHistoryEntry())
            return
        elif event.key() == Qt.Qt.Key_D and event.modifiers() == Qt.Qt.ControlModifier:
            self.close()
        super(Console, self).keyPressEvent(event)



def get_shell():
    if len(sys.argv) == 1:
        opt = 0
    else:
        opt = int(sys.argv[1])

    wdir = os.path.dirname(spyderlib.__file__)

    if opt == 0:
        shell = ExternalPythonShell(wdir=wdir,
                                    interact=True, umd_enabled=True,
                                    umd_namelist=['guidata', 'guiqwt'],
                                    umd_verbose=True, mpl_patch_enabled=False)
    elif opt == 1:
        shell = ExternalPythonShell(wdir=wdir,
                                    ipython=True, stand_alone=True,
                                    arguments="-q4thread -pylab -colors LightBG",
                                    mpl_patch_enabled=True)
    elif opt == 2:
        shell = ExternalPythonShell(wdir=wdir, ipython=True, stand_alone=True,
                                    arguments="-p spock", mpl_patch_enabled=False)
    else:
        shell = ExternalSystemShell(wdir=wdir)
    return shell

def test1():
    app = qapplication()
    shell = get_shell()
    shell.shell.toggle_wrap_mode(True)
    shell.start(False)
    font = Qt.QFont("Monospace")
    font.setPointSize(10)
    shell.shell.set_font(font)
    shell.show()
    sys.exit(app.exec_())

def test2():
    welcome_message = '''
---------------------------------------------------------------
  Welcome to a primitive Python interpreter.
---------------------------------------------------------------'''
    app = Qt.QApplication(sys.argv)
    console = Console(startup_message=welcome_message)
    console.updateNamespace({'myVar1' : app, 'myVar2' : 1234})
    console.show();
    sys.exit(app.exec_())

if __name__ == "__main__":
    test1()

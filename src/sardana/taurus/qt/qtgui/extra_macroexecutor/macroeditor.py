#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

from taurus.external.qt import Qt
from PyQt4 import Qsci

from taurus.qt.qtgui.resource import getThemeIcon


class MacroEditor(Qsci.QsciScintilla):
    __pyqtSignals__ = ("modelChanged(const QString &)",)

    def __init__(self, parent=None, designMode=False):
        Qsci.QsciScintilla.__init__(self, parent)

        self.textEdit = Qsci.QsciScintilla()
        self.textEdit.setAutoCompletionThreshold(1)
        self.textEdit.setAutoCompletionSource(Qsci.QsciScintilla.AcsAll)
        self.textEdit.setAutoIndent(True)
        self.textEdit.setCallTipsStyle(Qsci.QsciScintilla.CallTipsContext)
        self.textEdit.setCallTipsVisible(0)
        self.pythonLexer = Qsci.QsciLexerPython(self.textEdit)
        self.api = Qsci.QsciAPIs(self.pythonLexer)
        self.api.add(Qt.QString("dupa(a,b)this is function dupa"))
        self.api.prepare()
        self.pythonLexer.setAPIs(self.api)
        self.textEdit.setLexer(self.pythonLexer)

        self.newAction = Qt.QAction(getThemeIcon("document-new"), "New", self)
        self.connect(self.newAction, Qt.SIGNAL("triggered()"), self.newFile)
        self.newAction.setToolTip("Create new file")
        self.newAction.setShortcut("Ctrl+N")

        self.openAction = Qt.QAction(getThemeIcon("document-open"), "Open", self)
        self.connect(self.openAction, Qt.SIGNAL("triggered()"), self.openFile)
        self.openAction.setToolTip("Open existing file")
        self.openAction.setShortcut("Ctrl+O")

        self.saveAction = Qt.QAction(getThemeIcon("document-save"), "Save", self)
        self.connect(self.saveAction, Qt.SIGNAL("triggered()"), self.saveFile)
        self.saveAction.setToolTip("Save document to disk")
        self.saveAction.setShortcut("Ctrl+S")

        self.saveAsAction = Qt.QAction(getThemeIcon("document-save-as"), "Save as...", self)
        self.connect(self.saveAsAction, Qt.SIGNAL("triggered()"), self.saveFile)
        self.saveAsAction.setToolTip("Save document under a new name")

        self.cutAction = Qt.QAction(getThemeIcon("edit-cut"), "Cut", self)
        self.connect(self.cutAction, Qt.SIGNAL("triggered()"), self.cut)
        self.cutAction.setToolTip("Cut current selection's contents to the clipboard")
        self.cutAction.setShortcut("Ctrl+X")
        self.cutAction.setEnabled(False)

        self.copyAction = Qt.QAction(getThemeIcon("edit-copy"), "Copy", self)
        self.connect(self.copyAction, Qt.SIGNAL("triggered()"), self.copy)
        self.copyAction.setToolTip("Copy current selection's contents to the clipboard")
        self.copyAction.setShortcut("Ctrl+C")
        self.copyAction.setEnabled(False)

        self.pasteAction = Qt.QAction(getThemeIcon("edit-paste"), "Paste", self)
        self.connect(self.pasteAction, Qt.SIGNAL("triggered()"), self.paste)
        self.pasteAction.setToolTip("Paste the clipboard's contents into the current selection")
        self.pasteAction.setShortcut("Ctrl+V")

        self.aboutAction = Qt.QAction("About", self)
        self.connect(self.aboutAction, Qt.SIGNAL("triggered()"), self.about)
        self.aboutAction.setToolTip("Show the application's About box")

        self.connect(self.textEdit, Qt.SIGNAL("copyAvailable(bool)"), self.cutAction.setEnabled)
        self.connect(self.textEdit, Qt.SIGNAL("copyAvailable(bool)"), self.copyAction.setEnabled)

        self.setCurrentFile("")

    def closeEvent(self, event):
        if self.maybeSave():
#            self.writeSettings()
            event.accept()
        else:
            event.ignore()

    def newFile(self):
        if self.maybeSave():
            self.textEdit.clear()
            self.setCurrentFile("")

    def openFile(self):
        if self.maybeSave():
            fileName = Qt.QFileDialog.getOpenFileName(self)
        if not fileName is None and file != "":
            self.loadFile(fileName)

    def saveFile(self):
        if self.curFile == "":
            return self.__saveAs()
        else:
            return self.__saveFile(self.curFile)

    def __saveAs(self):
        self.fileName = Qt.QFileDialog.getSaveFileName(self)
        if self.fileName == "":
            return False
        return self.__saveFile(self.fileName)

    def about(self):
        Qt.QMessageBox.about(self, "About MacroEditor", "The MacroEditor by Zbigniew Reszela")

    def documentWasModified(self):
        self.setWindowModified(self.textEdit.isModified())

    def createMenus(self):
        fileMenu = self.menuBar().addMenu("File")
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)

        editMenu = self.menuBar().addMenu("Edit")
        editMenu.addAction(self.cutAction)
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)

        self.menuBar().addSeparator()

        helpMenu = self.menuBar().addMenu("&Help")
        helpMenu.addAction(self.aboutAction)

#    def createToolBars(self):
#        fileToolBar = self.addToolBar("File")
#        fileToolBar.setIconSize(Qt.QSize(36,36))
#        fileToolBar.addAction(self.newAction)
#        fileToolBar.addAction(self.openAction)
#        fileToolBar.addAction(self.saveAction)
#        fileToolBar.addAction(self.saveAsAction)
#
#        editToolBar = self.addToolBar("Edit")
#        editToolBar.setIconSize(Qt.QSize(36,36))
#        editToolBar.addAction(self.cutAction)
#        editToolBar.addAction(self.copyAction)
#        editToolBar.addAction(self.pasteAction)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def maybeSave(self):
        if self.textEdit.isModified():
            ret = Qt.QMessageBox.warning(self, "MacroEditor",
                     "The document has been modified\nDo you want to save your changes?",
                     Qt.QMessageBox.Yes | Qt.QMessageBox.Default,
                     Qt.QMessageBox.No,
                     Qt.QMessageBox.Cancel | Qt.QMessageBox.Escape)
            if ret == Qt.QMessageBox.Yes:
                return self.save()
            elif ret == Qt.QMessageBox.Cancel:
                return False
        return True

    def loadFile(self, fileName):
        try:
            fileHandle = open(fileName, 'r')
        except IOError, e:
            Qt.QMessageBox.warning(self, "MacroEditor", "Cannot read file %s:\n%s." % (fileName, e))
            return False
        fileContents = fileHandle.read()
        Qt.QApplication.setOverrideCursor(Qt.Qt.WaitCursor)
        self.textEdit.setText(fileContents)
        Qt.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName)
        self.statusBar().showMessage("File loaded", 2000)

    def __saveFile(self, fileName):
        try:
            file = open(fileName, 'w')
        except IOError, e:
            Qt.QMessageBox.warning(self, "MacroEditor", "Cannot write file %s:\n%s." % (fileName, e))
            return False
        Qt.QApplication.setOverrideCursor(Qt.Qt.WaitCursor)
        file.write(self.textEdit.text())
        Qt.QApplication.restoreOverrideCursor()
        self.setCurrentFile(fileName)
        self.statusBar().showMessage(("File saved"), 2000)
        return True

    def setCurrentFile(self, fileName):
        self.curFile = fileName
        self.textEdit.setModified(False)
        self.setWindowModified(False)

        if self.curFile == "":
            shownName = "untitled.txt"
        else:
            shownName = self.strippedName(self.curFile)
        self.setWindowTitle("%s[*] - %s" % (shownName, "MacroExecutor"))

    def strippedName(self, fullFileName):
        return Qt.QFileInfo(fullFileName).fileName()

    def cut(self):
        pass

    def copy(self):
        pass

    def paste(self):
        pass


def test():
    import sys
    app = Qt.QApplication(sys.argv)
    macroEditor = MacroEditor()
    macroEditor.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    test()

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

"""DataExportDlg.py: A Qt dialog for showing and exporting x-y Ascii data from
one or more curves"""

from __future__ import print_function

from future.utils import string_types

import os.path
from datetime import datetime

from taurus.external.qt import Qt, compat
from taurus.qt.qtgui.util.ui import UILoadable


__all__ = ["QDataExportDialog"]


@UILoadable
class QDataExportDialog(Qt.QDialog):
    """
    This creates a Qt dialog for showing and exporting x-y Ascii data from one or more curves
    The data sets are passed (by calling setDataSets() or at instantiation time) as a dictionary::

        datadict={name:(x,y),...}

    where name is the curve name and
    x,y are iterable containers (e.g., lists, tuple, arrays...) of data to be exported

    @TODO: It would be nice if the textedit scrolled to the start ***also for the first set loaded***"""

    # constants
    allInSingleFile = "All sets in a single file (table like)"
    allInMultipleFiles = "All set in multiple files"

    def __init__(self, parent=None, datadict=None, sortedNames=None):
        super(QDataExportDialog, self).__init__(parent)
        self.loadUi()
        self._xIsTime = False

        # connections
        self.exportBT.clicked.connect(self.exportData)
        self.dataSetCB.currentIndexChanged['QString'].connect(self.onDataSetCBChange)

        self.setDataSets(datadict, sortedNames)

    def setDataSets(self, datadict, sortedNames=None):
        """Used to set the sets that are to be offered for exporting. It overwrites previous values.
        """
        if datadict is None:
            return
        if sortedNames is None:
            sortedNames = sorted(self.datadict.keys())
        self.sortedNames = sortedNames
        self.datatime = datetime.now()
        self.datadict = datadict
        self.dataSetCB.clear()
        self.dataSetCB.insertItems(0, sortedNames)
        if len(self.datadict) > 1:
            self.dataSetCB.insertItems(
                0, [self.allInSingleFile, self.allInMultipleFiles])

    def exportData(self):
        if self.dataSetCB.currentText() == self.allInMultipleFiles:
            self.exportAllData()
        else:
            self.exportCurrentData()

    def exportCurrentData(self, set=None, ofile=None, verbose=True, AllowCloseAfter=True):
        """Exports data
        Arguments:
        set: the curve name. If none is passed, it uses the one selected by dataSetCB
        ofile: output file name or file handle. It will prompt if not provided
        verbose: set this to False to disable information popups
        AllowCloseAfter: set this to false if you want to ignore the checkbox in the dialog

        """
        if set is None:
            set = str(self.dataSetCB.currentText())

        if ofile is None:
            if set == self.allInSingleFile:
                name = "all.dat"
            else:
                #**lazy** sanitising of the set to *suggest* it as a filename
                name = set.replace('*', '').replace('/', '_').replace('\\', '_')
                name += ".dat"
            ofile, _ = compat.getSaveFileName(self, 'Export File Name', name,
                                              'All Files (*)')
            if not ofile:
                return False
        try:
            if isinstance(ofile, string_types):
                ofile = open(str(ofile), "w")
            if self.dataSetCB.currentText() == self.allInMultipleFiles:
                # 1  file per curve
                text = "# DATASET= %s" % set
                text += "\n# SNAPSHOT_TIME= %s\n" % self.datatime.isoformat('_')
                xdata, ydata = self.datadict[set]
                if self.xIsTime():
                    for x,y in zip(xdata, ydata):
                        t = datetime.fromtimestamp(x)
                        text += "%s\t%r\n" % (t.isoformat('_'), y)
                else:
                    for x,y in zip(xdata, ydata):
                        text+="%r\t%r\n" % (x, y)
                print(str(text), file=ofile)
            else:
                print(str(self.dataTE.toPlainText()), file=ofile)
        except:
            Qt.QMessageBox.warning(self,
                                   "File saving failed",
                                   "Failed to save file '%s'" % str(ofile.name),
                                   Qt.QMessageBox.Ok)
            raise
        finally:
            ofile.close()
        if verbose:
            msg = "Set saved to '%s'" % str(ofile.name)
            Qt.QMessageBox.information(self, "Set exported", msg,
                                       Qt.QMessageBox.Ok)
        if AllowCloseAfter and self.closeAfterCB.isChecked(): 
            self.accept() #closes the ExportData dialog with Accept state
        return True

    def exportAllData(self, preffix=None):
        """Exports all sets using a common preffix and appending 'XXX.dat', where XXX is a number starting at 001
        if preffix is not given, the user is prompted for a directory path"""
        if preffix is None:
            outputdir = Qt.QFileDialog.getExistingDirectory(
                self, 'Export Directory', '')
            if not outputdir:
                return False
            preffix = os.path.join(str(outputdir), "set")
        for i, k in zip(range(len(self.datadict)), self.sortedNames):
            ofile = "%s%03i.dat" % (preffix, i + 1)
            try:
                self.exportCurrentData(
                    set=k, ofile=ofile, verbose=False, AllowCloseAfter=False)
            except:
                return False
        # mend undesired side effect of updateText in the for loop
        self.updateText(self.allInMultipleFiles)
        Qt.QMessageBox.information(self, "All sets exported", "%i set(s) exported to:\n%sXXX.dat" % (
            len(self.datadict), preffix), Qt.QMessageBox.Ok)
        if self.closeAfterCB.isChecked():
            self.accept()  # closes the ExportData dialog with Accept state
        return True

    def onDataSetCBChange(self, key):
        key = str(key)
        self.updateText(key)

    def updateText(self, key=None):
        '''update the text edit that shows the preview of the data'''
        if key is None:
            key = str(self.dataSetCB.currentText())
        if key in (self.allInMultipleFiles, self.allInSingleFile):
            # check that all arrays have the same length and the same xdata and
            # update header section
            header = "# DATASET= "
            body = ""
            previous = None
            for curve_name in self.sortedNames:
                xdata, ydata = self.datadict[curve_name]
                if previous is None:
                    previous = xdata
                    header += ' "abscissa"'
                elif previous != xdata:
                    if (key == self.allInSingleFile):
                        self.dataTE.clear()
                        Qt.QMessageBox.critical(self,
                                    "Unable to display",
                                    "X axes of all sets in the plot must be " +
                                    "exactly the same for saving in a single " +
                                    "file!. Curves will be saved each one in " +
                                    "its own file",
                                    Qt.QMessageBox.Ok)
                        index = self.dataSetCB.findText(self.allInMultipleFiles)
                        self.dataSetCB.setCurrentIndex(index)
                        return
                    else:
                        self.dataTE.clear()
                        self.dataTE.insertPlainText("Unable to display because abscissas are different.\n"
                                                    "Curves will be saved each one in its own file")
                        return
                header += ' , "%s"' % curve_name

            header += "\n# SNAPSHOT_TIME= %s\n" % self.datatime.isoformat('_')
            # if we reached this point x axes are equal, so fill the editor
            # with the data
            for i, x in enumerate(previous):
                if self.xIsTime():
                    t = datetime.fromtimestamp(x)
                    body += "%s" % t.isoformat('_')
                else:
                    body += "%r" % x
                for curve_name in self.sortedNames:
                    xdata, ydata = self.datadict[curve_name]
                    body += ("\t%r" % ydata[i])
                body += "\n"
            # fill text editor
            self.dataTE.clear()
            self.dataTE.insertPlainText(header + body)
            self.dataTE.moveCursor(Qt.QTextCursor.Start)
            if key == self.allInMultipleFiles:
                self.dataTE.setReadOnly(True)
            else:
                self.dataTE.setReadOnly(False)
        else:
            self.dataTE.setReadOnly(False)
            xdata, ydata = self.datadict[key]
            text = '# DATASET= "%s"\n' % key
            text += "# SNAPSHOT_TIME= %s\n" % self.datatime.isoformat('_')
            if self.xIsTime():
                for x, y in zip(xdata, ydata):
                    t = datetime.fromtimestamp(x)
                    text += "%s\t%r\n"%(t.isoformat('_'), y)
            else:
                for x, y in zip(xdata, ydata):
                    text += "%r\t%r\n" %(x, y)
            self.dataTE.clear()
            self.dataTE.insertPlainText(text)
            self.dataTE.moveCursor(Qt.QTextCursor.Start)

    def setXIsTime(self, xIsTime):
        self._xIsTime = xIsTime
        self.updateText()

    def xIsTime(self):
        return self._xIsTime


if __name__ == "__main__":
    import sys
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(sys.argv, cmd_line_parser=None)
    form = QDataExportDialog()
    form.show()
    sys.exit(app.exec_())

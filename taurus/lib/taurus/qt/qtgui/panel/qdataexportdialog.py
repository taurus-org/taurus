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

"""DataExportDlg.py: A Qt dialog for showing and exporting x-y Ascii data from
one or more curves"""

import os.path
from datetime import datetime

from taurus.qt import Qt

from ui import ui_DataExportDlg

class QDataExportDialog(Qt.QDialog, ui_DataExportDlg.Ui_DataExportDlg):
    """
    This creates a Qt dialog for showing and exporting x-y Ascii data from one or more curves 
    The data sets are passed (by calling setDataSets() or at instantiation time) as a dictionary::
    
        datadict={name:(x,y),...}
        
    where name is the curve name and
    x,y are iterable containers (e.g., lists, tuple, arrays...) of data to be exported
     
    @TODO: It would be nice if the textedit scrolled to the start ***also for the first set loaded***"""

    #constants
    allInSingleFile = "All sets in a single file (table like)"
    allInMultipleFiles = "All set in multiple files"

    def __init__(self, parent=None, datadict=None):
        super(QDataExportDialog,self).__init__(parent)
        self.setupUi(self)
        self._xIsTime = False
        
        #connections
        Qt.QObject.connect(self.exportBT,Qt.SIGNAL("clicked()"),self.exportData)
        Qt.QObject.connect(self.dataSetCB,Qt.SIGNAL("currentIndexChanged(const QString&)"),self.onDataSetCBChange)
        
        self.setDataSets(datadict)


    def setDataSets(self, datadict):
        """Used to set the sets that are to be offered for exporting. It overwrites previous values.
        """
        if datadict is None: return
        self.datatime=datetime.now()
        self.datadict=datadict
        self.dataSetCB.clear()
        self.dataSetCB.insertItems(0,sorted(self.datadict.keys()))
        if len(self.datadict.keys()) > 1:
            self.dataSetCB.insertItems(0,[self.allInSingleFile, self.allInMultipleFiles])

    def exportData(self):
        if self.dataSetCB.currentText() == self.allInMultipleFiles:
            self.exportAllData()
        else:
            self.exportCurrentData()

    def exportCurrentData(self,set=None,ofile=None, verbose=True, AllowCloseAfter=True):
        """Exports data
        Arguments:
        set: the curve name. If none is passed, it uses the one selected by dataSetCB
        ofile: output file name or file handle. It will prompt if not provided
        verbose: set this to False to disable information popups
        AllowCloseAfter: set this to false if you want to ignore the checkbox in the dialog
        
        """
        if set is None: set=str(self.dataSetCB.currentText())

        self.updateText(set)
        if ofile is None:
            if set == self.allInSingleFile:
                name = "all.dat"
            else:
                name=set.replace('*','').replace('/','_').replace('\\','_')+".dat" #**lazy** sanitising of the set to *suggest* it as a filename
            ofile = Qt.QFileDialog.getSaveFileName( self, 'Export File Name', name, 'All Files (*)')
            if not ofile: return False
        try:
            if not isinstance(ofile,file):
                ofile=open(str(ofile),"w")
            print >>ofile, str(self.dataTE.toPlainText())
            ofile.close()
        except:
            Qt.QMessageBox.warning(self, "File saving failed","Failed to save file '%s'"%str(ofile.name),Qt.QMessageBox.Ok)
            raise
        if verbose: Qt.QMessageBox.information(self, "Set exported","Set saved to '%s'"%str(ofile.name),Qt.QMessageBox.Ok)
        if AllowCloseAfter and self.closeAfterCB.isChecked(): 
            self.accept() #closes the ExportData dialog with Accept state
        return True
        
    def exportAllData(self,preffix=None):
        """Exports all sets using a common preffix and appending 'XXX.dat', where XXX is a number starting at 001
        if preffix is not given, the user is prompted for a directory path"""
        if preffix is None:
            outputdir=Qt.QFileDialog.getExistingDirectory (self, 'Export Directory', Qt.QString())
            if not outputdir:return False
            preffix=os.path.join(str(outputdir),"set")
        for i,k in zip(range(len(self.datadict)),sorted(self.datadict.keys())):
            ofile="%s%03i.dat"%(preffix,i+1)
            try:
                self.exportCurrentData(set=k,ofile=ofile,verbose=False,AllowCloseAfter=False)
            except:
                return False
        #mend undesired side effect of updateText in the for loop
        self.updateText(self.allInMultipleFiles)
        Qt.QMessageBox.information(self, "All sets exported","%i set(s) exported to:\n%sXXX.dat"%(len(self.datadict),preffix),Qt.QMessageBox.Ok)
        if self.closeAfterCB.isChecked(): 
            self.accept() #closes the ExportData dialog with Accept state
        return True
    
    def onDataSetCBChange(self,key):
        key=str(key)
        self.updateText(key)
        
    def updateText(self, key=None):
        '''update the text edit that shows the preview of the data'''
        if key is None: key = str(self.dataSetCB.currentText())
        if key in (self.allInMultipleFiles, self.allInSingleFile):
            #check that all arrays have the same length and the same xdata and update header section
            header = "# DATASET= " 
            body = ""
            previous = None
            for curve_name in sorted(self.datadict.keys()):
                xdata, ydata = self.datadict[curve_name]
                if (previous is not None) and (previous != xdata):
                    if (key==self.allInSingleFile):
                        self.dataTE.clear()
                        Qt.QMessageBox.critical(self,\
                                    "Unable to display",\
                                    "X axes of all sets in the plot must be exactly the same for saving in a single file!",\
                                    Qt.QMessageBox.Ok)
                        return
                    else:
                        self.dataTE.clear()
                        self.dataTE.insertPlainText("Unable to display because abscissas are different.\n"\
                                                    "Curves will be saved each one in its own file")
                        return
                else:
                    previous = xdata
                    header +=' "abscissa", "%s"' % curve_name
            header+="\n# SNAPSHOT_TIME= %s\n"%self.datatime.isoformat('_')
            #if we reached this point x axes are equal, so fill the editor with the data
            for i, x in enumerate(previous):
                if self.xIsTime():
                    body += "%s" % t.isoformat('_')
                else:
                    body += "%g" % x
                for curve_name in sorted(self.datadict.keys()):
                    xdata, ydata = self.datadict[curve_name]
                    body += ("\t%g" % ydata[i])
                body+="\n"
            #fill text editor
            self.dataTE.clear()
            self.dataTE.insertPlainText(header+body)
            self.dataTE.moveCursor(Qt.QTextCursor.Start)
            if key == self.allInMultipleFiles:
                self.dataTE.setReadOnly(True)
            else:
                self.dataTE.setReadOnly(False)
        else:
            self.dataTE.setReadOnly(False)
            xdata,ydata=self.datadict[key]
            text='# DATASET= "%s"\n'%key
            text+="# SNAPSHOT_TIME= %s\n"%self.datatime.isoformat('_')
            if self.xIsTime():
                for x,y in zip(xdata, ydata):
                    t=datetime.fromtimestamp(x)
                    text+="%s\t%g\n"%(t.isoformat('_'),y)
            else:
                for x,y in zip(xdata, ydata):
                    text+="%g\t%g\n"%(x,y)
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
    app = Qt.QApplication(sys.argv)
    form = QDataExportDialog()
    form.show()
    sys.exit(app.exec_())

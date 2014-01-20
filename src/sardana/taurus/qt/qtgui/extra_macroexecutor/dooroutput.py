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
dooroutput.py: 
"""

from taurus.qt import Qt
import taurus.core

  
class DoorOutput(Qt.QPlainTextEdit):
    """Widget used for displaying changes of door's attributes: Output, Info, Warning and Error."""
    
    def __init__(self, parent = None):
        Qt.QTextEdit.__init__(self, parent)        
        self.setReadOnly(True)
        self.setFont(Qt.QFont("Courier",9))
        self.stopAction = Qt.QAction("Stop scrolling",self)
        self.stopAction.setCheckable(True)
        self.stopAction.setChecked(False)
        self._isStopped = False
                
    def onDoorOutputChanged(self, output):
        """call on output attribute changed"""
        txt ="<font color=\"Black\">"
        if output is None:
            return
        for line in output:
            txt+="OUTPUT  " + line.replace(' ', '&nbsp;')+"\n"
        txt += "</font>"
        self.appendHtmlText(txt)
        
    def onDoorInfoChanged(self, info):        
        """call on info attribute changed"""
        txt ="<font color=\"Black\">"
        if info is None:
            return
        
        for line in info:
            txt+="INFO  " + line.replace(' ', '&nbsp;')+"\n"
        txt += "</font>"
        self.appendHtmlText(txt)
        
    def onDoorWarningChanged(self, warning):
        """call on warning attribute changed"""        
        txt ="<font color=\"Black\">"
        if warning is None:
            return
        for line in warning:
            txt+="WARNING  " + line.replace(' ', '&nbsp;')+"\n"
        txt += "</font>"
        self.appendHtmlText(txt)
    
    def onDoorErrorChanged(self, error):
        """call on error attribute changed"""
        txt ="<font color=\"Red\">"
        if error is None:
            return
        for line in error:
            txt+="ERROR  " + line.replace(' ', '&nbsp;')+"\n"
        txt += "</font>"
        self.appendHtmlText(txt)
    
    def appendHtmlText(self, text):
        self.appendHtml(text)
        if not self._isStopped:
            self.moveCursor(Qt.QTextCursor.End)
    
    def contextMenuEvent(self,event):
        menu = self.createStandardContextMenu() 
        clearAction = Qt.QAction("Clear", menu)
        menu.addAction(clearAction)
        menu.addAction(self.stopAction)
        if not len(self.toPlainText()):
            clearAction.setEnabled(False) 

        Qt.QObject.connect(clearAction, Qt.SIGNAL("triggered()"), self.clear)
        Qt.QObject.connect(self.stopAction, Qt.SIGNAL("toggled(bool)"), self.stopScrolling)    
        menu.exec_(event.globalPos())
    
    def stopScrolling(self, stop):
        self._isStopped = stop
        
class DoorDebug(Qt.QPlainTextEdit):
    """Widget used for displaying changes of door's Debug attribute."""
    
    def __init__(self, parent = None):
        Qt.QTextEdit.__init__(self, parent)        
        self.setReadOnly(True)
        self.setFont(Qt.QFont("Courier",9))
        self.stopAction = Qt.QAction("Stop scrolling",self)
        self.stopAction.setCheckable(True)
        self.stopAction.setChecked(False)
        self._isStopped = False
        
    def onDoorDebugChanged(self, debug):
        """call on debug attribute changed"""
        if debug is None:
            return
        for line in debug: 
            self.appendPlainText("DEBUG  " + line)
        
        if not self._isStopped:
            self.moveCursor(Qt.QTextCursor.End)
        
    def contextMenuEvent(self,event):
        menu = self.createStandardContextMenu() 
        clearAction = Qt.QAction("Clear", menu)
        menu.addAction(clearAction)
        menu.addAction(self.stopAction)
        if not len(self.toPlainText()):
            clearAction.setEnabled(False) 
        
        Qt.QObject.connect(clearAction, Qt.SIGNAL("triggered()"), self.clear)
        Qt.QObject.connect(self.stopAction, Qt.SIGNAL("toggled(bool)"), self.stopScrolling)               
        menu.exec_(event.globalPos())
    
    def stopScrolling(self, stop):
        self._isStopped = stop
    
class DoorResult(Qt.QPlainTextEdit):
    """Widget used for displaying changes of door's Result attribute."""
    
    def __init__(self, parent = None):
        Qt.QTextEdit.__init__(self, parent)    
        self.setReadOnly(True)
        self.setFont(Qt.QFont("Courier",9))
        
    def onDoorResultChanged(self, result):
        """call on result attribute changed"""   
        if result is None:
            return
        for line in result:
            self.appendPlainText("RESULT  " + line)
        self.moveCursor(Qt.QTextCursor.End)
        
    def contextMenuEvent(self,event):
        menu = self.createStandardContextMenu() 
        clearAction = Qt.QAction("Clear", menu)
        menu.addAction(clearAction)
        if not len(self.toPlainText()):
            clearAction.setEnabled(False) 
        
        Qt.QObject.connect(clearAction, Qt.SIGNAL("triggered()"), self.clear)               
        menu.exec_(event.globalPos())


        
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# Door attributes listeners
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

class DoorAttrListener(Qt.QObject):
        
    def __init__(self, attrName):
        Qt.QObject.__init__(self)
        self.attrName = attrName
        self.attrObj = None
        
    def setDoorName(self, doorName):
        if not self.attrObj is None:
            self.attrObj.removeListener(self)
        self.attrObj = taurus.Attribute(doorName, self.attrName)
        self.attrObj.addListener(self)

    def eventReceived(self, src, type, value):
        if (type == taurus.core.taurusbasetypes.TaurusEventType.Error or
            type == taurus.core.taurusbasetypes.TaurusEventType.Config):
            return
        self.emit(Qt.SIGNAL('door%sChanged' % self.attrName), value.value)
        
if __name__=="__main__":
    import sys
    import taurus
    from taurus.qt.qtgui.application import TaurusApplication
    
    app = TaurusApplication(sys.argv)
    args = app.get_command_line_args()

    doorOutput = DoorOutput()
    if len(args) == 1:
        door = taurus.Device(args[0])
        Qt.QObject.connect(door, Qt.SIGNAL("outputUpdated"), doorOutput.onDoorOutputChanged)            
        Qt.QObject.connect(door, Qt.SIGNAL("infoUpdated"), doorOutput.onDoorInfoChanged)
        Qt.QObject.connect(door, Qt.SIGNAL("warningUpdated"), doorOutput.onDoorWarningChanged)
        Qt.QObject.connect(door, Qt.SIGNAL("errorUpdated"), doorOutput.onDoorErrorChanged)
    doorOutput.show()
    sys.exit(app.exec_())  
    

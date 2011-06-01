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

from PyQt4 import Qt
import taurus.core
        
        
class DoorOutput(Qt.QTextEdit):
    """Widget used for displaying changes of door's attributes: Output, Info, Warning and Error."""
    
    def __init__(self, parent = None):
        Qt.QTextEdit.__init__(self, parent)        
        self.setReadOnly(True)
        self.setFont(Qt.QFont("Courier",9))
                
    def onDoorOutputChanged(self, output):
        """call on output attribute changed"""
        self.setTextColor(Qt.Qt.black)
        if output is None:
            return
        for line in output:
            self.append("OUTPUT  " + line)
        self.moveCursor(Qt.QTextCursor.End)
    
    def onDoorInfoChanged(self, info):        
        """call on info attribute changed"""
        if info is None:
            return
        self.setTextColor(Qt.Qt.black)   
        for line in info: 
            self.append("INFO  " + line)
        self.moveCursor(Qt.QTextCursor.End)
        
    def onDoorWarningChanged(self, warning):
        """call on warning attribute changed"""        
        if warning is None:
            return
        self.setTextColor(Qt.Qt.black)
        for line in warning:
            self.append("WARNING  " + line)
        self.moveCursor(Qt.QTextCursor.End)
    
    def onDoorErrorChanged(self, error):
        """call on error attribute changed"""
        if error is None:
            return
        self.setTextColor(Qt.Qt.red)
        for line in error:
            self.append("ERROR  " + line)
        self.moveCursor(Qt.QTextCursor.End)
                        
    def contextMenuEvent(self,event):
        menu = self.createStandardContextMenu() 
        clearAction = Qt.QAction("Clear", menu)
        menu.addAction(clearAction)
        if not len(self.toPlainText()):
            clearAction.setEnabled(False) 
        
        Qt.QObject.connect(clearAction, Qt.SIGNAL("triggered()"), self.clear)               
        menu.exec_(event.globalPos())
        
class DoorDebug(Qt.QTextEdit):
    """Widget used for displaying changes of door's Debug attribute."""
    
    def __init__(self, parent = None):
        Qt.QTextEdit.__init__(self, parent)        
        self.setReadOnly(True)
        self.setFont(Qt.QFont("Courier",9))
        
    def onDoorDebugChanged(self, debug):
        """call on debug attribute changed"""
        if debug is None:
            return
        for line in debug: 
            self.append("DEBUG  " + line)
        self.moveCursor(Qt.QTextCursor.End)
        
    def contextMenuEvent(self,event):
        menu = self.createStandardContextMenu() 
        clearAction = Qt.QAction("Clear", menu)
        menu.addAction(clearAction)
        if not len(self.toPlainText()):
            clearAction.setEnabled(False) 
        
        Qt.QObject.connect(clearAction, Qt.SIGNAL("triggered()"), self.clear)               
        menu.exec_(event.globalPos())
        
class DoorResult(Qt.QTextEdit):
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
            self.append("RESULT  " + line)
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
        if (type == taurus.core.TaurusEventType.Error or
            type == taurus.core.TaurusEventType.Config):
            return
        self.emit(Qt.SIGNAL('door%sChanged' % self.attrName), value.value)

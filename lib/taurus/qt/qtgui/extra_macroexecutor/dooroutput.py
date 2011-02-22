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
        
#class DoorOutput(Qt.QTextEdit):
#    
#    def __init__(self, parent = None):
#        Qt.QTextEdit.__init__(self, parent)
#    
#        self._doorName = None
#
#        self._doorOutputListener = None
#        self._doorWarningListener = None
#        self._doorInfoListener = None
#        self._doorErrorListener = None
#        
#        self.setReadOnly(True)
#        self.setFont(Qt.QFont("Courier",9))
#        
#    def doorName(self):
#        return self._doorName
#    
#    def setDoorName(self, doorName):
#        self._doorName = doorName
#        
#    def doorOutputListener(self):
#        return self._doorOutputListener
#    
#    def setDoorOutputListener(self, doorOutputListener):
#        self._doorOutputListener = doorOutputListener
#        
#    def doorWarningListener(self):
#        return self._doorWarningListener
#    
#    def setDoorWarningListener(self, doorWarningListener):
#        self._doorWarningListener = doorWarningListener
#        
#    def doorInfoListener(self):
#        return self._doorInfoListener
#    
#    def setDoorInfoListener(self, doorInfoListener):
#        self._doorInfoListener = doorInfoListener
#        
#    def doorErrorListener(self):
#        return self._doorErrorListener
#    
#    def setDoorErrorListener(self, doorErrorListener):
#        self._doorErrorListener = doorErrorListener
#
##    def sizeHint(self):
##        return self.minimumSizeHint()
##
##    def minimumSizeHint(self):
##        return Qt.QSize(600,150)
#        
#    def onDoorChanged(self, doorName):
#        self.setDoorName(doorName)
#        self.resetListeners()
#    
#    def resetListeners(self):
#        
#        if not self.doorOutputListener() is None:
#            Qt.QObject.disconnect(self.doorOutputListener(),
#                                      Qt.SIGNAL("doorOutputChanged"),
#                                      self.onDoorOutputChanged)
#        if not self.doorInfoListener() is None:
#            Qt.QObject.disconnect(self.doorInfoListener(),
#                                      Qt.SIGNAL("doorInfoChanged"),
#                                      self.onDoorInfoChanged)
#        if not self.doorWarningListener() is None:
#            Qt.QObject.disconnect(self.doorWarningListener(),
#                                      Qt.SIGNAL("doorWarningChanged"),
#                                      self.onDoorWarningChanged)
#        if not self.doorErrorListener() is None:
#            Qt.QObject.disconnect(self.doorErrorListener(),
#                                      Qt.SIGNAL("doorErrorChanged"),
#                                      self.onDoorErrorChanged)
#            
#        self.clear()
#            
#        self.setDoorOutputListener(DoorAttrListener("Output"))
#        self.setDoorInfoListener(DoorAttrListener("Info"))
#        self.setDoorWarningListener(DoorAttrListener("Warning"))
#        self.setDoorErrorListener(DoorAttrListener("Error"))
#        
#        Qt.QObject.connect(self.doorOutputListener(),
#                               Qt.SIGNAL("doorOutputChanged"),
#                               self.onDoorOutputChanged)
#        Qt.QObject.connect(self.doorInfoListener(),
#                               Qt.SIGNAL("doorInfoChanged"),
#                               self.onDoorInfoChanged)
#        Qt.QObject.connect(self.doorWarningListener(),
#                               Qt.SIGNAL("doorWarningChanged"),
#                               self.onDoorWarningChanged)
#        Qt.QObject.connect(self.doorErrorListener(),
#                               Qt.SIGNAL("doorErrorChanged"),
#                               self.onDoorErrorChanged)
#        
#        self.doorOutputListener().setDoorName(self.doorName())
#        self.doorInfoListener().setDoorName(self.doorName())
#        self.doorWarningListener().setDoorName(self.doorName())
#        self.doorErrorListener().setDoorName(self.doorName())
#    
#    def onDoorOutputChanged(self, eventValue):
#        """call on output attribute changed"""
#        if eventValue is None: return
#        self.setTextColor(Qt.Qt.black)
#        for outputLine in eventValue:
#            self.append("OUTPUT  " + outputLine)
#        self.moveCursor(Qt.QTextCursor.End)
#    
#    def onDoorInfoChanged(self, eventValue):        
#        """call on info attribute changed"""
#        if eventValue is None: return
#        self.setTextColor(Qt.Qt.black)
#        for infoLine in eventValue:
#            self.append("INFO  " + infoLine)
#        self.moveCursor(Qt.QTextCursor.End)
#        
#    def onDoorErrorChanged(self, eventValue):
#        """call on error attribute changed"""
#        if eventValue is None: return
#        self.setTextColor(Qt.Qt.red)
#        for errorLine in eventValue:
#            self.append("ERROR  " + errorLine)
#        self.moveCursor(Qt.QTextCursor.End)
#                
#    def onDoorWarningChanged(self, eventValue):
#        """call on warning attribute changed"""        
#        if eventValue is None: return
#        self.setTextColor(Qt.Qt.black)
#        for warningLine in eventValue:
#            self.append("WARNING  " + warningLine)
#        self.moveCursor(Qt.QTextCursor.End)
#        
#    def contextMenuEvent(self,event):
#        menu = self.createStandardContextMenu() 
#        clearAction = Qt.QAction("Clear", menu)
#        menu.addAction(clearAction)
#        if not len(self.toPlainText()):
#            clearAction.setEnabled(False) 
#        
#        Qt.QObject.connect(clearAction, Qt.SIGNAL("triggered()"), self.clear)               
#        menu.exec_(event.globalPos())
 
        
#class DoorDebug(Qt.QTextEdit):
#    
#    def __init__(self, parent = None):
#        Qt.QTextEdit.__init__(self, parent)
#        
#        self._doorName = None
#
#        self._doorDebugListener = None
#        
#        self.setReadOnly(True)
#        self.setFont(Qt.QFont("Courier",9))
#    
#    def doorName(self):
#        return self._doorName
#    
#    def setDoorName(self, doorName):
#        self._doorName = doorName
#        
#    def doorDebugListener(self):
#        return self._doorDebugListener
#    
#    def setDoorDebugListener(self, doorDebugListener):
#        self._doorDebugListener = doorDebugListener
#
##    def sizeHint(self):
##        return self.minimumSizeHint()
##
##    def minimumSizeHint(self):
##        return Qt.QSize(600,150)
#    
#    def onDoorChanged(self, doorName):
#        self.setDoorName(doorName)
#        self.resetListeners()
#    
#    def resetListeners(self):
#        
#        if not self.doorDebugListener() is None:
#            Qt.QObject.disconnect(self.doorDebugListener(),
#                                      Qt.SIGNAL("doorDebugChanged"),
#                                      self.onDoorDebugChanged)
#            
#        self.clear()
#            
#        self.setDoorDebugListener(DoorAttrListener("Debug"))
#        
#        Qt.QObject.connect(self.doorDebugListener(),
#                               Qt.SIGNAL("doorDebugChanged"),
#                               self.onDoorDebugChanged)
#        
#        self._doorDebugListener.setDoorName(self._doorName)
#        
#    def onDoorDebugChanged(self, eventValue):
#        """call on debug attribute changed"""
#        if eventValue is None: return
#        for debugLine in eventValue: 
#            self.append("DEBUG  " + debugLine)
#        self.moveCursor(Qt.QTextCursor.End)
#        
#    def contextMenuEvent(self,event):
#        menu = self.createStandardContextMenu() 
#        clearAction = Qt.QAction("Clear", menu)
#        menu.addAction(clearAction)
#        if not len(self.toPlainText()):
#            clearAction.setEnabled(False) 
#        
#        Qt.QObject.connect(clearAction, Qt.SIGNAL("triggered()"), self.clear)               
#        menu.exec_(event.globalPos())


#class DoorResult(Qt.QTextEdit):
#    
#    def __init__(self, parent = None):
#        Qt.QTextEdit.__init__(self, parent)
#        
#        self._doorName = None
#
#        self._doorResultListener = None
#        
#        self.setReadOnly(True)
#        self.setFont(Qt.QFont("Courier",9))
#        
#    def doorName(self):
#        return self._doorName
#    
#    def setDoorName(self, doorName):
#        self._doorName = doorName
#        
#    def doorResultListener(self):
#        return self._doorResultListener
#    
#    def setDoorResultListener(self, doorResultListener):
#        self._doorResultListener = doorResultListener
#
##    def sizeHint(self):
##        return self.minimumSizeHint()
##
##    def minimumSizeHint(self):
##        return Qt.QSize(600,150)
#    
#    def onDoorChanged(self, doorName):
#        self.setDoorName(doorName)
#        self.resetListeners()
#    
#    def resetListeners(self):
#        if not self.doorResultListener() is None:
#            Qt.QObject.disconnect(self.doorResultListener(),
#                                      Qt.SIGNAL("doorResultChanged"),
#                                      self.onDoorResultChanged)
#            
#        self.clear()
#            
#        self.setDoorResultListener(DoorAttrListener("Result"))
#        
#        Qt.QObject.connect(self.doorResultListener(),
#                               Qt.SIGNAL("doorResultChanged"),
#                               self.onDoorResultChanged)
#        
#        self.doorResultListener().setDoorName(self.doorName())
#        
#    def onDoorResultChanged(self, eventValue):
#        """call on result attribute changed"""
#        if eventValue is None: return        
#        for resultLine in eventValue:
#            self.append("RESULT  " + resultLine)
#        self.moveCursor(Qt.QTextCursor.End)
#        
#    def contextMenuEvent(self,event):
#        menu = self.createStandardContextMenu() 
#        clearAction = Qt.QAction("Clear", menu)
#        menu.addAction(clearAction)
#        if not len(self.toPlainText()):
#            clearAction.setEnabled(False) 
#        
#        Qt.QObject.connect(clearAction, Qt.SIGNAL("triggered()"), self.clear)               
#        menu.exec_(event.globalPos())
        
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

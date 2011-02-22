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

"""MacroServer extension for taurus Qt"""

__all__ = ["QDoor", "QMacroServer"]

import taurus.core
from taurus.core.tango.macroserver import BaseMacroServer, BaseDoor

from PyQt4 import Qt

CHANGE_EVTS = (taurus.core.TaurusEventType.Change, taurus.core.TaurusEventType.Periodic)

class QDoor(Qt.QObject, BaseDoor):
    
    __pyqtSignals__ = ["resultUpdated","recordDataUpdated", "macroStatusUpdated"]
    __pyqtSignals__ += [ "%sUpdated" % l.lower() for l in BaseDoor.log_streams ]
    
    def __init__(self, name, qt_parent=None, **kw):
        self.call__init__wo_kw(Qt.QObject, qt_parent)
        self.call__init__(BaseDoor, name, **kw)
    
    def resultReceived(self, log_name, result):
        res = BaseDoor.resultReceived(self, log_name, result)
        self.emit(Qt.SIGNAL("resultUpdated"))
        return res
    
    def recordDataReceived(self, s, t, v):
        if t not in CHANGE_EVTS: return
        res = BaseDoor.recordDataReceived(self, s, t, v)
        self.emit(Qt.SIGNAL("recordDataUpdated"), res)
        return res
        
    def macroStatusReceived(self, s, t, v):
        res = BaseDoor.macroStatusReceived(self, s, t, v)
        if t == taurus.core.TaurusEventType.Error:
            macro = None
        else:
            macro = self.getRunningMacro()
        if macro is None: return
        self.emit(Qt.SIGNAL("macroStatusUpdated"), (macro, res))
        return res
    
    def logReceived(self, log_name, output):
        res = BaseDoor.logReceived(self, log_name, output)
        self.emit(Qt.SIGNAL("%sUpdated" % log_name.lower()), output)
        return res


class QMacroServer(Qt.QObject, BaseMacroServer):
    
    def __init__(self, name, qt_parent=None, **kw):
        self.call__init__wo_kw(Qt.QObject, qt_parent)
        self.call__init__(BaseMacroServer, name, **kw)
        
    def typesChanged(self, s, t, v):
        res = BaseMacroServer.typesChanged(self, s, t, v)
        self.emit(Qt.SIGNAL("typesUpdated"))
        return res
    
    def elementsChanged(self, s, t, v):
        res = BaseMacroServer.elementsChanged(self, s, t, v)
        self.emit(Qt.SIGNAL("elementsUpdated"))
        return res
    
    def macrosChanged(self, s, t, v):
        res = BaseMacroServer.macrosChanged(self, s, t, v)
        self.emit(Qt.SIGNAL("macrosUpdated"))
        return res
    

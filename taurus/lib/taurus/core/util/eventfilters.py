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

"""event filters library to be used with :meth:`taurus.qt.qtgui.base.TaurusBaseComponent.setFilters`"""

import PyTango
import taurus

def IGNORE_ALL(s, t, v):
    '''Will discard all events'''
    return None

def ONLY_CHANGE(s, t, v):
    '''Only change events pass'''
    if t == taurus.core.taurusbasetypes.TaurusEventType.Change: return s,t,v
    else: return None

def IGNORE_CHANGE(s, t, v):
    '''Config events are discarded'''
    if t != taurus.core.taurusbasetypes.TaurusEventType.Change: return s,t,v
    else: return None

def ONLY_CHANGE_AND_PERIODIC(s, t, v):
    '''Only change events pass'''
    if t in [taurus.core.taurusbasetypes.TaurusEventType.Change, taurus.core.taurusbasetypes.TaurusEventType.Periodic]: return s,t,v
    else: return None

def IGNORE_CHANGE_AND_PERIODIC(s, t, v):
    '''Config events are discarded'''
    if t not in [taurus.core.taurusbasetypes.TaurusEventType.Change, taurus.core.taurusbasetypes.TaurusEventType.Periodic]: return s,t,v
    else: return None
    
def ONLY_CONFIG(s, t, v):
    '''Only config events pass'''
    if t == taurus.core.taurusbasetypes.TaurusEventType.Config: return s,t,v
    else: return None
    
def IGNORE_CONFIG(s, t, v):
    '''Config events are discarded'''
    if t != taurus.core.taurusbasetypes.TaurusEventType.Config: return s,t,v
    else: return None
    
def ONLY_VALID(s, t, v):
    '''Only events whose quality is VALID pass'''
    if getattr(v,'quality',None) == PyTango.AttrQuality.ATTR_VALID: return s,t,v
    else: return None
    
def IGNORE_FAKE(s, t, v):
    '''Only events with actual value (!=None) pass'''
    if v is not None: return s,t,v
    else: return None


class EventValueMap(dict):
    """A filter destined to change the original value into another one according
    to a given map. Example:
           
        filter = EventValueMap({1:"OPEN", 2:"CHANGING", 3:"CLOSED"})
       
    this will create a filter that changes the integer value of the event
    into a string. The event type is changed according to the python type in
    the map value.
       
    For now it only supports simple types: str, int, long, float, bool
    """

    PYTYPE_TO_TANGO = {
        str   : PyTango.DevString,
        int   : PyTango.DevLong,
        long  : PyTango.DevLong64,
        float : PyTango.DevDouble,
        bool  : PyTango.DevBoolean,
    }

    def __call__(self, s, t, v):
        if not t in (taurus.core.taurusbasetypes.TaurusEventType.Change, taurus.core.taurusbasetypes.TaurusEventType.Periodic):
            return s, t, v
        if v is None:
            return s, t, v
        
        # make a copy
        v = PyTango.DeviceAttribute(v)
        
        v.value = self.get(v.value, v.value)
        
        v.type = EventValueMap.PYTYPE_TO_TANGO.get(type(v.value), v.type)
        return s, t, v
        
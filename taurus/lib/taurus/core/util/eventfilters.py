#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus
## 
## http://taurus-scada.org
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

"""event filters library to be used with 
:meth:`taurus.qt.qtgui.base.TaurusBaseComponent.setFilters`"""

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
    if t in [taurus.core.taurusbasetypes.TaurusEventType.Change, 
             taurus.core.taurusbasetypes.TaurusEventType.Periodic]: 
        return s,t,v
    else: return None

def IGNORE_CHANGE_AND_PERIODIC(s, t, v):
    '''Config events are discarded'''
    if t not in [taurus.core.taurusbasetypes.TaurusEventType.Change, 
                 taurus.core.taurusbasetypes.TaurusEventType.Periodic]: 
        return s,t,v
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
    to a given map. Example::
           
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
        if not t in (taurus.core.taurusbasetypes.TaurusEventType.Change, 
                     taurus.core.taurusbasetypes.TaurusEventType.Periodic):
            return s, t, v
        if v is None:
            return s, t, v
        
        # make a copy
        v = PyTango.DeviceAttribute(v)
        
        v.value = self.get(v.value, v.value)
        
        v.type = EventValueMap.PYTYPE_TO_TANGO.get(type(v.value), v.type)
        return s, t, v


class RepeatedEventFilter(object):
    """
    The instances of this class will be callables that can be used as filters 
    of repeated-value events. 
    If the event type is Change or Periodic, it will only pass when its 
    evt_value.value is different from that of the last event received from the 
    same source and type. If evt_value.value is not available in the current 
    event, the whole evt_value is used for comparison and as a future reference.
    
    This is useful to avoid processing repetitive events.
    
    Note that you cannot use this class as a filter: you need to use an 
    instance of it.
    
    Note 2: Use a different instance each time you insert this filter 
    into a different widget unless you *really* know what you are doing.
    
    Example of usage::
           
        filters = [RepeatedEventFilter(), IGNORE_CONFIG]
        filterEvent(s, t, v, filters)
        
    """
    def __init__(self):
        self._lastValues = {}

    def __call__(self, s, t, v):
        # restrict this  filter only to change and periodic events. 
        if ONLY_CHANGE_AND_PERIODIC(s, t, v) is None:
            return s,t,v
        # block event if we recorded one before with same src, type and v.value
        new_value = getattr(v, 'value', v)
        try:
            if self._lastValues[(s, t)] == new_value:
                return None
        except KeyError:
            pass
        # if it was't blocked, store src, type and v.value for future checks
        self._lastValues[(s, t)] =  new_value
        return s, t, v


def filterEvent(evt_src=-1, evt_type=-1, evt_value=-1, filters=()):
    """The event is processed by each and all filters in strict order
    unless one of them returns None (in which case the event is discarded)

    :param evt_src: (object) object that triggered the event
    :param evt_type: (taurus.core.taurusbasetypes.TaurusEventType) type of event
    :param evt_value: (object) event value
    :param filters: (sequence<callable>) a sequence of callables, each returning
                    either None (to discard the event) or the tuple (with 
                    possibly transformed values) of 
                    (evt_src, evt_type, evt_value)
    
    :return: (None or tuple) The result of piping the event through the given 
             filters.
    """
    evt = evt_src, evt_type, evt_value

    for f in filters:
        evt = f(*evt)
        if evt is None:
            return None
    return evt

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

"""This module contains the base TaurusModel class"""

__all__ = ["TaurusModel"]

__docformat__ = "restructuredtext"

import weakref
import operator
import threading

from .util.log import Logger
from .util.event import CallableRef, BoundMethodWeakref
from .taurusbasetypes import TaurusEventType, MatchLevel

class TaurusModel(Logger):
    
    RegularEvent = (TaurusEventType.Change, TaurusEventType.Config, TaurusEventType.Periodic)

    def __init__(self,full_name, parent, serializationMode=None):
        v = self.getNameValidator()
        self._full_name, self._norm_name, self._simp_name = v.getNames(full_name, self.factory())
        
        if self._full_name is None and self._norm_name and self._simp_name is None:
            self.trace("invalid name")
        
        name = self._simp_name or self._norm_name or self._full_name or 'TaurusModel'
        self.call__init__(Logger, name, parent)
        
        if serializationMode is None:
            s_obj = parent
            if s_obj is None:
                s_obj = self.factory()
                serializationMode = s_obj.getSerializationMode()
        self._serialization_mode = serializationMode
        
        try:
            self._parentObj = weakref.ref(parent)
        except Exception:
            self._parentObj = None
        self._listeners = []

    def __str__name__(self, name):
        return '{0}({1})'.format(self.__class__.__name__, name)
    
    def __str__(self):
        return self.__str__name__(self.getNormalName())

    def __repr__(self):
        return self.__str__name__(self.getFullName())
    
    def cleanUp(self):
        self.trace("[TaurusModel] cleanUp")
        #self._parentObj = None
        self._listeners = None
        Logger.cleanUp(self)
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for Factory access
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-   
    
    @classmethod
    def factory(cls):
        raise RuntimeError("TaurusModel::factory cannot be called")

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for naming
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    

    @classmethod
    def getTaurusElementType(cls):
        raise RuntimeError("TaurusModel::getTaurusElementType cannot be called")

    def getFullName(self):
        return self._full_name
    
    def getNormalName(self):
        return self._norm_name

    def getSimpleName(self):
        return self._simp_name

    @classmethod
    def isValid(cls, name, level = MatchLevel.ANY):
        return cls.getNameValidator().isValid(name, level)

    @classmethod
    def buildModelName(cls, parent_model, relative_name):
        raise RuntimeError("TaurusModel::buildModelName cannot be called")
    
    @classmethod
    def getNameValidator(cls):
        raise RuntimeError("TaurusModel::getNameValidator cannot be called")
            
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for hierarchy access 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
        
    def getParentObj(self):
        if self._parentObj is None: return None
        return self._parentObj()
    
    def getChildObj(self,child_name):
        return None

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for serialization
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def setSerializationMode(self, mode):
        """Sets the serialization mode for the system.
        
        :param mode: (TaurusSerializationMode) the new serialization mode"""
        self._serialization_mode = mode
    
    def getSerializationMode(self):
        """Gives the serialization operation mode.
        
        :return: (TaurusSerializationMode) the current serialization mode"""
        return self._serialization_mode
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for value access 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def getValueObj(self,cache=True):
        raise RuntimeError("TaurusModel::getValueObj cannot be called")
    
    def getDisplayValue(self,cache=True):
        raise RuntimeError("TaurusModel::getDisplayValue cannot be called")
    
    def getDisplayDescrObj(self,cache=True):
        """A brief description of the model. Can be used as tooltip, for example"""
        raise RuntimeError("TaurusModel::getDisplayDescrObj cannot be called")
    
    def getDisplayName(self,cache=True, complete=True):
        full_name = self.getFullName()
        normal_name = self.getNormalName()
        simple_name = self.getSimpleName()
        if simple_name:
            ret = simple_name 
            if complete: ret += " (" + normal_name.upper() + ")"
        elif normal_name:
            ret = normal_name.upper()
        else:
            ret = full_name.upper()
        return ret
            
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for listeners
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def _listenerDied(self, weak_listener):
        if self._listeners is None: 
            return
        try:
            self._listeners.remove(weak_listener)
        except Exception,e:
            pass
        
    def _getCallableRef(self, listener, cb = None):
        #return weakref.ref(listener, self._listenerDied)
        meth = getattr(listener, 'eventReceived', None)
        if meth is not None and operator.isCallable(meth):
            return weakref.ref(listener, cb)
        else:
            return CallableRef(listener, cb)
    
    def addListener(self, listener):
        if self._listeners is None or listener is None: 
            return False
        
        weak_listener = self._getCallableRef(listener, self._listenerDied)
        if weak_listener in self._listeners:
            return False
        self._listeners.append(weak_listener)
        return True
    
    def removeListener(self, listener):
        if self._listeners is None: 
            return
        weak_listener = self._getCallableRef(listener)
        try:
            self._listeners.remove(weak_listener)
        except Exception,e:
            return False
        return True
                    
    def forceListening(self):
        class __DummyListener:
            def eventReceived(self, *args):
                pass
        if not hasattr(self, '__dummyListener') or self.__dummyListener is None:
            self.__dummyListener = __DummyListener()
            self.addListener(self.__dummyListener)
        
    def unforceListening(self):
        if hasattr(self, '__dummyListener') and self.__dummyListener is not None:
            self.removeListener(self.__dummyListener)
            self.__dummyListener = None
    
    def deleteListener(self, listener):
        self.deprecated("Use removeListener(listener) instead")
        self.removeListener(listener)
        
    def hasListeners(self):
        """ returns True if anybody is listening to events from this attribute """
        if self._listeners is None: 
            return False
        return len(self._listeners) > 0
        
    def fireEvent(self, event_type, event_value, listeners=None):
        """sends an event to all listeners or a specific one"""
        
        if listeners is None:
            listeners = self._listeners
        
        if listeners is None:
            return
        
        if not operator.isSequenceType(listeners):
            listeners = listeners,
            
        for listener in listeners:
            if isinstance(listener, weakref.ref) or isinstance(listener, BoundMethodWeakref):
                l = listener()
            else:
                l = listener
            if l is None: continue
            meth = getattr(l, 'eventReceived', None)
            if meth is not None and operator.isCallable(meth):
                l.eventReceived(self, event_type, event_value)
            elif operator.isCallable(l):
                l(self, event_type, event_value)
            
    def isWritable(self):
        return False
        

#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
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

from taurus import Device, Factory

from sardana import ElementType
from sardana.sardanaevent import EventType

from msbase import MSObject


class MSDoor(MSObject):
    """Sardana door object"""
    
    def __init__(self, **kwargs):
        self._state = None
        self._status = None
        self._result = None
        self._macro_status = None
        self._record_data = None
        MSObject.__init__(self, **kwargs)
    
    def get_type(self):
        return ElementType.Door
    
    def get_macro_executor(self):
        return self.macro_server.macro_manager.getMacroExecutor(self)
    
    macro_executor = property(get_macro_executor)
    
    def get_running_macro(self):
        return self.macro_executor.getRunningMacro()
    
    running_macro = property(get_running_macro)
    
    def get_state(self):
        return self._state
    
    def set_state(self, state, propagate=1):
        self._state = state
        self.fire_event(EventType("state", priority=propagate), state)
    
    state = property(get_state, set_state)
    
    def get_status(self):
        return self._status
    
    def set_status(self, status, propagate=1):
        self._status = status
        self.fire_event(EventType("status", priority=propagate), status)
    
    status = property(get_status, set_status)
    
    def get_result(self):
        return self._result
    
    def set_result(self, result, propagate=1):
        self._result = result
        self.fire_event(EventType("result", priority=propagate), result)
    
    result = property(get_result, set_result)
    
    def get_macro_status(self):
        return self._macro_status
    
    def set_macro_status(self, macro_status, propagate=1):
        self._macro_status = macro_status
        self.fire_event(EventType("macrostatus", priority=propagate),
                        macro_status)
    
    result = property(get_result, set_result)
    
    def get_record_data(self):
        return self._record_data
    
    def set_record_data(self, record_data, codec=None, propagate=1):
        self._record_data = record_data
        self.fire_event(EventType("recorddata", priority=propagate),
                        record_data)
    
    record_data = property(get_record_data, set_record_data)
    
    def get_env(self, key=None, macro_name=None):
        """Gets the environment with the context for this door matching the
        given parameters:
        
        - macro_name defines the context where to look for the environment. If
          None, the global environment is used. If macro name is given the
          environment in the context of that macro is given
        - If key is None it returns the complete environment, otherwise
          key must be a string containing the environment variable name.
        
        :param key:
            environment variable name [default: None, meaning all environment]
        :type key: str
        :param macro_name:
            local context for a given macro [default: None, meaning no macro
            context is used]
        :type macro_name: str
        
        :raises: UnknownEnv"""
        return self.macro_server.environment_manager.getAllDoorEnv(self.name)
    
    def __getattr__(self, name):
        """Get methods from macro server"""
        return getattr(self.macro_server, name)
    
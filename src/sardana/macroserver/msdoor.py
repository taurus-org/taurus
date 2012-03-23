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

"""This module contains the class definition for the macro server door"""

__all__ = ["MacroProxy", "MSDoor",]

__docformat__ = 'restructuredtext'

import weakref

from taurus import Device, Factory
from taurus.core.util import Logger

from sardana import ElementType
from sardana.sardanaevent import EventType

from msbase import MSObject


class MacroProxy(object):
    
    def __init__(self, door, macro_meta):
        self._door = weakref.ref(door)
        self._macro_meta = weakref.ref(macro_meta)

    @property
    def door(self):
        return self._door()

    @property
    def macro_info(self):
        return self._macro_meta()
    
    def __call__(self, *args, **kwargs):
        door = self.door
        parent_macro = door.get_running_macro()
        parent_macro.syncLog()
        executor = parent_macro.executor
        opts=dict(parent_macro=parent_macro, executor=executor)
        kwargs.update(opts)
        eargs = [self.macro_info.name]
        eargs.extend(args)
        return parent_macro.execMacro(*eargs, **kwargs)
    

class MacroProxyCache(dict):
    
    def __init__(self, door):
        self._door = weakref.ref(door)
        self.rebuild()
    
    @property
    def door(self):
        return self._door()
    
    def rebuild(self):
        self.clear()
        door = self.door
        macros = self.door.get_macros()
        for macro_name, macro_meta in macros.items():
            self[macro_name] = MacroProxy(door, macro_meta)


class MSDoor(MSObject):
    """Sardana door object"""
    
    def __init__(self, **kwargs):
        self._state = None
        self._status = None
        self._result = None
        self._macro_status = None
        self._record_data = None
        self._macro_proxy_cache = None
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
    
    def set_env(self, key, value):
        return self.macro_server.set_env(key, value)
    
    def _build_macro_proxy_cache(self):
        self._macro_proxy_cache = MacroProxyCache(self)
    
    def get_macro_proxies(self):
        if self._macro_proxy_cache is None:
            self._macro_proxy_cache = MacroProxyCache(self)
        return self._macro_proxy_cache
    
    def run_macro(self, par_str_list, asynch=False):
        if isinstance(par_str_list, (str, unicode)):
            par_str_list = par_str_list,

        if not hasattr(self, "Output"):
            import sys, logging
            import taurus.core.util
            Logger.addLevelName(15, "OUTPUT")
            
            def output(loggable, msg, *args, **kw):
                loggable.getLogObj().log(Logger.Output, msg, *args, **kw)
            Logger.output = output
            
            Logger.disableLogOutput()
            Logger.setLogLevel(Logger.Output)
            #filter = taurus.core.util.LogFilter(level=Logger.Output)
            formatter = logging.Formatter(fmt="%(message)s")
            Logger.setLogFormat("%(message)s")
            handler = logging.StreamHandler(stream=sys.stdout)
            #handler.addFilter(filter)
            Logger.addRootLogHandler(handler)
            #handler.setFormatter(formatter)
            #logger.addHandler(handler)
            #logger.addFilter(filter)
            self.__logging_info = handler, filter, formatter
            
            # result of a macro
            #Logger.addLevelName(18, "RESULT")

        return self.macro_executor.run(par_str_list, asynch=asynch)
    
    def __getattr__(self, name):
        """Get methods from macro server"""
        return getattr(self.macro_server, name)

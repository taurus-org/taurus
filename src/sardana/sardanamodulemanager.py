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

"""This module is part of the Python Sardana libray. It defines the base classes
for module manager"""

__all__ = ["ModuleManager"]

__docformat__ = 'restructuredtext'

import sys
import os
import imp

from taurus.core import ManagerState
from taurus.core.util import Singleton, Logger

class ModuleManager(Singleton, Logger):
    
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self._state = ManagerState.UNINITIALIZED
        self.call__init__(Logger, name)
        self.reInit()
    
    def reInit(self):
        if self._state == ManagerState.INITED:
            return
        
        # dict<str, module>
        # key   - module name (without path and without extension)
        # value - python module object reference
        self._modules = {}
        
        self._state = ManagerState.INITED
    
    def cleanUp(self):
        if self._state == ManagerState.CLEANED:
            return

        self.unloadModules()

        self._modules = None

        self._state = ManagerState.CLEANED
    
    def reloadModule(self, module_name, path=None, reload=True):
        """Loads/reloads the given module name"""
        
        if not reload:
            return self.loadModule(module_name, path=path)
        
        self.unloadModule(module_name)
        
        m, trace, file = None, None, None
        try:
            file, pathname, desc = imp.find_module(module_name, path)
            self.info("(re)loading module %s...", module_name)
            m = imp.load_module(module_name, file, pathname, desc)
        except:
            self.error("Error (re)loading module %s", module_name)
            self.debug("Details:", exc_info=1)
            raise
        finally:
            if file is not None:
                file.close()
        
        if m is None:
            return
        
        self._modules[module_name] = m
        
        return m
    
    def loadModule(self, module_name, path=None):
        """Loads the given module name"""
        
        if module_name in sys.modules:
            return sys.modules[module_name]
        
        orig_path = list(sys.path)
        try:
            added = 0
            if path is not None:
                sys.path = path + sys.path
            self.info("loading module %s...", module_name)
            m = __import__(module_name, globals(), locals(), [], -1)
        except:
            self.error("Error loading module %s", module_name)
            self.debug("Details:", exc_info=1)
            raise
        
        if m is None:
            return
        
        self._modules[module_name] = m
        
        return m
    
    def unloadModule(self, module_name):
        """Unloads the given module name"""
        if self._modules.has_key(module_name):
            self.debug("unloading module %s" % module_name)
            assert(sys.modules.has_key(module_name))
            self._modules.pop(module_name)
            del sys.modules[module_name]
    
    def unloadModules(self, module_list = None):
        """Unloads the given module name"""
        modules = module_list or self._modules.keys()
        for module in modules:
            self.unloadModule(module, False)
    
    def getModule(self, module_name):
        """Returns the module object for the given module name"""
        m = self._modules.get(module_name)
        if m is None:
            m = self.reloadModule(module_name)
        return m

    def getModuleNames(self):
        module_names = self._modules.keys()
        module_names.sort()
        return module_names
    
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

from __future__ import with_statement

__all__ = ["ModuleManager"]

__docformat__ = 'restructuredtext'

import sys
import imp
import threading

from taurus.core import ManagerState
from taurus.core.util import Singleton, Logger

from sardanamanager import SardanaIDManager

class PathManager(SardanaIDManager):
    
    def __init__(self):
        SardanaIDManager.__init__(self)
        self._orig_path = list(sys.path)
        self._path_lock = threading.Lock()
        #: dict<int(path_id), list<int(path start index), list<str(path)>>
        self._path_info = {}
    
    @staticmethod
    def _decode_path(path):
        p = []
        for item in path:
            p.extend(item.split(":"))
        return p
    
    def add_python_path(self, path):
        """Adds a new path to the python path.
        
        :param path:
            a sequence of strings each string may contain an absolute path or a
            list of ":" or "\n" separated absolute paths
        :type path: list<str>
        :return:
            a path id identifying the changes that were made to sys.path. This
            ID can be used in :meth:`remove_path` to remove only the added path
        :rtype: int"""
        path = self._decode_path(path)
        path_len = len(path)
        pif = self._path_info
        
        with self._path_lock:
            path_id = self.get_new_id()
            
            for p_id, p_info in pif.items():
                p_info[0] += path_len
            
            pif[path_id] = [0, path]
            sys.path = path + sys.path
        return path_id
    
    def remove_python_path(self, path_id):
        """Removes the path given by the path_id
        
        :param path_id:
            a path id identifying specific changes that were made to sys.path
        :type path_id: int"""
        pif = self._path_info
        start, path = pif[path_id]
        path_len = len(path)
        
        with self._path_lock:
            sys.path = sys.path[:start+1] + sys.path[start+path_len:]
            del pif[path_id]
    
    def reset_python_path(self):
        with self._path_lock:
            sys.path = list(self._orig_path)
            self._path_info = {}
        

class ModuleManager(Singleton, Logger):
    """This class handles python module loading/reloading and unloading."""
    
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self._state = ManagerState.UNINITIALIZED
        self._path_manager = PathManager()
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
    
    def reset_python_path(self):
        return self._path_manager.reset_python_path()
    
    def remove_python_path(self, path_id):
        return self._path_manager.remove_python_path(path_id)
    
    def add_python_path(self, path):
        return self._path_manager.add_python_path(path)
    
    def findFullModuleName(self, module_name, path=None):
        file = None
        try:
            file, pathname, desc = imp.find_module(module_name, path)
        finally:
            if file is not None:
                file.close()
        return pathname
    
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
        """Loads the given module name. If the module has been already loaded
        into this python interpreter, nothing is done.
        
        :param module_name: the module to be loaded.
        :type module_name: str
        :param path: list of paths to look for modules [default: None]
        :type path: seq<str> or None
        :return: python module
        
        :raises: ImportError"""
        
        if module_name in sys.modules:
            return sys.modules[module_name]
        
        orig_path = list(sys.path)
        try:
            if path is not None:
                sys.path = path + sys.path
            self.info("loading module %s...", module_name)
            m = __import__(module_name, globals(), locals(), [], -1)
        except:
            self.error("Error loading module %s", module_name)
            self.debug("Details:", exc_info=1)
            raise
        finally:
            sys.path = orig_path
        
        self._modules[module_name] = m
        
        return m
    
    def unloadModule(self, module_name):
        """Unloads the given module name"""
        if self._modules.has_key(module_name):
            self.debug("unloading module %s" % module_name)
            assert(sys.modules.has_key(module_name))
            self._modules.pop(module_name)
            del sys.modules[module_name]
    
    def unloadModules(self, module_list=None):
        """Unloads the given module name"""
        modules = module_list or self._modules.keys()
        for module in modules:
            self.unloadModule(module)
    
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
    

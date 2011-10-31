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

"""This module contains the definition of the macroserver data type manager"""

__all__ = ["TypeManager"]

__docformat__ = 'restructuredtext'

import os
import inspect

from taurus.core import ManagerState
from taurus.core.util import InfoIt, Singleton, Logger, ListEventGenerator

from sardana.sardanamodulemanager import ModuleManager

from parameter import Type, ParamType, AbstractParamTypes


class TypeManager(Singleton, Logger):

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self._state = ManagerState.UNINITIALIZED
        self.call__init__(Logger, name)
        self._type_list_obj = ListEventGenerator('TypeList')

        self.reInit()
    
    def reInit(self):
        if self._state == ManagerState.INITED:
            return

        # dict<str, dict<str,class<ParamType>>
        # key   - module name (without path and without extension)
        # value - a dict where:
        #         key   - type name
        #         value - class object implementing the Type
        self._modules = {}
        
        # dict<str, ParamType>
        # key   - type name
        # value - object which inherits from ParamType
        self._inst_dict = {}
        
        self._state = ManagerState.INITED
    
    def cleanUp(self):
        if self._state == ManagerState.CLEANED:
            return
        
        if self._modules:
            mm = ModuleManager()
            for module_name, types_dict in self._modules.items():
                for type_name in types_dict:
                    Type.removeType(type_name)
                mm.unloadModule(module_name)
                
        self._modules = None
        self._inst_dict = None
        
        self._state = ManagerState.CLEANED
                
    def getTypeListObj(self):
        return self._type_list_obj
    
    def reloadTypeModule(self, module_name, path=None):
        """Loads/reloads the given module name"""
        #path = path or [ os.path.dirname(__file__) ]
        m = None
        try:
            m = ModuleManager().reloadModule(module_name, path)
        except:
            pass
        
        if m is None:
            if self._modules.has_key(module_name):
                self._modules.pop(module_name)
            return
        
        self._modules[module_name] = {}
        
        for name in dir(m):
            if name.startswith("_"):
                continue
            klass = getattr(m, name)
            try:
                if not issubclass(klass, ParamType):
                    continue
            except:
                continue
            if klass in AbstractParamTypes:
                continue
            t = klass(name)
            self.addType(t)

        self._fireTypeEvent()
        
    def addType(self, type_obj, fire_event=False):
        type_name = type_obj.getName()
        type_class = type_obj.__class__
        module_name = type_obj.__module__
        
        mod_types = self._modules[module_name]
        
        #action = (((type_name in mod_types) and "Updating") \
        #          or "Adding")
        action = "Updating"
        self.debug("%s type %s", action, type_name)
        mod_types[type_name] = type_class
        self._inst_dict[type_class] = type_obj
        
        Type.addType(type_name)
        
        if fire_event:
            self._fireTypeEvent()

    def getTypeListStr(self):
        type_list_basic, type_list_obj = [], []
        
        for module_name, type_class_dict in self._modules.items():
            for tname, tklass in type_class_dict.items():
                if tklass.hasCapability(ParamType.ItemList):
                    type_list_obj.append("%s*" % tname)
                else:
                    type_list_basic.append(tname)
        type_list = sorted(type_list_basic) + sorted(type_list_obj)
        
        return type_list

    def _fireTypeEvent(self):
        """Helper method that fires event for the current existing types"""
        type_list = self.getTypeListStr()
        self._type_list_obj.fireEvent(type_list)
        return type_list
        
    def getTypeClass(self, type_name):
        for module_name, type_class_dict in self._modules.items():
            tklass = type_class_dict.get(type_name)
            if tklass is None:
                continue
            return tklass
        return None
    
    def getTypeObj(self, type_name):
        for type_class_name, type_obj in self._inst_dict.items():
            if type_obj.getName() == type_name:
                return type_obj

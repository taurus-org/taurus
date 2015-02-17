#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
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

from sardana.sardanamodulemanager import ModuleManager

from sardana.macroserver.msparameter import Type, ParamType, AbstractParamTypes
from sardana.macroserver.msmanager import MacroServerManager

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class TypeManager(MacroServerManager):

    DEFAULT_TYPE_DIR = _BASE_DIR
    DEFAULT_TYPE_MODULES = 'basetypes',

    def reInit(self):
        if self.is_initialized():
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

        path = [self.DEFAULT_TYPE_DIR]
        for type_module in self.DEFAULT_TYPE_MODULES:
            self.reloadTypeModule(type_module, path=path)

        MacroServerManager.reInit(self)

    def cleanUp(self):
        if self.is_cleaned():
            return

        if self._modules:
            for _, types_dict in self._modules.items():
                for type_name in types_dict:
                    Type.removeType(type_name)

        self._modules = None
        self._inst_dict = None

        MacroServerManager.cleanUp(self)

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
            if module_name in self._modules:
                self._modules.pop(module_name)
            return

        self._modules[module_name] = {}

        abs_file = inspect.getabsfile(m)
        ms = self.macro_server
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
            if inspect.getabsfile(klass) != abs_file:
                continue

            t = klass(ms, name)
            self.addType(t)

    def addType(self, type_obj):
        type_name = type_obj.getName()
        type_class = type_obj.__class__
        module_name = type_obj.__module__

        mod_types = self._modules[module_name]

        #action = (((type_name in mod_types) and "Updating") \
        #          or "Adding")
        action = "Updating"
        self.debug("%s type %s", action, type_name)
        mod_types[type_name] = type_class
        self._inst_dict[type_name] = type_obj

        Type.addType(type_name)

    def getTypeListStr(self):
        type_list_basic, type_list_obj = [], []

        for _, type_class_dict in self._modules.items():
            for tname, tklass in type_class_dict.items():
                if tklass.hasCapability(ParamType.ItemList):
                    type_list_obj.append("%s*" % tname)
                else:
                    type_list_basic.append(tname)
        type_list = sorted(type_list_basic) + sorted(type_list_obj)

        return type_list

    def getTypeClass(self, type_name):
        for _, type_class_dict in self._modules.items():
            tklass = type_class_dict.get(type_name)
            if tklass is None:
                continue
            return tklass
        return None

    def getTypeObj(self, type_name):
        return self._inst_dict.get(type_name)

    def getTypes(self):
        return self._inst_dict

    def getTypeNames(self):
        return self._inst_dict.keys()

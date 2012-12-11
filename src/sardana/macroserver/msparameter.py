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

"""This module contains the definition of the macroserver parameters for
macros"""

__all__ = ["WrongParam", "MissingParam", "UnknownParamObj", "WrongParamType",
           "TypeNames", "Type", "ParamType", "ParamRepeat", "ElementParamType",
           "ElementParamInterface", "AttrParamType", "AbstractParamTypes",
           "ParamDecoder" ]

__docformat__ = 'restructuredtext'

from taurus.core.util import CaselessDict

from sardana import ElementType, INTERFACES_EXPANDED
from sardana.macroserver.msbase import MSBaseObject
from .msexception import MacroServerException, UnknownMacro, UnknownMacroLibrary

class WrongParam(MacroServerException):
    
    def __init__(self, *args):
        MacroServerException.__init__(self, *args)
        self.type = 'Wrong parameter'


class MissingParam(WrongParam):
    
    def __init__(self, *args):
        WrongParam.__init__(self, *args)
        self.type = 'Missing parameter'


class UnknownParamObj(WrongParam):

    def __init__(self, *args):
        WrongParam.__init__(self, *args)
        self.type = 'Unknown parameter'


class WrongParamType(WrongParam):

    def __init__(self, *args):
        WrongParam.__init__(self, *args)
        self.type = 'Unknown parameter type'


class TypeNames:
    """Class that holds the list of registered macro parameter types"""
    
    def __init__(self):
        self._type_names = {}
        self._pending_type_names = {}
    
    def addType(self, name):
        """Register a new macro parameter type"""
        setattr(self, name, name)
        self._type_names[name] = name
        if name in self._pending_type_names:
            del self._pending_type_names[name]
    
    def removeType(self, name):
        """remove a macro parameter type"""
        delattr(self, name)
        try:
            del self._type_names[name]
        except ValueError:
            pass
        
    def __str__(self):
        return str(self._type_names.keys())
    
#    def __getattr__(self, name):
#        if name not in self._pending_type_names:
#            self._pending_type_names[name] = name
#        return self._pending_type_names[name]


# This instance of TypeNames is intended to provide access to types to the 
# Macros in a "Type.Motor" fashion
Type = TypeNames()


class ParamType(MSBaseObject):
    
    All             = 'All'
    
    # Capabilities
    ItemList        = 'ItemList'
    ItemListEvents  = 'ItemListEvents'
    
    capabilities    = []
    
    type_class = str
    
    def __init__(self, macro_server, name):
        MSBaseObject.__init__(self, name=name, full_name=name,
                              macro_server=macro_server,
                              elem_type=ElementType.ParameterType)
    
    def getName(self):
        return self.name

    def getObj(self, str_repr):
        return self.type_class(str_repr)
        
    @classmethod
    def hasCapability(cls, cap):
        return cap in cls.capabilities

    def serialize(self, *args, **kwargs):
        kwargs = MSBaseObject.serialize(self, *args, **kwargs)
        kwargs['composed'] = False
        return kwargs


class ParamRepeat(object):
    # opts: min, max
    def __init__(self, *param_def, **opts):
        self.param_def = param_def
        self.opts = {'min': 1, 'max': None}
        self.opts.update(opts)
        self._obj = list(param_def)
        self._obj.append(self.opts)

    def items(self):
        return self.opts.items()
    
    def __getattr__(self, name):
        return self.opts[name]
    
    def obj(self):
        return self._obj
    

class ElementParamType(ParamType):
    
    capabilities = ParamType.ItemList, ParamType.ItemListEvents
    
    def __init__(self, macro_server, name):
        ParamType.__init__(self, macro_server, name)
    
    def accepts(self, elem):
        return elem.getType() == self._name
    
    def getObj(self, name, pool=ParamType.All, cache=False):
        macro_server = self.macro_server
        if pool == ParamType.All:
            pools = macro_server.get_pools()
        else:
            pools = macro_server.get_pool(pool),
        for pool in pools:
            elem_info = pool.getObj(name, elem_type=self._name)
            if elem_info is not None and self.accepts(elem_info):
                return elem_info
        # not a pool object, maybe it is a macro server object (perhaps a macro
        # code or a macro library
        try:
            return macro_server.get_macro(name)
        except UnknownMacro:
            pass
        
        try:
            return macro_server.get_macro_lib(name)
        except UnknownMacroLibrary:
            pass
    
    def getObjDict(self, pool=ParamType.All, cache=False):
        macro_server = self.macro_server
        objs = CaselessDict()
        if pool == ParamType.All:
            pools = macro_server.get_pools()
        else:
            pools = macro_server.get_pool(pool),
        for pool in pools:
            for elem_info in pool.getElements():
                if self.accepts(elem_info):
                    objs[elem_info.name] = elem_info
        for macro_lib_name, macro_lib in macro_server.get_macros().items():
            if self.accepts(macro_lib):
                objs[macro_lib_name] = macro_lib
        for macro_name, macro in macro_server.get_macros().items():
            if self.accepts(macro):
                objs[macro_name] = macro
        
        return objs
    
    def getObjListStr(self, pool=ParamType.All, cache=False):
        obj_dict = self.getObjDict(pool=pool, cache=cache)
        return obj_dict.keys()

    def getObjList(self, pool=ParamType.All, cache=False):
        obj_dict = self.getObjDict(pool=pool, cache=cache)
        return obj_dict.values()

    def serialize(self, *args, **kwargs):
        kwargs = ParamType.serialize(self, *args, **kwargs)
        kwargs['composed'] = True
        return kwargs


class ElementParamInterface(ElementParamType):

    def __init__(self, macro_server, name):
        ElementParamType.__init__(self, macro_server, name)
        bases, doc = INTERFACES_EXPANDED.get(name)
        self._interfaces = bases
    
    def accepts(self, elem):
        elem_type = elem.getType()
        elem_interfaces = INTERFACES_EXPANDED.get(elem_type)[0]
        if elem_interfaces is None:
            return ElementParamType.accepts(self, elem)
        return self._name in elem_interfaces
    
    def getObj(self, name, pool=ParamType.All, cache=False):
        macro_server = self.macro_server
        if pool == ParamType.All:
            pools = macro_server.get_pools()
        else:
            pools = macro_server.get_pool(pool),
        for pool in pools:
            elem_info = pool.getElementWithInterface(name, self._name)
            if elem_info is not None and self.accepts(elem_info):
                return elem_info
        # not a pool object, maybe it is a macro server object (perhaps a macro
        # class or a macro library
        try:
            return macro_server.get_macro(name)
        except UnknownMacro:
            pass
        
        try:
            return macro_server.get_macro_lib(name)
        except UnknownMacroLibrary:
            pass
    
    def getObjDict(self, pool=ParamType.All, cache=False):
        macro_server = self.macro_server
        objs = CaselessDict()
        if macro_server.is_macroserver_interface(self._name):
            return macro_server.get_elements_with_interface(self._name)
        
        if pool == ParamType.All:
            pools = macro_server.get_pools()
        else:
            pools = macro_server.get_pool(pool),
        for pool in pools:
            for elem_info in pool.getElementsWithInterface(self._name).values():
                if self.accepts(elem_info):
                    objs[elem_info.name] = elem_info
        return objs
    
    def getObjListStr(self, pool=ParamType.All, cache=False):
        obj_dict = self.getObjDict(pool=pool, cache=cache)
        return obj_dict.keys()
    
    def getObjList(self, pool=ParamType.All, cache=False):
        obj_dict = self.getObjDict(pool=pool, cache=cache)
        return obj_dict.values()


class AttrParamType(ParamType):
    pass


AbstractParamTypes = ParamType, ElementParamType, ElementParamInterface, AttrParamType


class ParamDecoder:

    def __init__(self, door, macro_meta, param_str_list):
        self.door = door
        self.macro_meta = macro_meta
        self.param_str_list = param_str_list
        self.param_list = None
        self.decode()

    @property
    def type_manager(self):
        return self.door.type_manager
    
    def decode(self):
        macro_meta = self.macro_meta
        macro_type = macro_meta.get_type()
        pars_str = self.param_str_list[1:]
        pars_def = macro_meta.get_parameter_definition()
        if macro_type == ElementType.MacroClass:
            _, self.param_list = self.decodeNormal(pars_str, pars_def)
        elif macro_type == ElementType.MacroFunction:
            if macro_meta.function.param_def is None:
                self.param_list = self.param_str_list[1:]
            else:
                _, self.param_list = self.decodeNormal(pars_str, pars_def)
        return self.param_list

    def decodeNormal(self, str_list, def_list):
        str_len = len(str_list)
        par_len = len(def_list)
        obj_list = []
        str_idx = 0
        for i, par_def in enumerate(def_list):
            name, type_class, def_val, desc = par_def
            if str_idx == str_len:
                if def_val is None:
                    if not isinstance(type_class, ParamRepeat):
                        raise MissingParam, "'%s' not specified" % name
                    elif isinstance(type_class, ParamRepeat):
                        min = par_def[1].opts['min']
                        if min > 0:
                            raise WrongParam, "'%s' demands at least %d values" % (name, min)
                new_obj_list = []
                if not def_val is None:
                    new_obj_list.append(def_val)
            else:
                if isinstance(type_class, ParamRepeat):
                    data = self.decodeRepeat(str_list[str_idx:], par_def)
                    dec_token, new_obj_list = data
                else:
                    type_manager = self.type_manager
                    type_name = type_class
                    type_class = type_manager.getTypeClass(type_name)
                    par_type = type_manager.getTypeObj(type_name)
                    par_str = str_list[str_idx]
                    try:
                        val = par_type.getObj(par_str)
                    except ValueError, e:
                        raise WrongParamType, e.message
                    if val is None:
                        msg = 'Could not create %s parameter "%s" for "%s"' % \
                              (par_type.getName(), name, par_str)
                        raise WrongParam, msg
                    dec_token = 1
                    new_obj_list = [val]
                str_idx += dec_token
            obj_list += new_obj_list
        return str_idx, obj_list

    def decodeRepeat(self, str_list, par_def):
        name, rep_data, def_val, desc = par_def
        min_rep = rep_data.min
        max_rep = rep_data.max
        dec_token = 0
        obj_list = []
        rep_nr = 0
        while dec_token < len(str_list):
            if max_rep is not None and rep_nr == max_rep:
                break
            new_token, new_obj_list = self.decodeNormal(str_list[dec_token:],
                                                        rep_data.param_def)
            dec_token += new_token
            if len(new_obj_list) == 1:
                new_obj_list = new_obj_list[0]
            obj_list.append(new_obj_list)
            rep_nr += 1
        if rep_nr < min_rep:
            msg = 'Found %d repetitions of param %s, min is %d' % \
                  (rep_nr, name, min_rep)
            raise RuntimeError, msg
        return dec_token, obj_list
        
    def getParamList(self):
        return self.param_list

    def __getattr__(self, name):
        return getattr(self.param_list, name)

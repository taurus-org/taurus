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
           "AttrParamType", "AbstractParamTypes", "ParamDecoder" ]

__docformat__ = 'restructuredtext'

import copy
import exception
import weakref

from taurus.core.util import CaselessDict, Logger, ListEventGenerator
from taurus.core.tango.sardana.pool import BaseElement


class WrongParam(exception.MacroServerException):
    
    def __init__(self, *args):
        exception.MacroServerException.__init__(self, *args)
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
    
    def addType(self, name):
        """Register a new macro parameter type"""
        setattr(self, name, name)
        self._type_names[name] = name
    
    def removeType(self, name):
        """remove a macro parameter type"""
        delattr(self, name)
        try:
            del self._type_names[name]
        except ValueError,e:
            pass
        
    def __str__(self):
        return str(self._type_names.keys())
    

# This instance of TypeNames is intended to provide access to types to the 
# Macros in a "Type.Motor" fashion
Type = TypeNames()


class ParamType(Logger):
    
    All             = 'All'
    
    # Capabilities
    ItemList        = 'ItemList'
    ItemListEvents  = 'ItemListEvents'
    
    capabilities    = []
    
    def __init__(self, name):
        self._name = name
        Logger.__init__(self, '%sType' % name)
    
    def getName(self):
        return self._name

    def getObj(self, str_repr):
        return self.type_class(str_repr)
        
    @classmethod
    def hasCapability(cls, cap):
        return cap in cls.capabilities


class ParamRepeat:
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
    
    def __init__(self, name):
        ParamType.__init__(self, name)
        
    def getManager(self):
        import manager
        return manager.MacroServerManager()
    
    def accepts(self, elem):
        return elem.getType() == self._name
    
    def getObj(self, name, pool=ParamType.All, cache=False):
        obj_dict = self.getObjDict(pool=pool, cache=cache)
        return obj_dict.get(name, None)
    
    def getObjDict(self, pool=ParamType.All, cache=False):
        objs = CaselessDict()
        if pool == ParamType.All:
            pools = self.getManager().getPoolListObjs()
        else:
            pools = self.getManager().getPoolObj(pool),
        for pool in pools:
            for elem_info in pool.getElements():
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


AbstractParamTypes = (ParamType, ElementParamType, AttrParamType)


class ParamDecoder:

    def __init__(self, macro_class, param_str_list):
        self.macro_class = macro_class
        self.param_str_list = param_str_list
        self.param_list = None
        self.decode()

    def getManager(self):
        import manager
        return manager.MacroServerManager()

    def decode(self):
        dec_token, obj_list = self.decodeNormal(self.param_str_list[1:],
                                                self.macro_class.param_def)
        self.param_list = obj_list

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
                    mg = self.getManager()
                    type_name = type_class
                    type_class = mg.getTypeClass(type_name)
                    par_type = mg.getTypeObj(type_name)
                    par_str = str_list[str_idx]
                    try:
                        val = par_type.getObj(par_str)
                    except ValueError, e:
                        raise WrongParamType, e.message
                    if val is None:
                        msg = 'Could not create %s param "%s" from "%s"' % \
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
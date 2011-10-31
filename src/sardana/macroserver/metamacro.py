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

"""This module contains the class definition for the MacroServer meta macro
information"""

__all__ = ["MACRO_TEMPLATE", "MacroLib", "MacroClass"]

__docformat__ = 'restructuredtext'

import inspect
import os
import operator
import types
import parameter

from taurus.core.util import CodecFactory

from sardana import InvalidId
from sardana.sardanameta import SardanaMetaLib, SardanaMetaClass

MACRO_TEMPLATE = """class @macro_name@(Macro):
    \"\"\"@macro_name@ description.\"\"\"

    # uncomment the following lines as necessary. Otherwise you may delete them
    #param_def = []
    #result_def = []
    #hints = {}
    #env = (,)
    
    # uncomment the following lines if need prepare. Otherwise you may delete them
    #def prepare(self):
    #    pass
        
    def run(self):
        pass

"""

class MacroLib(SardanaMetaLib):
    """Object representing a python module containning macro classes and/or 
    macro functins. Public members:
        
        - module - reference to python module
        - file_path - complete (absolute) path (with file name at the end)
        - file_name - file name (including file extension)
        - path - complete (absolute) path
        - name - (=module name) module name (without file extension)
        - macros - dict<str, MacroClass>
        - exc_info - exception information if an error occured when loading 
                    the module"""
    
    def __init__(self, **kwargs):
        kwargs['manager'] = kwargs.pop('macro_server')
        SardanaMetaLib.__init__(self, **kwargs)
    
    def serialize(self, *args, **kwargs):
        kwargs = SardanaMetaLib.serialize(self, *args, **kwargs)
        kwargs['macro_server'] = self.get_manager().name
        kwargs['id'] = InvalidId
        return kwargs
    
    add_macro = SardanaMetaLib.add_meta_class
    get_macro = SardanaMetaLib.get_meta_class
    get_macros = SardanaMetaLib.get_meta_classes
    has_macro = SardanaMetaLib.has_meta_class

    @property
    def macros(self):
        return self.meta_classes


import json

class MacroClassJSONEncoder(json.JSONEncoder):
    
    def default(self, obj):
        if not isinstance(obj, MacroClass):
            return json.JSONEncoder.default(self, ret)
        klass = obj.getMacroClass()
        ret = { 'name' : obj.getName(),
          'full_name' : obj.getFullName(),
          'id' : 0,
          'module_name' : obj.getModuleName(),
          'filename' : obj.getFileName(),
          'description' : obj.getDescription(),
          'hints' : obj.klass.hints }
        param, result = obj.getParamObj(), obj.getResultObj()
        if param: ret['parameters'] = param
        if result: ret['result'] = result
        return ret
        

class MacroClass(SardanaMetaClass):
    
    def __init__(self, **kwargs):
        kwargs['manager'] = kwargs.pop('macro_server')
        SardanaMetaClass.__init__(self, **kwargs)

    def serialize(self, *args, **kwargs):
        kwargs = SardanaMetaClass.serialize(self, *args, **kwargs)
        kwargs['macro_server'] = self.get_manager().name
        kwargs['id'] = InvalidId
        kwargs['hints'] = self.klass.hints
        param, result = self.getParamObj(), self.getResultObj()
        if param: kwargs['parameters'] = param
        if result: kwargs['result'] = result
        return kwargs
    
    @property
    def macro_class(self):
        return self.klass
    
    def get_brief_description(self, max_chars=60):
        desc = self.description.replace('\n',' ')
        if len(desc) > (max_chars-5):
            desc = desc[:max_chars-5] + '[...]'
        return desc

    def getInfo(self):
        klass = self.klass
        info = [self.full_name, self.description, str(klass.hints)]
        info += self.getParamInfo()
        info += self.getResultInfo()
        return info
    
    def getParamObj(self):
        return self._getParamObj(self.klass.param_def)

    def getResultObj(self):
        return self._getParamObj(self.klass.result_def)

    def _getParamObj(self, param_def):
        ret = []
        for p in param_def:
            t = p[1]
            ret_p = {'min': 1, 'max': None}
            # take care of old ParamRepeat
            if isinstance(t, parameter.ParamRepeat):
                t = t.obj()
                
            if operator.isSequenceType(t) and not type(t) in types.StringTypes:
                if operator.isMappingType(t[-1]):
                    ret_p.update(t[-1])
                    t = self._getParamObj(t[:-1])
                else:
                    t = self._getParamObj(t)
                
            ret_p['name'] = p[0]
            ret_p['type'] = t
            ret_p['default_value'] = p[2]
            ret_p['description'] = p[3]
            ret.append(ret_p)
        return ret

    def getParamInfo(self, param_def=None):
        param_def = param_def or self.klass.param_def
        
        info = [str(len(param_def))]
        for name, type_class, def_val, desc in param_def:
            repeat = isinstance(type_class, parameter.ParamRepeat)
            info.append(name)
            type_name = (repeat and 'ParamRepeat') or type_class
            info.append(type_name)
            info.append(desc)
            if repeat:
                rep = type_class
                opts = sep = ''
                for opt, val in rep.items():
                    opts += '%s%s=%s' % (sep, opt, val)
                    sep = ', '
                info.append(opts)
                info += self.getParamInfo(rep.param_def)
            else:
                info.append(str(def_val))
        return info

    def getResultInfo(self, result_def=None):
        result_def = result_def or self.klass.result_def
        
        info = [str(len(result_def))]
        for name, type_class, def_val, desc in result_def:
            repeat = isinstance(type_class, parameter.ParamRepeat)
            info.append(name)
            type_name = (repeat and 'ParamRepeat') or type_class
            info.append(type_name)
            info.append(desc)
            if repeat:
                rep = type_class
                opts = sep = ''
                for opt, val in rep.items():
                    opts += '%s%s=%s' % (sep, opt, val)
                    sep = ', '
                info.append(opts)
                info += self.getParamInfo(rep.param_def)
            else:
                info.append(str(def_val))
        return info
    
class MacroClass_OLD(object):
    """Object representing a python macro class. 
       Public members:
           name - class name
           klass - python class object
           lib - MacroLib object representing the module where the macro is.
    """
    
    NoDoc = '<Undocumented macro>'
    
    def __init__(self, lib, klass, name=None):
        self.klass = klass
        self.name = name or klass.__name__
        self.lib = lib

    def __cmp__(self, o):
        if o is None: return cmp(self.getName(), None)
        return cmp(self.getName(), o.getName())

    def __str__(self):
        return self.getName()

    def _toJSON(self, obj):
        klass = obj.getMacroClass()
        ret = { 'name' : obj.getName(),
          'module' : obj.getModuleName(),
          'filename' : obj.getFileName(),
          'description' : obj.getDescription(),
          'hints' : obj.klass.hints }
        param, result = obj.getParamObj(), obj.getResultObj()
        if param: ret['parameters'] = param
        if result: ret['result'] = result
        return ret
    
    def serialize(self, *args, **kwargs):
        kwargs['name'] = self.getName()
        kwargs['full_name'] = self.getFullName()
        kwargs['id'] = 0
        kwargs['type'] = self.__class__.__name__
        kwargs['module_name'] = self.getModuleName()
        kwargs['filename'] = self.getFileName()
        kwargs['description'] = self.getDescription()
        kwargs['hints'] = self.klass.hints
        param, result = self.getParamObj(), self.getResultObj()
        if param: kwargs['parameters'] = param
        if result: kwargs['result'] = result
        return kwargs
    
    def getJSON(self):
        json_codec = CodecFactory().getCodec('json')
        format, data = json_codec.encode(('', self), cls=MacroClassJSONEncoder)
        return data

    def getMacroLib(self):
        return self.lib
    
    def getMacroClass(self):
        return self.klass

    def getName(self):
        return self.name

    def getFullName(self):
        return '%s.%s' % (self.getModuleName(), self.getName())

    def getModuleName(self):
        return self.lib.module_name

    def getFileName(self):
        return self.lib.file_name
    
    def getDescription(self):
        return self.getMacroClass().__doc__ or MacroClass.NoDoc

    def getBriefDescription(self, max_chars=60):
        d = self.getMacroClass().__doc__ or MacroClass.NoDoc
        d = d.replace('\n',' ')
        if len(d) > max_chars: d = d[:max_chars-5] + '[...]'
        return d

    def getMacroCode(self):
        """Returns a tuple (sourcelines, firstline) corresponding to the 
        definition of the macro class. sourcelines is a list of source code 
        lines. firstline is the line number of the first source code line.
        """
        return inspect.getsourcelines(self.getMacroClass())

    def getInfo(self):
        klass = self.getMacroClass()
        info = [self.getFullName(), self.getDescription(), str(klass.hints)]
        info += self.getParamInfo()
        info += self.getResultInfo()
        return info
    
    def getParamObj(self):
        return self._getParamObj(self.klass.param_def)

    def getResultObj(self):
        return self._getParamObj(self.klass.result_def)

    def _getParamObj(self, param_def):
        ret = []
        for p in param_def:
            t = p[1]
            ret_p = {'min': 1, 'max': None}
            # take care of old ParamRepeat
            if isinstance(t, parameter.ParamRepeat):
                t = t.obj()
                
            if operator.isSequenceType(t) and not type(t) in types.StringTypes:
                if operator.isMappingType(t[-1]):
                    ret_p.update(t[-1])
                    t = self._getParamObj(t[:-1])
                else:
                    t = self._getParamObj(t)
                
            ret_p['name'] = p[0]
            ret_p['type'] = t
            ret_p['default_value'] = p[2]
            ret_p['description'] = p[3]
            ret.append(ret_p)
        return ret

    def getParamInfo(self, param_def=None):
        param_def = param_def or self.klass.param_def
        
        info = [str(len(param_def))]
        for name, type_class, def_val, desc in param_def:
            repeat = isinstance(type_class, parameter.ParamRepeat)
            info.append(name)
            type_name = (repeat and 'ParamRepeat') or type_class
            info.append(type_name)
            info.append(desc)
            if repeat:
                rep = type_class
                opts = sep = ''
                for opt, val in rep.items():
                    opts += '%s%s=%s' % (sep, opt, val)
                    sep = ', '
                info.append(opts)
                info += self.getParamInfo(rep.param_def)
            else:
                info.append(str(def_val))
        return info

    def getResultInfo(self, result_def=None):
        result_def = result_def or self.klass.result_def
        
        info = [str(len(result_def))]
        for name, type_class, def_val, desc in result_def:
            repeat = isinstance(type_class, parameter.ParamRepeat)
            info.append(name)
            type_name = (repeat and 'ParamRepeat') or type_class
            info.append(type_name)
            info.append(desc)
            if repeat:
                rep = type_class
                opts = sep = ''
                for opt, val in rep.items():
                    opts += '%s%s=%s' % (sep, opt, val)
                    sep = ', '
                info.append(opts)
                info += self.getParamInfo(rep.param_def)
            else:
                info.append(str(def_val))
        return info
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

__all__ = ["MACRO_TEMPLATE", "MacroLibrary", "MacroClass", "MacroFunction"]

__docformat__ = 'restructuredtext'

import inspect
import operator

from sardana import InvalidId, ElementType
from sardana.sardanameta import SardanaLibrary, SardanaClass, SardanaFunction

from msparameter import Type, ParamRepeat

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

MACRO_TEMPLATE = """\
@macro()
def @macro_name@(self):
    self.output("Running @macro_name@...")

"""

class MacroLibrary(SardanaLibrary):
    """Object representing a python module containing macro classes and/or 
    macro functions. Public members:
        
        - module - reference to python module
        - file_path - complete (absolute) path (with file name at the end)
        - file_name - file name (including file extension)
        - path - complete (absolute) path
        - name - (=module name) module name (without file extension)
        - macros - dict<str, MacroClass>
        - exc_info - exception information if an error occurred when loading 
                    the module"""
    
    def __init__(self, **kwargs):
        kwargs['manager'] = kwargs.pop('macro_server')
        kwargs['elem_type'] = ElementType.MacroLibrary
        SardanaLibrary.__init__(self, **kwargs)
    
    def serialize(self, *args, **kwargs):
        kwargs = SardanaLibrary.serialize(self, *args, **kwargs)
        kwargs['macro_server'] = self.get_manager().name
        kwargs['id'] = InvalidId
        return kwargs
    
    get_macro = SardanaLibrary.get_meta
    get_macros = SardanaLibrary.get_metas
    has_macro = SardanaLibrary.has_meta

    add_macro_class = SardanaLibrary.add_meta_class
    get_macro_class = SardanaLibrary.get_meta_class
    get_macro_classes = SardanaLibrary.get_meta_classes
    has_macro_class = SardanaLibrary.has_meta_class
    
    add_macro_function = SardanaLibrary.add_meta_function
    get_macro_function = SardanaLibrary.get_meta_function
    get_macro_functions = SardanaLibrary.get_meta_functions
    has_macro_function = SardanaLibrary.has_meta_function

    @property
    def macros(self):
        ret = {}
        ret.update(self.meta_classes)
        ret.update(self.meta_functions)
        return ret


class Parameterizable(object):
    """Helper class to handle parameter and result definition for a
    :class:`~sardana.macroserver.msmetamacro.MacroClass` or a
    :class:`~sardana.macroserver.msmetamacro.MacroFunction`"""
    
    def __init__(self):
        self._parameter = self.build_parameter()
        self._result = self.build_result()
    
    def get_parameter_definition(self):
        raise NotImplementedError
    
    def get_result_definition(self):
        raise NotImplementedError

    def get_hints_definition(self):
        raise NotImplementedError
    
    def get_parameter(self):
        return self._parameter
    
    def get_result(self):
        return self._result
    
    def build_parameter(self):
        return self._build_parameter(self.get_parameter_definition())

    def build_result(self):
        return self._build_parameter(self.get_result_definition())
        
    def _build_parameter(self, param_def):
        ret = []
        param_def = param_def or ()
        for p in param_def:
            t = p[1]
            ret_p = {'min': 1, 'max': None}
            # take care of old ParamRepeat
            if isinstance(t, ParamRepeat):
                t = t.obj()
                
            if operator.isSequenceType(t) and not isinstance(t, (str, unicode)):
                if operator.isMappingType(t[-1]):
                    ret_p.update(t[-1])
                    t = self._build_parameter(t[:-1])
                else:
                    t = self._build_parameter(t)
                
            ret_p['name'] = p[0]
            ret_p['type'] = t
            ret_p['default_value'] = p[2]
            ret_p['description'] = p[3]
            ret.append(ret_p)
        return ret

    def build_parameter_info(self, param_def=None):
        param_def = param_def or self.get_parameter_definition()
        
        info = [str(len(param_def))]
        for name, type_class, def_val, desc in param_def:
            repeat = isinstance(type_class, ParamRepeat)
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
                info += self.get_parameter_info(rep.param_def)
            else:
                info.append(str(def_val))
        return info
    
    def build_result_info(self, result_def=None):
        result_def = result_def or self.get_result_definition()
        
        info = [str(len(result_def))]
        for name, type_class, def_val, desc in result_def:
            repeat = isinstance(type_class, ParamRepeat)
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
                info += self.get_parameter_info(rep.param_def)
            else:
                info.append(str(def_val))
        return info
    
    def get_info(self):
        info = [self.full_name, self.description, str(self.code_object.hints)]
        info += self.get_parameter_info()
        info += self.get_result_info()
        return info
    
    def serialize(self, *args, **kwargs):
        kwargs['macro_server'] = self.get_manager().name
        kwargs['id'] = InvalidId
        kwargs['hints'] = self.code_object.hints
        param, result = self.get_parameter(), self.get_result()
        kwargs['parameters'] = param
        kwargs['result'] = result
        return kwargs


class MacroClass(SardanaClass, Parameterizable):
    
    def __init__(self, **kwargs):
        kwargs['manager'] = kwargs.pop('macro_server')
        kwargs['elem_type'] = ElementType.MacroClass
        SardanaClass.__init__(self, **kwargs)
        Parameterizable.__init__(self)
    
    def serialize(self, *args, **kwargs):
        kwargs = SardanaClass.serialize(self, *args, **kwargs)
        kwargs = Parameterizable.serialize(self, *args, **kwargs)
        return kwargs
    
    @property
    def macro_class(self):
        return self.klass
    
    def get_parameter_definition(self):
        return self.klass.param_def
    
    def get_result_definition(self):
        return self.klass.result_def

    def get_hints_definition(self):
        return self.klass.hints


class MacroFunction(SardanaFunction, Parameterizable):
    
    def __init__(self, **kwargs):
        kwargs['manager'] = kwargs.pop('macro_server')
        kwargs['elem_type'] = ElementType.MacroFunction
        SardanaFunction.__init__(self, **kwargs)
        Parameterizable.__init__(self)
    
    def serialize(self, *args, **kwargs):
        kwargs = SardanaFunction.serialize(self, *args, **kwargs)
        kwargs = Parameterizable.serialize(self, *args, **kwargs)
        return kwargs
    
    @property
    def macro_function(self):
        return self.function
    
    def to_parameter_definition(self):
        param_def = []
        args, varargs, keywords, defaults = inspect.getargspec(self.function)
        assert keywords is None
        assert len(args) > 0
        
        if varargs is None:
            for arg in args[1:]:
                param_def.append((arg, Type.Any, None, arg + " parameter"))
            i = len(param_def)-1
            if defaults is not None:
                for default in reversed(defaults):
                    param_def[i][2] = default
                    i -= 1
        else:
            param_def.append(
                (varargs , [[ varargs, Type.Any, None, varargs + " parameter"]],
                 None, "list of " + varargs))
        return param_def
    
    def get_parameter_definition(self):
        param_def = self.function.param_def
        if param_def is None:
            param_def = self.to_parameter_definition()
        return param_def
    
    def get_result_definition(self):
        result_def = self.function.result_def
        return result_def

    def get_hints_definition(self):
        return self.function.hints or ()


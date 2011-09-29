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

"""This module contains the class definition for the MacroServer macro
manager"""

__all__ = ["MacroManager", "MacroExecutor",]

__docformat__ = 'restructuredtext'

import sys
import os
import inspect
import copy
import traceback
import operator
import types
import re
import time
import threading
import json

from PyTango import DevState, DevFailed
from taurus.core import ManagerState
from taurus.core.util import Singleton, Logger, CodecFactory, InfoIt, \
    ListEventGenerator, etree

import macro
import metamacro
from exception import MacroServerExceptionList
from exception import UnknownMacro, UnknownLib, MissingEnv, LibError
from exception import MacroServerException, AbortException, MacroWrongParameterType
from modulemanager import ModuleManager


class MacroManager(Singleton, Logger):

    # States
    Init     = DevState.INIT
    Running  = DevState.RUNNING
    Pause    = DevState.STANDBY
    Stop     = DevState.STANDBY
    Fault    = DevState.FAULT
    Finished = DevState.ON
    Ready    = DevState.ON
    Abort    = DevState.ALARM
    
    DEFAULT_MACRO_DIRECTORIES = 'macros',
    
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self._state = ManagerState.UNINITIALIZED
        self.call__init__(Logger, name)
        self._macro_list_obj = ListEventGenerator('MacroList')
        self._macro_lib_list_obj = ListEventGenerator('MacroLibList')
        self.reInit()

    def reInit(self):
        if self._state == ManagerState.INITED:
            return
        
        # dict<str, metamacro.MacroLib>
        # key   - module name (without path and without extension)
        # value - MacroLib object representing the module 
        self._modules = {}
        
        # dict<str, <metamacro.MacroClass>
        # key   - macro name
        # value - MacroClass object representing the macro
        self._macro_dict = {}
    
        # list<str>
        # elements are absolute paths
        self._macro_path = []
        
        # dict<Door, <MacroExecutor>
        # key   - door
        # value - MacroExecutor object for the door
        self._macro_executors = {}
        
        self._state = ManagerState.INITED

    def cleanUp(self):
        if self._state == ManagerState.CLEANED:
            return
        
        if self._modules:
            ModuleManager().unloadModules(self._modules.keys())
        
        self._macro_path = None
        self._macro_dict = None
        self._modules = None
        
        self._state = ManagerState.CLEANED

    def setMacroPath(self, macro_path):
        """Registers a new list of macro directories in this manager.
        Warning: as a consequence all the macro modules will be reloaded.
        This means that if any reference to an old macro object was kept it will
        refer to an old module (which could possibly generate problems of type
        class A != class A)."""
        p = []
        for item in macro_path:
            p.extend(item.split(":"))

        # add basic macro directories
        macroserver_dir = os.path.dirname(os.path.abspath(__file__))
        for macro_dir in self.DEFAULT_MACRO_DIRECTORIES:
            macro_dir = os.path.join(macroserver_dir, macro_dir)
            if not macro_dir in p:
                p.append(macro_dir)
        
        self._macro_path = p
        
        macro_file_names = self._findMacroLibNames()
        for macro_file_name in macro_file_names:
            try:
                self.reloadMacroLib(macro_file_name)
            except:
                pass
        
    def getMacroPath(self):
        return self._macro_path

    def _findMacroLibNames(self, path=None):
        path = path or self.getMacroPath()
        ret = []
        for p in path:
            try:
                elems = os.listdir(p)
                for f in os.listdir(p):
                    name,ext = os.path.splitext(f)
                    if ext.endswith('py'):
                        ret.append(name)
            except:
                self.debug("'%s' is not a valid path" % p)
        return ret

    def _fromNameToFileName(self, lib_name, path=None):
        path = path or self.getMacroPath()[0]
        f_name = lib_name
        if not f_name.endswith('.py'):
            f_name += '.py'
            
        if os.path.isabs(f_name):
            path, name = os.path.split(f_name)
            if not path in self.getMacroPath():
                raise Exception("'%s' is not part of the MacroPath" % path)
        else:
            name = f_name
            f_name = os.path.join(path, f_name)
        return f_name

    def getOrCreateMacroLib(self, lib_name, macro_name=None):
        """Gets the exiting macro lib or creates a new macro lib file. If
        name is not None, a macro template code for the given macro name is 
        appended to the end of the file.
        
        @param[in] lib_name - module name, python file name, or full file name 
                              (with path)
        @param[in] macro_name - an optional macro name. If given a macro template
                                code is appended to the end of the file
                                (default is None meaning no macro code is added)
        macro_lib = self.getMacroLib(lib_name)
        
        @return a sequence with three items: full_filename, code, line number 
                line number is 0 if no macro is created or n representing the 
                first line of code for the given macro name.
        """
        # if only given the module name
        macro_lib = self.getMacroLib(lib_name)
        
        if macro_name is None:
            line_nb = 0
            if macro_lib is None:
                f_name, code = self.createMacroLib(lib_name), ''
            else:
                f_name = macro_lib.getFileName()
                f = file(f_name)
                code = f.read()
                f.close()
        else:
        # if given macro name
            if macro_lib is None:
                f_name, code, line_nb = self.createMacro(lib_name, macro_name)
            else:
                macro = macro_lib.getMacro(macro_name)
                if macro is None:
                    f_name, code, line_nb = self.createMacro(lib_name, macro_name)
                else:
                    code_lines, line_nb = macro.getMacroCode()
                    f_name = macro.getFileName()
                    f = file(f_name)
                    code = f.read()
                    f.close()
                
        return [ f_name, code, line_nb ]

    def setMacroLib(self, lib_name, code):
        f_name = self._fromNameToFileName(lib_name)
        f = open(f_name, 'w')
        f.write(code)
        f.flush()
        f.close()
        p, name = os.path.split(f_name)
        mod, ext = os.path.splitext(name)
        self.reloadMacroLib(mod)

    def createMacroLib(self, lib_name, path=None):
        """Creates a new empty macro library (python module)"""
        f_name = self._fromNameToFileName(lib_name, path)
        
        if os.path.exists(f_name):
            raise Exception("Unable to create macro lib: '%s' already exists" % f_name)
            
        f = open(f_name, 'w')
        f.close()
        return f_name

    def createMacro(self, lib_name, macro_name):
        f_name = self._fromNameToFileName(lib_name)
        
        create = not os.path.exists(f_name)
        
        template = ''
        if create:
            template += 'from macro import *\n\n'
            line_nb = 4
        else:
            template += '\n'
            t = open(f_name, 'rU')
            line_nb = -1
            for line_nb, line in enumerate(t): pass
            line_nb += 3
            t.close()
            
        f = open(f_name, 'a+')
        try:
            dir_name = os.path.realpath(__file__)
            dir_name = os.path.dirname(dir_name)
            template_fname = 'macro_template.txt'
            template_fname = os.path.join(dir_name, template_fname)
            f_templ = open(template_fname, 'r')
            template += f_templ.read()
            f_templ.close()
        except:
            self.debug("Failed to open template macro file. Using simplified template")
            template += metamacro.MACRO_TEMPLATE
            if f_templ:
                f_templ.close()
                
        template = template.replace('@macro_name@', macro_name)
        try:
            f.write(template)
            f.flush()
            f.seek(0)
            code = f.read()
        finally:
            f.close()
        return f_name, code, line_nb

    def reloadMacro(self, macro_name, path=None, fire_event=True):
        """Reloads the module corresponding to the given macro name
        
        :raises: MacroServerExceptionList in case the macro is unknown or the
        reload process is not successfull
        
        :param macro_name: macro name
        :param path: a list of absolute path to search for libraries 
                     (optional, default=None, means the current MacroPath 
                     will be used)
        :param fire_event: fire events in case something (macro list or
                           module list changes (optional, default=True)"""
        self.reloadMacros([macro_name], path=path, fire_event=fire_event)
        
    def reloadMacros(self, macro_names, path=None, fire_event=True):
        """Reloads the modules corresponding to the given macro names
        
        :raises: MacroServerExceptionList in case the macro(s) are unknown or the
        reload process is not successfull
        
        :param macro_names: a list of macro names
        :param path: a list of absolute path to search for libraries (optional, 
                     default=None, means the current MacroPath will be used)
        :param fire_event: fire events in case something (macro list or
                           module list changes (optional, default=True)
        """
        module_names = []
        for macro_name in macro_names:
            module_name = self.getMacroMetaClass(macro_name).getModuleName()
            module_names.append(module_name)
        self.reloadMacroLibs(module_names, path=path, fire_event=fire_event)
        
        if fire_event:
            self._fireMacroEvent()
    
    def reloadMacroLibs(self, module_names, path=None, fire_event=True):
        """Reloads the given lib(=module) names
        
        :raises: MacroServerExceptionList in case the reload process is not 
        successfull for at least one lib
        
        :param module_names: a list of module names
        :param path: a list of absolute path to search for libraries 
                     (optional, default=None, means the current MacroPath 
                     will be used)
        :param fire_event: fire events in case something (macro list or
                           module list changes (optional, default=True)
        """
        # Store how was the old list of modules to see if an event needs to be
        # fired
        old_modules = None
        if fire_event:
            old_modules = self.getMacroLibNames()

        ret = []
        for module_name in module_names:
            m = self.reloadMacroLib(module_name, path, fire_event=False)
            if m: ret.append(m)
        
        if fire_event:
            new_modules = self.getMacroLibNames()
            self._fireMacroLibEvent(new_modules)
        return ret
        
    def reloadMacroLib(self, module_name, path=None, fire_event=True):
        """Reloads the given lib(=module) names
        
        :raises: MacroServerExceptionList in case the reload process is not 
        successfull
        
        :param module_name: macro library name (=python module name)
        :param path: a list of absolute path to search for libraries 
                     (optional, default=None, means the current MacroPath 
                     will be used)
        :param fire_event: fire events in case something (macro list or
                           module list changes (optional, default=True)
        
        :return: the MacroLib object for the reloaded macro lib
        """
        # Store how was the old list of modules to see if an event needs to be
        # fired
        old_modules = None
        if fire_event:
            old_modules = self.getMacroLibNames()

        path = path or self.getMacroPath()
        # reverse the path order:
        # more priority elements last. This way if there are repeated elements
        # they first ones (lower priority) will be overwritten by the last ones
        if path: 
            path = copy.copy(path)
            path.reverse()
        
        # if there was previous Macro Lib info remove it
        if self._modules.has_key(module_name):
            self._modules.pop(module_name)

        try:
            m = ModuleManager().reloadModule(module_name, path)
        except Exception, e:
            exp_pars = { 'type' : e.__class__.__name__,
                         'msg' :  str(e),
                         'args' : e.args }
            raise LibError(exp_pars)
        
        macro_lib = None
        if not m is None:
            macro_lib = metamacro.MacroLib( os.path.abspath(m.__file__) )
            
            lib_contains_macros = False
            for name, klass in inspect.getmembers(m, inspect.isclass):
                if not klass is macro.Macro and issubclass(klass, macro.Macro):
                    lib_contains_macros = True
                    self.addMacro(macro_lib, klass)
            
            if lib_contains_macros:
                self._modules[module_name] = macro_lib

        if fire_event:
            self._fireMacroEvent()
            self._fireMacroLibEvent()

        return macro_lib
    
    def addMacro(self, macro_lib, klass, fire_event=False):
        macro_name = klass.__name__
        action = (macro_lib.hasMacro(macro_name) and "Updating") or "Adding"
        self.debug("%s macro %s" % (action, macro_name))
        
        macro_class = metamacro.MacroClass(macro_lib, klass)
        macro_lib.addMacro(macro_class)
        self._macro_dict[macro_name] = macro_class
        
        if fire_event:
            self._fireMacroEvent()
   
    def getMacroNames(self):
        return sorted(self._macro_dict.keys())

    def getMacroLibNames(self):
        return sorted(self._modules.keys())

    def _fireMacroEvent(self, data=None):
        """Helper method that fires event for the current existing macros"""
        macro_list = data or self.getMacroNames()
        self._macro_list_obj.fireEvent(macro_list)
        return macro_list
    
    def _fireMacroLibEvent(self, data=None):
        """Helper method that fires event for the current existing macro 
        libraries(=modules)"""
        macro_lib_list = data or self.getMacroLibNames()
        self._macro_lib_list_obj.fireEvent(macro_lib_list)
        return macro_lib_list
    
    def getMacroLibs(self):
        return self._modules

    def getMacros(self, filter=None):
        if filter is None:
            return sorted(self._macro_dict.values())
        expr = re.compile(filter, re.IGNORECASE)
        
        ret = [ kls for n, kls in self._macro_dict.iteritems() if not expr.match(n) is None ]
        ret.sort()
        return ret

    def getMacroMetaClass(self, macro_name):
        ret = self._macro_dict.get(macro_name)
        if ret is None:
            raise UnknownMacro("Unknown macro %s" % macro_name)
        return ret
    
    def getMacroLib(self, module_name):
        return self._modules.get(module_name)
        
    def getMacroListObj(self):
        return self._macro_list_obj
    
    def getMacroLibListObj(self):
        return self._macro_lib_list_obj

    def getMacroClass(self, macro_name):
        return self.getMacroMetaClass(macro_name).klass

    def getMacroInfo(self, macro_names, format='json'):
        if isinstance(macro_names, str):
            macro_names = [macro_names]
            
        m = self._getPlainMacroInfo
        if format == 'json':
            m = self._getJSONMacroInfo
        return m(macro_names)
    
    def _getPlainMacroInfo(self, macro_names):
        ret = []
        for macro_name in macro_names:
            macro_class = self.getMacroMetaClass(macro_name)
            if macro_class is not None:
                ret += macro_class.getInfo()
        return ret

    def _getJSONMacroInfo(self, macro_names):
        ret = []
        for macro_name in macro_names:
            macro_class = self.getMacroMetaClass(macro_name)
            ret.append(macro_class.getJSON())
        return ret

    def decodeMacroParameters(self, in_par_list):
        if len(in_par_list) == 0:
            raise RuntimeError('Macro name not specified')
        macro_name_or_klass = in_par_list[0]
        macro_class = macro_name_or_klass
        if type(macro_class) in types.StringTypes:
            macro_class = self.getMacroClass(macro_class)
        if macro_class is None:
            raise UnknownMacro("Unknown macro %s" % macro_name_or_klass)
        import parameter
        out_par_list = parameter.ParamDecoder(macro_class, in_par_list)
        return macro_class, in_par_list, out_par_list

    def strMacroParamValues(self,par_list):
        """strMacroParamValues(list<string> par_list) -> list<string> 
        
           Creates a short string representantion of the parameter values list.
           Params:
               - par_list: list of strings representing the parameter values.
           Return:
               a list containning an abreviated version of the par_list argument. 
        """
        ret = []
        for p in par_list:
            param_str = str(p)
            if len(param_str)>9:
                param_str = param_str[:9] + "..."
            ret.append(param_str)
        return ret

    def prepareMacro(self, macro_class, par_list, init_opts={}, prepare_opts={}):
        """Creates the macro object and calls its prepare method.
           The return value is a tuple (MacroObject, return value of prepare)
        """
        macro = self.createMacroObj(macro_class, par_list, init_opts=init_opts)
        prepare_result = self.prepareMacroObj(macro, par_list, prepare_opts=prepare_opts)
        return macro, prepare_result
    
    def createMacroObj(self, macro_class, par_list, init_opts={}):
        macro_env = macro_class.env
        macro_name = macro_class.__name__
        
        environment = init_opts.get('environment')
        
        r = []
        for env in macro_env:
            if not environment.hasEnv(env):
                r.append(env)
        if r:
            raise MissingEnv("The macro %s requires the following missing " \
                             "environment to be defined: %s" 
                             % (macro_name, str(r)))
        
        macro_opts = { 
            'no_exec': True, 
            'create_thread' : True,
            'external_prepare' : True 
        }
        
        macro_opts.update(init_opts)
        macroObj = macro_class(*par_list, **macro_opts)
        return macroObj
    
    def prepareMacroObj(self, macro, par_list, prepare_opts={}):
        return macro.prepare(*par_list, **prepare_opts)
    
    def getMacroExecutor(self, door):
        me = self._macro_executors.get(door)
        if me is None:
            self._macro_executors[door] = me = MacroExecutor(door)
        return me



class MacroExecutor(Logger):
    """ """
    
    class RunSubXMLHook:
        def __init__(self, me, xml):
            self._me = me
            self._xml = xml
        
        def __call__(self):
            self._me._runXMLMacro(xml=self._xml)
    
    def __init__(self, door):
        self._door = door
        self._macro_stack = None
        self._xml_stack = None
        self._macro_pointer = None
        self._macro_counter = 0
        self._aborted = False
        self._paused = False
        self._last_macro_status = None
        name = "%s.%s" % (str(door), self.__class__.__name__)
        self._macro_status_codec = CodecFactory().getCodec('json')
        self.call__init__(Logger, name)
    
    def _preprocessParameters(self, par_str_list):
        if not par_str_list[0].lstrip().startswith('<'):
            xml_root = xml_seq = etree.Element('sequence')
            xml_macro = etree.SubElement(xml_seq, 'macro', name=par_str_list[0])
            for p in par_str_list[1:]:
                xml_param = etree.SubElement(xml_macro, 'param', value=p)
        else:
            xml_root = etree.fromstring(par_str_list[0])

        macro_nodes = xml_root.findall('.//macro')

        # make sure macros exist
        self.__checkXMLSequence(macro_nodes)
        
        # fill the xml with macro id macro_line
        self.__fillXMLSequence(macro_nodes)
        
        return xml_root

    def __checkXMLSequence(self, macros):
        for macro in macros:
            name = macro.get('name')
            self.manager.getMacroMetaClass(name)

    def __fillXMLSequence(self, macros):
        for macro in macros:
            id = macro.get('id')
            if id is None:
                id = str(self.getNewMacroID())
                macro.set('id', id)
            name = macro.get('name')
            params = []
            for p in macro.xpath('param|paramrepeat'):
                if p.tag == 'param':
                    params.append(p.get('value'))
                else:
                    params.extend([ p2.get('value') for p2 in p.findall(".//param")])
            macro.set('macro_line', "%s(%s)" % (name, ", ".join(params)))

    def __preprocessResult(self, result):
        """decodes the given output from a macro in order to be able to send to 
        the result channel as a sequence<str>
           
        :param out: output value
           
        :return: the output as a sequence of strings
        """
        if result is None:
            return ()
        if operator.isSequenceType(result) and not type(result) in types.StringTypes:
            result = map(str, result)
        else:
            result = (str(result),)
        return result
    
    def _decodeXMLMacroParameters(self, xml_macro):
        str_params = [xml_macro.get('name')]
        for param in xml_macro.findall('.//param'):
            str_params.append(param.get('value'))
        return self.manager.decodeMacroParameters(str_params)
    
    def _decodeMacroParameters(self, params):
        return self.manager.decodeMacroParameters(params)
    
    def _prepareXMLMacro(self, xml_macro, parent_macro=None):
        macro_klass, str_params, params = self._decodeXMLMacroParameters(xml_macro)
        init_opts = { 
            'id'           : xml_macro.get('id'),
            'macro_line'   : xml_macro.get('macro_line'),
            'parent_macro' : parent_macro,
        }
        
        macro_obj = self._createMacroObj(macro_klass, params, init_opts)
        for macro in xml_macro.findall('macro'):
            hook = MacroExecutor.RunSubXMLHook(self, macro)
            hook_hints = macro.findall('hookPlace')
            if hook_hints is None:
                macro_obj.hooks = [ hook ]
            else:
                hook_places = [ h.text for h in hook_hints ]
                macro_obj.hooks = [ (hook, hook_places) ]
        prepare_result = self._prepareMacroObj(macro_obj, params)
        return macro_obj, prepare_result
    
    def _createMacroObj(self, macro_name_or_klass, pars, init_opts={}):
        macro_klass = macro_name_or_klass
        if type(macro_klass) in types.StringTypes:
            macro_klass = self.manager.getMacroClass(macro_klass)

        macro_opts = {
            'executor'    : self,
            'environment' : self.main_manager
        }
        macro_opts.update(init_opts)
        if not macro_opts.has_key('id'):
            macro_opts['id'] = str(self.getNewMacroID())

        macroObj = self.manager.createMacroObj(macro_klass, pars, init_opts=macro_opts)
        
        return macroObj
    
    def _prepareMacroObj(self, macro_obj, pars, prepare_opts={}):
        return self.manager.prepareMacroObj(macro_obj, pars, prepare_opts=prepare_opts)
    
    def prepareMacroObj(self, macro_name_or_klass, pars, init_opts={}, prepare_opts={}):
        """Prepare a new macro for execution
        
        :param macro_name_or_klass name: name of the macro to be prepared or 
                                         the macro class itself
        :param pars: list of parameter objects
        :param init_opts: keyword parameters for the macro constructor
        :param prepare_opts: keyword parameters for the macro prepare
           
        :return: a tuple of two elements: macro object, the result of preparing the macro"""
        macroObj = self._createMacroObj(macro_name_or_klass, pars, init_opts=init_opts)
        prepare_result = self._prepareMacroObj(macroObj, pars, prepare_opts=prepare_opts)
        return macroObj, prepare_result
    
    def prepareMacro(self, pars, init_opts={}, prepare_opts={}):
        """Prepare a new macro for execution
           Several different parameter formats are supported:
           1. several parameters:
             1.1 executor.prepareMacro('ascan', 'th', '0', '100', '10', '1.0')
             1.2 executor.prepareMacro('ascan', 'th', 0, 100, 10, 1.0)
             1.3 th = self.getObj('th');
                 executor.prepareMacro('ascan', th, 0, 100, 10, 1.0)
           2. a sequence of parameters:
              2.1 executor.prepareMacro(['ascan', 'th', '0', '100', '10', '1.0')
              2.2 executor.prepareMacro(('ascan', 'th', 0, 100, 10, 1.0))
              2.3 th = self.getObj('th');
                  executor.prepareMacro(['ascan', th, 0, 100, 10, 1.0])
           3. a space separated string of parameters:
              executor.prepareMacro('ascan th 0 100 10 1.0')

        :param pars: the command parameters as explained above
        :param opts: keyword optional parameters for prepare
        :return: a tuple of two elements: macro object, the result of preparing the macro
        """
        par0 = pars[0]
        if len(pars) == 1:
            if type(par0) in types.StringTypes :
                pars = par0.split(' ')
            elif operator.isSequenceType(par0):
                pars = par0
        pars = map(str, pars)

        macro_klass, str_pars, pars = self._decodeMacroParameters(pars)
        
        init_opts['macro_line'] = "%s(%s) -> [%s]" % (str_pars[0], ", ".join(str_pars[1:]), id) 
        if not init_opts.has_key('id'):
            init_opts['id'] = str(self.getNewMacroID())
        return self.prepareMacroObj(macro_klass, pars, init_opts, prepare_opts)
        
    @property
    def manager(self):
        return MacroManager()
    
    @property
    def main_manager(self):
        import manager
        return manager.MacroServerManager()
    
    def getDoor(self):
        return self._door

    def getNewMacroID(self):
        self._macro_counter -= 1
        return self._macro_counter
    
    def getRunningMacro(self):
        return self._macro_pointer

    def __abortObjects(self):
        """Aborts all the reserved objects in the executor"""
        for objs in self._reserved_macro_objs.values():
            for obj in objs:
                try:
                    obj.abort()
                except AttributeError:
                    pass
                except Exception:
                    self.warning("Unable to abort %s" % obj)
                    self.debug("Unable to abort %s. Details:", obj, exc_info=1)

    def abort(self):
        self._aborted, m = True, self.getRunningMacro()
        if m is not None:
            m.abort()
            if m.isPaused():
                m.resume(cb=self._macroResumed)
        self.__abortObjects()
    
    def pause(self):
        self._paused = True
        m = self.getRunningMacro()
        if m is not None:
            m.pause(cb=self._macroPaused)
    
    def _macroPaused(self, m):
        """Calback that is executed when the macro has efectively paused"""
        self.sendMacroStatusPause()
        self.sendState(MacroManager.Pause)
    
    def resume(self):
        if not self._paused:
            return
        self._paused = False
        m = self.getRunningMacro()
        if m is not None:
            m.resume(cb=self._macroResumed)
    
    def _macroResumed(self, m):
        """Calback that is executed when the macro has efectively resumed 
        ejecution after being paused"""
        self.sendMacroStatusResume()
        self.sendState(MacroManager.Running)
    
    def run(self, params):
        """Runs the given macro(s)
        
        :param params: (sequence<str>) can be either a sequence of <macro name> [, <macro_parameter> ]
                       or a sequence with a single element which represents the xml string for a
                       macro script
        :return: (lxml.etree.Element) the xml representation of the running macro
        """
        
        # dict<PoolElement, set<Macro>>
        # key PoolElement - reserved object
        # value set<Macro> macros that reserved the object
        self._reserved_objs = {}
        
        # dict<Macro, seq<PoolElement>>
        # key Macro - macro object
        # value - sequence of reserverd objects by the macro
        self._reserved_macro_objs = {}

        # reset the stacks
        self._macro_stack = []
        self._xml_stack = []
        self._macro_pointer = None
        self._aborted = False
        self._paused = False
        self._last_macro_status = None
        
        # convert given parameters into an xml
        self._xml = self._preprocessParameters(params)

        # start the job of actually running the macro
        self.main_manager.addJob(self.__runXML, self._jobEnded)
        #return the proper xml
        return self._xml

    def _jobEnded(self, *args, **kw):
        self.debug("Job ended")

    def __runXML(self):
        self.sendState(MacroManager.Running)
        try:
            self.__runStatelessXML()
        except AbortException as ae:
            pass
        except Exception as e:
            pass
        finally:
            self._macro_stack = None
            self._xml_stack = None
            self.sendState(MacroManager.Finished)
    
    def __runStatelessXML(self, xml=None):
        if xml is None:
            xml = self._xml
        node = xml.tag
        if node == 'sequence':
            for xml_macro in xml.findall('macro'):
                self.__runXMLMacro(xml_macro)
        elif node == 'macro':
            self.__runXMLMacro(xml)
    
    def __runXMLMacro(self, xml):
        assert xml.tag == 'macro'
        try:
            macro_obj, ret = self._prepareXMLMacro(xml)
        except AbortException as ae:
            raise ae
        except Exception as e:
            door = self.getDoor()
            door.debug(traceback.format_exc())
            door.error("An error occured while preparing macro %s:\n%s" % (xml.get('macro_line'), str(e)))
            raise e
        
        self._xml_stack.append(xml)
        try:
            self.runMacro(macro_obj)
        finally:
            self._xml_stack.pop()
    
    _runXMLMacro = __runXMLMacro
    
    def runMacro(self, macro_obj):
        name = macro_obj._getName()
        desc = macro_obj._getDescription()
        if self._aborted:
            self.sendMacroStatusAbort()
            raise AbortException("aborted between macros (before %s)" % name)
        macro_exp, tb, result = None, None, None
        try:
            self.debug("[START] runMacro %s" % desc)
            self._macro_pointer = macro_obj
            self._macro_stack.append(macro_obj)

            for step in macro_obj.exec_():
                self.sendMacroStatus((step,))
                
            if macro_obj.hasResult() and macro_obj.getParentMacro() is None:
                result = macro_obj.getResult()
                door = self.getDoor()
                door.push_change_event('Result', self.__preprocessResult(result))
        except AbortException as ae:
            macro_exp = ae
        except MacroServerException as mse:
            exc_info = sys.exc_info()
            macro_exp = mse
            if not mse.traceback:
                mse.traceback = traceback.format_exc()
        except DevFailed as df:
            exc_info = sys.exc_info()
            exp_pars = {'type'      : df[0].reason,
                        'msg'       : df[0].desc,
                        'args'      : df.args,
                        'traceback' : traceback.format_exc() }
            macro_exp = MacroServerException(exp_pars)
        except Exception, err:
            exc_info = sys.exc_info()
            exp_pars = {'type'      : err.__class__.__name__,
                        'msg'       : err.args[0],
                        'args'      : err.args,
                        'traceback' : traceback.format_exc() }
            macro_exp = MacroServerException(exp_pars)
        finally:
            self.returnObjs(self._macro_pointer)
        
        # make sure the macro's on_abort is called and that a proper macro
        # status is sent
        if self._aborted:
            macro_obj._abortOnError()
            self.sendMacroStatusAbort()
        
        # From this point on don't call any method of macro_obj which is part
        # of the mAPI (methods decorated with @mAPI) to avoid throwing an
        # AbortException if an Abort has been performed.
        if macro_exp is not None:
            if not self._aborted:
                self.sendMacroStatusException(exc_info)
            self.debug("[ENDEX] (%s) runMacro %s" % (macro_exp.__class__.__name__, name))
            if isinstance(macro_exp, MacroServerException) and macro_obj.parent_macro is None:
                door = self.getDoor()
                door.debug(macro_exp.traceback)
                door.error("An error occured while running macro %s:\n%s" % (macro_obj.description, macro_exp.msg))
            self._popMacro()
            raise macro_exp
        self.debug("[ END ] runMacro %s" % desc)
        self._popMacro()
        return result

    def _popMacro(self):
        curr_macro = self._macro_stack.pop()
        length = len(self._macro_stack)
        if length > 0:
            self._macro_pointer = self._macro_stack[-1]
        else:
            self._macro_pointer = None

    def sendState(self, state):
        return self.getDoor().sendState(state)
    
    def sendStatus(self, status):
        return self.getDoor().sendStatus(status)

    def getLastMacroStatus(self):
        return self._macro_pointer.getMacroStatus()

    def sendMacroStatusAbort(self):
        ms = self.getLastMacroStatus()
        if ms is not None:
            ms['state'] = 'abort'
            
            self.debug("Sending abort event %s", ms)
            self.sendMacroStatus((ms,))

    def sendMacroStatusException(self, exc_info):
        ms = self.getLastMacroStatus()
        if ms is not None:
            ms['state'] = 'exception'
            ms['exc_type'] = str(exc_info[0])
            ms['exc_value'] = str(exc_info[1])
            ms['exc_stack'] = traceback.format_exception(*exc_info)
            self.debug("Sending exception event %s", ms)
            self.sendMacroStatus((ms,))

    def sendMacroStatusPause(self):
        ms = self.getLastMacroStatus()
        if ms is not None and len(ms) > 0:
            ms['state'] = 'pause'
            self.debug("Sending pause event %s", ms)
            self.sendMacroStatus((ms,))

    def sendMacroStatusResume(self):
        ms = self.getLastMacroStatus()
        if ms is not None and len(ms) > 0:
            ms['state'] = 'resume'
            self.debug("Sending resume event %s", ms)
            self.sendMacroStatus((ms,))

    def sendMacroStatus(self, data):
        self._last_macro_status = data
        data = self._macro_status_codec.encode(('', data))
        return self.getDoor().sendMacroStatus(*data)
    
    def sendRecordData(self, *data):
        door = self.getDoor()
        return door.sendRecordData(*data)
    
    def reserveObj(self, obj, macro_obj, priority=0):
        if obj is None or macro_obj is None: return
        
        # Fill _reserved_macro_objs
        objs = self._reserved_macro_objs[macro_obj] = \
            self._reserved_macro_objs.get(macro_obj, list())
        if not obj in objs:
            if priority:
                objs.insert(0, obj)
            else:
                objs.append(obj)
        
        # Fill _reserved_objs
        macros = self._reserved_objs[obj] = self._reserved_objs.get(obj, set())
        macros.add(macro_obj)
        
        # Tell the object that it is reserved by a new macro
        if hasattr(obj, 'reserve'): obj.reserve(macro_obj)
    
    def returnObjs(self, macro_obj):
        """Free the macro reserved objects"""
        if macro_obj is None: return
        objs = self._reserved_macro_objs.get(macro_obj)
        if objs is None: return
        
        # inside returnObj we change the list so we have to iterate with a copy
        for obj in copy.copy(objs):
            self.returnObj(obj, macro_obj)
    
    def returnObj(self, obj, macro_obj):
        """Free an object reserved by a macro"""
        if obj is None or macro_obj is None: return
        
        if hasattr(obj, 'unreserve'): obj.unreserve()
        objs = self._reserved_macro_objs.get(macro_obj)
        if objs is None:
            return
        objs.remove(obj)
        if len(objs) == 0:
            del self._reserved_macro_objs[macro_obj]
        
        try:
            macros = self._reserved_objs[obj]
            macros.remove(macro_obj)
            if not len(macros):
                del self._reserved_objs[obj]
        except KeyError:
            self.debug("Unexpected KeyError trying to remove reserved object")

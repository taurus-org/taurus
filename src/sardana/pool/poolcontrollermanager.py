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

"""This module is part of the Python Pool library. It defines the class which
controls finding, loading/unloading of device pool controller plug-ins."""

__all__ = ["ControllerManager" ]

__docformat__ = 'restructuredtext'

import sys
import os
import inspect
import copy

import types
import re

from taurus.core import ManagerState
from taurus.core.util import Singleton, Logger

from sardana.sardanamodulemanager import ModuleManager

import controller
from poolexception import UnknownController
from poolmetacontroller import ControllerLibrary, ControllerClass

CONTROLLER_TEMPLATE = '''

class @controller_name@(MotorController):
    """This class representes a Sardana motor controller."""
    
    ctrl_features = []
    MaxDevice = 1024
    
    ctrl_properties = {}
    ctrl_attributes = {}
    axis_attributes = {}
    
    def __init__(self, inst, props, *args, **kwargs):
        MotorController.__init__(self, inst, props, *args, **kwargs)

'''

class ControllerManager(Singleton, Logger):
    """The singleton class responsible for managing controller plug-ins."""
    
    DEFAULT_CONTROLLER_DIRECTORIES = 'poolcontrollers',
    
    def __init__(self):
        """Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self._state = ManagerState.UNINITIALIZED
        self.call__init__(Logger, name)
        self._pool = None
        self.reInit()

    def reInit(self):
        """Singleton re-initialization."""
        if self._state == ManagerState.INITED:
            return
        
        #: dict<str, metacontroller.ControllerLibray>
        #: key   - module name (without path and without extension)
        #: value - ControllerLibrary object representing the module 
        self._modules = {}
        
        #: dict<str, <metacontroller.ControllerClass>
        #: key   - controller name
        #: value - ControllerClass object representing the controller
        self._controller_dict = {}
    
        #: list<str>
        #: elements are absolute paths
        self._controller_path = []
        
        l = []
        for _, klass in inspect.getmembers(controller, inspect.isclass):
            if not issubclass(klass, controller.Controller):
                continue
            l.append(klass)
        self._base_classes = l
        
        self._state = ManagerState.INITED

    def cleanUp(self):
        """Singleton clean up."""
        if self._state == ManagerState.CLEANED:
            return
        
        #if self._modules:
        #    ModuleManager().unloadModules(self._modules.keys())
        
        self._controller_path = None
        self._controller_dict = None
        self._modules = None
        
        self._state = ManagerState.CLEANED
    
    def set_pool(self, pool):
        self._pool = pool
    
    def get_pool(self):
        return self._pool
    
    def setControllerPath(self, controller_path, reload=True):
        """Registers a new list of controller directories in this manager.
        
        :param seq<str> controller_path: a sequence of absolute paths where this
                                         manager should look for controllers
        
        .. warning::
            as a consequence all the controller modules will be reloaded.
            This means that if any reference to an old controller object was
            kept it will refer to an old module (which could possibly generate
            problems of type class A != class A)."""
        p = []
        for item in controller_path:
            p.extend(item.split(":"))
        
        # filter empty and commented paths
        p = [ i for i in p if i and not i.startswith("#") ]
        
        # add basic dummy controller directory(ies)
        pool_dir = os.path.dirname(os.path.abspath(__file__))
        for ctrl_dir in self.DEFAULT_CONTROLLER_DIRECTORIES:
            ctrl_dir = os.path.join(pool_dir, ctrl_dir)
            if not ctrl_dir in p:
                p.append(ctrl_dir)
        
        self._controller_path = p
        
        controller_file_names = self._findControllerLibNames()
        
        for controller_file_name in controller_file_names:
            try:
                self.reloadControllerLib(controller_file_name, reload=reload)
            except Exception:
                pass
        
    def getControllerPath(self):
        """Returns the current sequence of absolute paths used to look for
        controllers.
        
        :return: sequence of absolute paths
        :rtype: seq<str>"""
        return self._controller_path

    def _findControllerLibNames(self, path=None):
        """internal method"""
        path = path or self.getControllerPath()
        ret = []
        for p in path:
            try:
                for f in os.listdir(p):
                    name,ext = os.path.splitext(f)
                    if not name[0].isalpha():
                        continue
                    if ext.endswith('py'):
                        ret.append(name)
            except:
                self.debug("'%s' is not a valid path" % p)
        return ret

    def _fromNameToFileName(self, lib_name, path=None):
        """internal method"""
        path = path or self.getControllerPath()[0]
        f_name = lib_name
        if not f_name.endswith('.py'):
            f_name += '.py'
            
        if os.path.isabs(f_name):
            path, _ = os.path.split(f_name)
            if not path in self.getControllerPath():
                raise Exception("'%s' is not part of the PoolPath" % path)
        else:
            f_name = os.path.join(path, f_name)
        return f_name

    def getOrCreateControllerLib(self, lib_name, controller_name=None):
        """Gets the exiting controller lib or creates a new controller lib file.
        If name is not None, a controller template code for the given controller
        name is appended to the end of the file.
        
        :param str lib_name: module name, python file name, or full file name
                             (with path)
        :param str controller_name: an optional controller name. If given a
                                    controller template code is appended to the
                                    end of the file [default: None, meaning no
                                    controller code is added)
        
        :return: a sequence with three items: full_filename, code, line number
                 line number is 0 if no controller is created or n representing
                 the first line of code for the given controller name.
        :rtype: tuple<str, str, int>
        """
        # if only given the module name
        controller_lib = self.getControllerLib(lib_name)
        
        if controller_name is None:
            line_nb = 0
            if controller_lib is None:
                f_name, code = self.createControllerLib(lib_name), ''
            else:
                f_name = controller_lib.get_file_name()
                f = file(f_name)
                code = f.read()
                f.close()
        else:
        # if given controller name
            if controller_lib is None:
                f_name, code, line_nb = self.createController(lib_name, controller_name)
            else:
                controller = controller_lib.get_controller(controller_name)
                if controller is None:
                    f_name, code, line_nb = self.createController(lib_name, controller_name)
                else:
                    _, line_nb = controller.getCode()
                    f_name = controller.getFileName()
                    f = file(f_name)
                    code = f.read()
                    f.close()
                
        return [ f_name, code, line_nb ]

    def setControllerLib(self, lib_name, code):
        """Creates a new controller library file with the given name and code.
        The new module is imported and becomes imediately available.
        
        :param str lib_name: name of the new library
        :param str code: python code of the new library"""
        f_name = self._fromNameToFileName(lib_name)
        f = open(f_name, 'w')
        f.write(code)
        f.flush()
        f.close()
        _, name = os.path.split(f_name)
        mod, _ = os.path.splitext(name)
        self.reloadControllerLib(mod)

    def createControllerLib(self, lib_name, path=None):
        """Creates a new empty controller library (python module)"""
        f_name = self._fromNameToFileName(lib_name, path)
        
        if os.path.exists(f_name):
            raise Exception("Unable to create controller lib: '%s' already exists" % f_name)
            
        f = open(f_name, 'w')
        f.close()
        return f_name

    def createController(self, lib_name, controller_name):
        """Creates a new controller"""
        f_name = self._fromNameToFileName(lib_name)
        
        create = not os.path.exists(f_name)
        
        template = ''
        if create:
            template += 'from sardana.pool.controller import *\n\n'
            line_nb = 4
        else:
            template += '\n'
            t = open(f_name, 'rU')
            line_nb = -1
            for line_nb, _ in enumerate(t): pass
            line_nb += 3
            t.close()
            
        f = open(f_name, 'a+')
        try:
            dir_name = os.path.realpath(__file__)
            dir_name = os.path.dirname(dir_name)
            template_fname = 'controller_template.txt'
            template_fname = os.path.join(dir_name, template_fname)
            f_templ = open(template_fname, 'r')
            template += f_templ.read()
            f_templ.close()
        except:
            self.debug("Failed to open template controller file. Using simplified template")
            template += CONTROLLER_TEMPLATE
            if f_templ:
                f_templ.close()
                
        template = template.replace('@controller_name@', controller_name)
        try:
            f.write(template)
            f.flush()
            f.seek(0)
            code = f.read()
        finally:
            f.close()
        return f_name, code, line_nb

    def reloadController(self, controller_name, path=None):
        """Reloads the module corresponding to the given controller name
        
        :raises: :exc:`sardana.pool.poolexception.UnknownController`
                 in case the controller is unknown or :exc:`ImportError` if
                 the reload process is not successfull
        
        :param str controller_name: controller class name
        :param seq<str> path: a list of absolute path to search for libraries 
                              [default: None, meaning the current ControllerPath
                              will be used]"""
        self.reloadControllers([controller_name], path=path)
        
    def reloadControllers(self, controller_names, path=None):
        """Reloads the modules corresponding to the given controller names
        
        :raises: :exc:`sardana.pool.poolexception.UnknownController`
                 in case the controller is unknown or :exc:`ImportError` if
                 the reload process is not successful
        
        :param seq<str> controller_names: a list of controller class names
        :param seq<str> path: a list of absolute path to search for libraries
                              [default: None, meaning the current ControllerPath
                              will be used]"""
        module_names = []
        for controller_name in controller_names:
            module_name = self.getControllerMetaClass(controller_name).get_module_name()
            module_names.append(module_name)
        self.reloadControllerLibs(module_names, path=path)
    
    def reloadControllerLibs(self, module_names, path=None, reload=True):
        """Reloads the given library(=module) names
        
        :raises: :exc:`sardana.pool.poolexception.UnknownController`
                 in case the controller is unknown or :exc:`ImportError` if
                 the reload process is not successful
        
        :param seq<str> module_names: a list of module names
        :param seq<str> path: a list of absolute path to search for libraries
                              [default: None, meaning the current ControllerPath
                              will be used]"""
        ret = []
        for module_name in module_names:
            try:
                m = self.reloadControllerLib(module_name, path, reload=reload)
                if m: ret.append(m)
            except:
                self.info("Failed to reload controller library %s", module_name)
                self.debug("Failed to reload controller library %s details",
                           module_name, exc_info=1)
        
        return ret

    def reloadControllerLib(self, module_name, path=None, reload=True):
        """Reloads the given library(=module) names
        
        :raises: :exc:`sardana.pool.poolexception.UnknownController`
                 in case the controller is unknown or :exc:`ImportError` if
                 the reload process is not successful
        
        :param str module_name: controller library name (=python module name)
        :param seq<str> path: a list of absolute path to search for libraries
                              [default: None, meaning the current ControllerPath
                              will be used]
        
        :return: the ControllerLib object for the reloaded controller lib
        :rtype: sardana.pool.poolmetacontroller.ControllerLibrary
        """
        path = path or self.getControllerPath()
        # reverse the path order:
        # more priority elements last. This way if there are repeated elements
        # they first ones (lower priority) will be overwritten by the last ones
        if path:
            path = copy.copy(path)
            path.reverse()
        
        # if there was previous Controller Lib info remove it
        if self._modules.has_key(module_name):
            self._modules.pop(module_name)
        
        m, exc_info = None, None
        try:
            m = ModuleManager().reloadModule(module_name, path, reload=reload)
        except:
            exc_info = sys.exc_info()
            
        controller_lib = None
        params = dict(module=m, name=module_name, pool=self.get_pool())
        if m is None or exc_info is not None:
            params['exc_info'] = exc_info
            controller_lib = ControllerLibrary(**params)
            self._modules[module_name] = controller_lib
        else:
            controller_lib = ControllerLibrary(**params)
            lib_contains_controllers = False
            abs_file = controller_lib.file_path
            for _, klass in inspect.getmembers(m, inspect.isclass):
                if issubclass(klass, controller.Controller):
                    # if it is a class defined in some other class forget it to
                    # avoid replicating the same controller in different
                    # controller files
                    if inspect.getabsfile(klass) != abs_file:
                        continue
                    lib_contains_controllers = True
                    self.addController(controller_lib, klass)
            
            if lib_contains_controllers:
                self._modules[module_name] = controller_lib
        
        return controller_lib
    
    def addController(self, controller_lib, klass):
        """Adds a new controller class"""
        controller_name = klass.__name__
        exists = controller_lib.has_controller(controller_name)
        if exists:
            action = "Updating"
        else:
            action = "Adding"
        
        self.debug("%s controller %s" % (action, controller_name))
        
        try:
            controller_class = ControllerClass(pool=self.get_pool(),
                                               lib=controller_lib, klass=klass)
            #self._setControllerTypes(klass, controller_class)
            controller_lib.add_controller(controller_class)
            self._controller_dict[controller_name] = controller_class
            
        except:
            self.warning("Failed to add controller class %s", controller_name,
                         exc_info=1)
        
        if exists:
            action = "Updated"
        else:
            action = "Added"
        self.debug("%s controller %s" % (action, controller_name))
   
    def getControllerNames(self):
        return sorted(self._controller_dict.keys())

    def getControllerLibNames(self):
        return sorted(self._modules.keys())
    
    def getControllerLibs(self, filter=None):
        ret, expr = [], None
        if filter is not None:
            expr = re.compile(filter, re.IGNORECASE)
        for name, lib in self._modules.iteritems():
            if lib.has_errors() or (expr is not None and expr.match(name) is None):
                continue
            ret.append(lib)
        ret.sort()
        return ret
    
    def getControllers(self, filter=None):
        if filter is None:
            return sorted(self._controller_dict.values())
        expr = re.compile(filter, re.IGNORECASE)
        
        ret = [ kls for n, kls in self._controller_dict.iteritems() if not expr.match(n) is None ]
        ret.sort()
        return ret
    
    def getControllerMetaClass(self, controller_name):
        ret = self._controller_dict.get(controller_name)
        if ret is None:
            raise UnknownController("Unknown controller %s" % controller_name)
        return ret
    
    def getControllerMetaClasses(self, controller_names):
        ret = {}
        for name in controller_names:
            ret[name] = self._controller_dict.get(name)
        return ret
    
    def getControllerLib(self, name):
        if os.path.isabs(name):
            abs_file_name = name
            for lib in self._modules.values():
                if lib.file_path == abs_file_name:
                    return lib
        elif name.count(os.path.extsep):
            file_name = name
            for lib in self._modules.values():
                if lib.file_name == file_name:
                    return lib
        module_name = name
        return self._modules.get(module_name)
    
    def getControllerClass(self, controller_name):
        return self.getControllerMetaClass(controller_name).klass
    
    def _getPlainControllerInfo(self, controller_names):
        ret = []
        for controller_name in controller_names:
            controller_class = self.getControllerMetaClass(controller_name)
            if controller_class is not None:
                ret += controller_class.getInfo()
        return ret
    
    def decodeControllerParameters(self, in_par_list):
        if len(in_par_list) == 0:
            raise RuntimeError('Controller name not specified')
        controller_name_or_klass = in_par_list[0]
        controller_class = controller_name_or_klass
        if type(controller_class) in types.StringTypes:
            controller_class = self.getControllerClass(controller_class)
        if controller_class is None:
            raise UnknownController("Unknown controller %s" % controller_name_or_klass)
        import parameter
        out_par_list = msparameter.ParamDecoder(controller_class, in_par_list)
        return controller_class, in_par_list, out_par_list

    def strControllerParamValues(self,par_list):
        """Creates a short string representation of the parameter values list.
           
           :param par_list: list of strings representing the parameter values.
           :type par_list: list<str>
           :return: a list containning an abreviated version of the par_list
                    argument.
           :rtype: list<str>
        """
        ret = []
        for p in par_list:
            param_str = str(p)
            if len(param_str)>9:
                param_str = param_str[:9] + "..."
            ret.append(param_str)
        return ret


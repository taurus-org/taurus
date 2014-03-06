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

__all__ = ["MacroManager", "MacroExecutor", "is_macro"]

__docformat__ = 'restructuredtext'

import sys
import os
import inspect
import copy
import re
import functools
import traceback

from lxml import etree

from PyTango import DevFailed
from taurus.core.util.log import Logger
from taurus.core.util.codecs import CodecFactory

from sardana.sardanadefs import ElementType
from sardana.sardanamodulemanager import ModuleManager
from sardana.sardanaexception import format_exception_only_str
from sardana.sardanautils import is_pure_str, is_non_str_seq

from .msmanager import MacroServerManager
from .msmetamacro import MACRO_TEMPLATE, MacroLibrary, MacroClass, MacroFunction
from .msparameter import ParamDecoder
from .macro import Macro, MacroFunc
from .msexception import UnknownMacroLibrary, LibraryError, UnknownMacro, \
    MissingEnv, AbortException, StopException, MacroServerException

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def islambda(f):
    """inspect doesn't come with islambda so I create one :-P"""
    return inspect.isfunction(f) and \
           f.__name__ == (lambda: True).__name__

def is_macro(macro, abs_file=None, logger=None):
    """Helper function to determine if a certain python object is a valid
    macro"""
    if inspect.isclass(macro):
        if not issubclass(macro, Macro):
            return False
        # if it is a class defined in some other module forget it to
        # avoid replicating the same macro in different macro files
        try:
            if inspect.getabsfile(macro) != abs_file:
                return False
        except TypeError:
            return False
    elif callable(macro) and not islambda(macro):
        # if it is a function defined in some other module forget it to
        # avoid replicating the same macro in different macro files
        try:
            if inspect.getabsfile(macro) != abs_file:
                return False
        except TypeError:
            return False

        if not hasattr(macro, 'macro_data'):
            return False

        args, varargs, keywords, _ = inspect.getargspec(macro)
        if len(args) == 0:
            if logger:
                logger.debug("Could not add macro %s: Needs at least one "
                             "parameter (usually called 'self')",
                             macro.func_name)
            return False
        if keywords is not None:
            if logger:
                logger.debug("Could not add macro %s: Unsupported keyword "
                             "parameters '%s'", macro.func_name, keywords)
            return False
        if varargs and len(args) > 1:
            if logger:
                logger.debug("Could not add macro %s: Unsupported giving "
                             "named parameters '%s' and varargs '%s'",
                             macro.func_name, args, varargs)
            return False
    else:
        return False
    return True


class MacroManager(MacroServerManager):

    DEFAULT_MACRO_DIRECTORIES = os.path.join(_BASE_DIR, 'macros'),

    def __init__(self, macro_server, macro_path=None):
        MacroServerManager.__init__(self, macro_server)
        if macro_path is not None:
            self.setMacroPath(macro_path)

    def reInit(self):
        if self.is_initialized():
            return

        # dict<str, MacroLibrary>
        # key   - module name (without path and without extension)
        # value - MacroLibrary object representing the module
        self._modules = {}

        # dict<str, <MacroClass>
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

        MacroServerManager.reInit(self)

    def cleanUp(self):
        if self.is_cleaned():
            return

        #if self._modules:
        #    ModuleManager().unloadModules(self._modules.keys())

        self._macro_path = None
        self._macro_dict = None
        self._modules = None

        MacroServerManager.cleanUp(self)

    def setMacroPath(self, macro_path):
        """Registers a new list of macro directories in this manager.
        Warning: as a consequence all the macro modules will be reloaded.
        This means that if any reference to an old macro object was kept it will
        refer to an old module (which could possibly generate problems of type
        class A != class A)."""
        p = []
        for item in macro_path:
            p.extend(item.split(":"))

        # filter empty and commented paths
        p = [ i for i in p if i and not i.startswith("#") ]

        # add basic macro directories
        for macro_dir in self.DEFAULT_MACRO_DIRECTORIES:
            if not macro_dir in p:
                p.append(macro_dir)

        self._macro_path = p

        macro_file_names = self._findMacroLibNames()
        for mod_name in macro_file_names:
            try:
                self.reloadMacroLib(mod_name)
            except:
                pass

    def getMacroPath(self):
        return self._macro_path

    def _findMacroLibName(self, lib_name, path=None):
        path = path or self.getMacroPath()
        f_name = lib_name
        if not f_name.endswith('.py'):
            f_name += '.py'
        for p in path:
            try:
                elems = os.listdir(p)
                if f_name in elems:
                    return os.path.abspath(os.path.join(p, f_name))
            except:
                self.debug("'%s' is not a valid path" % p)
        return None

    def _findMacroLibNames(self, path=None):
        path = path or self.getMacroPath()
        ret = {}
        for p in reversed(path):
            try:
                for f in os.listdir(p):
                    name,ext = os.path.splitext(f)
                    if name.startswith("_"):
                        continue
                    if ext.endswith('py'):
                        ret[name] = os.path.abspath(os.path.join(p, f))
            except:
                self.debug("'%s' is not a valid path" % p)
        return ret

    def _fromNameToFileName(self, lib_name, path=None):
        path = path or self.getMacroPath()[0]
        f_name = lib_name
        if not f_name.endswith('.py'):
            f_name += '.py'

        if os.path.isabs(f_name):
            path, _ = os.path.split(f_name)
            if not path in self.getMacroPath():
                raise Exception("'%s' is not part of the MacroPath" % path)
        else:
            f_name = os.path.join(path, f_name)
        return f_name

    def getOrCreateMacroLib(self, lib_name, macro_name=None):
        """Gets the exiting macro lib or creates a new macro lib file. If
        name is not None, a macro template code for the given macro name is
        appended to the end of the file.

        :param lib_name:
            module name, python file name, or full file name (with path)
        :type lib_name: str
        :param macro_name:
            an optional macro name. If given a macro template code is appended
            to the end of the file (default is None meaning no macro code is
            added)
        :type macro_name: str

        :return:
            a sequence with three items: full_filename, code, line number is 0
            if no macro is created or n representing the first line of code for
            the given macro name.
        :rtype: seq<str, str, int>"""
        # if only given the module name
        try:
            macro_lib = self.getMacroLib(lib_name)
        except UnknownMacroLibrary:
            macro_lib = None

        if macro_name is None:
            line_nb = 0
            if macro_lib is None:
                f_name, code = self.createMacroLib(lib_name), ''
            else:
                f_name = macro_lib.file_path
                f = file(f_name)
                code = f.read()
                f.close()
        else:
        # if given macro name
            if macro_lib is None:
                f_name, code, line_nb = self.createMacro(lib_name, macro_name)
            else:
                macro = macro_lib.get_macro(macro_name)
                if macro is None:
                    f_name, code, line_nb = self.createMacro(lib_name, macro_name)
                else:
                    _, line_nb = macro.code
                    f_name = macro.file_path
                    f = file(f_name)
                    code = f.read()
                    f.close()

        return [ f_name, code, line_nb ]

    def setMacroLib(self, lib_name, code, auto_reload=True):
        f_name = self._fromNameToFileName(lib_name)
        f = open(f_name, 'w')
        f.write(code)
        f.flush()
        f.close()
        _, name = os.path.split(f_name)
        mod, _ = os.path.splitext(name)
        if auto_reload:
            self.reloadMacroLib(mod)
        return mod

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
            template += 'from sardana.macroserver.macro import Macro, macro, Type\n\n'
            line_nb = 4
        else:
            template += '\n'
            t = open(f_name, 'rU')
            line_nb = -1
            for line_nb, _ in enumerate(t): pass
            line_nb += 3
            t.close()

        f = open(f_name, 'a+')
        f_templ = None
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
            template += MACRO_TEMPLATE
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

    def reloadMacro(self, macro_name, path=None):
        """Reloads the module corresponding to the given macro name

        :raises: MacroServerExceptionList in case the macro is unknown or the
        reload process is not successful

        :param macro_name: macro name
        :param path: a list of absolute path to search for libraries
                     (optional, default=None, means the current MacroPath
                     will be used)"""
        self.reloadMacros([macro_name], path=path)

    def reloadMacros(self, macro_names, path=None):
        """Reloads the modules corresponding to the given macro names

        :raises: MacroServerExceptionList in case the macro(s) are unknown or the
        reload process is not successful

        :param macro_names: a list of macro names
        :param path: a list of absolute path to search for libraries (optional,
                     default=None, means the current MacroPath will be used)"""
        module_names = []
        for macro_name in macro_names:
            module_name = self.getMacro(macro_name).module_name
            module_names.append(module_name)
        self.reloadMacroLibs(module_names, path=path)

    def reloadMacroLibs(self, module_names, path=None):
        """Reloads the given lib(=module) names

        :raises: MacroServerExceptionList in case the reload process is not
        successful for at least one library

        :param module_names: a list of module names
        :param path: a list of absolute path to search for libraries
                     (optional, default=None, means the current MacroPath
                     will be used)"""
        ret = []
        for module_name in module_names:
            m = self.reloadMacroLib(module_name, path=path)
            if m: ret.append(m)
        return ret

    def reloadLib(self, module_name, path=None):
        """Reloads the given library(=module) names.

        :raises:
            ImportError in case the reload process is not successful
            LibraryError if trying to reload a macro library
            
        :param module_name: module name
        :param path:
            a list of absolute path to search for libraries [default: None,
            meaning search in MacroPath. If not found, search for a built-in,
            frozen or special module and continue search in sys.path. ]
        :return: the reloaded python module object"""
        
        if module_name in self._modules:
            raise LibraryError("Cannot use simple reload to reload a Macro Library")
        
        mod_manager = ModuleManager()
        retry = path is None
        try:
            if retry:
                path = self.getMacroPath()
                if path:
                    path = copy.copy(path)
                    path.reverse()                
            return mod_manager.reloadModule(module_name, path)
        except ImportError:
            if retry:
                return mod_manager.reloadModule(module_name, path=None)
            else:
                raise

    def reloadMacroLib(self, module_name, path=None):
        """Reloads the given library(=module) names.

        :raises:
            LibraryError in case the reload process is not successful

        :param module_name: macro library name (=python module name)
        :param path:
            a list of absolute path to search for libraries [default: None,
            means the current MacroPath will be used]
        :return: the MacroLibrary object for the reloaded macro library"""
        path = path or self.getMacroPath()
        # reverse the path order:
        # more priority elements last. This way if there are repeated elements
        # they first ones (lower priority) will be overwritten by the last ones
        if path:
            path = copy.copy(path)
            path.reverse()

        # if there was previous Macro Library info remove it
        old_macro_lib = self._modules.pop(module_name, None)
        if old_macro_lib is not None:
            for macro in old_macro_lib.get_macros():
                self._macro_dict.pop(macro.name)

        mod_manager = ModuleManager()
        m, exc_info = None, None
        try:
            m = mod_manager.reloadModule(module_name, path)
        except:
            exc_info=sys.exc_info()
        macro_lib = None

        params = dict(module=m, name=module_name,
                      macro_server=self.macro_server, exc_info=exc_info)
        if m is None:
            file_name = self._findMacroLibName(module_name)
            if file_name is None:
                if exc_info:
                    msg = format_exception_only_str(*exc_info[:2])
                else:
                    msg = "Error (re)loading macro library '%s'" % module_name
                raise LibraryError(msg, exc_info=exc_info)
            params['file_path'] = file_name
            macro_lib = MacroLibrary(**params)
        else:
            macro_lib = MacroLibrary(**params)
            abs_file = macro_lib.file_path
            _is_macro = functools.partial(is_macro, abs_file=abs_file,
                                          logger=self)
            for _, macro in inspect.getmembers(m, _is_macro):
                try:
                    self.addMacro(macro_lib, macro)
                except:
                    self.error("Error adding macro %s", macro.__name__)
                    self.debug("Details:", exc_info=1)
        self._modules[module_name] = macro_lib
        return macro_lib

    def addMacro(self, macro_lib, macro):
        add = self.addMacroFunction
        if inspect.isclass(macro):
            add = self.addMacroClass
        return add(macro_lib, macro)

    def addMacroClass(self, macro_lib, klass):
        macro_name = klass.__name__
        action = (macro_lib.has_macro(macro_name) and "Updating") or "Adding"
        self.debug("%s macro class %s" % (action, macro_name))

        params = dict(macro_server=self.macro_server, lib=macro_lib,
                      klass=klass)
        macro_class = MacroClass(**params)
        macro_lib.add_macro_class(macro_class)
        self._macro_dict[macro_name] = macro_class

    def addMacroFunction(self, macro_lib, func):
        macro_name = func.func_name
        action = (macro_lib.has_macro(macro_name) and "Updating") or "Adding"
        self.debug("%s macro function %s" % (action, macro_name))

        params = dict(macro_server=self.macro_server, lib=macro_lib,
                      function=func)
        macro_function = MacroFunction(**params)
        macro_lib.add_macro_function(macro_function)
        self._macro_dict[macro_name] = macro_function

    def getMacroLibNames(self):
        return sorted(self._modules.keys())

    def getMacroLibs(self, filter=None):
        if filter is None:
            return self._modules
        expr = re.compile(filter, re.IGNORECASE)
        ret = {}
        for name, macro_lib in self._modules.iteritems():
            if expr.match(name) is None:
                continue
            ret[name] = macro_lib
        return ret

    def getMacros(self, filter=None):
        """Returns a :obj:`dict` containing information about macros.

        :param filter:
            a regular expression for macro names [default: None, meaning all
            macros]
        :type filter: str
        :return: a :obj:`dict` containing information about macros
        :rtype:
            :obj:`dict`\<:obj:`str`\, :class:`~sardana.macroserver.msmetamacro.MacroCode`\>"""
        if filter is None:
            return self._macro_dict
        expr = re.compile(filter, re.IGNORECASE)

        ret = {}
        for name, macro in self._macro_dict.iteritems():
            if expr.match(name) is None:
                continue
            ret[name] = macro
        return ret
    
    def getMacroClasses(self, filter=None):
        """Returns a :obj:`dict` containing information about macro classes.

        :param filter:
            a regular expression for macro names [default: None, meaning all
            macros]
        :type filter: str
        :return: a :obj:`dict` containing information about macro classes
        :rtype:
            :obj:`dict`\<:obj:`str`\, :class:`~sardana.macroserver.msmetamacro.MacroClass`\>"""
        macros = self.getMacros(filter=filter)
        macro_classes = {}
        for name, macro in macros.items():
            if macro.get_type() == ElementType.MacroClass:
                macro_classes[name] = macro
        return macro_classes

    def getMacroFunctions(self, filter=None):
        """Returns a :obj:`dict` containing information about macro functions.

        :param filter:
            a regular expression for macro names [default: None, meaning all
            macros]
        :type filter: str
        :return: a :obj:`dict` containing information about macro functions
        :rtype:
            :obj:`dict`\<:obj:`str`\, :class:`~sardana.macroserver.msmetamacro.MacroFunction`\>"""
        macros = self.getMacros(filter=filter)
        macro_classes = {}
        for name, macro in macros.items():
            if macro.get_type() == ElementType.MacroFunction:
                macro_classes[name] = macro
        return macro_classes
        
    def getMacroNames(self):
        return sorted(self._macro_dict.keys())

    def getMacro(self, macro_name):
        ret = self._macro_dict.get(macro_name)
        if ret is None:
            raise UnknownMacro("Unknown macro %s" % macro_name)
        return ret

    def getMacroClass(self, macro_name):
        return self.getMacro(macro_name)

    def getMacroFunction(self, macro_name):
        return self.getMacro(macro_name)

    def removeMacro(self, macro_name):
        self._macro_dict.pop(macro_name)

    def getMacroLib(self, name):
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
        ret = self._modules.get(module_name)
        if ret is None:
            raise UnknownMacroLibrary("Unknown macro library %s" % module_name)
        return ret

    def getMacroCode(self, macro_name):
        return self.getMacro(macro_name).code_object

    def getMacroClassCode(self, macro_name):
        return self.getMacroClass(macro_name).klass

    def getMacroFunctionCode(self, macro_name):
        return self.getMacroFunction(macro_name).function

    def getMacroInfo(self, macro_names, format='json'):
        if isinstance(macro_names, (str, unicode)):
            macro_names = [macro_names]
        ret = []
        json_codec = CodecFactory().getCodec(format)
        for macro_name in macro_names:
            macro_meta = self.getMacro(macro_name)
            ret.append(json_codec.encode(('', macro_meta.serialize()))[1])
        return ret

    def decodeMacroParameters(self, door, in_par_list):
        if len(in_par_list) == 0:
            raise RuntimeError('Macro name not specified')
        macro_name = in_par_list[0]
        macro_meta = self.getMacro(macro_name)
        out_par_list = ParamDecoder(door, macro_meta, in_par_list)
        return macro_meta, in_par_list, out_par_list

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
            if not environment.has_env(env):
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

    def createMacroObjFromMeta(self, meta, par_list, init_opts={}):
        code = meta.code_object
        macro_env = code.env or ()

        environment = init_opts.get('environment')

        r = []
        for env in macro_env:
            if not environment.has_env(env):
                r.append(env)
        if r:
            macro_name = meta.name
            raise MissingEnv("The macro %s requires the following missing " \
                             "environment to be defined: %s"
                             % (macro_name, str(r)))

        macro_opts = dict(no_exec=True, create_thread=True,
                          external_prepare=True)

        macro_opts.update(init_opts)
        if meta.get_type() == ElementType.MacroClass:
            macroObj = meta.macro_class(*par_list, **macro_opts)
        else:
            macro_opts['function'] = code
            macroObj = MacroFunc(*par_list, **macro_opts)
        return macroObj

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
        self._macro_counter = 0

        # dict<PoolElement, set<Macro>>
        # key PoolElement - reserved object
        # value set<Macro> macros that reserved the object
        self._reserved_objs = {}

        # dict<Macro, seq<PoolElement>>
        # key Macro - macro object
        # value - sequence of reserverd objects by the macro
        self._reserved_macro_objs = {}

        # reset the stacks
#        self._macro_stack = None
#        self._xml_stack = None
        self._macro_stack = []
        self._xml_stack = []
        self._macro_pointer = None
        self._aborted = False
        self._stopped = False
        self._paused = False
        self._last_macro_status = None

        name = "%s.%s" % (str(door), self.__class__.__name__)
        self._macro_status_codec = CodecFactory().getCodec('json')
        self.call__init__(Logger, name)

    def getDoor(self):
        return self._door

    door = property(getDoor)

    def getMacroServer(self):
        return self.door.macro_server

    macro_server = property(getMacroServer)

    @property
    def macro_manager(self):
        return self.macro_server.macro_manager

    def getNewMacroID(self):
        self._macro_counter -= 1
        return self._macro_counter

    def _preprocessParameters(self, par_str_list):
        if not par_str_list[0].lstrip().startswith('<'):
            xml_root = xml_seq = etree.Element('sequence')
            xml_macro = etree.SubElement(xml_seq, 'macro', name=par_str_list[0])
            for p in par_str_list[1:]:
                etree.SubElement(xml_macro, 'param', value=p)
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
            self.macro_manager.getMacro(name)

    def __fillXMLSequence(self, macros):
        for macro in macros:
            eid = macro.get('id')
            if eid is None:
                eid = str(self.getNewMacroID())
                macro.set('id', eid)
            name = macro.get('name')
            params = []
            
            # SEEMS THERE IS A MEMORY LEAK IN lxml.etree Element.xpath :
            # https://bugs.launchpad.net/lxml/+bug/397933
            # https://mailman-mail5.webfaction.com/pipermail/lxml/2011-October/006205.html
            # We work around it using findall:
            
            #for p in macro.xpath('param|paramrepeat'):
            #    if p.tag == 'param':
            #        params.append(p.get('value'))
            #    else:
            #        params.extend([ p2.get('value') for p2 in p.findall(".//param")])
            for p in macro.findall('*'):
                if p.tag == 'param':
                    params.append(p.get('value'))
                elif p.tag == 'paramrepeat':
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
        if is_non_str_seq(result):
            result = map(str, result)
        else:
            result = (str(result),)
        return result

    def _decodeXMLMacroParameters(self, xml_macro):
        str_params = [xml_macro.get('name')]
        for param in xml_macro.findall('.//param'):
            str_params.append(param.get('value'))
        return self._decodeMacroParameters(str_params)

    def _decodeMacroParameters(self, params):
        return self.macro_manager.decodeMacroParameters(self.door, params)

    def _prepareXMLMacro(self, xml_macro, parent_macro=None):
        macro_meta, _, params = self._decodeXMLMacroParameters(xml_macro)
        init_opts = {
            'id'           : xml_macro.get('id'),
            'macro_line'   : xml_macro.get('macro_line'),
            'parent_macro' : parent_macro,
        }

        macro_obj = self._createMacroObj(macro_meta, params, init_opts)
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

    def _createMacroObj(self, macro_name_or_meta, pars, init_opts={}):
        macro_meta = macro_name_or_meta
        if isinstance(macro_meta, (str, unicode)):
            macro_meta = self.macro_manager.getMacro(macro_meta)

        macro_opts = {
            'executor'    : self,
            'environment' : self.macro_server
        }
        macro_opts.update(init_opts)
        if not macro_opts.has_key('id'):
            macro_opts['id'] = str(self.getNewMacroID())

        macroObj = self.macro_manager.createMacroObjFromMeta(macro_meta, pars,
                                                             init_opts=macro_opts)

        return macroObj

    def _prepareMacroObj(self, macro_obj, pars, prepare_opts={}):
        return self.macro_manager.prepareMacroObj(macro_obj, pars,
                                                  prepare_opts=prepare_opts)

    def prepareMacroObj(self, macro_name_or_meta, pars, init_opts={},
                        prepare_opts={}):
        """Prepare a new macro for execution

        :param macro_name_or_meta name: name of the macro to be prepared or
                                        the macro meta itself
        :param pars: list of parameter objects
        :param init_opts: keyword parameters for the macro constructor
        :param prepare_opts: keyword parameters for the macro prepare

        :return: a tuple of two elements: macro object, the result of preparing the macro"""
        macroObj = self._createMacroObj(macro_name_or_meta, pars, init_opts=init_opts)
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
            if is_pure_str(par0):
                pars = par0.split(' ')
            elif is_non_str_seq(par0):
                pars = par0
        pars = map(str, pars)

        macro_klass, str_pars, pars = self._decodeMacroParameters(pars)

        init_opts['macro_line'] = "%s(%s) -> [%s]" % (str_pars[0], ", ".join(str_pars[1:]), id)
        if not init_opts.has_key('id'):
            init_opts['id'] = str(self.getNewMacroID())
        return self.prepareMacroObj(macro_klass, pars, init_opts, prepare_opts)

    def getRunningMacro(self):
        return self._macro_pointer

    def __stopObjects(self):
        """Stops all the reserved objects in the executor"""
        for _, objs in self._reserved_macro_objs.items():
            for obj in objs:
                try:
                    obj.stop()
                except AttributeError:
                    pass
                except:
                    self.warning("Unable to stop %s" % obj)
                    self.debug("Details:", exc_info=1)

    def __abortObjects(self):
        """Aborts all the reserved objects in the executor"""
        for _, objs in self._reserved_macro_objs.items():
            for obj in objs:
                try:
                    obj.abort()
                except AttributeError:
                    pass
                except:
                    self.warning("Unable to abort %s" % obj)
                    self.debug("Details:", exc_info=1)

    def abort(self):
        self.macro_server.add_job(self._abort, None)

    def stop(self):
        self.macro_server.add_job(self._stop, None)

    def _abort(self):
        m = self.getRunningMacro()
        if m is not None:
            self._aborted = True
            m.abort()
        self.__abortObjects()

    def _stop(self):
        m = self.getRunningMacro()
        if m is not None:
            self._stopped = True
            m.stop()
            if m.isPaused():
                m.resume(cb=self._macroResumed)
        self.__stopObjects()

    def pause(self):
        self._paused = True
        m = self.getRunningMacro()
        if m is not None:
            m.pause(cb=self._macroPaused)

    def _macroPaused(self, m):
        """Calback that is executed when the macro has efectively paused"""
        self.sendMacroStatusPause()
        self.sendState(Macro.Pause)

    def resume(self):
        if not self._paused:
            return
        self._paused = False
        m = self.getRunningMacro()
        if m is not None:
            m.resume(cb=self._macroResumed)

    def _macroResumed(self, m):
        """Callback that is executed when the macro has effectively resumed
        execution after being paused"""
        self.sendMacroStatusResume()
        self.sendState(Macro.Running)

    def run(self, params, asynch=True):
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
        # value - sequence of reserved objects by the macro
        self._reserved_macro_objs = {}

        # reset the stacks
        self._macro_stack = []
        self._xml_stack = []
        self._macro_pointer = None
        self._aborted = False
        self._stopped = False
        self._paused = False
        self._last_macro_status = None

        # convert given parameters into an xml
        self._xml = self._preprocessParameters(params)

        if asynch:
            # start the job of actually running the macro
            self.macro_server.add_job(self.__runXML, self._jobEnded)
            #return the proper xml
            return self._xml
        else:
            self.__runXML()
            #return self._macro_pointer.getResult()

    def _jobEnded(self, *args, **kw):
        self.debug("Job ended (stopped=%s, aborted=%s)",
                   self._stopped, self._aborted)

    def __runXML(self):
        self.sendState(Macro.Running)
        try:
            self.__runStatelessXML()
            self.sendState(Macro.Finished)
        except AbortException:
            self.sendState(Macro.Abort)
        except Exception:
            self.sendState(Macro.Abort)
        finally:
            self._macro_stack = None
            self._xml_stack = None

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
            macro_obj, _ = self._prepareXMLMacro(xml)
        except AbortException as ae:
            raise ae
        except Exception as e:
            door = self.door
            door.error("Error: %s", str(e))
            door.debug("Error details:", exc_info=1)
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
        door = self.door
        if self._aborted:
            self.sendMacroStatusAbort()
            raise AbortException("aborted between macros (before %s)" % name)
        elif self._stopped:
            self.sendMacroStatusStop()
            raise StopException("stopped between macros (before %s)" % name)
        macro_exp, tb, result = None, None, None
        try:
            self.debug("[START] runMacro %s" % desc)
            self._macro_pointer = macro_obj
            self._macro_stack.append(macro_obj)
            for step in macro_obj.exec_():
                self.sendMacroStatus((step,))

            if macro_obj.hasResult() and macro_obj.getParentMacro() is None:
                result = self.__preprocessResult(macro_obj.getResult())
                door.debug("sending result %s", result)
                self.sendResult(result)
        except AbortException as ae:
            macro_exp = ae
        except StopException as se:
            macro_exp = se
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
        if self._stopped:
            macro_obj._stopOnError()
            self.sendMacroStatusStop()
        elif self._aborted:
            macro_obj._abortOnError()
            self.sendMacroStatusAbort()

        # From this point on don't call any method of macro_obj which is part
        # of the mAPI (methods decorated with @mAPI) to avoid throwing an
        # AbortException if an Abort has been performed.
        if macro_exp is not None:
            if not self._stopped and not self._aborted:
                self.sendMacroStatusException(exc_info)
            self.debug("[ENDEX] (%s) runMacro %s" % (macro_exp.__class__.__name__, name))
            if isinstance(macro_exp, MacroServerException) and macro_obj.parent_macro is None:
                door.debug(macro_exp.traceback)
                door.error("An error occurred while running %s:\n%s" % (macro_obj.description, macro_exp.msg))
            self._popMacro()
            raise macro_exp
        self.debug("[ END ] runMacro %s" % desc)
        self._popMacro()
        return result

    def _popMacro(self):
        self._macro_stack.pop()
        length = len(self._macro_stack)
        if length > 0:
            self._macro_pointer = self._macro_stack[-1]
        #disable macro data for now. Comment following lines to enable it again
        else:
            self._macro_pointer = None

    def sendState(self, state):
        return self.door.set_state(state)

    def sendStatus(self, status):
        return self.door.set_status(status)

    def sendResult(self, result):
        return self.door.set_result(result)

    def getLastMacroStatus(self):
        return self._macro_pointer._getMacroStatus()

    def sendMacroStatusFinish(self):
        ms = self.getLastMacroStatus()
        if ms is not None:
            ms['state'] = 'finish'

            self.debug("Sending finish event")
            self.sendMacroStatus((ms,))

    def sendMacroStatusStop(self):
        ms = self.getLastMacroStatus()
        if ms is not None:
            ms['state'] = 'stop'

            self.debug("Sending stop event")
            self.sendMacroStatus((ms,))

    def sendMacroStatusAbort(self):
        ms = self.getLastMacroStatus()
        if ms is not None:
            ms['state'] = 'abort'

            self.debug("Sending abort event")
            self.sendMacroStatus((ms,))

    def sendMacroStatusException(self, exc_info):
        ms = self.getLastMacroStatus()
        if ms is not None:
            ms['state'] = 'exception'
            ms['exc_type'] = str(exc_info[0])
            ms['exc_value'] = str(exc_info[1])
            ms['exc_stack'] = traceback.format_exception(*exc_info)
            self.debug("Sending exception event")
            self.sendMacroStatus((ms,))

    def sendMacroStatusPause(self):
        ms = self.getLastMacroStatus()
        if ms is not None and len(ms) > 0:
            ms['state'] = 'pause'
            self.debug("Sending pause event")
            self.sendMacroStatus((ms,))

    def sendMacroStatusResume(self):
        ms = self.getLastMacroStatus()
        if ms is not None and len(ms) > 0:
            ms['state'] = 'resume'
            self.debug("Sending resume event")
            self.sendMacroStatus((ms,))

    def sendMacroStatus(self, data):
        self._last_macro_status = data
        #data = self._macro_status_codec.encode(('', data))
        return self.door.set_macro_status(data)

    def sendRecordData(self, data, codec=None):
        return self.door.set_record_data(data, codec=codec)

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

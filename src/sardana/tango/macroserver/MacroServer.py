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

"""The MacroServer tango module"""

import os.path

from PyTango import Util, Except, DevVoid, DevLong, DevString, DevState, \
    DevEncoded, DevVarStringArray, READ, READ_WRITE, SCALAR, SPECTRUM, DebugIt

#from taurus.core.util import Logger
from taurus.core.util.codecs import CodecFactory

from sardana import State, SardanaServer #, ElementType
from sardana.tango.core.SardanaDevice import SardanaDevice, SardanaDeviceClass
from sardana.macroserver.msexception import MacroServerException
from sardana.macroserver.macroserver import MacroServer as MS


class MacroServer(SardanaDevice):
    """The MacroServer tango class"""
    
    ElementsCache = None
    EnvironmentCache = None
    
    def __init__(self,cl, name):
        self._macro_server = None
        SardanaDevice.__init__(self,cl, name)
    
    def init(self, name):
        SardanaDevice.init(self, name)
        
        if self._alias is None:
            self._alias = Util.instance().get_ds_inst_name()
        
        self._macro_server = ms = MS(self.get_full_name(), self.alias)
        ms.add_listener(self.on_macro_server_changed)
    
    @property
    def macro_server(self):
        return self._macro_server
    
    def delete_device(self):
        SardanaDevice.delete_device(self)
        self.clear_log_report()

    def init_device(self):
        SardanaDevice.init_device(self)
        self.set_change_event('State', True, False)
        self.set_change_event('Status', True, False)
        self.set_change_event('TypeList', True, False)
        self.set_change_event('DoorList', True, False)
        self.set_change_event('MacroList', True, False)
        self.set_change_event('MacroLibList', True, False)
        self.set_change_event('Elements', True, False)
        self.set_change_event('Environment', True, False)
        
        dev_class = self.get_device_class()
        self.get_device_properties(dev_class)
        
        self.EnvironmentDb = self._calculate_name(self.EnvironmentDb)
        self.LogReportFilename = self._calculate_name(self.LogReportFilename)

        macro_server = self.macro_server
        macro_server.set_python_path(self.PythonPath)
        macro_server.set_max_parallel_macros(self.MaxParallelMacros)
        
        # if it is not possible to store/retrieve the environment from the 
        # current path then setup a new unique path and store the environment 
        # there forever
        try:
            macro_server.set_environment_db(self.EnvironmentDb)
        except:
            self.error("Failed to set environment DB to %s", self.EnvironmentDb)
            self.debug("Details:", exc_info=1)
            import tempfile
            env_db = os.path.join(tempfile.mkdtemp(),
                                  MacroServerClass.DefaultEnvRelDir)
            env_db = self._calculate_name(env_db)
            db = Util.instance().get_database()
            db.put_device_property(self.get_name(), dict(EnvironmentDb=env_db))
            self.EnvironmentDb = env_db
            macro_server.set_environment_db(self.EnvironmentDb)
        
        try:
            macro_server.set_log_report(self.LogReportFilename, self.LogReportFormat)
        except:
            self.error("Failed to setup log report to %s",
                       self.LogReportFilename)
            self.debug("Details:", exc_info=1)
        
        macro_server.set_macro_path(self.MacroPath)
        macro_server.set_pool_names(self.PoolNames)
        
        if self.RConsolePort:
            try:
                import rfoo.utils.rconsole
                rfoo.utils.rconsole.spawn_server(port=self.RConsolePort)
            except Exception:
                self.warning("Failed to start rconsole")
                self.debug("Details:", exc_info=1)
        self.set_state(DevState.ON)
    
    def _calculate_name(self, name):
        if name is None:
            return None
        util = Util.instance()
        return name % { 'ds_name' : util.get_ds_name().lower(),
                        'ds_exec_name' : util.get_ds_exec_name(),
                        'ds_inst_name' : util.get_ds_inst_name().lower() }
    
    def on_macro_server_changed(self, evt_src, evt_type, evt_value):
        # during server startup and shutdown avoid processing element
        # creation events
        if SardanaServer.server_state != State.Running:
            return
        
        evt_name = evt_type.name.lower()
        
        multi_attr = self.get_device_attr()
        elems_attr = multi_attr.get_attr_by_name("Elements")
        if evt_name == "poolelementschanged":
            # force the element list cache to be rebuild next time someone reads
            # the element list
            self.ElementsCache = None
            self.set_attribute(elems_attr, value=evt_value.value)
            #self.push_change_event('Elements', *evt_value.value)
        elif evt_name in ("elementcreated", "elementdeleted"):
            # force the element list cache to be rebuild next time someone reads
            # the element list
            self.ElementsCache = None

            elem = evt_value
            
            value = { }
            if "created" in evt_name:
                key = 'new'
            else:
                key = 'del'
            json_elem = elem.serialize(pool=self.pool.full_name)
            value[key] = json_elem,
            value = CodecFactory().getCodec('json').encode(('', value))
            self.set_attribute(elems_attr, value=value)
            #self.push_change_event('Elements', *value)
        elif evt_name == "elementschanged":
            # force the element list cache to be rebuild next time someone reads
            # the element list
            self.ElementsCache = None
            
            ms_name = self.macro_server.full_name
            new_values, changed_values, deleted_values = [], [], []
            for elem in evt_value['new']:
                json_elem = elem.serialize(macro_server=ms_name)
                new_values.append(json_elem)
            for elem in evt_value['change']:
                json_elem = elem.serialize(macro_server=ms_name)
                changed_values.append(json_elem)
            for elem in evt_value['del']:
                json_elem = elem.serialize(macro_server=ms_name)
                deleted_values.append(json_elem)
            value = { "new" : new_values, "change": changed_values,
                      "del" : deleted_values }
            value = CodecFactory().getCodec('json').encode(('', value))
            self.set_attribute(elems_attr, value=value)
            #self.push_change_event('Elements', *value)
        elif evt_name == "environmentchanged":
            self.EnvironmentCache = None
            env_attr = multi_attr.get_attr_by_name("Environment")
            value = CodecFactory().getCodec('pickle').encode(('', evt_value))
            self.set_attribute(env_attr, value=value)
            
    
    def always_executed_hook(self):
        pass
    
    def read_attr_hardware(self,data):
        pass
    
    def read_DoorList(self, attr):
        door_names = self.macro_server.get_door_names()
        attr.set_value(door_names)
        
    @DebugIt()
    def read_MacroList(self, attr):
        macro_names = self.macro_server.get_macro_names()
        attr.set_value(macro_names)
    
    def read_MacroLibList(self, attr):
        macro_lib_names = self.macro_server.get_macro_lib_names()
        attr.set_value(macro_lib_names)
    
    def read_TypeList(self, attr):
        type_names = self.macro_server.get_data_type_names_with_asterisc()
        attr.set_value(type_names)
        
    #@DebugIt()
    def getElements(self, cache=True):
        value = self.ElementsCache
        if cache and value is not None:
            return value
        elements = self.macro_server.get_elements_info()
        value = dict(new=elements)
        value = CodecFactory().getCodec('json').encode(('', value))
        self.ElementsCache = value
        return value
    
    #@DebugIt()
    def read_Elements(self, attr):
        fmt, data = self.getElements()
        attr.set_value(fmt, data)

    def is_Elements_allowed(self, req_type):
        return SardanaServer.server_state == State.Running

    is_DoorList_allowed = \
    is_MacroList_allowed = \
    is_MacroLibList_allowed = \
    is_TypeList_allowed = is_Elements_allowed
        
    def GetMacroInfo(self, macro_names):
        """GetMacroInfo(list<string> macro_names):
        
           Returns a list of string containing macro information.
           Each string is a JSON encoded.
           
           Params:
               - macro_name: a list of strings with the macro(s) name(s)
           Returns:
               - a list of string containing macro information.
        """
        macro_server = self.macro_server
        codec = CodecFactory().getCodec('json')
        ret = [ codec.encode(('', macro.serialize()))[1]
            for macro in macro_server.get_macros()
                if macro.name in macro_names ]
        return ret
    
    def ReloadMacro(self, macro_names):
        """ReloadMacro(list<string> macro_names):"""
        try:
            for macro_name in macro_names:
                self.macro_server.reload_macro(macro_name)
        except MacroServerException, mse:
            Except.throw_exception(mse.type, mse.msg, 'ReloadMacro')
        return ['OK']
    
    def ReloadMacroLib(self, lib_names):
        """ReloadMacroLib(sequence<string> lib_names):
        """
        try:
            for lib_name in lib_names:
                self.macro_server.reload_macro_lib(lib_name)
        except MacroServerException, mse:
            Except.throw_exception(mse.type, mse.msg, 'ReloadMacroLib')
        return ['OK']
    
    def GetMacroCode(self, argin):
        """GetMacroCode(<module name> [, <macro name>]) -> full filename, code, line_nb
        """
        ret = self.macro_server.get_or_create_macro_lib(*argin)
        return map(str, ret)
    
    def SetMacroCode(self, argin):
        lib_name, code = argin[:2]
        auto_reload = True
        if len(argin) > 2:
            auto_reload = argin[2].lower() in ('true', 'yes')
        self.macro_server.set_macro_lib(lib_name, code, auto_reload=auto_reload)

    #@DebugIt()
    def getEnvironment(self, cache=True):
        value = self.EnvironmentCache
        if cache and value is not None:
            return value
        env = self.macro_server.get_env()
        value = dict(new=env)
        value = CodecFactory().getCodec('pickle').encode(('', value))
        self.EnvironmentCache = value
        return value
    
    def read_Environment(self, attr):
        fmt, data = self.getEnvironment()
        attr.set_value(fmt, data)
    
    def write_Environment(self, attr):
        data = attr.get_write_value()
        data = CodecFactory().getCodec('pickle').decode(data)[1]
        self.macro_server.change_env(data)
    
    def is_Environment_allowed(self, req_type):
        return True


class MacroServerClass(SardanaDeviceClass):
    """MacroServer Tango class class"""
    
    #    Class Properties
    class_property_list = {
    }
    
    
    DefaultEnvBaseDir = "/tmp/tango"
    DefaultEnvRelDir = "%(ds_exec_name)s/%(ds_inst_name)s/macroserver.properties"
    
    DefaultLogReportFormat = '%(levelname)-8s %(asctime)s: %(message)s'
    
    #    Device Properties
    device_property_list = {
        'PoolNames':
            [DevVarStringArray,
            "Sardana device pool device names",
            [] ],
        'MacroPath':
            [DevVarStringArray,
            "list of directories to search for macros (path separators "
            "can be '\n' or ':')",
            [] ],
        'PythonPath':
            [DevVarStringArray,
            "list of directories to be appended to sys.path at startup (path "
            "separators can be '\n' or ':')",
            [] ],
        'MaxParallelMacros':
            [DevLong,
            "Maximum number of macros that can execute concurrently.",
            [10] ],
        'EnvironmentDb':
            [DevString,
            "The environment database (usually a plain file).",
            os.path.join(DefaultEnvBaseDir, DefaultEnvRelDir) ],
        'RConsolePort':
            [DevLong,
            "The rconsole port number",
            None ],
        'LogReportFilename':
            [DevString,
            "Filename (absolute) which contains user log reports [default: "
            "None, meaning don't store log report messages]. The system will "
            "save old log files by appending extensions to the filename. The "
            "extensions are date-and-time based, using the strftime "
            "format %Y-%m-%d_%H-%M-%S or a leading portion thereof, "
            "depending on the rollover interval.",
            None ],
        'LogReportFormat':
            [DevString,
            "Log report format [default: '%s']" % DefaultLogReportFormat,
            DefaultLogReportFormat],
    }

    #    Command definitions
    cmd_list = {
        'GetMacroInfo':
            [[DevVarStringArray, "Macro(s) name(s)"],
            [DevVarStringArray, "Macro(s) description(s)"]],
        'ReloadMacro':
            [[DevVarStringArray, "Macro(s) name(s)"],
            [DevVarStringArray, "[OK] if successfull or a traceback " \
                "if there was a error (one string with complete traceback of " \
                "each error)"]],
        'ReloadMacroLib':
            [[DevVarStringArray, "MacroLib(s) name(s)"],
            [DevVarStringArray, "[OK] if successfull or a traceback " \
                "if there was a error (one string with complete traceback of " \
                "each error)" ]],
        'GetMacroCode':
            [[DevVarStringArray, "<MacroLib name> [, <Macro name>]"],
            [DevVarStringArray, "result is a sequence of 3 strings:\n"
                "<full path and file name>, <code>, <line number>" ]],
        'SetMacroCode':
            [[DevVarStringArray, "<MacroLib name>, <code> [, <Auto reload>=True]\n" \
                "- if macro lib is a simple module name:\n" \
                "  - if it exists, it is overwritten, otherwise a new python " \
                "file is created in the directory of the first element in "\
                "the MacroPath property" \
                "- if macro lib is the full path name:\n" \
                "  - if path is not in the MacroPath, an exception is thrown" \
                "  - if file exists it is overwritten otherwise a new file " \
                "is created"],
            [DevVoid, "" ]],
    }

    #    Attribute definitions
    attr_list = {
        'DoorList'     : [ [ DevString,  SPECTRUM, READ, 256 ] ],
        'MacroList'    : [ [ DevString,  SPECTRUM, READ, 4096 ] ],
        'MacroLibList' : [ [ DevString,  SPECTRUM, READ, 1024 ] ],
        'TypeList'     : [ [ DevString,  SPECTRUM, READ, 256 ] ],
        'Elements'     : [ [ DevEncoded, SCALAR,   READ ],
                           { 'label'       : "Elements",
                             'description' : "the list of all elements "
                                             "(a JSON encoded dict)", } ],
        'Environment'  : [ [ DevEncoded, SCALAR, READ_WRITE],
                           { 'label'       : 'Environment',
                             'description' : "The macro server environment "
                                             "(a JSON encoded dict)", } ],
    }
    

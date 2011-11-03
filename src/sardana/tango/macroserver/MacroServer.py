#!/usr/bin/env python

import sys
import os
import copy
import threading
import logging.handlers

import PyTango
from PyTango import Util, DebugIt

from taurus.core.util import Logger, CodecFactory

from sardana.tango.core.SardanaDevice import SardanaDevice, SardanaDeviceClass
from sardana.tango.core.util import GenericSpectrumAttr
from sardana.macroserver.exception import MacroServerException
from sardana.macroserver.manager import MacroServerManager


class MacroServer(SardanaDevice):
    
    ElementsCache = None
    
    def __init__(self,cl, name):
        SardanaDevice.__init__(self,cl, name)
        MacroServer.init_device(self)

    def __getManager(self, *args):
        return MacroServerManager(*args)
    
    def delete_device(self):
        SardanaDevice.delete_device(self)
        self.__getManager().cleanUp()
        
    def init_device(self):
        SardanaDevice.init_device(self)
        self.set_state(PyTango.DevState.ON)
        self.set_change_event('State', True, False)
        self.set_change_event('Status', True, False)
        self.set_change_event('TypeList', True, False)
        self.set_change_event('DoorList', True, False)
        self.set_change_event('MacroList', True, False)
        self.set_change_event('MacroLibList', True, False)
        self.set_change_event('Elements', True, False)
        
        dev_class = self.get_device_class()
        self.get_device_properties(dev_class)
        
        self.EnvironmentDb = self._calculate_environment_name(self.EnvironmentDb)

        # Init MacroServer Manager
        # it is important that the MacroServerManager singleton be called
        # here for the first time. So don't call it in the main or 
        # MacroServerClass
        manager_params = self.PoolNames, self.MacroPath, self.EnvironmentDb, \
            self.MaxParallelMacros, self
        ms_manager = self.__getManager(*manager_params)
        ms_manager.reInit(*manager_params)
        
        # if default directories are not in the MacroPath property, write them
        # into the database
        mpath = set(self.MacroPath)
        default_mpath = set(ms_manager.DEFAULT_MACRO_DIRECTORIES)
        if mpath & default_mpath != default_mpath:
            db = Util.instance().get_database()
            db.put_device_property(self.get_name(),
                                   dict(MacroPath=ms_manager.getMacroPath()))
        
        dl = ms_manager.getDoorListObj()
        if not dl.isSubscribed(self.doorsChanged):
            dl.subscribeEvent(self.doorsChanged)
        
        if self.RConsolePort:
            try:
                import rfoo.utils.rconsole
                rfoo.utils.rconsole.spawn_server(port=self.RConsolePort)
            except:
                self.warning(exc_info=1)
    
    def _calculate_environment_name(self, name):
        u = PyTango.Util.instance()
        return name % { 'ds_name' : u.get_ds_name() }
    
    def always_executed_hook(self):
        pass
    
    def read_attr_hardware(self,data):
        pass
    
    def read_DoorList(self, attr):
        ms_manager = self.__getManager()
        door_list_obj = ms_manager.getDoorListObj()
        attr.set_value(door_list_obj.read())
        
    @DebugIt()
    def read_MacroList(self, attr):
        self.info_stream("inside read_MacroList")
        ms_manager = self.__getManager()
        macro_list_obj = ms_manager.getMacroListObj()
        attr.set_value(macro_list_obj.read())
    
    def read_MacroLibList(self, attr):
        ms_manager = self.__getManager()
        macro_lib_list_obj = ms_manager.getMacroLibListObj()
        attr.set_value(macro_lib_list_obj.read())
    
    def read_TypeList(self, attr):
        ms_manager = self.__getManager()
        type_list_obj = ms_manager.getTypeListObj()
        attr.set_value(type_list_obj.read())
        
    #@DebugIt()
    def getElements(self, cache=True):
        value = self.ElementsCache
        if cache and value is not None:
            return value
        elements = self.__getManager().get_elements_info()
        value = dict(new=elements)
        value = CodecFactory().getCodec('json').encode(('', value))
        self.ElementsCache = value
        return value
    
    #@DebugIt()
    def read_Elements(self, attr):
        element_list = self.getElements()
        attr.set_value(*element_list)
    
    def GetMacroInfo(self, argin):
        """GetMacroInfo(list<string> macro_names):
        
           Returns a list of string representing macro information.
           
           Params:
               - macro_name: a list of strings with the macro(s) name(s)
           Returns:
               - list[0]: macro description (documentation)
                 list[1]: macro hints, if any
                 list[2]: number of parameters = N
                 list[3...3+4*N]: parameter info: name, type, desc, default value
                 list[4+4*N]: number of results = M
                 list[5+4*N...5+4*N+4*M]: result info: name, type, desc, default value
        """        
        return self.__getManager().getMacroInfo(argin)
    
    def ReloadMacro(self, argin):
        """ReloadMacro(list<string> macro_names):"""
        try:
            self.__getManager().reloadMacros(argin)
        except MacroServerException, mse:
            PyTango.Except.throw_exception(mse.type, mse.msg, 'ReloadMacro')
        return ['OK']
    
    def ReloadMacroLib(self, argin):
        """ReloadMacroLib(sequence<string> lib_names):
        """
        try:
            self.__getManager().reloadMacroLibs(argin)
        except MacroServerException, mse:
            PyTango.Except.throw_exception(mse.type, mse.msg, 'ReloadMacroLib')
        return ['OK']
    
    def GetMacroCode(self, argin):
        """GetMacroCode(<module name> [, <macro name>]) -> full filename, code, line_nb
        """
        ret = self.__getManager().getOrCreateMacroLib(*argin)
        ret = map(str, ret)
        return ret
    
    def SetMacroCode(self, argin):
        self.__getManager().setMacroLib(*argin)
    
    def dyn_attr(self):
        ms_manager = self.__getManager()
        type_list_obj = ms_manager.getTypeListObj()
        type_list_obj.subscribeEvent(self.typesChanged)
        macro_list_obj = ms_manager.getMacroListObj()
        macro_list_obj.subscribeEvent(self.macrosChanged)
        macro_lib_list_obj = ms_manager.getMacroLibListObj()
        macro_lib_list_obj.subscribeEvent(self.macroLibsChanged)
    
    def typesChanged(self, data, type_data):
        all_types, old_types, new_types = type_data
        
        for type_name in old_types:
            if type_name[-1] == '*':
                self.removeTypeAttribute(type_name[:-1])

        #for type_name in new_types:
        #    if type_name[-1] == '*':
        #        self.addTypeAttribute(type_name[:-1])

        self.push_change_event('TypeList', all_types)
    
    def addTypeAttribute(self, name):
        self.trace("Adding dynamic attribute %s" % name)
        attr_name = "%sList" % name
        attr_data = (name, attr_name)
        attr = GenericSpectrumAttr(attr_name, PyTango.DevString, PyTango.READ)
        self.add_attribute(attr, MacroServer.read_GenericList)
        
        self.set_change_event(attr_name, True, False) 
        
        type_obj = self.__getManager().getTypeObj(name)
        type_obj.subscribeEvent(self.genericListChanged, attr_data)
    
    def removeTypeAttribute(self, name):
        pass
    
    def macrosChanged(self, data, macro_data):
        all_macros, removed, added = macro_data
        self.push_change_event('MacroList', all_macros)
    
    def macroLibsChanged(self, data, macro_lib_data):
        all_macro_libs = macro_lib_data[0]
        self.push_change_event('MacroLibList', all_macro_libs) 
    
    def genericListChanged(self, attr_data, data):
        pass
    
    def doorsChanged(self, attr_data, data):
        pass
    
    def read_GenericList(self, attr):
        attr_name = attr.get_name()
        type_name = attr_name[:attr_name.index('List')]
        type_obj = self.__getManager().getTypeObj(type_name)
        item_list = type_obj.read()
        attr.set_value(item_list)


class MacroServerClass(PyTango.DeviceClass, Logger):

    #    Class Properties
    class_property_list = {
        }

    #    Device Properties
    device_property_list = {
        'PoolNames':
            [PyTango.DevVarStringArray,
            "Sardana device pool device names",
            [] ],
        'MacroPath':
            [PyTango.DevVarStringArray,
            "List of directories (absolute or relative path) that contain macro files.",
            [] ],
        'MaxParallelMacros':
            [PyTango.DevLong,
            "Maximum number of macros that can execute concurrently.",
            [10] ],
        'EnvironmentDb':
            [PyTango.DevString,
            "The environment database (usualy a plain file).",
            ["/tmp/tango/%(ds_name)s/macroserver.properties"] ],
        'RConsolePort':
            [PyTango.DevLong,
            "The rconsole port number",
            None ],
        }

    #    Command definitions
    cmd_list = {
        'GetMacroInfo':
            [[PyTango.DevVarStringArray, "Macro(s) name(s)"],
            [PyTango.DevVarStringArray, "Macro(s) description(s)"]],
        'ReloadMacro':
            [[PyTango.DevVarStringArray, "Macro(s) name(s)"],
            [PyTango.DevVarStringArray, "[OK] if successfull or a traceback " \
                "if there was a error (one string with complete traceback of " \
                "each error)"]],
        'ReloadMacroLib':
            [[PyTango.DevVarStringArray, "MacroLib(s) name(s)"],
            [PyTango.DevVarStringArray, "[OK] if successfull or a traceback " \
                "if there was a error (one string with complete traceback of " \
                "each error)" ]],
        'GetMacroCode':
            [[PyTango.DevVarStringArray, "<MacroLib name> [, <Macro name>]"],
            [PyTango.DevVarStringArray, "result is a sequence of 3 strings:\n"
                "<full path and file name>, <code>, <line number>" ]],
        'SetMacroCode':
            [[PyTango.DevVarStringArray, "<MacroLib name>, <code>\n" \
                "- if macro lib is a simple module name:\n" \
                "  - if it exists, it is overwritten otherwise a new python " \
                "file is created in the directory of the first element in "\
                "the MacroPath property" \
                "- if macro lib is the full path name:\n" \
                "  - if path is not in the MacroPath, an exception is thrown" \
                "  - if file exists it is overwritten otherwise a new file " \
                "is created"],
            [PyTango.DevVoid, "" ]],
        }

    #    Attribute definitions
    attr_list = {
        'DoorList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 256]],
        'MacroList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 4096]],
        'MacroLibList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 1024]],
        'TypeList':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 256]],
        'Elements':
            [[PyTango.DevEncoded,
            PyTango.SCALAR,
            PyTango.READ],
            {
                'label':"Elements",
                'description':"the list of all elements (a JSON encoded dict)",
            } ],
        }
    
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        Logger.__init__(self, "%sClass" % name)
        
        self.set_type(name);

        
    def dyn_attr(self, dev_list):
        for dev in dev_list:
            dev.dyn_attr()

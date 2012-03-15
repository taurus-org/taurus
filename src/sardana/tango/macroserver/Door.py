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

import sys
import threading
import time
import copy
import json

from PyTango import Util, DevFailed, Except, DevVoid, DevShort, DevLong, \
    DevLong64, DevDouble, DevBoolean, DevString, DevState, DevEncoded, \
    DevVarStringArray, \
    DispLevel, AttrQuality, TimeVal, AttrData, ArgType, \
    READ, READ_WRITE, SCALAR, SPECTRUM

import taurus
import taurus.core.util
from taurus.core.util import etree, CodecFactory, DebugIt

from sardana import State, InvalidId, SardanaServer
from sardana.sardanaattribute import SardanaAttribute
from sardana.macroserver.msexception import MacroServerException
from sardana.macroserver.macro import Macro
from sardana.tango.core.attributehandler import AttributeLogHandler
from sardana.tango.core.SardanaDevice import SardanaDevice, SardanaDeviceClass

class DoorSimulation(taurus.core.util.Logger):
    
    def __init__(self, door):
        taurus.core.util.Logger.__init__(self, "Simulation", door)
        self._door = door
        self._currentDelay = None
        self._currentTimer = None
        self._startTime = None
        self._currentMacro = None

    def finishRun(self, *args):
        self._currentDelay = None
        self._currentTimer = None
        self._startTime = None
        self._currentMacro = None
        msg = "Macro %s just FINISHED" % args[0]
        self._door.info(msg)
        self._door.set_state(Macro.Finished)
        self._door.push_change_event('state')

    def runMacro(self, params):
        self._door.set_state(Macro.Init)
        self._door.push_change_event('state')
        #self._currentDelay = random.random() * 5 # random [0,5)
        self._currentDelay = 5
        self._currentTimer = threading.Timer(self._currentDelay, self.finishRun, params)
        self._currentMacro = params
        self._startTime = time.time()
        self._door.set_state(Macro.Running)
        self._door.push_change_event('state')
        msg = "Macro %s just STARTED" % params[0]
        self._door.info(msg)
        self._currentTimer.start()
    
    def pauseMacro(self):
        pauseTime = time.time()
        self._currentTimer.cancel()
        self._currentTimer = None
        elapsedTime = pauseTime - self._startTime
        self._currentDelay = self._currentDelay - elapsedTime
        self._door.set_state(Macro.Pause)
        self._door.push_change_event('state')
        msg = "Macro %s just PAUSED" % self._currentMacro[0]
        self._door.info(msg)
    
    def stopMacro(self):
        stopTime = time.time()
        self._currentTimer.cancel()
        self._currentTimer = None
        elapsedTime = stopTime - self._startTime
        self._currentDelay = self._currentDelay - elapsedTime
        self._door.set_state(Macro.Stop)
        self._door.push_change_event('state')
        msg = "Macro %s just STOPPED" % self._currentMacro[0]
        self._door.info(msg)
        
    def resumeMacro(self):
        self._door.set_state(Macro.Running)
        self._door.push_change_event('state')
        self._currentTimer = threading.Timer(self._currentDelay, self.finishRun, self._currentMacro)
        msg = "Macro %s just RESUMED" % self._currentMacro[0]
        self._door.info(msg)
        self._startTime = time.time()
        self._currentTimer.start()
    
    def abortMacro(self):
        if self._currentTimer:
            self._currentTimer.cancel()
        self._currentTimer = None
        self._currentDelay = None
        self._startTime = None
        msg = "Macro %s just ABORTED" % self._currentMacro[0]
        self._door.info(msg)
        self._currentMacro = None
        self._door.set_state(Macro.Abort)
        self._door.push_change_event('state')
        self._door.set_state(Macro.Ready)
        self._door.push_change_event('state')

    def __del__(self):
        if self._currentTimer:
            try:
                self._currentTimer.cancel()
            finally:
                del self._currentTimer


class Door(SardanaDevice):

    def __init__(self, dclass, name):
        SardanaDevice.__init__(self, dclass, name)
        self._last_result = ()
        Door.init_device(self)

    def init(self, name):
        SardanaDevice.init(self, name)
        self._simulation = None
        self._door = None
        self._macro_server_device = None
    
    def get_door(self):
        return self._door
    
    def set_door(self, door):
        self._door = door
    
    door = property(get_door, set_door)
    
    @property
    def macro_server_device(self):
        return self._macro_server_device
    
    @property
    def macro_server(self):
        return self.door.macro_server

    def delete_device(self):
        if self.getRunningMacro():
            self.debug("aborting running macro")
            self.macro_executor.abort()
        
        if self._simulation:
            del self._simulation
        
        for handler, filter, format in self._handler_dict.values():
            handler.finish()
    
    @DebugIt()
    def init_device(self):
        SardanaDevice.init_device(self)
        levels = 'Critical', 'Error', 'Warning', 'Info', 'Output', 'Debug'
        detect_evts = ()
        non_detect_evts = ['State', 'Status', 'Result', 'RecordData',
                           'MacroStatus', ] + list(levels)
        self.set_change_events(detect_evts, non_detect_evts)

        util = Util.instance()
        db = util.get_database()
        
        # Find the macro server for this door
        macro_servers = util.get_device_list_by_class("MacroServer")
        if self.MacroServerName is None:
            self._macro_server_device = macro_servers[0]
        else:
            ms_name = self.MacroServerName.lower()
            for ms in macro_servers:
                if ms.get_name().lower() == ms_name or \
                   ms.alias.lower() == ms_name:
                    self._macro_server_device = ms
                    break
        
        # support for old doors which didn't have ID
        if self.Id == InvalidId:
            self.Id = self.macro_server_device.macro_server.get_new_id()
            db.put_device_property(self.get_name(), dict(Id=self.Id))
        
        if self.door is None:
            full_name = self.get_name()
            name = full_name
            macro_server = self.macro_server_device.macro_server
            door = macro_server.create_element(type="Door", name=name,
                                               full_name=full_name, id=self.Id)
            door.add_listener(self.on_door_changed)
            self.door = door
            
        self._setupLogHandlers(levels)
    
    def _setupLogHandlers(self, levels):
        self._handler_dict = {}
        for level in levels:
            handler = AttributeLogHandler(self, level,
                                          max_buff_size=self.MaxMsgBufferSize)
            filter = taurus.core.util.LogFilter(level=getattr(self, level))
            handler.addFilter(filter)
            self.addLogHandler(handler)
            format = None
            self._handler_dict[level] = handler, filter, format
    
    def on_door_changed(self, event_source, event_type, event_value):
        # during server startup and shutdown avoid processing element
        # creation events
        if SardanaServer.server_state != State.Running:
            return
        
        timestamp = time.time()
        
        name = event_type.name.lower()
        
        multi_attr = self.get_device_attr()
        try:
            attr = multi_attr.get_attr_by_name(name)
        except DevFailed:
            return
        
        if name == "state":
            event_value = self.calculate_tango_state(event_value)
        elif name == "status":
            event_value = self.calculate_tango_status(event_value)
        else:
            if isinstance(event_value, SardanaAttribute):
                if event_value.error:
                    error = Except.to_dev_failed(*event_value.exc_info)
                timestamp = event_value.timestamp
                event_value = event_value.value
            
            if attr.get_data_type() == ArgType.DevEncoded:
                codec = CodecFactory().getCodec('json')
                event_value = codec.encode(('', event_value))
        self.set_attribute(attr, value=event_value, timestamp=timestamp)
    
    @property
    def macro_executor(self):
        return self.door.macro_executor
    
    def getRunningMacro(self):
        return self.door.running_macro
    
    def always_executed_hook(self):
        pass
    
    def read_attr_hardware(self,data):
        pass
    
    def read_SimulationMode(self, attr):
        if not hasattr(self, '_simulation'):
            self._simulation = None
        attr.set_value(not self._simulation is None)
    
    def write_SimulationMode(self, attr):
        data=[]
        attr.get_write_value(data)
        sim = data[0]
        self.debug('Setting simulation mode to %s' % str(sim))
        if sim:
            self._simulation = DoorSimulation(self)
        else:
            self._simulation = None
    
    def is_SimulationMode_allowed(self, req_type):
        return self.get_state() in (Macro.Ready, Macro.Abort)
    
    def readLogAttr(self, attr):
        name = attr.get_name()
        handler, filter, format = self._handler_dict[name]
        handler.read(attr)
    
    read_Critical = read_Error = read_Warning = read_Info = read_Output = \
        read_Debug = read_Trace = readLogAttr 
    
    #@DebugIt()
    def read_ElementList(self, attr):
        element_list = self.macro_server_device.getElementList()
        attr.set_value(*element_list)
    
    def sendRecordData(self, format, data):
        self.push_change_event('RecordData', format, data)
    
#    def sendState(self, state):
#        self.set_state(state)
#        self.push_change_event('state')
    
#    def sendStatus(self, status):
#        self.set_status(status)
#        self.push_change_event('status')
    
#    def sendMacroStatus(self, format, data):
#        self.push_change_event('MacroStatus', format, data)
##        attr = self.get_device_attr().get_attr_by_name('MacroStatus')
##        attr.set_value(format, data)
##        attr.fire_change_event()
    
#    def sendEnvironment(self, format, data):
#        self.push_change_event('Environment', format, data)
##        attr = self.get_device_attr().get_attr_by_name('Environment')
##        attr.set_value(format, data)
##        attr.fire_change_event()
    
#    def sendResult(self, result):
#        self._last_result = result
#        attr = self.get_device_attr().get_attr_by_name('Result')
#        attr.set_value(result)
##       attr.fire_change_event()
#        self.push_change_event('Result', result)

    def getLogAttr(self, name):
        return self._handler_dict.get(name)
    
    def read_Result(self, attr):
        #    Add your own code here
        attr.set_value(self._last_result)
    
    def read_RecordData(self, attr):
        attr.set_value('', '')
    
    def read_MacroStatus(self, attr):
        attr.set_value('', '')
    
    def Abort(self):
        self.debug("Abort is deprecated. Use StopMacro instead")
        return self.StopMacro()
    
    def AbortMacro(self):
        if self._simulation is None:
            self.debug("Aborting")
            self.macro_executor.abort()
            self.debug("Finished aborting")
        else:
            self._simulation.abortMacro()
            return
        
    def is_Abort_allowed(self):
        return True

    def PauseMacro(self):
        if self._simulation is None:
            macro = self.getRunningMacro()
            if macro is None:
                print "Unable to pause Null macro"
                return
            self.macro_executor.pause()
        else:
            self._simulation.pauseMacro()

    def is_PauseMacro_allowed(self):
        return self.get_state() == Macro.Running

    def StopMacro(self):
        if self._simulation is None:
            macro = self.getRunningMacro()
            if macro is None:
                return
            self.debug("stopping macro %s" % macro._getDescription())
            self.macro_executor.stop()
        else:
            self._simulation.stopMacro()
    
    def is_StopMacro_allowed(self):
        return self.get_state() == Macro.Running
    
    def ResumeMacro(self):
        if self._simulation is None:
            macro = self.getRunningMacro()
            if macro is None:
                return
            self.debug("resume macro %s" % macro._getDescription())
            self.macro_executor.resume()
        else:
            self._simulation.resumeMacro()
        
    def is_ResumeMacro_allowed(self):
        return self.get_state() == Macro.Pause
    
    def RunMacro(self, par_str_list):
        #first empty all the buffers
        for handler, filter, fmt in self._handler_dict.values():
            handler.clearBuffer()
        
        if not self._simulation is None:
            self._simulation.runMacro(par_str_list)
            return []
        if len(par_str_list) == 0:
            return []
        
        xml_seq = self.door.run_macro(par_str_list, asynch=True)
        return [etree.tostring(xml_seq, pretty_print=False)]

    def is_RunMacro_allowed(self):
        return self.get_state() in [Macro.Finished, Macro.Abort]

    def SimulateMacro(self, par_str_list):
        raise Exception("Not implemented yet")
    
    def GetMacroEnv(self, argin):
        macro_name = argin[0]
        if len(argin) > 1:
            macro_env = argin[1:]
        else:
            macro_env = self.door.get_macro_class_info(macro_name).env
        env = self.door.get_env(macro_env, macro_name=macro_name)
        ret = []
        for k,v in env.iteritems():
            ret.extend((k,v))
        return ret
    
    def is_GetMacroEnv_allowed(self):
        return self.get_state() in [Macro.Finished, Macro.Abort]


class DoorClass(SardanaDeviceClass):

    #    Class Properties
    class_property_list = {
        }

    #    Device Properties
    device_property_list = {
        'Id': [DevLong64, "Internal ID", [ InvalidId ] ],
        'MaxMsgBufferSize':
            [DevLong,
            'Maximum size for the Output, Result, Error, Warning, Debug and '
            'Info buffers',
            [512] ],
        'MacroServerName':
            [DevString,
            'Name of the macro server device to connect to. [default: None, '
            'meaning connect to the first registered macroserver',
            None ],
        }

    #    Command definitions
    cmd_list = {
        'Abort':
            [ [ DevVoid, ""],
              [ DevVoid, ""] ],
        'PauseMacro':
            [ [DevVoid, ""],
              [DevVoid, ""] ],
        'AbortMacro':
            [ [DevVoid, ""],
              [DevVoid, ""] ],
        'StopMacro':
            [ [DevVoid, ""],
              [DevVoid, ""] ],
        'ResumeMacro':
            [ [DevVoid, ""],
              [DevVoid, ""] ],
        'RunMacro':
            [ [DevVarStringArray, 'Macro name and parameters'],
              [DevVarStringArray, 'Macro Result']],
        'SimulateMacro':
            [ [DevVarStringArray, 'Macro name and parameters'],
              [DevVarStringArray, 'Macro statistics']],
        'GetMacroEnv':
            [ [ DevVarStringArray, 'Macro name followed by an ' \
                'optional list of environment names' ],
              [ DevVarStringArray, 'Macro environment as a list of '\
                'pairs keys, value'] ],
#        'ReloadMacro':
#            [[DevVarStringArray, "Macro(s) name(s)"],
#            [DevVarStringArray, "[OK] if successfull or a traceback " \
#                "if there was a error (one string with complete traceback of " \
#                "each error)"]],
#        'ReloadMacroLib':
#            [[DevVarStringArray, "MacroLib(s) name(s)"],
#            [DevVarStringArray, "[OK] if successfull or a traceback " \
#                "if there was a error (one string with complete traceback of " \
#                "each error)"]],
        }

    #    Attribute definitions
    attr_list = {
        'SimulationMode': [ [ DevBoolean, SCALAR, READ_WRITE] ,
                            { 'label'     : 'Simulation mode',
                              'Memorized' : 'true', } ],
        'Result'        : [ [ DevString, SPECTRUM, READ, 512],
                            { 'label'     : 'Result for the last macro', } ],
        'Critical'      : [ [ DevString, SPECTRUM, READ, 512],
                            { 'label'     : 'Macro critical error message', } ],
        'Error'         : [ [ DevString, SPECTRUM, READ, 512],
                            { 'label'     : 'Macro error message', } ],
        'Warning'       : [ [ DevString, SPECTRUM, READ, 512],
                            { 'label'     : 'Macro warning message', } ],
        'Info'          : [ [ DevString, SPECTRUM, READ, 512],
                            { 'label'     : 'Macro information message', } ],
        'Output'        : [ [ DevString, SPECTRUM, READ, 512],
                            { 'label'     : 'Macro output message', } ],
        'Debug'         : [ [ DevString, SPECTRUM, READ, 512],
                            { 'label'     : 'Macro debug message', } ],
        'RecordData'    : [ [ DevEncoded, SCALAR, READ],
                            { 'label'     : 'Record Data', } ],
        'MacroStatus'   : [ [ DevEncoded, SCALAR, READ],
                            { 'label'     : 'Macro Status', } ],
        'ElementList'   : [ [ DevEncoded, SCALAR, READ],
                            { 'label':"Element list",
                              'description' : 'the list of all elements (a '
                                              'JSON encoded dict)', } ],
        }

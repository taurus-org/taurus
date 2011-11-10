import sys
import threading
import time
import copy
import json

import PyTango
import taurus
import taurus.core.util
from taurus.core.util import etree, CodecFactory

from sardana.macroserver.exception import MacroServerException
from sardana.macroserver.attributehandler import AttributeLogHandler
from sardana.macroserver.macro import Macro


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


class Door(PyTango.Device_4Impl, taurus.core.util.Logger):

    def __init__(self,cl, name):
        PyTango.Device_4Impl.__init__(self,cl,name)
        try:
            db = taurus.Database()
            self._alias = db.get_alias(name)
            if self._alias.lower() == 'nada':
                self._alias = name
        except:
            self._alias = name
        self._simulation = None
        self._macro_server = None
        taurus.core.util.Logger.__init__(self, self._alias)
        Door.init_device(self)

    def delete_device(self):
        if self.getRunningMacro():
            self.debug("aborting running macro")
            self.macro_executor.abort()
        
        if self._simulation:
            del self._simulation
        
        for handler, filter, format in self._handler_dict.values():
            handler.finish()
        
        self.manager.removeDoor(self)

    def init_device(self):
        self.set_state(Macro.Ready)
        self.get_device_properties(self.get_device_class())
        self.set_change_event('State', True, False)
        self.set_change_event('Status', True, False)
        self.set_change_event('Result', True, False)
        self.set_change_event('RecordData', True, False)
        self.set_change_event('MacroStatus', True, False)
        self.set_change_event('Environment', True, False)
        
        self.manager.addDoor(self)
        
        self._setupLogHandlers()
        
        self.push_change_event('State')
        self.push_change_event('Status')
    
    def _setupLogHandlers(self):
        self._handler_dict = {}
        levels = ('Critical', 'Error', 'Warning', 'Info', 'Output', 'Debug')
        
        for level in levels:
            level_val = getattr(Door, level)
            handler_klass = AttributeLogHandler
            handler = handler_klass(self, level, max_buff_size=self.MaxMsgBufferSize)
            filter = taurus.core.util.LogFilter(level=level_val)
            handler.addFilter(filter)
            self.addLogHandler(handler)
            format = None
            self._handler_dict[level] = handler, filter, format
        
    @property
    def manager(self):
        import sardana.macroserver.manager
        return sardana.macroserver.manager.MacroServerManager()
    
    @property
    def macro_executor(self):
        return self.manager.getMacroExecutor(self)
    
    def getRunningMacro(self):
        return self.macro_executor.getRunningMacro()
    
    @property
    def macro_server(self):
        ms = self._macro_server
        if ms is None:
            util = PyTango.Util.instance()
            self._macro_server = ms = \
                util.get_device_list_by_class("MacroServer")[0]
        return ms

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
        return self.get_state() in [Macro.Ready, Macro.Abort]
    
    def readLogAttr(self, attr):
        name = attr.get_name()
        handler, filter, format = self._handler_dict[name]
        handler.read(attr)

    read_Critical = read_Error = read_Warning = read_Info = read_Output = \
        read_Debug = read_Trace = readLogAttr 

    #@DebugIt()
    def read_ElementList(self, attr):
        element_list = self.macro_server.getElementList()
        attr.set_value(*element_list)
        
    def sendRecordData(self, format, data):
        self.push_change_event('RecordData', format, data)

    def sendState(self, state):
        self.set_state(state)
        self.push_change_event('state')
    
    def sendStatus(self, status):
        self.set_status(status)
        self.push_change_event('status')
    
    def sendMacroStatus(self, format, data):
        self.push_change_event('MacroStatus', format, data)
    
    def sendEnvironment(self, format, data):
        self.push_change_event('Environment', format, data)
    
    def getLogAttr(self, name):
        return self._handler_dict.get(name)
    
    def read_Result(self, attr):
        #    Add your own code here
        attr.set_value([], 0)
    
    def read_RecordData(self, attr):
        attr.set_value('', '')
    
    def read_MacroStatus(self, attr):
        attr.set_value('', '')
    
    def read_Environment(self, attr):
        env = self.manager.getAllDoorEnv(door_name=self.get_name())
        env["__type__"] = "new"
        attr.set_value('json', json.dumps(env))
        return
        
    def write_Environment(self, attr):
        data = attr.get_write_value()
        codec = CodecFactory().getCodec('json')
        data = codec.decode(data, ensure_ascii=True)[1]
        self.manager.setEnvObj(data)
    
    def is_Environment_allowed(self, req_type):
        return True
    
    def Abort(self):
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
            self.debug("stoping macro %s" % macro.getDescription())
            self.macro_executor.stop()
        else:
            self._simulation.stopMacro()
    
    def is_PauseMacro_allowed(self):
        return self.get_state() == Macro.Running
    
    def ResumeMacro(self):
        if self._simulation is None:
            macro = self.getRunningMacro()
            if macro is None:
                return
            self.debug("resume macro %s" % macro.getDescription())
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
        
        xml_seq = self.macro_executor.run(par_str_list)
        return [etree.tostring(xml_seq, pretty_print=False)]

    def is_RunMacro_allowed(self):
        return self.get_state() in [Macro.Finished, Macro.Abort]

    def SimulateMacro(self, par_str_list):
        raise Exception("Not implemented yet")
    
    def ReloadMacro(self, argin):
        """ReloadMacro(list<string> macro_names):
        """
        try:
            self.manager.reloadMacros(argin)
        except MacroServerException, mse:
            PyTango.Except.throw_exception(mse.type, mse.msg, 'ReloadMacro')
        return ['OK']

    def is_ReloadMacro_allowed(self):
        return self.get_state() in [Macro.Finished, Macro.Abort]
    
    def ReloadMacroLib(self, argin):
        """ReloadMacroLib(list<string> lib_names):
        """
        try:
            self.manager.reloadMacroLibs(argin)
        except MacroServerException, mse:
            PyTango.Except.throw_exception(mse.type, mse.msg, 'ReloadMacroLib')
        return ['OK']
    
    def is_ReloadMacroLib_allowed(self):
        return self.get_state() in [Macro.Finished, Macro.Abort]

    def GetMacroEnv(self, argin):
        macro_name = argin[0]
        if len(argin) > 1:
            macro_env = argin[1:]
        else:
            macro_env = self.manager.getMacroClass(macro_name).env
        env = self.manager.getDoorMacroEnv(self.get_name(), macro_name, macro_env)
        ret = []
        for k,v in env.iteritems():
            ret.extend((k,v))
        return ret
    
    def is_GetMacroEnv_allowed(self):
        return self.get_state() in [Macro.Finished, Macro.Abort]
    
class DoorClass(PyTango.DeviceClass):

    #    Class Properties
    class_property_list = {
        }

    #    Device Properties
    device_property_list = {
        'MaxMsgBufferSize':
            [PyTango.DevLong,
            'Maximum size for the Output, Result, Error, Warning, Debug and Info buffers',
            [512] ],
        }

    #    Command definitions
    cmd_list = {
        'Abort':
            [ [ PyTango.DevVoid, ""],
              [ PyTango.DevVoid, ""] ],
        'PauseMacro':
            [ [PyTango.DevVoid, ""],
              [PyTango.DevVoid, ""] ],
        'StopMacro':
            [ [PyTango.DevVoid, ""],
              [PyTango.DevVoid, ""] ],
        'ResumeMacro':
            [ [PyTango.DevVoid, ""],
              [PyTango.DevVoid, ""] ],
        'RunMacro':
            [ [PyTango.DevVarStringArray, 'Macro name and parameters'],
              [PyTango.DevVarStringArray, 'Macro Result']],
        'SimulateMacro':
            [ [PyTango.DevVarStringArray, 'Macro name and parameters'],
              [PyTango.DevVarStringArray, 'Macro statistics']],
        'GetMacroEnv':
            [ [ PyTango.DevVarStringArray, 'Macro name followed by an ' \
                'optional list of environment names' ],
              [ PyTango.DevVarStringArray, 'Macro environment as a list of '\
                'pairs keys, value'] ],
#        'ReloadMacro':
#            [[PyTango.DevVarStringArray, "Macro(s) name(s)"],
#            [PyTango.DevVarStringArray, "[OK] if successfull or a traceback " \
#                "if there was a error (one string with complete traceback of " \
#                "each error)"]],
#        'ReloadMacroLib':
#            [[PyTango.DevVarStringArray, "MacroLib(s) name(s)"],
#            [PyTango.DevVarStringArray, "[OK] if successfull or a traceback " \
#                "if there was a error (one string with complete traceback of " \
#                "each error)"]],
        }


    #    Attribute definitions
    attr_list = {
        'SimulationMode':
            [[PyTango.DevBoolean,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
                'label'     : 'Simulation mode',
                'Memorized' : 'true',
            } ],
        'Result':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 512],
            {
                'label'     : 'Result for the last macro',
            } ],
        'Critical':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 512],
            {
                'label'     : 'Macro critical error message',
            } ],
        'Error':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 512],
            {
                'label'     : 'Macro error message',
            } ],
        'Warning':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 512],
            {
                'label'     : 'Macro warning message',
            } ],
        'Info':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 512],
            {
                'label'     : 'Macro information message',
            } ],
        'Output':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 512],
            {
                'label'     : 'Macro output message',
            } ],
        'Debug':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 512],
            {
                'label'     : 'Macro debug message',
            } ],
        'Environment':
            [[PyTango.DevEncoded,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
                'label'     : 'Door environment',
            } ],
        'RecordData':
            [[PyTango.DevEncoded,
            PyTango.SCALAR,
            PyTango.READ],
            {
                'label'     : 'Record Data',
            } ],
        'MacroStatus':
            [[PyTango.DevEncoded,
            PyTango.SCALAR,
            PyTango.READ],
            {
                'label'     : 'Macro Status',
            } ],
        'ElementList':
            [[PyTango.DevEncoded,
            PyTango.SCALAR,
            PyTango.READ],
            {
                'label':"Element list",
                'description':"the list of all elements (a JSON encoded dict)",
            } ],
        }

    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name);

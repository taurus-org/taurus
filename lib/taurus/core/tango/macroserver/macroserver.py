#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""The macroserver submodule. It contains specific part of macroserver"""

__all__ = [ 'BaseDoor', 'BaseMacroServer', 'registerExtensions' ]

__docformat__ = 'restructuredtext'

import sys
import re
import weakref
import copy
import types
import operator
import threading
import time
import uuid

import PyTango

import taurus
import taurus.core
import taurus.core.tango
import taurus.core.util
from taurus.core.util import etree
from taurus.core.util.console import NoColors, TermColors
import macro

CHANGE_EVTS = (taurus.core.TaurusEventType.Change, taurus.core.TaurusEventType.Periodic)

class Attr(taurus.core.util.Logger, taurus.core.util.EventGenerator):

    def __init__(self, dev, name, obj_class, attr):
        self._dev = weakref.ref(dev)
        self._obj_class  = obj_class
        self._attr = attr
        self.call__init__(taurus.core.util.Logger, name)
        event_name = '%s %s' % (dev.getNormalName(), name)
        self.call__init__(taurus.core.util.EventGenerator, event_name)
        
        self._attr.addListener(self)
        
    def eventReceived(self, src, type, evt_value):
        if type == taurus.core.TaurusEventType.Error:
            self.fireEvent(None)
        elif type != taurus.core.TaurusEventType.Config:
            if evt_value:
                self.fireEvent(evt_value.value)
            else:
                self.fireEvent(None)
                
    def getTaurusAttribute(self):
        return self._attr

    def __getattr__(self, name):
        return getattr(self._attr, name)

class LogAttr(Attr):
    
    def __init__(self, dev, name, obj_class, attr, max_buff_size=4096):
        self._log_buffer = []
        self._max_buff_size = max_buff_size
        self.call__init__(Attr, dev, name, obj_class, attr)
        
    def getLogBuffer(self):
        return self._log_buffer
    
    def clearLogBuffer(self):
        self._log_buffer = []
    
    def eventReceived(self, src, type, evt_value):
        if type == taurus.core.TaurusEventType.Change:
            if evt_value is None or evt_value.value is None:
                self.fireEvent(None)
            else:
                self._log_buffer.extend(evt_value.value)
                while len(self._log_buffer) > self._max_buff_size:
                    self._log_buffer.pop(0)
                if evt_value:
                    self.fireEvent(evt_value.value)


class MacroServerDevice(taurus.core.tango.TangoDevice):
    """A class encapsulating a generic macro server device (usually a 
    MacroServer or a Door"""

    def _createAttribute(self, attr_name):
        attr_name = "%s/%s" % (self.getFullName(), attr_name)
        return self.factory().getAttribute(attr_name)

    def _getEventWait(self):
        if not hasattr(self, '_evt_wait'):
            # create an object that waits for attribute events.
            # each time we use it we have to connect and disconnect to an attribute
            self._evt_wait = taurus.core.util.AttributeEventWait()
        return self._evt_wait


class BaseDoor(MacroServerDevice):
    """ Class encapsulating Door device functionality."""

    On = PyTango.DevState.ON
    Running = PyTango.DevState.RUNNING
    Paused = PyTango.DevState.STANDBY
    
    Critical = 'Critical'
    Error = 'Error'
    Warning = 'Warning'
    Info = 'Info'
    Output = 'Output'
    Debug = 'Debug'
    Result = 'Result'
    RecordData = 'RecordData'

    BlockStart  = '<BLOCK>'
    BlockFinish = '</BLOCK>'

    log_streams = (Error, Warning, Info, Output, Debug, Result)

    # maximum execution time without user interruption
    InteractiveTimeout = 0.1
    
    def __init__(self, name, **kw):
        self._log_attr = taurus.core.util.CaselessDict()
        self._block_lines = 0
        self._macro_server = None

        self._running_macros = None
        self._running_macro = None
        self._user_xml =None
        self._ignore_logs = kw.get("ignore_logs", False)
        self._silent = kw.get("silent", True)
        self._debug = kw.get("debug", False)
        self._output_stream = kw.get("output", sys.stdout)
        self._writeLock = threading.Lock()
        self._env = {}

        self.call__init__(taurus.core.tango.TangoDevice, name, **kw)
        
        self._old_door_state = PyTango.DevState.UNKNOWN
        self._old_sw_door_state = taurus.core.TaurusSWDevState.Uninitialized
        
        self.getStateObj().addListener(self.stateChanged)
        #self._state_attr = Attr(self, "state", None, self.getStateObj())
        #self._state_attr.subscribeEvent(self.stateChanged)

        for log_name in self.log_streams:
            tg_attr = self._createAttribute(log_name)
            attr = LogAttr(self, log_name, None, tg_attr)
            if log_name == 'Result':
                attr.subscribeEvent(self.resultReceived, log_name)
            else:
                attr.subscribeEvent(self.logReceived, log_name)
            self._log_attr[log_name] = attr

        self._environment_attr = self._createAttribute('Environment')
        self._environment_attr.addListener(self.environmentChanged)
        
        #ms = self.macro_server
        #macro_list_obj = ms.getAttribute("MacroList")
        #macro_list_obj.addListener(self.macrosChanged)
        
        record_data_attr = self.getAttribute('RecordData')
        record_data_attr.addListener(self.recordDataReceived)
        
        macro_status_attr = self.getAttribute('MacroStatus')
        macro_status_attr.addListener(self.macroStatusReceived)
        
        #record_data_attr = self._createAttribute('RecordData')
        #self._record_data_attr = Attr(self, 'RecordData', None, record_data_attr)
        #self._record_data_attr.subscribeEvent(self.recordDataReceived)

    def get_color_mode(self):
        return "NoColor"
    
    #def macrosChanged(self, s, v, t):
    #    pass
    
    @property
    def log_start(self):
        if not hasattr(self, "_log_start"):
            import taurus.core.util.console
            if self.get_color_mode() == "NoColor":
                kls = taurus.core.util.console.NoColors
            else:
                kls = taurus.core.util.console.TermColors
            self._log_start = { BaseDoor.Critical : kls.LightRed,
                                BaseDoor.Error    : kls.Red,
                                BaseDoor.Info     : kls.LightBlue,
                                BaseDoor.Warning  : kls.Brown,
                                BaseDoor.Output   : kls.Normal,
                                BaseDoor.Debug    : kls.DarkGray,
                                BaseDoor.Result   : kls.LightGreen }
        return self._log_start
    
    @property
    def log_stop(self):
        if not hasattr(self, "_log_stop"):
            import taurus.core.util.console
            if self.get_color_mode() == "NoColor":
                kls = taurus.core.util.console.NoColors
            else:
                kls = taurus.core.util.console.TermColors
            self._log_stop = {  BaseDoor.Critical : kls.Normal,
                                BaseDoor.Error    : kls.Normal,
                                BaseDoor.Info     : kls.Normal,
                                BaseDoor.Warning  : kls.Normal,
                                BaseDoor.Output   : kls.Normal,
                                BaseDoor.Debug    : kls.Normal,
                                BaseDoor.Result   : kls.Normal }
        return self._log_stop
    
    def getStateAttr(self):
        return self._state_attr
    
    @property
    def macro_server(self):
        if self._macro_server is None:
            self._macro_server = self._get_macroserver_for_door()
        return self._macro_server

    def _get_macroserver_for_door(self):
        """Returns the MacroServer device object in the same DeviceServer as this
        door"""
        db = self.factory().getDatabase()
        door_name = self.dev_name()
        server_list = db.get_server_list('MacroServer/*')
        server_devs = None
        for server in server_list:
            server_devs = db.get_device_class_list(server)
            devs, klasses = server_devs[0::2], server_devs[1::2]
            for dev in devs:
                if dev.lower() == door_name:
                    for i, klass in enumerate(klasses):
                        if klass == 'MacroServer':
                            return self.factory().getDevice(devs[i])
        else:
            return None

    def setDebugMode(self, state):
        self._debug = state
    
    def getDebugMode(self):
        return self._debug

    def setSilent(self, yesno):
        self._silent = yesno
    
    def isSilent(self):
        return self._silent
    
    def getEnvironmentObj(self):
        return self._environment_attr

    def getLogObj(self, log_name='Debug'):
        return self._log_attr.get(log_name, None)

    def getRunningXML(self):
        return self._user_xml

    def getRunningMacro(self):
        return self._running_macro

    def abort(self, synch=True):
        if not synch:
            self.command_inout("Abort")
            return
        
        evt_wait = taurus.core.util.AttributeEventWait(self.getAttribute("state"))
        evt_wait.lock()
        try:
            time_stamp = time.time()
            self.command_inout("Abort")
            evt_wait.waitEvent(self.On, after=time_stamp, timeout=self.InteractiveTimeout)
        finally:
            evt_wait.unlock()
            evt_wait.disconnect()

    def _clearRunMacro(self):
        # Clear the log buffer
        map(LogAttr.clearLogBuffer, self._log_attr.values())
        self._running_macros = None
        self._running_macro = None
        self._user_xml =None
        self._block_lines = 0

    def preRunMacro(self, obj, parameters):
        self._clearRunMacro()
            
        xml_root = None
        if type(obj) in types.StringTypes:
            if obj.startswith('<') and not parameters:
                xml_root = etree.fromstring(obj)
            else:
                macros = []
                if len(parameters) == 0:
                    macros_strs = obj.split('\n')
                    for m in macros_strs:
                        pars = m.split()
                        macros.append((pars[0], pars[1:]))
                else:
                    parameters = map(str, parameters)
                    macros.append((obj, parameters))
                xml_root = xml_seq = etree.Element('sequence')
                for m in macros:
                    xml_macro = etree.SubElement(xml_seq, 'macro')
                    xml_macro.set('name', m[0])
                    xml_macro.set('id', str(uuid.uuid1()))
                    for p in m[1]:
                        xml_param = etree.SubElement(xml_macro, 'param', value=p)
        elif etree.iselement(obj):
            xml_root = obj
        else:
            raise TypeError('obj must be a string or a etree.Element')
    
        self._running_macros = {}
        for macro_xml in xml_root.xpath('//macro'):
            id, name = macro_xml.get('id'), macro_xml.get('name')
            self._running_macros[id] = macro.Macro(self, name, id, macro_xml)
        return xml_root

    def postRunMacro(self, result, synch):
        pass
    
    def runMacro(self, obj, parameters=[], synch=False):
        self._user_xml = self.preRunMacro(obj, parameters)
        result = self._runMacro(self._user_xml, synch=synch)
        return self.postRunMacro(result, synch)

    def _runMacro(self, xml, synch=False):
        if not synch:
            return self.command_inout("RunMacro", [etree.tostring(xml)])
        
        evt_wait = self._getEventWait()
        evt_wait.connect(self.getAttribute("state"))
        evt_wait.lock()
        try:
            evt_wait.waitEvent(self.Running, equal=False, timeout=self.InteractiveTimeout)
            ts = time.time()
            result = self.command_inout("RunMacro", [etree.tostring(xml)])
            evt_wait.waitEvent(self.Running, after=ts, timeout=self.InteractiveTimeout)
            if synch:
                evt_wait.waitEvent(self.On, after=ts, timeout=self.InteractiveTimeout)
        except:
            self._clearRunMacro()
            raise
        finally:
            evt_wait.unlock()
            evt_wait.disconnect()
        return result
    
    def stateChanged(self, s, t, v):
        self._old_door_state = self.getState()
        self._old_sw_door_state = self.getSWState()

    def resultReceived(self, log_name, result):
        """Method invoked by the arrival of a change event on the Result attribute"""
        
        if self._ignore_logs or self._running_macros is None: 
            return
        self._running_macro.setResult(result)
    
    def environmentChanged(self, s, t, v):
        if t not in CHANGE_EVTS: return
        return self._processEnvironmentData(v)
        
    def _processEnvironmentData(self, data):
        if data is None: return
        data = data.value
        size = len(data[1])
        if size == 0: return
        format = data[0]
        codec = taurus.core.util.CodecFactory().getCodec(format)
        obj = codec.decode(data)
        env_type = obj[1].get("__type__")
        if env_type == 'set_env':
            self._env.update(obj[1])
        return obj
    
    def recordDataReceived(self, s, t, v):
        if t not in CHANGE_EVTS: return
        return self._processRecordData(v)
    
    def _processRecordData(self, data):
        if data is None: return
        data = data.value
        size = len(data[1])
        if size == 0: return
        format = data[0]
        codec = taurus.core.util.CodecFactory().getCodec(format)
        return codec.decode(data)
    
    def macroStatusReceived(self, s, t, v):
        if v is None or self._running_macros is None:
            return
        if t not in CHANGE_EVTS: return

        v = v.value
        if not len(v[1]):
            return
        format = v[0]
        codec = taurus.core.util.CodecFactory().getCodec(format)
        
        fmt, data = codec.decode(v)
        for macro_status in data:
            id = macro_status.get('id')
            self._running_macro = macro = self._running_macros.get(id)
            # if we don't have the ID it's because the macro is running a submacro
            # or another client is connected to the same door (shame on him!) and
            # executing a macro we discard this event
            if not macro is None:
                macro.__dict__.update(macro_status)
        return data

    def logReceived(self, log_name, output):
        if not output or self._silent or self._ignore_logs:
            return
        
        if log_name == self.Debug and not self._debug:
            return

        o = self.log_start[log_name]
        for line in output:
            if not self._debug:
                if line == self.BlockStart:
                    for i in xrange(self._block_lines):
                        o += '\x1b[2K\x1b[1A\x1b[2K' #erase current line, up one line, erase current line
                    self._block_lines = 0
                    continue
                elif line == self.BlockFinish:
                    continue
            o += "%s\n" % line
            self._block_lines += 1
        o += self.log_stop[log_name]
        self.write(o)
    
    def write(self, msg, stream=None):
        if self.isSilent():
            return
        msg = msg.encode('utf-8')
        self._output_stream = sys.stdout
        out = self._output_stream
        if not stream is None:
            start,stop = self.log_start.get(stream), self.log_stop.get(stream)
            if start is not None and stop is not None:
                out.write(start)
                out.write(msg)
                out.write(stop)
                out.flush()
                return
        out.write(msg)
        out.flush()
    
    def writeln(self, msg='', stream=None):
        self.write("%s\n" % msg, stream=stream)


class UnknownMacroServerElementFormat(Exception):
    pass


class MacroServerElement:
    
    CommonReStr = '(?P<alias>\S+)\s+\((?P<id>[^)]+)\)'
    
    # The regular expression string to parse from the MacroServer
    BaseReStr    = CommonReStr + '.+\[(?P<pool_id>[^\)]+)\]'
    # The compiled regular expression to parse from the MacroServer
    BaseRe       = re.compile(BaseReStr)

    # The basic string representation
    SimpleReprStr = '%(alias)s'
    # The string representation  
    ReprStr   = SimpleReprStr + ' (%(id)s) [%(pool_id)s]'

    def __init__(self, type, from_str):
        self._type = type
        m = self.BaseRe.match(from_str)
        if m is None:
            raise UnknownMacroServerElementFormat('Unable to parse element ' \
                                                  'information %s' % from_str)
        self.__dict__.update(m.groupdict())

    def __repr__(self):
        return self.SimpleReprStr % self.__dict__
    
    def __str__(self):
        return self.ReprStr % self.__dict__
    
    def getName(self):
        return self.SimpleReprStr % self.__dict__
    
    def getId(self):
        return self.id

    def getPoolId(self):
        return self.pool_id
    
    def getType(self):
        return self._type


class MacroServerElementContainer:
    
    def __init__(self):
        # dict<str, dict> where key is the pool device name and value is:
        #     dict<str, MacroServerElement> where key is the element alias
        #                                   and value is the Element object
        self._pool_elems_dict = taurus.core.util.CaselessDict()
        
        # dict<str, dict> where key is the type and value is:
        #     dict<str, MacroServerElement> where key is the element alias and
        #                                   value is the Element object
        self._type_elems_dict = taurus.core.util.CaselessDict()
        
        # dict<str, MacroServerElement> where key is the element alias and value
        #                               value is the Element object
        self._name_elems_dict = taurus.core.util.CaselessDict()
    
    def addElement(self, e):
        pool = e.getPoolId()
        type = e.getType()
        name = e.getName()
        id = e.getId()
        
        # update pool_elems
        if self._pool_elems_dict.has_key(pool):
            pool_elems = self._pool_elems_dict.get(pool)
        else:
            pool_elems = taurus.core.util.CaselessDict()
            self._pool_elems_dict[pool] = pool_elems
        pool_elems[name] = e
    
        #update type_elems
        if self._type_elems_dict.has_key(type):
            type_elems = self._type_elems_dict.get(type)
        else:
            type_elems = taurus.core.util.CaselessDict()
            self._type_elems_dict[type] = type_elems
        type_elems[name] = e
        
        #update name_elems
        self._name_elems_dict[name] = e
    
    def removeElement(self, e):
        pool = e.getPoolId()
        type = e.getType()
        name = e.getName()
        id = e.getId()
        
        # update pool_elems
        pool_elems = self._pool_elems_dict.get(pool)
        if pool_elems:
            del pool_elems[name]
        
        # update type_elems
        type_elems = self._type_elems_dict.get(type)
        if type_elems:
            del type_elems[name]
        
        if self._name_elems_dict.has_key(name):
            del self._name_elems_dict[name]
    
    def removeElementsOfType(self, t):
        for elem in self.getElementsOfType(t):
            self.removeElement(elem)
    
    def getElementsOfType(self, t):
        elems = self._type_elems_dict.get(t, {})
        return elems.values()
    
    def getElementNamesOfType(self, t):
        elems = self._type_elems_dict.get(t, {})
        return elems.keys()
    
    def getElementsOfPool(self, pool):
        elems = self._pool_elems_dict.get(type, {})
        return elems.values()

    def getElementNamesOfPool(self, pool):
        elems = self._pool_elems_dict.get(type, {})
        return elems.keys()
    
    def hasElementName(self, elem_name):
        return self._name_elems_dict.has_key(elem_name)
    
    def getElementObj(self, elem_name):
        return self._name_elems_dict.get(elem_name)


class BaseMacroServer(MacroServerDevice):
    """Class encapsulating Macro Server device functionality."""
    
    def __init__(self, name, **kw):
        # dict<str, taurus.core.tango.TangoAttribute>
        # key - attribute name
        # value - taurus tango attribute object
        self._attr_dict = taurus.core.util.CaselessDict()
        
        # dict<str, sequence<object>>
        # key - type of object ('Macro', 'Type', 'Motor', 'CTExpChannel', etc)
        # value - sequence of objects of the key type
        self._obj_dict = taurus.core.util.CaselessDict()
        self._elems = MacroServerElementContainer()
        
        self._type_dict = {}
        
        self._macro_dict = {}
        
        self.call__init__(taurus.core.tango.TangoDevice, name, **kw)

        macro_list = self.getAttribute("MacroList")
        #self._attr_dict["MacroList"] = macro_list
        macro_list.addListener(self.macrosChanged)

        type_list = self.getAttribute("TypeList")
        #self._attr_dict["TypeList"] = type_list
        type_list.addListener(self.typesChanged)

    def typesChanged(self, s, t, v):
        if t not in CHANGE_EVTS: return
        self.removeTypes()
        self.addTypes(v.value)
            
    def addTypes(self, type_names):
        dev = self.getHWObj()
        dev_attr_names = map(str.lower, dev.get_attribute_list())

        for name in type_names:
            if self._type_dict.has_key(name):
                continue
            
            self._type_dict[name] = []
            
            name = name[:-1]
            attr_name = '%sList' % name
            
            if attr_name.lower() in dev_attr_names:
                attr = self._createAttribute(attr_name)
                self._attr_dict[attr_name] = attr
                attr_list = AttrList(self, name, None, attr)
                self._obj_dict[name] = attr_list
                attr_list.subscribeEvent(self.elementsChanged, name)

    def addTypes(self, type_names):
        dev = self.getHWObj()
        dev_attr_names = map(str.lower, dev.get_attribute_list())

        for name in type_names:
            if self._type_dict.has_key(name):
                continue
            
            self._type_dict[name] = []
            
            name = name[:-1]
            attr_name = '%sList' % name
            
            if attr_name.lower() in dev_attr_names:
                attr = self.getAttribute(attr_name)
                self._attr_dict[attr_name] = attr
                attr.addListener(self.elementsChanged)

    def removeTypes(self, type_names=None):
        type_names = type_names or self._type_dict.keys()
        for type_name in type_names:
            
            del self._type_dict[type_name]
            
            if not type_name.endswith('*'):
                return

            name = type_name[:-1]
            attr_name = '%sList' % name
            
            self._elems.removeElementsOfType(name)
            
            del_obj = self._attr_dict.pop(name, None)
            if not del_obj is None:
                del_obj.removeListener(self.elementsChanged)

    def elementsChanged(self, s, t, v):
        """Executed when the list of elements of a certain type as changed"""
        if t not in CHANGE_EVTS: return
        family = v.name[:-4] # Take the 'List' suffix out
        self._elems.removeElementsOfType(family)
        if v.value:
            for elem_str in v.value:
                self.addElement(family, elem_str)

    def addElement(self, family, elem_str):
        elem = MacroServerElement(family, elem_str)
        self._elems.addElement(elem)
        return elem
        
    def macrosChanged(self, s, t, v):
        if t == taurus.core.TaurusEventType.Config:
            return
        
        try:
            old_macro_names = set(self.getMacroStrList())
        except AttributeError:
            old_macro_names = set()

        # remove information about all macros. some macros may just have
        # changed their description, for example, so everything needs to be rebuild
        self.removeMacros()
        
        if t ==  taurus.core.TaurusEventType.Error:
            return
        
        all_macros = v.value
        self.addMacros(all_macros)

        all_macro_names = set(all_macros)
        deleted_macro_names = old_macro_names.difference(all_macro_names)
        new_macro_names = all_macro_names.difference(old_macro_names)

        deleted_macro_nb = len(deleted_macro_names)
        new_macro_nb = len(new_macro_names)

        if deleted_macro_nb != 0:
            self.debug('%d macro(s) deleted' % deleted_macro_nb)
        if new_macro_nb != 0:
            self.debug('%d new macro(s) available' % new_macro_nb)
    
    def addMacros(self, macro_names):
        json_macros = self.GetMacroInfo(macro_names)
        for json_macro in json_macros:
            self.addMacro(json_macro)
            
    def removeMacros(self, macro_names=None):
        if macro_names is None:
            macro_names = self._macro_dict.keys()
        
        for macro_name in macro_names:
            self.removeMacro(macro_name)

    def addMacro(self, json_macro):
        macro_info = macro.MacroInfo(from_json_str=json_macro)
        self._macro_dict[macro_info.name] = macro_info
        return macro_info
        
    def removeMacro(self, macro_name):
        if self._macro_dict.has_key(macro_name):
            del self._macro_dict[macro_name]
    
    def getMacroInfoObj(self, macro_name):
        return self._macro_dict.get(macro_name)
    
    def getMacroStrList(self):
        return self._macro_dict.keys()
    
    def getElementNamesOfType(self, type):
        return self._elems.getElementNamesOfType(type)
    
    def getMacroNodeObj(self, macro_name):
        """
        This method retrieves information about macro from MacroServer
        and creates MacroNode object, filled with all information about parameters.
        
        :param macro_name: (str) macro name 
        
        :return: (MacroNode)
        
        See Also: fillMacroNodeAddidtionalInfos
        """
        
        macroNode = macro.MacroNode(name=macro_name)
        macroInfoObj = self._macro_dict.get(macro_name)
        if macroInfoObj is None: return
        allowedHookPlaces = []
        for hook in macroInfoObj.hints.get('allowsHooks', []):
            allowedHookPlaces.append(str(hook))
        macroNode.setAllowedHookPlaces(allowedHookPlaces)
        macroNode.setHasParams(macroInfoObj.hasParams())
        paramsInfo = macroInfoObj.getParamList()
        for paramInfo in paramsInfo:
            param = macro.ParamFactory(paramInfo)
            macroNode.addParam(param)
        return macroNode
    
    def fillMacroNodeAdditionalInfos(self, macroNode):        
        """
        This method filles macroNode information which couldn't be stored 
        in XML file.
        
        :param macroNode: (MacroNode) macro node obj populated from XML information
        
        See Also: getMacroNodeObj
        """
        macroInfoObj = self._macro_dict.get(macroNode.name())
        if macroInfoObj is None: return
        allowedHookPlaces = []
        for hook in macroInfoObj.hints.get("allowsHooks", []):
            allowedHookPlaces.append(str(hook))
        macroNode.setAllowedHookPlaces(allowedHookPlaces)
        hasParams = macroInfoObj.hasParams()
        macroNode.setHasParams(hasParams)
        if hasParams:
            paramList = macroInfoObj.getParamList()
            for paramNode, paramInfo in zip(macroNode.params(), paramList):
                self.__fillParamNodeAdditionalInfos(paramNode, paramInfo)
                                
    
    def __fillParamNodeAdditionalInfos(self, paramNode, paramInfo):
        """
        This is a protected method foreseen to use only internally by 
        fillMacroNodeAdditionaInfos, to be called for every param node obj."""
        type = paramInfo.get('type')
        paramNode.setDescription(str(paramInfo.get("description")))
        min = paramInfo.get("min")
        paramNode.setMin(min)
        max = paramInfo.get("max")
        paramNode.setMax(max)    
        if isinstance(type,list):
            paramNode.setParamsInfo(type)
            for repeatNode in paramNode.children():
                for internalParamNode, internalParamInfo in zip(repeatNode.children(), type):
                    self.__fillParamNodeAdditionalInfos(internalParamNode, internalParamInfo)
        else:
            paramNode.setType(str(type))
            paramNode.setDefValue(str(paramInfo.get("default_value")))


def registerExtensions():
    factory = taurus.Factory()
    factory.registerDeviceClass('MacroServer', BaseMacroServer)
    factory.registerDeviceClass('Door', BaseDoor)


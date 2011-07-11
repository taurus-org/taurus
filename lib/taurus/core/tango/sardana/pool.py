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

"""The device pool submodule. It contains specific part of sardana device pool"""

__all__ = ["AbortException", "BaseElement", "ControllerClassProp",
           "ControllerClassPropInstance", "ControllerClass", "PoolElement",
           "Controller", "ComChannel", "ExpChannel", "CTExpChannel",
           "ZeroDExpChannel", "OneDExpChannel", "TwoDExpChannel",
           "PseudoCounter", "Motor", "PseudoMotor", "MotorGroup",
           "MeasurementGroup", "IORegister", "Instrument", "Pool",
           "registerExtensions"]

__docformat__ = 'restructuredtext'

import os
import weakref
import re
import thread
import copy
import time
import operator

import taurus.core
import taurus.core.util
import taurus.core.tango

import motion

import PyTango

Ready = Standby = PyTango.DevState.ON
Counting = Acquiring = Moving = PyTango.DevState.MOVING
Alarm = PyTango.DevState.ALARM
Fault = PyTango.DevState.FAULT

class AbortException(Exception):
    pass

class BaseElement(object):
    """ The base class for elements in the Pool (Pool itself, Motor, 
    ControllerClass, ExpChannel all should inherit from this class directly or
    indirectly) 
    
    Demands that the subclasses contain the following members:
    - At the class level:
      cls.BaseReStr - a string representing the regular expression to parse from
                      the string that is received from the Pool
      cls.BaseRe - a re.compile result of the cls.BaseReStr
      cls.SimpleReprStr - the basic string representation for the MacroServer 
                          attribute
      cls.ReprStr - the string representation for the MacroServer attribute

    - At the object level:
      self._name_lower - the lower case string name of the object (used for 
                         __cmp__)
      self._full_pool_name - the original string coming from the Pool
      self._pool - the pool object
    """
    CommonReStr = '(?P<_alias>\S+)\s+\((?P<_id>[^\)]+)\)\s+'

    # The string representation for the MacroServer attribute
    ReprStr   = '%(_full_pool_name)s [%(_pool)s]'
    
    # The basic string representation for the MacroServer attribute
    SimpleReprStr = '%(_simp_name)s'
        
    @classmethod
    def getElementRE(cls):
        return cls.BaseRe

    @classmethod
    def getElementREStr(cls):
        return cls.BaseReStr

    @classmethod
    def match(cls, s):
        r = cls.BaseRe.match(s)
        if r: return r.groupdict()
        return None

    def __repr__(self):
        return self.ReprStr % self.__dict__
    
    def __str__(self):
        return self.SimpleReprStr % self.__dict__

    def str(self, n=4):
        """Returns a sequence of strings representing the object in 'consistent'
        way. Default is to return <name>, <controller name>, <axis>
        @param n the number of elements in the tuple."""
        return self._str_tuple[:n]
    
    def __cmp__(self,o):
        return cmp(self._name_lower, o._name_lower)
    
    def getName(self):
        return self.SimpleReprStr % self.__dict__

    def getPoolObj(self):
        return self._pool


class ControllerClassProp(taurus.core.util.Object):
    
    def __init__(self,name,type,desc,dftv):
        self.name = name
        self.type = type
        self.desc = desc
        self.dftv = dftv
    
    
class ControllerClassPropInstance(ControllerClassProp):
    
    def __init__(self,name,type,desc,value):
        self.name = name
        self.type = type
        self.desc = desc
        self.value = value


class ControllerClass(BaseElement):
    
    BaseReStr = '(?P<_alias>\w+)\s+\((?P<_filename>.+)\)\s+(?P<_type>\w+)'
    # The compiled regular expression to parse from the pool
    BaseRe       = re.compile(BaseReStr)
    
    # The basic string representation for the MacroServer attribute
    SimpleReprStr = '%(_alias)s'
    
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self._id = self._alias
        self._simp_name = self._alias
        self._path, self._fname = os.path.split(self._filename)
        self._libname, self._ext = os.path.splitext(self._fname)
        self._props = {}
        
        self._buildInfo()
        
        self._str_tuple = self.getName(), self.getType(), self.getLib(), self.getGender()
        
    def _buildInfo(self):
        
        params = self.getType(), self.getLib(), self.getClassName()
        pool = self.getPoolObj()
        info = pool.command_inout("getControllerInfo", params)
        self._descr = info[0]
        self._gender = info[1]
        self._model = info[2]
        self._organization = info[3]
        
        self._nb_prop = int(info[4])
        for i in xrange(self._nb_prop):
            idx = 5 + 4*i
            p = ControllerClassProp(info[idx],info[idx+1],info[idx+2],info[idx+3])
            self._props[p.name] = p
        
        i = 5 + 4 * self._nb_prop
        
        if self._type == "PseudoMotor":
            self._mot_roles = []
            self._nb_mot_roles = int(info[i])
            i = i + 1
            for m in xrange(self._nb_mot_roles):
                self._mot_roles.append(info[i])
                i = i + 1 
                
            self._pm_roles = []
            self._nb_pm_roles = int(info[i])
            i = i + 1
            for pm in xrange(self._nb_pm_roles):
                self._pm_roles.append(info[i])
                i = i + 1
            
        elif self._type == "PseudoCounter":
            self._counter_roles = []
            self._nb_counter_roles = int(info[i])
            i = i + 1
            for c in xrange(self._nb_counter_roles):
                self._counter_roles.append(info[i])
                i = i + 1 

    def getFileName(self):
        return self._filename

    def getClassName(self):
        return self.getName()
    
    def getType(self):
        return self._type

    def getLib(self):
        return self._fname
    
    def getGender(self):
        return self._gender
    
    def getModel(self):
        return self._model
    
    def getOrganization(self):
        return self._organization

    def __cmp__(self, o):
        t = cmp(self.getType(), o.getType())
        if t != 0: return t
        t = cmp(self.getGender(), o.getGender())
        if t != 0: return t
        return cmp(self.getClassName(), o.getClassName())


class BaseObjList(taurus.core.util.Logger, taurus.core.util.EventGenerator):
    """An event generator for a 'List' type attribute"""
    def __init__(self, pool, name, obj_class, attr):
        self._pool = weakref.ref(pool)
        self._type = name
        self._list_name = '%sList' % self._type
        self._obj_class  = obj_class
        self._attr = attr
        self.call__init__(taurus.core.util.Logger, self._list_name, pool)
        event_name = 'Pool %s %s list' % (pool.getNormalName(), name)
        self.call__init__(taurus.core.util.EventGenerator, event_name)
        self._attr.addListener(self)
            
    def eventReceived(self, src, type, evt_value):
        """Event handler from Taurus"""
        pass

    def getPoolObj(self):
        return self._pool()
    
    def getObjClass(self):
        return self._obj_class

    def getObjByName(self, name):
        return self._obj_dict.get(name)

    def getElementRE(self):
        return self.getObjClass().getElementRE()

    def getElementREStr(self):
        return self.getObjClass().getElementREStr()
    
    def match(self, s):
        return self.getObjClass().match(s)

    def getObjs(self):
        return self.getObjDict().values()
    
    def getObjDict(self):
        return self._obj_dict

    def getObj(self, id):
        return self._obj_dict.get(id)


class SoftwareObjList(BaseObjList):
    """An event generator for a 'List' type attribute in the Pool 
    (ControllerClassList so far)"""
    def __init__(self, pool, name, obj_class, attr):
        self._obj_dict = None
        self.call__init__(BaseObjList, pool, name, obj_class, attr)

    def _buildCache(self, elems):
        self._obj_dict = {}
        pool = self.getPoolObj()
        for elem in elems:
            info_dict = self.match(elem)
            key = info_dict['_alias']
            info_dict.update({ '_pool' : pool, '_full_pool_name' : elem })
            self._obj_dict[key] = self._obj_class(**info_dict)
        return self._obj_dict.keys()

#    def read(self, cache=False):
#        if not cache or self._obj_dict is None:
#            return self._buildCache(self.attr.read(cache=False).value)
#        return self._obj_dict.keys()
    
    def eventReceived(self, evt_src, evt_type, evt_value):
        """Event handler from Taurus"""
        if not evt_type in (taurus.core.TaurusEventType.Change, taurus.core.TaurusEventType.Periodic):
            return
        
        if evt_value is None:
            self.debug('Received empty Change event')
            return
        
        # workaround for taurus bug
        if evt_value.value is None: evt_value.value = []
        
        res = self._buildCache(evt_value.value)

        # fire the event to the listeners ( a list of id )
        self.fireEvent(res)

class HardwareObjList(BaseObjList):
    """An event generator for a 'List' type attribute in the Pool 
    (MotorList, ExpChannelList, ComChannelList, etc)"""
    def __init__(self, pool, name, obj_class, attr):
        self._obj_dict = taurus.core.util.CaselessDict()
        self._obj_alias_dict = taurus.core.util.CaselessDict()
        self.call__init__(BaseObjList, pool, name, obj_class, attr)
    
    def getObjNameDict(self):
        return self._obj_alias_dict
    
    def getObjByName(self, name):
        #Overwrite base class because the alias is in another dictionary in this class
        return self._obj_alias_dict.get(name)
    
    def eventReceived(self, src, type, evt_value):
        """Event handler from Taurus"""
        
        if type != taurus.core.TaurusEventType.Change:
            return
        
        if evt_value is None or evt_value.value is None:
            return 
        
        elems_str = evt_value.value
        
        pool = self.getPoolObj()
        
        # - new_elems: list where each elem is a dict with keys dev_name and
        #   name and values the corresponding strings
        new_elems, modif_elems, del_elems = [], [], []
        all_elem_ids = []
        
        # find new and modified elements
        for elem_str in elems_str:
            info_dict = self.match(elem_str)
            if info_dict is None:
                self.warning("String '%s' could not match %s" % (elem_str, self.getElementREStr()))
                continue
            info_dict['_full_pool_name'] = elem_str
            id, name = info_dict['_id'].lower(), info_dict['_alias']
            all_elem_ids.append(id)
            if self._obj_dict.has_key(id):
                name = info_dict['_alias']
                elem = self._obj_dict[id]
                if elem.getName().lower() != name.lower():
                    modif_elems.append(info_dict)
            else:
                new_elems.append(info_dict)
        
        # find deleted elements
        for id, elem in self._obj_dict.items():
            if not id.lower() in all_elem_ids:
                del_elems.append({ '_id':id })
        
        # create the new elements
        f = taurus.Factory()
        for new_elem_data in new_elems:
            id = new_elem_data['_id']
            ctrl_name = new_elem_data.get('_ctrl_name')
            axis = int(new_elem_data.get('_axis', '0'))
            type = new_elem_data.get('_type')
            full_pool_name = new_elem_data.get('_full_pool_name')
            elem = f.getExistingDevice(id)
            if elem is not None:
                f.removeExistingDevice(id)
            elem = f.getDevice(id, _pool=pool, _ctrl_name=ctrl_name, 
                               _ctrl_axis=axis, _type=type,
                               _full_pool_name=full_pool_name)
            self._obj_dict[id] = elem
        
        # modify the existing ones
        for modif_elem_data in modif_elems:
            id, name = modif_elem_data['_id'], modif_elem_data['_name']
            elem = self._obj_dict.get(id)
            elem.setName(name)
        
        # remove the deleted elements
        for del_elem_data in del_elems:
            id = del_elem_data['_id']
            self._obj_dict.pop(id)
            f.removeExistingDevice(id)
            
        self._obj_alias_dict = taurus.core.util.CaselessDict()
        for elem in self._obj_dict.values():
            self._obj_alias_dict[elem.getName()] = elem
        
        # fire the event to the listeners ( a list of id )
        self.fireEvent(all_elem_ids)


class TangoAttributeEG(taurus.core.util.Logger, taurus.core.util.EventGenerator):
    """An event generator for a 'State' attribute"""
    
    def __init__(self, attr):
        self._attr = attr
        self.call__init__(taurus.core.util.Logger, 'EG', attr)
        event_name = '%s EG' % (attr.getParentObj().getNormalName())
        self.call__init__(taurus.core.util.EventGenerator, event_name)

        self._attr.addListener(self)
    
    def eventReceived(self, src, type, evt_value):
        """Event handler from Taurus"""
        if type not in (taurus.core.TaurusEventType.Change, taurus.core.TaurusEventType.Periodic):
            return
        if not evt_value is None:
            evt_value = evt_value.value
        taurus.core.util.EventGenerator.fireEvent(self, evt_value)

    def read(self, force=False):
        try:
            self.last_val = self._attr.read(cache=not force).value
        except:
            self.last_val = None
        return taurus.core.util.EventGenerator.read(self)
    
    def readValue(self, force=False):
        r = self.read(force=force)
        if r is None: return None
        return r
    
    def __getattr__(self, name):
        return getattr(self._attr, name)

def reservedOperation(fn):
    def new_fn(*args, **kwargs):
        self = args[0]
        wr = self.getReservedWR()
        if wr is not None and wr().isAborted():
            raise AbortException("aborted when calling %s" % fn.__name__)
        return fn(*args, **kwargs)
    return new_fn

class PoolElement(BaseElement, taurus.core.tango.TangoDevice):
    """Base class for a Pool element device."""
    
    # The regular expression string to parse from the pool
    BaseReStr    = BaseElement.CommonReStr + '\((?P<_ctrl_name>[^\/]+)\/(?P<_axis>\d+)\)\s+(?P<_type>\S+)'
    
    # The compiled regular expression to parse from the pool
    BaseRe       = re.compile(BaseReStr)
    
    # The basic string representation for the MacroServer attribute
    SimpleReprStr = '%(_simp_name)s'
    
    def __init__(self, name, **kw):
        """PoolElement initialization."""
        self._reserved = None
        self.call__init__(taurus.core.tango.TangoDevice, name, **kw)
        self._name_lower = self.getName().lower()
        self._str_tuple = self.getName(), self.getType(), self.getControllerName(), self.getAxis()

        # dict<string, TangoAttribute>
        # key : the attribute name
        # value : the corresponding TangoAttribute object from the taurus layer
        self._attr_obj = taurus.core.util.CaselessDict()
        
        # dict<string, TangoAttributeEG>
        # key : the attribute name
        # value : the corresponding TangoAttributeEG 
        self._attr_obj_ex = taurus.core.util.CaselessDict()
                
        # force the creation of a state attribute
        self.getStateExObj()

    def reserve(self, obj):
        if obj is None:
            self._reserved = None
            return
        self._reserved = weakref.ref(obj, self._unreserveCB)
    
    def _unreserveCB(self, obj):
        self.unreserve()
    
    def unreserve(self):
        self._reserved =None
        
    def isReserved(self, obj=None):
        if obj is None:
            return self._reserved is not None
        else:
            o = self._reserved()
            return o == obj

    def getReservedWR(self):
        return self._reserved

    def getReserved(self):
        if self._reserved is None: return None
        return self._reserved()
    
    def _getAttrValue(self, name, force=False):
        attrExObj = self._getAttrEx(name)
        if attrExObj is None: return None
        return attrExObj.readValue(force=force)
    
    def _getAttrEx(self, name):
        attrExObj = self.getAttrExObj(name)
        if attrExObj is None:
            attrExObj = self._createAttribute(name)[1]
        return attrExObj
    
    def _createAttribute(self, name):
        attrObj = self.getAttribute(name)
        if attrObj is None:
            self.warning("Unable to create attribute %s" % name)
            return None, None
        self._attr_obj[name] = attrObj
        attrExObj = TangoAttributeEG(attrObj)
        self._attr_obj_ex[name] = attrExObj
        return attrObj, attrExObj
    
    def _getEventWait(self):
        if not hasattr(self, '_evt_wait'):
            # create an object that waits for attribute events.
            # each time we use it we have to connect and disconnect to an attribute
            self._evt_wait = taurus.core.util.AttributeEventWait()
        return self._evt_wait
    
    def getStateExObj(self):
        return self._getAttrEx('state')
    
    def __cmp__(self,o):
        return cmp(self._name_lower, o._name_lower)

    def getControllerName(self):
        return self._ctrl_name
    
    def getAxis(self):
        return self._ctrl_axis

    def getType(self):
        return self._type

    def getPoolObj(self):
        return self._pool

    def waitReady(self, timeout=None):
        return self.getStateExObj().waitEvent(Moving, equal=False, timeout=timeout)

    def getAttrExObj(self, name):
        """Returns the TangoAttributeEG object"""
        return self._attr_obj_ex.get(name)
    
    def getAttrObj(self, name):
        """Returns the taurus.core.TangoAttribute object"""
        return self._attr_obj.get(name)

    def getInstrumentObj(self):
        return self._getAttrEx('instrument')
    
    def getInstrumentName(self, force=False):
        instr_name = self._getAttrValue('instrument', force=force)
        if len(instr_name) == 0: return instr_name
        instr_name = instr_name[:instr_name.index('(')]
        return instr_name
    
    def getInstrument(self):
        instr_name = self.getInstrumentName()
        if len(instr_name) == 0: return None
        return self.getPoolObj().getObj("Instrument", instr_name)
    

class Controller(BaseElement):
    """ Class encapsulating Controller functionality."""

    BaseReStr = '(?P<_alias>\S+)\s+' \
                '\((?P<_module>[^\.]+)\.(?P<_klass>[^/]+)/(?P<_inst>[^\)]+)\)\s+-\s+(?P<_type>\w+)'
    BaseRe = re.compile(BaseReStr)

    # The basic string representation for the MacroServer attribute
    SimpleReprStr = '%(_alias)s'
    
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self._str_tuple = self.getName(), self.getType(), self.getClassName(), self.getModuleName()
        
    @classmethod
    def match(cls, s):
        r = cls.BaseRe.match(s)
        if r:
            r = r.groupdict()
            r['_id'] = "%(_module)s.%(_klass)s/%(_inst)s" % r
        return r

#    def getControllerName(self):
#        return self._alias
    
#    def getAxis(self):
#        return '-'

    def getModuleName(self):
        return self._module
    
    def getClassName(self):
        return self._klass
    
    def getType(self):
        return self._type
    
    def __cmp__(self, o):
        return cmp(self._id, o._id)


class ComChannel(PoolElement):
    """ Class encapsulating CommunicationChannel functionality."""
    pass


class ExpChannel(PoolElement):
    """ Class encapsulating ExpChannel functionality."""
    pass


class CTExpChannel(ExpChannel):
    """ Class encapsulating CTExpChannel functionality."""
    pass


class ZeroDExpChannel(ExpChannel):
    """ Class encapsulating ZeroDExpChannel functionality."""
    pass


class OneDExpChannel(ExpChannel):
    """ Class encapsulating OneDExpChannel functionality."""
    pass


class TwoDExpChannel(ExpChannel):
    """ Class encapsulating TwoDExpChannel functionality."""
    pass


class PseudoCounter(ExpChannel):
    """ Class encapsulating PseudoCounter functionality."""
    pass


class Motor(PoolElement, motion.Moveable):
    """ Class encapsulating Motor functionality."""

    def __init__(self, name, **kw):
        """PoolElement initialization."""
        self.call__init__(PoolElement, name, **kw)
        self.call__init__(motion.Moveable)

    def getPosition(self, force=False):
        return self._getAttrValue('position', force=force)

    def getDialPosition(self):
        return self._getAttrValue('dialposition', force=True)
    
    def getVelocity(self):
        return self._getAttrValue('velocity', force=True)

    def getAcceleration(self):
        return self._getAttrValue('acceleration', force=True)

    def getDeceleration(self):
        return self._getAttrValue('deceleration', force=True)
    
    def getBaseRate(self):
        return self._getAttrValue('base_rate', force=True)

    def getBacklash(self):
        return self._getAttrValue('backlash', force=True)

    def getLimitSwitches(self):
        return self._getAttrValue('limit_switches', force=True)
    
    def getOffset(self):
        return self._getAttrValue('offset', force=True)
    
    def getStepPerUnit(self):
        return self._getAttrValue('step_per_unit', force=True)
    
    def getSign(self):
        return self._getAttrValue('Sign', force=True)
    
    def getSimulationMode(self):
        return self._getAttrValue('SimulationMode', force=True)

    def getPositionObj(self):
        return self._getAttrEx('position')

    def getDialPositionObj(self):
        return self._getAttrEx('dialposition')

    def getVelocityObj(self):
        return self._getAttrEx('velocity')

    def getAccelerationObj(self):
        return self._getAttrEx('acceleration')

    def getDecelerationObj(self):
        return self._getAttrEx('deceleration')
    
    def getBaseRateObj(self):
        return self._getAttrEx('base_rate')

    def getBacklashObj(self):
        return self._getAttrEx('backlash')

    def getLimitSwitchesObj(self):
        return self._getAttrEx('limit_switches')
    
    def getOffsetObj(self):
        return self._getAttrEx('offset')
    
    def getStepPerUnitObj(self):
        return self._getAttrEx('step_per_unit')
    
    def getSimulationModeObj(self):
        return self._getAttrEx('step_per_unit')

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Moveable interface
    #
    
    @reservedOperation
    def startMove(self, new_pos, timeout=None):
        new_pos = new_pos[0]
        evt_wait = self._getEventWait()
        evt_wait.connect(self.getAttribute("state"))
        evt_wait.lock()
        try:
            evt_wait.waitEvent(PyTango.DevState.MOVING, equal=False)
            ts1 = time.time()
            try:
                self.getPositionObj().write(new_pos)
            except PyTango.DevFailed, df:
                for err in df:
                    if err.reason == 'API_AttrNotAllowed':
                        raise RuntimeError('%s is already moving' % self)
                    else:
                        raise
            self.final_pos = new_pos
            ts2 = time.time()
            # putting timeout=0.1 and retries=1 is a patch for the case the when the initial
            # moving event doesn't arrive due to an unknow tango/pytango error at the time
            evt_wait.waitEvent(PyTango.DevState.MOVING, after=ts1, timeout=0.1, retries=1)
        except Exception,e:
            evt_wait.disconnect()
            raise e
        finally:
            evt_wait.unlock()
        ts2 = evt_wait.getRecordedEvents().get(PyTango.DevState.MOVING, ts2)
        return (ts2,)
    
    @reservedOperation
    def waitMove(self, timeout=None, id=None):
        if id is not None:
            id = id[0]
        evt_wait = self._getEventWait()
        evt_wait.lock()
        try:
            evt_wait.waitEvent(PyTango.DevState.MOVING, after=id, equal=False, timeout=timeout)
        finally:
            evt_wait.unlock()
            evt_wait.disconnect()
    
    @reservedOperation
    def move(self, new_pos, timeout=None):
        if not operator.isSequenceType(new_pos):
            new_pos = (new_pos,)
        self.waitMove(id=self.startMove(new_pos))
        return self.getStateExObj().readValue(), self.readPosition()
    
    @reservedOperation
    def iterMove(self, new_pos, timeout=None):
        if operator.isSequenceType(new_pos):
            new_pos = new_pos[0]
        state, pos = self.getAttribute("state"), self.getAttribute("position")

        evt_wait = self._getEventWait()
        evt_wait.connect(state)
        evt_wait.lock()
        try:
            evt_wait.waitEvent(PyTango.DevState.MOVING, equal=False)
            time_stamp = time.time()
            try:
                self.getPositionObj().write(new_pos)
            except PyTango.DevFailed, err_traceback:
                for err in err_traceback:
                    if err.reason == 'API_AttrNotAllowed':
                        raise RuntimeError, '%s is already moving' % self
                    else:
                        raise
            self.final_pos = new_pos
            # putting timeout=0.1 and retries=1 is a patch for the case the when the initial
            # moving event doesn't arrive do to an unknow tango/pytango error at the time
            evt_wait.waitEvent(PyTango.DevState.MOVING, time_stamp, timeout=0.1, retries=1)
        finally:
            evt_wait.unlock()
            evt_wait.disconnect()
        
        evt_iter_wait = taurus.core.util.AttributeEventIterator(state, pos)
        evt_iter_wait.lock()
        try:
            for evt_data in evt_iter_wait.events():
                src, value = evt_data
                if src == state and value != PyTango.DevState.MOVING:
                    raise StopIteration
                yield value
        finally:
            evt_iter_wait.unlock()
            evt_iter_wait.disconnect()
    
    def abort(self, wait_ready=True, timeout=None):
        state = self.getStateExObj()
        state.lock()
        try:
            if state.readValue() == Moving:
                self.command_inout("Abort")
            if wait_ready:
                self.waitReady(timeout=timeout)
        finally:
            state.unlock()
    
    def readPosition(self, force=False):
        return [ self.getPosition(force=force) ]
    
    def getMoveableSource(self):
        return self.getPoolObj()

    def getSize(self):
        return 1
    
    def getIndex(self, name):
        if name.lower() == self._name_lower:
            return 0
        return -1
    #
    # End of Moveable interface
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-


class PseudoMotor(PoolElement, motion.Moveable):
    """ Class encapsulating PseudoMotor functionality."""

    def __init__(self, name, **kw):
        """PoolElement initialization."""
        self.call__init__(PoolElement, name, **kw)
        self.call__init__(motion.Moveable)

    def getPosition(self, force=False):
        return self._getAttrValue('position', force=force)

    def getDialPosition(self, force=False):
        return self.getPosition(force=force)

    def getPositionObj(self):
        return self._getAttrEx('position')

    def getDialPositionObj(self):
        return self.getPositionObj()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Moveable interface
    #

    @reservedOperation
    def startMove(self, new_pos, timeout=None):
        new_pos = new_pos[0]
        evt_wait = self._getEventWait()
        evt_wait.connect(self.getAttribute("state"))
        evt_wait.lock()
        try:
            evt_wait.waitEvent(PyTango.DevState.MOVING, equal=False)
            ts1 = time.time()
            try:
                self.getPositionObj().write(new_pos)
            except PyTango.DevFailed, df:
                for err in df:
                    if err.reason == 'API_AttrNotAllowed':
                        raise RuntimeError('%s is already moving' % self)
                    else:
                        raise
            self.final_pos = new_pos
            ts2 = time.time()
            # putting timeout=0.1 and retries=1 is a patch for the case the when the initial
            # moving event doesn't arrive due to an unknow tango/pytango error at the time
            evt_wait.waitEvent(PyTango.DevState.MOVING, after=ts1, timeout=0.1, retries=1)
        except Exception,e:
            evt_wait.disconnect()
            raise e
        finally:
            evt_wait.unlock()
        ts2 = evt_wait.getRecordedEvents().get(PyTango.DevState.MOVING, ts2)
        return (ts2,)
    
    @reservedOperation
    def waitMove(self, timeout=None, id=None):
        if id is not None:
            id = id[0]
        evt_wait = self._getEventWait()
        evt_wait.lock()
        try:
            evt_wait.waitEvent(PyTango.DevState.MOVING, id, equal=False)
        finally:
            evt_wait.unlock()
            evt_wait.disconnect()
    
    @reservedOperation
    def move(self, new_pos, timeout=None):
        self.waitMove(id=self.startMove(new_pos))
        return self.getStateExObj().readValue(), self.readPosition()
    
    def abort(self, wait_ready=True, timeout=None):
        state = self.getStateExObj()
        state.lock()
        try:
            if state.readValue() == Moving:
                self.command_inout('Abort')
            if wait_ready:
                self.waitReady(timeout=timeout)
        finally:
            state.unlock()

    def readPosition(self, force=False):
        return [ self.getPosition(force=force) ]
    
    def getMoveableSource(self):
        return self.getPoolObj()

    def getSize(self):
        return 1
    
    def getIndex(self, name):
        if name.lower() == self._name_lower:
            return 0
        return -1
    #
    # End of Moveable interface
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

class MotorGroup(PoolElement, motion.Moveable):
    """ Class encapsulating MotorGroup functionality."""

    BaseReStr    = PoolElement.CommonReStr + \
                   'Motor list:\s+(?P<_user_name_list>.+)\s+\((?P<_hw_name_list>.+)\)'

    # The compiled regular expression to parse from the pool
    BaseRe       = re.compile(BaseReStr)

    def __init__(self, name, **kw):
        """PoolElement initialization."""
        self.call__init__(PoolElement, name, **kw)
        self.call__init__(motion.Moveable)
        groups = self.BaseRe.match(self._full_pool_name).groupdict()
        self._user_name_list = [ e.strip() for e in groups.get('_user_name_list').split(',') ]
        self._hw_name_list = [ e.strip() for e in groups.get('_hw_name_list').split(',') ]

        # user name list lower case cache. For performance reasons.
        self._user_name_list_l = [ e.lower() for e in self._user_name_list ]
    
    def getMotorNames(self):
        return self._user_name_list
    
    def hasMotor(self, name):
        return name.lower() in self._user_name_list_l
    
    def getPosition(self, force=False):
        return self._getAttrValue('position', force=force)

    def getPositionObj(self):
        return self._getAttrEx('position')

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Moveable interface
    #

    @reservedOperation
    def startMove(self, new_pos, timeout=None):
        evt_wait = self._getEventWait()
        evt_wait.connect(self.getAttribute("state"))
        evt_wait.lock()
        try:
            evt_wait.waitEvent(PyTango.DevState.MOVING, equal=False)
            ts1 = time.time()
            try:
                self.getPositionObj().write(new_pos)
            except PyTango.DevFailed, df:
                for err in df:
                    if err.reason == 'API_AttrNotAllowed':
                        raise RuntimeError('%s is already moving' % self)
                    else:
                        raise
            self.final_pos = new_pos
            ts2 = time.time()
            # putting timeout=0.1 and retries=1 is a patch for the case the when the initial
            # moving event doesn't arrive due to an unknow tango/pytango error at the time
            evt_wait.waitEvent(PyTango.DevState.MOVING, after=ts1, timeout=0.1, retries=1)
        except Exception,e:
            evt_wait.disconnect()
            raise e
        finally:
            evt_wait.unlock()
        ts2 = evt_wait.getRecordedEvents().get(PyTango.DevState.MOVING, ts2)
        return (ts2,)
    
    
    @reservedOperation
    def waitMove(self, timeout=None, id=None):
        if id is not None:
            id = id[0]
        evt_wait = self._getEventWait()
        evt_wait.lock()
        try:
            evt_wait.waitEvent(PyTango.DevState.MOVING, id, equal=False)
        finally:
            evt_wait.unlock()
            evt_wait.disconnect()
    
    @reservedOperation
    def move(self, new_pos, timeout=None):
        self.waitMove(id=self.startMove(new_pos))
        return self.getStateExObj().readValue(), self.readPosition()
    
    def abort(self, wait_ready=True, timeout=None):
        state = self.getStateExObj()
        state.lock()
        try:
            if state.readValue() == Moving:
                self.command_inout('Abort')
            if wait_ready:
                self.waitReady(timeout=timeout)
        finally:
            state.unlock()

    def readPosition(self, force=False):
        return self.getPosition(force=force)
    
    def getMoveableSource(self):
        return self.getPoolObj()

    def getSize(self):
        return len(self._user_name_list)
    
    def getIndex(self, name):
        try:
            return self._user_name_list_l.index(name.lower())
        except:
            return -1
    
    #
    # End of Moveable interface
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    
    
    
class MeasurementGroup(PoolElement):
    """ Class encapsulating MeasurementGroup functionality."""
    # The regular expression string to parse from the pool
    BaseReStr    = PoolElement.CommonReStr + \
                   'ExpChannel list:\s+(?P<_user_name_list>.+)\s+\((?P<_hw_name_list>.+)\)'

    # The compiled regular expression to parse from the pool
    BaseRe       = re.compile(BaseReStr)

    def __init__(self, name, **kw):
        """PoolElement initialization."""
        self.call__init__(PoolElement, name, **kw)

        self._user_0d_name_list_l = map(str.lower, self.read_attribute('ZeroDExpChannels').value or () )

        self._createAttributes()
        
        groups = self.BaseRe.match(self._full_pool_name).groupdict()
        self._user_name_list = [ e.strip() for e in groups.get('_user_name_list').split(',') ]
        self._hw_name_list = [ e.strip() for e in groups.get('_hw_name_list').split(',') ]
        self._channel_attrex_list = self._getChannelsAttrEx()

        # user name list lower case cache. For performance reasons.
        self._user_name_list_l = map(str.lower, self._user_name_list)

        self._str_tuple = [self.getName(), self.getTimer(), ' ,'.join(self.getCounterNames())]
        
        timer_ch = self._getAttrEx('timer')
        timer_ch.subscribeEvent(self.timerChanged)
        
    def timerChanged(self, obj, data):
        self._str_tuple[1] = data
        
    def _createAttributes(self):
        attrs = self.attribute_list_query_ex()
        
        for attr in attrs:
            
            name = attr.name
            name_lower = name.lower()
            if name_lower == 'state':
                name = 'StateEx'
                name_lower = name.lower()
                attrObj = self.getAttribute(attr.name)
            # Workaround for 0Ds while the measurement group 0d attribute doesn't 
            # send events: we read the attribute 'cumulatedvalue' from the 0D device
            # instead of the corresponding attribute in the measurement group
            #elif name_lower.endswith('_value') and \
            #     name_lower[:name_lower.rfind('_value')] in self._user_0d_name_list_l:
            #    n = name_lower[:name_lower.rfind('_value')]
            #    attrObj = taurus.Attribute(n,'CumulatedValue')
            else:
                attrObj = self.getAttribute(attr.name)
            if attrObj is None:
                self.warning("Unable to create attribute %s" % name)
            self._attr_obj[name] = attrObj
            self._attr_obj_ex[name] = TangoAttributeEG(attrObj)

    def _getChannelsAttrEx(self):
        """Returns a sequence of TangoAttributeEG objects, one for each channel
        in this measurement group"""
        return [ self._attr_obj_ex.get('%s_value' % c) for c in self._user_name_list ]

    def getChannelObj(self, name):
        """Returns a TangoDevice subclass object corresponding to the 
        channel name"""
        return self.getPoolObj().getObj('ExpChannel', name)
    
    def getChannelObjs(self):
        """Returns a sequence of TangoDevice subclass objects corresponding to
        this measurement group channels"""
        return [ self.getChannelObj(n) for n in self._user_name_list ]
    
    def getChannelAttrExs(self):
        return self._channel_attrex_list

    def getChannelNames(self):
        return self._user_name_list
    
    def getCounterNames(self):
        t = self.getTimer()
        if t is None:
            # it was not possible to read the Timer: all channels are counters
            return copy.copy(self.getChannelNames())
        t = t.lower()
        return [ e for e in self._user_name_list if e.lower() != t ]

    def getCounterAttrs(self):
        """Returns a sequence of taurus.core.TangoAttribute objects, one for each
        channel in this measurement group"""
        ret, t = [], self.getTimer()
        if t: t = t.lower()
        for k, v in self._attr_obj.iteritems():
            k = k.lower()
            if k == t: continue
            if k.endswith('_value'):
                ret.append(v)
        return ret

    def getChannelAttrs(self):
        """Returns a sequence of taurus.core.TangoAttribute objects, one for each
        channel in this measurement group"""
        return [ v for k, v in self._attr_obj.iteritems() if k.lower().endswith('_value') ]
    
    def getValue(self, name):
        return self.getAttrExObj(name).readValue()

    def setTimer(self, timer_name):
        timer_name_l = timer_name.lower()
        if not timer_name_l in self._user_name_list_l:
            raise Exception("%s does not contain a channel named '%s'" % (str(self),timer_name))
        self.getTimerObj().write(timer_name)

    def getTimer(self):
        return self._getAttrValue('timer')

    def getTimerObj(self):
        return self._getAttrEx('timer')

    def getTimerValue(self):
        t = self.getTimer()
        if t is None:
            return None
        return self.getAttrExObj(t).readValue()

    def getValues(self, force=False):
        #if force:
        #    return self.getValuesFromHW()
        ret = {}
        nan = float('NAN')
        
        for ch_name in self.getChannelNames():
            ch_attr = self.getAttrExObj("%s_value" % ch_name)
            try:
                ch_value = ch_attr.readValue(force=force)
            except Exception, e:
                self.debug("Failed to read '%s': %s" % (ch_name, str(e)))
                ch_value = None
            if ch_value is None: ch_value = nan
            ret[ch_name] = ch_value
        return ret

    def getValuesFromHW(self):
        pass

    def getIntegrationTime(self):
        return self._getAttrValue('integration_time')

    def getIntegrationTimeObj(self):
        return self._getAttrEx('integration_time')

    def setIntegrationTime(self, ctime):
        if self.getIntegrationTime() != ctime:
            self.getIntegrationTimeObj().write(ctime)
    
    @reservedOperation
    def startCount(self, timeout=None):
        state = self.getStateExObj()
        state.lock()
        try:
            try:
                self.Start()
                state.waitEvent(Counting, timeout=timeout)
            except PyTango.DevFailed:
                raise
        finally:
            state.unlock()

    @reservedOperation
    def waitCount(self, timeout=None):
        return self.getStateExObj().waitEvent(Counting, equal=False, timeout=timeout)

    @reservedOperation
    def count(self, duration=None, timeout=None):
        if duration is None or duration == 0:
            return self.getStateExObj().readValue(), self.getValues(force=True)
        
        self.setIntegrationTime(duration)

        evt_wait = self._getEventWait()
        evt_wait.connect(self.getAttribute("state"))
        try:
            evt_wait.lock()
            evt_wait.waitEvent(Counting, equal=False)
            time_stamp = time.time()
            self.Start()
            evt_wait.waitEvent(Counting, time_stamp)
            evt_wait.waitEvent(Counting, time_stamp, equal=False)
        finally:
            evt_wait.unlock()
            evt_wait.disconnect()
        return self.getStateExObj().readValue(), self.getValues(force=True)

    def stopCount(self, timeout=None):
        state = self.getStateExObj()
        state.lock()
        try:
            if state.readValue() == Counting:
                self.command_inout('Abort')
                self.waitCount(timeout=timeout)
        finally:
            state.unlock()

    def abort(self, wait_ready=True, timeout=None):
        self.stopCount(timeout=timeout)
        #PoolElement.Abort(self, wait_ready, timeout)
        

class IORegister(PoolElement):
    """ Class encapsulating IORegister functionality."""

    def __init__(self, name, **kw):
        """IORegister initialization."""
        self.call__init__(PoolElement, name, **kw)

    def getValueObj(self):
        return self._getAttrEx('value')
    
    def readValue(self, force=False):
        return self._getAttrValue('value', force=force)
    
    def startWriteValue(self, new_value, timeout=None):
        try:
            self.getValueObj().write(new_value)
            self.final_val = new_value
        except PyTango.DevFailed, err_traceback:
            for err in err_traceback:
                if err.reason == 'API_AttrNotAllowed':
                    raise RuntimeError, '%s is already chaging' % self
                else:
                    raise
    
    def waitWriteValue(self, timeout=None):
        pass
    
    def writeValue(self, new_value, timeout=None):
        self.startWriteValue(new_value, timeout=timeout)
        self.waitWriteValue(timeout=timeout)
        return self.getStateExObj().readValue(), self.readValue()

    writeIORegister = writeIOR = writeValue
    readIORegister = readIOR = getValue = readValue


class Instrument(BaseElement):

    BaseReStr = '(?P<_alias>.+)\((?P<_type>\w+)\)'
    
    # The compiled regular expression to parse from the pool
    BaseRe       = re.compile(BaseReStr)

    # The string representation for the MacroServer attribute
    ReprStr   = '%(_alias)s (%(_id)s) (%(_type)s) [%(_pool)s]'

    # The basic string representation for the MacroServer attribute
    SimpleReprStr = '%(_alias)s'
    
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self._id = self._alias
        self._simp_name = self._alias
        self._elements = []
        self._parent = None
        self._parent_name = ""
        self._children = []
        self._name_lower = self.getName().lower()
        self._buildInfo()
    
    def _buildInfo(self):
        if self._id.count('/') > 1:
            self._parent_name = self._id[:self._id.rindex('/')]
            self._parent = self.getPoolObj().getObj('Instrument', self._parent_name)
            if self._parent is not None:
                self._parent._children.append(self)
                
        self._str_tuple = self.getName(), self.getType(), self.getParentInstrumentName()
    
    def getFullName(self):
        return self._id
    
    def getParentInstrument(self):
        return self._parent

    def getParentInstrumentName(self):
        return self._parent_name
    
    def getChildrenInstruments(self):
        return self._children
    
    def getElements(self):
        return self._elements

    def getType(self):
        return self._type
    

HardwareObjNames   = [
    'ExpChannel', 'ComChannel', 'Motor',
    'IORegister', 'MotorGroup', 'MeasurementGroup']

HardwareObjTypeNames   = [
    'ComChannel', 'Motor', 'PseudoMotor',  
    'CTExpChannel','ZeroDExpChannel','OneDExpChannel', 'TwoDExpChannel', 
    'PseudoCounter', 'IORegister', 'MotorGroup', 'MeasurementGroup']
HardwareObjTypeClasses = [globals()[x] for x in HardwareObjTypeNames]

SoftwareObjNames   = ['ControllerClass', 'Controller', 'Instrument']


class Pool(taurus.core.tango.TangoDevice, motion.MoveableSource):
    """ Class encapsulating device Pool functionality."""

    SoftwareObjMap = [ (name, globals()[name]) for name in SoftwareObjNames ]
    HardwareObjMap = [ (name, globals()[name]) for name in HardwareObjNames ]
    HardwareObjTypeMap = [ (name, globals()[name]) for name in HardwareObjTypeNames ]
    
    def __init__(self, name, **kw):
        # dict<TangoAttribute, string>
        # key : A tango attribute object
        # value : the name of the attribute
        self._attr_dict = {}
        
        # dict<string, HardwareObjList>
        # key : the hardware object name
        # value : the Hardware object list object
        self._obj_dict = taurus.core.util.CaselessDict()
        
        self.call__init__(taurus.core.tango.TangoDevice, name, **kw)
        self.call__init__(motion.MoveableSource)
        
        for name, obj_class in self.SoftwareObjMap:
            attr_name = "%sList" % name
            attr = self._createAttribute(attr_name)
            self._attr_dict[attr] = attr_name
            sw_obj_list = SoftwareObjList(self, name, obj_class, attr)
            self._obj_dict[name] = sw_obj_list

        for name, obj_class in self.HardwareObjMap:
            attr_name = "%sList" % name
            attr = self._createAttribute(attr_name)
            self._attr_dict[attr] = attr_name
            hw_obj_list = HardwareObjList(self, name, obj_class, attr)
            self._obj_dict[name] = hw_obj_list

    def _createAttribute(self, attr_name):
        attr_name = "%s/%s" % (self.getFullName(), attr_name)
        return self.factory().getAttribute(attr_name)

    def hasListObj(self, name):
        return self._obj_dict.has_key(name)

    def getListObj(self, name):
        return self._obj_dict.get(name, None)

    def getObj(self, type, name):
        list_obj = self.getListObj(type)
        if list_obj is None:
            return
        return list_obj.getObjByName(name)
    
    def __repr__(self):
        return self.getNormalName()

    def __str__(self):
        return repr(self)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # MoveableSource interface
    #    
    
    def getMoveable(self, names):
        """getMoveable(list<string> names) -> Moveable 

        Returns a moveable object that handles all the moveable items given in 
        names."""        
        # if simple motor just return it (if the pool has it)
        if len(names) == 1:
            name = names[0]
            return self.getObj('Motor',name) or self.getObj('MotorGroup',name)
        
        # find a motor group that contains elements
        moveable = self.__findMotorGroupWithElems(names)
        
        # if none exists create one
        if moveable is None:
            name = "_mg_macserv_" + str(os.getpid()) + "_" + str(thread.get_ident()) 
            self.createMotorGroup(name, names)
            moveable = self.getObj('MotorGroup', name)
        return moveable
             
    def __findMotorGroupWithElems(self, names):
        mg_list = self.getListObj('MotorGroup')
        len_names = len(names)
        for mg in mg_list.getObjs():
            motor_names = mg.getMotorNames()
            if len_names == len(motor_names):
                found = True
                for name in names:
                    if not mg.hasMotor(name):
                        found = False
                        break;
                if found:
                    return mg
        return None
    #
    # End of MoveableSource interface
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def createMotorGroup(self, name, elements):
        params = [name,] + map(str, elements)
        self.debug('trying to create motor group: %s', params)
        self.command_inout('CreateMotorGroup', params)
        mg_list = self.getListObj('MotorGroup')
        mg_list.waitEvent(any=True)
    
    def createMeasurementGroup(self, name, elements):
        params = [name,] + map(str,elements)
        self.debug('trying to create measurement group: %s', params)
        self.command_inout('CreateMeasurementGroup', params)


def registerExtensions():
    import taurus
    factory = taurus.Factory()
    factory.registerDeviceClass("Pool", Pool)
    for klass_name, klass in Pool.HardwareObjTypeMap:
        factory.registerDeviceClass(klass_name, klass)

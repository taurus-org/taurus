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

__all__ = ["AbortException", "BaseElement", "ControllerClass",
           "PoolElement", "Controller", "ComChannel", "ExpChannel",
           "CTExpChannel", "ZeroDExpChannel", "OneDExpChannel", "TwoDExpChannel",
           "PseudoCounter", "Motor", "PseudoMotor", "MotorGroup",
           "MeasurementGroup", "IORegister", "Instrument", "Pool",
           "registerExtensions"]

__docformat__ = 'restructuredtext'

import sys
import os
import weakref
import re
import thread
import time
import operator
import json

from PyTango import DevState, AttrDataFormat, DevFailed, \
    DeviceProxy, AttributeProxy

from taurus import Factory
from taurus.core import TaurusEventType, AttributeNameValidator
from taurus.core.util import Logger, CaselessDict, CodecFactory, \
    EventGenerator, AttributeEventWait, AttributeEventIterator
from taurus.core.tango import TangoDevice, FROM_TANGO_TO_STR_TYPE

from sardana import BaseSardanaElementContainer, BaseSardanaElement
from motion import Moveable, MoveableSource

Ready = Standby = DevState.ON
Counting = Acquiring = Moving = DevState.MOVING
Alarm = DevState.ALARM
Fault = DevState.FAULT

CHANGE_EVT_TYPES = TaurusEventType.Change, TaurusEventType.Periodic

MOVEABLE_TYPES = 'Motor', 'PseudoMotor', 'MotorGroup'

class AbortException(Exception):
    pass

class BaseElement(object):
    """ The base class for elements in the Pool (Pool itself, Motor, 
    ControllerClass, ExpChannel all should inherit from this class directly or
    indirectly) 

    - At the object level:
      self._name_lower - the lower case string name of the object (used for 
                         __cmp__)
      self._full_pool_name - the original string coming from the Pool
      self._pool - the pool object
    """
    
    def __repr__(self):
        pd = self._pool_data
        return "{0}({1})".format(pd['type'], pd['full_name'])
    
    def __str__(self):
        return self.getName()
    
    def to_json(self):
        return self._pool_data
    
    def str(self, n=0):
        """Returns a sequence of strings representing the object in 'consistent'
        way. Default is to return <name>, <controller name>, <axis>
        
        :param n: the number of elements in the tuple."""
        if n == 0:
            return json.dumps(self.to_json())
        return self._str_tuple[:n]
    
    def __cmp__(self,o):
        return cmp(self._name_lower, o._name_lower)
    
    def getName(self):
        return self._pool_data['name']

    def getPoolObj(self):
        return self._pool


class ControllerClass(BaseElement):
    
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self._name_lower = self.name
        self.path, self.fname = os.path.split(self.filename)
        self.libname, self.ext = os.path.splitext(self.fname)
        
        self._str_tuple = self.getName(), self.getType(), self.getLib(), self.getGender()

    def __repr__(self):
        pd = self._pool_data
        return "ControllerClass({0})".format(pd['full_name'])
        
    def getSimpleFileName(self):
        return self.fname

    def getFileName(self):
        return self.filename

    def getClassName(self):
        return self.getName()
    
    def getType(self):
        return self.getTypes()[0]

    def getTypes(self):
        return self.type

    def getLib(self):
        return self.fname
    
    def getGender(self):
        return self.gender
    
    def getModel(self):
        return self.model
    
    def getOrganization(self):
        return self.organization

    def __cmp__(self, o):
        t = cmp(self.getType(), o.getType())
        if t != 0: return t
        t = cmp(self.getGender(), o.getGender())
        if t != 0: return t
        return cmp(self.getClassName(), o.getClassName())


class ControllerLib(BaseElement):
    
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self._name_lower = self.name

    def getType(self):
        return self.getTypes()[0]

    def getTypes(self):
        return self.type


class TangoAttributeEG(Logger, EventGenerator):
    """An event generator for a 'State' attribute"""
    
    def __init__(self, attr):
        self._attr = attr
        self.call__init__(Logger, 'EG', attr)
        event_name = '%s EG' % (attr.getParentObj().getNormalName())
        self.call__init__(EventGenerator, event_name)

        self._attr.addListener(self)
    
    def getAttribute(self):
        return self._attr
    
    def eventReceived(self, evt_src, evt_type, evt_value):
        """Event handler from Taurus"""
        if evt_type not in CHANGE_EVT_TYPES:
            return
        if evt_value is None:
            v = None
        else:
            v = evt_value.value
        EventGenerator.fireEvent(self, v)

    def read(self, force=False):
        try:
            self.last_val = self._attr.read(cache=not force).value
        except:
            self.last_val = None
        return EventGenerator.read(self)
    
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


class PoolElement(BaseElement, TangoDevice):
    """Base class for a Pool element device."""
    
    def __init__(self, name, **kw):
        """PoolElement initialization."""
        self._reserved = None
        self.call__init__(TangoDevice, name, **kw)
        self._name_lower = self.getName().lower()
        
        # dict<string, TangoAttributeEG>
        # key : the attribute name
        # value : the corresponding TangoAttributeEG 
        self._attrEG = CaselessDict()
                
        # force the creation of a state attribute
        self.getStateEG()

        self._str_tuple = self._create_str_tuple()

    def _create_str_tuple(self):
        return self.getName(), self.getType(), self.getControllerName(), self.getAxis()

    def cleanUp(self):
        TangoDevice.cleanUp(self)
        self._reserved = None
        f = self.factory()
        
        attr_map = self._attrEG
        for attr_name in attr_map.keys():
            attrEG = attr_map.pop(attr_name)
            attr = attrEG.getAttribute()
            attrEG = None
            f.removeExistingAttribute(attr)
        
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
        attrEG = self._getAttrEG(name)
        if attrEG is None: return None
        return attrEG.readValue(force=force)
    
    def _getAttrEG(self, name):
        attrEG = self.getAttrEG(name)
        if attrEG is None:
            attrEG = self._createAttribute(name)
        return attrEG
    
    def _createAttribute(self, name):
        attrObj = self.getAttribute(name)
        if attrObj is None:
            self.warning("Unable to create attribute %s" % name)
            return None, None
        attrEG = TangoAttributeEG(attrObj)
        self._attrEG[name] = attrEG
        return attrEG
    
    def _getEventWait(self):
        if not hasattr(self, '_evt_wait'):
            # create an object that waits for attribute events.
            # each time we use it we have to connect and disconnect to an attribute
            self._evt_wait = AttributeEventWait()
        return self._evt_wait
    
    def getStateEG(self):
        return self._getAttrEG('state')
    
    def __cmp__(self,o):
        return cmp(self._name_lower, o._name_lower)

    def getControllerName(self):
        return self._pool_data['controller']
    
    def getControllerObj(self):
        return self.getPoolObj().getObj("Controller", self.getControllerName())
    
    def getAxis(self):
        return self._pool_data['axis']

    def getType(self):
        return self._pool_data['type']

    def getPoolObj(self):
        return self._pool_obj

    def waitReady(self, timeout=None):
        return self.getStateEG().waitEvent(Moving, equal=False, timeout=timeout)

    def getAttrEG(self, name):
        """Returns the TangoAttributeEG object"""
        return self._attrEG.get(name)
    
    def getAttrObj(self, name):
        """Returns the taurus.core.TangoAttribute object"""
        attrEG = self._attrEG.get(name)
        if attrEG is None:
            return None
        return attrEG.getAttribute()

    def getInstrumentObj(self):
        return self._getAttrEG('instrument')
    
    def getInstrumentName(self, force=False):
        instr_name = self._getAttrValue('instrument', force=force)
        if len(instr_name) == 0: return instr_name
        #instr_name = instr_name[:instr_name.index('(')]
        return instr_name
    
    def getInstrument(self):
        instr_name = self.getInstrumentName()
        if len(instr_name) == 0: return None
        return self.getPoolObj().getObj("Instrument", instr_name)
    
    @reservedOperation
    def start(self, *args, **kwargs):
        evt_wait = self._getEventWait()
        evt_wait.connect(self.getAttribute("state"))
        evt_wait.lock()
        try:
            evt_wait.waitEvent(DevState.MOVING, equal=False)
            ts1 = time.time()
            self._start(*args, **kwargs)
            ts2 = time.time()
            evt_wait.waitEvent(DevState.MOVING, after=ts1)
        except:
            evt_wait.disconnect()
            raise
        finally:
            evt_wait.unlock()
        ts2 = evt_wait.getRecordedEvents().get(DevState.MOVING, ts2)
        return (ts2,)

    @reservedOperation
    def waitFinish(self, timeout=None, id=None):
        if id is not None:
            id = id[0]
        evt_wait = self._getEventWait()
        evt_wait.lock()
        try:
            evt_wait.waitEvent(DevState.MOVING, after=id, equal=False, timeout=timeout)
        finally:
            evt_wait.unlock()
            evt_wait.disconnect()

    @reservedOperation
    def go(self, *args, **kwargs):
        id = self.start(*args, **kwargs)
        self.waitFinish(id=id)

    def abort(self, wait_ready=True, timeout=None):
        state = self.getStateEG()
        state.lock()
        try:
            self.command_inout("Abort")
            if wait_ready:
                self.waitReady(timeout=timeout)
        finally:
            state.unlock()


class Controller(PoolElement):
    """ Class encapsulating Controller functionality."""

    def __init__(self, name, **kw):
        """PoolElement initialization."""
        self.call__init__(PoolElement, name, **kw)

    def _create_str_tuple(self):
        return self.getName(), self.getType(), self.getClassName(), self.getModuleName()

    def getModuleName(self):
        return self._pool_data['module']
    
    def getClassName(self):
        return self._pool_data['class']
    
    def addElement(self, elem):
        axis = elem.getAxis()
        self._elems[axis] = elem
        self._last_axis = max(self._last_axis, axis)
        
    def removeElement(self, elem):
        axis = elem.getAxis()
        del self._elems[elem.getAxis()]
        if axis == self._last_axis:
            self._last_axis = max(self._elems)
    
    def getElementByAxis(self, axis):
        pool = self.getPoolObj()
        lst = pool.getObjList(self.getType())
        for name, elem in lst.getObjNameDict().items():
            if elem.getAxis() != axis:
                continue
            if elem.getControllerName() != self.getName():
                continue
            return elem
    
    def getElementByName(self, name):
        pool = self.getPoolObj()
        lst = pool.getObjList(self.getType())
        for name, elem in lst.getObjNameDict().items():
            if elem.getName() != name:
                continue
            if elem.getControllerName() != self.getName():
                continue
            return elem
    
    def getUsedAxis(self):
        pool = self.getPoolObj()
        lst = pool.getObjList(self.getType())
        axis = []
        for name, elem in lst.getObjNameDict().items():
            if elem.getControllerName() != self.getName():
                continue
            axis.append(elem.getAxis())
        return sorted(axis)
    
    def getLastUsedAxis(self):
        return max(self.getUsedAxis())
    
    def __cmp__(self, o):
        return cmp(self.getName(), o.getName())


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


class Motor(PoolElement, Moveable):
    """ Class encapsulating Motor functionality."""

    def __init__(self, name, **kw):
        """PoolElement initialization."""
        self.call__init__(PoolElement, name, **kw)
        self.call__init__(Moveable)

    def getPosition(self, force=False):
        return self._getAttrValue('position', force=force)

    def getDialPosition(self, force=False):
        return self._getAttrValue('dialposition', force=force)
    
    def getVelocity(self, force=False):
        return self._getAttrValue('velocity', force=force)

    def getAcceleration(self, force=False):
        return self._getAttrValue('acceleration', force=force)

    def getDeceleration(self, force=False):
        return self._getAttrValue('deceleration', force=force)
    
    def getBaseRate(self, force=False):
        return self._getAttrValue('base_rate', force=force)

    def getBacklash(self, force=False):
        return self._getAttrValue('backlash', force=force)

    def getLimitSwitches(self, force=False):
        return self._getAttrValue('limit_switches', force=force)
    
    def getOffset(self, force=False):
        return self._getAttrValue('offset', force=force)
    
    def getStepPerUnit(self, force=False):
        return self._getAttrValue('step_per_unit', force=force)
    
    def getSign(self, force=False):
        return self._getAttrValue('Sign', force=force)
    
    def getSimulationMode(self, force=False):
        return self._getAttrValue('SimulationMode', force=force)

    def getPositionObj(self):
        return self._getAttrEG('position')

    def getDialPositionObj(self):
        return self._getAttrEG('dialposition')

    def getVelocityObj(self):
        return self._getAttrEG('velocity')

    def getAccelerationObj(self):
        return self._getAttrEG('acceleration')

    def getDecelerationObj(self):
        return self._getAttrEG('deceleration')
    
    def getBaseRateObj(self):
        return self._getAttrEG('base_rate')

    def getBacklashObj(self):
        return self._getAttrEG('backlash')

    def getLimitSwitchesObj(self):
        return self._getAttrEG('limit_switches')
    
    def getOffsetObj(self):
        return self._getAttrEG('offset')
    
    def getStepPerUnitObj(self):
        return self._getAttrEG('step_per_unit')
    
    def getSimulationModeObj(self):
        return self._getAttrEG('step_per_unit')

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Moveable interface
    #
    
    def _start(self, *args, **kwargs):
        new_pos = args[0]
        if operator.isSequenceType(new_pos):
           new_pos = new_pos[0]
        try:
            self.write_attribute('position', new_pos)
            #self.getPositionObj().write(new_pos)
        except DevFailed, df:
            for err in df:
                if err.reason == 'API_AttrNotAllowed':
                    raise RuntimeError('%s is already moving' % self)
                else:
                    raise
        self.final_pos = new_pos

    def go(self, *args, **kwargs):
        PoolElement.go(self, *args, **kwargs)
        return self.getStateEG().readValue(), self.readPosition()
        
    startMove = PoolElement.start
    waitMove = PoolElement.waitFinish    
    move = go    
    
    @reservedOperation
    def iterMove(self, new_pos, timeout=None):
        if operator.isSequenceType(new_pos):
            new_pos = new_pos[0]
        state, pos = self.getAttribute("state"), self.getAttribute("position")

        evt_wait = self._getEventWait()
        evt_wait.connect(state)
        evt_wait.lock()
        try:
            #evt_wait.waitEvent(DevState.MOVING, equal=False)
            time_stamp = time.time()
            try:
                self.getPositionObj().write(new_pos)
            except DevFailed, err_traceback:
                for err in err_traceback:
                    if err.reason == 'API_AttrNotAllowed':
                        raise RuntimeError, '%s is already moving' % self
                    else:
                        raise
            self.final_pos = new_pos
            # putting timeout=0.1 and retries=1 is a patch for the case the when the initial
            # moving event doesn't arrive do to an unknow tango/pytango error at the time
            evt_wait.waitEvent(DevState.MOVING, time_stamp, timeout=0.1, retries=1)
        finally:
            evt_wait.unlock()
            evt_wait.disconnect()
        
        evt_iter_wait = AttributeEventIterator(state, pos)
        evt_iter_wait.lock()
        try:
            for evt_data in evt_iter_wait.events():
                src, value = evt_data
                if src == state and value != DevState.MOVING:
                    raise StopIteration
                yield value
        finally:
            evt_iter_wait.unlock()
            evt_iter_wait.disconnect()
    
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


class PseudoMotor(PoolElement, Moveable):
    """ Class encapsulating PseudoMotor functionality."""

    def __init__(self, name, **kw):
        """PoolElement initialization."""
        self.call__init__(PoolElement, name, **kw)
        self.call__init__(Moveable)

    def getPosition(self, force=False):
        return self._getAttrValue('position', force=force)

    def getDialPosition(self, force=False):
        return self.getPosition(force=force)

    def getPositionObj(self):
        return self._getAttrEG('position')

    def getDialPositionObj(self):
        return self.getPositionObj()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Moveable interface
    #

    def _start(self, *args, **kwargs):
        new_pos = args[0]
        if operator.isSequenceType(new_pos):
           new_pos = new_pos[0]
        try:
            self.getPositionObj().write(new_pos)
        except DevFailed, df:
            for err in df:
                if err.reason == 'API_AttrNotAllowed':
                    raise RuntimeError('%s is already moving' % self)
                else:
                    raise
        self.final_pos = new_pos

    def go(self, *args, **kwargs):
        PoolElement.go(self, *args, **kwargs)
        return self.getStateEG().readValue(), self.readPosition()
        
    startMove = PoolElement.start
    waitMove = PoolElement.waitFinish    
    move = go   
    
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

class MotorGroup(PoolElement, Moveable):
    """ Class encapsulating MotorGroup functionality."""

    def __init__(self, name, **kw):
        """PoolElement initialization."""
        self.call__init__(PoolElement, name, **kw)
        self.call__init__(Moveable)

    def _create_str_tuple(self):
        return 3*["TODO"]
    
    def getMotorNames(self):
        return self._pool_data['elements']
    
    def hasMotor(self, name):
        motor_names = map(str.lower, self.getMotorNames())
        return name.lower() in motor_names
    
    def getPosition(self, force=False):
        return self._getAttrValue('position', force=force)

    def getPositionObj(self):
        return self._getAttrEG('position')

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Moveable interface
    #

    def _start(self, *args, **kwargs):
        new_pos = args[0]
        try:
            self.getPositionObj().write(new_pos)
        except DevFailed, df:
            for err in df:
                if err.reason == 'API_AttrNotAllowed':
                    raise RuntimeError('%s is already moving' % self)
                else:
                    raise
        self.final_pos = new_pos

    def go(self, *args, **kwargs):
        PoolElement.go(self, *args, **kwargs)
        return self.getStateEG().readValue(), self.readPosition()
        
    startMove = PoolElement.start
    waitMove = PoolElement.waitFinish
    move = go

    def readPosition(self, force=False):
        return self.getPosition(force=force)
    
    def getMoveableSource(self):
        return self.getPoolObj()

    def getSize(self):
        return len(self.getMotorNames())
    
    def getIndex(self, name):
        try:
            motor_names = map(str.lower, self.getMotorNames())
            return motor_names.index(name.lower())
        except:
            return -1
    
    #
    # End of Moveable interface
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    


class BaseChannelInfo(object):
    
    def __init__(self, data):
        # dict<str, obj>
        # channel data
        self.raw_data = data
        self.__dict__.update(data)


class TangoChannelInfo(BaseChannelInfo):
    
    def __init__(self, data, info):
        BaseChannelInfo.__init__(self, data)
        
        # PyTago.AttributeInfoEx
        self.raw_info = info
        
        self.data_type_str = FROM_TANGO_TO_STR_TYPE[self.data_type]
        
        shape = ()
        if info.data_format == AttrDataFormat.SPECTRUM:
            shape = (info.max_dim_x,)
        elif info.data_format == AttrDataFormat.IMAGE:
            shape = (info.max_dim_x, info.max_dim_y)
        self.shape = shape
        
    def __getattr__(self, name):
        return getattr(self.raw_info, name)


class MGConfiguration(object):
    
    def __init__(self, mg, data):
        self._mg = weakref.ref(mg)
        if isinstance(data, str):
            json_codec = CodecFactory().getCodec('json')
            _, data = json_codec.decode(('json', data), ensure_ascii=True)
        self.raw_data = data
        self.__dict__.update(data)
        
        # dict<str, dict>
        # where key is the channel name and value is the channel data in form
        # of a dict as receveid by the MG configuration attribute 
        self.channels = channels = CaselessDict()
        
        for ctrl_name, ctrl_data in self.controllers.items():
            for unit_id, unit_data in ctrl_data['units'].items():
                for channel_name, channel_data in unit_data['channels'].items():
                    data_source = channel_data['source']
                    channels[channel_name] = channel_data
        
        # seq<dict> each element is the channel data in form of a dict as
        # receveid by the MG configuration attribute. This seq is just a cache
        # ordered by channel index in the MG.
        self.channel_list = channel_list = len(channels)*[None]
        
        for channel in channels.values():
            self.channel_list[channel['index']] = channel

        # dict<str, list[DeviceProxy, CaselessDict<str, dict>]>
        # where key is a device name and value is a list with two elements:
        #  - A device proxy or None if there was an error building it
        #  - A dict where keys are attribute names and value is a reference to
        #    a dict representing channel data as received in raw data
        self.tango_dev_channels = None
        
        # Number of elements in tango_dev_channels in error (could not build 
        # DeviceProxy, probably)
        self.tango_dev_channels_in_error = 0
        
        # dict<str, tuple<str, str, TangoChannelInfo>>
        # where key is a channel name and value is a tuple of three elements:
        #  - device name
        #  - attribute name
        #  - attribute information or None if there was an error trying to get
        #    the information
        self.tango_channels_info = None

        # Number of elements in tango_channels_info_in_error in error
        # (could not build attribute info, probably)
        self.tango_channels_info_in_error = 0
        
        # dict<str, dict>
        # where key is a channel name and data is a reference to a dict
        # representing channel data as received in raw data
        self.non_tango_channels = None
        
        self.initialized = False
        
    def _build(self):
        # internal channel structure that groups channels by tango device so
        # they can be read as a group minimizing this way the network requests
        self.tango_dev_channels = tg_dev_chs = CaselessDict()
        self.tango_dev_channels_in_error = 0
        self.tango_channels_info = tg_chs_info = CaselessDict()
        self.tango_channels_info_in_error = 0
        self.non_tango_channels = n_tg_chs = CaselessDict()
        self.cache = cache = {}
        
        tg_attr_validator = AttributeNameValidator()
        for channel_name, channel_data in self.channels.items():
            cache[channel_name] = None
            data_source = channel_data['source']
            params = tg_attr_validator.getParams(data_source)
            if params is None:
                # Handle NON tango channel
                n_tg_chs[channel_name] = channel_data
            else:
                # Handle tango channel
                dev_name = params['devicename'].lower()
                attr_name = params['attributename'].lower()
                host, port = params.get('host'), params.get('port')
                if host is not None and port is not None:
                    dev_name = "{0}:{1}/{2}".format(host, port, dev_name)
                dev_data = tg_dev_chs.get(dev_name)
                
                if dev_data is None:
                    # Build tango device
                    dev = None
                    try:
                        dev = DeviceProxy(dev_name)
                    except:
                        self.tango_dev_channels_in_error += 1
                    tg_dev_chs[dev_name] = dev_data = [ dev, CaselessDict() ]
                dev, attr_data = dev_data
                attr_data[attr_name] = channel_data
                
                # get attribute configuration
                attr_info = None
                if dev is None:
                    self.tango_channels_info_in_error += 1
                else:
                    try:
                        tg_attr_info = dev.get_attribute_config_ex(attr_name)[0]
                        attr_info = TangoChannelInfo(channel_data, tg_attr_info)
                    except:
                        import traceback
                        traceback.print_exc()
                        self.tango_channels_info_in_error += 1
                tg_chs_info[channel_name] = dev_name, attr_name, attr_info
    
    def prepare(self):
        # first time? build everything
        if self.tango_dev_channels is None:
            return self._build()
        
        # prepare missing tango devices
        if self.tango_dev_channels_in_error > 0:
            for dev_name, dev_data in self.tango_dev_channels.items():
                if dev_data[0] is None:
                    try:
                        dev_data[0] = DeviceProxy(dev_name)
                        self.tango_dev_channels_in_error -= 1
                    except:
                        pass
        
        # prepare missing tango attribute configuration
        if self.tango_channels_info_in_error > 0:
            for channel_name, attr_data in self.tango_channels_info.items():
                dev_name, attr_name, attr_info = attr_data
                if attr_info is not None:
                    continue
                dev = self.tango_dev_channels[dev_name]
                if dev is None:
                    continue
                try:
                    tg_attr_info = dev.get_attribute_config_ex(attr_name)[0]
                    channel_data = self.channels[channel_name]
                    attr_info = attr_info = TangoChannelInfo(channel_data, tg_attr_info)
                    attr_data[2] = attr_info
                    self.tango_channels_info_in_error -= 1
                except:
                    continue
    
    def getChannelInfo(self, channel_name):
        return self.tango_channels_info[channel_name]
    
    def getChannelsInfo(self):
        self.prepare()
        return self.tango_channels_info
    
    def getChannelsInfoList(self):
        ch_info = self.getChannelsInfo()
        return [ ch_info[ch['name']][2] for ch in self.channel_list ]
    
    def getCountersInfoList(self):
        ch_info = self.getChannelsInfo()
        ret = []
        for ch in self.channel_list:
            ch_name = ch['name']
            if ch_name != self.timer:
                ret.append(ch_info[ch_name][2])
        return ret
    
    def read(self):
        ret = CaselessDict(self.cache)
        dev_replies = {}
        for dev_name, dev_data in self.tango_dev_channels.items():
            dev, attrs = dev_data
            if dev is None:
                continue
            try:
                dev_replies[dev] = dev.read_attributes_asynch(attrs.keys()), attrs
            except:
                continue
        for dev, reply_data in dev_replies.items():
            reply, attrs = reply_data
            try:
                data = dev.read_attributes_reply(reply, 0)
                for data_item in data:
                    channel_data = attrs[data_item.name]
                    if data_item.has_failed:
                        value = None
                    else:
                        value = data_item.value
                    ret[channel_data['name']] = value
            except:
                continue
        return ret


class MeasurementGroup(PoolElement):
    """ Class encapsulating MeasurementGroup functionality."""
    
    def __init__(self, name, **kw):
        """PoolElement initialization."""
        self._configuration = None
        self._channels = None
        self.call__init__(PoolElement, name, **kw)
        
        cfg_attr = self.getAttribute('configuration')
        cfg_attr.addListener(self.on_configuration_changed)

    def _create_str_tuple(self):
        return self.getName(), self.getTimerName(), ", ".join(self.getChannelNames())
 
    def getConfigurationAttrEG(self):
        return self._getAttrEG('Configuration')
    
    def setConfiguration(self, configuration):
        codec = CodecFactory().getCodec('json')
        data = codec.encode(configuration)
        self.write_attribute('configuration', data)
    
    def _setConfiguration(self, data):
        self._configuration = MGConfiguration(self, data)
        
    def getConfiguration(self, force=False):
        if force or self._configuration is None:
            data = self.getConfigurationAttrEG().readValue(force=True)
            self._setConfiguration(data)
        return self._configuration
    
    def on_configuration_changed(self, evt_src, evt_type, evt_value):
        if evt_type not in CHANGE_EVT_TYPES:
            return
        self._setConfiguration(evt_value.value)
    
    def getTimerName(self):
        return self.getConfiguration().timer
    
    def getTimer(self):
        cfg = self.getConfiguration()
        return cfg.channels[cfg.timer]

    def getTimerValue(self):
        return self.getTimerName()

    def getMonitorName(self):
        return self.getConfiguration().monitor

    def getMonitor(self):
        cfg = self.getConfiguration()
        return cfg.channels[cfg.monitor]

    def setTimer(self, timer_name):
        timer_name_l = timer_name.lower()
        if not timer_name_l in self._user_name_list_l:
            raise Exception("%s does not contain a channel named '%s'" % (str(self),timer_name))
        self.getTimerObj().write(timer_name)
    
    def getChannels(self):
        return self.getConfiguration().channel_list
    
    def getCounters(self):
        cfg = self.getConfiguration()
        return [ ch for ch in self.getChannels() if ch['name'] != cfg.timer ]
    
    def getChannelNames(self):
        return [ ch['name'] for ch in self.getChannels() ]
    
    def getCounterNames(self):
        cfg = self.getConfiguration()
        return [ ch['name'] for ch in self.getCounters() ]
    
    def getChannel(self, name):
        return self.getConfiguration().channels[name]
    
    def getChannelInfo(self, name):
        return self.getConfiguration().getChannelInfo(name)
    
    def getChannelsInfo(self):
        return self.getConfiguration().getChannelsInfoList()
    
    def getCountersInfo(self):
        return self.getConfiguration().getCountersInfoList()
    
    def getValues(self):
        return self.getConfiguration().read()
    
    def getIntegrationTime(self):
        return self._getAttrValue('IntegrationTime')
    
    def getIntegrationTimeObj(self):
        return self._getAttrEG('IntegrationTime')
    
    def setIntegrationTime(self, ctime):
        self.getIntegrationTimeObj().write(ctime)
    
    def _start(self, *args, **kwargs):
        self.Start()
    
    def go(self, *args, **kwargs):
        cfg = self.getConfiguration()
        cfg.prepare()
        duration = args[0]
        if duration is None or duration == 0:
            return self.getStateEG().readValue(), self.getValues()
        self.setIntegrationTime(duration)
        PoolElement.go(self, *args, **kwargs)
        return self.getStateEG().readValue(), self.getValues()
        
    startCount = PoolElement.start
    waitCount = PoolElement.waitFinish
    count = go
    stopCount = PoolElement.abort


class IORegister(PoolElement):
    """ Class encapsulating IORegister functionality."""

    def __init__(self, name, **kw):
        """IORegister initialization."""
        self.call__init__(PoolElement, name, **kw)

    def getValueObj(self):
        return self._getAttrEG('value')
    
    def readValue(self, force=False):
        return self._getAttrValue('value', force=force)
    
    def startWriteValue(self, new_value, timeout=None):
        try:
            self.getValueObj().write(new_value)
            self.final_val = new_value
        except DevFailed, err_traceback:
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
        return self.getStateEG().readValue(), self.readValue()

    writeIORegister = writeIOR = writeValue
    readIORegister = readIOR = getValue = readValue


class Instrument(BaseElement):
    
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self._name_lower = self.full_name.lower()
    
    def getFullName(self):
        return self.full_name
    
    def getParentInstrument(self):
        return self.getPoolObj().getObj(self.parent_instrument)

    def getParentInstrumentName(self):
        return self.parent_instrument
    
    def getChildrenInstruments(self):
        raise NotImplementedError
        return self._children
    
    def getElements(self):
        raise NotImplementedError
        return self._elements

    def getType(self):
        return self.klass

    def getPoolObj(self):
        return self._pool_obj

HardwareObjNames   = [
    'Controller',
    'ExpChannel', 'ComChannel', 'Motor',
    'IORegister', 'MotorGroup', 'MeasurementGroup']

HardwareObjTypeNames   = [
    'Controller',
    'ComChannel', 'Motor', 'PseudoMotor',
    'CTExpChannel','ZeroDExpChannel','OneDExpChannel', 'TwoDExpChannel',
    'PseudoCounter', 'IORegister', 'MotorGroup', 'MeasurementGroup']
HardwareObjTypeClasses = [globals()[x] for x in HardwareObjTypeNames]

SoftwareObjNames   = ['ControllerClass', 'Instrument']


class Pool(TangoDevice, MoveableSource):
    """ Class encapsulating device Pool functionality."""

    SoftwareObjMap = [ (name, globals()[name]) for name in SoftwareObjNames ]
    HardwareObjMap = [ (name, globals()[name]) for name in HardwareObjNames ]
    HardwareObjTypeMap = [ (name, globals()[name]) for name in HardwareObjTypeNames ]
    
    def __init__(self, name, **kw):
        # dict<string, HardwareObjList>
        # key : the hardware object name
        # value : the Hardware object list object
        self._obj_dict = CaselessDict()
        
        self.call__init__(TangoDevice, name, **kw)
        self.call__init__(MoveableSource)
        
        self._elements = BaseSardanaElementContainer()
        self.getAttribute("ElementList").addListener(self.on_elements_changed)
    
    def getObject(self, element_info):
        elem_type = element_info.getType()
        data = element_info._data
        if elem_type in ('ControllerClass', 'ControllerLib', 'Instrument'):
            klass = globals()[elem_type]
            kwargs = dict(data)
            kwargs['_pool_data'] = data
            return klass(**kwargs)
        obj = Factory().getDevice(element_info.full_name, _pool_obj=self,
                                  _pool_data=data)
        return obj
        
    def on_elements_changed(self, evt_src, evt_type, evt_value):
        if evt_type not in CHANGE_EVT_TYPES:
            return
        try:
            elems = CodecFactory().decode(evt_value.value, ensure_ascii=True)
        except:
            self.error("Could not decode element info format=%s len=%s",
                       evt_value.value[0], len(evt_value.value[1]))
            return
        
        event_type = elems['__type__']
        elements_data = elems['elements']
        
        elements = self.getElementsInfo()
        if event_type == 'set':
            for element_data in elements_data:
                element_data['manager'] = self
                element = BaseSardanaElement(**element_data)
                elements.addElement(element)
        else:
            for element_data in elements_data:
                element = self.getElementInfo(element_data['name'])
                elements.removeElement(element)
    
    def getElementsInfo(self):
        return self._elements
    
    def getElements(self):
        return self.getElementsInfo().getElements()
    
    def getElementInfo(self, name):
        return self.getElementsInfo().getElement(name)

    def getElementNamesOfType(self, elem_type):
        return self.getElementsInfo().getElementNamesOfType(elem_type)
    
    def getElementsOfType(self, elem_type):
        return self.getElementsInfo().getElementsOfType(elem_type)
        
    def getObj(self, name, elem_type=None):
        if elem_type is None:
            return self.getElementInfo(name)
        elif isinstance(elem_type, (str, unicode)):
            elem_types = elem_type,
        else:
            elem_types = elem_type
        for e_type in elem_type:
            elems = self.getElementsOfType(e_type)
            elem = elems.get(name)
            if elem is not None:
                return elem
    
    def __repr__(self):
        return self.getNormalName()

    def __str__(self):
        return repr(self)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # MoveableSource interface
    #    
    
    def getMoveable(self, names):
        """getMoveable(seq<string> names) -> Moveable

        Returns a moveable object that handles all the moveable items given in 
        names."""
        # if simple motor just return it (if the pool has it)
        if isinstance(names, (str, unicode)):
            names = names,
            
        if len(names) == 1:
            name = names[0]
            return self.getObj(name, elem_type=MOVEABLE_TYPES)
        
        # find a motor group that contains elements
        moveable = self.__findMotorGroupWithElems(names)
        
        # if none exists create one
        if moveable is None:
            mgs = self.getElementsOfType('MotorGroup')
            i, cont = 1, True
            pid = os.getpid()
            while cont:
                name = "_mg_ms_{0}_{1}".format(pid, i)
                if name not in mgs:
                    cont = False
                i += 1
            moveable = self.createMotorGroup(name, names)
        return moveable
    
    def __findMotorGroupWithElems(self, names):
        names_lower = map(str.lower, names)
        len_names = len(names)
        mgs = self.getElementsOfType('MotorGroup')
        for mg in mgs.values():
            mg_elems = mg.elements
            if len(mg_elems) != len_names:
                continue
            for mg_elem, name in zip(mg_elems, names_lower):
                if mg_elem.lower() != name:
                    break
            else:
                return mg
    
    #
    # End of MoveableSource interface
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def _wait_for_element_in_container(self, container, elem_name, timeout=0.5):
        start = time.time()
        cond = True
        nap = 0.01
        if timeout:
            nap = timeout / 10.
        while cond:
            if elem_name in container:
                return True
            if timeout:
                dt = time.time() - start
                if dt > timeout:
                    return False
            time.sleep(nap)
    
    def createMotorGroup(self, mg_name, elements):
        params = [mg_name,] + map(str, elements)
        self.debug('trying to create motor group for elements: %s', params)
        self.command_inout('CreateMotorGroup', params)
        elements = self.getElements()
        if self._wait_for_element_in_container(elements, mg_name):
            return elements[mg_name]
    
    def createMeasurementGroup(self, name, elements):
        params = [name,] + map(str,elements)
        self.debug('trying to create measurement group: %s', params)
        mg_list = self.getListObj('MeasurementGroup')
        self.command_inout('CreateMeasurementGroup', params)
        mg_list.waitEvent(any=True, timeout=0.5)
        return mg_list.getObjByName(name)
        
    def deleteMeasurementGroup(self, name):
        mg_list = self.getListObj('MeasurementGroup')
        mg = mg_list.getObjByName(name)
        self.command_inout('DeleteMeasurementGroup', name)
        mg_list.waitEvent(any=True, timeout=0.5)
    
    def createElement(self, name, ctrl, axis=None):
        ctrl_type = ctrl.getType()
        if axis is None:
            axis = ctrl.getLastUsedAxis() + 1
        else:
            axis = int(axis)
        elem_type = ctrl_type
        if elem_type not in ("Motor", "IORegister", "ComChannel"):
            elem_type = "ExpChannel"
        cmd = "Create" + elem_type
        lst = self.getListObj(elem_type)
        self.command_inout(cmd, [[axis], [name, ctrl.getName()]])
        lst.waitEvent(any=True, timeout=0.5)
        return lst.getObjByName(name)

    def deleteElement(self, name):
        obj = None
        for obj_list in self._obj_dict.values():
            obj = obj_list.getObjByName(name)
            if obj is not None:
                break
        if obj is None:
            raise Exception("Element %s not found" % name)
        elem_type = obj.getType()
        if elem_type not in ("Motor", "IORegister", "ComChannel"):
            elem_type = "ExpChannel"
        cmd = "Delete" + elem_type
        lst = self.getListObj(elem_type)
        self.command_inout(cmd, name)
        lst.waitEvent(any=True, timeout=0.5)

    def createController(self, class_name, name, *props):
        ctrl_class = self.getObj('ControllerClass', class_name)
        if ctrl_class is None:
            raise Exception("Controller class %s not found" % class_name)
        cmd = "CreateController"
        pars = [ctrl_class.getType(), ctrl_class.getSimpleFileName(), class_name, name]
        pars.extend(map(str, props))
        ctrl_list = self.getListObj('Controller')
        self.command_inout(cmd, pars)
        ctrl_list.waitEvent(any=True, timeout=0.5)
        return ctrl_list.getObjByName(name)

    def deleteController(self, name):
        ctrl_list = self.getListObj('Controller')
        ctrl = ctrl_list.getObjByName(name)
        self.command_inout('DeleteController', name)
        ctrl_list.waitEvent(any=True, timeout=0.5)
        
def registerExtensions():
    factory = Factory()
    factory.registerDeviceClass("Pool", Pool)
    for klass_name, klass in Pool.HardwareObjTypeMap:
        factory.registerDeviceClass(klass_name, klass)

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

"""This module contains all taurus tango attribute configuration"""

__all__ = ["TangoConfiguration"]

__docformat__ = "restructuredtext"

# -*- coding: utf-8 -*-
import threading
import weakref
import time

import PyTango

from taurus import Factory, Manager
from taurus.core.taurusbasetypes import TaurusEventType
from taurus.core.taurusconfiguration import TaurusConfiguration
from .enums import EVENT_TO_POLLING_EXCEPTIONS

class TangoConfiguration(TaurusConfiguration):
    
    def __init__(self, name, parent, storeCallback = None):
        self._events_working = False
        self.call__init__(TaurusConfiguration, name, parent, storeCallback)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel necessary overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    # helper class property that stores a reference to the corresponding factory
    _factory = None
    
    @classmethod
    def factory(cls):
        if cls._factory is None:
            cls._factory = Factory("tango")
        return cls._factory

    def __getattr__(self, name):
        if self._attr_info is None:
            return
        try:
            return getattr(self._attr_info,name)
        except:
            try:
                return getattr(self._attr_info.alarms,name)
            except:
                try:
                    return getattr(self._attr_info.events,name)
                except AttributeError:
                    raise AttributeError
                    
    def isWrite(self, cache=True):
        return self.getWritable(cache) == PyTango.AttrWriteType.WRITE
    
    def isReadOnly(self, cache=True):
        return self.getWritable(cache) == PyTango.AttrWriteType.READ

    def isReadWrite(self, cache=True):
        return self.getWritable(cache) == PyTango.AttrWriteType.READ_WRITE
    
    def isScalar(self, cache=True):
        return self.getDataFormat(cache) == PyTango.AttrDataFormat.SCALAR
    
    def isSpectrum(self, cache=True):
        return self.getDataFormat(cache) == PyTango.AttrDataFormat.SPECTRUM
    
    def isImage(self, cache=True):
        return self.getDataFormat(cache) == PyTango.AttrDataFormat.IMAGE
    
    def encode(self, value):
        """Translates the given value into a tango compatible value according to
        the attribute data type
        value must be a valid """
        return value

    def getValueObj(self, cache=True):
        """ Returns the current configuration for the attribute.
            if cache is set to True (default) and the the configuration has 
            events active then it will return the local cached value. Otherwise
            it will read from the tango layer."""
        if cache and self._attr_info is not None:
            return self._attr_info
        
        curr_time = time.time()
        
        dt = (curr_time - self._attr_timestamp)*1000
        if dt < TangoConfiguration.DftTimeToLive:
            return self._attr_info
            
        self._attr_timestamp = curr_time
        try:
            dev = self._getDev()
            v = dev.attribute_query(self._getAttrName())
            self._attr_info = self.decode(v)
        except PyTango.DevFailed, df:
            err = df[0]
            self.debug("[Tango] read configuration failed (%s): %s" % (err.reason, err.desc))
        except Exception, e:
            self.debug("[Tango] read configuration failed: %s" % str(e))
        return self._attr_info

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for listeners
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    

    def __fireRegisterEvent(self, listener):
        value = self.getValueObj()
        if value is not None:
            self.fireEvent(TaurusEventType.Config, value, listener)

    def addListener(self, listener):
        """ Add a TaurusListener object in the listeners list.
            If the listener is already registered nothing happens."""
        ret = TaurusConfiguration.addListener(self, listener)
        if not ret:
            return ret
        
        #fire a first configuration event
        #if len(self._listeners) > 1 or not self._events_working:
        Manager().addJob(self.__fireRegisterEvent, None, (listener,))
        return ret
    
    def removeListener(self, listener):
        """ Remove a TaurusListener from the listeners list.
        If it is the last listener, unsubscribe from events."""
        ret = TaurusConfiguration.removeListener(self, listener)
        if not ret:
            return ret
        if not self.hasListeners():
            self._unsubscribeEvents()
        return ret

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # PyTango event handling (private) 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    

    def _subscribeEvents(self):
        """ Enable subscription to the attribute configuration events."""
        self.trace("Subscribing to configuration events...")
        dev = self._getDev()
        if dev is None:
            self.debug("failed to subscribe config events: device is None")
            return
        dev = dev.getHWObj()
        if dev is None:
            self.debug("failed to subscribe config events: HW is None")
            return
        
        attrname = self._getAttrName()
        try:
            self._cfg_evt_id = dev.subscribe_event(attrname,
                                                  PyTango.EventType.ATTR_CONF_EVENT,
                                                  self, [], True)
        except PyTango.DevFailed, e:
            self.debug("Unexpected exception trying to subscribe to CONFIGURATION events.")
            self.traceback()
            # Subscription failed either because event mechanism is not available
            # or because the device server is not running.
            # The first possibility is assumed so an attempt to get the configuration
            # manually is done 
            try:
                self.getValueObj(cache=False)
            except: 
                self.debug("Error getting attribute configuration")
                self.traceback()
        
    def _unsubscribeEvents(self):
        # Careful in this method: This is intended to be executed in the cleanUp
        # so we should not access external objects from the factory, like the 
        # parent object
        if self._cfg_evt_id and not self._dev_hw_obj is None:
            self.trace("Unsubscribing to configuration events (ID=%s)" % str(self._cfg_evt_id))
            try:
                self._dev_hw_obj.unsubscribe_event(self._cfg_evt_id)
                self._cfg_evt_id = None
            except PyTango.DevFailed, e:
                self.debug("Exception trying to unsubscribe configuration events")
                self.trace(str(e))
                
    def decode(self, i):
        if i is None:
            return i
        
        i.climits = [i.min_value, i.max_value]
        i.calarms = [i.min_alarm, i.max_alarm]
        i.cwarnings = [i.alarms.min_warning, i.alarms.max_warning]
        i.cranges = [i.min_value, i.min_alarm, i.alarms.min_warning,
                    i.alarms.max_warning, i.max_alarm, i.max_value]
        i.range = [i.min_value, i.max_value]
        i.alarm = [i.min_alarm, i.max_alarm]
        i.warning = [i.alarms.min_warning, i.alarms.max_warning]
        # add dev_name, dev_alias, attr_name, attr_full_name
        i.dev_name = self._getDev().getNormalName()
        i.dev_alias = self._getDev().getSimpleName()
        try:
            attr = self._getAttr()
            if attr is not None:
                i.attr_fullname = self._getAttr().getNormalName()
                i.attr_name = self._getAttr().getSimpleName()
            else: 
                self.debug(('TangoConfiguration.decode(%s/%s): ' +
                              'self._getAttr() returned None (failed detach?)'), 
                           i.dev_name, i.name)
        except:
            import traceback
            self.warning('at TangoConfiguration.decode(%s/%s)', i.dev_name, i.name)
            self.warning(traceback.format_exc())
            i.attr_name = i.attr_fullname = ''
        
        # %6.2f is the default value that Tango sets when the format is
        # unassigned. This is only good for float types! So for other
        # types I am changing this value.
        # There's a bug about this in the core TangoC++ project, so
        # this code may become useless someday.
        if i.format == '%6.2f':
            if PyTango.is_float_type(i.data_type, inc_array=True):
                pass
            elif PyTango.is_int_type(i.data_type, inc_array=True):
                i.format = '%d'
            elif i.data_type in (PyTango.CmdArgType.DevString, PyTango.CmdArgType.DevVarStringArray):
                i.format = '%s'
        return i

    def push_event(self, event):
        if event.err:
            if event.errors[0].reason not in EVENT_TO_POLLING_EXCEPTIONS:
                self._attr_timestamp = time.time()
                self._events_working = True
            else:
                self._events_working = False
            return
        if self._getAttr() is None and not self._listeners:
            #===================================================================
            # This is a safety net to catch "zombie" TangoConfiguration objects
            # when they get called.
            # If you get here, there is some bug elsewhere which should be
            # investigated.
            # Without this safety net, you would get exceptions.
            # We assume that a TangoConfiguration object which has no listeners
            # and which is not associated to a TangoAttribute, is a "zombie".
            self.warning('"Zombie" object (%s) received an event. Unsubscribing it.', repr(self))
            self._unsubscribeEvents()
            return
            #===================================================================
        self._events_working = True
        self._attr_timestamp = time.time()
        self._attr_info = self.decode(event.attr_conf)
        listeners = tuple(self._listeners)
        #Manager().addJob(self._push_event, None, event)
        Manager().addJob(self.fireEvent, None, TaurusEventType.Config, self._attr_info, listeners=listeners)
        
    
    #===========================================================================
    # Some methods reimplemented from TaurusConfiguration
    #===========================================================================
    
    def getMaxDimX(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.max_dim_x
        return None

    def getMaxDimY(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.max_dim_y
        return None
    
    def getType(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.data_type
        return None
    
    def getRange(self, cache=True):
        return self.getLimits(cache=cache)
    
    def getLimits(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.climits
        return None
    
    def getRanges(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return list(c.cranges)
        return None
    
    def getMinAlarm(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.min_alarm
        return None

    def getMaxAlarm(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.max_alarm
        return None
        
    def getAlarms(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return list(c.calarms)
        return None
    
    def getMinWarning(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.alarms.min_warning
        return None

    def getMaxWarning(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return c.alarms.max_warning
        return None
        
    def getWarnings(self, cache=True):
        c = self.getValueObj(cache=cache)
        if c:
            return list(c.cwarnings)
        return None
    
    def getParam(self, param_name):
        config = self.getValueObj()
        if config:
            if param_name.endswith('warning') or param_name.endswith('alarm'):
                config = config.alarms
            try:
                return getattr(config, param_name)
            except:
                return None
            
    def setParam(self, param_name, value):
        config = self.getValueObj()
        if config is None:
            return
        if param_name.endswith('warning') or param_name.endswith('alarm'):
            config = config.alarms
        setattr(config, param_name, value)
        self._applyConfig()
    
    def setDescription(self,descr):
        config = self.getValueObj()
        if config:
            config.description = descr
            self._applyConfig()

    def setLabel(self,lbl):
        config = self.getValueObj()
        if config:
            config.label = lbl
            self._applyConfig()

    def setUnit(self,unit):
        config = self.getValueObj()
        if config:
            config.unit = unit
            self._applyConfig()

    def setStandardUnit(self,standard_unit):
        config = self.getValueObj()
        if config:
            config.standard_unit = standard_unit
            self._applyConfig()
        
    def setDisplayUnit(self,display_unit):
        config = self.getValueObj()
        if config:
            config.display_unit = display_unit
            self._applyConfig()
    
    def setFormat(self,fmt):
        config = self.getValueObj()
        if config:
            config.format = fmt
            self._applyConfig()
        
    def setLimits(self,low, high):
        config = self.getValueObj()
        if config:
            l_str, h_str = str(low), str(high)
            config.cranges[0] = config.min_value = l_str
            config.cranges[5] = config.max_value = h_str
            config.climits = [l_str, h_str]
            self._applyConfig()

    def setWarnings(self,low, high):
        config = self.getValueObj()
        if config:
            l_str, h_str = str(low), str(high)
            config.cranges[2] = config.alarms.min_warning = l_str
            config.cranges[3] = config.alarms.max_warning = h_str
            config.cwarnings = [l_str, h_str]
            self._applyConfig()

    def setAlarms(self,low, high):
        config = self.getValueObj()
        if config:
            l_str, h_str = str(low), str(high)
            config.cranges[1] = config.min_alarm = config.alarms.min_alarm = l_str
            config.cranges[4] = config.max_alarm = config.alarms.max_alarm = h_str
            config.calarms = [l_str, h_str]
            self._applyConfig()
    
    def _applyConfig(self):
        config = self.getValueObj()
        if config:
            self.getParentObj().setConfigEx(config)

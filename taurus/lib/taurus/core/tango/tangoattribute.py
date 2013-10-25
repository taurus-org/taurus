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

"""This module contains all taurus tango attribute"""

__all__ = ["TangoAttribute", "TangoStateAttribute", "TangoAttributeEventListener"]

__docformat__ = "restructuredtext"

# -*- coding: utf-8 -*-
import time
import threading
import PyTango

from taurus import Factory, Manager
from taurus.core.taurusattribute import TaurusAttribute, TaurusStateAttribute
from taurus.core.taurusbasetypes import TaurusEventType, TaurusSerializationMode, \
    SubscriptionState
from taurus.core.taurusoperation import WriteAttrOperation
from taurus.core.util.event import EventListener
from .enums import EVENT_TO_POLLING_EXCEPTIONS

DataType = PyTango.CmdArgType

class TangoAttribute(TaurusAttribute):

    # helper class property that stores a reference to the corresponding factory
    _factory = None
    
    def __init__(self, name, parent, **kwargs):

        # the last attribute value
        self.__attr_value = None
        
        # the last attribute error
        self.__attr_err = None
        
        # the last time the attribute was read
        self.__attr_timestamp = 0
        
        # the change event identifier
        self.__chg_evt_id = None

        # reference to the configuration object
        self.__attr_config = None
        
        # current event subscription state
        self.__subscription_state = SubscriptionState.Unsubscribed
        self.__subscription_event = threading.Event()

        self.call__init__(TaurusAttribute, name, parent, **kwargs)

    def __getattr__(self,name):
        return getattr(self._getRealConfig(), name)
    
    def _getRealConfig(self):
        """ Returns the current configuration of the attribute."""

        if self.__attr_config is None:
            cfg_name = "%s?configuration" % self.getFullName()
            from taurus.core.tango import TangoConfiguration # @todo...
            self.__attr_config = TangoConfiguration(cfg_name, self)
        return self.__attr_config
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusModel necessary overwrite
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    @classmethod
    def factory(cls):
        if cls._factory is None:
            cls._factory = Factory(scheme='tango')
        return cls._factory

    def getNewOperation(self, value):
        attr_value = PyTango.AttributeValue()
        attr_value.name = self.getSimpleName()
        attr_value.value = self.encode(value)
        op = WriteAttrOperation(self, attr_value)
        return op
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # PyTango connection
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    
    
    def isNumeric(self, inc_array=False):
        cfg = self._getRealConfig()
        if not cfg:
            self.warning("attribute does not contain information")
            return False
        if inc_array and not self.isScalar():
            return False
        
        type = cfg.getType()
        return PyTango.is_numerical_type(type, inc_array=inc_array)
    
    def isInteger(self, inc_array=False):
        cfg = self._getRealConfig()
        if not cfg:
            self.warning("attribute does not contain information")
            return False
        if inc_array and not self.isScalar():
            return False

        type = cfg.getType()
        return PyTango.is_int_type(type, inc_array=inc_array)

    def isFloat(self, inc_array=False):
        cfg = self._getRealConfig()
        if not cfg:
            self.warning("attribute does not contain information")
            return False
        if inc_array and not self.isScalar():
            return False

        type = cfg.getType()
        return PyTango.is_float_type(type, inc_array=inc_array)
    
    def isBoolean(self, inc_array=False):
        cfg = self._getRealConfig()
        if not cfg:
            self.warning("attribute does not contain information")
            return False
        if inc_array and not self.isScalar():
            return False
        
        type = cfg.getType()
        if inc_array:
            return type in (DataType.DevBoolean, DataType.DevVarBooleanArray)
        else:
            return type == DataType.DevBoolean
    
    def isState(self):
        cfg = self._getRealConfig()
        if not cfg:
            self.warning("attribute does not contain information")
            return False
        return cfg.getType() == DataType.DevState
        
    def getDisplayValue(self,cache=True):
        attrvalue = self.getValueObj(cache=cache)
        if not attrvalue:
            return None
        v = attrvalue.value
            
        return self.displayValue(v)
        
    def encode(self, value):
        """Translates the given value into a tango compatible value according to
        the attribute data type"""
        
        attrvalue = None
        
        if self._getRealConfig() is None:
            self.warning("attribute does not contain information")
            return value
            
        fmt = self.getDataFormat()
        type = self.getType()
        if fmt == PyTango.SCALAR:
            if PyTango.is_float_type(type):
                attrvalue = float(value)
            elif PyTango.is_int_type(type):
                #attrvalue = int(value)
                attrvalue = long(value) #changed as a partial workaround to a problem in PyTango writing to DevULong64 attributes (see ALBA RT#29793)
            elif type == DataType.DevBoolean:
                try:
                    attrvalue = bool(int(value))
                except:
                    attrvalue = str(value).lower() == 'true'
            elif type == DataType.DevUChar:
                attrvalue = chr(value)
            elif type == DataType.DevState:
                attrvalue = value
            else:
                attrvalue = str(value)
        elif fmt in (PyTango.SPECTRUM, PyTango.IMAGE):
            attrvalue = value
        else:
            attrvalue = str(value)
        return attrvalue
    
    def decode(self, attr_value):
        """Decodes a value that was received from PyTango into the expected 
        representation"""
        return attr_value
    
    def write(self, value, with_read=True):
        """ Write the value in the Tango Device Attribute """
        try:
            dev = self.getParentObj()
            name, value = self.getSimpleName(), self.encode(value)
            if self.isUsingEvents() or not self.isReadWrite():
                with_read = False
            if with_read:
                try:
                    result = dev.write_read_attribute(name, value)
                except AttributeError:
                    # handle old PyTango
                    dev.write_attribute(name, value)
                    result = dev.read_attribute(name)
                except PyTango.DevFailed, df:
                    for err in df:
                        # Handle old device servers
                        if err.reason == 'API_UnsupportedFeature':
                            dev.write_attribute(name, value)
                            result = dev.read_attribute(name)
                            break;
                    else:
                        raise df
                result = self.decode(result)
                self.poll(single=False, value=result, time=time.time())
                return result
            else:
                dev.write_attribute(name, value)
        except PyTango.DevFailed, df:
            err = df[0]
            self.error("[Tango] write failed (%s): %s" % (err.reason, err.desc))
            raise df
        except Exception, e:
            self.error("[Tango] write failed: %s" % str(e))
            raise e

    def poll(self, **kwargs):
        """ Notify listeners when the attribute has been polled"""
        single = kwargs.get('single',True)
        try:
            if single:
                self.read(cache=False)
            else:
                self.__attr_value = self.decode(kwargs.get('value'))
                self.__attr_err = kwargs.get('error')
                self.__attr_timestamp = kwargs.get('time', time.time())
                if self.__attr_err:
                    raise self.__attr_err
        except PyTango.DevFailed, df:
            self.__subscription_event.set()
            self.debug("Error polling: %s" % df[0].desc)
            self.traceback()
            self.fireEvent(TaurusEventType.Error, self.__attr_err)
        except Exception, e:
            self.__subscription_event.set()
            self.debug("Error polling: %s" % str(e))
            self.fireEvent(TaurusEventType.Error, self.__attr_err)
        else:
            self.__subscription_event.set()
            self.fireEvent(TaurusEventType.Periodic, self.__attr_value)
            
    def read(self, cache=True):
        """ Returns the current value of the attribute.
            if cache is set to True (default) or the attribute has events 
            active then it will return the local cached value. Otherwise it will
            read the attribute value from the tango device."""
        curr_time = time.time()

        if cache:
            dt = (curr_time - self.__attr_timestamp)*1000
            if dt < self.getPollingPeriod():
                if self.__attr_value is not None:
                    return self.__attr_value
                elif self.__attr_err is not None:
                    raise self.__attr_err

        if not cache or (self.__subscription_state in (SubscriptionState.PendingSubscribe, SubscriptionState.Unsubscribed) and not self.isPollingActive()):
            try:
                dev = self.getParentObj()
                v = dev.read_attribute(self.getSimpleName())
                self.__attr_value, self.__attr_err, self.__attr_timestamp = self.decode(v), None, curr_time 
                return self.__attr_value
            except PyTango.DevFailed, df:
                self.__attr_value, self.__attr_err, self.__attr_timestamp = None, df, curr_time
                err = df[0]
                self.debug("[Tango] read failed (%s): %s", err.reason, err.desc)
                raise df
            except Exception, e:
                self.__attr_value, self.__attr_err = None, e
                self.debug("[Tango] read failed: %s", e)
                raise e
        elif self.__subscription_state in (SubscriptionState.Subscribing, SubscriptionState.PendingSubscribe):
            self.__subscription_event.wait()
            
    
        if self.__attr_err is not None:
            raise self.__attr_err
        return self.__attr_value

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for listeners
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    

    def __fireRegisterEvent(self, listener):
        #fire a first configuration event
        #cfg = self._getRealConfig().getValueObj()
        #if cfg:
        #    self.fireEvent(TaurusEventType.Config, cfg, listener)
        #else:
        
        #fire a first change event
        try:
            v = self.read()
            self.fireEvent(TaurusEventType.Change,v, listener)
        except:
            self.fireEvent(TaurusEventType.Error, self.__attr_err, listener)

    def addListener(self, listener):
        """ Add a TaurusListener object in the listeners list.
            If it is the first element and Polling is enabled starts the 
            polling mechanism.
            If the listener is already registered nothing happens."""
        cfg = self._getRealConfig()
        cfg.addListener(listener)
        
        listeners = self._listeners
        initial_subscription_state = self.__subscription_state

        ret = TaurusAttribute.addListener(self, listener)
        if not ret:
            return ret
        
        assert len(listeners) >= 1
        
        if self.__subscription_state == SubscriptionState.Unsubscribed and len(listeners) == 1:
            self._subscribeEvents()
        
        #if initial_subscription_state == SubscriptionState.Subscribed:
        if len(listeners) > 1 and (initial_subscription_state == SubscriptionState.Subscribed or self.isPollingActive()):
            sm = self.getSerializationMode()
            if sm == TaurusSerializationMode.Concurrent:
                Manager().addJob(self.__fireRegisterEvent, None, (listener,))
            else:
                self.__fireRegisterEvent((listener,))
        return ret
        
    def removeListener(self, listener):
        """ Remove a TaurusListener from the listeners list. If polling enabled 
            and it is the last element the stop the polling timer.
            If the listener is not registered nothing happens."""
        ret = TaurusAttribute.removeListener(self, listener)

        cfg = self._getRealConfig()
        cfg.removeListener(listener)
        
        if not ret:
            return ret
    
        if self.hasListeners():
            return ret
        
        if self.__subscription_state != SubscriptionState.Unsubscribed:
            self._unsubscribeEvents()
            
        return ret
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for attribute configuration
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    

    def setConfigEx(self,config):
        self.getParentObj().set_attribute_config([config])

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # PyTango event handling (private) 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-    

    def isUsingEvents(self):
        return self.__subscription_state == SubscriptionState.Subscribed

    def _process_event_exception(self, ex):
        pass

    def _subscribeEvents(self):
        """ Enable subscription to the attribute events. If change events are 
            not supported polling is activated """
        
        # We have to register for configuration events before registering for 
        # change events because when a change event occurs we need to have 
        # configuration info in order to know how to decode the value
        self._getRealConfig().addListener(self)
        

        self.trace("Subscribing to change events...")

        dev = self.getParentObj()
        if dev is None:
            self.debug("failed to subscribe change events: device is None")
            return
        dev = dev.getHWObj()
        if dev is None:
            self.debug("failed to subscribe change events: HW is None")
            return

        self.__subscription_event = threading.Event()

        try:
            self.__subscription_state = SubscriptionState.Subscribing
            self.__chg_evt_id = dev.subscribe_event(self.getSimpleName(),
                                                  PyTango.EventType.CHANGE_EVENT,
                                                  self, [])
            
        except:
            self.__subscription_state = SubscriptionState.PendingSubscribe
            self._activatePolling()
            self.__chg_evt_id = dev.subscribe_event(self.getSimpleName(),
                                                  PyTango.EventType.CHANGE_EVENT,
                                                  self, [], True)
    
    def _unsubscribeEvents(self):
        # Careful in this method: This is intended to be executed in the cleanUp
        # so we should not access external objects from the factory, like the 
        # parent object
        self._getRealConfig().removeListener(self)
        if not self.__chg_evt_id is None and not self._dev_hw_obj is None:
            self.trace("Unsubscribing to change events (ID=%d)" % self.__chg_evt_id)
            try:
                self._dev_hw_obj.unsubscribe_event(self.__chg_evt_id)
                self.__chg_evt_id = None
            except PyTango.DevFailed, df:
                if len(df.args) and df[0].reason == 'API_EventNotFound':
                    # probably tango shutdown as been initiated before and it
                    # unsubscribed from events itself
                    pass
                else:
                    self.debug("Failed: %s" % df[0].desc)
                    self.trace(str(df))
        self._deactivatePolling()
        self.__subscription_state = SubscriptionState.Unsubscribed
    
    def push_event(self, event):
        """Method invoked by the PyTango layer when a change event occurs.
           Default implementation propagates the event to all listeners."""
        
        curr_time = time.time()
        manager = Manager()
        sm = self.getSerializationMode()
        if not event.err:
            self.__attr_value, self.__attr_err, self.__attr_timestamp = self.decode(event.attr_value), None, curr_time
            self.__subscription_state = SubscriptionState.Subscribed
            self.__subscription_event.set()
            if not self.isPollingForced():
                self._deactivatePolling()
            listeners = tuple(self._listeners)
            if sm == TaurusSerializationMode.Concurrent:
                manager.addJob(self.fireEvent, None, TaurusEventType.Change,
                               self.__attr_value, listeners=listeners)
            else:
                self.fireEvent(TaurusEventType.Change, self.__attr_value,
                               listeners=listeners)
        elif event.errors[0].reason in EVENT_TO_POLLING_EXCEPTIONS:
            if self.isPollingActive():
                return
            self.__subscription_state = SubscriptionState.PendingSubscribe
            self._activatePolling()
        else:
            self.__attr_value, self.__attr_err = None, PyTango.DevFailed(*event.errors)
            self.__subscription_state = SubscriptionState.Subscribed
            self.__subscription_event.set()
            self._deactivatePolling()
            listeners = tuple(self._listeners)
            if sm == TaurusSerializationMode.Concurrent:
                manager.addJob(self.fireEvent, None, TaurusEventType.Error,
                               self.__attr_err, listeners=listeners)
            else:
                self.fireEvent(TaurusEventType.Error, self.__attr_err,
                               listeners=listeners)

    def isInformDeviceOfErrors(self):
        return False


class TangoStateAttribute(TangoAttribute, TaurusStateAttribute):
    def __init__(self, name, parent, **kwargs):
        self.call__init__(TangoAttribute, name, parent, **kwargs)
        self.call__init__(TaurusStateAttribute, name, parent, **kwargs)


class TangoAttributeEventListener(EventListener):
    """A class that listens for an event with a specific value
    
    Note: Since this class stores for each event value the last timestamp when
    it occured, it should only be used for events for which the event value
    domain (possible values) is limited and well known (ex: an enum)"""
    
    def __init__(self, attr):
        EventListener.__init__(self)
        self.attr = attr
        attr.addListener(self)
        
    def eventReceived(self, s, t, v):
        if t not in (TaurusEventType.Change, TaurusEventType.Periodic):
            return
        self.fireEvent(v.value)



def test1():
    import numpy
    from taurus import Attribute
    a = Attribute('sys/tg_test/1/ulong64_scalar')
    
    a.write(numpy.uint64(88))

if __name__ == "__main__":
    test1()
    

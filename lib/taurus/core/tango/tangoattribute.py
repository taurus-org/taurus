#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus
##
## http://taurus-scada.org
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

__all__ = ["TangoAttribute", "TangoStateAttribute", 
           "TangoAttributeEventListener", "TangoAttrValue"]

__docformat__ = "restructuredtext"

# -*- coding: utf-8 -*-
import time
import threading
import PyTango
import numpy
from functools import partial

from taurus import Manager
from taurus.external.pint import Quantity

from taurus.core.taurusattribute import TaurusAttribute, TaurusStateAttribute
from taurus.core.taurusbasetypes import (TaurusEventType,
                                         TaurusSerializationMode,
                                         SubscriptionState, TaurusAttrValue,
                                         DataFormat, DataType)
from taurus.core.taurusoperation import WriteAttrOperation
from taurus.core.util.event import EventListener

from .enums import EVENT_TO_POLLING_EXCEPTIONS, FROM_TANGO_TO_NUMPY_TYPE

from .util.tango_taurus import (description_from_tango,
                                display_level_from_tango,
                                quality_from_tango,
                                standard_display_format_from_tango,
                                unit_from_tango, quantity_from_tango_str,
                                str_2_obj, data_format_from_tango,
                                data_type_from_tango)

class TangoAttrValue(TaurusAttrValue):
    '''A TaurusAttrValue specialization to decode PyTango.DeviceAttribute 
    objects'''
    
    def __init__(self, config=None, pytango_dev_attr=None, attrref=None):
        TaurusAttrValue.__init__(self, attrref=attrref)
        self._pytango_dev_attr = p = pytango_dev_attr
        if p is None:
            self._pytango_dev_attr = p = PyTango.DeviceAttribute()
            return
        numerical = PyTango.is_numerical_type(attrref._tango_data_type,
                                              inc_array=True)
        if p.has_failed:
            self.error = PyTango.DevFailed(*p.get_err_stack())
        else:
            if p.is_empty: # spectra and images can be empty without failing
                dtype = FROM_TANGO_TO_NUMPY_TYPE.get(attrref._tango_data_type)
                if attrref.data_format == DataFormat._1D:
                    shape = (0,)
                elif attrref.data_format == DataFormat._2D:
                    shape = (0, 0)
                p.value = numpy.empty(shape, dtype=dtype)
                if not (numerical or attrref.type==DataType.Boolean):
                    # generate a nested empty list of given shape
                    p.value = []
                    for _ in xrange(len(shape)-1):
                        p.value = [p.value]

        rvalue = p.value
        wvalue = p.w_value
        #fmt = self.config._display_format
        units = self.config._units
        if numerical:
            if rvalue is not None:
                rvalue = Quantity(rvalue, units=units)
            if wvalue is not None:
                wvalue = Quantity(wvalue, units=units)

        self.rvalue = rvalue
        self.wvalue = wvalue
        self.time = p.time
        self.quality = quality_from_tango(p.quality)
     
    def __attr__(self, name):
        try:
            return getattr(self._attrRef, name)
        except AttributeError:
            return getattr(self._pytango_dev_attr, name)


class TangoAttribute(TaurusAttribute):

    # helper class property that stores a reference to the corresponding factory
    _factory = None
    _scheme = 'tango'

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

        #######################################################################
        # From TangoConfiguration
        self._events_working = False

    def __getattr__(self, name):
        dev = self.getParentObj()
        try:
            attr_name = self.getSimpleName().split('#')[0]
            attr_info = dev.attribute_query(attr_name)
            return getattr(attr_info, name)
        except AttributeError:
            return None

 #   def getParentObj(self):
 #       if self._parentObj is None:
 #           f = self._factory
 #           v = f.getAttributeNameValidator()
 #           dev_name = v.getUriGroups(self.getFullName())['devname']
 #           self._parentObj = f.getDevice(dev_name)
 #       return self._parentObj()

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
        tgtype = self._tango_data_type
        return PyTango.is_numerical_type(tgtype, inc_array=inc_array)

    def isInteger(self, inc_array=False):
        tgtype = self._tango_data_type
        return PyTango.is_int_type(tgtype, inc_array=inc_array)

    def isFloat(self, inc_array=False):
        tgtype = self._tango_data_type
        return PyTango.is_float_type(tgtype, inc_array=inc_array)

    def isBoolean(self, inc_array=False):
        tgtype = self._tango_data_type
        return PyTango.is_bool_type(tgtype, inc_array=inc_array)

    def isState(self):
        tgtype = self._tango_data_type
        return tgtype == PyTango.CmdArgType.DevState

    def getDisplayValue(self, cache=True):
        attrvalue = self.getValueObj(cache=cache)
        if not attrvalue:
            return None
        v = attrvalue.rvalue

        return self.displayValue(v)

    def encode(self, value):
        """Translates the given value into a tango compatible value according to
        the attribute data type"""

        attrvalue = None
#        cfg = self._getRealConfig()
#        if cfg is None:
#            self.warning("attribute does not contain information")
#            return value
        
        try:
            magnitude = value.magnitude
            units = value.units
        except AttributeError:
            magnitude = value
            units = None
            
        # convert the magnitude to the units of the server
        if units:
            if self._units:
                magnitude = value.to(self._units).magnitude
            else:
                msg = ( 'Attempt to encode a value with units (%s)' +
                        ' for an attribute without configured units') % units
                raise ValueError(msg)

        fmt = self.getDataFormat()
        tgtype = self._tango_data_type
        if fmt == DataFormat._0D:
            if tgtype == PyTango.CmdArgType.DevDouble:
                attrvalue = float(magnitude)
            elif tgtype == PyTango.CmdArgType.DevFloat:
                # We encode to float, but rounding to Tango::DevFloat precision
                # see: http://sf.net/p/sardana/tickets/162
                attrvalue = float(numpy.float32(magnitude))
            elif PyTango.is_int_type(tgtype):
                #attrvalue = int(magnitude)
                attrvalue = long(magnitude)  #changed as a partial workaround to a problem in PyTango writing to DevULong64 attributes (see ALBA RT#29793)
            elif tgtype == PyTango.CmdArgType.DevBoolean:
                try:
                    attrvalue = bool(int(magnitude))
                except:
                    attrvalue = str(magnitude).lower() == 'true'
            elif tgtype == PyTango.CmdArgType.DevUChar:
                attrvalue = chr(magnitude)
            elif tgtype in (PyTango.CmdArgType.DevState,
                            PyTango.CmdArgType.DevEncoded):
                attrvalue = magnitude
            else:
                attrvalue = str(magnitude)
        elif fmt in (DataFormat._1D, DataFormat._2D):
            if PyTango.is_int_type(tgtype):
                # cast to integer because the magnitude conversion gives floats 
                magnitude = magnitude.astype('int64')
            attrvalue = magnitude
        else:
            attrvalue = str(magnitude)
        return attrvalue

    def decode(self, attr_value):
        """Decodes a value that was received from PyTango into the expected 
        representation"""
        # TODO decode of the configuration
        #config = self._getRealConfig().getValueObj()
        dev = self.getParentObj()
        attr_info = None
        if dev:
            attr_name = self.getSimpleName().split('#')[0]
            attr_info = dev.attribute_query(attr_name)
        self.reInit(attr_info)
        value = TangoAttrValue(pytango_dev_attr=attr_value, attrref=self)
        return value

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
                #result = self.decode(result) #TODO: make sure this is not needed
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
        single = kwargs.get('single', True)
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
            dt = (curr_time - self.__attr_timestamp) * 1000
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
        # TODO TaurusEventType.Config
        # cfg = self._pytango_attrinfoex
        # self.fireEvent(TaurusEventType.Config, cfg, listener)

        #fire a first change event
        try:
            v = self.read()
            self.fireEvent(TaurusEventType.Change, v, listener)
        except:
            self.fireEvent(TaurusEventType.Error, self.__attr_err, listener)

    def addListener(self, listener):
        """ Add a TaurusListener object in the listeners list.
            If it is the first element and Polling is enabled starts the 
            polling mechanism.
            If the listener is already registered nothing happens."""

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

    def setConfigEx(self, config):
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
            self.info("Activating polling. Reason: %s", event.errors[0].reason)
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

    ###########################################################################
    # TangoConfiguration

    def isWrite(self, cache=True):
        return self.getTangoWritable(cache) == PyTango.AttrWriteType.WRITE

    def isReadOnly(self, cache=True):
        return not self.getTangoWritable(cache) == PyTango.AttrWriteType.READ

    def isReadWrite(self, cache=True):
        return self.getTangoWritable(cache) == PyTango.AttrWriteType.READ_WRITE

    def getTangoWritable(self, cache=True):
        '''like TaurusConfiguration.getWritable, but it returns a
         PyTango.AttrWriteType instead of a bool'''
        return self.tango_writable

#    def encode(self, value):
#        """Translates the given value into a tango compatible value according to
#        the attribute data type
#        value must be a valid """
#        return value

    def getValueObj(self, cache=True):
        """ Returns the current configuration for the attribute.
            if cache is set to True (default) and the the configuration has 
            events active then it will return the local cached value. Otherwise
            it will read from the tango layer."""
        if cache and self._attr_info is not None:
            return self._attr_info

        curr_time = time.time()

        dt = (curr_time - self._attr_timestamp)*1000
        if dt < self.DftTimeToLive:
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

    # def __fireRegisterEvent(self, listener):
    #     value = self.getValueObj()
    #     if value is not None:
    #         self.fireEvent(TaurusEventType.Config, value, listener)
    #
    # def addListener(self, listener):
    #     """ Add a TaurusListener object in the listeners list.
    #         If the listener is already registered nothing happens."""
    #     ret = TaurusConfiguration.addListener(self, listener)
    #     if not ret:
    #         return ret
    #
    #     #fire a first configuration event
    #     #if len(self._listeners) > 1 or not self._events_working:
    #     Manager().addJob(self.__fireRegisterEvent, None, (listener,))
    #     return ret
    #
    # def removeListener(self, listener):
    #     """ Remove a TaurusListener from the listeners list.
    #     If it is the last listener, unsubscribe from events."""
    #     ret = TaurusConfiguration.removeListener(self, listener)
    #     if not ret:
    #         return ret
    #     if not self.hasListeners():
    #         self._unsubscribeEvents()
    #     return ret

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # PyTango event handling (private)
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    # def _subscribeEvents(self):
    #     """ Enable subscription to the attribute configuration events."""
    #     self.trace("Subscribing to configuration events...")
    #     dev = self._getDev()
    #     if dev is None:
    #         self.debug("failed to subscribe config events: device is None")
    #         return
    #     dev = dev.getHWObj()
    #     if dev is None:
    #         self.debug("failed to subscribe config events: HW is None")
    #         return
    #
    #     attrname = self._getAttrName()
    #     try:
    #         self._cfg_evt_id = dev.subscribe_event(attrname,
    #                                               PyTango.EventType.ATTR_CONF_EVENT,
    #                                               self, [], True)
    #     except PyTango.DevFailed, e:
    #         self.debug("Unexpected exception trying to subscribe to CONFIGURATION events.")
    #         self.traceback()
    #         # Subscription failed either because event mechanism is not available
    #         # or because the device server is not running.
    #         # The first possibility is assumed so an attempt to get the configuration
    #         # manually is done
    #         try:
    #             self.getValueObj(cache=False)
    #         except:
    #             self.debug("Error getting attribute configuration")
    #             self.traceback()
    #
    # def _unsubscribeEvents(self):
    #     # Careful in this method: This is intended to be executed in the cleanUp
    #     # so we should not access external objects from the factory, like the
    #     # parent object
    #     if self._cfg_evt_id and not self._dev_hw_obj is None:
    #         self.trace("Unsubscribing to configuration events (ID=%s)" % str(self._cfg_evt_id))
    #         try:
    #             self._dev_hw_obj.unsubscribe_event(self._cfg_evt_id)
    #             self._cfg_evt_id = None
    #         except PyTango.DevFailed, e:
    #             self.debug("Exception trying to unsubscribe configuration events")
    #             self.trace(str(e))

    # def decode(self, i):
    #     #     #i is a pytango_AttrInfoEx... the return must be TangoConfigValue
    #     ret = self._getAttr().__attr_value
    #     ret.reInit(i)
    #
    #     # TODO: These may not be necessary (Taurus agnostic code should not
    #     #       depend on them)
    #     # add dev_name, dev_alias, attr_name, attr_full_name
    #     self.dev_name = self._getDev().getNormalName()
    #     self.dev_alias = self._getDev().getSimpleName()
    #     try:
    #         attr = self._getAttr()
    #         if attr is not None:
    #             ret.attr_fullname = self._getAttr().getNormalName()
    #             ret.attr_name = self._getAttr().getSimpleName()
    #         else:
    #             self.debug(('TangoConfiguration.decode(%s/%s): ' +
    #                           'self._getAttr() returned None (failed detach?)'),
    #                        ret.dev_name, ret.name)
    #     except:
    #         import traceback
    #         self.warning('at TangoConfiguration.decode(%s/%s)', ret.dev_name,
    #                      ret.name)
    #         self.warning(traceback.format_exc())
    #         ret.attr_name = ret.attr_fullname = ''
    #     return ret

    # def push_event(self, event):
    #     if event.err:
    #         if event.errors[0].reason not in EVENT_TO_POLLING_EXCEPTIONS:
    #             self._attr_timestamp = time.time()
    #             self._events_working = True
    #         else:
    #             self._events_working = False
    #         return
    #     if self._getAttr() is None and not self._listeners:
    #         #===================================================================
    #         # This is a safety net to catch "zombie" TangoConfiguration objects
    #         # when they get called.
    #         # If you get here, there is some bug elsewhere which should be
    #         # investigated.
    #         # Without this safety net, you would get exceptions.
    #         # We assume that a TangoConfiguration object which has no listeners
    #         # and which is not associated to a TangoAttribute, is a "zombie".
    #         self.warning('"Zombie" object (%s) received an event. Unsubscribing it.', repr(self))
    #         self._unsubscribeEvents()
    #         return
    #         #===================================================================
    #     self._events_working = True
    #     self._attr_timestamp = time.time()
    #     self._attr_info = self.decode(event.attr_conf)
    #     listeners = tuple(self._listeners)
    #     #Manager().addJob(self._push_event, None, event)
    #     Manager().addJob(self.fireEvent, None, TaurusEventType.Config, self._attr_info, listeners=listeners)

    #===========================================================================
    # Some methods reimplemented from TaurusConfiguration
    #===========================================================================

#    def getMaxDimX(self, cache=True):
#        return self.max_dim_x

#    def getMaxDimY(self, cache=True):
#        return self.max_dim_y

#    def getType(self, cache=True):
#        return self.data_type

    def getRange(self, cache=True):
        return self.getLimits(cache=cache)

    def getLimits(self, cache=True):
        return self.climits

    def getRanges(self, cache=True):
        return list(self.cranges)

    def getMinAlarm(self, cache=True):
        return self.min_alarm

    def getMaxAlarm(self, cache=True):
        return self.max_alarm

    def getAlarms(self, cache=True):
        return list(self.calarms)

    def getMinWarning(self, cache=True):
        return self.alarms.min_warning

    def getMaxWarning(self, cache=True):
        return self.alarms.max_warning

    def getWarnings(self, cache=True):
        return list(self.cwarnings)

    def getParam(self, param_name):
        # TODO mal implementado
        if param_name.endswith('warning') or param_name.endswith('alarm'):
            attr = self.alarms
        try:
            return getattr(attr, param_name)
        except:
            return None

    def setParam(self, param_name, value):
        # TODO mal implementado
        if param_name.endswith('warning') or param_name.endswith('alarm'):
            attr = self.alarms
        setattr(attr, param_name, value)
        self._applyConfig()

    def setLimits(self,low, high):
        l_str, h_str = str(low), str(high)
        self.cranges[0] = self.min_value = l_str
        self.cranges[5] = self.max_value = h_str
        self.climits = [l_str, h_str]
        self._applyConfig()

    def setWarnings(self,low, high):
        l_str, h_str = str(low), str(high)
        self.cranges[2] = self.alarms.min_warning = l_str
        self.cranges[3] = self.alarms.max_warning = h_str
        self.cwarnings = [l_str, h_str]
        self._applyConfig()

    def setAlarms(self,low, high):
        l_str, h_str = str(low), str(high)
        self.cranges[1] = self.min_alarm = self.alarms.min_alarm = l_str
        self.cranges[4] = self.max_alarm = self.alarms.max_alarm = h_str
        self.calarms = [l_str, h_str]
        self._applyConfig()

    def _applyConfig(self):
        config = self._pytango_attrinfoex
        self.setConfigEx(config)

    ###########################################################################
    # TangoConfValue methods
    # it is the old constructor
    def reInit(self, pytango_attrinfoex=None):
        if  pytango_attrinfoex is None:
            self._pytango_attrinfoex = PyTango.AttrInfoEx()
        else:
            self._pytango_attrinfoex = i = pytango_attrinfoex

            self.name = i.name
            self.writable = i.writable != PyTango.AttrWriteType.READ
            self.label = i.label

            self.data_format = data_format_from_tango(i.data_format)
            self.description = description_from_tango(i.description)

            units = unit_from_tango(i.unit )
            #disp_fmt = display_format_from_tango(i.data_type, i.format)

            ###############################################################
            # changed in taurus4: range, alarm and warning now return
            # quantities if appropriate
            if PyTango.is_numerical_type(i.data_type, inc_array=True):
                Q_ = partial(quantity_from_tango_str, units=units,
                             dtype=i.data_type)
            else:
                Q_ = partial(str_2_obj, tg_type=i.data_type)
            min_value = Q_(i.min_value)
            max_value = Q_(i.max_value)
            min_alarm = Q_(i.min_alarm)
            max_alarm = Q_(i.max_alarm)
            min_warning = Q_(i.alarms.min_warning)
            max_warning = Q_(i.alarms.max_warning)
            self.range = [min_value, max_value]
            self.warning = [min_warning, max_warning]
            self.alarm = [min_alarm, max_alarm]
            #
            ###############################################################
            self.type = data_type_from_tango(i.data_type)

            #################################################
            # Tango-specific extension of TaurusConfigValue


            self.climits = [i.min_value, i.max_value]
            self.calarms = [i.min_alarm, i.max_alarm]
            self.cwarnings = [i.alarms.min_warning, i.alarms.max_warning]
            self.cranges = [i.min_value, i.min_alarm, i.alarms.min_warning,
                        i.alarms.max_warning, i.max_alarm, i.max_value]
            self.max_dim = 1, 1

            self.display_level = display_level_from_tango(i.disp_level)
            self.tango_writable = i.writable
            #################################################


            self.format = standard_display_format_from_tango(i.data_type,
                                                             i.format)

            # self._units and self._display_format is to be used by
            # TangoAttrValue for performance reasons. Do not rely on it in other
            # code
            self._units = units
            #self._display_format = disp_fmt

            #################################################
            # The following members will be accessed via __getattr__
            # self.standard_unit
            # self.display_unit
            # self.disp_level
            #################################################

    @property
    def _tango_data_type(self):
        '''returns the *tango* (not Taurus) data type'''
        return self._pytango_attrinfoex.data_type

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


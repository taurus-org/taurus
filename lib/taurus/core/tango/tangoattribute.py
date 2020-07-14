# -*- coding: utf-8 -*-
#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This module contains all taurus tango attribute"""

from builtins import range
from builtins import str

import re
import time
import threading
import weakref
import PyTango
import numpy
from functools import partial

from taurus import Manager
from taurus.core.units import Quantity, UR

from taurus import tauruscustomsettings
from taurus.core.taurusattribute import TaurusAttribute
from taurus.core.taurusbasetypes import (TaurusEventType,
                                         TaurusSerializationMode,
                                         SubscriptionState, TaurusAttrValue,
                                         DataFormat, DataType)
from taurus.core.taurusoperation import WriteAttrOperation
from taurus.core.util.event import EventListener, _BoundMethodWeakrefWithCall
from taurus.core.util.log import (debug, taurus4_deprecation,
                                  deprecation_decorator)

from taurus.core.tango.enums import (EVENT_TO_POLLING_EXCEPTIONS,
                                     FROM_TANGO_TO_NUMPY_TYPE,
                                     DevState)

from .util.tango_taurus import (description_from_tango,
                                display_level_from_tango,
                                quality_from_tango,
                                standard_display_format_from_tango,
                                quantity_from_tango_str,
                                data_format_from_tango,
                                data_type_from_tango)

__all__ = ["TangoAttribute", "TangoAttributeEventListener", "TangoAttrValue"]

__docformat__ = "restructuredtext"


class TangoAttrValue(TaurusAttrValue):
    """A TaurusAttrValue specialization to decode PyTango.DeviceAttribute
    objects
    """

    def __init__(self, attr=None, pytango_dev_attr=None, config=None):
        # config parameter is kept for backwards compatibility only
        TaurusAttrValue.__init__(self)
        if config is not None:
            from taurus.core.util.log import deprecated
            deprecated(dep='"config" kwarg', alt='"attr"', rel='4.0')
            attr = config
        if attr is None:
            self._attrRef = None
            self.__attrType = None
        else:
            self._attrRef = weakref.proxy(attr)
            self.__attrName = attr.getFullName()
            self.__attrType = attr.type

        self.config = self._attrRef  # bck-compat

        self._pytango_dev_attr = p = pytango_dev_attr
        if p is None:
            self._pytango_dev_attr = p = PyTango.DeviceAttribute()
            return

        if self._attrRef is None:
            return

        numerical = PyTango.is_numerical_type(self._attrRef._tango_data_type,
                                              inc_array=True)

        if p.has_failed:
            self.error = PyTango.DevFailed(*p.get_err_stack())
        else:
            # spectra and images can be empty without failing
            if p.is_empty and self._attrRef.data_format != DataFormat._0D:
                dtype = FROM_TANGO_TO_NUMPY_TYPE.get(
                    self._attrRef._tango_data_type)
                if self._attrRef.data_format == DataFormat._1D:
                    shape = (0,)
                elif self._attrRef.data_format == DataFormat._2D:
                    shape = (0, 0)
                p.value = numpy.empty(shape, dtype=dtype)
                if not (numerical or self._attrRef.type == DataType.Boolean):
                    # generate a nested empty list of given shape
                    p.value = []
                    for _ in range(len(shape) - 1):
                        p.value = [p.value]

        # Protect against DeviceAttribute not providing .value in some cases,
        # seen e.g. in PyTango 9.3.0
        rvalue = getattr(p, 'value', None)
        wvalue = getattr(p, 'w_value', None)
        if numerical:
            units = self._attrRef._units
            if rvalue is not None:
                rvalue = Quantity(rvalue, units=units)
            if wvalue is not None:
                wvalue = Quantity(wvalue, units=units)
        elif isinstance(rvalue, PyTango._PyTango.DevState):
            rvalue = DevState[str(rvalue)]

        self.rvalue = rvalue
        self.wvalue = wvalue
        self.time = p.time  # TODO: decode this into a TaurusTimeVal
        self.quality = quality_from_tango(p.quality)

    def __getattr__(self, name):
        """
        If the member `name` is not defined in this class, try to get it
        from the TangoAttribute (configuration) or from the PyTango value
        """
        # Do not try to delegate special methods
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError("'%s' object has no attribute %s"
                                 % (self.__class__.__name__, name))
        try:
            # maybe name is defined in the TangoAttribute?
            try:
                # Use the attr reference if the attr is still valid
                ret = getattr(self._attrRef, name)
            except ReferenceError:
                # re-create the attribute in case it was no longer referenced
                # (this may happen in some rare cases in which the value is
                # still used but the attr is no longer referenced elsewhere)
                a = TangoAttribute.factory().getAttribute(self.__attrName)
                ret = getattr(a, name)
        except AttributeError:
            try:
                # maybe name is defined in the PyTango value?
                ret = getattr(self._pytango_dev_attr, name)
            except AttributeError:
                raise AttributeError("'%s' object has no attribute %s"
                                     % (self.__class__.__name__, name))
        # return the attr but only after warning
        from taurus.core.util.log import deprecated
        deprecated(dep='TangoAttrValue.%s' % name,
                   alt='TangoAttribute.%s' % name, rel='4.0')
        return ret

    # --------------------------------------------------------
    # This is for backwards compat with the API of taurus < 4
    #
    @taurus4_deprecation(alt='.rvalue')
    def _get_value(self):
        """for backwards compat with taurus < 4"""
        try:
            return self.__fix_int(self.rvalue.magnitude)
        except AttributeError:
            return self.rvalue

    @taurus4_deprecation(alt='.rvalue')
    def _set_value(self, value):
        """for backwards compat with taurus < 4"""
        debug('Setting %r to %s' % (value, self.name))

        if self.rvalue is None:  # we do not have a previous rvalue
            import numpy
            dtype = numpy.array(value).dtype
            if numpy.issubdtype(dtype, int) or numpy.issubdtype(dtype, float):
                msg = 'Refusing to set ambiguous value (deprecated .value API)'
                raise ValueError(msg)
            else:
                self.rvalue = value
        elif hasattr(self.rvalue, 'units'):  # we do have it and is a Quantity
            self.rvalue = Quantity(value, units=self.rvalue.units)
        else:  # we do have a previous value and is not a quantity
            self.rvalue = value

    value = property(_get_value, _set_value)

    @taurus4_deprecation(alt='.wvalue')
    def _get_w_value(self):
        """for backwards compat with taurus < 4"""
        debug(repr(self))
        try:
            return self.__fix_int(self.wvalue.magnitude)
        except AttributeError:
            return self.wvalue

    @taurus4_deprecation(alt='.wvalue')
    def _set_w_value(self, value):
        """for backwards compat with taurus < 4"""
        debug('Setting %r to %s' % (value, self.name))

        if self.wvalue is None:  # we do not have a previous wvalue
            import numpy
            dtype = numpy.array(value).dtype
            if numpy.issubdtype(dtype, int) or numpy.issubdtype(dtype, float):
                msg = 'Refusing to set ambiguous value (deprecated .value API)'
                raise ValueError(msg)
            else:
                self.wvalue = value
        elif hasattr(self.wvalue, 'units'):  # we do have it and is a Quantity
            self.wvalue = Quantity(value, units=self.wvalue.units)
        else:  # we do have a previous value and is not a quantity
            self.wvalue = value

    w_value = property(_get_w_value, _set_w_value)

    @property
    @taurus4_deprecation(alt='.error')
    def has_failed(self):
        return self.error

    def __fix_int(self, value):
        """cast value to int if it is an integer.
        Works on scalar and non-scalar values
        """
        if self.__attrType != DataType.Integer:
            return value
        try:
            return int(value)
        except TypeError:
            import numpy
            return numpy.array(value, dtype='int')


class TangoAttribute(TaurusAttribute):

    no_cfg_value = '-----'
    no_unit = 'No unit'
    no_standard_unit = 'No standard unit'
    no_display_unit = 'No display unit'
    no_description = 'No description'
    not_specified = 'Not specified'
    no_min_value = no_max_value = not_specified
    no_min_alarm = no_max_alarm = not_specified
    no_min_warning = no_max_warning = not_specified
    no_delta_t = no_delta_val = not_specified
    no_rel_change = no_abs_change = not_specified
    no_archive_rel_change = no_archive_abs_change = not_specified
    no_archive_period = not_specified

    # helper class property that stores a reference to the corresponding
    # factory
    _factory = None
    _scheme = 'tango'
    _description = 'A Tango Attribute'

    def __init__(self, name='', parent=None, **kwargs):
        # the last attribute value
        self.__attr_value = None

        # the last attribute error
        self.__attr_err = None

        # Lock for protecting the critical read region 
        # where __attr_value and __attr_err are updated
        self.__read_lock = threading.RLock()

        # the change event identifier
        self.__chg_evt_id = None

        # current event subscription state
        self.__subscription_state = SubscriptionState.Unsubscribed
        self.__subscription_event = threading.Event()

        # the parent's HW object (the PyTango Device obj)
        self.__dev_hw_obj = None

        # unit for which a decode warning has already been issued
        self.__already_warned_unit = None

        self.call__init__(TaurusAttribute, name, parent, **kwargs)
        self.__deactivate_polling = False

        attr_info = None
        if parent:
            attr_name = self.getSimpleName()
            try:
                attr_info = parent.attribute_query(attr_name)
            except (AttributeError, PyTango.DevFailed):
                # if PyTango could not connect to the dev
                attr_info = None

        # Set default values in case the attrinfoex is None
        self.writable = False
        dis_level = PyTango.DispLevel.OPERATOR
        self.display_level = display_level_from_tango(dis_level)
        self.tango_writable = PyTango.AttrWriteType.READ
        self._units = self._unit_from_tango(PyTango.constants.UnitNotSpec)
        # decode the Tango configuration attribute (adds extra members)
        self._pytango_attrinfoex = None
        self._decodeAttrInfoEx(attr_info)

        # subscribe to configuration events (unsubscription done at cleanup)
        auto_subscribe_conf = getattr(
            tauruscustomsettings, "TANGO_AUTOSUBSCRIBE_CONF", True
        )
        self.__cfg_evt_id = None
        if auto_subscribe_conf and self.factory().is_tango_subscribe_enabled():
            self._subscribeConfEvents()

    def __del__(self):
        self.cleanUp()

    def cleanUp(self):
        self.trace("[TangoAttribute] cleanUp")
        self._unsubscribeConfEvents()
        self._unsubscribeChangeEvents()
        TaurusAttribute.cleanUp(self)
        self.__dev_hw_obj = None
        self._pytango_attrinfoex = None

    def __getattr__(self, name):
        try:
            return getattr(self._pytango_attrinfoex, name)
        except AttributeError:
            raise AttributeError("'TangoAttribute' object has no attribute %s"
                                 % name)

    def getNewOperation(self, value):
        attr_value = PyTango.AttributeValue()
        attr_value.name = self.getSimpleName()
        attr_value.value = self.encode(value)
        op = WriteAttrOperation(self, attr_value)
        return op

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # PyTango connection
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def isInteger(self, inc_array=False):
        tgtype = self._tango_data_type
        return PyTango.is_int_type(tgtype, inc_array=inc_array)

    def isFloat(self, inc_array=False):
        tgtype = self._tango_data_type
        return PyTango.is_float_type(tgtype, inc_array=inc_array)

    def isBoolean(self, inc_array=False):
        tgtype = self._tango_data_type
        # PyTango.is_bool_type is not implemented in Tango7 and neither in
        # some Tango8, at least 8.1.1. Avoid to use is_bool_type method
        # while taurus is still compatible with these versions.
        # PyTango.is_bool_type(tgtype, inc_array=inc_array)
        if tgtype == PyTango.CmdArgType.DevBoolean:
            return True
        if inc_array and tgtype == PyTango.CmdArgType.DevVarBooleanArray:
            return True
        return False

    def isState(self):
        """
        returns whether the attribute of tango DevState type
        """
        tgtype = self._tango_data_type
        return tgtype == PyTango.CmdArgType.DevState

    def getFormat(self, cache=True):
        return self.format

    def encode(self, value):
        """Translates the given value into a tango compatible value according to
        the attribute data type.

        Raises `pint.DimensionalityError` if value is a Quantity and it
        cannot be expressed in the units of the attribute set in the DB
        """
        if isinstance(value, Quantity):
            # convert to units of the attr in the DB (or raise an exception)
            magnitude = value.to(self._units).magnitude
        else:
            magnitude = value

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
                # changed as a partial workaround to a problem in PyTango
                # writing to DevULong64 attributes (see ALBA RT#29793)
                attrvalue = int(magnitude)
            elif tgtype == PyTango.CmdArgType.DevBoolean:
                try:
                    attrvalue = bool(int(magnitude))
                except:
                    attrvalue = str(magnitude).lower() == 'true'
            elif tgtype == PyTango.CmdArgType.DevUChar:
                attrvalue = int(magnitude)
            elif tgtype in (PyTango.CmdArgType.DevState,
                            PyTango.CmdArgType.DevEncoded):
                attrvalue = magnitude
            else:
                attrvalue = str(magnitude)
        elif fmt in (DataFormat._1D, DataFormat._2D):
            if PyTango.is_int_type(tgtype):
                # cast to integer because the magnitude conversion gives floats
                attrvalue = numpy.array(magnitude, copy=False, dtype='int64')
            elif tgtype == PyTango.CmdArgType.DevUChar:
                attrvalue = magnitude.view('uint8')
            else:
                attrvalue = magnitude
        else:
            attrvalue = str(magnitude)
        return attrvalue

    def decode(self, attr_value):
        """Decodes a value that was received from PyTango into the expected
        representation"""
        if self._pytango_attrinfoex is None:
            self.getAttributeInfoEx(cache=False)
            self._decodeAttrInfoEx()
        value = TangoAttrValue(pytango_dev_attr=attr_value, attr=self)
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
                except PyTango.DevFailed as df:
                    for err in df.args:
                        # Handle old device servers
                        if err.reason == 'API_UnsupportedFeature':
                            dev.write_attribute(name, value)
                            result = dev.read_attribute(name)
                            break
                    else:
                        raise df
                self.poll(single=False, value=result, time=time.time())
                return self.decode(result)
            else:
                dev.write_attribute(name, value)
                return None
        except PyTango.DevFailed as df:
            err = df.args[0]
            self.error("[Tango] write failed (%s): %s" %
                       (err.reason, err.desc))
            raise df
        except Exception as e:
            self.error("[Tango] write failed: %s" % str(e))
            raise e

    def poll(self,  single=True, value=None, time=None, error=None):
        """ Notify listeners when the attribute has been polled"""
        with self.__read_lock:
            try:
                if single:
                    self.read(cache=False)
                else:
                    value = self.decode(value)
                    self.__attr_err = error
                    if self.__attr_err:

                        raise self.__attr_err
                    # Avoid "valid-but-outdated" notifications
                    # if FILTER_OLD_TANGO_EVENTS is enabled
                    # and the given timestamp is older than the timestamp
                    # of the cached value
                    filter_old_event = getattr(tauruscustomsettings,
                                               'FILTER_OLD_TANGO_EVENTS',
                                               False)
                    if (self.__attr_value is not None
                            and filter_old_event
                            and time is not None
                            and time < self.__attr_value.time.totime()
                       ):
                        return
                    self.__attr_value = value
            except PyTango.DevFailed as df:
                self.__subscription_event.set()
                self.debug("Error polling: %s" % df.args[0].desc)
                self.traceback()
                self.fireEvent(TaurusEventType.Error, self.__attr_err)
            except Exception as e:
                self.__subscription_event.set()
                self.debug("Error polling: %s" % str(e))
                self.fireEvent(TaurusEventType.Error, self.__attr_err)
            else:
                self.__subscription_event.set()
                self.fireEvent(TaurusEventType.Periodic, self.__attr_value)

    def read(self, cache=True):
        """ Returns the current value of the attribute.

        If `cache` is not False, or expired, or the attribute has events
        active, then it will return the local cached value. Otherwise it will
        read the attribute value from the tango device.

        The cached value expires if it is older than the value (im ms) passed 
        as the `cache` argument or the *polling period* if `cache==True` 
        (default). If the cache is expired a reading will be done just as if 
        cache was False.

        :param cache: use cache value or make readout, eventually pass a
             cache's expiration period in milliseconds
        :type cache: :obj:`bool` or :obj:`float`
        :return: attribute value
        :rtype: :obj:`~taurus.core.tango.TangoAttributeValue`
        """
        curr_time = time.time()
        if cache:
            try:
                attr_timestamp = self.__attr_value.time.totime()
            except AttributeError:
                attr_timestamp = 0
            dt = (curr_time - attr_timestamp) * 1000
            if cache is True:  # cache *is* a bool True
                expiration_period = self.getPollingPeriod()
            else:  # cache is a non-zero numeric value
                expiration_period = cache
            if dt < expiration_period:
                if self.__attr_value is not None:
                    return self.__attr_value
                elif self.__attr_err is not None:
                    self.debug("[Tango] read from cache failed (%s): %s",
                               self.fullname, self.__attr_err)
                    raise self.__attr_err

        if not cache or (self.__subscription_state in 
                         (SubscriptionState.PendingSubscribe,
                          SubscriptionState.Unsubscribed)
                         and not self.isPollingActive()):
            with self.__read_lock:
                try:
                    dev = self.getParentObj()
                    v = dev.read_attribute(self.getSimpleName())
                    self.__attr_value = self.decode(v)
                    self.__attr_err = None
                    return self.__attr_value
                except PyTango.DevFailed as df:
                    self.__attr_value = None
                    self.__attr_err = df
                    err = df.args[0]
                    self.debug("[Tango] read failed (%s): %s",
                               err.reason, err.desc)
                    raise df
                except Exception as e:
                    self.__attr_value = None
                    self.__attr_err = e
                    self.debug("[Tango] read failed: %s", e)
                    raise e
        elif self.__subscription_state in (SubscriptionState.Subscribing,
                                           SubscriptionState.PendingSubscribe):
            self.__subscription_event.wait()

        if self.__attr_err is not None:
            raise self.__attr_err
        return self.__attr_value


    def getAttributeProxy(self):
        """Convenience method that creates and returns a PyTango.AttributeProxy
        object"""
        return PyTango.AttributeProxy(self.getFullName())

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API for listeners
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def __fireRegisterEvent(self, listener):
        '''fire the first config and change (or error) events'''
        try:
            v = self.read()
            # note: it may seem redundant, but some widgets may only react to
            # one or another type, so we should send both for bck-compat
            # Taurus4 widgets should never use config events since the same info
            # is always emitted in a change event
            self.fireEvent(TaurusEventType.Config, v, listener)
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
            self._subscribeChangeEvents()

        # if initial_subscription_state == SubscriptionState.Subscribed:
        if (len(listeners) > 1
            and (initial_subscription_state == SubscriptionState.Subscribed 
                 or self.isPollingActive())
           ):
            sm = self._serialization_mode
            if sm == TaurusSerializationMode.TangoSerial:
                self.__fireRegisterEvent((listener,))
            else:
                job = _BoundMethodWeakrefWithCall(self.__fireRegisterEvent)
                Manager().enqueueJob(job,
                                     job_args=((listener,),),
                                     serialization_mode=sm)
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
            self._unsubscribeChangeEvents()

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
    
    def getSubscriptionState(self):
        return self.__subscription_state    

    def _process_event_exception(self, ex):
        pass

    def _subscribeChangeEvents(self):
        """ Enable subscription to the attribute events. If change events are
            not supported polling is activated """
            
        if self.__chg_evt_id is not None:
            self.warning("chg events already subscribed (id=%s)"
                       %self.__chg_evt_id)
            return

        if self.__dev_hw_obj is None:
            dev = self.getParentObj()
            if dev is None:
                self.debug("failed to subscribe to chg events: device is None")
                return
            self.__dev_hw_obj = dev.getDeviceProxy()
            if self.__dev_hw_obj is None:
                self.debug("failed to subscribe to chg events: HW is None")
                return

        if not self.factory().is_tango_subscribe_enabled():
            self.enablePolling(True)
            return       

        try:
            self.__subscription_state = SubscriptionState.Subscribing
            self._call_dev_hw_subscribe_event(False)
        except:
            self.__subscription_state = SubscriptionState.PendingSubscribe
            self._activatePolling()
            self._call_dev_hw_subscribe_event(True)
                
    def _call_dev_hw_subscribe_event(self, stateless=True):
        """ Executes event subscription on parent TangoDevice objectName
        """
        
        if self.__chg_evt_id is not None:
            self.warning("chg events already subscribed (id=%s)",
                         self.__chg_evt_id)
            return
                
        attr_name = self.getSimpleName()

        # connects to self.push_event callback
        # TODO: _BoundMethodWeakrefWithCall is used as workaround for
        # PyTango #185 issue
        self.__chg_evt_id = self.__dev_hw_obj.subscribe_event(
                attr_name, PyTango.EventType.CHANGE_EVENT,
                _BoundMethodWeakrefWithCall(self.push_event), [], stateless)
        
        return self.__chg_evt_id
                
    def _unsubscribeChangeEvents(self):
        # Careful in this method: This is intended to be executed in the cleanUp
        # so we should not access external objects from the factory, like the
        # parent object
        
        if self.__dev_hw_obj is not None and self.__chg_evt_id is not None:
            self.trace("Unsubscribing to change events (ID=%d)",
                       self.__chg_evt_id)
            try:
                self.__dev_hw_obj.unsubscribe_event(self.__chg_evt_id)
                self.__chg_evt_id = None
            except PyTango.DevFailed as df:
                if len(df.args) and df.args[0].reason == 'API_EventNotFound':
                    # probably tango shutdown has been initiated before and
                    # it unsubscribed from events itself
                    pass
                else:
                    self.debug("Failed: %s", df.args[0].desc)
                    self.trace(str(df))
        self._deactivatePolling()
        self.__subscription_state = SubscriptionState.Unsubscribed

    def _subscribeConfEvents(self):
        """ Enable subscription to the attribute configuration events."""
        self.trace("Subscribing to configuration events...")

        if self.__cfg_evt_id is not None:
            self.warning("cfg events already subscribed (id=%s)"
                       %self.__cfg_evt_id)
            return
        
        if self.__dev_hw_obj is None:
            dev = self.getParentObj()
            if dev is None:
                self.debug("failed to subscribe to cfg events: device is None")
                return
            self.__dev_hw_obj = dev.getDeviceProxy()
            if self.__dev_hw_obj is None:
                self.debug("failed to subscribe to cfg events: HW is None")
                return

        attr_name = self.getSimpleName()
        try:
            # connects to self.push_event callback
            # TODO: _BoundMethodWeakrefWithCall is used as workaround for
            # PyTango #185 issue
            self.__cfg_evt_id = self.__dev_hw_obj.subscribe_event(
                attr_name,
                PyTango.EventType.ATTR_CONF_EVENT,
                _BoundMethodWeakrefWithCall(self.push_event), [], True)
        except PyTango.DevFailed as e:
            self.debug("Error trying to subscribe to CONFIGURATION events.")
            self.traceback()
            # Subscription failed either because event mechanism is not available
            # or because the device server is not running.
            # The first possibility is assumed so an attempt to get the configuration
            # manually is done
            # TODO decide what should be done here
            try:
                attrinfoex = self.__dev_hw_obj.attribute_query(attr_name)
                self._decodeAttrInfoEx(attrinfoex)
            except:
                self.debug("Error getting attribute configuration")
                self.traceback()
                
    def _unsubscribeConfEvents(self):
        # Careful in this method: This is intended to be executed in the cleanUp
        # so we should not access external objects from the factory, like the
        # parent object
        
        if self.__cfg_evt_id is not None and self.__dev_hw_obj is not None:
            self.trace("Unsubscribing to configuration events (ID=%s)",
                       str(self.__cfg_evt_id))
            try:
                self.__dev_hw_obj.unsubscribe_event(self.__cfg_evt_id)
                self.__cfg_evt_id = None
            except PyTango.DevFailed as e:
                self.debug("Error trying to unsubscribe configuration events")
                self.trace(str(e))
                
    def subscribePendingEvents(self):
        """ Execute delayed event subscription
        """                
        if (self.__subscription_state == SubscriptionState.Unsubscribed 
                          or self.isPollingActive()):
            self.__subscription_state = SubscriptionState.PendingSubscribe
        self._subscribeConfEvents()
        self._call_dev_hw_subscribe_event(True)

    def push_event(self, event):
        """Method invoked by the PyTango layer when an event occurs.
        It propagates the event to listeners and delegates other tasks to
        specific handlers for different event types.
        """
        with self.__read_lock:

            # if it is a configuration event
            if isinstance(event, PyTango.AttrConfEventData):
                etype, evalue = self._pushConfEvent(event)
            # if it is an attribute event
            else:
                etype, evalue = self._pushAttrEvent(event)

            # notify the listeners if required (i.e, if etype is not None)
            if etype is None:
                return
            manager = Manager()
            listeners = tuple(self._listeners)
            sm = self._serialization_mode
            if sm == TaurusSerializationMode.TangoSerial:
                self.fireEvent(etype, evalue, listeners=listeners)
            else:
                job = _BoundMethodWeakrefWithCall(self.fireEvent)
                manager.enqueueJob(job, job_args=(etype, evalue),
                                   job_kwargs={'listeners': listeners},
                                   serialization_mode=sm)

        # Deactivate polling in case of PyTango.DevFailed
        # it must be managed out of the critical region to avoid deadlock
        if self.__deactivate_polling:
            self.__deactivate_polling = False
            self._deactivatePolling()

    def _pushAttrEvent(self, event):
        """Handler of (non-configuration) events from the PyTango layer.
        It handles the subscription and the (de)activation of polling

        :param event: (A PyTango event)

        :return: (evt_type, evt_value)  Tuple containing the event type and the
                 event value. evt_type is a `TaurusEventType` (or None to
                 indicate that there should not be notification to listeners).
                 evt_value is a TaurusValue, an Exception, or None.
        """
        if not event.err:
            attr_value = self.decode(event.attr_value)
            filter_old_event = getattr(tauruscustomsettings,
                                       'FILTER_OLD_TANGO_EVENTS', False)
            time = event.attr_value.time.totime()

            # Discard "valid" events if the attribute value is not None
            # and FILTER_OLD_TANGO_EVENTS is enabled
            # and the given timestamp is older than the timestamp
            # of the cache value
            if (self.__attr_value is not None
                and self.__subscription_state == SubscriptionState.Subscribed
                and filter_old_event
                and time < self.__attr_value.time.totime()):
                return [None, None]

            self.__attr_value = attr_value
            self.__attr_err = None
            self.__subscription_state = SubscriptionState.Subscribed
            self.__subscription_event.set()
            if not self.isPollingForced():
                self.disablePolling()
            return TaurusEventType.Change, self.__attr_value

        elif event.errors[0].reason in EVENT_TO_POLLING_EXCEPTIONS:
            if not self.isPollingActive():
                self.info("Activating polling. Reason: %s",
                          event.errors[0].reason)
                self.__subscription_state = SubscriptionState.PendingSubscribe
                self._activatePolling()
            return [None, None]

        else:
            self.__attr_value, self.__attr_err = None, PyTango.DevFailed(
                *event.errors)
            self.__subscription_state = SubscriptionState.Subscribed
            self.__subscription_event.set()
            self.__deactivate_polling = True
            return TaurusEventType.Error, self.__attr_err

    def _pushConfEvent(self, event):
        """Handler of AttrConfEventData events from the PyTango layer.

        :param event: (PyTango.AttrConfEventData)

        :return: (evt_type, evt_value)  Tuple containing the event type and the
                 event value. evt_type is a `TaurusEventType` (or None to
                 indicate that there should not be notification to listeners).
                 evt_value is a TaurusValue, an Exception, or None.
        """
        if not event.err:
            # update conf-related attributes
            self._decodeAttrInfoEx(event.attr_conf)
            # make sure that there is a self.__attr_value
            if self.__attr_value is None:
                # TODO: maybe we can avoid this read?
                self.__attr_value = self.getValueObj(cache=False)
            return TaurusEventType.Config, self.__attr_value

        else:
            self.__attr_value, self.__attr_err = None, PyTango.DevFailed(
                *event.errors)
            return TaurusEventType.Error, self.__attr_err

    def isWrite(self, cache=True):
        return self.getTangoWritable(cache) == PyTango.AttrWriteType.WRITE

    def isReadOnly(self, cache=True):
        return not self.getTangoWritable(cache) == PyTango.AttrWriteType.READ

    def isReadWrite(self, cache=True):
        return self.getTangoWritable(cache) == PyTango.AttrWriteType.READ_WRITE

    def getTangoWritable(self, cache=True):
        """like TaurusAttribute.isWritable(), but it returns a
        PyTango.AttrWriteType instead of a bool"""
        return self.tango_writable

    def getLabel(self, cache=True):
        return self._label

    def getRange(self, cache=True):
        return self._range

    def getLimits(self, cache=True):
        return self.getRange(cache)

    def getRanges(self, cache=True):
        return self.getRange()

    def getAlarms(self, cache=True):
        return self._alarm

    def getWarnings(self, cache=True):
        return self._warning

    def getMaxDim(self, cache=True):
        return self.max_dim_x, self.max_dim_y

    def setLimits(self, low, high):
        self.setRange([low, high])

    def setLabel(self, lbl):
        TaurusAttribute.setLabel(self, lbl)
        infoex = self._pytango_attrinfoex or PyTango.AttributeInfoEx()
        infoex.label = lbl
        self._applyConfig()

    def setRange(self, *limits):
        if isinstance(limits[0], list):
            limits = limits[0]
        low, high = limits
        low = Quantity(low)
        if low.unitless:
            low = Quantity(low.magnitude, self._units)
        high = Quantity(high)
        if high.unitless:
            high = Quantity(high.magnitude, self._units)
        TaurusAttribute.setRange(self, [low, high])
        infoex = self._pytango_attrinfoex or PyTango.AttributeInfoEx()
        if low.magnitude != float('-inf'):
            infoex.min_value = str(low.to(self._units).magnitude)
        else:
            infoex.min_value = 'Not specified'
        if high.magnitude != float('inf'):
            infoex.max_value = str(high.to(self._units).magnitude)
        else:
            infoex.max_value = 'Not specified'
        self._applyConfig()

    def setWarnings(self, *limits):
        if isinstance(limits[0], list):
            limits = limits[0]
        low, high = limits
        low = Quantity(low)
        if low.unitless:
            low = Quantity(low.magnitude, self._units)
        high = Quantity(high)
        if high.unitless:
            high = Quantity(high.magnitude, self._units)
        TaurusAttribute.setWarnings(self, [low, high])
        infoex = self._pytango_attrinfoex or PyTango.AttributeInfoEx()
        if low.magnitude != float('-inf'):
            infoex.alarms.min_warning = str(low.to(self._units).magnitude)
        else:
            infoex.alarms.min_warning = 'Not specified'
        if high.magnitude != float('inf'):
            infoex.alarms.max_warning = str(high.to(self._units).magnitude)
        else:
            infoex.alarms.max_warning = 'Not specified'
        self._applyConfig()

    def setAlarms(self, *limits):
        if isinstance(limits[0], list):
            limits = limits[0]
        low, high = limits
        low = Quantity(low)
        if low.unitless:
            low = Quantity(low.magnitude, self._units)
        high = Quantity(high)
        if high.unitless:
            high = Quantity(high.magnitude, self._units)
        TaurusAttribute.setAlarms(self, [low, high])
        infoex = self._pytango_attrinfoex or PyTango.AttributeInfoEx()
        if low.magnitude != float('-inf'):
            infoex.alarms.min_alarm = str(low.to(self._units).magnitude)
        else:
            infoex.alarms.min_alarm = 'Not specified'
        if high.magnitude != float('inf'):
            infoex.alarms.max_alarm = str(high.to(self._units).magnitude)
        else:
            infoex.alarms.max_alarm = 'Not specified'
        self._applyConfig()

    def _applyConfig(self):
        config = self._pytango_attrinfoex or PyTango.AttributeInfoEx()
        self.setConfigEx(config)

    def _decodeAttrInfoEx(self, pytango_attrinfoex=None):
        if pytango_attrinfoex is None:
            return

        self._pytango_attrinfoex = i = pytango_attrinfoex

        self.writable = i.writable != PyTango.AttrWriteType.READ
        self._label = i.label
        self.data_format = data_format_from_tango(i.data_format)
        desc = description_from_tango(i.description)
        if desc != "":
            self._description = desc
        self.type = data_type_from_tango(i.data_type)
        ###############################################################
        # changed in taurus4: range, alarm and warning now return
        # quantities if appropriate
        if self.isNumeric():
            units = self._unit_from_tango(i.unit)
        else:
            units = UR.parse_units(None)

        if PyTango.is_numerical_type(i.data_type, inc_array=True):
            Q_ = partial(quantity_from_tango_str, units=units,
                         dtype=i.data_type)
            ninf, inf = float('-inf'), float('inf')

            min_value = Q_(i.min_value)
            if min_value is None:
                min_value = Quantity(ninf, units)
            max_value = Q_(i.max_value)
            if max_value is None:
                max_value = Quantity(inf, units)
            min_alarm = Q_(i.alarms.min_alarm)
            if min_alarm is None:
                min_alarm = Quantity(ninf, units)
            max_alarm = Q_(i.alarms.max_alarm)
            if max_alarm is None:
                max_alarm = Quantity(inf, units)
            min_warning = Q_(i.alarms.min_warning)
            if min_warning is None:
                min_warning = Quantity(ninf, units)
            max_warning = Q_(i.alarms.max_warning)
            if max_warning is None:
                max_warning = Quantity(inf, units)

            self._range = [min_value, max_value]
            self._warning = [min_warning, max_warning]
            self._alarm = [min_alarm, max_alarm]

        ###############################################################
        # The following members will be accessed via __getattr__
        # self.standard_unit
        # self.display_unit
        # self.disp_level
        ###############################################################
        # Tango-specific extension of TaurusConfigValue
        self.display_level = display_level_from_tango(i.disp_level)
        self.tango_writable = i.writable
        self.max_dim = i.max_dim_x, i.max_dim_y
        ###############################################################
        fmt = standard_display_format_from_tango(i.data_type, i.format)
        self.format_spec = fmt.lstrip('%')  # format specifier
        match = re.search(r"[^\.]*\.(?P<precision>[0-9]+)[eEfFgG%]", fmt)
        if match:
            self.precision = int(match.group(1))
        elif re.match(r"%[0-9]*d", fmt):
            self.precision = 0
        # self._units and self._display_format is to be used by
        # TangoAttrValue for performance reasons. Do not rely on it in other
        # code
        self._units = units

    @property
    @deprecation_decorator(alt='format_spec or precision', rel='4.0.4')
    def format(self):
        i = self._pytango_attrinfoex or PyTango.AttributeInfoEx()
        return standard_display_format_from_tango(i.data_type, i.format)

    @property
    def _tango_data_type(self):
        '''returns the *tango* (not Taurus) data type'''
        i = self._pytango_attrinfoex or PyTango.AttributeInfoEx()
        return i.data_type

    def _unit_from_tango(self, unit):
        # silently treat unit-not-defined as unitless
        # TODO: consider logging that unit-not-defined is treated as unitless
        # TODO: See https://github.com/taurus-org/taurus/issues/584 and
        # https://github.com/taurus-org/taurus/pull/662
        # The extra comparison to "No unit" is necessary where
        # server/database runs Tango 7 or 8 and client runs higher versions.
        if unit == PyTango.constants.UnitNotSpec or unit == "No unit":
            unit = None
        try:
            return UR.parse_units(unit)
        except Exception as e:
            # TODO: Maybe we could dynamically register the unit in the UR
            msg = 'Unknown unit "%s" (will be treated as unitless)'
            if self.__already_warned_unit == unit:
                self.debug(msg, unit)
            else:
                self.warning(msg, unit)
                self.debug('%r', e)
                self.__already_warned_unit = unit
            return UR.parse_units(None)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Deprecated methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @taurus4_deprecation(alt=".description")
    def getDescription(self, cache=True):
        return self.description

    @taurus4_deprecation(alt=".description")
    def setDescription(self, descr):
        self.description = descr

    @taurus4_deprecation()
    def isInformDeviceOfErrors(self):
        return False

    @taurus4_deprecation(dbg_msg='Deprecated method')
    def displayValue(self, value):
        return str(value)

    @taurus4_deprecation(alt='getLabel')
    def getDisplayValue(self, cache=True):
        attrvalue = self.getValueObj(cache=cache)
        if not attrvalue:
            return None
        v = attrvalue.rvalue

        return self.displayValue(v)

    @taurus4_deprecation(alt='.rvalue.units')
    def getStandardUnit(self, cache=True):
        try:
            return str(self.getValueObj(cache).rvalue.units)
        except:
            return None

    @taurus4_deprecation(alt='.rvalue.units')
    def getDisplayUnit(self, cache=True):
        try:
            return str(self.getValueObj(cache).rvalue.units)
        except:
            return None

    @taurus4_deprecation(dbg_msg='Do not use')
    def getDisplayWriteValue(self, cache=True):
        raise NotImplementedError("Not available since Taurus4")

    @taurus4_deprecation(alt='isWritable')
    def getWritable(self, cache=True):
        return self.isWritable(cache)

    @taurus4_deprecation(alt='self.data_format')
    def isScalar(self, cache=True):
        # cache is ignored, it is only for back. compat.
        return self.data_format == DataFormat._0D

    @taurus4_deprecation(alt='self.data_format')
    def isSpectrum(self, cache=True):
        # cache is ignored, it is only for back. compat.
        return self.data_format == DataFormat._1D

    @taurus4_deprecation(alt='self.data_format')
    def isImage(self):
        return self.data_format == DataFormat._2D

    @taurus4_deprecation(alt='getMaxDim')
    def getMaxDimX(self, cache=True):
        dim = self.getMaxDim(cache)
        if dim:
            return dim[0]
        else:
            return None

    @taurus4_deprecation(alt='getMaxDim')
    def getMaxDimY(self, cache=True):
        dim = self.getMaxDim(cache)
        if dim:
            return dim[1]
        else:
            return None

    @taurus4_deprecation(dbg_msg='Deprecated method')
    def getShape(self, cache=True):
        if self.isScalar(cache):
            return ()
        elif self.isSpectrum():
            return (self.getMaxDimX(),)
        else:
            return self.getMaxDim()

    @taurus4_deprecation(alt='getAttributeInfoEx')
    def getParam(self, param_name):
        """ Get attributes of AttributeInfoEx (PyTango)
        """
        try:
            return getattr(self._pytango_attrinfoex, param_name)
        except:
            return None

    @taurus4_deprecation(alt='PyTango')
    def setParam(self, param_name, value):
        """ Set attributes of AttributeInfoEx (PyTango)
        """
        if hasattr(self._pytango_attrinfoex, param_name):
            setattr(self._pytango_attrinfoex, param_name, str(value))
        self._applyConfig()

    @taurus4_deprecation(alt='self')
    def getConfig(self):
        """Returns the current configuration of the attribute."""
        return weakref.proxy(self)

    def getAttributeInfoEx(self, cache=True):
        if not cache:
            try:
                attr_name = self.getSimpleName()
                attrinfoex = self.__dev_hw_obj.attribute_query(attr_name)
                self._decodeAttrInfoEx(attrinfoex)
            except Exception as e:
                self.debug("Error getting attribute configuration: %s", e)
                self.traceback()

        return self._pytango_attrinfoex

    @taurus4_deprecation(alt='.rvalue.units')
    def getUnit(self, cache=True):
        try:
            return str(self.getValueObj(cache).rvalue.units)
        except:
            return None

    @taurus4_deprecation(alt='.rvalue.units')
    def _set_unit(self, value):
        '''for backwards compat with taurus < 4'''
        extra_msg = 'Ignoring setting of units of %s to %r' % (self.name,
                                                               value)
        self.debug(extra_msg)

    @taurus4_deprecation(alt='getMinRange')
    def getMinValue(self, cache=True):
        return self.getMinRange()

    @taurus4_deprecation(alt='getMaxRange')
    def getMaxValue(self, cache=True):
        return self.getMaxRange()

    @taurus4_deprecation(alt='getRange')
    def getCLimits(self):
        if self._pytango_attrinfoex is not None:
            value = [self._pytango_attrinfoex.min_value,
                     self._pytango_attrinfoex.max_value]
        else:
            value = [self.not_specified, self.not_specified]
        return value

    @taurus4_deprecation(alt='getAlarms')
    def getCAlarms(self):
        if self._pytango_attrinfoex is not None:
            value = [self._pytango_attrinfoex.min_alarm,
                     self._pytango_attrinfoex.max_alarm]
        else:
            value = [self.not_specified, self.not_specified]
        return value

    @taurus4_deprecation(alt='getWarnings')
    def getCWarnings(self):
        if self._pytango_attrinfoex is not None:
            value = [self._pytango_attrinfoex.alarms.min_warning,
                     self._pytango_attrinfoex.alarms.max_warning]
        else:
            value = [self.not_specified, self.not_specified]
        return value

    @taurus4_deprecation(alt='getRange + getAlarms + getWarnings')
    def getCRanges(self):
        if self._pytango_attrinfoex is not None:
            value = [self._pytango_attrinfoex.min_value,
                     self._pytango_attrinfoex.min_alarm,
                     self._pytango_attrinfoex.alarms.min_warning,
                     self._pytango_attrinfoex.alarms.max_warning,
                     self._pytango_attrinfoex.max_alarm,
                     self._pytango_attrinfoex.max_value]
        else:
            value = [self.not_specified, self.not_specified,
                     self.not_specified, self.not_specified,
                     self.not_specified, self.not_specified]
        return value

    @taurus4_deprecation(alt='.alarms[0]')
    def getMinAlarm(self):
        if self._pytango_attrinfoex is None:
            return None
        return self._pytango_attrinfoex.alarms.min_alarm

    @taurus4_deprecation(alt='.alarms[1]')
    def getMaxAlarm(self):
        if self._pytango_attrinfoex is None:
            return None
        return self._pytango_attrinfoex.alarms.max_alarm

    @taurus4_deprecation(alt='.warnings[0]')
    def getMinWarning(self):
        if self._pytango_attrinfoex is None:
            return None
        return self._pytango_attrinfoex.alarms.min_warning

    @taurus4_deprecation(alt='.warnings[1]')
    def getMaxWarning(self):
        if self._pytango_attrinfoex is None:
            return None
        return self._pytango_attrinfoex.alarms.max_warning

    @taurus4_deprecation(alt='.alarms')
    def setMinAlarm(self, value):
        if self._pytango_attrinfoex is None:
            self._pytango_attrinfoex.alarms.min_alarm = str(value)
            self._applyConfig()

    @taurus4_deprecation(alt='.alarms')
    def setMaxAlarm(self, value):
        if self._pytango_attrinfoex is None:
            self._pytango_attrinfoex.alarms.max_alarm = str(value)
            self._applyConfig()

    @taurus4_deprecation(alt='.warnings')
    def setMinWarning(self, value):
        if self._pytango_attrinfoex is None:
            self._pytango_attrinfoex.alarms.min_warning = str(value)
            self._applyConfig()

    @taurus4_deprecation(alt='.warnings')
    def setMaxWarning(self, value):
        if self._pytango_attrinfoex is None:
            self._pytango_attrinfoex.alarms.max_warning = str(value)
            self._applyConfig()

    # deprecated property!
    unit = property(getUnit, _set_unit)
    climits = property(getCLimits)
    calarms = property(getCAlarms)
    cwarnings = property(getCAlarms)
    cranges = property(getCRanges)

    min_alarm = property(getMinAlarm, setMinAlarm)
    max_alarm = property(getMaxAlarm, setMaxAlarm)
    min_warning = property(getMinWarning, setMinWarning)
    max_warning = property(getMaxWarning, setMaxWarning)

    # properties
    label = property(getLabel, setLabel)
    range = property(getRange, setRange)
    warnings = property(getWarnings, setWarnings)
    alarms = property(getAlarms, setAlarms)

    @property
    def description(self):
        return self._description

    @property
    def dev_alias(self):
        self.deprecated(dep='dev_alias', alt='getParentObj().name', rel='tep14')
        parent = self.getParentObj()
        if parent is None:
            return None
        else:
            return parent.name

    @description.setter
    def description(self, descr):
        if descr != self._description:
            if descr == '':
                descr = 'A Tango Attribute'
            self._description = descr
            self._applyConfig()


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

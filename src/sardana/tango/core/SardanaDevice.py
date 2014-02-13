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

"""Generic Sardana Tango device module"""

from __future__ import with_statement

__all__ = ["SardanaDevice", "SardanaDeviceClass"]

__docformat__ = 'restructuredtext'

import time
import threading

import PyTango.constants
from PyTango import Device_4Impl, DeviceClass, Util, DevState, \
    AttrQuality, TimeVal, ArgType, ApiUtil, DevFailed, WAttribute

from taurus.core.util.threadpool import ThreadPool
from taurus.core.util.log import Logger

from util import to_tango_state, NO_DB_MAP


__thread_pool_lock = threading.Lock()
__thread_pool = None

def get_thread_pool():
    """Returns the global pool of threads for Sardana

    :return: the global pool of threads object
    :rtype: taurus.core.util.ThreadPool"""

    global __thread_pool

    if __thread_pool:
        return __thread_pool

    global __thread_pool_lock
    with __thread_pool_lock:
        if __thread_pool is None:
            __thread_pool = ThreadPool(name="EventTH", Psize=1, Qsize=1000)
        return __thread_pool


class SardanaDevice(Device_4Impl, Logger):
    """SardanaDevice represents the base class for all Sardana 
    :class:`PyTango.DeviceImpl` classes"""
    
    def __init__(self, dclass, name):
        """Constructor"""
        self.in_constructor = True
        try:
            Device_4Impl.__init__(self, dclass, name)
            self.init(name)
            Logger.__init__(self, name)
    
            self._state = DevState.INIT
            self._status = 'Waiting to be initialized...'
    
            # access to some tango API (like MultiAttribute and Attribute) is
            # still not thread safe so we have this lock to protect
            # Wa can't always use methods which use internally the
            # C++ AutoTangoMonitor because it blocks the entire tango device.
            self.tango_lock = threading.RLock()
    
            self._event_thread_pool = get_thread_pool()
            self.init_device()
        finally:
            self.in_constructor = False

    def init(self, name):
        """initialize the device once in the object lifetime. Override when
        necessary but **always** call the method from your super class
        
        :param str name: device name"""
        
        db = self.get_database()
        if db is None:
            self._alias = self._get_nodb_device_info()[0]
        else:
            try:
                self._alias = db.get_alias(name)
                if self._alias.lower() == 'nada':
                    self._alias = None
            except:
                self._alias = None

    def get_alias(self):
        """Returns this device alias name

        :return: this device alias
        :rtype: str"""
        return self._alias

    alias = property(get_alias, doc="the device alias name")

    def get_full_name(self):
        """Returns the device full name in format
        dbname:dbport/<domain>/<family>/<member>
        
        :return: this device full name
        :rtype: str"""
        db = self.get_database()
        if db.get_from_env_var():
            db_name = ApiUtil.get_env_var("TANGO_HOST")
        else:
            if db.is_dbase_used():
                db_name = db.get_db_host() + ":" + db.get_db_port()
            else:
                db_name = db.get_file_name()
        return db_name + "/" + self.get_name()

    def init_device(self):
        """Initialize the device. Called during startup after :meth:`init` and
        every time the tango ``Init`` command is executed.
        Override when necessary but **always** call the method from your super
        class"""
        self.set_state(self._state)
        db = self.get_database()
        if db is None:
            self.init_device_nodb()
        else:
            self.get_device_properties(self.get_device_class())

        detect_evts = "state", "status"
        non_detect_evts = ()
        self.set_change_events(detect_evts, non_detect_evts)

    def _get_nodb_device_info(self):
        """Internal method. Returns the device info when tango database is not
        being used (example: in demos)"""
        name = self.get_name()
        tango_class = self.get_device_class().get_name()
        devices = NO_DB_MAP.get(tango_class, ())
        for dev_info in devices:
            if dev_info[1] == name:
                return dev_info

    def init_device_nodb(self):
        """Internal method. Initialize the device when tango database is not
        being used (example: in demos)"""
        _, _, props = self._get_nodb_device_info()
        for prop_name, prop_value in props.items():
            setattr(self, prop_name, prop_value)

    def delete_device(self):
        """Clean the device. Called during shutdown and every time the tango
        ``Init`` command is executed.
        Override when necessary but **always** call the method from your super
        class"""
        pass

    def set_change_events(self, evts_checked, evts_not_checked):
        """Helper method to set change events on attributes
        
        :param evts_checked:
            list of attribute names to activate change events programatically
            with tango filter active
        :type evts_checked: seq<:obj:`str`\>
        :param evts_not_checked:
            list of attribute names to activate change events programatically
            with tango filter inactive. Use this with care! Attributes
            configured with no change event filter may potentially generated a
            lot of events!
        :type evts_not_checked: seq<:obj:`str`\>"""     
        for evt in evts_checked:
            self.set_change_event(evt, True, True)
        for evt in evts_not_checked:
            self.set_change_event(evt, True, False)

    def initialize_dynamic_attributes(self):
        """Initialize dynamic attributes. Default implementation does nothing.
        Override when necessary."""
        pass

    def get_event_thread_pool(self):
        """Return the :class:`~taurus.core.util.ThreadPool` used by sardana to
        send tango events.
        
        :return: the sardana :class:`~taurus.core.util.ThreadPool`
        :rtype: :class:`~taurus.core.util.ThreadPool`"""
        return self._event_thread_pool
    
    def get_attribute_by_name(self, attr_name):
        """Gets the attribute for the given name.
        
        :param attr_name: attribute name
        :type attr_name: str
        :return: the attribute object
        :rtype: :class:`~PyTango.Attribute`"""
        return self.get_device_attr().get_attr_by_name(attr_name)
    
    def get_wattribute_by_name(self, attr_name):
        """Gets the writable attribute for the given name.
        
        :param attr_name: attribute name
        :type attr_name: str
        :return: the attribute object
        :rtype: :class:`~PyTango.WAttribute`"""
        return self.get_device_attr().get_w_attr_by_name(attr_name)
    
    def get_database(self):
        """Helper method to return a reference to the current tango database
        
        :return: the Tango database
        :rtype: :class:`~PyTango.Database`"""
        return Util.instance().get_database()
    
    def set_write_attribute(self, attr, w_value):
        try:
            attr.set_write_value(w_value)
        except DevFailed as df:
            df0 = df[0]
            reason = df0.reason
            # if outside limit prefix the description with the device name
            if reason == PyTango.constants.API_WAttrOutsideLimit:
                desc = self.alias + ": " + df0.desc
                _df = DevFailed(*df[1:])
                PyTango.Except.re_throw_exception(_df, df0.reason, desc, df0.origin)
            raise df
    
    def set_attribute(self, attr, value=None, w_value=None, timestamp=None,
                      quality=None, error=None, priority=1, synch=True):
        """Sets the given attribute value. If timestamp is not given, *now* is
        used as timestamp. If quality is not given VALID is assigned. If error
        is given an error event is sent (with no value and quality INVALID).
        If priority is > 1, the event filter is temporarily disabled so the event
        is sent for sure. If synch is set to True, wait for fire event to finish
        
        :param attr: 
            the tango attribute
        :type attr: :class:`PyTango.Attribute`
        :param value:
            the value to be set (not mandatory if setting an error)
            [default: None]
        :type value: object
        :param w_value:
            the write value to be set (not mandatory)
            [default: None, meaning maintain current write value]
        :type value: object
        :param timestamp:
            the timestamp associated with the operation [default: None, meaning
            use *now* as timestamp]
        :type timestamp: float or :class:`PyTango.TimeVal`
        :param quality:
            attribute quality [default: None, meaning VALID]
        :type quality: :class:`PyTango.AttrQuality`
        :param error:
            a tango DevFailed error or None if not an error [default: None]
        :type error:
            :exc:`PyTango.DevFailed`
        :param priority:
            event priority [default: 1, meaning *normal* priority]. If
            priority is > 1, the event filter is temporarily disabled so the
            event is sent for sure. The event filter is restored to the
            previous value
        :type priority: int
        :param synch:
            If synch is set to True, wait for fire event to finish.
            If False, a job is sent to the sardana thread pool and the method
            returns immediately [default: True]
        """
        set_attr = self.set_attribute_push
        if synch:
            set_attr(attr, value=value, w_value=w_value, timestamp=timestamp,
                     quality=quality, error=error, priority=priority,
                     synch=synch)
        else:
            th_pool = self.get_event_thread_pool()
            th_pool.add(set_attr, None, attr, value=value, w_value=w_value,
                        timestamp=timestamp, quality=quality, error=error,
                        priority=priority, synch=synch)

    def set_attribute_push(self, attr, value=None, w_value=None, timestamp=None,
                           quality=None, error=None, priority=1, synch=True):
        """Synchronous internal implementation of :meth:`set_attribute` (synch
        is passed to this method because it might need to know if it is being
        executed in a synchronous or asynchronous context)."""
        
        if priority > 0 and not synch:
            with self.tango_lock:
                return self._set_attribute_push(attr, value=value,
                        w_value=w_value, timestamp=timestamp, quality=quality,
                        error=error, priority=priority)
        else:
            return self._set_attribute_push(attr, value=value,
                        w_value=w_value, timestamp=timestamp, quality=quality,
                        error=error, priority=priority)

    def _set_attribute_push(self, attr, value=None, w_value=None, timestamp=None,
                            quality=None, error=None, priority=1):
        """Internal method."""
        fire_event = priority > 0

        recover = False
        if priority > 1 and attr.is_check_change_criteria():
            attr.set_change_event(True, False)
            recover = True
        
        attr_name = attr.get_name().lower()

        if value is None and error is None:
            raise Exception("Cannot set value of attribute '%s' with None" % (attr_name,))

        try:
            if error is not None and fire_event:
                self.push_change_event(attr_name, error)
                return

            # some versions of Tango have a memory leak if you do
            # push_change_event(attr_name, value [, ...]) on state or status.
            # This solves the problem.
            if attr_name == "state":
                self.set_state(value)
                if fire_event:
                    self.push_change_event(attr_name)
                return
            elif attr_name == "status":
                self.set_status(value)
                if fire_event:
                    self.push_change_event(attr_name)
                return

            if timestamp is None:
                timestamp = time.time()
            elif isinstance(timestamp, TimeVal):
                timestamp = TimeVal.totime(timestamp)

            if quality is None:
                quality = AttrQuality.ATTR_VALID

            data_type = attr.get_data_type()
            if w_value is not None and isinstance(attr, WAttribute):
                attr.set_write_value(w_value)
            if fire_event:
                if data_type == ArgType.DevEncoded:
                    fmt, data = value
                    args = attr_name, fmt, data, timestamp, quality

                else:
                    args = attr_name, value, timestamp, quality
                self.push_change_event(*args)
            else:
                if data_type == ArgType.DevEncoded:
                    fmt, data = value
                    attr.set_value_date_quality(fmt, data, timestamp, quality)
                else:
                    attr.set_value_date_quality(value, timestamp, quality)
        finally:
            if recover:
                attr.set_change_event(True, True)

    def calculate_tango_state(self, ctrl_state, update=False):
        """Calculate tango state based on the controller state.
        
        :param ctrl_state: the state returned by the controller
        :type ctrl_state: :obj:`~sardana.sardanadefs.State`
        :param bool update:
            if True, set the state of this device with the calculated tango
            state [default: False:
        :return: the corresponding tango state
        :rtype: :class:`PyTango.DevState`"""
        self._state = state = to_tango_state(ctrl_state)
        if update:
            self.set_state(state)
        return state

    def calculate_tango_status(self, ctrl_status, update=False):
        """Calculate tango status based on the controller status.
        
        :param str ctrl_status: the status returned by the controller
        :param bool update:
            if True, set the state of this device with the calculated tango
            state [default: False:
        :return: the corresponding tango state
        :rtype: str"""
        self._status = status = ctrl_status
        if update:
            self.set_status(status)
        return status


class SardanaDeviceClass(DeviceClass):
    """SardanaDeviceClass represents the base class for all Sardana
    :class:`PyTango.DeviceClass` classes"""
    
    #:
    #: Sardana device class properties definition
    #: 
    #: .. seealso:: :ref:`server`
    #:
    class_property_list = {
    }

    #:
    #: Sardana device properties definition
    #: 
    #: .. seealso:: :ref:`server`
    #:
    device_property_list = {
    }

    #:
    #: Sardana device command definition
    #: 
    #: .. seealso:: :ref:`server`
    #:
    cmd_list = {
    }

    #:
    #: Sardana device attribute definition
    #: 
    #: .. seealso:: :ref:`server`
    #:
    attr_list = {
    }

    def __init__(self, name):
        DeviceClass.__init__(self, name)
        self.set_type(name)

    def _get_class_properties(self):
        """Internal method"""
        return dict(ProjectTitle="Sardana", Description="Generic description",
                    doc_url="http://sardana-controls.org/",
                    __icon=self.get_name().lower() + ".png",
                    InheritedFrom=["Device_4Impl"])
    
    def write_class_property(self):
        """Write class properties ``ProjectTitle``, ``Description``, 
        ``doc_url``, ``InheritedFrom`` and ``__icon``"""
        db = self.get_database()
        if db is None:
            return
        db.put_class_property(self.get_name(), self._get_class_properties())

    def dyn_attr(self, dev_list):
        """Invoked to create dynamic attributes for the given devices.
        Default implementation calls
        :meth:`SardanaDevice.initialize_dynamic_attributes` for each device
        
        :param dev_list: list of devices
        :type dev_list: :class:`PyTango.DeviceImpl`"""
        for dev in dev_list:
            try:
                dev.initialize_dynamic_attributes()
            except:
                dev.warning("Failed to initialize dynamic attributes")
                dev.debug("Details:", exc_info=1)

    def device_name_factory(self, dev_name_list):
        """Builds list of device names to use when no Database is being used
        
        :param dev_name_list: list to be filled with device names
        :type dev_name_list: seq<obj:`list`\>"""
        tango_class = self.get_name()
        devices = NO_DB_MAP.get(tango_class, ())
        for dev_info in devices:
            dev_name_list.append(dev_info[1])

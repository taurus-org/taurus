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

"""This module provides the `TangoFactory` object"""

__all__ = ["TangoFactory"]

__docformat__ = "restructuredtext"

try:
    import PyTango
except ImportError:
    # note that if PyTango is not installed the factory will not be available
    from taurus.core.util.log import debug
    msg = 'cannot import PyTango module. ' + \
          'Taurus will not support the "tango" scheme'
    debug(msg)
    raise

from taurus.core.taurusbasetypes import TaurusElementType
from taurus.core.taurusfactory import TaurusFactory
from taurus.core.taurusbasetypes import OperationMode
from taurus.core.taurusexception import TaurusException, DoubleRegistration
from taurus.core.util.log import Logger, taurus4_deprecation
from taurus.core.util.singleton import Singleton
from taurus.core.util.containers import CaselessWeakValueDict, CaselessDict

from .tangodatabase import TangoAuthority
from .tangoattribute import TangoAttribute
from .tangodevice import TangoDevice

_Authority = TangoAuthority
_Attribute = TangoAttribute
_Device = TangoDevice


class TangoFactory(Singleton, TaurusFactory, Logger):
    """A :class:`TaurusFactory` singleton class to provide Tango-specific
    Taurus Element objects (TangoAuthority, TangoDevice, TangoAttribute)

    Tango model names are URI based See https://tools.ietf.org/html/rfc3986.
    For example, a TangoAttribute would be::

        tango://foo.org:1234/a/b/c/d#label
        \___/   \_____/ \__/ \_____/ \___/
          |        |     |      |      |
          |    hostname port  attr     |
          |   \____________/\______/   |
          |         |           |      |
        scheme   authority     path  fragment

    For Tango Elements:

        - The 'scheme' must be the string "tango" (lowercase mandatory)
        - The 'authority' identifies the Tango database (<hostname> and <port>
          are mandatory if authority is given)
        - The 'path' identifies Tango Device and Attributes.
          For devices it must have the format _/_/_ or alias
          For attributes it must have the format _/_/_/_ or devalias/_
        - The 'fragment' is optional and it refers to a member of the model
          object, thus not being part of the model name itself
    """

    #: the list of schemes that this factory supports. For this factory: 'tango'
    #: is the only scheme
    schemes = ("tango",)
    caseSensitive = False
    elementTypesMap = {TaurusElementType.Authority: TangoAuthority,
                       TaurusElementType.Device: TangoDevice,
                       TaurusElementType.Attribute: TangoAttribute
                       }

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization.
           **For internal usage only**"""
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        self.call__init__(TaurusFactory)
        self._polling_enabled = True
        self.reInit()
        self.scheme = 'tango'

    def reInit(self):
        """Reinitialize the singleton"""
        self._default_tango_host = None
        self.dft_db = None
        self.tango_db = CaselessWeakValueDict()
        self.tango_db_queries = CaselessWeakValueDict()
        self.tango_attrs = CaselessWeakValueDict()
        self.tango_devs = CaselessWeakValueDict()
        self.tango_dev_queries = CaselessWeakValueDict()
        self.tango_alias_devs = CaselessWeakValueDict()
        self.polling_timers = {}

        # Plugin device classes
        self.tango_dev_klasses = {}

        # Plugin attribute classes
        self.tango_attr_klasses = CaselessDict()

    def cleanUp(self):
        """Cleanup the singleton instance"""
        self.trace("[TangoFactory] cleanUp")
        for k, v in self.tango_attrs.items():
            v.cleanUp()
        for k, v in self.tango_dev_queries.items():
            v.cleanUp()
        for k, v in self.tango_devs.items():
            v.cleanUp()
        self.dft_db = None
        for k, v in self.tango_db_queries.items():
            v.cleanUp()
        for k, v in self.tango_db.items():
            v.cleanUp()
        self.reInit()

    def getExistingAttributes(self):
        """Returns a new dictionary will all registered attributes on this factory

           :return:  dictionary will all registered attributes on this factory
           :rtype: dict"""
        return dict(self.tango_attrs)

    def getExistingDevices(self):
        """Returns a new dictionary will all registered devices on this factory

           :return:  dictionary will all registered devices on this factory
           :rtype: dict"""
        return dict(self.tango_devs)

    def getExistingDatabases(self):
        """Returns a new dictionary will all registered databases on this factory

           :return:  dictionary will all registered databases on this factory
           :rtype: dict"""
        return dict(self.tango_db)

    def set_default_tango_host(self, tango_host):
        """Sets the new default tango host.

        :param tango_host: (str) the new tango host
        """
        self._default_tango_host = tango_host
        self.dft_db = None

    def registerAttributeClass(self, attr_name, attr_klass):
        """Registers a new attribute class for the attribute name.

           :param attr_name: (str) attribute name
           :param attr_klass: (taurus.core.tango.TangoAttribute) the new class that
                              will handle the attribute
        """
        self.tango_attr_klasses[attr_name] = attr_klass

    def unregisterAttributeClass(self, attr_name):
        """Unregisters the attribute class for the given attribute
           If no class was registered before for the given attribute, this call
           as no effect

           :param attr_name: (str) attribute name
        """
        if self.tango_attr_klasses.has_key(attr_name):
            del self.tango_attr_klasses[attr_name]

    def registerDeviceClass(self, dev_klass_name, dev_klass):
        """Registers a new python class to handle tango devices of the given tango class name

           :param dev_klass_name: (str) tango device class name
           :param dev_klass: (taurus.core.tango.TangoDevice) the new class that will
                             handle devices of the given tango class name
        """
        self.tango_dev_klasses[dev_klass_name] = dev_klass

    def unregisterDeviceClass(self, dev_klass_name):
        """Unregisters the class for the given tango class name
           If no class was registered before for the given attribute, this call
           as no effect

           :param dev_klass_name: (str) tango device class name
        """
        if self.tango_dev_klasses.has_key(dev_klass_name):
            del self.tango_dev_klasses[dev_klass_name]

    def getDatabase(self, name=None):
        '''Deprecated. Use getAuthority instead'''
        return self.getAuthority(name=name)

    def getAuthority(self, name=None):
        """
        Obtain the object corresponding to the given database name or the
        default database if name is None.
        If the corresponding authority object already exists, the existing
        instance is returned. Otherwise a new instance is stored and returned.

        :param name: (str) database name string alias. If None, the
                        default database is used

        :return: (taurus.core.tangodatabase.TangoAuthority) database object
        :raise: (taurus.core.taurusexception.TaurusException) if the given alias is invalid.
        """
        ret = None
        if name is None:
            if self.dft_db is None:
                try:
                    if self._default_tango_host is None:
                        self.dft_db = _Authority()
                    else:
                        name = self._default_tango_host
                        validator = _Authority.getNameValidator()
                        groups = validator.getUriGroups(name)
                        if groups is None:
                            raise TaurusException(
                                "Invalid default Tango authority name %s" % name)
                        self.dft_db = _Authority(host=groups['host'],
                                                 port=groups['port'])
                except:
                    self.debug("Could not create Authority", exc_info=1)
                    raise
                name = self.dft_db.getFullName()
                self.tango_db[name] = self.dft_db
            ret = self.dft_db
        else:
            ret = self.tango_db.get(name)
            if not ret is None:
                return ret
            validator = _Authority.getNameValidator()
            groups = validator.getUriGroups(name)
            if not validator.isValid(name):
                raise TaurusException("Invalid Tango authority name %s" % name)
            try:
                ret = _Authority(host=groups['host'], port=groups['port'])
            except:
                self.debug("Could not create Authority %s", groups['authority'],
                           exc_info=1)

            self.tango_db[name] = ret
        return ret

    def getDevice(self, dev_name, create_if_needed=True, **kw):
        """Obtain the object corresponding to the given tango device name.
           If the corresponding device already exists, the existing instance
           is returned. Otherwise a new instance is stored and returned.

           :param dev_name: (str) tango device name or tango alias for the
                            device. It must be a valid Tango device URI.
                            If authority is not explicit, the default Tango
                            Database will be used
           :param create_if_needed: (bool) If True, the Device is created if it
                                    did not exist previously. If False, it
                                    returns None if it did not exist

           :return: (taurus.core.tango.TangoDevice) a device object
           :raise: (taurus.core.taurusexception.TaurusException) if the given
                   dev_name is invalid.
        """
        d = self.tango_devs.get(dev_name)
        if d is None:
            d = self.tango_alias_devs.get(dev_name)
        if d is not None:
            return d

        validator = _Device.getNameValidator()
        groups = validator.getUriGroups(dev_name)
        if groups is None:
            raise TaurusException("Invalid Tango device name '%s'" % dev_name)

        full_dev_name, _, _ = validator.getNames(dev_name)

        if full_dev_name is None:
            raise TaurusException("Cannot find full name of '%s'" % dev_name)

        d = self.tango_devs.get(full_dev_name)

        if not create_if_needed:
            return d

        if d is None:
            try:
                db = self.getAuthority(groups.get('authority'))
                dev_klass = self._getDeviceClass(
                    db=db, devname=groups['devname'])
                kw['storeCallback'] = self._storeDevice
                kw['parent'] = db
                d = dev_klass(full_dev_name, **kw)
                # device objects will register themselves in this factory
                # so there is no need to do it here
            except DoubleRegistration:
                d = self.tango_devs.get(full_dev_name)
            except:
                self.debug("Error creating device %s", dev_name, exc_info=1)
                raise
        return d

    def getAttribute(self, attr_name, create_if_needed=True, **kwargs):
        """Obtain the object corresponding to the given attribute name.
           If the corresponding attribute already exists, the existing instance
           is returned. Otherwise a new instance is stored and returned.

           :param attr_name: (str) a valid attribute name URI
           :param create_if_needed: (bool) If True, the Attribute is created if
                                    it did not already exist. If False,
                                    None is returned if it did not exist
           :return: (taurus.core.tangoattribute.TangoAttribute) attribute object
           :raise: (taurus.core.taurusexception.TaurusException) if the given
                   alias is invalid.
        """
        attr = self.tango_attrs.get(attr_name)
        if attr is not None:
            return attr

        # Simple approach did not work. Lets build a proper device name
        validator = _Attribute.getNameValidator()
        groups = validator.getUriGroups(attr_name)
        if groups is None:
            raise TaurusException(("Invalid Tango attribute name '%s'") %
                                  attr_name)

        full_attr_name, _, _ = validator.getNames(attr_name)

        if full_attr_name is None:
            raise TaurusException("Cannot find full name of '%s'" % attr_name)

        attr = self.tango_attrs.get(full_attr_name)

        if attr is None:
            dev_name = full_attr_name.rsplit('/', 1)[0]
            try:
                dev = self.getDevice(dev_name)
                if dev is not None:
                    # Do another try in case the Device object created the attribute
                    # itself. This happens for the 'state' attribute
                    attr = self.tango_attrs.get(full_attr_name)
                    if attr is not None:
                        return attr
                    try:
                        attr_klass = self._getAttributeClass(
                            attr_name=attr_name)
                        kwargs['storeCallback'] = self._storeAttribute
                        if not kwargs.has_key('pollingPeriod'):
                            kwargs[
                                'pollingPeriod'] = self.getDefaultPollingPeriod()
                        attr = attr_klass(full_attr_name, dev, **kwargs)
                        # attribute objects will register themselves in this factory
                        # so there is no need to do it here
                    except DoubleRegistration:
                        attr = self.tango_attrs.get(full_attr_name)
            except:
                self.debug("Error creating attribute %s",
                           attr_name, exc_info=1)
                raise
        return attr

    def getAttributeInfo(self, full_attr_name):
        """Deprecated: Use :meth:`taurus.core.tango.TangoFactory.getConfiguration` instead.

           Obtain attribute information corresponding to the given attribute name.
           If the corresponding attribute info already exists, the existing information
           is returned. Otherwise a new information instance is stored and returned.

           :param full_attr_name: (str) attribute name in format: <tango device name>'/'<attribute name>

           :return: (taurus.core.tango.TangoConfiguration) configuration object
        """
        self.deprecated("Use getConfiguration(full_attr_name) instead")
        attr = self.getAttribute(full_attr_name)
        return attr

    @taurus4_deprecation(alt='getAttribute')
    def getConfiguration(self, param):
        """Obtain the object corresponding to the given attribute or full name.
           If the corresponding configuration already exists, the existing instance
           is returned. Otherwise a new instance is stored and returned.

           :param param: (taurus.core.taurusattribute.TaurusAttribute or str)
                         attribute object or full configuration name

           :return: (taurus.core.tango.TangoAttribute) configuration object
        """
        if isinstance(param, str):
            return self.getAttribute(param)
        return param

    def _getAttributeClass(self, **params):
        attr_name = params.get("attr_name")
        attr_klass = self.tango_attr_klasses.get(attr_name, _Attribute)
        return attr_klass

    def _getDeviceClass(self, **kwargs):
        db, dev_name = kwargs.get("db"), kwargs.get("devname")
        if db is None or dev_name is None or len(self.tango_dev_klasses) == 0:
            return _Device
        else:
            if '/' not in dev_name:  # we got an alias... find the devslashname
                dev_name = db.getElementFullName(dev_name)
            try:
                tango_dev_klass = db.get_class_for_device(dev_name)
            except PyTango.DevFailed:
                # sometimes we can't get the class (e.g. dev_name not defined)
                return _Device
            return self.tango_dev_klasses.get(tango_dev_klass, _Device)

    def _storeDevice(self, dev):
        name, alias = dev.getFullName(), dev.getSimpleName()
        exists = self.tango_devs.get(name)
        if not exists is None:
            if exists == dev:
                msg = "%s has already been registered before" % name
            else:
                msg = "%s has already been registered before with a different object!" % name
            self.debug(msg)
            raise DoubleRegistration(msg)
        self.tango_devs[name] = dev
        if not alias is None and len(alias):
            self.tango_alias_devs[alias] = dev

    def _storeAttribute(self, attr):
        name = attr.getFullName()
        exists = self.tango_attrs.get(name)
        if not exists is None:
            if exists == attr:
                msg = "%s has already been registered before" % name
            else:
                msg = "%s has already been registered before with a different object!" % name
            self.debug(msg)
            raise DoubleRegistration(msg)
        self.tango_attrs[name] = attr

    def getExistingAttribute(self, attr_name):
        """Deprecated: use getAtribute with create_if_needed=False
        """
        self.warning(('getExistingAttribute is deprecated. ' +
                      'Use getDevice with create_if_needed=False'))
        return self.getAttribute(attr_name, create_if_needed=False)

    def getExistingDevice(self, dev_name):
        """Deprecated: use getDevice with create_if_needed=False
        """
        self.warning(('getExistingDevice is deprecated. ' +
                      'Use getDevice with create_if_needed=False'))
        return self.getDevice(dev_name, create_if_needed=False)

    def removeExistingDevice(self, dev_or_dev_name):
        """Removes a previously registered device.

           :param dev_or_dev_name: (str or TangoDevice) device name or device object
        """
        if isinstance(dev_or_dev_name, _Device):
            dev = dev_or_dev_name
        else:
            dev = self.getDevice(dev_or_dev_name, create_if_needed=False)
        if dev is None:
            raise KeyError("Device %s not found" % dev_or_dev_name)
        dev.cleanUp()
        full_name = dev.getFullName()
        if self.tango_devs.has_key(full_name):
            del self.tango_devs[full_name]
        simp_name = dev.getSimpleName()
        if self.tango_alias_devs.has_key(simp_name):
            del self.tango_alias_devs[simp_name]

    def removeExistingAttribute(self, attr_or_attr_name):
        """Removes a previously registered attribute.

           :param attr_or_attr_name: (str or TangoAttribute) attribute name or attribute object
        """
        if isinstance(attr_or_attr_name, _Attribute):
            attr = attr_or_attr_name
        else:
            attr = self.getExistingAttribute(attr_or_attr_name)
        if attr is None:
            raise KeyError("Attribute %s not found" % attr_or_attr_name)
        attr.cleanUp()
        full_name = attr.getFullName()
        if self.tango_attrs.has_key(full_name):
            del self.tango_attrs[full_name]

    def isPollingEnabled(self):
        """Tells if the local tango polling is enabled

           :return: (bool) wheter or not the polling is enabled
        """
        return self._polling_enabled

    def disablePolling(self):
        """Disable the application tango polling"""
        if not self.isPollingEnabled():
            return
        self._polling_enabled = False
        for period, timer in self.polling_timers.iteritems():
            timer.stop()

    def enablePolling(self):
        """Enable the application tango polling"""
        if self.isPollingEnabled():
            return
        for period, timer in self.polling_timers.iteritems():
            timer.start()
        self._polling_enabled = True

    def getDatabaseNameValidator(self):
        """Deprecated"""
        self.warning(('getDatabaseNameValidator is deprecated.' +
                      'Use "Authority" instead of "Database"'))
        return self.getAuthorityNameValidator()

    def getAuthorityNameValidator(self):
        """Return TangoAuthorityNameValidator"""
        import tangovalidator
        return tangovalidator.TangoAuthorityNameValidator()

    def getDeviceNameValidator(self):
        """Return TangoDeviceNameValidator"""
        import tangovalidator
        return tangovalidator.TangoDeviceNameValidator()

    def getAttributeNameValidator(self):
        """Return TangoAttributeNameValidator"""
        import tangovalidator
        return tangovalidator.TangoAttributeNameValidator()

    def setOperationMode(self, mode):
        """ Deprecated. setOperationMode(OperationMode mode) -> None
            Sets the operation mode for the Tango system."""
        dep = 'setOperationMode'
        rel = 'Taurus4'
        dbg_msg = "Don't use this method"
        msg = '%s is deprecated (from %s). %s' % (dep, rel, dbg_msg)
        self.deprecated(msg)

    def getOperationMode(self):
        """Deprecated. Gives the current operation mode."""
        dep = 'getOperationMode'
        rel = 'Taurus4'
        dbg_msg = "Don't use this method"
        msg = '%s is deprecated (from %s). %s' % (dep, rel, dbg_msg)
        self.deprecated(msg)
        return OperationMode.ONLINE

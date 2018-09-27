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

"""
Epics module. See __init__.py for more detailed documentation
"""
from __future__ import absolute_import
import weakref
try:
    import epics
except ImportError:
    from taurus.core.util.log import debug
    debug('cannot import epics module. ' +
          'Taurus will not support the "epics" scheme')
    raise
from taurus.core.taurusexception import TaurusException
from taurus.core.util.singleton import Singleton
from taurus.core.util.log import Logger
from taurus.core.taurusbasetypes import TaurusElementType
from taurus.core.taurusfactory import TaurusFactory
from .epicsattribute import EpicsAttribute
from .epicsdevice import EpicsDevice
from .epicsauthority import EpicsAuthority

__all__ = ['EpicsFactory']


class EpicsFactory(Singleton, TaurusFactory, Logger):
    """
    A Singleton class that provides Epics related objects.
    """

    schemes = ("ca", "epics",)
    DEFAULT_DEVICE = 'ca:'
    DEFAULT_AUTHORITY = 'ca://'
    caseSensitive = True
    elementTypesMap = {TaurusElementType.Authority: EpicsAuthority,
                       TaurusElementType.Device: EpicsDevice,
                       TaurusElementType.Attribute: EpicsAttribute
                       }

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        self.call__init__(TaurusFactory)
        if EpicsAttribute is None:
            self.debug('cannot import epics module.'
                       'Taurus will not support the "epics" scheme')
            raise Exception('"epics" module is not available')
        self.epics_attrs = weakref.WeakValueDictionary()
        self.epics_devs = weakref.WeakValueDictionary()

    def getAuthority(self, name=None):
        """Obtain the Epics (ca) authority object.

        :param name: (str) only a dummy authority ("ca://") is supported

        :return: (EpicsAuthority)
        """
        if name is None:
            name = 'ca://'

        v = self.getAuthorityNameValidator()
        if not v.isValid(name):
            raise TaurusException("Invalid ca authority name %s" % name)

        if not hasattr(self, "_auth"):
            self._auth = EpicsAuthority(self.DEFAULT_AUTHORITY)
        return self._auth

    def getDevice(self, dev_name):
        """Obtain the EpicsDevice object.

        :param dev_name: (str) only one dummy device ("") is supported

        :return: (EpicsDevice)

        .. todo:: epics.Device may be wrapped as taurus device...
        """
        validator = self.getDeviceNameValidator()
        names = validator.getNames(dev_name)
        if names is None:
            raise TaurusException("Invalid epics device name %s" % dev_name)
        fullname = names[0]
        d = self.epics_devs.get(fullname, None)
        if d is None:  # if the full name is not there, create one
            auth = self.getAuthority()
        d = EpicsDevice(fullname, parent=auth)
        self.epics_devs[fullname] = d
        return d

    def getAttribute(self, attr_name):
        """Obtain the object corresponding to the given attribute name. If the
        corresponding attribute already exists, the existing instance is
        returned. Otherwise a new instance is stored and returned. The
        device associated to this attribute will also be created if necessary.

        :param attr_name: (str) the attribute name string. See
                          :mod:`taurus.core.epics` for valid attribute names

        :return: (EpicsAttribute)

        :raises: :TaurusException: if the given name is invalid.
        """
        validator = self.getAttributeNameValidator()
        names = validator.getNames(attr_name)
        if names is None:
            raise TaurusException(
                "Invalid epics attribute name %s" % attr_name)
        fullname = names[0]
        a = self.epics_attrs.get(fullname, None)
        if a is None:  # if the full name is not there, create one
            a = EpicsAttribute(fullname, parent=None)  # note: no parent!
            self.epics_attrs[fullname] = a
        return a

    def getAuthorityNameValidator(self):
        """Return EpicsAuthorityNameValidator"""
        from . import epicsvalidator
        return epicsvalidator.EpicsAuthorityNameValidator()

    def getDeviceNameValidator(self):
        """Return EpicsDeviceNameValidator"""
        from . import epicsvalidator
        return epicsvalidator.EpicsDeviceNameValidator()

    def getAttributeNameValidator(self):
        """Return EpicsAttributeNameValidator"""
        from . import epicsvalidator
        return epicsvalidator.EpicsAttributeNameValidator()

if __name__ == "__main__":
    pass

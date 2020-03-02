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

from builtins import object
from taurus.core import TaurusElementType
from taurus.core.taurusvalidator import (TaurusAttributeNameValidator,
                                         TaurusDeviceNameValidator,
                                         TaurusAuthorityNameValidator)
from taurus.core.taurushelper import getSchemeFromName, Factory

__all__ = ['ResourceAuthorityNameValidator', 'ResourceDeviceNameValidator',
           'ResourceAttributeNameValidator']

# Pattern for python variables
PY_VAR = r'(?<![\.a-zA-Z0-9_])[a-zA-Z_][a-zA-Z0-9_]*'


class _ResNameValidator(object):
    """
    Abstract class for all Res validators. Res Name validators should inherit
    first from it and then from the TaurusXXXNameValidator to give its methods
    highest precedence according to the python MRO
    """
    scheme = 'res'
    authority = '(?!)'
    path = r'(?P<_resname>%s)' % PY_VAR
    query = '(?!)'
    fragment = '(?!)'

    pattern = r'^(?P<scheme>%(scheme)s):' + \
              r'((?P<authority>%(authority)s)(?=/))?' + \
              r'(?P<path>%(path)s)' + \
              r'(\?(?P<query>%(query)s))?' + \
              r'(#(?P<fragment>%(fragment)s))?$'

    _elementType = None

    def _getValueValidator(self, name):
        """Return the name validator for the mapped model name scheme

        :param name: (str) resource name
        :return: A specific TaurusValidator
        """
        scheme = getSchemeFromName(name)
        f = Factory(scheme)
        if self._elementType == TaurusElementType.Attribute:
            return f.getAttributeNameValidator()
        elif self._elementType == TaurusElementType.Device:
            return f.getDeviceNameValidator()
        elif self._elementType == TaurusElementType.Authority:
            return f.getAuthorityNameValidator()
        else:
            msg = '_elementType must be one of (Authority, Device, Attribute)'
            raise Exception(msg)

    def _getKey(self, name):

        if self._elementType == TaurusElementType.Attribute:
            g = TaurusAttributeNameValidator.getUriGroups(self, name)
        elif self._elementType == TaurusElementType.Device:
            g = TaurusDeviceNameValidator.getUriGroups(self, name)
        elif self._elementType == TaurusElementType.Authority:
            g = TaurusAuthorityNameValidator.getUriGroups(self, name)
        else:
            msg = '_elementType must be one of (Authority, Device, Attribute)'
            raise Exception(msg)
        if g is None:
            return None
        else:
            return g['_resname']

    def _getValue(self, key):
        return Factory('res').getValue(key)

    def isValid(self, name, *args, **kwargs):
        """Checks validity of the key (resname) and also of the value
        (model name)"""
        key = self._getKey(name)
        if key is None:
            return False
        value = self._getValue(key)
        if value is None:
            return False
        v = self._getValueValidator(value)
        return v.isValid(value, *args, **kwargs)

    def getUriGroups(self, name, *args, **kwargs):
        """Returns the groups for the value extended with '_resname'"""
        key = self._getKey(name)
        if key is None:
            return None
        value = self._getValue(key)
        if value is None:
            return None
        v = self._getValueValidator(value)
        ret = v.getUriGroups(value, *args, **kwargs)
        if ret is None:
            return None
        ret['_resname'] = key
        return ret

    def getNames(self, name, *args, **kwargs):
        """Returns the names of the value"""
        key = self._getKey(name)
        if key is None:
            return None
        value = self._getValue(key)
        if value is None:
            return None
        return self._getValueValidator(value).getNames(value, *args, **kwargs)


class ResourceAuthorityNameValidator(_ResNameValidator,
                                     TaurusAuthorityNameValidator):
    """Validator for res authority names. Apart from the named related to the
    mapped model value, the following named groups are created:

     - _resname: resource name (aka key)
    """
    # authority = r'(?P<_resname>%s)' % PY_VAR
    # path = '(?!)'
    _elementType = TaurusElementType.Authority


class ResourceDeviceNameValidator(_ResNameValidator,
                                  TaurusDeviceNameValidator):
    """Validator for res device names. Apart from the named related to the
    mapped model value, the following named groups are created:

     - _resname: resource name (aka key)
    """
    _elementType = TaurusElementType.Device


class ResourceAttributeNameValidator(_ResNameValidator,
                                     TaurusAttributeNameValidator):
    """Validator for res attribute names. Apart from the named related to the
    mapped model value, the following named groups are created:

     - _resname: resource name (aka key)
    """
    _elementType = TaurusElementType.Attribute

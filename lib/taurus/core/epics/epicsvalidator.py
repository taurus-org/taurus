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
__all__ = ['EpicsAuthorityNameValidator', 'EpicsDeviceNameValidator',
           'EpicsAttributeNameValidator']

import re
from taurus.core.taurusvalidator import (TaurusAttributeNameValidator,
                                         TaurusDeviceNameValidator,
                                         TaurusAuthorityNameValidator)

# legal chars on PV names: a-z A-Z 0-9 _ - : . [ ] < > ;
# ... but "[" "]" and "." are discouraged:
# http://www.aps.anl.gov/epics/tech-talk/2006/msg00431.php
PV_CHARS = r'[a-zA-Z0-9_\-:;\<\>' + r'[\.\[\]]'


class EpicsAuthorityNameValidator(TaurusAuthorityNameValidator):
    """Validator for Epics authority names. For now, the only supported
    authority is "//":
    """
    scheme = '(ca|epics)'
    authority = '//'
    path = '(?!)'
    query = '(?!)'
    fragment = '(?!)'

    def getNames(self, fullname, factory=None):
        if self.isValid(fullname):
            return 'ca://', '//', ''
        return None


class EpicsDeviceNameValidator(TaurusDeviceNameValidator):
    """Validator for Epics device names. Apart from the standard named
    groups (scheme, authority, path, query and fragment), the following named
    groups are created:

     - devname: device name (only empty string allowed for now)

    Note: brackets on the group name indicate that this group will only contain
    a string if the URI contains it.
    """

    scheme = '(ca|epics)'
    authority = EpicsAuthorityNameValidator.authority
    path = r'/(?P<devname>)'  # (only empty string allowed for now)
    query = '(?!)'
    fragment = '(?!)'

    def getNames(self, fullname, factory=None):
        if self.isValid(fullname):
            return 'ca:', '', ''
        return None


class EpicsAttributeNameValidator(TaurusAttributeNameValidator):
    """Validator for Epics attribute names. Apart from the standard named
    groups (scheme, authority, path, query and fragment), the following named
    groups are created:

     - attrname: attribute name (an epics PV name).

    Note: brackets on the group name indicate that this group will only contain
    a value if the URI contains it.
    """
    scheme = '(ca|epics)'
    authority = EpicsAuthorityNameValidator.authority
    path = r'(?P<attrname>%s+?(\.(?P<_field>[A-Z]+))?)' % PV_CHARS
    query = '(?!)'
    fragment = '[^# ]*'

    def getNames(self, fullname, factory=None, fragment=False):
        """reimplemented from :class:`TaurusDeviceNameValidator`"""

        groups = self.getUriGroups(fullname)
        if groups is None:
            return None

        complete = 'ca:%s' % groups['attrname']
        normal = groups['attrname']
        short = normal

        # return fragment if requested
        if fragment:
            key = groups.get('fragment', None)
            return complete, normal, short, key
        return complete, normal, short

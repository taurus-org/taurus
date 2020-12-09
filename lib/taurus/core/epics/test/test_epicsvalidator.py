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

"""Test for taurus.core.epics.test.test_epicsvalidator..."""


__docformat__ = 'restructuredtext'

import sys
import unittest
from taurus.core.test import (valid, invalid, names,
                              AbstractNameValidatorTestCase)
from taurus.core.epics.epicsvalidator import (EpicsAuthorityNameValidator,
                                              EpicsDeviceNameValidator,
                                              EpicsAttributeNameValidator)

# ==============================================================================
# Tests for Epics Authority  name validation
# ==============================================================================
@valid(name='ca://', groups=dict(authority='//'))
@names(name='ca://', out=('ca://', '//', ''))
@names(name='epics://', out=('ca://', '//', ''))
@invalid(name='ca:')
@invalid(name='ca:/')
@invalid(name='ca:///')
@invalid(name='ca://a')
@unittest.skipIf(('epics' in sys.modules) is False,
                 "epics module is not available")
class EpicsAuthValidatorTestCase(AbstractNameValidatorTestCase,
                                 unittest.TestCase):
    validator = EpicsAuthorityNameValidator


# ==============================================================================
# Tests for Epics Device name validation
# ==============================================================================
@valid(name='ca:/', groups=dict(authority=None, devname='', path='/'))
@valid(name='epics:/', groups=dict(authority=None, devname='', path='/'))
@valid(name='ca:///', groups=dict(authority='//', devname='', path='/'))
@invalid(name='ca:')  # device requires absolute non-empty path
@invalid(name='epics:')  # device requires absolute non-empty path
@invalid(name='ca://')  # this is an auth
@invalid(name='ca:foo')  #  device requires absolute path
@invalid(name='ca:/foo')  # devname must be empty (for now)
@invalid(name='ca:@foo')
@unittest.skipIf(('epics' in sys.modules) is False,
                 "epics module is not available")
class EpicsDevValidatorTestCase(AbstractNameValidatorTestCase,
                                unittest.TestCase):
    validator = EpicsDeviceNameValidator


# ==============================================================================
# Tests for Epics Attribute name validation
# ==============================================================================
@valid(name='epics:XXX:sum',
       groups={'scheme': 'epics',
               'authority': None,
               'attrname': 'XXX:sum',
               '__STRICT__': True,
               'fragment': None}
       )
@valid(name='ca:XXX:sum',
       groups={'scheme': 'ca',
               'authority': None,
               'attrname': 'XXX:sum',
               '_field': None,
               '__STRICT__': True,
               'fragment': None}
       )
@valid(name='ca:XXX:sum.RBV',
       groups={'scheme': 'ca',
               'authority': None,
               'attrname': 'XXX:sum.RBV',
               '_field': 'RBV',
               '__STRICT__': True,
               'fragment': None}
       )
@valid(name='ca:XXX:sum.rbv',
       groups={'scheme': 'ca',
               'authority': None,
               'attrname': 'XXX:sum.rbv',
               '_field': None,
               '__STRICT__': True,
               'fragment': None}
       )
@invalid(name='ca://XXX:sum')  # TODO: Maybe this should be valid?
@invalid(name='ca:///XXX:sum')  # TODO: Maybe this should be valid?
@valid(name='ca:a.B_c1;d:f-e[g]<h>#i',
       groups={'attrname': 'a.B_c1;d:f-e[g]<h>',
               '_field': None,
               '__STRICT__': True,
               'fragment': 'i'}
       )
@invalid(name='ca:a$b')
@invalid(name='ca:a/b')
@invalid(name=r'ca:a\b')
@invalid(name='ca:a%b')
@invalid(name='ca:a?b')
@invalid(name='ca://XXX:sum')
@invalid(name='ca://')
# ==============================================================================
# Tests for epics attribute  name validation (when passing fragment / cfgkey)
# ==============================================================================
@valid(name='ca:1#')
@valid(name='ca:1#units', groups={'fragment': 'units'})
@valid(name='ca:a')
@names(name='ca:XXX:sum', out=('ca:XXX:sum', 'XXX:sum', 'XXX:sum'))
@unittest.skipIf(('epics' in sys.modules) is False,
                 "epics module is not available")
class EpicsAttrValidatorTestCase(AbstractNameValidatorTestCase,
                                 unittest.TestCase):
    validator = EpicsAttributeNameValidator

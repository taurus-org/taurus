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

"""Test for taurus.core.epics.test.test_epicsvalidator..."""


__docformat__ = 'restructuredtext'

from taurus.external import unittest
from taurus.core.test import (valid, invalid, names,
                              AbstractNameValidatorTestCase)
from taurus.core.epics.epicsvalidator import (EpicsAuthorityNameValidator,
                                              EpicsDeviceNameValidator,
                                              EpicsAttributeNameValidator)


# ==============================================================================
# Tests for Epics Authority  name validation
# ==============================================================================
@valid(name='epics://', groups=dict(authority='//'))
@names(name='epics://', out=('epics://', '//', ''))
@invalid(name='epics:')
@invalid(name='epics:/')
@invalid(name='epics:///')
@invalid(name='epics://a')
class EpicsAuthValidatorTestCase(AbstractNameValidatorTestCase,
                                 unittest.TestCase):
    validator = EpicsAuthorityNameValidator


# ==============================================================================
# Tests for Epics Device name validation
# ==============================================================================
@valid(name='epics:', groups=dict(authority=None, devname=''))
@invalid(name='epics:/')
@invalid(name='epics://')  # this is an auth
@invalid(name='epics:///')
@invalid(name='epics:foo')
@invalid(name='epics:@foo')
class EpicsDevValidatorTestCase(AbstractNameValidatorTestCase,
                                unittest.TestCase):
    validator = EpicsDeviceNameValidator


# ==============================================================================
# Tests for Epics Attribute name validation
# ==============================================================================

@valid(name='epics:XXX:sum',
       groups={'authority': None,
               'devname': None,
               'attrname': 'XXX:sum',
               '__STRICT__': True,
               'fragment': None}
       )
@valid(name='epics:/XXX:sum',
       groups={'authority': None,
               'devname': '',
               'attrname': 'XXX:sum',
               '__STRICT__': True,
               'fragment': None}
       )
@invalid(name='epics://XXX:sum')
@valid(name='epics:///XXX:sum',
       groups={'authority': '//',
               'devname': '',
               'attrname': 'XXX:sum',
               '__STRICT__': True,
               'fragment': None}
       )
@valid(name='epics:a.b_c;d:f-e[g]<h>#i',
       groups={'attrname': 'a.b_c;d:f-e[g]<h>',
               '__STRICT__': True,
               'fragment': 'i'}
       )
@invalid(name='epics:a$b')
@invalid(name='epics:a/b')
@invalid(name=r'epics:a\b')
@invalid(name='epics:a%b')
@invalid(name='epics:a?b')
@invalid(name='epics://XXX:sum')
@invalid(name='epics://')
# ==============================================================================
# Tests for epics attribute  name validation (when passing fragment / cfgkey)
# ==============================================================================
@valid(name='epics:1#')
@valid(name='epics:1#units', groups={'fragment': 'units'})
@valid(name='epics:a')
class EpicsAttrValidatorTestCase(AbstractNameValidatorTestCase,
                                 unittest.TestCase):
    validator = EpicsAttributeNameValidator

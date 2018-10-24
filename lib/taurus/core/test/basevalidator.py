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

"""Test util module for creating test cases for name validators"""

#__all__ = []

from builtins import object
from functools import partial
from taurus.test import insertTest
from taurus.core.taurusvalidator import TaurusAttributeNameValidator

__docformat__ = 'restructuredtext'


valid = partial(insertTest, helper_name='isValid')
invalid = partial(insertTest, helper_name='isInvalid')
names = partial(insertTest, helper_name='getNames')


class AbstractNameValidatorTestCase(object):
    '''A util class to create test cases for name validators'''
    validator = None  # implement in derived classes

    def isValid(self, name=None, groups=None, strict=True):
        msg = '%s should be valid (with strict=%s)' % (name, strict)
        self.assertTrue(self.validator().isValid(name, strict=strict), msg)
        if groups is not None:
            returned = self.validator().getUriGroups(name, strict=strict)
            for k, v in groups.items():
                msg = ('"%s" not in %s.getUriGroups("%s"). Returned %s' %
                       (k, self.validator.__name__, name, returned))
                self.assertIn(k, returned, msg=msg)
                msg = ('%s.getUriGroups("%s")["%s"] should be "%s". ' +
                       'Returned "%s"\nGroups: %s') % (self.validator.__name__,
                                                       name, k, v, returned[k],
                                                       str(returned))
                self.assertEqual(v, returned[k], msg=msg)

    def isInvalid(self, name=None, groups=None, strict=True,
                  exceptionType=None):
        try:
            valid = self.validator().isValid(name, strict=strict)
            groups = self.validator().getUriGroups(name, strict=strict)
            msg = '%s should be invalid. Matched: %s' % (name, groups)
            self.assertFalse(valid, msg)
        except exceptionType:
            # do not fail if the exception is expected
            pass
        else:
            # there was no exception. Check if an exception was expected
            msg = '%s should raise %s' % (name, exceptionType)
            self.assertTrue(exceptionType is None, msg)

    def test_singleton(self):
        '''Check that the validator is a singleton'''
        self.assertIs(self.validator(), self.validator())

    def getNames(self, name=None, out=None):
        v = self.validator()
        if isinstance(v, TaurusAttributeNameValidator):
            fragment = len(out) > 3
            names = v.getNames(name, fragment=fragment)
        else:
            names = v.getNames(name)
        self.assertEqual(names, out)

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
import functools
from taurus import Device, Attribute  # , Authority
from taurus.test import insertTest


class TaurusModelEqualityTestCase(object):
    """Base class for taurus model equality testing."""

    def modelsEqual(self, models, class_, equal=True):
        """A helper method to create tests that checks equality (or inequality)
        of taurus objects e.g. TaurusAttribute.

        :param models: (seq<str>): a sequence of two taurus models
        :param class_: (function) model factory function
        :param equal: (bool) If True, check equality. Else check inequality
        """
        name1, name2 = models
        obj1 = class_(name1)
        obj2 = class_(name2)
        if equal:
            msg = 'models for %s and %s are not equal (they should)' % \
                  (name1, name2)
            self.assertIs(obj1, obj2, msg)
        else:
            msg = 'models for %s and %s are equal (they should not)' % \
                  (name1, name2)
            self.assertIsNot(obj1, obj2, msg)


testDeviceModelEquality = functools.partial(insertTest,
                                            helper_name='modelsEqual',
                                            class_=Device,
                                            test_method_name='testDeviceModelEquality')

testAttributeModelEquality = functools.partial(insertTest,
                                               helper_name='modelsEqual',
                                               class_=Attribute,
                                               test_method_name='testAttributeModelEquality')

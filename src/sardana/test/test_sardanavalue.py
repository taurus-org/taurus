#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
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

"""Unit tests for sardanavalue module"""

from taurus.external import unittest
from sardana.sardanavalue import SardanaValue


class SardanaValueTestCase(unittest.TestCase):

    """Instantiating in different ways a Sardana Value and perform some
       verifications.
    """

    def testInstanceCreation(self):
        """
        Instantiate in different ways a SardanaValue object.
            """
        sar_val = SardanaValue()
        self.assertIsInstance(sar_val, SardanaValue, 'Instantiation of an ' +
                              'object SardanaValue without arguments does not work')

        sar_val1 = SardanaValue(value=9)
        self.assertIsInstance(sar_val1, SardanaValue, 'Instantiation of an ' +
                              'object SardanaValue with the value argument does not work')

        sar_val2 = SardanaValue(value=8, exc_info=None,
                                timestamp='09:30', dtype='int', dformat='int')

        self.assertIsInstance(sar_val2, SardanaValue, 'Instantiation of an ' +
                              'object SardanaValue with arguments and exc_info equal None, ' +
                              'does not work.')

        sar_val3 = SardanaValue(value=7, exc_info='exception_info',
                                timestamp='09:30', dtype='int', dformat='int')

        self.assertIsInstance(sar_val3, SardanaValue, 'Instantiation of an ' +
                              'object SardanaValue with arguments and exc_info ' +
                              'different of None, does not work.')

    def testSardanaValueWithExceptionInfo(self):
        """Verify the creation of SardanaValue when exc_info != None.
            Verify that 'Error' is contained in the returned string.
        """
        val = 4
        sar_val = SardanaValue(value=val, exc_info='exception_info')
        representation = repr(sar_val)

        self.assertEqual(sar_val.error, True,
                         'The error attribute should be True.')

        self.assertRegexpMatches(representation, ".*<Error>.*",
                                 'The SardanaValue representation does not contain <Error>.')

    def testSardanaValueWithNoExceptionInfo(self):
        """Verify the creation of SardanaValue when exc_info is not specified
            and we give a value as argument of the SardanaValue constructor.
            SardanaValue representation shall contain its value.
            """
        value = 5
        sar_val = SardanaValue(value=value)
        returned_string = sar_val.__repr__()

        self.assertRegexpMatches(returned_string, repr(value),
                                 'The SardanaValue representation does not contain its value')

        self.assertEqual(sar_val.error, False,
                         'The error attribute should be False')

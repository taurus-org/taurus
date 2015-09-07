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

"""Unit tests for taurusbase"""


from taurus.external import unittest
from taurus.test import insertTest
from taurus.qt.qtgui.test import BaseWidgetTestCase
from taurus.qt.qtgui.container import TaurusWidget
from taurus.core.tango.starter import ProcessStarter
from taurus.test import insertTest, getResourcePath


DEV_NAME = 'TangoSchemeTest/unittest/temp-1'

@insertTest(helper_name='getDisplayValue',
            model= 'eval:1+2#label',
            expected='1+2')

@insertTest(helper_name='getDisplayValue',
            model= 'eval:1+2',
            expected='3')

@insertTest(helper_name='getDisplayValue',
            model= DEV_NAME + '/float_scalar?configuration=label',
            expected='float_scalar')

@insertTest(helper_name='getDisplayValue',
            model= DEV_NAME + '/float_scalar#label',
            expected='float_scalar')

@insertTest(helper_name='getDisplayValue',
            model= DEV_NAME + '/state',
            expected='ON')

# this fails due to encode/decode rounding errors for float<-->numpy.float32
@insertTest(helper_name='getDisplayValue',
            model= DEV_NAME + '/float_scalar',
            expected='1.23 mm')

@insertTest(helper_name='getDisplayValue',
            model= DEV_NAME + '/double_scalar',
            expected='1.23 mm')

@insertTest(helper_name='getDisplayValue',
            model= DEV_NAME + '/short_scalar',
            expected='123 mm')

@insertTest(helper_name='getDisplayValue',
            model= DEV_NAME + '/boolean_scalar',
            expected='True')

class GetDisplayValueTestCase(BaseWidgetTestCase, unittest.TestCase):
    """Check TaurusBaseComponent.getDisplayValue
    """
    _klass = TaurusWidget

    @classmethod
    def setUpClass(cls):
        """ Create and run a TangoSchemeTest device server
        """
        # get path to DS and executable
        device = getResourcePath('taurus.core.tango.test.res',
                                 'TangoSchemeTest')
        # create starter for the device server
        cls._starter = ProcessStarter(device, 'TangoSchemeTest/unittest')
        # register   #TODO: guarantee that devname is not in use
        cls._starter.addNewDevice(DEV_NAME, klass='TangoSchemeTest')
        # start device server
        cls._starter.startDs()

    @classmethod
    def tearDownClass(cls):
        """ Stop the device server and undo changes to the database
        """
        cls._starter.stopDs(hard_kill=True)
        # remove server
        cls._starter.cleanDb(force=True)

    def setUp(self):
        BaseWidgetTestCase.setUp(self)

    # def tearDown(self):
    #     BaseWidgetTestCase.tearDown(self)

    def getDisplayValue(self, model=None, expected=None):
        '''Check if setModel works when using parent model'''
        self._widget.setModel(model)
        got = self._widget.getDisplayValue()
        msg = ('getDisplayValue for "%s" should be %r (got %r)' %
               (model, expected, got))
        self.assertEqual(expected, got, msg)



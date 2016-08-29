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

"""Unit tests for taurusbase"""


from taurus.external import unittest
from taurus.test import insertTest
from taurus.qt.qtgui.test import BaseWidgetTestCase
from taurus.core.tango.test import TangoSchemeTestLauncher
from taurus.qt.qtgui.container import TaurusWidget

DEV_NAME = TangoSchemeTestLauncher.DEV_NAME


@insertTest(helper_name='getDisplayValue',
            model='eval:1+2#',
            expected='-----')
@insertTest(helper_name='getDisplayValue',
            model='eval:1+2#label',
            expected='1+2')
@insertTest(helper_name='getDisplayValue',
            model='eval:1+2',
            expected='3 ')  # @TODO: change to '3' if/when pint supports it
# This checks if the pre-tep3 behavior is kept (and it fails)
# ...but I think it should *not* be kept
@insertTest(helper_name='getDisplayValue',
            model='tango://' + DEV_NAME + '/double_scalar?configuration',
            expected='double_scalar?configuration',
            test_skip="old behaviour which we probably don't want")
@insertTest(helper_name='getDisplayValue',
            model='tango://' + DEV_NAME + '/float_scalar?configuration=label',
            expected='float_scalar')
@insertTest(helper_name='getDisplayValue',
            model='tango:' + DEV_NAME + '/double_scalar#rvalue.magnitude',
            expected='1.23')
@insertTest(helper_name='getDisplayValue',
            model='tango:' + DEV_NAME + '/float_scalar#label',
            expected='float_scalar')
@insertTest(helper_name='getDisplayValue',
            model='tango:' + DEV_NAME + '/float_scalar#',
            expected='-----')
@insertTest(helper_name='getDisplayValue',
            model='tango:' + DEV_NAME + '/state',
            expected='ON')
# This fails due to encode/decode rounding errors for float<-->numpy.float32
@insertTest(helper_name='getDisplayValue',
            model='tango:' + DEV_NAME + '/float_scalar',
            expected='1.23 mm',
            test_skip='enc/decode rounding errors for float<-->numpy.float32')
@insertTest(helper_name='getDisplayValue',
            model='tango:' + DEV_NAME + '/double_scalar',
            expected='1.23 mm')
@insertTest(helper_name='getDisplayValue',
            model='tango:' + DEV_NAME + '/short_scalar',
            expected='123 mm')
@insertTest(helper_name='getDisplayValue',
            model='tango:' + DEV_NAME + '/boolean_scalar',
            expected='True')
class GetDisplayValueTestCase(TangoSchemeTestLauncher, BaseWidgetTestCase,
                              unittest.TestCase):
    """Check TaurusBaseComponent.getDisplayValue
    """
    _klass = TaurusWidget

    def setUp(self):
        BaseWidgetTestCase.setUp(self)

    # def tearDown(self):
    #     BaseWidgetTestCase.tearDown(self)

    def getDisplayValue(self, model=None, expected=None):
        '''Check if setModel works when using parent model'''
        self._widget.setModel(model)
        # ----------------------------
        # workaround for https://sourceforge.net/p/tauruslib/tickets/334/
        import time
        time.sleep(BaseWidgetTestCase._BUG_334_WORKAROUND_TIME)
        # ----------------------------
        got = self._widget.getDisplayValue()
        msg = ('getDisplayValue for "%s" should be %r (got %r)' %
               (model, expected, got))
        self.assertEqual(expected, got, msg)
        self.assertMaxDeprecations(0)

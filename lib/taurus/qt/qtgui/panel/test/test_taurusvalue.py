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

"""Test for taurus.qt.qtgui.panel.taurusvalue"""

from taurus.external import unittest
from taurus.test import insertTest
from taurus.qt.qtgui.test import BaseWidgetTestCase
from taurus.qt.qtgui.panel import TaurusValue
from taurus.core.tango.test import TangoSchemeTestLauncher

DEV_NAME = TangoSchemeTestLauncher.DEV_NAME


@insertTest(helper_name='texts',
            model='tango:' + DEV_NAME + '/double_scalar',
            expected=('double_scalar', '1.23', '0.00 mm', 'mm'),
            # expected=('double_scalar', '1.23', '0.0', 'mm'),
            # TODO: change taurusvalue's line edit to hide units
            )
class TaurusValueTest(TangoSchemeTestLauncher, BaseWidgetTestCase,
                      unittest.TestCase):
    '''
    Specific tests for TaurusValue
    '''
    _klass = TaurusValue

    def test_bug126(self):
        '''Verify that case is not lost when customizing a label (bug#126)'''
        w = self._widget
        # self._widget.setModel('eval:1')
        self._widget.setModel('tango:' + DEV_NAME + '/double_scalar')
        label = 'MIXEDcase'
        w.setLabelConfig(label)
        self.processEvents(repetitions=10, sleep=.1)
        shownLabel = str(w.labelWidget().text())
        msg = 'Shown label ("%s") differs from set label ("%s")' % (shownLabel,
                                                                    label)
        self.assertEqual(label, shownLabel, msg)
        self.assertMaxDeprecations(0)

    def texts(self, model=None, expected=None, fgRole=None, maxdepr=0):
        '''Checks the texts for scalar attributes'''
        self._widget.setModel(model)
        if fgRole is not None:
            self._widget.setFgRole(fgRole)
        self.processEvents(repetitions=10, sleep=.1)
        got = (str(self._widget.labelWidget().text()),
               str(self._widget.readWidget().text()),
               str(self._widget.writeWidget().displayText()),
               str(self._widget.unitsWidget().text()),
               )
        msg = ('wrong text for "%s":\n expected: %s\n got: %s' %
               (model, expected, got))
        self.assertEqual(got, expected, msg)
        self.assertMaxDeprecations(maxdepr)

    def tearDown(self):
        '''Set Model to None'''
        self._widget.setModel(None)
        TangoSchemeTestLauncher.tearDown(self)
        unittest.TestCase.tearDown(self)

if __name__ == '__main__':
    pass

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


"""Unit tests for Taurus Label"""

from taurus.external import unittest
from taurus.test import insertTest
from taurus.qt.qtgui.test import GenericWidgetTestCase, BaseWidgetTestCase
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.container import TaurusWidget
from taurus.core.tango.test import TangoSchemeTestLauncher
import functools

DEV_NAME = TangoSchemeTestLauncher.DEV_NAME


class TaurusLabelTest(GenericWidgetTestCase, unittest.TestCase):

    '''
    Generic tests for TaurusLabel.

    .. seealso: :class:`taurus.qt.qtgui.test.base.GenericWidgetTestCase`
    '''
    _klass = TaurusLabel
    modelnames = ['sys/tg_test/1/wave', '', 'eval:1', None]
    
class Bug169_Test(BaseWidgetTestCase, unittest.TestCase):

    '''
    Test bug169: 
    
        AttributeError: type object 'TaurusConfigurationProxy' has no attribute
        'buildModelName'.
        
        See: http://sf.net/p/tauruslib/tickets/65/
    

    .. seealso: :class:`taurus.qt.qtgui.test.base.BaseWidgetTestCase`
    '''
    _klass = TaurusLabel
    
    def setUp(self):
        BaseWidgetTestCase.setUp(self)
        self._widget.setModel('sys/tg_test/1/double_scalar#label')
        self._expectedModelClass = self._widget.getModelClass()
        self._parent = TaurusWidget()
        self._parent.setModel('sys/tg_test/1')
        self._widget.setUseParentModel(True)
        self._widget.setParent(self._parent)
        
    def test_bug169(self):
        '''Check if setModel works when using parent model''' 
        self._widget.setModel('/double_scalar#label')
        self.assertMaxDeprecations(0)
        
    def test_relativemodelclass(self):
        '''Check consistency in modelClass when using parent model (re: bug169)
        ''' 
        try:
            self._widget.setModel('/double_scalar#label')
        finally:
            mc = self._widget.getModelClass()
            msg = ('getModelClass() inconsistency:\n expected: %s\n got: %s' % 
                   (self._expectedModelClass, mc))
            self.assertEqual(self._expectedModelClass, mc, msg)
        self.assertMaxDeprecations(0)



# ------------------------------------------------------------------------------
# Check bck-compat with pre-tep14  FgRoles: value, w_value, state, quality, none
testOldFgroles = functools.partial(insertTest, helper_name='text', maxdepr=1,
                                   model='tango:' + DEV_NAME + '/double_scalar')

@testOldFgroles(fgRole='value', expected='1.23 mm')
@testOldFgroles(fgRole='w_value', expected='0.0 mm')
@testOldFgroles(fgRole='state', expected='Ready')
@testOldFgroles(fgRole='quality', expected='ATTR_VALID')
@testOldFgroles(fgRole='none', expected='')
# ------------------------------------------------------------------------------

@insertTest(helper_name='text',
            model='tango:' + DEV_NAME + '/double_scalar#state',
            expected='Ready')

@insertTest(helper_name='text',
            model='tango:' + DEV_NAME + '/double_scalar#rvalue',
            fgRole='label',
            expected='double_scalar')
@insertTest(helper_name='text',
            model='tango:' + DEV_NAME + '/double_scalar',
            fgRole='label',
            expected='double_scalar')
@insertTest(helper_name='text',
            model='tango:' + DEV_NAME + '/double_scalar#label',
            expected='double_scalar')
class TaurusLabelTest2(TangoSchemeTestLauncher, BaseWidgetTestCase,
                       unittest.TestCase):
    '''
    Specific tests for TaurusLabel
    '''
    _klass = TaurusLabel

    def text(self, model=None, expected=None, fgRole=None, maxdepr=0):
        '''Check that the label text'''
        self._widget.setModel(model)
        if fgRole is not None:
            self._widget.setFgRole(fgRole)
        self._app.processEvents()
        got = str(self._widget.text())
        msg = ('wrong text for "%s":\n expected: %s\n got: %s' %
                   (model, expected, got))
        self.assertEqual(got, expected, msg)
        self.assertMaxDeprecations(maxdepr)



#
# if __name__ == "__main__":
#     unittest.main()

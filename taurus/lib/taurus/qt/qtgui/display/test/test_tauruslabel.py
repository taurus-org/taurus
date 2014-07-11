#!/usr/bin/env python
#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
##
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
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
from taurus.qt.qtgui.test import GenericWidgetTestCase, BaseWidgetTestCase
from taurus.qt.qtgui.display import TaurusLabel
from taurus.qt.qtgui.container import TaurusWidget


class TaurusLabelTest(GenericWidgetTestCase, unittest.TestCase):

    '''
    Generic tests for TaurusLabel.

    .. seealso: :class:`taurus.qt.qtgui.test.base.GenericWidgetTestCase`
    '''
    _klass = TaurusLabel
    modelnames = ['sys/tg_test/1/wave', '', 'eval://1', None]
    
class Bug169_Test(BaseWidgetTestCase, unittest.TestCase):

    '''
    Test bug169: 
    
        AttributeError: type object 'TaurusConfigurationProxy' has no attribute
        'buildModelName'.
        
        See: http://sf.net/p/sardana/tickets/169/
    

    .. seealso: :class:`taurus.qt.qtgui.test.base.BaseWidgetTestCase`
    '''
    _klass = TaurusLabel
    
    def setUp(self):
        BaseWidgetTestCase.setUp(self)
        self._widget.setModel('sys/tg_test/1/double_scalar?configuration=label')
        self._expectedModelClass = self._widget.getModelClass()
        self._parent = TaurusWidget()
        self._parent.setModel('sys/tg_test/1')
        self._widget.setUseParentModel(True)
        self._widget.setParent(self._parent)
        
    def test_bug169(self):
        '''Check if setModel works when using parent model''' 
        self._widget.setModel('/double_scalar?configuration=label')
        
    def test_relativemodelclass(self):
        '''Check consistency in modelClass when using parent model (re: bug169)
        ''' 
        try:
            self._widget.setModel('/double_scalar?configuration=label')
        finally:
            mc = self._widget.getModelClass()
            msg = ('getModelClass() inconsistency:\n expected: %s\n got: %s' % 
                   (self._expectedModelClass, mc))
            self.assertEqual(self._expectedModelClass, mc, msg)


#
# if __name__ == "__main__":
#     unittest.main()

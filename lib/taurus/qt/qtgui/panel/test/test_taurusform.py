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

"""Unit tests for Taurus Forms"""

from taurus.external import unittest
from taurus.qt.qtgui.test import GenericWidgetTestCase
from taurus.qt.qtgui.panel import TaurusForm, TaurusAttrForm


class TaurusFormTest(GenericWidgetTestCase, unittest.TestCase):

    '''
    Generic tests for TaurusForm widget.

    .. seealso: :class:`taurus.qt.qtgui.test.base.GenericWidgetTestCase`
    '''
    _klass = TaurusForm
    modelnames = [['sys/tg_test/1'],
                  ['sys/tg_test/1/wave'],
                  [],
                  '',
                  ['eval:1'],
                  None,
                  ['sys/tg_test/1/%s' % a for a in (
                   'short_scalar', 'double_array',
                   'uchar_image_ro', 'string_spectrum',
                   'no_value', 'throw_exception')],
                  [''],
                  'sys/tg_test/1,eval:1',
                  'sys/tg_test/1/short_image eval:rand(16)',
                  [None]
                  ]


class TaurusAttrFormTest(GenericWidgetTestCase, unittest.TestCase):

    '''
    Generic tests for TaurusAttrForm widget.

    .. seealso: :class:`taurus.qt.qtgui.test.base.GenericWidgetTestCase`
    '''
    _klass = TaurusAttrForm
    modelnames = ['sys/tg_test/1', None]


# if __name__ == "__main__":
#     unittest.main()
#    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TaurusFormTest)
#    unittest.TextTestRunner(verbosity=2).run(suite)

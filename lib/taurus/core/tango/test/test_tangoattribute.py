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

"""Test for taurus.core.tango.test.test_tangovalidator..."""

# __all__ = []

__docformat__ = 'restructuredtext'

import numpy
from taurus.external import unittest
from taurus.external.pint import Quantity
import taurus
from taurus.core import DataType
from taurus.core.tango.tangoattribute import TangoAttrValue
from taurus.core.tango.test import TangoSchemeTestLauncher
from taurus.test import insertTest

_INT_IMG = numpy.arange(2*3, dtype='int16').reshape((2,3))
_INT_SPE = _INT_IMG[1, :]
_FLOAT_IMG = _INT_IMG * .1
_FLOAT_SPE = _INT_SPE * .1
_BOOL_IMG = numpy.array([[True,False],[False,True]])
_BOOL_SPE = [True,False]
_STR = 'foo BAR |-+#@!?_[]{}'

# ==============================================================================
# Test encode-decode of empty arrays

@insertTest(helper_name='write_read_attr',
            attrname='short_spectrum',
            setvalue=Quantity(numpy.empty(0, dtype='int16')),
            expected=dict(rvalue=Quantity([], 'mm'),
                          type=DataType.Integer),
            expectedshape=(0,))

@insertTest(helper_name='write_read_attr',
            attrname='short_image',
            setvalue=Quantity(numpy.empty((0, 0), dtype='int16')),
            expected=dict(rvalue=Quantity([], 'mm'),
                          type=DataType.Integer),
            expectedshape=(0, 0))

@insertTest(helper_name='write_read_attr',
            attrname='boolean_spectrum',
            setvalue=numpy.empty(0, dtype='bool8'),
            expected=dict(type=DataType.Boolean),
            expectedshape=(0,))

@insertTest(helper_name='write_read_attr',
            attrname='boolean_image',
            setvalue=numpy.empty((0, 0), dtype='bool8'),
            expected=dict(type=DataType.Boolean),
            expectedshape=(0, 0))

# # Cannot test: Tango ignores writes of empty list for string attributes.
# @insertTest(helper_name='write_read_attr',
#             attrname='string_spectrum',
#             setvalue=[],
#             expected=dict(value=(), type=DataType.String,
#                           rvalue=(), wvalue=()))
#
# # Cannot test: Tango ignores writes of empty list for string attributes.
# @insertTest(helper_name='write_read_attr',
#             attrname='string_image',
#             setvalue=[[]],
#             expected=dict(value=[[]], type=DataType.String))

# ==============================================================================
# Test encode-decode of strings and booleans (no quantities)

@insertTest(helper_name='write_read_attr',
            attrname='string_image',
            setvalue=((_STR,)*3,)*2,
            expected=dict(rvalue=((_STR,)*3,)*2,
                          value=((_STR,)*3,)*2,
                          wvalue=((_STR,)*3,)*2,
                          w_value=((_STR,)*3,)*2,
                          type=DataType.String))

@insertTest(helper_name='write_read_attr',
            attrname='string_spectrum',
            setvalue=(_STR,)*3,
            expected=dict(rvalue=(_STR,)*3,
                          value=(_STR,)*3,
                          wvalue=(_STR,)*3,
                          w_value=(_STR,)*3,
                          type=DataType.String))

@insertTest(helper_name='write_read_attr',
            attrname='string_scalar',
            setvalue=_STR,
            expected=dict(rvalue=_STR,
                          value=_STR,
                          wvalue=_STR,
                          w_value=_STR,
                          type=DataType.String))

@insertTest(helper_name='write_read_attr',
            attrname='boolean_image',
            setvalue=_BOOL_IMG,
            expected=dict(rvalue=_BOOL_IMG,
                          value=_BOOL_IMG,
                          wvalue=_BOOL_IMG,
                          w_value=_BOOL_IMG,
                          type=DataType.Boolean))

@insertTest(helper_name='write_read_attr',
            attrname='boolean_spectrum',
            setvalue=_BOOL_SPE,
            expected=dict(rvalue=_BOOL_SPE,
                          value=_BOOL_SPE,
                          wvalue=_BOOL_SPE,
                          w_value=_BOOL_SPE,
                          type=DataType.Boolean))

@insertTest(helper_name='write_read_attr',
            attrname='boolean_scalar',
            setvalue=False,
            expected=dict(rvalue=False,
                          value=False,
                          wvalue=False,
                          w_value=False,
                          type=DataType.Boolean))

# ==============================================================================
# Test encode-decode with quantitiy conversions

@insertTest(helper_name='write_read_attr',
            attrname='float_image',
            setvalue=Quantity(_FLOAT_IMG, 'm'),
            expected=dict(rvalue=Quantity(_FLOAT_IMG, 'm'),
                          value=1000*_FLOAT_IMG,
                          wvalue=Quantity(_FLOAT_IMG, 'm'),
                          w_value=1000*_FLOAT_IMG,
                          type=DataType.Float),
            expectedshape=numpy.shape(_FLOAT_IMG))

@insertTest(helper_name='write_read_attr',
            attrname='float_spectrum',
            setvalue=Quantity(_FLOAT_SPE, 'm'),
            expected=dict(rvalue=Quantity(_FLOAT_SPE, 'm'),
                          value=1000*_FLOAT_SPE,
                          wvalue=Quantity(_FLOAT_SPE, 'm'),
                          w_value=1000*_FLOAT_SPE,
                          type=DataType.Float),
            expectedshape=numpy.shape(_FLOAT_SPE))

@insertTest(helper_name='write_read_attr',
            attrname='float_scalar',
            setvalue=Quantity(0.2, 'm'),
            expected=dict(value=200,
                          rvalue=Quantity(0.2, 'm'),
                          w_value=200,
                          wvalue=Quantity(200, 'mm'),
                          type=DataType.Float))

@insertTest(helper_name='write_read_attr',
            attrname='short_image',
            setvalue=Quantity(_INT_IMG, 'm'),
            expected=dict(rvalue=Quantity(_INT_IMG, 'm'),
                          value=1000*_INT_IMG,
                          wvalue=Quantity(_INT_IMG, 'm'),
                          w_value=1000*_INT_IMG,
                          type=DataType.Integer),
            expectedshape=numpy.shape(_INT_IMG))

@insertTest(helper_name='write_read_attr',
            attrname='short_spectrum',
            setvalue=Quantity(_INT_SPE, 'm'),
            expected=dict(rvalue=Quantity(_INT_SPE, 'm'),
                          value=1000*_INT_SPE,
                          wvalue=Quantity(_INT_SPE, 'm'),
                          w_value=1000*_INT_SPE,
                          type=DataType.Integer),
            expectedshape=numpy.shape(_INT_SPE))

@insertTest(helper_name='write_read_attr',
            attrname='short_scalar',
            setvalue=Quantity(2, 'm'),
            expected=dict(rvalue=Quantity(2000, 'mm'),
                          value=2000,
                          wvalue=Quantity(2000, 'mm'),
                          w_value=2000,
                          type=DataType.Integer))

# ==============================================================================
# Test read of tango attributes

@insertTest(helper_name='write_read_attr',
            attrname='string_image_ro',
            expected=dict(rvalue=(('hello world',)*3,)*3,
                          value=(('hello world',)*3,)*3,
                          wvalue=None, # TODO: we get () instead of None (check)
                          w_value=None,
                          type=DataType.String),
            expectedshape=(3,3))

@insertTest(helper_name='write_read_attr',
            attrname='string_spectrum_ro',
            expected=dict(rvalue=('hello world',)*3,
                          value=('hello world',)*3,
                          wvalue=None, # TODO: we get () instead of None (check)
                          w_value=None,
                          type=DataType.String),
            expectedshape=(3,))

@insertTest(helper_name='write_read_attr',
            attrname='string_scalar_ro',
            expected=dict(rvalue='hello world',
                          value='hello world',
                          wvalue=None,
                          w_value=None,
                          type=DataType.String))

@insertTest(helper_name='write_read_attr',
            attrname='boolean_image_ro',
            expected=dict(rvalue=numpy.ones((3,3), dtype='b'),
                          value= numpy.ones((3,3), dtype='b'),
                          wvalue=None,
                          w_value=None,
                          type=DataType.Boolean),
            expectedshape=(3,3))

@insertTest(helper_name='write_read_attr',
            attrname='boolean_spectrum_ro',
            expected=dict(rvalue=numpy.array([True]*3),
                          value=numpy.array([True]*3),
                          wvalue=None,
                          w_value=None,
                          type=DataType.Boolean),
            expectedshape=(3,))

@insertTest(helper_name='write_read_attr',
            attrname='boolean_scalar_ro',
            expected=dict(rvalue=True,
                          value=True,
                          wvalue=None,
                          w_value=None,
                          type=DataType.Boolean))

@insertTest(helper_name='write_read_attr',
            attrname='float_image_ro',
            expected=dict(rvalue=Quantity([[1.23]*3]*3, 'mm'),
                          value=[[1.23]*3]*3,
                          wvalue=None,
                          w_value=None,
                          type=DataType.Float),
            expectedshape=(3,3))

@insertTest(helper_name='write_read_attr',
            attrname='float_spectrum_ro',
            expected=dict(rvalue=Quantity([1.23]*3, 'mm'),
                          value=[1.23]*3,
                          wvalue=None,
                          w_value=None,
                          type=DataType.Float),
            expectedshape=(3,))

@insertTest(helper_name='write_read_attr',
            attrname='float_scalar_ro',
            expected=dict(value=1.23,
                          rvalue=Quantity(1.23, 'mm'),
                          wvalue=None,
                          w_value=None,
                          type=DataType.Float))

@insertTest(helper_name='write_read_attr',
            attrname='short_image_ro',
            expected=dict(rvalue=Quantity([[123]*3]*3, 'mm'),
                          value=[[123]*3]*3,
                          wvalue=None,
                          w_value=None,
                          type=DataType.Integer),
            expectedshape=(3,3))

@insertTest(helper_name='write_read_attr',
            attrname='short_spectrum_ro',
            expected=dict(rvalue=Quantity([123]*3, 'mm'),
                          value=[123]*3,
                          wvalue=None,
                          w_value=None,
                          type=DataType.Integer),
            expectedshape=(3,))

@insertTest(helper_name='write_read_attr',
            attrname='short_scalar_ro',
            expected=dict(rvalue=Quantity(123, 'mm'),
                          value=123,
                          wvalue=None,
                          w_value=None,
                          type=DataType.Integer))


class AttributeTestCase(TangoSchemeTestLauncher, unittest.TestCase):
    """TestCase for the taurus.Attribute helper"""

    def write_read_attr(self, attrname=None, setvalue=None, expected=None,
                        expectedshape=None):
        """check creation and correct write-and-read of an attribute"""

        name = '%s/%s' % (self.DEV_NAME, attrname)
        a = taurus.Attribute(name)

        if setvalue is None:
            read_value = a.read()
        else:
            old_value = a.read().value
            try:
                a.write(setvalue)
                read_value = a.read()
            finally:
                a.write(old_value)

        # print "!!!!", attrname, read_value
        msg = ('read() for "%s" did not return a TangoAttrValue (got a %s)' %
               (attrname, read_value.__class__.__name__))
        self.assertTrue(isinstance(read_value, TangoAttrValue), msg)
        for k, exp in expected.iteritems():
            try:
                got = getattr(read_value, k)
            except AttributeError:
                msg = ('The read value for "%s" does not provide info on %s' %
                       (attrname, k))
                self.fail(msg)

            msg = ('%s for "%s" should be %r (got %r)' %
                   (k, attrname, exp, got))

            # if we are dealing with quantities, use the magnitude for comparing
            if isinstance(got, Quantity):
                got = got.to(Quantity(exp).units).magnitude
            if isinstance(exp, Quantity):
                exp = exp.magnitude

            try:
                # for those values that can be handled by numpy.allclose()
                chk = numpy.allclose(got, exp)
            except TypeError:
                # for the rest
                chk = bool(got == exp)

            self.assertTrue(chk, msg)

        if expectedshape is not None:
            msg = ('rvalue.shape for %s should be %r (got %r)' %
                   (attrname, expectedshape, read_value.rvalue.shape))
            self.assertEqual(read_value.value.shape, expectedshape, msg)



if __name__ == '__main__':
    pass

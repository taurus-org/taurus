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

"""Test for taurus.core.tango.test.test_tangovalidator..."""

# __all__ = []

__docformat__ = 'restructuredtext'

import numpy
import PyTango
import unittest
from taurus.core.units import Quantity, UR
from pint import UndefinedUnitError

import taurus
from taurus.core import DataType, DataFormat
from taurus.core.tango.tangoattribute import TangoAttrValue
from taurus.core.tango.test import TangoSchemeTestLauncher
from taurus.test import insertTest
from taurus.core.taurusbasetypes import AttrQuality

_INT_IMG = numpy.arange(2 * 3, dtype='int16').reshape((2, 3))
_INT_SPE = _INT_IMG[1, :]
_FLOAT_IMG = _INT_IMG * .1
_FLOAT_SPE = _INT_SPE * .1
_BOOL_IMG = numpy.array([[True, False], [False, True]])
_BOOL_SPE = [True, False]
_STR = 'foo BAR |-+#@!?_[]{}'
_UINT8_IMG = numpy.array([[1, 2], [3, 4]], dtype='uint8')
_UINT8_SPE = _UINT8_IMG[1, :]

# ==============================================================================
# Test writing fragment values

@insertTest(helper_name='write_read_conf', attr_name='short_scalar_nu',
            cfg='range', value=[float('-inf'), float('inf')],
            expected=[Quantity(float('-inf')), Quantity(float('inf'))]
            )
@insertTest(helper_name='write_read_conf', attr_name='short_scalar_nu',
            cfg='range', value=[Quantity(float('-inf')),
                                Quantity(float('inf'))],
            expected=[Quantity(float('-inf')), Quantity(float('inf'))])
@insertTest(helper_name='write_read_conf', attr_name='short_scalar_nu',
            cfg='range', value=[100, 300],
            expected=[Quantity(100), Quantity(300)])
@insertTest(helper_name='write_read_conf', attr_name='short_scalar_nu',
            cfg='range', value=[Quantity(100), Quantity(300)],
            expected=[Quantity(100), Quantity(300)])
@insertTest(helper_name='write_read_conf', attr_name='float_scalar',
            cfg='range', value=[Quantity(-5, 'mm'), Quantity(5, 'mm')],
            expected=[Quantity(-0.005, 'm'), Quantity(5, 'mm')])
@insertTest(helper_name='write_read_conf', attr_name='short_spectrum',
            cfg='label', value='Just a Test',
            expected='Just a Test')
@insertTest(helper_name='write_read_conf', attr_name='boolean_spectrum',
            cfg='label', value='Just_a_Test',
            expected='Just_a_Test')
@insertTest(helper_name='write_read_conf', attr_name='short_scalar',
            cfg='warnings', value=[Quantity(-2, 'mm'), Quantity(2, 'mm')],
            expected=[Quantity(-2, 'mm'), Quantity(0.002, 'm')])
@insertTest(helper_name='write_read_conf', attr_name='short_image',
            cfg='warnings', value=[Quantity(-2, 'mm'), Quantity(2, 'mm')],
            expected=[Quantity(-0.002, 'm'), Quantity(2, 'mm')])
@insertTest(helper_name='write_read_conf', attr_name='float_image',
            cfg='warnings', value=[Quantity(-0.75, 'mm'),
                                        Quantity(0.75, 'mm')],
            expected=[Quantity(-0.00075, 'm'), Quantity(0.75, 'mm')])
@insertTest(helper_name='write_read_conf', attr_name='short_scalar_nu',
            cfg='warnings', value=[100, 300],
            expected=[Quantity(100), Quantity(300)])
@insertTest(helper_name='write_read_conf', attr_name='short_scalar',
            cfg='alarms', value=[Quantity(-50, 'mm'), Quantity(50, 'mm')],
            expected=[Quantity(-50, 'mm'), Quantity(50, 'mm')])
@insertTest(helper_name='write_read_conf', attr_name='short_image',
            cfg='alarms', value=[Quantity(-2, 'mm'), Quantity(2, 'mm')],
            expected=[Quantity(-0.002, 'm'), Quantity(2, 'mm')])
@insertTest(helper_name='write_read_conf', attr_name='float_image',
            cfg='alarms', value=[Quantity(-0.75, 'mm'), Quantity(0.75, 'mm')],
            expected=[Quantity(-0.00075, 'm'), Quantity(0.75, 'mm')])
@insertTest(helper_name='write_read_conf', attr_name='short_scalar_nu',
            cfg='alarms', value=[100, 300],
            expected=[Quantity(100), Quantity(300)])

# ==============================================================================
# Test encode-decode of empty arrays


@insertTest(helper_name='write_read_attr',
            attrname='short_spectrum',
            setvalue=Quantity(numpy.empty(0, dtype='int16'), 'km'),
            expected=dict(rvalue=Quantity([], 'mm'),
                          type=DataType.Integer,
                          unit="mm"
                          ),
            expected_attrv=dict(rvalue=Quantity([], 'mm'),
                                type=DataType.Integer,
                                unit="mm"
                                ),
            expectedshape=(0,)
            )
@insertTest(helper_name='write_read_attr',
            attrname='short_image',
            setvalue=Quantity(numpy.empty((0, 0), dtype='int16'), 'mm'),
            expected=dict(rvalue=Quantity([], 'mm'),
                          type=DataType.Integer
                          ),
            expectedshape=(0, 0)
            )
@insertTest(helper_name='write_read_attr',
            attrname='boolean_spectrum',
            setvalue=numpy.empty(0, dtype='bool8'),
            expected=dict(type=DataType.Boolean),
            expectedshape=(0,)
            )
@insertTest(helper_name='write_read_attr',
            attrname='boolean_image',
            setvalue=numpy.empty((0, 0), dtype='bool8'),
            expected=dict(type=DataType.Boolean),
            expectedshape=(0, 0)
            )
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
# Test encode-decode of strings, booleans and uchars
@insertTest(helper_name='write_read_attr',
            attrname='uchar_image',
            setvalue=_UINT8_IMG,
            expected=dict(rvalue=_UINT8_IMG,
                          wvalue=_UINT8_IMG,
                          type=DataType.Bytes,
                          label='uchar_image',
                          writable=True,
                          ),
            expected_attrv=dict(rvalue=_UINT8_IMG,
                                value=_UINT8_IMG,
                                wvalue=_UINT8_IMG,
                                w_value=_UINT8_IMG,
                                quality=AttrQuality.ATTR_VALID
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='uchar_spectrum',
            setvalue=_UINT8_SPE,
            expected=dict(rvalue=_UINT8_SPE,
                          wvalue=_UINT8_SPE,
                          type=DataType.Bytes,
                          writable=True,
                          ),
            expected_attrv=dict(rvalue=_UINT8_SPE,
                                value=_UINT8_SPE,
                                wvalue=_UINT8_SPE,
                                w_value=_UINT8_SPE,
                                quality=AttrQuality.ATTR_VALID
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='uchar_scalar',
            setvalue=12,
            expected=dict(rvalue=12,
                          wvalue=12,
                          type=DataType.Bytes,
                          writable=True,
                          range=[None, None],
                          alarms=[None, None],
                          warnings=[None, None]
                          ),
            expected_attrv=dict(rvalue=12,
                                value=12,
                                wvalue=12,
                                w_value=12,
                                quality=AttrQuality.ATTR_VALID
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='uchar_image',
            setvalue=_UINT8_IMG,
            expected=dict(rvalue=_UINT8_IMG,
                          wvalue=_UINT8_IMG,
                          type=DataType.Bytes,
                          label='uchar_image',
                          writable=True,
                          ),
            expected_attrv=dict(rvalue=_UINT8_IMG,
                                value=_UINT8_IMG,
                                wvalue=_UINT8_IMG,
                                w_value=_UINT8_IMG,
                                quality=AttrQuality.ATTR_VALID
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='uchar_spectrum',
            setvalue=_UINT8_SPE,
            expected=dict(rvalue=_UINT8_SPE,
                          wvalue=_UINT8_SPE,
                          type=DataType.Bytes,
                          writable=True,
                          ),
            expected_attrv=dict(rvalue=_UINT8_SPE,
                                value=_UINT8_SPE,
                                wvalue=_UINT8_SPE,
                                w_value=_UINT8_SPE,
                                quality=AttrQuality.ATTR_VALID
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='uchar_scalar',
            setvalue=12,
            expected=dict(rvalue=12,
                          wvalue=12,
                          type=DataType.Bytes,
                          writable=True,
                          range=[None, None],
                          alarms=[None, None],
                          warnings=[None, None]
                          ),
            expected_attrv=dict(rvalue=Quantity(12, 'mm'),
                                value=12,
                                wvalue=Quantity(12, 'mm'),
                                w_value=12,
                                quality=AttrQuality.ATTR_VALID
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='string_image',
            setvalue=((_STR,) * 3,) * 2,
            expected=dict(rvalue=((_STR,) * 3,) * 2,
                          wvalue=((_STR,) * 3,) * 2,
                          type=DataType.String,
                          label='string_image',
                          writable=True,
                          ),
            expected_attrv=dict(value=((_STR,) * 3,) * 2,
                                w_value=((_STR,) * 3,) * 2,
                                rvalue=((_STR,) * 3,) * 2,
                                wvalue=((_STR,) * 3,) * 2,
                                quality=AttrQuality.ATTR_VALID
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='string_spectrum',
            setvalue=(_STR,) * 3,
            expected=dict(rvalue=(_STR,) * 3,
                          wvalue=(_STR,) * 3,
                          type=DataType.String,
                          label='string_spectrum',
                          writable=True,
                          ),
            expected_attrv=dict(value=(_STR,) * 3,
                                w_value=(_STR,) * 3,
                                rvalue=(_STR,) * 3,
                                wvalue=(_STR,) * 3,
                                quality=AttrQuality.ATTR_VALID
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='string_scalar',
            setvalue=_STR,
            expected=dict(rvalue=_STR,
                          wvalue=_STR,
                          type=DataType.String,
                          label='string_scalar',
                          writable=True,
                          ),
            expected_attrv=dict(value=_STR,
                                w_value=_STR,
                                rvalue=_STR,
                                wvalue=_STR,
                                quality=AttrQuality.ATTR_VALID
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='boolean_image',
            setvalue=_BOOL_IMG,
            expected=dict(rvalue=_BOOL_IMG,
                          wvalue=_BOOL_IMG,
                          type=DataType.Boolean,
                          label='boolean_image',
                          writable=True,
                          ),
            expected_attrv=dict(rvalue=_BOOL_IMG,
                                value=_BOOL_IMG,
                                wvalue=_BOOL_IMG,
                                w_value=_BOOL_IMG,
                                quality=AttrQuality.ATTR_VALID
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='boolean_spectrum',
            setvalue=_BOOL_SPE,
            expected=dict(rvalue=_BOOL_SPE,
                          wvalue=_BOOL_SPE,
                          type=DataType.Boolean,
                          writable=True,
                          ),
            expected_attrv=dict(rvalue=_BOOL_SPE,
                                value=_BOOL_SPE,
                                wvalue=_BOOL_SPE,
                                w_value=_BOOL_SPE,
                                quality=AttrQuality.ATTR_VALID
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='boolean_scalar',
            setvalue=False,
            expected=dict(rvalue=False,
                          wvalue=False,
                          type=DataType.Boolean,
                          writable=True,
                          range=[None, None],
                          alarms=[None, None],
                          warnings=[None, None]
                          ),
            expected_attrv=dict(rvalue=False,
                                value=False,
                                wvalue=False,
                                w_value=False,
                                quality=AttrQuality.ATTR_VALID
                                )
            )
# ==============================================================================
# Test encode-decode with quantitiy conversions
@insertTest(helper_name='write_read_attr',
            attrname='float_image',
            setvalue=Quantity(_FLOAT_IMG, 'm'),
            expected=dict(rvalue=Quantity(_FLOAT_IMG, 'm'),
                          wvalue=Quantity(_FLOAT_IMG, 'm'),
                          type=DataType.Float,
                          writable=True,
                          quality=AttrQuality.ATTR_VALID,
                          label='float_image',
                          range=[Quantity(float('-inf'), 'mm'),
                                 Quantity(float('inf'), 'mm')],
                          alarms=[Quantity(float('-inf'), 'mm'),
                                  Quantity(float('inf'), 'mm')],
                          warnings=[Quantity(float('-inf'), 'mm'),
                                    Quantity(float('inf'), 'mm')]
                          ),
            expected_attrv=dict(rvalue=Quantity(_FLOAT_IMG, 'm'),
                                value=1000 * _FLOAT_IMG,
                                wvalue=Quantity(_FLOAT_IMG, 'm'),
                                w_value=1000 * _FLOAT_IMG,
                                quality=AttrQuality.ATTR_VALID
                                ),
            expectedshape=numpy.shape(_FLOAT_IMG)
            )
@insertTest(helper_name='write_read_attr',
            attrname='float_spectrum',
            setvalue=Quantity(_FLOAT_SPE, 'm'),
            expected=dict(rvalue=Quantity(_FLOAT_SPE, 'm'),
                          wvalue=Quantity(_FLOAT_SPE, 'm'),
                          type=DataType.Float,
                          quality=AttrQuality.ATTR_VALID
                          ),
            expected_attrv=dict(rvalue=Quantity(_FLOAT_SPE, 'm'),
                                value=1000 * _FLOAT_SPE,
                                wvalue=Quantity(_FLOAT_SPE, 'm'),
                                w_value=1000 * _FLOAT_SPE,
                                quality=AttrQuality.ATTR_VALID
                                ),
            expectedshape=numpy.shape(_FLOAT_SPE)
            )
@insertTest(helper_name='write_read_attr',
            attrname='float_scalar',
            setvalue=Quantity(0.01, 'm'),
            expected=dict(rvalue=Quantity(0.01, 'm'),
                          wvalue=Quantity(10, 'mm'),
                          type=DataType.Float,
                          name='float_scalar',
                          range=[Quantity(-12.30, 'mm'),
                                 Quantity(12.30, 'mm')],
                          alarms=[Quantity(-6.15, 'mm'),
                                  Quantity(6.15, 'mm')],
                          warnings=[Quantity(-3.69, 'mm'),
                                    Quantity(3.69, 'mm')]
                          ),
            expected_attrv=dict(value=10,
                                rvalue=Quantity(0.01, 'm'),
                                w_value=10,
                                wvalue=Quantity(10, 'mm'),
                                quality=AttrQuality.ATTR_ALARM
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='float_scalar',
            setvalue=Quantity(0.004, 'm'),
            expected=dict(rvalue=Quantity(4, 'mm'),
                          wvalue=Quantity(4, 'mm')
                          ),
            expected_attrv=dict(rvalue=Quantity(4, 'mm'),
                                wvalue=Quantity(0.004, 'm'),
                                quality=AttrQuality.ATTR_WARNING
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='float_scalar',
            setvalue=Quantity(3, 'mm'),
            expected=dict(rvalue=Quantity(3, 'mm'),
                          wvalue=Quantity(3, 'mm'),
                          type=DataType.Float,
                          ),
            expected_attrv=dict(value=3,
                                w_value=3,
                                quality=AttrQuality.ATTR_VALID
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='double_scalar',
            setvalue=Quantity(0.01, 'm'),
            expected=dict(rvalue=Quantity(0.01, 'm'),
                          wvalue=Quantity(10, 'mm'),
                          type=DataType.Float,
                          name="double_scalar",
                          range=[Quantity(-12.30, 'mm'),
                                 Quantity(12.30, 'mm')],
                          alarms=[Quantity(-6.15, 'mm'),
                                  Quantity(6.15, 'mm')],
                          warnings=[Quantity(-3.69, 'mm'),
                                    Quantity(3.69, 'mm')]
                          ),
            expected_attrv=dict(value=10,
                                rvalue=Quantity(0.01, 'm'),
                                w_value=10,
                                wvalue=Quantity(10, 'mm'),
                                quality=AttrQuality.ATTR_ALARM
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='double_scalar',
            setvalue=Quantity(0.004, 'm'),
            expected=dict(rvalue=Quantity(4, 'mm'),
                          wvalue=Quantity(4, 'mm')
                          ),
            expected_attrv=dict(rvalue=Quantity(4, 'mm'),
                                wvalue=Quantity(0.004, 'm'),
                                quality=AttrQuality.ATTR_WARNING
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='double_scalar',
            setvalue=Quantity(3, 'mm'),
            expected=dict(rvalue=Quantity(3, 'mm'),
                          wvalue=Quantity(3, 'mm'),
                          type=DataType.Float,
                          ),
            expected_attrv=dict(value=3,
                                w_value=3,
                                quality=AttrQuality.ATTR_VALID
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='short_image',
            setvalue=Quantity(_INT_IMG, 'm'),
            expected=dict(rvalue=Quantity(_INT_IMG, 'm'),
                          wvalue=Quantity(_INT_IMG, 'm'),
                          type=DataType.Integer
                          ),
            expected_attrv=dict(value=1000 * _INT_IMG,
                                rvalue=Quantity(_INT_IMG, 'm'),
                                wvalue=Quantity(_INT_IMG, 'm'),
                                w_value=1000 * _INT_IMG,
                                quality=AttrQuality.ATTR_VALID
                                ),
            expectedshape=numpy.shape(_INT_IMG)
            )
@insertTest(helper_name='write_read_attr',
            attrname='short_spectrum',
            setvalue=Quantity(_INT_SPE, 'm'),
            expected=dict(rvalue=Quantity(_INT_SPE, 'm'),
                          wvalue=Quantity(_INT_SPE, 'm'),
                          type=DataType.Integer),
            expectedshape=numpy.shape(_INT_SPE),
            expected_attrv=dict(value=1000 * _INT_SPE,
                                w_value=1000 * _INT_SPE
                                )
            )
@insertTest(helper_name='write_read_attr',
            attrname='short_scalar',
            setvalue=Quantity(1, 'm'),
            expected=dict(rvalue=Quantity(1000, 'mm'),
                          wvalue=Quantity(1000, 'mm'),
                          type=DataType.Integer,
                          label='short_scalar',
                          data_format=DataFormat._0D,
                          writable=True,
                          range=[Quantity(-1230, 'mm'),
                                 Quantity(1230, 'mm')],
                          alarms=[Quantity(-615, 'mm'),
                                  Quantity(615, 'mm')],
                          warnings=[Quantity(-369, 'mm'),
                                    Quantity(369, 'mm')]
                          ),
            expected_attrv=dict(value=1000,
                                w_value=1000,
                                quality=AttrQuality.ATTR_ALARM
                                )
            )
# ==============================================================================
# Test read of tango attributes
@insertTest(helper_name='write_read_attr',
            attrname='uchar_image_ro',
            expected=dict(rvalue=Quantity([[1] * 3] * 3, 'mm'),
                          wvalue=None,
                          type=DataType.Bytes
                          ),
            expected_attrv=dict(value=[[1] * 3] * 3,
                                w_value=None,
                                quality=AttrQuality.ATTR_VALID
                                ),
            expectedshape=(3, 3),
            )

@insertTest(helper_name='write_read_attr',
            attrname='uchar_scalar_ro',
            expected=dict(rvalue=1,
                          wvalue=None,
                          type=DataType.Bytes,
                          data_format=DataFormat._0D,
                          writable=False,
                          range=[None, None],
                          alarms=[None, None],
                          warnings=[None, None]
                          ),
            expected_attrv=dict(rvalue=Quantity(1, 'mm'),
                                value=1,
                                quality=AttrQuality.ATTR_VALID,
                                wvalue=None,
                                w_value=None)
            )
@insertTest(helper_name='write_read_attr',
            attrname='string_image_ro',
            expected=dict(rvalue=(('hello world',) * 3,) * 3,
                          wvalue=None,
                          type=DataType.String
                          ),
            expected_attrv=dict(value=(('hello world',) * 3,) * 3,
                                w_value=None,
                                quality=AttrQuality.ATTR_VALID
                                ),
            expectedshape=(3, 3),
            test_skip='Known (Py)Tango bug for empty string arrays',
            )
@insertTest(helper_name='write_read_attr',
            attrname='string_spectrum_ro',
            expected=dict(rvalue=('hello world',) * 3,
                          wvalue=None,
                          type=DataType.String),
            expected_attrv=dict(value=('hello world',) * 3,
                                w_value=None,
                                quality=AttrQuality.ATTR_VALID
                                ),
            expectedshape=(3,),
            test_skip='Known (Py)Tango bug for empty string arrays',
            )
@insertTest(helper_name='write_read_attr',
            attrname='string_scalar_ro',
            expected=dict(rvalue='hello world',
                          wvalue=None,
                          type=DataType.String
                          ),
            expected_attrv=dict(value='hello world',
                                w_value=None,
                                quality=AttrQuality.ATTR_VALID
                                ),
            )
@insertTest(helper_name='write_read_attr',
            attrname='boolean_image_ro',
            expected=dict(rvalue=numpy.ones((3, 3), dtype='b'),
                          wvalue=None,
                          type=DataType.Boolean
                          ),
            expected_attrv=dict(value=numpy.ones((3, 3), dtype='b'),
                                w_value=None,
                                quality=AttrQuality.ATTR_VALID
                                ),
            expectedshape=(3, 3))
@insertTest(helper_name='write_read_attr',
            attrname='boolean_spectrum_ro',
            expected=dict(rvalue=numpy.array([True] * 3),
                          wvalue=None,
                          type=DataType.Boolean,
                          label='boolean_spectrum_ro'
                          ),
            expected_attrv=dict(value=numpy.array([True] * 3),
                                w_value=None,
                                quality=AttrQuality.ATTR_VALID
                                ),
            expectedshape=(3,))
@insertTest(helper_name='write_read_attr',
            attrname='boolean_scalar_ro',
            expected=dict(rvalue=True,
                          wvalue=None,
                          type=DataType.Boolean,
                          range=[None, None],
                          alarms=[None, None],
                          warnings=[None, None],
                          data_format=DataFormat._0D,
                          writable=False
                          ),
            expected_attrv=dict(value=True,
                                w_value=None,
                                quality=AttrQuality.ATTR_VALID
                                ),
            )
@insertTest(helper_name='write_read_attr',
            attrname='float_image_ro',
            expected=dict(rvalue=Quantity([[1.23] * 3] * 3, 'mm'),
                          wvalue=None,
                          type=DataType.Float
                          ),
            expected_attrv=dict(value=[[1.23] * 3] * 3,
                                w_value=None,
                                quality=AttrQuality.ATTR_VALID,
                                wvalue=None),
            expectedshape=(3, 3))
@insertTest(helper_name='write_read_attr',
            attrname='float_spectrum_ro',
            expected=dict(rvalue=Quantity([1.23] * 3, 'mm'),
                          wvalue=None,
                          type=DataType.Float
                          ),
            expected_attrv=dict(value=[1.23] * 3,
                                w_value=None,
                                quality=AttrQuality.ATTR_VALID
                                ),
            expectedshape=(3,)
            )
@insertTest(helper_name='write_read_attr',
            attrname='float_scalar_ro',
            expected=dict(rvalue=Quantity(1.23, 'mm'),
                          wvalue=None,
                          type=DataType.Float,
                          writable=False,
                          range=[Quantity(float('-inf'), 'mm'),
                                 Quantity(float('inf'), 'mm')],
                          alarms=[Quantity(float('-inf'), 'mm'),
                                  Quantity(float('inf'), 'mm')],
                          warnings=[Quantity(float('-inf'), 'mm'),
                                    Quantity(float('inf'), 'mm')]
                          ),
            expected_attrv=dict(value=1.23,
                                w_value=None,
                                quality=AttrQuality.ATTR_VALID
                                ),
            )
@insertTest(helper_name='write_read_attr',
            attrname='short_image_ro',
            expected=dict(rvalue=Quantity([[123] * 3] * 3, 'mm'),
                          wvalue=None,
                          type=DataType.Integer
                          ),
            expected_attrv=dict(rvalue=Quantity([[123] * 3] * 3, 'mm'),
                                value=[[123] * 3] * 3,
                                quality=AttrQuality.ATTR_VALID,
                                wvalue=None,
                                w_value=None),
            expectedshape=(3, 3)
            )
@insertTest(helper_name='write_read_attr',
            attrname='short_spectrum_ro',
            expected=dict(rvalue=Quantity([123] * 3, 'mm'),
                          wvalue=None,
                          type=DataType.Integer,
                          data_format=DataFormat._1D,
                          writable=False
                          ),
            expected_attrv=dict(rvalue=Quantity([123] * 3, 'mm'),
                                value=[123] * 3,
                                quality=AttrQuality.ATTR_VALID,
                                wvalue=None,
                                w_value=None),
            expectedshape=(3,)
            )
@insertTest(helper_name='write_read_attr',
            attrname='short_scalar_ro',
            expected=dict(rvalue=Quantity(123, 'mm'),
                          wvalue=None,
                          type=DataType.Integer,
                          data_format=DataFormat._0D,
                          writable=False,
                          range=[Quantity(float('-inf'), 'mm'),
                                 Quantity(float('inf'), 'mm')],
                          alarms=[Quantity(float('-inf'), 'mm'),
                                  Quantity(float('inf'), 'mm')],
                          warnings=[Quantity(float('-inf'), 'mm'),
                                    Quantity(float('inf'), 'mm')]
                          ),
            expected_attrv=dict(rvalue=Quantity(123, 'mm'),
                                value=123,
                                quality=AttrQuality.ATTR_VALID,
                                wvalue=None,
                                w_value=None)
            )
class AttributeTestCase(TangoSchemeTestLauncher, unittest.TestCase):
    """TestCase for the taurus.Attribute helper"""

    def tearDown(self):
        TangoSchemeTestLauncher.tearDown(self)

    def _getDecodePyTangoAttr(self, attr_name, cfg):
        """Helper for decode the PyTango attribute infoex
        """
        dev = PyTango.DeviceProxy(self.DEV_NAME)
        infoex = dev.get_attribute_config_ex(attr_name)[0]
        try:
            unit = UR.parse_units(infoex.unit)
        except (UndefinedUnitError, UnicodeDecodeError):
            unit = UR.parse_units(None)
        if cfg in ['range', 'alarms', 'warnings']:
            if cfg == 'range':
                low = infoex.min_value
                high = infoex.max_value
            elif cfg == 'alarms':
                low = infoex.alarms.min_alarm
                high = infoex.alarms.max_alarm
            elif cfg == 'warnings':
                low = infoex.alarms.min_warning
                high = infoex.alarms.max_warning
            if low == 'Not specified':
                low = '-inf'
            if high == 'Not specified':
                high = 'inf'
            return [Quantity(float(low), unit),
                    Quantity(float(high), unit)]
        elif cfg == 'label':
            return infoex.label
        else:
            return None

    def write_read_conf(self, attr_name, cfg, value, expected):
        """ Helper for checking the write-and-read of the Tango
        attribute configuration (existing in Taurus).
        """
        attr_fullname = '%s/%s' % (self.DEV_NAME, attr_name)
        attr = taurus.Attribute(attr_fullname)
        # write the property
        setattr(attr, cfg, value)
        # read the property
        got = getattr(attr, cfg)
        msg = '%s.%s from Taurus do not mach, expected %s read %s' %\
              (attr_name, cfg, expected, got)
        map(self.__assertValidValue, got, expected, msg)

        msg = '%s.%s from Tango do not mach, expected %s read %s' %\
              (attr_name, cfg, expected, got)
        tangovalue = self._getDecodePyTangoAttr(attr_name, cfg)
        map(self.__assertValidValue, got, tangovalue, msg)

    def write_read_attr(self, attrname=None, setvalue=None, expected=None,
                        expected_attrv=None, expectedshape=None):
        """check creation and correct write-and-read of an attribute"""

        if expected is None:
            expected = {}
        if expected_attrv is None:
            expected_attrv = {}

        name = '%s/%s' % (self.DEV_NAME, attrname)
        a = taurus.Attribute(name)

        if setvalue is None:
            read_value = a.read()
        else:
            a.write(setvalue)
            read_value = a.read(cache=False)

        msg = ('read() for "%s" did not return a TangoAttrValue (got a %s)' %
               (attrname, read_value.__class__.__name__))
        self.assertTrue(isinstance(read_value, TangoAttrValue), msg)

        # Test attribute
        for k, exp in expected.items():
            try:
                got = getattr(a, k)
            except AttributeError:
                msg = ('The attribute, "%s" does not provide info on %s' %
                       (attrname, k))
                self.fail(msg)
            msg = ('%s for "%s" should be %r (got %r)' %
                   (k, attrname, exp, got))
            self.__assertValidValue(exp, got, msg)

        # Test attribute value
        for k, exp in expected_attrv.items():
            try:
                got = getattr(read_value, k)
            except AttributeError:
                msg = ('The read value for "%s" does not provide info on %s' %
                       (attrname, k))
                self.fail(msg)
            msg = ('%s for the value of %s should be %r (got %r)' %
                   (k, attrname,  exp, got))
            self.__assertValidValue(exp, got, msg)

        if expectedshape is not None:
            msg = ('rvalue.shape for %s should be %r (got %r)' %
                   (attrname, expectedshape, read_value.rvalue.shape))
            self.assertEqual(read_value.rvalue.shape, expectedshape, msg)

    def __assertValidValue(self, exp, got, msg):
        # if we are dealing with quantities, use the magnitude for comparing
        if isinstance(got, Quantity):
            got = got.to(Quantity(exp).units).magnitude
        if isinstance(exp, Quantity):
            exp = exp.magnitude
        try:
            # first try the most generic equality
            chk = bool(got == exp)
        except:
            chk = False
        if not chk:
            # some cases may fail the simple equality but still be True
            try:
                # for those values that can be handled by numpy.allclose()
                chk = numpy.allclose(got, exp)
            except:
                if isinstance(got, numpy.ndarray):
                    # uchars were not handled with allclose
                    # UGLY!! but numpy.all does not work
                    chk = got.tolist() == exp.tolist()
        self.assertTrue(chk, msg)


if __name__ == '__main__':
    pass

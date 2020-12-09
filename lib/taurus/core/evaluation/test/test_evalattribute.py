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

import numpy
import unittest
from taurus.core.units import Quantity
import taurus
from taurus.test import insertTest
from taurus.core.taurusbasetypes import DataType, DataFormat, AttrQuality
from taurus.core.evaluation.evalattribute import EvaluationAttrValue


@insertTest(helper_name='read_attr',
            attr_fullname='eval:1',
            expected=dict(rvalue=Quantity(1, 'dimensionless'),
                          type=DataType.Integer,
                          label='1',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue=Quantity([], 'dimensionless'),
                                wvalue=None
                                ),
            expectedshape=None
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:Quantity("1m")+Quantity("2m")',
            expected=dict(rvalue=Quantity(3, 'm'),
                          type=DataType.Integer,
                          label='Quantity("1m")+Quantity("2m")',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue=Quantity(3, 'm'),
                                wvalue=None
                                ),
            expectedshape=None
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:foo=Quantity("1m");bar=Quantity("2m");foo+bar',
            expected=dict(rvalue=Quantity(3, 'm'),
                          type=DataType.Integer,
                          label='foo+bar',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue=Quantity(3, 'm'),
                                wvalue=None
                                ),
            expectedshape=None
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:foo=Q("1m");foo-Q("2m")',
            expected=dict(rvalue=Quantity(-1, 'm'),
                          type=DataType.Integer,
                          label='foo-Q("2m")',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue=Quantity(-1, 'm'),
                                wvalue=None
                                ),
            expectedshape=None
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:[123, 123, 123]',
            expected=dict(rvalue=Quantity([123, 123, 123], 'dimensionless'),
                          type=DataType.Integer,
                          label='[123, 123, 123]',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue=Quantity([123, 123, 123],
                                                'dimensionless'),
                                wvalue=None
                                ),
            expectedshape=(3, )
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:Quantity([1.23, 1.23, 1.23], "m")',
            expected=dict(rvalue=Quantity([1.23, 1.23, 1.23], 'm'),
                          type=DataType.Float,
                          label='Quantity([1.23, 1.23, 1.23], "m")',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue=Quantity([1.23, 1.23, 1.23], 'm'),
                                wvalue=None
                                ),
            expectedshape=(3, )
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:foo=Quantity([1.23, 1.23, 1.23], "m");foo*10',
            expected=dict(rvalue=Quantity([12.3, 12.3, 12.3], 'm'),
                          type=DataType.Float,
                          label='foo*10',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue=Quantity([12.3, 12.3, 12.3],
                                                'm'),
                                wvalue=None
                                ),
            expectedshape=(3, )
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:[[1,2,3]]*3',
            expected=dict(rvalue=Quantity([[1, 2, 3]] * 3, 'dimensionless'),
                          type=DataType.Integer,
                          label='[[1,2,3]]*3',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue=Quantity([[1, 2, 3]] * 3,
                                                'dimensionless'),
                                wvalue=None
                                ),
            expectedshape=(3, 3)
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:foo=1;foo+{eval:foo=2;foo}+{eval:foo=3;foo}',
            expected=dict(rvalue=Quantity(6, 'dimensionless'),
                          type=DataType.Integer,
                          label='foo+foo+foo',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue=Quantity(6, 'dimensionless'),
                                wvalue=None
                                ),
            expectedshape=None
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:True',
            expected=dict(rvalue=True,
                          type=DataType.Boolean,
                          label='True',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue=True,
                                wvalue=None
                                ),
            expectedshape=None
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:foo=1;bar=2;foo==bar',
            expected=dict(rvalue=False,
                          type=DataType.Boolean,
                          label='foo==bar',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue=False,
                                wvalue=None
                                ),
            expectedshape=None
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:[[True, False, True]]*3',
            expected=dict(rvalue=[[True, False, True]] * 3,
                          type=DataType.Boolean,
                          label='[[True, False, True]]*3',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue=[[True, False, True]] * 3,
                                wvalue=None
                                ),
            expectedshape=(3, 3)
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:"1m"',
            expected=dict(rvalue="1m",
                          type=DataType.String,
                          label='"1m"',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue="1m",
                                wvalue=None
                                ),
            expectedshape=None
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:"m"*3',
            expected=dict(rvalue="mmm",
                          type=DataType.String,
                          label='"m"*3',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue="mmm",
                                wvalue=None
                                ),
            expectedshape=None
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:"2+5-10"',
            expected=dict(rvalue="2+5-10",
                          type=DataType.String,
                          label='"2+5-10"',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue="2+5-10",
                                wvalue=None
                                ),
            expectedshape=None
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:[["HelloWorld", "HelloWorld", "HelloWorld"]]*3',
            expected=dict(rvalue=[["HelloWorld", "HelloWorld", "HelloWorld"]] * 3,
                          type=DataType.String,
                          label='[["HelloWorld", "HelloWorld",' +
                                ' "HelloWorld"]]*3',
                          writable=False,
                          ),
            expected_attrv=dict(rvalue=[["HelloWorld", "HelloWorld",
                                         "HelloWorld"]] * 3,
                                wvalue=None
                                ),
            expectedshape=(3, 3)
            )
@insertTest(helper_name='read_attr',
            attr_fullname='eval:@os.*/path.exists("%s")' % __file__,
            expected=dict(rvalue=True,
                          type=DataType.Boolean,
                          label='path.exists("%s")' % __file__,
                          writable=False,
                          ),
            expected_attrv=dict(rvalue=True,
                                wvalue=None
                                ),
            expectedshape=None
            )
@insertTest(helper_name='write_read_attr',
            attr_fullname='eval:@taurus.core.evaluation.test.res.mymod.MyClass()/self.foo',
            setvalue=Quantity(1, 'm'),
            expected=dict(rvalue=Quantity(1, 'm'),
                          wvalue=Quantity(1, 'm'),
                          type=DataType.Integer,
                          label='self.foo',
                          data_format=DataFormat._0D,
                          writable=True,
                          range=[None, None],
                          alarms=[None, None],
                          warnings=[None, None]
                          ),
            expected_attrv=dict(rvalue=Quantity(1, 'm'),
                                wvalue=Quantity(1, 'm'),
                                quality=AttrQuality.ATTR_VALID
                                )
            )
class EvalAttributeTestCase(unittest.TestCase):

    def read_attr(self, attr_fullname, expected={}, expected_attrv={},
                  expectedshape=None):
        """check creation and correct read of an evaluationAttribute"""

        a = taurus.Attribute(attr_fullname)
        read_value = a.read()

        msg = ('read() for "{0}" did not return an EvaluationAttrValue ' +
               '(got a {1})').format(attr_fullname,
                                     read_value.__class__.__name__)
        self.assertTrue(isinstance(read_value, EvaluationAttrValue), msg)

        # Test attribute
        for k, exp in expected.items():
            try:
                got = getattr(a, k)
            except AttributeError:
                msg = ('The attribute, "%s" does not provide info on %s' %
                       (attr_fullname, k))
                self.fail(msg)
            msg = ('%s for "%s" should be %r (got %r)' %
                   (attr_fullname, k,  exp, got))
            self.__assertValidValue(exp, got, msg)

        # Test attribute value
        for k, exp in expected_attrv.items():
            try:
                got = getattr(read_value, k)
            except AttributeError:
                msg = ('The read value for "%s" does not provide info on %s' %
                       (attr_fullname, k))
                self.fail(msg)
            msg = ('%s for "%s" should be %r (got %r)' %
                   (attr_fullname, k,  exp, got))
            self.__assertValidValue(exp, got, msg)

        if expectedshape is not None:
            shape = numpy.shape(read_value.rvalue)
            msg = ('rvalue.shape for %s should be %r (got %r)' %
                   (attr_fullname, expectedshape, shape))
            self.assertEqual(shape, expectedshape, msg)

    def write_read_attr(self, attr_fullname=None, setvalue=None, expected=None,
                        expected_attrv=None, expectedshape=None):
        """check creation and correct write-and-read of an attribute"""

        if expected is None:
            expected = {}
        if expected_attrv is None:
            expected_attrv = {}

        name = attr_fullname
        a = taurus.Attribute(attr_fullname)

        if setvalue is None:
            read_value = a.read()
        else:
            a.write(setvalue)
            read_value = a.read(cache=False)

        msg = ('read() for "%s" does not return an EvaluationAttrValue' +
               '(got a %s)') % (attr_fullname, read_value.__class__.__name__)
        self.assertTrue(isinstance(read_value, EvaluationAttrValue), msg)

        # Test attribute
        for k, exp in expected.items():
            try:
                got = getattr(a, k)
            except AttributeError:
                msg = ('The attribute, "%s" does not provide info on %s' %
                       (attr_fullname, k))
                self.fail(msg)
            msg = ('%s for "%s" should be %r (got %r)' %
                   (k, attr_fullname, exp, got))
            self.__assertValidValue(exp, got, msg)

        # Test attribute value
        for k, exp in expected_attrv.items():
            try:
                got = getattr(read_value, k)
            except AttributeError:
                msg = ('The read value for "%s" does not provide info on %s' %
                       (attr_fullname, k))
                self.fail(msg)
            msg = ('%s for the value of %s should be %r (got %r)' %
                   (k, attr_fullname, exp, got))
            self.__assertValidValue(exp, got, msg)

        if expectedshape is not None:
            msg = ('rvalue.shape for %s should be %r (got %r)' %
                   (attr_fullname, expectedshape, read_value.rvalue.shape))
            self.assertEqual(read_value.rvalue.shape, expectedshape, msg)


    def __assertValidValue(self, exp, got, msg):
        # if we are dealing with quantities, use the magnitude for comparing
        if isinstance(got, Quantity):
            got = got.to(Quantity(exp).units).magnitude
        if isinstance(exp, Quantity):
            exp = exp.magnitude
        try:
            # for those values that can be handled by numpy.allclose()
            chk = numpy.allclose(got, exp)
        except:
            # for the rest
            if isinstance(got, numpy.ndarray):
                got = got.tolist()
            chk = bool(got == exp)

        self.assertTrue(chk, msg)

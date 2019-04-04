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

"""Test for taurus.core.taurushelper"""

#__all__ = []

__docformat__ = 'restructuredtext'

import numpy
import functools
import unittest
from taurus.core.units import Quantity
import taurus
from taurus.test import insertTest
from taurus.core import (TaurusElementType, TaurusAttribute, TaurusDevice,
                         TaurusAuthority, DataType, TaurusAttrValue, DataFormat)

# decorators
isValid = functools.partial(insertTest, helper_name='isValid')
isInvalid = functools.partial(insertTest, helper_name='isValid',
                              expected=False)
isValidAuth = functools.partial(insertTest, helper_name='isValid',
                                elementType=TaurusElementType.Authority)
isInvalidAuth = functools.partial(insertTest, helper_name='isValid',
                                  expected=False,
                                  elementType=TaurusElementType.Authority)
isValidDev = functools.partial(insertTest, helper_name='isValid',
                               elementType=TaurusElementType.Device)
isInvalidDev = functools.partial(insertTest, helper_name='isValid',
                                 expected=False,
                                 elementType=TaurusElementType.Device)
isValidAttr = functools.partial(insertTest, helper_name='isValid',
                                elementType=TaurusElementType.Attribute)
isInvalidAttr = functools.partial(insertTest, helper_name='isValid',
                                  expected=False,
                                  elementType=TaurusElementType.Attribute)

from taurus import tauruscustomsettings
DEFAULT_SCHEME = getattr(tauruscustomsettings, 'DEFAULT_SCHEME')


@isValidAuth(name='//implicittangodb:123', skip=(DEFAULT_SCHEME != 'tango'))
@isValidAuth(name='tango://foo:10000')
@isInvalidAuth(name='tango://foo bar:10000')
@isInvalidAuth(name='tango://db')
@isInvalidAuth(name='tango://db:10000/a/b/c')
@isInvalidAuth(name='tango://db:')
@isInvalidAuth(name='tango://db:10000/')
@isInvalidAuth(name='tango://a/b/c')
@isValidDev(name='implicit/tango/devname', skip=(DEFAULT_SCHEME != 'tango'))
@isValidDev(name='implicittangoalias', skip=(DEFAULT_SCHEME != 'tango'))
@isValidDev(name='tango://db:10000/alias')
@isValidDev(name='tango://foo:10000/a/b/c')
@isValidDev(name='tango:alias')
@isValidDev(name='tango://alias', strict=False)
@isValidDev(name='tango:a/b/c')
@isValidDev(name='tango:a/b  /c')
@isValidDev(name='tango://a/b/c', strict=False)
@isInvalidDev(name='tango://a/b/c', strict=True)
@isInvalidDev(name='tango://alias', strict=True)
@isInvalidDev(name='tango:a/b/c/')
@isInvalidDev(name='tango:a/b')
@isInvalidDev(name='tango:a/b/c/d')
@isValidAttr(name='implicittangoalias/attrname',
             skip=(DEFAULT_SCHEME != 'tango'))
@isValidAttr(name='implicit/tango/attr/name', skip=(DEFAULT_SCHEME != 'tango'))
@isValidAttr(name='tango:alias/attr')
@isValidAttr(name='tango://alias/attr', strict=False)
@isValidAttr(name='tango://foo:10000/a/b/c/d')
@isValidAttr(name='tango:a/b/c/d')
@isValidAttr(name='tango://a/b/c/d', strict=False)
# @isValidAttr(name='epics://my:example.RBV') disabled till bug #215 is fixed
@isValidAttr(name='tango:a/b  /c/d')
@isInvalidAttr(name='tango:a/b/c/d/')
@isInvalidAttr(name='tango:a/b/c')
@isValidAttr(name='implicit/tango/attr/name#label',
             skip=(DEFAULT_SCHEME != 'tango'))
@isValidAttr(name='implicittangoalias/attrname#label',
             skip=(DEFAULT_SCHEME != 'tango'))
@isValidAttr(name='tango:alias/attr#label')
@isValidAttr(name='tango://foo:10000/a/b/c/d#label')
@isValidAttr(name='tango:a/b/c/d#label')
@isValidAttr(name='tango:a/b  /c/d#label')
@isValidAttr(name='tango://a/b/c/d?configuration=label', strict=False)
@isInvalidAttr(name='tango://a/b/c/d#label', strict=True)
@isInvalidAttr(name='tango://a/b')
@isInvalidAttr(name='tango://a/b/c')
@isInvalidAttr(name='tango://a/b/c/d')
@isValidAuth(name='eval://localhost')
@isInvalidAuth(name='eval://foo')
@isInvalidAuth(name='evaluation://db=foo')
@isInvalidAuth(name='evaluation://localhost')
@isInvalidAuth(name='eval://db=foo')
@isInvalidAuth(name='eval://localhost#')
@isInvalidAuth(name='eval://')
@isInvalidAuth(name='evaluation://user@host:port')
@isInvalidAuth(name='eval://user@host:port')
@isInvalidAuth(name='eval://user:host@port')
@isInvalidAuth(name='eval://user@host:port/1')
@isInvalidAuth(name='eval:{tango://localhost:10000}')
@isValidAuth(name='evaluation://db=foo', strict=False)
@isValidAuth(name='eval://db=foo', strict=False)
@isInvalidAuth(name='eval://foo', strict=False)
@isInvalidAuth(name='eval://DB=foo', strict=False)
@isValidDev(name='eval:@module.EvalClass')
@isValidDev(name='eval:@1')
@isValidDev(name='eval:@Foo')
@isValidDev(name='eval:@FOO')
@isValidDev(name='eval://localhost/@Foo')
@isValidDev(name='eval://localhost/@mod.Class')
@isInvalidDev(name='evaluation:@Foo')
@isInvalidDev(name='eval://db=foo')
@isInvalidDev(name='eval://dev=bar')
@isInvalidDev(name='eval:')
@isInvalidDev(name='eval:@Foo#')
@isInvalidDev(name='eval:1')
@isInvalidDev(name='eval:DEV=bar')
@isInvalidDev(name='eval:@DEV=bar')
@isValidDev(name='eval://db=foo;dev=bar', strict=False)
@isValidDev(name='eval://dev=bar', strict=False)
@isValidDev(name='eval://dev=bar?a=1;b=2', strict=False)
# yes, this is ok
@isValidDev(name='eval://dev=bar?configuration', strict=False)
@isInvalidDev(name='eval:dev=bar', strict=False)
@isInvalidDev(name='eval://db=Bla/dev=bar', strict=False)
@isValidAttr(name='eval:1')
@isValidAttr(name='eval:/1')
@isValidAttr(name='eval:@bar/1')
@isValidAttr(name='evaluation://db=foo;dev=bar;1', strict=False)
@isValidAttr(name='eval://db=foo;dev=bar;1', strict=False)
@isValidAttr(name='eval://dev=bar;foo', strict=False)
@isValidAttr(name='eval://2+3', strict=False)
@isValidAttr(name='evaluation://2+3', strict=False)
@isValidAttr(name='eval://a+b?a=2;b=3', strict=False)
@isValidAttr(name='eval://a*{tango://a/b/c/d}?a=10', strict=False)
@isValidAttr(name='eval://dev=bar/1', strict=False)
@isValidAttr(name='eval://a[:2]?a=[1,2,3]', strict=False)
@isValidAttr(name='eval://{eval://1}', strict=False)
@isValidAttr(name='eval://{eval://{eval://1}}', strict=False)
@isValidAttr(name='eval:{tango:a/b/c/d}*2')
@isValidAttr(name='eval:k=2;a={tango:a/b/c/d};a*k')
@isValidAttr(name='eval:@mymod.MyEvalClass/k=2;a={tango:a/b/c/d};a*k')
@isValidAttr(name='eval://localhost/k=2;a={tango:a/b/c/d};a*k')
@isValidAttr(name='eval://localhost/@Foo/k=2;a={tango:a/b/c/d};a*k')
@isValidAttr(name='eval:a=[1,2,3];a[:2]')
@isValidAttr(name='eval:{eval:1}')
@isValidAttr(name='eval:{eval:{eval:1}}')
@isInvalidAttr(name='EVAL:1')
@isInvalidAttr(name='evaluation:1')
@isInvalidAttr(name='eval://db=foo;dev=bar;1')
@isInvalidAttr(name='eval://2+3')
@isInvalidAttr(name='evaluation://2+3')
@isInvalidAttr(name='eval:a+b?a=2;b=3')
@isValidAttr(name='eval:foo#')
@isInvalidAttr(name='eval:{tango:a/b/c}*2')
@isInvalidAttr(name='eval:k-a;k=2;a=3')
@isInvalidAttr(name='eval:a=1;b=2;a+b;a*2')
@isInvalidAttr(name='eval:a=1;b=2;a+b;;;')
@isInvalidAttr(name='eval:a=1;;;b=2;a+b')
@isValidAttr(name='eval:a=2;b=3;a+b#label')
@isValidAttr(name='eval:{tango:a/b/c/d}#')
@isValidAttr(name='eval:{tango:a/b/c/d}*2#label')
@isValidAttr(name='eval:k=2;a=3;a*k#units')
@isValidAttr(name='eval://localhost/@mymod.MyClass/1#label')
@isValidAttr(name='eval:{tango:a/b/c/d}*2#1+2')
@isInvalidAttr(name='eval:{tango:a/b/c}*2#')
@isInvalidAttr(name='eval:2# ')
@isInvalidAttr(name='evaluation:1#label')
@isInvalidAttr(name='eval://dev=bar;foo#label')
@isInvalidAttr(name='eval:a+b;a=2;b=3#label')
@isInvalidAttr(name='eval://foo')
@isValidAttr(name='evaluation://db=foo;dev=bar;1?configuration=label', strict=False)
@isValidAttr(name='eval://db=foo;dev=bar;1?configuration=label', strict=False)
@isValidAttr(name='eval://dev=bar;foo?configuration=label', strict=False)
@isValidAttr(name='eval://2+3?configuration=label', strict=False)
@isValidAttr(name='eval://a+b?a=2;b=3?configuration=label', strict=False)
class IsValidNameTestCase(unittest.TestCase):
    '''Class to test validity or invalidity of taurus URIs'''

    def isValid(self, name=None, expected=True, elementType=None,
                strict=True, skip=False, skipmsg='Test explicitly disabled'):
        '''Helper method to test validity or invalidity of taurus URIs'''
        if skip:
            self.skipTest(skipmsg)
        if elementType is None:
            elementName = '<any>'
        else:
            elementName = TaurusElementType.whatis(elementType)
            elementType = [elementType]
        manager = taurus.Manager()
        scheme = manager.getScheme(name)
        supportedSchemes = list(manager.getPlugins().keys())
        if scheme not in supportedSchemes:
            self.skipTest('"%s" scheme not supported' % scheme)
        returned = taurus.isValidName(name, etypes=elementType, strict=strict)

        msg = ('isValidName returns %s (expected %s for name=%s and etype=%s)' %
               (returned, expected, name, elementName))
        self.assertEqual(returned, expected, msg)

    def test_unsupported(self):
        '''Testing that an unsupported scheme validates as False'''
        returned = taurus.isValidName('_unsupported_://foo')
        msg = ('Validating unsupported schemes must return False (got %s)' %
               returned)
        self.assertFalse(returned, msg)


#@insertTest(helper_name='get_object', name='eval://foo')
@insertTest(helper_name='get_object', name='eval://localhost')
class AuthorityTestCase(unittest.TestCase):
    '''TestCase for the taurus.Authority helper'''

    def get_object(self, name=None, klass=None):
        '''check if Authority returns the expected type'''
        if klass is None:
            klass = TaurusAuthority
        manager = taurus.Manager()
        scheme = manager.getScheme(name)
        supportedSchemes = list(manager.getPlugins().keys())
        if scheme not in supportedSchemes:
            self.skipTest('"%s" scheme not supported' % scheme)
        a = taurus.Authority(name)
        msg = ('%s("%s") is not an instance of %s (it is %s)' %
               (taurus.Authority.__name__, name,
                klass.__name__, a.__class__.__name__))
        self.assertTrue(isinstance(a, klass), msg)


@insertTest(helper_name='get_object', name='tango:a/b/c')
@insertTest(helper_name='get_object', name='eval://localhost/@Foo')
@insertTest(helper_name='get_object', name='eval:@Foo')
@insertTest(helper_name='get_object', name='eval://dev=Foo')
@insertTest(helper_name='get_object', name='eval:@datetime.*')
@insertTest(helper_name='get_object', name='eval:@d=datetime.date(2017,3,29)')
class DeviceTestCase(unittest.TestCase):
    '''TestCase for the taurus.Device helper'''

    def get_object(self, name=None, klass=None):
        '''check if Device returns the expected type'''
        if klass is None:
            klass = TaurusDevice
        manager = taurus.Manager()
        scheme = manager.getScheme(name)
        supportedSchemes = list(manager.getPlugins().keys())
        if scheme not in supportedSchemes:
            self.skipTest('"%s" scheme not supported' % scheme)

        a = taurus.Device(name)
        msg = ('%s("%s") is not an instance of %s (it is %s)' %
               (taurus.Device.__name__, name,
                klass.__name__, a.__class__.__name__))

        self.assertTrue(isinstance(a, klass), msg)


@insertTest(helper_name='read_attr',
            name='eval:2*{eval:x=2;x}',
            expected=dict(label='2*x', data_format=DataFormat._0D,
                          type=DataType.Integer))
@insertTest(helper_name='read_attr',
            name='eval:x=-1;x+{eval:x=2;x}+{eval:x=10;x}',
            expected=dict(data_format=DataFormat._0D, wvalue=None, w_value=None,
                          label='x+x+x',
                          type=DataType.Integer))
@insertTest(helper_name='read_attr', name='eval://2*{eval://1.0}+{eval://2.0}',
            expected=dict(data_format=DataFormat._0D, type=DataType.Float,
                          label='2*1.0+2.0'))
@insertTest(helper_name='read_attr',
            name='eval:2*{tango:sys/tg_test/1/short_scalar}',
            expected=dict(data_format=DataFormat._0D, type=DataType.Integer,
                          label='2*short_scalar'))
@insertTest(helper_name='read_attr',
            name='eval:1==1',
            expected=dict(data_format=DataFormat._0D, type=DataType.Boolean,
                          label='1==1'))
@insertTest(helper_name='read_attr',
            name='eval:[1,2,3]',
            expected=dict(data_format=DataFormat._1D, type=DataType.Integer,
                          label='[1,2,3]'))
@insertTest(helper_name='read_attr',
            name='eval:img={tango:sys/tg_test/1/short_image_ro};img+10*rand(*img.shape)',
            expected=dict(data_format=DataFormat._2D, type=DataType.Float))
@insertTest(helper_name='read_attr',
            name='eval:{tango:sys/tg_test/1/string_image}',
            expected=dict(data_format=DataFormat._2D, type=DataType.String))
@insertTest(helper_name='get_object', name='tango:a/b/c/d')
@insertTest(helper_name='read_attr', name='tango:sys/tg_test/1/short_scalar',
            expected=dict(data_format=DataFormat._0D, type=DataType.Integer,
                          label='short_scalar'))
@insertTest(helper_name='read_attr', name='tango:sys/tg_test/1/float_image',
            expected=dict(data_format=DataFormat._2D, type=DataType.Float,
                          label='float_image'))
@insertTest(helper_name='read_attr', name='tango:sys/tg_test/1/boolean_scalar',
            expected=dict(data_format=DataFormat._0D, type=DataType.Boolean,
                          label='boolean_scalar'))
@insertTest(helper_name='read_attr', name='tango:sys/tg_test/1/double_spectrum',
            expected=dict(data_format=DataFormat._1D, type=DataType.Float,
                          label='double_spectrum'))
@insertTest(helper_name='read_attr', name='eval:1.0',
            expected=dict(rvalue=1.0, value=1.0,
                          wvalue=None, w_value=None, label='1.0',
                          type=DataType.Float, data_format=DataFormat._0D))
@insertTest(helper_name='read_attr', name='eval:x=3;x+1',
            expected=dict(rvalue=4, value=4, wvalue=None, w_value=None,
                          label='x+1',
                          type=DataType.Integer, data_format=DataFormat._0D))
@insertTest(helper_name='read_attr', name='eval:2*{eval:3}',
            expected=dict(rvalue=6, value=6, label='2*3',
                          wvalue=None, w_value=None,
                          type=DataType.Integer, data_format=DataFormat._0D))
@insertTest(helper_name='read_attr', name='eval:2*{eval:3*{eval:4}}',
            expected=dict(rvalue=24, value=24, label='2*3*4',
                          wvalue=None, w_value=None, type=DataType.Integer,
                          data_format=DataFormat._0D))
@insertTest(helper_name='read_attr', name='eval:1*{eval:2*{eval:3*{eval:4}}}',
            expected=dict(rvalue=24, value=24,
                          label='1*2*3*4',
                          wvalue=None, w_value=None, type=DataType.Integer,
                          data_format=DataFormat._0D))
@insertTest(helper_name='read_attr', name='eval:{eval:1}+{eval:9}',
            expected=dict(rvalue=10, value=10, label='1+9',
                          wvalue=None, w_value=None, type=DataType.Integer,
                          data_format=DataFormat._0D))
@insertTest(helper_name='read_attr', name='eval:"aaa"+"bbb"',
            expected=dict(rvalue="aaabbb", value="aaabbb", label='"aaa"+"bbb"',
                          wvalue=None, w_value=None, type=DataType.String,
                          data_format=DataFormat._0D))
@insertTest(helper_name='read_attr', name='eval:{eval:"aaa"}+{eval:"bbb"}',
            expected=dict(rvalue="aaabbb", value="aaabbb",
                          wvalue=None, w_value=None,
                          label='"aaa"+"bbb"',
                          type=DataType.String, data_format=DataFormat._0D))
@insertTest(helper_name='read_attr', name='eval:{eval:"a"}*3',
            expected=dict(rvalue="aaa", value="aaa", label='"a"*3',
                          wvalue=None, w_value=None, type=DataType.String,
                          data_format=DataFormat._0D))
@insertTest(helper_name='read_attr', name='eval:len("abc")',
            expected=dict(rvalue=3, wvalue=None, value=3, w_value=None,
                          label='len("abc")',
                          type=DataType.Integer, data_format=DataFormat._0D))
@insertTest(helper_name='read_attr', name='eval:"a.b.c".split(".")',
            expected=dict(rvalue=['a', 'b', 'c'], value=['a', 'b', 'c'],
                          wvalue=None, w_value=None,
                          label='"a.b.c".split(".")', type=DataType.String,
                          data_format=DataFormat._1D))
@insertTest(helper_name='read_attr', name='eval:[1,1,1].count(1)',
            expected=dict(rvalue=3, wvalue=None, value=3, w_value=None,
                          type=DataType.Integer, data_format=DataFormat._0D))
@insertTest(helper_name='read_attr', name='eval:[1,2,3].reverse()',
            expected=dict(rvalue=None, value=None, wvalue=None, w_value=None,
                          label='[1,2,3].reverse()'))
@insertTest(helper_name='read_attr',
            name='eval:[1,1,3].count(1)*{eval:[1,1,3].count(1)*{eval:2}}',
            expected=dict(rvalue=8, value=8, wvalue=None, w_value=None,
                          type=DataType.Integer))
@insertTest(helper_name='read_attr', name='eval:"split.split".split("split")',
            expected=dict(rvalue=['', '.', ''], value=['', '.', ''],
                          wvalue=None, w_value=None,
                          label='"split.split".split("split")',
                          type=DataType.String))
@insertTest(helper_name='read_attr', name='eval:Quantity(1.0)',
            expected=dict(rvalue=Quantity(1.0), value=1.0,
                          w_value=None, wvalue=None, label='Quantity(1.0)',
                          type=DataType.Float, data_format=DataFormat._0D))
@insertTest(helper_name='read_attr', name='eval:Quantity("1km")',
            expected=dict(rvalue=Quantity(1000, 'm'), value=1,
                          w_value=None, wvalue=None, label='Quantity("1km")',
                          type=DataType.Integer, data_format=DataFormat._0D))
@insertTest(helper_name='read_attr', name='eval:Quantity("0.1km")',
            expected=dict(rvalue=Quantity(100, 'm'), value=0.1,
                          w_value=None, wvalue=None, label='Quantity("0.1km")',
                          type=DataType.Float, data_format=DataFormat._0D))
@insertTest(helper_name='read_attr', name='eval:Q("1m")*3+{eval:Q(3,"dm")}',
            expected=dict(rvalue=Quantity("3.3m"), value=3.3,
                          wvalue=None, w_value=None,
                          label='Q("1m")*3+Q(3,"dm")',
                          type=DataType.Float))
@insertTest(helper_name='read_attr', name='eval:Q("1km").to("mm").magnitude',
            expected=dict(rvalue=1e6, value=1e6, wvalue=None, w_value=None,
                          label='Q("1km").to("mm").magnitude',
                          type=DataType.Float))
@insertTest(helper_name='read_attr',
            name='eval:@d=datetime.date(1931,4,14)/d.isoformat()',
            expected=dict(rvalue='1931-04-14', value='1931-04-14',
                          wvalue=None, w_value=None,
                          label='d.isoformat()',
                          type=DataType.String))
@insertTest(helper_name='read_attr', name='eval:1#')
class AttributeTestCase(unittest.TestCase):
    '''TestCase for the taurus.Attribute helper'''

    def get_object(self, name=None, klass=None):
        '''check if Attribute returns the expected type'''
        if klass is None:
            klass = TaurusAttribute
        manager = taurus.Manager()
        scheme = manager.getScheme(name)
        supportedSchemes = list(manager.getPlugins().keys())
        if scheme not in supportedSchemes:
            self.skipTest('"%s" scheme not supported' % scheme)
        a = taurus.Attribute(name)
        msg = ('%s("%s") is not an instance of %s (it is %s)' %
               (taurus.Attribute.__name__, name,
                klass.__name__, a.__class__.__name__))
        self.assertTrue(isinstance(a, klass), msg)
        return a

    def read_attr(self, name=None, expected=None, skip=False,
                  skipmsg='Test explicitly disabled'):
        '''check creation and correct reading of an attribute'''
        if skip:
            self.skipTest(skipmsg)
        if expected is None:
            expected = {}
        a = self.get_object(name)
        readvalue = a.read()
        msg = ('read() for "%s" did not return a TaurusAttrValue (got a %s)' %
               (name, readvalue.__class__.__name__))
        self.assertTrue(isinstance(readvalue, TaurusAttrValue), msg)
        for k, exp in expected.items():
            try:
                got = getattr(readvalue, k)
            except AttributeError:
                msg = ('The read value for "%s" does not provide info on %s' %
                       (name, k))
                self.fail(msg)
            msg = ('Expected %s=%r for "%s" (got %r)' % (k, exp, name, got))

            try:
                self.assertEqual(got, exp, msg)
            except ValueError:
                # Validate the arrays
                try:
                    # for those values that can be handled by numpy.allclose()
                    chk = numpy.allclose(got, exp)
                except:
                    # for the rest
                    if isinstance(got, numpy.ndarray):
                        got = got.tolist()
                    chk = bool(got == exp)

                self.assertTrue(chk, msg)


class ValidatorFromName(unittest.TestCase):
    """TestCase for the taurus.getValidatorFromName helper"""

    def test_getValidatorFromName(self):
        """check that getValidatorFromName returns the expected values"""

        self.assertIsInstance(
            taurus.getValidatorFromName('eval:@foo'),
            taurus.core.evaluation.evalvalidator.EvaluationDeviceNameValidator
        )
        self.assertIsNone(taurus.getValidatorFromName('eval:@/'))
        self.assertIsNone(taurus.getValidatorFromName('unsupported:scheme'))


if __name__ == '__main__':
    pass

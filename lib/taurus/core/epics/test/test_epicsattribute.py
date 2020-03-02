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

"""Test for epicsattributes..."""

import os
import sys
import numpy
import subprocess
import unittest
from taurus.core.units import Quantity
import taurus
from taurus.test import insertTest, getResourcePath
from taurus.core.taurusbasetypes import DataType, AttrQuality, DataFormat
from taurus.core.taurusbasetypes import TaurusAttrValue
import pytest




@insertTest(helper_name='write_read_attr',
            attrname='ca:test:a',
            setvalue=Quantity('1000mm'),
            expected=dict(rvalue=Quantity('1m'),
                          type=DataType.Float,
                          writable=True,
                          data_format=DataFormat._0D,
                          range=[Quantity('-10m'), Quantity('10m')],
                          alarms=[None, None],
                          warnings=[None, None],
                          ),
            expected_attrv=dict(rvalue=Quantity('1m'),
                                wvalue=Quantity('1m'),
                                quality=AttrQuality.ATTR_VALID,
                                error=None,
                                )
            )
@unittest.skipIf(('epics' in sys.modules) is False,
                 "epics module is not available")
@pytest.mark.xfail(reason='epics CV init issues need fixing in this test')
class AttributeTestCase(unittest.TestCase):
    """TestCase for the taurus.Attribute helper"""
    _process = None

    @classmethod
    def setUpClass(cls):
        """Run the epics_test softIoc"""
        db_name = getResourcePath(
            'taurus.core.epics.test.res', 'epics_test.db')
        args = ['softIoc', '-m', 'INST=test', '-d', db_name]
        dev_null = open(os.devnull, 'wb')
        cls._process = subprocess.Popen(args, stdout=dev_null, stderr=dev_null)

    @classmethod
    def tearDownClass(cls):
        """Terminate the epics_test softIoc process"""
        if cls._process:
            cls._process.terminate()
        else:
            taurus.warning('Process not started, cannot terminate it.')

    def write_read_attr(self, attrname=None, setvalue=None, expected=None,
                        expected_attrv=None, expectedshape=None):
        """check creation and correct write-and-read of an attribute"""
        if expected is None:
            expected = {}
        if expected_attrv is None:
            expected_attrv = {}

        a = taurus.Attribute(attrname)

        if setvalue is None:
            read_value = a.read(cache=False)
        else:
            read_value = a.write(setvalue,  with_read=True)

        # avoid EpicsAttribute disconnection warning
        # a.getPV().disconnect()
        msg = ('read() for "%s" did not return a TaurusAttrValue (got a %s)' %
               (attrname, read_value.__class__.__name__))
        self.assertTrue(isinstance(read_value, TaurusAttrValue), msg)

        # Test attribute
        for k, exp in expected.items():
            try:
                got = getattr(a, k)
            except AttributeError:
                msg = ('The attribute, "%s" does not provide info on %s' %
                       (attrname, k))
                self.fail(msg)
            msg = ('%s for "%s" should be %r (got %r)' %
                   (k, attrname,  exp, got))
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
            # for those values that can be handled by numpy.allclose()
            chk = numpy.allclose(got, exp)
        except:
            if isinstance(got, numpy.ndarray):
                # uchars were not handled with allclose
                # UGLY!! but numpy.all does not work
                chk = got.tolist() == exp.tolist()
            else:
                # for the rest
                chk = bool(got == exp)

        self.assertTrue(chk, msg)
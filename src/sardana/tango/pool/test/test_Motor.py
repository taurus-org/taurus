#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""Tests Read Position from Sardana using PyTango"""
import PyTango
from taurus.external import unittest
from sardana.tango.pool.test import BasePoolTestCase
from sardana.tango.core.util import get_free_alias
import numbers

class ReadMotorPositionOutsideLim(BasePoolTestCase, unittest.TestCase):
    """TestCase class for testing that read position is possible when
    motor is out of SW limits. Verify that position has a numeric type.
    """
    def setUp(self):
        """Create dummy motor controller and dummy motor element
        """
        super(ReadMotorPositionOutsideLim, self).setUp()
        cls = 'DummyMotorController'
        self.ctrl_name = get_free_alias(PyTango.Database(), "readposctrl")
        props = ()
        ctrl = self.pool.createController(cls, self.ctrl_name, *props)
        #Add extra timeout of 3 seconds.
        if ctrl is None:
            elements_info = self.pool.getElementsInfo()
            ctrl = self.pool._wait_for_element_in_container(elements_info,
                                                  self.ctrl_name, timeout = 3)
        self.elem_name = get_free_alias(PyTango.Database(), "mot_test")
        elem_axis = 1
        self.elem = self.pool.createElement(self.elem_name, ctrl, elem_axis)
        self.elem.DefinePosition(0)
    
    @unittest.expectedFailure #Note: this tests known bug #238
    def test_read_position_outside_sw_lim(self):
        """Test bug #238: reading position when motor is out of SW lims.
        Verify that position has a numeric type."""
        pc = self.elem.get_attribute_config("position")
        pc.min_value = "1"
        pc.max_value = "2"
        self.elem.set_attribute_config(pc)
        try:
            posread = self.elem.read_attribute('position').value
        except Exception as e_read:
            msg = ("Position cannot be read. Exception: %s" % e_read)
            self.fail(msg)
        msg = ("Position is not a number")
        self.assertIsInstance(posread, numbers.Number, msg)

    def tearDown(self):
        """Remove motor element and motor controller
        """
        self.pool.DeleteElement(self.elem_name)
        self.pool.DeleteElement(self.ctrl_name)
        super(ReadMotorPositionOutsideLim, self).tearDown()

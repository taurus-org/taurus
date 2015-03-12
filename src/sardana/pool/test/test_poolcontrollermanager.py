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

from taurus.external import unittest
from sardana.pool.poolcontrollermanager import ControllerManager

class ControllerManagerTestCase(unittest.TestCase):
    """Unittest of ControllerManager Class"""

    def setUp(self):
        """Create a ControllerManager"""
        self.cm = ControllerManager()

    def test_init(self):
        """Verify that the created ControllerManager is a ControllerManager
        instance."""
        msg = 'ControllerManager constructor does not create ' +\
              'ControllerManager instance'
        self.assertIsInstance(self.cm, ControllerManager, msg)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.cm = None
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
from sardana.pool.test import (FakePool, createPoolController,
                               dummyPoolCTCtrlConf01)
from sardana.pool.poolcontroller import PoolController

class PoolControllerTestCase(unittest.TestCase):
    """Unittest of PoolController Class"""

    def setUp(self):
        """Instantiate a fake Pool and create a Controller"""
        pool = FakePool()
        self.pc = createPoolController(pool, dummyPoolCTCtrlConf01)

    def test_init(self):
        """Verify that the created Controller is an instance of
        PoolController"""
        msg = 'PoolController constructor does not create ' +\
              'PoolController instance'
        self.assertIsInstance(self.pc, PoolController, msg)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.pc = None

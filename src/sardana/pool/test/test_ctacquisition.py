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

import time
from taurus.external import unittest
from sardana.pool.poolmeasurementgroup import PoolMeasurementGroup
from sardana.pool.test import (FakePool, createPoolController,
                               createPoolMeasurementGroup,
                               createPoolCounterTimer, dummyCounterTimerConf01,
                               dummyPoolCTCtrlConf01,
                               dummyMeasurementGroupConf01)

class PoolMeasurementGroupTestCase(unittest.TestCase):
    """Class used for an acquisition done by a Measurement Group with a
    dummyCounterTimer channel. The Measurement Group runs with a freshly created
    fake Pool which does not depends on the Sardana Pool.
    """

    def setUp(self):
        """Setup:
        - Use resources for Controller, CounterTimer and MeasurementGroup
        features.
        - Create Controller, CounterTimer and MeasurementGroup.
        """
        pool = FakePool()

        pc = createPoolController(pool, dummyPoolCTCtrlConf01)
        pct = createPoolCounterTimer(pool, pc, dummyCounterTimerConf01)

        pc.add_element(pct)
        pool.add_element(pc)
        pool.add_element(pct)

        self.pmg = createPoolMeasurementGroup(pool, dummyMeasurementGroupConf01)
        self._pct = pct # keep a reference to use it in test_acquisition

    def test_init(self):
        """check that the PoolMeasurementGroup is correctly instantiated"""
        msg = 'PoolMeasurementGroup constructor does not create ' +\
              'PoolMeasurementGroup instance'
        self.assertIsInstance(self.pmg, PoolMeasurementGroup, msg)

    def test_acquisition(self):
        """Test acquisition using the created measurement group without
        using a Sardana pool."""
        msg = 'Pool Measurement Group does not acquire'
        integ_time = 1
        self.pmg.set_integration_time(integ_time)
        self.pmg.start_acquisition()

        acq = self.pmg.get_acquisition()._ct_acq
        # 'acquiring..'
        while acq.is_running():
            time.sleep(0.05)
        values = acq.raw_read_value_loop()
        self.assertEqual(values[self._pct].value, integ_time, msg)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.pmg = None
        self._pct = None

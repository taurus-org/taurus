import time
from taurus.external import unittest
from sardana.pool.poolmeasurementgroup import PoolMeasurementGroup
from sardana.pool.test import (PoolFake, createPoolController,
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
        pool = PoolFake()

        pc = createPoolController(pool, dummyPoolCTCtrlConf01)
        pct = createPoolCounterTimer(pool, pc, dummyCounterTimerConf01)

        pc.add_element(pct)
        pool.add_element(pc)
        pool.add_element(pct)

        self.pmg = createPoolMeasurementGroup(pool, dummyMeasurementGroupConf01)

    def test_init(self):
        msg = 'PoolMeasurementGroup constructor does not create ' +\
              'PoolMeasurementGroup instance'
        self.assertIsInstance(self.pmg, PoolMeasurementGroup, msg)

    def test_acquisition(self):
        """Test acquisition using the created measurement group without
        using a Sardana pool."""
        msg = 'Pool Measurement Group does not acquire'
        self.pmg.set_integration_time(1)
        self.pmg.start_acquisition()

        acq = self.pmg.get_acquisition()._ct_acq
        # 'acquiring..'
        while acq.is_running():
            time.sleep(0.05)
        values = {}
        acq.raw_read_value_loop(ret=values)
        self.assertEqual(values[values.keys()[0]].value, 1, msg)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

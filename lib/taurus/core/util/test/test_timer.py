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

"""Test for taurus.core.util.timer"""

#__all__ = []

__docformat__ = 'restructuredtext'

import time
import threading
import numpy
import unittest
import pytest
from taurus.core.util.timer import Timer


@pytest.mark.flaky(max_runs=3, min_passes=2)
class TimerTest(unittest.TestCase):
    '''Test case for testing the taurus.core.util.timer.Timer class'''

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.__count = 0
        self.__calltimes = []

    def tearDown(self):
        self.__count = 0
        self.__calltimes = []

    def test_calltimes(self):
        '''check the quality of the Timer's timing'''
        period = .1  # in s
        n = 10  # make this >2 !
        timeout = n * period + 2  # expected time +2 seconds margin
        tol = 0.001  # time tolerance for the various checks (in s)

        timer = Timer(period, self._callback, None, strict_timing=True,
                      sleep=.05, n=n)

        # Start the timer, wait till the callback is called n times and then s
        # and then stop it
        self.__nCalls = threading.Event()
        timer.start()
        self.__nCalls.wait(timeout)
        timer.stop()
        self.__nCalls.clear()

        # checking number of calls
        ts = numpy.array(self.__calltimes)
        msg = '%i calls expected (got %i)' % (n, ts.size)
        self.assertEqual(ts.size, n, msg)

        # checking drift
        totaltime = ts[-1] - ts[0]
        drift = abs(totaltime - ((n - 1) * period))
        msg = 'Too much drift (%g). Tolerance=%g' % (drift, tol)
        self.assertLess(drift, tol, msg)

        # checking period jitter (mean period and its standard dev)
        periods = numpy.diff(ts)
        mean = periods.mean()
        std = periods.std()
        msg = 'Wrong period. Expected: %g +/- %g Got: %g +/- %g' % (period, tol,
                                                                    mean, std)
        self.assertAlmostEqual(mean, period, msg=msg, delta=tol)
        self.assertLess(std, tol, msg)

    def _callback(self, sleep=0, n=5):
        '''store times at which it has been called, and signal when n calls
        have been done. If sleep>0 is passed, sleep that much in each call '''
        self.__calltimes.append(time.time())
        self.__count += 1
        time.sleep(sleep)
        if self.__count == n:
            self.__nCalls.set()  # signal that we have been called n times


if __name__ == '__main__':
    pass

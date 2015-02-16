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

"""Tests for scan macros"""

from taurus.external import unittest
from sardana.macroserver.macros.test import (RunStopMacroTestCase,
                                             testRun, testStop, SarDemoEnv)

#get handy motor names from sardemo
try:
    _MOTORS = SarDemoEnv().getMotors()
    _m1, _m2 = _MOTORS[:2]
except RuntimeError:
    import taurus
    from sardana import sardanacustomsettings
    door_name = getattr(sardanacustomsettings, 'UNITTEST_DOOR_NAME',
                        'UNDEFINED')
    taurus.warning("The door %s is not running. " % (door_name) +
                   "Ignore this message if you are building the documentation")
    _m1 = _m2 = 'motor_not_defined'
except Exception, e:
    import taurus
    taurus.debug(e)
    taurus.warning("It was not possible to retrieve the motor names. " +
                 "Ignore this message if you are building the documentation.")
    _m1 = _m2 = 'motor_not_defined'


def parsing_log_output(log_output):
    """A helper method to parse log output of an executed scan macro.
    :params log_output: (seq<str>) Result of macro_executor.getLog('output')
    (see description in :class:`.BaseMacroExecutor`).

    :return: (seq<number>) The numeric data of a scan.
    """
    first_data_line = 1
    scan_index = 0
    data = []
    for line, in log_output[first_data_line:]:
        # Get a list of elements without white spaces between them
        l = line.split()
        # Cast all elements of the scan line (l) to float
        l = [float(scan_elem) for scan_elem in l]
        # Cast index of scan to int (the first element of the list)
        l[scan_index] = int(l[scan_index])
        data.append(l)
    return data


class ANscanTest(RunStopMacroTestCase):

    """Not yet implemented. Once implemented it will test anscan.
    See :class:`.RunStopMacroTestCase` for requirements.
    """
    pass


class DNscanTest(ANscanTest):

    """Not yet implemented. Once implemented it will test the macro dnscanc.
    See :class:`ANscanTest` for requirements.
    """
    pass


class DNscancTest(DNscanTest):

    """Not yet implemented. Once implemented it will test the macro dnscanc.
    See :class:`DNscanTest` for requirements.
    """
    pass


@testRun(macro_params=[_m1, '0', '5', '4', '.1'], wait_timeout=float("inf"))
@testStop(macro_params=[_m1, '0', '5', '3', '.1'])
class AscanTest(ANscanTest, unittest.TestCase):

    """Test of ascan macro. See :class:`ANscanTest` for requirements.
    It verifies that macro ascan can be executed and stoped and tests
    the output of the ascan using data from log system and macro data.
    """
    macro_name = 'ascan'

    def macro_runs(self, macro_params=None, wait_timeout=float("inf")):
        """Reimplementation of macro_runs method for ascan macro.
        It verifies using double checking, with log output and data from
        the macro:

            - The motor initial and final positions of the scan are the
              ones given as input.

            - Intervals in terms of motor position between one point and
              the next one are equidistant.
        """
        #call the parent class implementation
        ANscanTest.macro_runs(self, macro_params=macro_params,
                              wait_timeout=wait_timeout)

        mot_name = macro_params[0]
        expected_init_pos = float(macro_params[1])
        expected_final_pos = float(macro_params[2])
        self.steps = int(macro_params[-2])
        interval = abs(expected_final_pos - expected_init_pos) / self.steps

        # Test data from macro (macro_executor.getData())
        data = self.macro_executor.getData()
        mot_init_pos = data[min(data.keys())].data[mot_name]
        mot_final_pos = data[max(data.keys())].data[mot_name]
        pre = mot_init_pos

        for step in range(1, max(data.keys()) + 1):
            self.assertAlmostEqual(abs(pre - data[step].data[mot_name]),
                                   interval, 7,
                                   "Step interval differs for more than expected (using getData)")
            pre = data[step].data[mot_name]

        self.assertAlmostEqual(mot_init_pos, expected_init_pos, 7,
                               "Initial possition differs from set value (using getData)")
        self.assertAlmostEqual(mot_final_pos, expected_final_pos, 7,
                               "Final possition differs from set value (using getData)")

        # Test data from log_output (macro_executor.getLog('output'))
        log_output = self.macro_executor.getLog('output')
        data = parsing_log_output(log_output)
        init_pos = 0
        last_pos = -1
        value = 1
        pre = data[init_pos]
        for step in data[1:]:
            self.assertAlmostEqual(abs(pre[value] - step[value]),
                                   interval, 7,
                                   "Step interval differs for more than expected (using getData)")
            pre = step

        self.assertAlmostEqual(data[init_pos][value], expected_init_pos, 7,
                               "Initial possition differs from set value (using getLog)")
        self.assertAlmostEqual(data[last_pos][value], expected_final_pos, 7,
                               "Final possition differs from set value (using getLog)")


@testRun(macro_params=[_m1, '-1', '1', '2', '.1'])
@testStop(macro_params=[_m1, '1', '-1', '3', '.1'])
class DscanTest(DNscanTest, unittest.TestCase):

    """Test of dscan macro. It verifies that macro dscan can be executed and
    stoped. See :class:`DNscanTest` for requirements.
    """
    macro_name = 'dscan'


@testRun(macro_params=[_m1, '-1', '1', '3', _m2, '-1', '0', '2', '.1'])
@testRun(macro_params=[_m1, '-2', '2', '3', _m2, '-2', '-1', '2', '.1'])
@testStop(macro_params=[_m1, '-3', '0', '3', _m2, '-3', '0', '2', '.1'])
class MeshTest(RunStopMacroTestCase, unittest.TestCase):

    """Test of mesh macro. It verifies that macro mesh can be executed and
    stoped. See :class:`.RunStopMacroTestCase` for requirements.
    """
    macro_name = 'mesh'

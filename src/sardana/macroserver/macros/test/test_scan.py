#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
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

import unittest
from sardana.macroserver.macros.test import (RunStopMacroTestCase, 
                                             testRun, testStop)
from sardana.macroserver.macros.test.sardemoenv import SarDemoEnv

#get handy motor names from sardemo 
_MOTORS = SarDemoEnv().getMotors()
_m1,_m2 = _MOTORS[:2]


def parsingOutput(logOutput):
    """It parses the output of the executed scan macro in order to analyze
       it and test different aspects of it."""
    firstdataline = 1
    scan_index = 0
    data = []
    for line, in logOutput[firstdataline:]:
        # Get a list of elements without white spaces between them
        l = line.split() 
        # Cast all elements of the scan line (l) to float
        l = [float(scan_elem) for scan_elem in l]
        # Cast index of scan to int (the first element of the list)
        l[scan_index]= int(l[scan_index])
        data.append(l)
    return data 


class ANscanTest(RunStopMacroTestCase):
    """Not yet implemented. Once implemented it will test anscan."""
    pass


class DNscanTest(ANscanTest):
    """Not yet implemented. Once implemented it will test the macro dnscanc."""
    pass


class DNscancTest(DNscanTest):
    """Not yet implemented. Once implemented it will test the macro dnscanc."""
    pass


@testRun(macro_params=[_m1, '0', '5', '4', '.1'], wait_timeout=float("inf"))
@testStop(macro_params=[_m1, '0', '5', '3', '.1'])
class AscanTest(ANscanTest, unittest.TestCase):
    """Test of ascan macro. It verifies that macro ascan can be executed and 
    stoped and tests the output of the ascan. It inherits from ANscanTest.
    """
    macro_name = 'ascan'

    def macro_runs(self, macro_params=None, wait_timeout=float("inf")):
        """Verify that the motor initial and final positions of the scan 
           are the ones given as input. Verify that the intervals in terms
           of motor position between one point ant the next one have always
           an error lower than 1% regarding the theoretical interval."""
        
        #call the parent class implementation
        ANscanTest.macro_runs(self, macro_params=macro_params, 
                              wait_timeout=wait_timeout)
        
        initPos = float(macro_params[1])
        finalPos = float(macro_params[2])
        self.steps = int(macro_params[-2])
        logOutput = self.macro_executor.getLog('output')
        self.data = parsingOutput(logOutput)
        interval = abs(finalPos - initPos) / self.steps
        pre = self.data[0]
        for d in self.data[1:]:
            self.assertTrue(abs(abs(pre[2] - d[2]) - interval)
                            < interval * 0.01,
                            "Step interval differs for more than 1% ")
            pre = d

        self.assertAlmostEqual(self.data[0][2], initPos, 7,
                         "Initial possition differs from set value")
        self.assertAlmostEqual(self.data[-1][2], finalPos, 7,
                         "Final possition differs from set value")


@testRun(macro_params=[_m1, '-1', '1', '2', '.1'])
@testStop(macro_params=[_m1, '1', '-1', '3', '.1'])
class DscanTest(DNscanTest, unittest.TestCase):
    """Test of dscan macro. It verifies that macro dscan can be executed and 
    stoped.
    """
    macro_name = 'dscan'


@testRun(macro_params=[_m1, '-1', '1', '3', _m2, '-1', '0', '2', '.1'])
@testRun(macro_params=[_m1, '-2', '2', '3', _m2, '-2', '-1', '2', '.1'])
@testStop(macro_params=[_m1, '-3', '0', '3', _m2, '-3', '0', '2', '.1'])
class MeshTest(RunStopMacroTestCase, unittest.TestCase):
    """Test of mesh macro. It verifies that macro mesh can be executed and 
    stoped.
    """
    macro_name = 'mesh'
    



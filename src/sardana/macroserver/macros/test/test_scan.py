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
    #@TODO: Document!
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
    #@TODO: naming convention for TestCase classes? RunStopMacroTest{Case}?
    #@TODO: Document!
    pass

class DNscanTest(ANscanTest):
    #@TODO: Document!
    pass

class DNscancTest(DNscanTest):
    #@TODO: Document!
    pass


@testRun(macro_params=[_m1, '0', '100', '4', '.1'])
@testStop(macro_params=[_m1, '0', '100', '4', '.1'])
class AscanTest(ANscanTest, unittest.TestCase):
    #@TODO: Document!
    macro_name = 'ascan'

    def macro_runs(self, macro_params=None, wait_timeout=1000):
        #@TODO: Document!
        
        #call the parent class implementation
        ANscanTest.macro_runs(self, macro_params=macro_params, 
                              wait_timeout=wait_timeout)
        
        #check extra assertions
        initPos = float(macro_params[1])
        finalPos = float(macro_params[2])
        self.steps = int(macro_params[-2])

        logOutput = self.macro_executor.getLog('output')
        self.data = parsingOutput(logOutput)
        interval = abs(finalPos - initPos) / self.steps
        pre = self.data[0]
        for d in self.data[1:]:
            # TODO use assertAlmostEqual
            #self.assertAlmostEqual(abs(pre[1] - d[1]), interval,
            #                       "Real interval differs from set interval")
            self.assertTrue(abs(abs(pre[1] - d[1]) - interval)
                            < interval * 0.01,
                            "Step interval differs for more than 1% ")
            pre = d

        self.assertEqual(self.data[0][1], initPos,
                         "Initial possition differs from set value")
        self.assertEqual(self.data[-1][1], finalPos,
                         "Final possition differs from set value")



@testRun(macro_params=[_m1, '-10', '10', '2', '.1'])
@testStop(macro_params=[_m1, '-10', '10', '3', '.1'])
class DscanTest(DNscanTest, unittest.TestCase):
    macro_name = 'dscan'


@testRun(macro_params=[_m1, '-10', '10', '4', _m2, '-10', '0', '3', '.1'])
@testRun(macro_params=[_m1, '-5', '5', '4', _m2, '-8', '0', '2', '.1'])
@testStop(macro_params=[_m1, '-5', '3', '4', _m2, '-8', '0', '2', '.1'])
class MeshTest(RunStopMacroTestCase, unittest.TestCase):
    macro_name = 'mesh'
    



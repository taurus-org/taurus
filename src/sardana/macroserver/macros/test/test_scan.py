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
from sardana.macroserver.macros.test import RunStopMacroTestCase
from sardana.macroserver.macros.test import macroTest
from sardana.macroserver.macros.test import macroTestRun
from sardana.macroserver.macros.test import macroTestStop
from sardana.macroserver.macros.test.sardemoenv import SarDemoEnv

#Mockup tool
def parsingOutput(logOutput):
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

# Mockup
class ScanTest(RunStopMacroTestCase):

    motor_list = SarDemoEnv().getMotors()
    data = []    

    def setUp(self):
        RunStopMacroTestCase.setUp(self)

    def _test_run(self):
        self.steps = int(self.macro_params[-2])
        RunStopMacroTestCase._test_run(self)
        logOutput = self.macro_executor.getLog('output')

        # loginfo - 1 not counting titles
        # steps + 1 is the number of data points
        self.assertEqual(len(logOutput) - 1, self.steps + 1,
                         ("Output data lines (%d) differs " + 
                          "from expected data points (%d)\n Macro input: %s") 
                         % (len(logOutput) - 1, self.steps + 1,
                            ",".join(map(str, self.macro_params))))

        self.data = parsingOutput(logOutput)


    def tearDown(self):
        RunStopMacroTestCase.tearDown(self)


class ANscanTest(RunStopMacroTestCase):

    def setUp(self):
        RunStopMacroTestCase.setUp(self)

    def _test_run(self):
        RunStopMacroTestCase._test_run(self)

    def tearDown(self):
        RunStopMacroTestCase.tearDown(self)


class DNscanTest(ANscanTest):

    def setUp(self):
        ANscanTest.setUp(self)

    def _test_run(self):
        ANscanTest._test_run(self)

    def tearDown(self):
        ANscanTest.tearDown(self)


class DNscancTest(DNscanTest):

    def setUp(self):
        DNscanTest.setUp(self)

    def _test_run(self):
        DNscanTest._test_run(self)

    def tearDown(self):
        DNscanTest.tearDown(self)


@macroTest('run',[SarDemoEnv().getMotors()[0], '0', '100', '4', '.1'])
@macroTest('stop',[SarDemoEnv().getMotors()[0], '0', '100', '4', '.1'])
class AscanTest(ANscanTest, unittest.TestCase):
    macro_name = 'ascan'

    def _test_run(self):
        #super(ScanTest, self).test_Run()
        #ScanTest._test_run(self)

        #ascan
        initPos = float(self.macro_params[1])
        finalPos = float(self.macro_params[2])
        self.steps = int(self.macro_params[-2])

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



@macroTestRun([SarDemoEnv().getMotors()[0], '-10', '10', '2', '.1'])
@macroTestStop([SarDemoEnv().getMotors()[0], '-10', '10', '3', '.1'])
class DscanTest(DNscanTest, unittest.TestCase):
    macro_name = 'dscan'


@macroTestRun([SarDemoParsing().getMotors()[0], '-10', '10', '4', SarDemoParsing().getMotors()[1], '-10', '0', '3', '.1'])
@macroTestRun([SarDemoParsing().getMotors()[0], '-5', '5', '4', SarDemoParsing().getMotors()[1], '-8', '0', '2', '.1'])
@macroTestStop([SarDemoParsing().getMotors()[0], '-5', '3', '4', SarDemoParsing().getMotors()[1], '-8', '0', '2', '.1'])
class MeshTest(RunStopMacroTestCase, unittest.TestCase):
    macro_name = 'mesh'
    



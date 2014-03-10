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
from sardana.tango.macroserver.test import TangoMacroExecutor
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

    @unittest.skip("Test not ready")
    def test01_outputSpec(self):
        #TODO Define ScanDir and ScanFile

        self.macro_executor.run(macro_name = self.macro_name, 
                                macro_params = self.macro_params, 
                                sync = True)

        logInfo = self.macro_executor.getLog('info')

    @unittest.skip("Test not ready")
    def test02_outputNxScan(self):
        #TODO Define ScanDir and ScanFile
        self.macro_executor.run(macro_name = self.macro_name,
                                macro_params = self.macro_params,
                                sync = True)

        logInfo = self.macro_executor.getLog('info')

    def tearDown(self):
        pass  


@macroTestRun([SarDemoEnv().getMotors()[0], '-10', '10', '2', '.1'])
@macroTestStop([SarDemoEnv().getMotors()[0], '-10', '10', '3', '.1'])
class DscanTest(DNscanTest, unittest.TestCase):
    macro_name = 'dscan'
    run_timeout = 3.


@macroTestRun([SarDemoParsing().getMotors()[0], '-10', '10', '4', SarDemoParsing().getMotors()[1], '-10', '0', '3', '.1'])
@macroTestRun([SarDemoParsing().getMotors()[0], '-5', '5', '4', SarDemoParsing().getMotors()[1], '-8', '0', '2', '.1'])
@macroTestStop([SarDemoParsing().getMotors()[0], '-5', '3', '4', SarDemoParsing().getMotors()[1], '-8', '0', '2', '.1'])
class MeshTest(RunStopMacroTestCase, unittest.TestCase):
    macro_name = 'mesh'
    



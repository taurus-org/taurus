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


class ScanTest(RunStopMacroTestCase):

    motor_list = SarDemoEnv().getMotors()
    data = []    

    def setUp(self):
        RunStopMacroTestCase.setUp(self)

        self.motor = self.macro_params[0]
        self.initPos = float(self.macro_params[1])
        self.finalPos = float(self.macro_params[2])
        self.steps = int(self.macro_params[3])
        self.dt = float(self.macro_params[4])

    def test_Run(self):
        RunStopMacroTestCase.test_Run(self)

        logOutput = self.macro_executor.getLog('output')
        #import pdb; pdb.set_trace()
        # loginfo - 1 not counting titles
        # steps + 1 is the number of data points
        self.assertEqual(len(logOutput) - 1, self.steps + 1,
                         ("Output data lines (%d) differs " + 
                          "from expected data points (%d)") 
                         % (len(logOutput) - 1, self.steps + 1))

        self.data = []
        for line in logOutput[1:]:
            l = line[0].split() 
            l = [float(i) for i in l]
            l[0]= int(l[0])
            self.data.append(l)

@macroTest('run',[SarDemoEnv().getMotors()[0], '0', '100', '4', '.1'])
@macroTest('stop',[SarDemoEnv().getMotors()[0], '0', '100', '4', '.1'])
class AscanTest(ScanTest, unittest.TestCase):
    macro_name = 'ascan'

    def _test_run(self):
        #super(ScanTest, self).test_Run()
        #ScanTest._test_run(self)

        #ascan
        initPos = float(self.macro_params[1])
        finalPos = float(self.macro_params[2])

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


class AscanTest(ScanTest, unittest.TestCase):
    macro_name = 'ascan'
    #TODO use generator to get a arbitrary motor from sar_demo
    macro_params = [ScanTest.motor_list[0], '0', '1', '10', '.1']
    run_timeout = 3.

    def test_Run(self):
        ScanTest.test_Run(self)
        self.assertEqual(self.data[0][1], self.initPos,
                         "Initial possition differs from set value")
        self.assertEqual(self.data[-1][1], self.finalPos,
                         "Final possition differs from set value")

@macroTestRun([SarDemoEnv().getMotors()[0], '-10', '10', '2', '.1'])
@macroTestStop([SarDemoEnv().getMotors()[0], '-10', '10', '3', '.1'])
class DscanTest(ScanTest, unittest.TestCase):
    macro_name = 'dscan'

    macro_params = [ScanTest.motor_list[0], '0', '1', '10', '.1']
    run_timeout = 3.

    def test_Run(self):
        ScanTest.test_Run(self)
        #self.assertAlmostEqual(self.data[0][1] - self.data[-1][1],
        #                       self.initPos - self.finalPos,
        #                       "")


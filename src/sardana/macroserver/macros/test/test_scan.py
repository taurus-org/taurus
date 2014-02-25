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
from sardana.macroserver.macros.test import GenericMacroTestCase


class ScanTest(GenericMacroTestCase, unittest.TestCase):

    logOutput = {}
    logInfo = {}

    def setUp(self):
        GenericMacroTestCase.setUp(self)

        self.macro_executor.registerAll()
        self.motor = self.macro_params[0]
        self.initPos = float(self.macro_params[1])
        self.finalPos = float(self.macro_params[2])
        self.steps = int(self.macro_params[3])
        self.dt = float(self.macro_params[4])

    def test00_outputLog(self):
        self.macro_executor.run(macro_name = self.macro_name, 
                                macro_params = self.macro_params, 
                                sync = True)
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

        interval = abs(self.finalPos - self.initPos) / self.steps
        pre = self.data[0]
        for d in self.data[1:]:
            self.assertTrue(abs(abs(pre[1] - d[1]) - interval) 
                            < interval * 0.01, 
                            "Step interval differs for more than 1% ")
            pre = d


    def test01_outputSpec(self):
        #TODO Define ScanDir and ScanFile

        self.macro_executor.run(macro_name = self.macro_name, 
                                macro_params = self.macro_params, 
                                sync = True)

        logInfo = self.macro_executor.getLog('info')


    def tearDown(self):
        #self.macro_executor.unregisterAll()
        pass


class AscanTest(scanTest):
    macro_name = 'ascan'
    #TODO use generator to get a random motor from sar_demo
    macro_params = ['mot17', '0', '1', '10', '.1']
    macro_executor_klass = TangoMacroExecutor
    run_timeout = 3.

    def test00_outputLog(self):
        scanTest.test00_outputLog(self)

        self.assertEqual(self.data[0][1], self.initPos)
        self.assertEqual(self.data[-1][1], self.finalPos)


class DscanTest(scanTest):
    macro_name = 'dscan'
    #TODO use generator to get a random motor from sar_demo
    macro_params = ['mot17', '0', '1', '10', '.1']
    macro_executor_klass = TangoMacroExecutor
    run_timeout = 3.

  
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ascanTest)
    unittest.TextTestRunner(descriptions=True, verbosity=2).run(suite)

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(dscanTest)
    unittest.TextTestRunner(descriptions=True, verbosity=2).run(suite)


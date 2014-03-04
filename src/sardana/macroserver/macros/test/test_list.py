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

"""Tests for list macros"""

import unittest
from sardana.tango.macroserver.test import TangoMacroExecutor
from sardana.macroserver.macros.test import RunMacroTestCase
from sardana.macroserver.macros.test import BaseMacroExecutor
from sardemoparsing import SarDemoParsing

class LsTest(RunMacroTestCase):
    """Base class for testing macros used to list elements.
    """
    def setUp(self):    
        RunMacroTestCase.setUp(self)

    def test_Run(self):
        RunMacroTestCase.test_Run(self)
        self.logOutput = self.macro_executor.getLog("output")
        msg = "generic ls macro does not contain elements"
        self.assertTrue(len(self.logOutput) > 0, msg)


class LsmTest(LsTest, unittest.TestCase):
    """Class used for testing the 'lsm' macro.
       It verifies that all motors created by sar_demo are listed after 
       execution of the macro 'lsm'.
    """
    macro_name = "lsm"
    sar_demo = SarDemoParsing()

    def setUp(self):
        LsTest.setUp(self)
        self.motorlist = self.sar_demo.getMotors() + \
                            self.sar_demo.getPseudoMotors()

    def tearDown(self):
        self.macro_executor.unregisterAll()

    def test_Run(self):      
        LsTest.test_Run(self)
        output_ml = []
        for i in self.logOutput[2:]:
            output_ml.append(i[0].split()[0])
        for i in self.motorlist:
            msg = "lsm does not contain {0}".format(i)
            self.assertTrue(i in output_ml, msg)


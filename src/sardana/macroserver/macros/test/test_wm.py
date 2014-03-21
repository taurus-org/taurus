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

"""Tests for wm macros"""

import time
import unittest
from sardana.macroserver.macros.test import RunMacroTestCase
from sardana.macroserver.macros.test import testRun
from sardemoenv import SarDemoEnv


class WTest(RunMacroTestCase):
    """Base class for testing macros used to read position."""
    
    header_rows = 2
    names_column_index = 0
    values_column_index = 1
    sar_demo = SarDemoEnv()
 
    def setUp(self):    
        RunMacroTestCase.setUp(self)
        
    def macro_runs(self, **kw):
        RunMacroTestCase.macro_runs(self, **kw)
        self.logOutput = self.macro_executor.getLog("output")
        msg = "wm macro did not return any data."
        self.assertTrue(len(self.logOutput) > 0, msg)
                
    def tearDown(self):  
        RunMacroTestCase.tearDown(self)


@testRun(macro_params = [SarDemoEnv().getMotors()[0]], wait_timeout=5.0)
class WmTest(WTest, unittest.TestCase):
    """Class used for testing 'wm' macro.
       It checks that the execution of wm returns data.
    """
    macro_name = "wm"

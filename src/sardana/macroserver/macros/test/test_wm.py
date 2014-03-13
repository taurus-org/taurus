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

import time
import unittest
from sardana.macroserver.macros.test import RunMacroTestCase
from sardana.macroserver.macros.test import testRun
from sardemoenv import SarDemoEnv

class WTest(RunMacroTestCase):
    """Base class for testing macros used to list elements.
    """
    #TODO: copypaste error in docstring
    #TODO: Improve this whole class... not ready for deployment!!!
    header_rows = 2
    names_column_index = 0
    sar_demo = SarDemoEnv()
 
    def setUp(self):    
        RunMacroTestCase.setUp(self)
        
    def macro_runs(self, **kw):
        RunMacroTestCase.macro_runs(self, **kw)
        self.logOutput = self.macro_executor.getLog("output")
        msg = "wm does not contain any position"
        self.assertTrue(len(self.logOutput) > 0, msg)
                
        #parsing output to get all elements
        macro_output = []
        for row, in self.logOutput[self.header_rows:]:
            macro_output.append(row.split()[self.names_column_index])
        #TODO: FINISH THIS IMPLEMENATION!!!

    def tearDown(self):  
        time.sleep(0.15)  #TODO: Why the sleeps????
        RunMacroTestCase.tearDown(self)
        time.sleep(0.15)



# @testRun(macro_params = [SarDemoEnv().getMotors()[0], '3.0'])
# class WmTest(WTest, unittest.TestCase):
#     """Class used for testing the 'lspm' macro.
#        It verifies that all motors created by sar_demo are listed after 
#        execution of the macro 'lspm'.
#     """
#     TODO: copypaste error in docstring
#     macro_name = "wm"



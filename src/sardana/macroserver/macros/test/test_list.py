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
from sardana.tango.macroserver.test import TangoMacroExecutor
from sardana.macroserver.macros.test import RunMacroTestCase
from sardana.macroserver.macros.test import BaseMacroExecutor
from sardana.macroserver.macros.test import macroTestRun
from sardemoparsing import SarDemoParsing

class LsTest(RunMacroTestCase):
    """Base class for testing macros used to list elements.
    """

    header_rows = 2
    names_column_index = 0
    elem_type = None
    sar_demo = SarDemoParsing()
 
    def setUp(self):    
        RunMacroTestCase.setUp(self)
        
    def check_elements(self, sardemolist, outputlist):
        for elem in sardemolist:
            msg = "{0} does not contain {1}".format(self.macro_name, elem)
            self.assertTrue(elem in outputlist, msg)

    def check_atleastNelements(self, outputlist, sardemolist):
        for elem in outputlist:
            msg = "{0} does not contain {1}".format(self.macro_name, elem)
            self.assertTrue(elem in sardemolist, msg)

    def _test_run(self):
        RunMacroTestCase._test_run(self)
        self.logOutput = self.macro_executor.getLog("output")
        msg = "generic ls macro does not contain elements"
        self.assertTrue(len(self.logOutput) > 0, msg)

        if (self.elem_type is not None):
            list_sardemo = self.sar_demo.getElements(self.elem_type)
        else:
            raise Exception("element_type cannot be None") 
                
        #parsing output to get all elements
        macro_output = []
        for row, in self.logOutput[self.header_rows:]:
            macro_output.append(row.split()[self.names_column_index])
        if len(macro_output)>= len(list_sardemo):
            self.check_elements(list_sardemo, macro_output)
        else:
            self.check_atleastNelements(macro_output, list_sardemo)  

    def tearDown(self):  
        time.sleep(0.15)  
        RunMacroTestCase.tearDown(self)
        time.sleep(0.15)

import random 

@macroTestRun(random.choice(SarDemoParsing().getMoveables()))
@macroTestRun('l.*')
@macroTestRun()
class LsmTest(LsTest, unittest.TestCase):
    """Class used for testing the 'lsm' macro.
       It verifies that all motors created by sar_demo are listed after 
       execution of the macro 'lsm'.
    """
    macro_name = "lsm"
    elem_type = "moveable"


@macroTestRun()
class LspmTest(LsTest, unittest.TestCase):
    """Class used for testing the 'lspm' macro.
       It verifies that all motors created by sar_demo are listed after 
       execution of the macro 'lspm'.
    """
    macro_name = "lspm"
    elem_type = "pseudomotor"


@macroTestRun()
class LsctrlTest(LsTest, unittest.TestCase):
    """Class used for testing the 'lsctrl' macro.
       It verifies that all controllers created by sar_demo are listed after 
       execution of the macro 'lsctrl'.
    """
    macro_name = "lsctrl"
    elem_type = "controller"


@macroTestRun()
class LsctTest(LsTest, unittest.TestCase):
    """Class used for testing the 'lsct' macro.
       It verifies that all ct created by sar_demo are listed after 
       execution of the macro 'lsct'.
    """
    macro_name = "lsct"
    elem_type = "ctexpchannel"


@macroTestRun()
class Ls0dTest(LsTest, unittest.TestCase):
    """Class used for testing the 'ls0d' macro.
       It verifies that all 0d created by sar_demo are listed after 
       execution of the macro 'ls0d'.
    """
    macro_name = "ls0d"
    elem_type = "zerodexpchannel"


@macroTestRun()
class Ls1dTest(LsTest, unittest.TestCase):
    """Class used for testing the 'ls1d' macro.
       It verifies that all 1d created by sar_demo are listed after 
       execution of the macro 'ls1d'.
    """
    macro_name = "ls1d"
    elem_type = "onedexpchannel"


@macroTestRun()
class Ls2dTest(LsTest, unittest.TestCase):
    """Class used for testing the 'ls2d' macro.
       It verifies that all 2d created by sar_demo are listed after 
       execution of the macro 'ls2d'.
    """
    macro_name = "ls2d"
    elem_type = "twodexpchannel"




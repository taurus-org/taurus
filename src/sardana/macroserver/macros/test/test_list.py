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

class LsmTest(RunMacroTestCase, unittest.TestCase):
	
    door_name = "door/demo1/1"
    macro_executor_klass = TangoMacroExecutor	
    tango_macro_executor = macro_executor_klass(door_name)
    tango_macro_executor.registerAll()
    macro_name = "lsm"	
    motor = "gap05"

    def testFindMotor(self):
        screen_output = self.tango_macro_executor.getLog("output")
        output = screen_output[0]

        print("\n")
        count_motor = False
        for i in range (len(output)):
            
            print(output[i])       
            if (output[i].find(self.motor) != -1):
                count_motor = True
        
        msg = "lsm does not contain {0}".format(self.motor)
        self.assertTrue(count_motor, msg)         
        print("\n")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(LsmTest)
    unittest.TextTestRunner(descriptions=True, verbosity=2).run(suite)



        


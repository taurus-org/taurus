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
from sardana import sardanacustomsettings

class LsmTest(RunMacroTestCase, unittest.TestCase):

    door_name = getattr(sardanacustomsettings,'UNITTEST_DOOR_NAME')

    #TODO: This will change to use a Factory.
    macro_executor_klass = TangoMacroExecutor
    macro_name = "lsm"

    #tango_macro_executor = macro_executor_klass(door_name)

    def setUp(self):
        RunMacroTestCase.setUp(self)
        self.macro_executor.registerAll()
        self.element = "gap05"

    def testFindElement(self):

        screen_output = self.macro_executor.getLog("output")
        output = screen_output[0]

        print("\n")
        count_element = False
        for i in range (len(output)):

            print(output[i])
            if (output[i].find(self.element) != -1):
                count_element = True

        msg = "lsm does not contain {0}".format(self.element)
        self.assertTrue(count_element, msg)
        print("\n")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(LsmTest)
    unittest.TextTestRunner(descriptions=True, verbosity=2).run(suite)



        


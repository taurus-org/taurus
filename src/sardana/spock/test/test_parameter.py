#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""Documentation module docstring"""

import os
import sys
import unittest
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import parameter



class ReleaseTestCase(unittest.TestCase):
    """ID: SPOCK_PARAMETER

    Title: Spock Parameter tests.

    Description: Unit Test for parameter module (from Spock folder).

    Automation: Yes 
    """


    def setUp(self):
        pass
             
   
    def tearDown(self):
        pass


    def testInstanceCreation(self):
        """Purpose: Instantiate in different ways a SardanaValue object.

        Steps:\n
        1: Test1: Instantiate a SardanaValue without arguments.\n

        Input Data:\n
        1: Test1: None\n

        Expected Results:\n             
        1: Test1: No exception. Object can be instantiated.\n              
        """


        spock_param = parameter.Param()
        self.assertIsInstance(spock_param, parameter.Param, 'Instantiation of an object Param without arguments does not work')
    


    def testInstanceWithArguments(self):
        """
        Purpose: Instantiate in different ways a SardanaValue object.

        Steps:\n
        1: Test1: Instantiate a SardanaValue with a name.\n 
        2: Test2: Instantiate a SardanaValue with a name and a description.\n
        3: Test3: Instantiate a SardanaValue with a name, a description and a type.\n 
        4: Test4: Instantiate a SardanaValue with a name, a description, a type and a default value.\n

        Input Data:\n
        1: Test1: name='sardanaName' \n
        2: Test2: name='sardanaName', desc='description_is_present' \n
        3: Test3: name='sardanaName', desc='description_is_present', type_name='integer' \n
        4: Test4: name='sardanaName', desc='description_is_present', type_name='integer', defvalue=7 \n

        Expected Results:\n             
        1: Test1: No exception. Object can be instantiated.\n
        2: Test2: No exception. Object can be instantiated.\n 
        3: Test3: No exception. Object can be instantiated.\n  
        4: Test4: No exception. Object can be instantiated with parameters name, desc, type_name and defvalue.\n                 
        """

        spock_param = parameter.Param(name='sardanaName')
        self.assertIsInstance(spock_param, parameter.Param, 'Instantiation of an object Param with arguments does not work')

        spock_param = parameter.Param(name='sardanaName', desc='description_is_present')
        self.assertIsInstance(spock_param, parameter.Param, 'Instantiation of an object Param with arguments does not work')

        spock_param = parameter.Param(name='sardanaName', desc='description_is_present', type_name='integer')
        self.assertIsInstance(spock_param, parameter.Param, 'Instantiation of an object Param with arguments does not work')

        spock_param = parameter.Param(name='sardanaName', desc='description_is_present', type_name='integer', defvalue=7)
        self.assertIsInstance(spock_param, parameter.Param, 'Instantiation of an object Param with arguments does not work')




    def testFormatParamValue(self):
	spock_param = parameter.Param(name='sardanaName', desc='description_is_present', type_name='integer', defvalue=7)
        returnedValue = spock_param.formatParamValue(45)
	self.assertEqual(returnedValue, 45, 'returned value should correspond with the one passed as input, and it is not the case')

class ReleaseTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, map(ReleaseTestCase, ("testInstanceCreation", "testInstanceWithArguments", "testFormatParamValue")))


if __name__ == "__main__":
    unittest.main()






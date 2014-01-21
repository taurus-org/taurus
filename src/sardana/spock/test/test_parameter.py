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



class ParameterTestCase(unittest.TestCase):
    """
    Description: Unit Test for parameter module (from Spock folder).

    Steps: 
    1: Instantiate a Param without arguments.

    2: Instantiate a Param with a name.
    3: Instantiate a Param with a name and a description.
    4: Instantiate a Param with a name, a description and a type.
    5: Instantiate a Param with a name, a description, a type and a default value.

    6: Verify that the function testFormatParamValue returns the expected value as output.
    """

    def setUp(self):
        pass
             
   
    def tearDown(self):
        pass


    def testInstanceCreation(self):
        """Purpose: Instantiate a Param object without arguments and verify that it is a correct instance from the class Param.

        Steps: 1

        Input Data:
        None

        Expected Results:            
        No exception. Object can be instantiated.             
        """

        spock_param = parameter.Param()
        self.assertIsInstance(spock_param, parameter.Param, 'Instantiation of an object Param without arguments does not work')
    

    def testInstanceWithArguments(self):
        """
        Purpose: Instantiate in different ways a Param object and verify that they are correct instances from the class Param.

        Steps: 2, 3, 4 and 5

        Input Data:
        1: Assert1: name='sardanaName' 
        2: Assert2: name='sardanaName', desc='description_is_present' 
        3: Assert3: name='sardanaName', desc='description_is_present', type_name='integer' 
        4: Assert4: name='sardanaName', desc='description_is_present', type_name='integer', defvalue=7 

        Expected Results:             
        1: Assert1: No exception. Object can be instantiated with argument name.
        2: Assert2: No exception. Object can be instantiated with arguments name and desc. 
        3: Assert3: No exception. Object can be instantiated with arguments name, desc and type_name.  
        4: Assert4: No exception. Object can be instantiated with arguments name, desc, type_name and defvalue.                
        """

        spock_param = parameter.Param(name='sardanaName')
        self.assertIsInstance(spock_param, parameter.Param, 'Instantiation of an object Param with argument name does not work')

        spock_param = parameter.Param(name='sardanaName', desc='description_is_present')
        self.assertIsInstance(spock_param, parameter.Param, 'Instantiation of an object Param with arguments name and description does not work')

        spock_param = parameter.Param(name='sardanaName', desc='description_is_present', type_name='integer')
        self.assertIsInstance(spock_param, parameter.Param, 'Instantiation of an object Param with arguments name, description and type_name does not work')

        spock_param = parameter.Param(name='sardanaName', desc='description_is_present', type_name='integer', defvalue=7)
        self.assertIsInstance(spock_param, parameter.Param, 'Instantiation of an object Param with arguments name, description, type_name and defvalue does not work')


    def testFormatParamValue(self):
        """Purpose: Instantiate a Param object and verify that the function 'formatParamValue' give us the good output result based on the input.

        Steps: 6

        Input Data:
        45

        Expected Results:            
        45             
        """

        spock_param = parameter.Param(name='sardanaName', desc='description_is_present', type_name='integer', defvalue=7)
        returnedValue = spock_param.formatParamValue(45)
        self.assertEqual(returnedValue, 45, 'returned value should correspond with the one passed as input, and it is not the case')



class ReleaseTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, map(ParameterTestCase, ("testInstanceCreation", "testInstanceWithArguments", "testFormatParamValue")))


if __name__ == "__main__":
    unittest.main()






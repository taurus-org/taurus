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

import unittest

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from sardanavalue import SardanaValue


class ReleaseTestCase(unittest.TestCase):
    """ID: SARDANA_VALUE

    Title: Sardana Value Test.

    Description: Unit Test of sardanavalue module.

    Automation: Yes 
    """


    def setUp(self):
        pass
             
   
    def tearDown(self):
        pass



    def testInstanceCreation(self):
        """
        Purpose: Instantiate in different ways a SardanaValue object.

        Steps:\n
        1: Test1: Instantiate a SardanaValue without arguments.\n
        2: Test2: Instantiate a SardanaValue with a value.\n 
        3: Test3: Instantiate a SardanaValue with exc_info different than None.\n
        4: Test4: Instantiate a SardanaValue.\n 

        Input Data:\n
        1: Test1: None\n
        2: Test2: value=9\n
        3: Test3: value=8\n
        4: Test4: value=7\n

        Expected Results:\n             
        1: Test1: No exception. Object can be instantiated.\n 
        2: Test2: No exception. Object can be instantiated.\n
        3: Test3: No exception. Object can be instantiated.\n 
        4: Test4: No exception. Object can be instantiated.\n                 
        """

        sar_val = SardanaValue()
        self.assertIsInstance(sar_val, SardanaValue, 'Instantiation of an object SardanaValue without arguments does not work')
    
        sar_val1 = SardanaValue(value = 9)
        self.assertIsInstance(sar_val1, SardanaValue, 'Instantiation of an object SardanaValue with the value argument does not work')

        sar_val2 = SardanaValue(value = 8, exc_info = None, timestamp = '09:30', dtype = 'int', dformat = 'int')
        self.assertIsInstance(sar_val2, SardanaValue, 'Instantiation of an object SardanaValue with arguments and exc_info equal None, does not work.')

        sar_val3 = SardanaValue(value = 7, exc_info = 'exception_info', timestamp = '09:30', dtype = 'int', dformat = 'int')
        self.assertIsInstance(sar_val3, SardanaValue, 'Instantiation of an object SardanaValue with arguments and exc_info different of None, does not work.')


    def testSardanaValueExceptionInfo(self):
        """Purpose: Verify that the value given as input to SardanaValue is well set if ExcInfo is None.
        Steps:\n
        1: Instantiate a SardanaValue with two arguments: value=4; exc_info=exception_info.
        2: Read the returned string by the method __repr__() of the SardanaValue Class.
        3: See that the 'Error' is contained in the returned string. 

        Input Data:\n
        - val = 4
        - exc_info = 'exception_info' 
        - boolean = False
        - boolean_is = True

        Expected Results:\n             
        - No exception. 
        - boolean = True.
        - The returned string by the method __repr__() shall contain the string 'Error'.        
        """

        val = 4
        sar_val4 = SardanaValue(value = val, exc_info = 'exception_info')
        returned_string = sar_val4.__repr__()
        
        boolean = False
        if ("Error" or "error" or "ERROR") in returned_string: 
            boolean = True        

        boolean_is = True

        if boolean == False:
            print(returned_string)
        self.assertEqual(boolean_is, boolean, 'exc_info is not None, thus the returned string of __repr__ method should return Error.')



    def testSardanaValueExcInfoNone(self):
        """Purpose: Verify that the value given as input to SardanaValue is well set if ExcInfo is None.
        Steps:\n
        1: Instantiate a SardanaValue with two arguments: value=5; exc_info=None.
        2: Read the returned string by the method __repr__() of the SardanaValue Class.
        3: See that the value 5 is contained in the returned string. 

        Input Data:\n
        - val = 5
        - exc_info = None 
        - boolean = False
        - boolean_is = True

        Expected Results:\n             
        - No exception. 
        - boolean = True.
        - The returned string by the method __repr__() shall contain the value 5.        
        """

        val = 5
        sar_val5 = SardanaValue(value = val, exc_info = None)
        returned_string = sar_val5.__repr__()

        boolean = False
        if ("value="+str(val) or "value = "+str(val)) in returned_string: 
            boolean = True        

        boolean_is = True

        if boolean == False:
            print(returned_string)
        self.assertEqual(boolean_is, boolean, 'exc_info is None, thus the returned string of __repr__ method should return the corresponding value.')



    def testSardanaValueWithoutArgumentExcInfo(self):
        """Purpose: Verify that the value given as input to SardanaValue is well set if ExcInfo is None.
        Steps:\n
        1: Instantiate a SardanaValue with only one argument: value=6.\n
        2: Read the returned string by the method __repr__() of the SardanaValue Class.\n
        3: See that the value 6 is contained in the returned string.\n

        Input Data:\n
        - val = 6 
        - boolean = False
        - boolean_is = True

        Expected Results:\n            
        - No exception. 
        - boolean = True.
        - The returned string by the method __repr__() shall contain the value 6.        
        """

        val = 6
        sar_val6 = SardanaValue(value = val)
        returned_string = sar_val6.__repr__()
        
        boolean = False
        if ("value="+str(6) or "value = "+str(val)) in returned_string: 
            boolean = True        

        boolean_is = True

        if boolean == False:
            print(returned_string)
        self.assertEqual(boolean_is, boolean, 'exc_info is None (instantiation without the ExcInfo argument), thus the returned string of __repr__ method should return the corresponding value.')




class ReleaseTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, map(ReleaseTestCase, ("testInstanceCreation", "testSardanaValueExceptionInfo", "testSardanaValueExcInfoNone", "testSardanaValueWithoutArgumentExcInfo")))



if __name__ == "__main__":
    unittest.main()







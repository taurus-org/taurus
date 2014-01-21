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


class SardanaValueTestCase(unittest.TestCase):
    """Description: Unit Test of sardanavalue module.

    Steps:
        1: Instantiate a SardanaValue without arguments and verify if it is a 
           correct instance of SardanaValue.
        2: Instantiate a SardanaValue with a value and verify if it is a 
           correct instance of SardanaValue.
        3: Instantiate a SardanaValue with exc_info equal None and verify if
           it is a correct instance of SardanaValue.
        4: Instantiate a SardanaValue with exc_info different than None and 
           verify if it is a correct instance of SardanaValue.

        5: Instantiate a SardanaValue with two arguments: value=4; 
           exc_info=exception_info.
        6: Read the returned string by the method __repr__() of the 
           SardanaValue Class.
        7: See that the 'Error' is contained in the returned string. 

        8: Instantiate a SardanaValue with two arguments: value=5; 
           exc_info=None.
        9: Read the returned string by the method __repr__() of the SardanaValue
           Class.
        10: See that the value 5 is contained in the returned string.

        11: Instantiate a SardanaValue with only one argument: value=6.
        12: Read the returned string by the method __repr__() of the 
           SardanaValue Class.
        13: See that the value 6 is contained in the returned string.
    """


    def setUp(self):
        pass
             
   
    def tearDown(self):
        pass



    def testInstanceCreation(self):
        """
        Purpose: Instantiate in different ways a SardanaValue object.

        Steps:
        1, 2, 3 and 4.

        Input Data:
        1: Test1: None
        2: Test2: value=9
        3: Test3: value=8
        4: Test4: value=7

        Expected Results:          
        1: Test1: No exception. Object can be instantiated. 
        2: Test2: No exception. Object can be instantiated.
        3: Test3: No exception. Object can be instantiated. 
        4: Test4: No exception. Object can be instantiated.                 
        """

        sar_val = SardanaValue()
        self.assertIsInstance(sar_val, SardanaValue, 'Instantiation of an ' + 
                          'object SardanaValue without arguments does not work')
    
        sar_val1 = SardanaValue(value = 9)
        self.assertIsInstance(sar_val1, SardanaValue, 'Instantiation of an ' +
                    'object SardanaValue with the value argument does not work')

        sar_val2 = SardanaValue(value = 8, exc_info = None, 
                            timestamp = '09:30', dtype = 'int', dformat = 'int')

        self.assertIsInstance(sar_val2, SardanaValue, 'Instantiation of an ' + 
            'object SardanaValue with arguments and exc_info equal None, ' +
            'does not work.')

        sar_val3 = SardanaValue(value = 7, exc_info = 'exception_info', 
                        timestamp = '09:30', dtype = 'int', dformat = 'int')

        self.assertIsInstance(sar_val3, SardanaValue, 'Instantiation of an ' + 
            'object SardanaValue with arguments and exc_info ' +
            'different of None, does not work.')


    def testSardanaValueExceptionInfo(self):
        """Purpose: Verify that the value given as input to SardanaValue is not 
        set if ExcInfo is not None.

        Steps:
        5, 6 and 7

        Input Data:
        - val = 4
        - exc_info = 'exception_info' 
        - boolean = False
        - boolean_is = True

        Expected Results:             
        - No exception. 
        - boolean = True.
        - The returned string by the method __repr__() shall contain the string 
          'Error'.        
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
        self.assertEqual(boolean_is, boolean, 'exc_info is not None, thus ' +
                'the returned string of __repr__ method should return Error.')



    def testSardanaValueExcInfoNone(self):
        """Purpose: Verify that the value given as input to SardanaValue is well 
        set if ExcInfo is not set.

        Steps:
        8, 9 and 10

        Input Data:
        - val = 5
        - exc_info = None 
        - boolean = False
        - boolean_is = True

        Expected Results:             
        - No exception. 
        - boolean = True.
        - The returned string by the method __repr__() shall contain 
          the value 5.        
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
        self.assertEqual(boolean_is, boolean, 'exc_info is None, thus the ' +
                                 'returned string of __repr__ method should ' + 
                                 'return the corresponding value.')



    def testSardanaValueWithoutArgumentExcInfo(self):
        """Purpose: Verify that the value given as input to SardanaValue is 
        well set if ExcInfo is None.

        Steps:
        11, 12 and 13

        Input Data:
        - val = 6 
        - boolean = False
        - boolean_is = True

        Expected Results:           
        - No exception. 
        - boolean = True.
        - The returned string by the method __repr__() shall contain 
          the value 6.        
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
        self.assertEqual(boolean_is, boolean, 'exc_info is None ' + 
            '(instantiation without the ExcInfo argument), thus the returned' + 
            'string of __repr__ method should return the corresponding value.')



class SardanaValueTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, map(SardanaValueTestCase, 
            ("testInstanceCreation", "testSardanaValueExceptionInfo", 
             "testSardanaValueExcInfoNone", 
             "testSardanaValueWithoutArgumentExcInfo")))



if __name__ == "__main__":
    unittest.main()







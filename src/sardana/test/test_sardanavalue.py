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
    """


    def testInstanceCreation(self):
        """
        Purpose: Instantiate in different ways a SardanaValue object. The 
        consecutive numbers correspond to the different ways of instantiation.

        Steps:
        1, 2, 3 and 4.

        Input Data:
        1: None
        2: value=9
        3: value=8, exc_info = None, timestamp = '09:30', dtype = 'int', 
                  dformat = 'int'
        4: value=7, exc_info = 'exception_info', timestamp = '09:30', 
                  dtype = 'int', dformat = 'int' 
               
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

    def testSardanaValueWithExceptionInfo(self):
        """Purpose: Verify the creation of SardanaValue when exc_info != None.

        Steps:
        5, 6 and 7

        Input Data:
        - exc_info argument is 'exception_info' 

        Expected Results:
        - error attribute is True
        - the SardanaValue representation shall contain '<Error>'        
        """

        val = 4
        
        sar_val = SardanaValue(value = val, exc_info = 'exception_info')
        representation = repr(sar_val)     

        self.assertEqual(sar_val.error, True, 
                'The error attribute is not True.')
                
        self.assertRegexpMatches(representation, ".*<Error>.*", 
                'The SardanaValue representation does not contain <Error>.')

    def testSardanaValueWithNoExceptionInfo(self):
        """Purpose: Verify the creation of SardanaValue when exc_info is None.

        Steps:
        8, 9 and 10

        Input Data:
        - value = 5

        Expected Results:             
        - error attribute is False
        - the SardanaValue representation shall contain its value
        """

        value = 5
        sar_val = SardanaValue(value = value)
        returned_string = sar_val.__repr__()

        self.assertRegexpMatches(returned_string, repr(value), 
                   'The SardanaValue representation does not contain its value')

        self.assertEqual(sar_val.error, False, 
                'The error attribute is not False.')


if __name__ == "__main__":
    unittest.main()







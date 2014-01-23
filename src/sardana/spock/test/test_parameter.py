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
from sardana.spock import parameter


class ParamTestCase(unittest.TestCase):
    """
    Description: Unit Test for Param class (from Spock folder).
    """

    def testInstanceCreation(self):
        """
        Purpose: Instantiate in different ways a Param object and verify that 
        they are correct instances from the class Param. The consecutive 
        numbers correspond to the different ways of instantiation.

        Input Data:
        1: None
        2: name='sardanaName' 
        3: name='sardanaName', desc='description_is_present' 
        4: name='sardanaName', desc='description_is_present', 
                type_name='integer' 
        5: name='sardanaName', desc='description_is_present', 
                type_name='integer', defvalue=7 

        Expected Results:
        1: No exception. Object can be instantiated.              
        2: Object can be instantiated with argument name.
        3: Object can be instantiated with arguments name and desc. 
        4: Object can be instantiated with arguments name, desc and 
                 type_name.  
        5: No exception. Object can be instantiated with arguments 
                 name, desc, type_name and defvalue.                
        """

        spock_param = parameter.Param()
        self.assertIsInstance(spock_param, parameter.Param, 'Instantiation of' +
                            ' an object Param without arguments does not work')

        spock_param = parameter.Param(name='sardanaName')
        self.assertIsInstance(spock_param, parameter.Param, 'Instantiation of' + 
                            ' an object Param with argument name does not work')

        spock_param = parameter.Param(name='sardanaName', 
                                            desc='description_is_present')
        self.assertIsInstance(spock_param, parameter.Param, 'Instantiation of' +
           ' an object Param with arguments name and description does not work')

        spock_param = parameter.Param(name='sardanaName', 
                            desc='description_is_present', type_name='integer')
        self.assertIsInstance(spock_param, parameter.Param, 'Instantiation of' +
                           ' an object Param with arguments name, description' +
                           ' and type_name does not work')

        spock_param = parameter.Param(name='sardanaName', 
                desc='description_is_present', type_name='integer', defvalue=7)
        self.assertIsInstance(spock_param, parameter.Param, 'Instantiation of' +
                   ' an object Param with arguments name, description,' +
                   ' type_name and defvalue does not work')



if __name__ == "__main__":
    unittest.main()

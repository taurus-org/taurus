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

"""Tests for scan macros"""

import unittest
from sardana.tango.macroserver.test import TangoMacroExecutor
from sardana.macroserver.macros.test import GenericMacroTestCase

class AscanTest(GenericMacroTestCase, unittest.TestCase):

    macro_name = 'ascan'
    #TODO use generator to get a random motor from sar_demo
    macro_params = ['mot09', '0', '1', '10', '.1']
    macro_executor_klass = TangoMacroExecutor
    run_timeout = 3.
        
if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(AscanTest)
    unittest.TextTestRunner(descriptions=True, verbosity=2).run(suite)

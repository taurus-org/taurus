#!/usr/bin/env python
#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################


"""Unit tests for Taurus"""

import unittest

class TaurusImportTestCase(unittest.TestCase):
    def setUp(self):
        from moduleexplorer import ModuleExplorer
        self.explore = ModuleExplorer.explore
    
    def testImportSubmodules(self):
        """All submodules should import without problems"""
        moduleinfo, wrn = self.explore('taurus', verbose=False)
        msg = None
        if wrn:
            msg = '\n%s'%'\n'.join(zip(*wrn)[1]) 
        self.assertEqual(len(wrn),0, msg=msg)
        
        
       
if __name__ == "__main__":
    unittest.main()

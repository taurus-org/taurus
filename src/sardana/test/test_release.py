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
import release




class ReleaseTestCase(unittest.TestCase):
"""Documentation class docstring"""

    version_info = (1, 2, 1, 'dev', 0)
    version = '.'.join(map(str, version_info[:3]))
    revision = str(version_info[4])

    def setUp(self):
        pass
                
    def tearDown(self):
        pass

    def testDocFormat(self):
        """Documentation method docstring""" 
        __docformat__ = 'restructuredtext'    
        self.assertEqual(release.__docformat__, __docformat__, '__docformat__ should be equal to restructuredtext.')

    def testName(self):
        """Documentation class docstring"""
        name = 'sardana'
        self.assertEqual(release.name, name, 'name must be sardana.')

    def testVersionInfo(self):
        """Documentation class docstring"""
        self.assertEqual(release.version_info, self.version_info, 'version info is not correct.')
           
    def testVersion(self):
        self.assertEqual(release.version, self.version, 'version is not correct.')
    
    def testRevision(self):
        self.assertEqual(release.revision, self.revision, 'version info is not correct.')

    def testDescription(self):
        description = "Sardana is a generic program for control applications in large and small installations"
        self.assertEqual(release.description, description, 'Code description does not correspond to test description. Change it in the test or in the code.')

    def testLicense(self):
        license = 'LGPL'
        self.assertEqual(release.license, license, 'License has to be equal to LGPL, and this is not the case.')

    def testAuthors(self):
        authors = {'Tiago'          : ('Tiago Coutinho','tiago.coutinho@esrf.fr'),
                   'Pascual-Izarra' : ('Carlos Pascual-Izarra','cpascual@cells.es') }
        self.assertEqual(release.authors, authors, 'Authors does not correspond between the code and the test.')

    def testUrl(self):
        url = 'http://www.tango-controls.org/static/sardana/latest/doc/html/'
        self.assertEqual(release.url, url, 'URL is not the current one. It should be corrected.')


    def testDownloadUrl(self):
        download_url = 'http://sourceforge.net/projects/sardana/'
        self.assertEqual(release.download_url, download_url, 'download_url is not the current one. It should be corrected.')

    def testPlatforms(self):
        platforms = ['Linux','Windows XP/2000/NT','Windows 95/98/ME']

    def testKeywords(self):
        keywords = ['Sardana', 'Tango', 'Python', 'Control System']
        self.assertEqual(release.keywords, keywords, 'Keywords are not the expected ones.')





class ReleaseTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, map(ReleaseTestCase, 
                                                ("testDocFormat", "testName", "testLicense", "testUrl", "testDownloadUrl")))



if __name__ == "__main__":
    unittest.main()


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
from sardana import release


class ReleaseTestCase(unittest.TestCase):
    """
    Description: Unit Test of Sardana 'release.py' module.
    Verification that the release name, version, etc are correct.
    """

    version_info = (1, 2, 1, 'dev', 0)
    version = '.'.join(map(str, version_info[:3]))
    revision = str(version_info[4])


    def setUp(self):
        pass
         
       
    def tearDown(self):
        pass


    def testDocFormat(self):
        """
        Purpose: Test if the __docformat__ is equal to restructured test, 
        othewise the test will Fail.

        Input Data:
        None

        Expected Results:           
        No exception. If the __docformat__ is not 'restructuredtext', 
        the test will Fail.             
        """
        __docformat__ = 'restructuredtext'    
        self.assertEqual(release.__docformat__, __docformat__, 
                        '__docformat__ should be equal to restructuredtext.')


    def testName(self):
        """
        Purpose: Test if the name of the project equals 'sardana'.

        Input Data:
        None

        Expected Results:            
        No exception              
        """
        name = 'sardana'
        self.assertEqual(release.name, name, 'name must be sardana.')


    def testVersionInfo(self):
        """
        Purpose: Test that the version information is the expected one.

        Input Data:
        None

        Expected Results:             
        No exception        
        """
        self.assertEqual(release.version_info, self.version_info, 
                         'version info is not correct.')
       
    
    def testVersion(self):
        """
        Purpose: Test that the version is the expected one.

        Input Data:
        None

        Expected Results:            
        No exception                  
        """
        self.assertEqual(release.version, self.version, 
                         'version is not correct.')
    

    def testRevision(self):
        """
        Purpose: Test if the revision is the expected one.

        Input Data:
        None

        Expected Results:             
        No exception            
        """
        self.assertEqual(release.revision, self.revision, 
                                                'version info is not correct.')


    def testDescription(self):
        """
        Purpose: Test if the test description is the expected one.

        Input Data:
        None

        Expected Results:            
        No exception       
        """
        description = 'Sardana is a generic program for control ' +\
                      'applications in large and small installations'

        self.assertEqual(release.description, description, 
                'Code description does not correspond to test description. ' + 
                'Change it in the test or in the code.')


    def testLicense(self):
        """
        Purpose: Test if the Licence is the expected one.

        Input Data:
        None

        Expected Results:            
        No exception             
        """
        license = 'LGPL'
        self.assertEqual(release.license, license, 
                  'License has to be equal to LGPL, and this is not the case.')


    def testAuthors(self):
        """
        Purpose: Test if the dictionary containing the author names and 
                 code is the expected one.

        Input Data:
        None

        Expected Results:            
        No exception             
        """
        authors = {'Tiago'      : ('Tiago Coutinho','tiago.coutinho@esrf.fr'),
             'Pascual-Izarra' : ('Carlos Pascual-Izarra','cpascual@cells.es') }
        self.assertEqual(release.authors, authors, 
                  'Authors does not correspond between the code and the test.')


    def testUrl(self):
        """
        Purpose: Test if the url of Sardana is the correct one.

        Input Data:
        None

        Expected Results:            
        No exception             
        """
        url = 'http://www.tango-controls.org/static/sardana/latest/doc/html/'
        self.assertEqual(release.url, url, 'URL is not the current one.' +
                                        'It should be corrected.')


    def testDownloadUrl(self):
        """
        Purpose: Test if the Download url is the expected one.

        Input Data:
        None

        Expected Results:            
        No exception       
        """
        download_url = 'http://sourceforge.net/projects/sardana/'
        self.assertEqual(release.download_url, download_url, 
                'download_url is not the current one. It should be corrected.')


    def testPlatforms(self):
        """
        Purpose: Test if the platforms are the expected ones.

        Input Data:
        None

        Expected Results:             
        No exception             
        """
        platforms = ['Linux','Windows XP/2000/NT','Windows 95/98/ME']
        self.assertEqual(release.platforms, platforms, 
                                        'Keywords are not the expected ones.')


    def testKeywords(self):
        """
        Purpose: Test if the Keywords are the expected ones.

        Input Data:
        None

        Expected Results:             
        No exception      
        """
        keywords = ['Sardana', 'Tango', 'Python', 'Control System']
        self.assertEqual(release.keywords, keywords, 
                                        'Keywords are not the expected ones.')





class ReleaseTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, map(ReleaseTestCase, 
                         ("testDocFormat", "testName", "testVersionInfo" ,
                          "testVersion", "testRevision", "testDescription", 
                          "testLicense", "testAuthors", "testUrl", 
                          "testDownloadUrl", "testPlatforms", "testKeywords")))



if __name__ == "__main__":
    unittest.main()


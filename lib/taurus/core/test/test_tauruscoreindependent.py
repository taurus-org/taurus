#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""Test for taurus.core being PyTango Independent"""

__docformat__ = 'restructuredtext'

from taurus.external import unittest
# import functools
# from taurus.test import insertTest
# from modulemanager import ModuleManager
#
# # Decorator
# isTangoAvailable = functools.partial(insertTest, helper_name='isTangoAvailable',
#                             blockPytango=False)
#
#
# *TODO
#@isTangoAvailable(blockPytango=True)
#@isTangoAvailable() # Default False
#@isTangoAvailable(blockPytango=True)


class CoreTangoIndependentTestCase(unittest.TestCase):
    '''Test the Tango-independent core. As part of the SEP3 specification
       Taurus's core must be functional without PyTango.
       This test checks that you can import taurus without PyTango.
    '''

    def _importTaurus(self):
        ''' Helper method'''
        try:
            import taurus
        except ImportError:
            raise ImportError("Cannot import Taurus")

    def test_basicImport(self):
        '''Check if Taurus can be imported without PyTango
        '''
        # skip if PyTango is available
        try:
            import PyTango
            msg = 'Cannot test Tango-independence if PyTango can be imported'
            self.skipTest(msg)
        except ImportError:
            pass
        # check that taurus can be imported
        self.assertRaises(ImportError, self._importTaurus())

#     _modmanager = ModuleManager()
#     def _basicImportWithoutPyTango(self):
#         '''Basic test just try to import taurus (without PyTango)
#         '''
#         # TODO:
#         # _basicImportWithoutPyTango -> test_basicImportWithoutPyTango
#         # We have problems blocking modules so this test failed
#         self._modmanager.blockModule('PyTango')
#         self.assertRaises(ImportError, self._importTaurus())
#
#     def isTangoAvailable(self, blockPytango=False):
#         '''Test to check is Tango module is available for Taurus
#         '''
#         # TODO:
#         # We have problems blocking modules so this test failed because that
#         if blockPytango:
#             self._modmanager.blockModule('PyTango')
#
#         from taurus.core.taurusmanager import TaurusManager
#         plugins = TaurusManager().buildPlugins()
#
#         if blockPytango:
#             print '\t***', plugins
#             msg = 'Taurus is using Tango scheme, but you are blocking PyTango'
#             self.assertFalse('tango' in plugins, msg)
#         else:
#             msg = 'Taurus can not use Tango scheme, maybe you have not' +\
#                   ' installed PyTango'
#             self.assertTrue('tango' in plugins, msg)
#
#
#     def tearDown(self):
#         ''' Restore the original PyTango module'''
#         # *TODO
#         #self._modmanager.reloadModule('PyTango')
#         pass
#

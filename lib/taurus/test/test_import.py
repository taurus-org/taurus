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


"""Taurus import tests"""
from __future__ import absolute_import

import sys
import unittest


class TaurusImportTestCase(unittest.TestCase):

    """
    Test if all the submodules can be imported
    """

    def setUp(self):
        """Preconditions: moduleexplorer utility has to be available """
        from .moduleexplorer import ModuleExplorer
        self.explore = ModuleExplorer.explore

    def testImportSubmodules(self):
        """
        Check that all taurus submodules import without problems

        Expected Results: It is expected to get no warning message
        on module importing
        """
        exclude_patterns = [r'taurus\.qt\.qtgui\.extra_.*',
                            r'taurus\.qt\.qtgui\.qwt5',
                            r'taurus\.external\.qt\.QtUiTools',
                            r'taurus\.external\.qt\.QtWebKit',
                            r'taurus\.external\.qt\.Qwt5',
                            ]

        try:
            import PyTango
        except ImportError:
            exclude_patterns.append(r'taurus\.core\.tango')
        try:
            import epics
        except ImportError:
            exclude_patterns.append(r'taurus\.core\.epics')

        from taurus.external.qt import PYSIDE2
        if PYSIDE2:
            exclude_patterns.append(r'taurus\.external\.qt\.QtDesigner')
            exclude_patterns.append(r'taurus\.qt\.qtdesigner')

        moduleinfo, wrn = self.explore('taurus', verbose=False,
                                       exclude_patterns=exclude_patterns)
        msg = None
        if wrn:
            msg = '\n%s' % '\n'.join(list(zip(*wrn))[1])
        self.assertEqual(len(wrn), 0, msg=msg)


if __name__ == "__main__":
    unittest.main()

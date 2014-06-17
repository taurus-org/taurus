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

"""Tests for wm macros"""

from taurus.external import unittest
from sardana.macroserver.macros.test import (RunMacroTestCase, testRun,
                                             SarDemoEnv)

try:
    _MOTORS = SarDemoEnv().getMotors()
    _m1, _m2 = _MOTORS[:2]
except RuntimeError:
    import taurus
    from sardana import sardanacustomsettings
    door_name = getattr(sardanacustomsettings, 'UNITTEST_DOOR_NAME',
                        'UNDEFINED')
    taurus.warning("The door %s is not running. " % (door_name) +
                   "Ignore this message if you are building the documentation.")
    _m1 = _m2 = 'motor_not_defined'
except Exception, e:
    import taurus
    taurus.debug(e)
    taurus.warning("It was not possible to retrieve the motor names. " +
                 "Ignore this message if you are building the documentation.")
    _m1 = _m2 = 'motor_not_defined'


class WBase(RunMacroTestCase):

    """Base class for testing macros used to read position.
    """

    def macro_runs(self, **kw):
        """Testing the execution of the 'wm' macro and verify that the log
        'output' exists.
        """
        RunMacroTestCase.macro_runs(self, **kw)
        self.logOutput = self.macro_executor.getLog("output")
        msg = "wm macro did not return any data."
        self.assertTrue(len(self.logOutput) > 0, msg)


@testRun(macro_params=[_m1], wait_timeout=5.0)
class WmTest(WBase, unittest.TestCase):

    """Test of wm macro. It verifies that the macro 'wm' can be executed.
    It inherits from WmBase and from unittest.TestCase.
    It tests the execution of the 'wm' macro and verifies that the log 'output'
    exists.
    """
    macro_name = "wm"

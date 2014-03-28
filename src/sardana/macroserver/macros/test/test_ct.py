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

"""Tests for list macros"""

import unittest
from sardana.macroserver.macros.test import RunMacroTestCase
from sardana.macroserver.macros.test import RunStopMacroTestCase
from sardana.macroserver.macros.test import macroTestRun
from sardana.macroserver.macros.test import macroTestStop



@macroTestRun(params='1', wait_timeout=3.0)
@macroTestRun(params='3', wait_timeout=3.5)
@macroTestRun(params='2', wait_timeout=3.0)
class CtTest(RunMacroTestCase, unittest.TestCase):
    """Class for testing ct.
    """

    macro_name = "ct"


@macroTestRun(params='2', wait_timeout=3.0)
@macroTestStop(params='2')
class CtTestAbort(RunStopMacroTestCase, unittest.TestCase):
    """Class for testing ct.
    """

    macro_name = "ct"





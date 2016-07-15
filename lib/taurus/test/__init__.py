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

"""
Taurus provides a framework for testing.
This framework intends to facilitate evaluation, bug finding and integration of
contributed code/patches, as well as to promote test driven development in
Taurus.

The first implementation of this Framework is an outcome of the [Sardana
Enhancement Proposal 5 (SEP5)](http://sourceforge.net/p/sardana/wiki/SEP5/)

Ideally, bug reports should be accompanied by a test revealing the bug,
whenever possible.

The first tests implemented are focused on Unit Tests, but the same framework
should be used for integration and system tests as well.

The taurus.test.testsuite module provides an autodiscovered suite for all
tests implemented in Taurus.

The following are some key points to keep in mind when using this framework:

- The Taurus test framework is based on :mod:`unittest` which should be imported
  from :mod:`taurus.external` in order to be compatible with all versions of
  python supported by Taurus.

- all test-related code is contained in submodules named `test` which appear
  in any module of taurus.

- test-related code falls in one of these three categories:

  - actual test code (classes that derive from unittest.TestCase)

  - utility classes/functions (code to simplify development of test code)

  - resources (accessory files required by some test). They are located in
    subdirectories named `res`

For a more complete description of the conventions on how to write tests with
the Taurus testing framework, please refer to the
[SEP5](http://sourceforge.net/p/sardana/wiki/SEP5/).
"""

from .moduleexplorer import ModuleExplorer
from .resource import getResourcePath
from .base import insertTest
from .fuzzytest import calculateTestFuzziness, loopSubprocess, loopTest

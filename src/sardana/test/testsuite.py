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

"""
This module defines the test suite for the whole Sardana package
Usage::

  from taurus.test import testsuite
  testsuite.run()

"""

__docformat__ = 'restructuredtext'

import os
from taurus.external import unittest
import sardana


def run(disableLogger=True):
    '''Runs all tests for the taurus package'''
    # discover all tests within the sardana/src directory
    loader = unittest.defaultTestLoader
    suite = loader.discover(os.path.dirname(sardana.__file__))
    # use the basic text test runner that outputs to sys.stderr
    runner = unittest.TextTestRunner(descriptions=True, verbosity=2)
    # run the test suite
    runner.run(suite)

if __name__ == '__main__':
    run()

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

"""
This module defines the test suite for the whole Taurus package
Usage::

  from taurus.test import testsuite
  testsuite.run()

"""

__docformat__ = 'restructuredtext'

import os
from taurus.external import unittest
import taurus


def run(disableLogger=True):
    '''Runs all tests for the taurus package'''
    # disable logging messages
    if disableLogger:
        taurus.disableLogOutput()
    # discover all tests within the taurus/lib directory
    loader = unittest.defaultTestLoader
    suite = loader.discover(os.path.dirname(taurus.__file__))
    # use the basic text test runner that outputs to sys.stderr
    runner = unittest.TextTestRunner(descriptions=True, verbosity=2)
    # run the test suite
    runner.run(suite)

if __name__ == '__main__':
    import argparse  # TODO: use taurus.external.argparse (when available)
    parser = argparse.ArgumentParser(description=
                                     'Main test suite for Taurus')
    parser.add_argument('--skip-gui-tests', dest='skip_gui',
                        action='store_true', default=False,
                        help='Do not perform tests requiring GUI')
    args = parser.parse_args()

    if args.skip_gui:
        import taurus.test
        taurus.test.GUI_TESTS_ENABLED = False
    run()

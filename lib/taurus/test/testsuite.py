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
This module defines the test suite for the whole Taurus package
Usage::

  from taurus.test import testsuite
  testsuite.run()

"""

__docformat__ = 'restructuredtext'

import os
import re
from taurus.external import unittest
import taurus


def _filter_suite(suite, exclude_pattern, ret=None):
    """removes TestCases from a suite based on regexp matching on the Test id"""
    if ret is None:
        ret = unittest.TestSuite()
    for e in suite:
        if isinstance(e, unittest.TestCase):
            if re.match(exclude_pattern, e.id()):
                print "Excluded %s" % e.id()
                continue
            ret.addTest(e)
        else:
            _filter_suite(e, exclude_pattern, ret=ret)
    return ret


def get_taurus_suite(exclude_pattern='(?!)'):
    """discover all tests in taurus, except those matching `exclude_pattern`"""
    loader = unittest.defaultTestLoader
    start_dir = os.path.dirname(taurus.__file__)
    suite = loader.discover(start_dir, top_level_dir=os.path.dirname(start_dir))
    return _filter_suite(suite, exclude_pattern)


def run(disableLogger=True, exclude_pattern='(?!)'):
    """Runs tests for the taurus package"""
    # disable logging messages
    if disableLogger:
        taurus.disableLogOutput()
    # discover tests within the taurus/lib directory
    suite = get_taurus_suite(exclude_pattern=exclude_pattern)
    # use the basic text test runner that outputs to sys.stderr
    runner = unittest.TextTestRunner(descriptions=True, verbosity=2)
    # run the test suite
    return runner.run(suite)


def main():
    import sys
    import taurus.test.skip
    from taurus.external import argparse
    from taurus import Release
    parser = argparse.ArgumentParser(description='Main test suite for Taurus')
    parser.add_argument('--skip-gui-tests', dest='skip_gui',
                        action='store_true', default=False,
                        help='Do not perform tests requiring GUI')
    # TODO: Define the default exclude patterns as a tauruscustomsettings
    # variable.
    help = """regexp pattern matching test ids to be excluded.
    (e.g. 'taurus\.core\..*' would exclude taurus.core tests)
    """
    parser.add_argument('-e', '--exclude-pattern',
                        dest='exclude_pattern',
                        default='(?!)',
                        help=help)
    parser.add_argument('--version', action='store_true', default=False,
                        help="show program's version number and exit")
    args = parser.parse_args()

    if args.version:
        print Release.version
        sys.exit(0)

    if args.skip_gui:
        import taurus.test.skip
        taurus.test.skip.GUI_TESTS_ENABLED = False
    if not taurus.test.skip.GUI_TESTS_ENABLED:
        exclude_pattern = '(taurus\.qt\..*)|(%s)' % args.exclude_pattern
    else:
        exclude_pattern = args.exclude_pattern

    ret = run(exclude_pattern=exclude_pattern)

    # calculate exit code (0 if OK and 1 otherwise)
    if ret.wasSuccessful():
        exit_code = 0
    else:
        exit_code = 1
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
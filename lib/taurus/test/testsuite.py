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
from __future__ import print_function

import os
import sys
import re
import unittest
import click
import taurus
from taurus.external.qt import PYQT4

__docformat__ = 'restructuredtext'

PY3_EXCLUDED = (
    'unittest.loader._FailedTest.taurus.qt.qtgui.qwt5',
    'unittest.loader._FailedTest.taurus.qt.qtgui.extra_sardana',
    'unittest.loader._FailedTest.taurus.qt.qtgui.extra_pool',
    'unittest.loader._FailedTest.taurus.qt.qtgui.extra_macroexecutor'
)

ONLY_PYQT4 = (
    'unittest.loader._FailedTest.taurus.qt.qtgui.qwt5',
)

def _filter_suite(suite, exclude_pattern, ret=None):
    """removes TestCases from a suite based on regexp matching on the Test id"""
    if ret is None:
        ret = unittest.TestSuite()
    for e in suite:
        if isinstance(e, unittest.TestCase):

            if e.__module__ == 'unittest.case':
                continue

            if sys.version_info.major > 2 and e.id() in PY3_EXCLUDED:
                print("Excluded %s" % e.id())
                continue

            if not PYQT4 and e.id() in ONLY_PYQT4:
                print("Excluded %s" % e.id())
                continue
            
            if re.match(exclude_pattern, e.id()):
                print("Excluded %s" % e.id())
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


@click.command('testsuite')
@click.option(
    '--gui-tests/--skip-gui-tests', 'gui_tests',
    default=True, show_default=True,
    help='Perform tests requiring GUI'
)
@click.option(
    '-e', '--exclude-pattern', 'exclude_pattern',
    default='(?!)',
    help=r"""regexp pattern matching test ids to be excluded.
    (e.g. 'taurus\.core\..*' would exclude taurus.core tests)
    """
)
def testsuite_cmd(gui_tests, exclude_pattern):
    """Launch the main test suite for Taurus'"""
    import taurus.test.skip

    taurus.test.skip.GUI_TESTS_ENABLED = gui_tests
    if not taurus.test.skip.GUI_TESTS_ENABLED:
        exclude_pattern = r'(taurus\.qt\..*)|(%s)' % exclude_pattern
    else:
        exclude_pattern = exclude_pattern

    ret = run(exclude_pattern=exclude_pattern)

    # calculate exit code (0 if OK and 1 otherwise)
    if ret.wasSuccessful():
        exit_code = 0
    else:
        exit_code = 1
    sys.exit(exit_code)


if __name__ == '__main__':
    testsuite_cmd()

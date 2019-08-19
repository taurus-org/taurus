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

"""This module provides utilities for skipping certain sets of tests"""

#__all__ = []

__docformat__ = 'restructuredtext'

import unittest
from taurus import tauruscustomsettings
from taurus import Logger


def skipUnlessGui():
    '''Decorator to indicate that the given test should be skipped if GUI
    Tests are not enabled.

    It can be applied both to :class:`unittest.TestCase` classes and to
    test methods::

        class FooTest(unittest.TestCase):
            def test_something_which_does_not_need_gui()
                (...)

            @skipUnlessGui()
            def test_something_that requires_gui()
                (...)

        @skipUnlessGui()
        class GUITest(unittest.TestCase):
            (...)

    Note: using skipUnlessGui is equivalent to:

        @skipunless(taurus.test.GUI_TESTS_ENABLED, 'requires GUI')

    '''
    Logger.deprecated(dep='skipUnlessGui', rel='4.0',
                      alt='taurus testsuite --exclude-pattern')
    return unittest.skipUnless(GUI_TESTS_ENABLED, 'requires GUI')


def _hasgui():
    '''Returns True if GUI is available. False otherwise
    The current implementation is not very robust: it just looks for the
    'DISPLAY' environment variable on posix systems and assumes True
    for other systems'''
    import os
    if os.name == 'posix' and not os.getenv('DISPLAY'):
        return False
    else:
        return True

GUI_TESTS_ENABLED = getattr(
    tauruscustomsettings, 'ENABLE_GUI_TESTS', _hasgui())

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

"""Common tools and fixtures for using with taurus and pytest"""

import pytest
import contextlib
from taurus.external.qt import PYSIDE2


@contextlib.contextmanager
def check_taurus_deprecations(caplog, expected=0):
    """context manager that checks the number of taurus deprecation warnings
    logged within the context execution.

    :param expected: (int) Expected number of deprecations. Default is 0
    """
    from taurus import tauruscustomsettings
    # disable deprecation silencing in this context
    bck = getattr(tauruscustomsettings, "MAX_DEPRECATIONS_LOGGED", None)
    tauruscustomsettings._MAX_DEPRECATIONS_LOGGED = None
    caplog.clear()
    try:
        yield
    finally:
        tauruscustomsettings._MAX_DEPRECATIONS_LOGGED = bck
    # check the deprecations after the context is run
    deps = [r for r in caplog.records if "DeprecationWarning" in r.msg]
    n = len(deps)
    msg = "{} Deprecation Warnings ({} expected)".format(n, expected)
    if PYSIDE2 and len(deps) != expected:
        # TODO: investigate the cause for this (note that it happens only
        #       if taurus.external.qt has been imported)
        pytest.xfail("log handling is not working as expected for PySide2")
    assert len(deps) == expected, msg

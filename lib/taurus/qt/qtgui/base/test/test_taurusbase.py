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

"""Unit tests for taurusbase"""


import pytest
from taurus.qt.qtgui.container import TaurusWidget

from taurus.test.pytest import check_taurus_deprecations

try:
    # The following are Tango-centric imports.
    from taurus.core.tango.test import taurus_test_ds  # pytest fixture

    _TANGO_MISSING = False
except:
    _TANGO_MISSING = True


@pytest.mark.skipif(_TANGO_MISSING, reason="tango-dependent test")
@pytest.mark.parametrize(
    "model, expected",
    [
        ("/boolean_scalar", "True"),
        ("/short_scalar", "123 mm"),
        ("/double_scalar", "1.23 mm"),
        ("/state", "ON"),
        ("/float_scalar#", "-----"),
        ("/float_scalar#label", "float_scalar"),
        ("/double_scalar#rvalue.magnitude", "1.23"),
        #("/float_scalar?configuration=label", "float_scalar"),
        ("eval:1+2", "3"),
        ("eval:1+2#label", "1+2"),
        ("eval:1+2#", "-----"),
    ],
)
def test_display_value(
    qtbot,
    caplog,
    taurus_test_ds,
    model,
    expected
):
    """Check the getDisplayValue method"""
    with check_taurus_deprecations(caplog):
        w = TaurusWidget()
        qtbot.addWidget(w)
        if model.startswith("/"):
            model = "tango:{}{}".format(taurus_test_ds, model)
        with qtbot.waitSignal(w.modelChanged, timeout=3200):
            w.setModel(model)

        def _ok():
            """Check text"""
            assert w.getDisplayValue() == expected

        qtbot.waitUntil(_ok, timeout=3200)

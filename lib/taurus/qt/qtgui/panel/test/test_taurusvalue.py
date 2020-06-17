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

"""Test for taurus.qt.qtgui.panel.taurusvalue"""

import pytest
from taurus.qt.qtgui.panel import TaurusValue
from taurus.test.pytest import check_taurus_deprecations

try:
    # The following are Tango-centric imports.
    from taurus.core.tango.test import taurus_test_ds  # pytest fixture

    _TANGO_MISSING = False
except:
    _TANGO_MISSING = True


@pytest.mark.skipif(_TANGO_MISSING, reason="tango-dependent test")
def test_bug126(qtbot, caplog):
    """Verify that case is not lost when customizing a label (bug#126)"""
    with check_taurus_deprecations(caplog, expected=0):
        w = TaurusValue()
        qtbot.addWidget(w)
        w.setModel("tango:sys/tg_test/1/double_scalar")
        label = "MIXEDcase"
        w.setLabelConfig(label)

        def _ok():
            assert w.labelWidget().text() == label

        qtbot.waitUntil(_ok, timeout=3200)


@pytest.mark.skipif(_TANGO_MISSING, reason="tango-dependent test")
def test_label_case_sensitivity(qtbot, caplog, taurus_test_ds):
    """Verify that case is respected of in the label widget"""
    with check_taurus_deprecations(caplog, expected=0):
        w = TaurusValue()
        qtbot.addWidget(w)
        w.setModel("tango:{}/MIXEDcase".format(taurus_test_ds))

        def _ok():
                assert w.labelWidget().text() == "MIXEDcase"

        qtbot.waitUntil(_ok, timeout=3200)


def test_taurusvalue_subwidget_texts(qtbot, caplog):
    """Checks the texts for scalar attributes"""

    model = "eval:@a=taurus.core.evaluation.test.res.mymod.MyClass()/a.foo"
    expected = ("a.foo", "123", "123", "m")
    depr = 0

    with check_taurus_deprecations(caplog, expected=depr):
        w = TaurusValue()
        qtbot.addWidget(w)
        w.setModel(model)

        def _ok():
            got = (
                str(w.labelWidget().text()),
                str(w.readWidget().text()),
                str(w.writeWidget().displayText()),
                str(w.unitsWidget().text()),
            )
            assert got == expected

        qtbot.waitUntil(_ok, timeout=3200)


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

"""Unit tests for Taurus Label"""


from taurus.qt.qtgui.display import TaurusLabel
from taurus.core.util.colors import ATTRIBUTE_QUALITY_DATA, DEVICE_STATE_DATA
from taurus.external.qt import Qt
from pint import UnitRegistry as ur
import numpy

from taurus.test.pytest import check_taurus_deprecations

import pytest

try:
    # The following are Tango-centric imports.
    from taurus.core.tango.test import taurus_test_ds  # pytest fixture

    _TANGO_MISSING = False
except:
    _TANGO_MISSING = True


def _chek_tauruslabel(
    qtbot,
    caplog,
    taurus_test_ds,
    model,
    fmt=None,
    fgRole=None,
    bgRole=None,
    modelIndex=None,
    depr=0,
    expected_fg=None,
    expected_bg=None,
):
    """Check the label foreground and background"""
    # TODO: these tests are not properly isolated. For example, the
    #       parameterization testing fgrole="quality" fails in PySide2
    #       if it is called after another parameterization.
    if expected_fg is None and expected_bg is None:
        raise ValueError("expected_fg or expected_bg must not be None")
    with check_taurus_deprecations(caplog, expected=depr):
        w = TaurusLabel()
        qtbot.addWidget(w)
        if model.startswith("/"):
            model = "tango:{}{}".format(taurus_test_ds, model)
        with qtbot.waitSignal(w.modelChanged, timeout=3200):
            w.setModel(model)
        if fmt is not None:
            w.setFormat(fmt)
        if modelIndex is not None:
            w.setModelIndex(modelIndex)
        if fgRole is not None:
            w.setFgRole(fgRole)
        if bgRole is not None:
            w.setBgRole(bgRole)

        def _ok():
            """Check text"""
            if expected_fg is not None:
                assert w.text() == expected_fg
            if expected_bg is not None:
                p = w.palette()
                assert p.color(p.Background).getRgb()[:3] == expected_bg

        qtbot.waitUntil(_ok, timeout=3200)


@pytest.mark.skipif(_TANGO_MISSING, reason="tango-dependent test")
@pytest.mark.parametrize(
    "model, fgRole, modelIndex, depr, fg",
    [
        # pre-tep14 compat FgRole checks: value, w_value, state, quality, none
        ("/double_scalar", "quality", None, 0, "ATTR_VALID"),
        ("/double_scalar", "value", None, 0, "1.23 mm"),
        ("/double_scalar", "w_value", None, 0, "0.00 mm"),
        ("/double_scalar", "state", None, 0, "Ready"),
        ("/double_scalar", "none", None, 0, ""),
        # fragment and modelIndex checks
        ("/double_scalar#label", None, None, 0, "double_scalar"),
        ("/double_scalar", "label", None, 0, "double_scalar"),
        ("/double_scalar#rvalue", "label", None, 0, "double_scalar"),
        ("/double_scalar#state", None, None, 0, "Ready"),
        ("/double_spectrum", None, 1, 0, "1.23 mm"),
        ("/double_spectrum#rvalue[1]", None, None, 0, "1.23 mm"),
        ("/double_image", None, (1, 1), 0, "1.23 mm"),
        (
            "/double_image#rvalue[1,::2]",
            None,
            None,
            0,
            # expected is not explicit to support pint v<0.8 particularities
            "{:~}".format(numpy.array([1.23, 1.23]) * ur().mm),
        ),
    ],
)
def test_tauruslabel_text(
    qtbot, caplog, taurus_test_ds, model, fgRole, modelIndex, depr, fg
):
    """Check the label text"""
    _chek_tauruslabel(
        qtbot,
        caplog,
        taurus_test_ds,
        model,
        fgRole=fgRole,
        modelIndex=modelIndex,
        depr=depr,
        expected_fg=fg,
    )


TRANSPARENT_BG = Qt.QColor(Qt.Qt.transparent).getRgb()[:3]
TAURUS_READY_BG = DEVICE_STATE_DATA["TaurusDevState.Ready"][1:4]
TG_ATTR_VALID_BG = ATTRIBUTE_QUALITY_DATA["ATTR_VALID"][1:4]


@pytest.mark.skipif(_TANGO_MISSING, reason="tango-dependent test")
@pytest.mark.parametrize(
    "model, bgRole, bg",
    [
        # pre-tep14 compat BgRole checks: state, quality, none
        ("/float_scalar_ro", "none", TRANSPARENT_BG),
        ("/float_scalar_ro", "state", TAURUS_READY_BG),
        ("/float_scalar_ro", "quality", TG_ATTR_VALID_BG),
        ("/float_scalar_ro", None, TG_ATTR_VALID_BG),
    ],
)
def test_tauruslabel_bg(qtbot, caplog, taurus_test_ds, model, bgRole, bg):
    """"Check the label background"""
    _chek_tauruslabel(
        qtbot, caplog, taurus_test_ds, model, bgRole=bgRole, expected_bg=bg
    )


def _oneDecimalFormater(dtype, **kwargs):
    return "{:~.1f}"


def _typeFormatter(dtype, **kwargs):
    return dtype.__name__


@pytest.mark.parametrize(
    "model, fmt, fg",
    [
        ("eval:1.2345", "{:.3f}", "1.234 dimensionless"),
        ("eval:1.2345", "{:~.3f}", "1.234"),
        ("eval:1.2345", "{:~.3f}", "1.234"),
        ("eval:1.2345", ">>{}<<", ">>1.2345<<"),
        ('eval:"hello"', None, "hello"),
        ('eval:"hello"', _oneDecimalFormater, "hello"),
        ('eval:"hello"', _typeFormatter, "str"),
        ("eval:1.2345", _oneDecimalFormater, "1.2"),
        ('eval:Q("5m")#rvalue.units', _typeFormatter, "Unit"),
        ("eval:Q(5)#rvalue.magnitude", _typeFormatter, "int"),
    ],
)
def test_instance_format(qtbot, caplog, taurus_test_ds, model, fmt, fg):
    """Check formatter API at instance level"""
    _chek_tauruslabel(
        qtbot, caplog, taurus_test_ds, model, fmt=fmt, expected_fg=fg
    )


@pytest.mark.parametrize(
    "model, fmt, fg",
    [
        ("eval:1.2345", "{:.3f}", "1.234 dimensionless"),
        ("eval:1.2345", "{:~.3f}", "1.234"),
        ("eval:1.2345", "{:~.3f}", "1.234"),
        ("eval:1.2345", ">>{}<<", ">>1.2345<<"),
        ('eval:"hello"', None, "hello"),
        ('eval:"hello"', _oneDecimalFormater, "hello"),
        ('eval:"hello"', _typeFormatter, "str"),
        ("eval:1.2345", _oneDecimalFormater, "1.2"),
        ('eval:Q("5m")#rvalue.units', _typeFormatter, "Unit"),
        ("eval:Q(5)#rvalue.magnitude", _typeFormatter, "int"),
    ],
)
def test_class_format(monkeypatch, qtbot, caplog, model, fmt, fg):
    """Check formatter API at class level"""
    monkeypatch.setattr(TaurusLabel, "FORMAT", fmt)

    with check_taurus_deprecations(caplog, expected=0):
        w = TaurusLabel()
        qtbot.addWidget(w)

        w.setModel(model)
        w.resetFormat()  # needed to avoid fuzzyness in the tests

        def _ok():
            """Check text"""
            assert w.text() == fg

        qtbot.waitUntil(_ok, timeout=3200)
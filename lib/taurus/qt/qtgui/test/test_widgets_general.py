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
Generic tests (instantiation, set models, etc) for several widgets
"""

import pytest
from importlib import import_module
import taurus
from taurus.test.pytest import check_taurus_deprecations


DB = 'sys/database/2'
TGT = 'tango:sys/tg_test/1'
TGT_FL_SC = TGT + '/float_scalar'
TGT_FL_SP = TGT + '/float_spectrum'
TGT_SH_SC = TGT + '/short_scalar'
TGT_UC_IM = TGT + '/uchar_image_ro'
TGT_ST_SP = TGT + '/string_spectrum'
TGT_WAVE = TGT + '/wave'
TGT_NOVAL = TGT + '/no_value'
TGT_EXC = TGT + '/throw_exception'
EV_INT = 'eval:123'
EV_Q = 'eval:1.23*UR.mV'
EV_RND5 = 'eval:rand(5)'

# TODO: create and keep model objects in setup_module to speed up


def _import_obj(obj_str, package="taurus.qt.qtgui"):
    """
    returns objects described by a string like "<modname>[:<objname>]"
    """
    if ":" in obj_str:
        modname, oname = obj_str.split(":")
        return getattr(import_module(modname, package=package), oname)
    else:
        return import_module(obj_str, package=package)


@pytest.mark.parametrize(
    "widgetname,depr,models",
    [
        (".display:TaurusLabel", 0, [TGT_WAVE, "", EV_INT, None]),
        (".button:TaurusCommandButton", 0, [TGT, "", DB, None]),
        (".panel:TaurusAttrForm", 0, [TGT, "", DB, None]),
        (".panel:TaurusForm", 0, [
                  [TGT],
                  [TGT_WAVE],
                  [],
                  "",
                  [EV_INT],
                  None,
                  [TGT_SH_SC, TGT_UC_IM, TGT_ST_SP, TGT_NOVAL, TGT_EXC],
                  [""],
                  ",".join((TGT, EV_INT)),
                  " ".join((TGT_UC_IM, EV_RND5)),
                  [None]
        ]),
    ]
)
def test_set_models(qtbot, caplog, widgetname, depr, models):
    """
    Generic test that checks that a widget can be instantiated and given
    its setModel called sequentially.

    It can be parameterized or run with functools.partial
    """
    with check_taurus_deprecations(caplog, expected=depr):
        klass = _import_obj(widgetname)
        w = klass()
        qtbot.addWidget(w)

        for model in models:
            if not model:
                model_obj = None
            else:
                try:
                    model_obj = taurus.Object(model)
                except:  # allow non-string models (e.g. lists of models)
                    model_obj = None
            w.setModel(model)
            assert w.getModelObj() == model_obj

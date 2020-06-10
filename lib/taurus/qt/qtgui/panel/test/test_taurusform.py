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

"""Unit tests for Taurus Forms"""

import unittest
from taurus.qt.qtgui.test import GenericWidgetTestCase
from taurus.qt.qtgui.panel import TaurusForm, TaurusAttrForm, TaurusValue
from taurus.core.util.test.test_plugin import mock_entry_point


class _DummyTV(TaurusValue):
    pass


def _DummyItemFactory(m):
    """
    A dummy item factory that returns _DummyTV instance for one specific
    attribute: "eval://localhost/@dummy/'test_itemfactory'"
    """
    if m.fullname == "eval://localhost/@dummy/'test_itemfactory'":
        return _DummyTV()


def _BadFactory(m):
    """
    A dummy item factory that fails when called with the attribute
    "eval://localhost/@dummy/'test_badfactory'" and returns _DummyTV otherwise.
    """
    if m.fullname == "eval://localhost/@dummy/'test_badfactory'":
        return _DummyTV()
    raise RuntimeError("_BadFactory is doomed to fail")


class _BadEntryPoint(object):
    """A dummy entry point -like class that fails when loaded (for testing)"""
    name = '_BadEntryPoint'
    def load(self):
        raise RuntimeError("_BadEntryPoint is doomed to fail")


def test_form_itemFactory(qtbot):
    """Checks that the TaurusForm itemFactory API works"""
    lines = ["test_Form_ItemFactory={}:_DummyItemFactory".format(__name__)]
    group = "taurus.form.item_factories"
    mock_entry_point(lines, group=group)

    w = TaurusForm()
    qtbot.addWidget(w)

    w.setModel(
        [
            "eval://localhost/@dummy/'test_itemfactory'",
            "eval://localhost/@dummy/'test_itemfactory2'",
        ]
    )
    qtbot.wait_until(lambda: len(w) == 2, timeout=3200)
    # The first item should get a customized _DummyTV widget
    assert type(w[0]) is _DummyTV
    # The second item shoud get the default form widget
    assert type(w[1]) is w._defaultFormWidget


def test_form_itemFactory_selection(qtbot):
    """Checks that the TaurusForm itemFactory selection API works"""
    lines = ["test_Form_ItemFactorySel={}:_DummyItemFactory".format(__name__)]
    group = "taurus.form.item_factories"
    mapping = mock_entry_point(lines, group=group)
    ep1 = mapping[group]["test_Form_ItemFactorySel"]

    w = TaurusForm()
    qtbot.addWidget(w)

    # the test_Form_ItemFactory should be in the default factories
    default_factories = w.getItemFactories()
    assert ep1 in default_factories

    # no factories should be excluded by default
    inc, exc = w.getItemFactories(return_disabled=True)
    assert exc == []

    # Check that we can deselect all factories
    no_factories = w.setItemFactories(include=[])
    assert no_factories == []

    # Check that we can exclude everything except test_Form_ItemFactory
    select1 = w.setItemFactories(
        exclude=[r"(?!.*test_Form_ItemFactorySel).*"]
    )
    assert select1 == [ep1]

    # Check that we can include only test_Form_ItemFactory
    select2 = w.setItemFactories(include=["test_Form_ItemFactorySel"])
    assert select2 == [ep1]

    # Check that the selected test_Form_ItemFactory is an entry point
    from pkg_resources import EntryPoint
    assert type(select2[0]) == EntryPoint

    # Check that the selected entry point loads _DummyItemFactory
    assert select2[0].load() is _DummyItemFactory

    # Check that we can include a factory instance
    select3 = w.setItemFactories(include=[_DummyItemFactory])

    # Check that the selected test_Form_ItemFactory is an entry point-alike
    from taurus.core.util.plugin import EntryPointAlike
    assert type(select3[0]) == EntryPointAlike

    # Check that the selected entry point loads _DummyItemFactory
    assert select3[0].load() is _DummyItemFactory

    # Check that the selected entry point has the given name
    assert select3[0].name == repr(_DummyItemFactory)


def test_form_cwidget_bck_compat(qtbot):
    """check that the cusomWidgetMap bck-compat works"""

    w = TaurusForm()
    qtbot.addWidget(w)

    # check that custom widget map is empty by default
    assert w.getCustomWidgetMap() == {}

    w.setItemFactories(include=())

    try:
        # check that an explicit call to setCustomWidgetMap works
        dummy = ("taurus.qt.qtgui.panel.test.test_taurusform._DummyTV", (), {})
        w.setCustomWidgetMap({"DataBase": dummy})
        w.setModel(["tango:sys/database/2", "tango:sys/tg_test/1"])
        qtbot.wait_until(lambda: len(w) == 2, timeout=3200)
        assert type(w[0]) == _DummyTV
        assert type(w[1]) == TaurusValue
        assert w.getCustomWidgetMap() == {"DataBase": dummy}

        # check that the custom widget map can be restored
        w.setCustomWidgetMap({})
        w.setModel(["tango:sys/database/2", "tango:sys/tg_test/1"])
        qtbot.wait_until(lambda: len(w) == 2, timeout=3200)
        assert type(w[0]) == TaurusValue
        assert type(w[1]) == TaurusValue
        assert w.getCustomWidgetMap() == {}
    finally:
        # set model to None as an attempt to avoid problems in atexit()
        w.setModel(None)
        qtbot.wait_until(lambda: len(w) == 0, timeout=3200)


def test_form_itemFactory_loading(qtbot):
    """
    check that the factory loading is robust against unloadable plugins
    and badly-implemented item factories
    """

    w = TaurusForm()
    qtbot.addWidget(w)

    w.setItemFactories(
        include=(_BadEntryPoint, _BadFactory, _DummyItemFactory)
    )
    w.setModel(
        ["eval://localhost/@dummy/'test_itemfactory'",
         "eval://localhost/@dummy/'test_badfactory'",
         "eval:1",
         ]
    )
    qtbot.wait_until(lambda: len(w) == 3, timeout=3200)

    # handled by _DummyItemFactory
    assert type(w[0]) == _DummyTV
    # handled in _BadFactory (even if with wrong return value)
    assert type(w[1]) == _DummyTV
    # errored in _BadFactory, ignored by _DummyItemFactory
    assert type(w[2]) == TaurusValue




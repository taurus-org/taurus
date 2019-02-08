# -*- coding: utf-8 -*-

##############################################################################
##
## This file is part of Taurus
##
## http://taurus-scada.org
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
##############################################################################

import sys

import taurus
import unittest


def _import(name):
    __import__(name)
    return sys.modules[name]


class QtTestCase(unittest.TestCase):

    _api_name = None

    def setUp(self):
        taurus.setLogLevel(taurus.Critical)

        self.opt_mods = ("QtDesigner", "QtNetwork", "Qt", "QtSvg",
                         "QtUiTools", "QtWebKit", "Qwt5", "uic")

        # store a "snapshot" of the currently loaded modules
        self._orig_mods = set(sys.modules.keys())

        # this import initializes Qt in case it is not loaded
        from taurus.external.qt import Qt, API_NAME

        self._api_name = API_NAME
        self.__qt = Qt

    def test_qt_base_import(self):
        mods = set(sys.modules.keys())

        other_apis = set(('PyQt5', 'PySide2', 'PyQt4', 'PySide'))
        other_apis.remove(self._api_name)

        # the selected API and the QtCore should be loaded
        self.assertTrue(self._api_name in mods, self._api_name + " not loaded")
        self.assertTrue(self._api_name + ".QtCore" in mods,
                        "QtCore not loaded")

        # the other APIs should *not* be loaded
        for other_api in other_apis:
            self.assertFalse(
                other_api in mods,
                other_api + " loaded in " + self._api_name + " test")

        # the other Qt submodules should *not* be loaded
        for opt_mod in self.opt_mods:
            mod = "{0}.{1}".format(self._api_name, opt_mod)
            self.assertFalse(mod in mods - self._orig_mods, mod + " is loaded")

    def __test_qt_module(self, qt_mod_name):
        """Checks that the given shim is complete"""
        taurus_qt_mod_name = "taurus.external.qt.{0}".format(qt_mod_name)
        orig_qt_mod_name = "{0}.{1}".format(self._api_name, qt_mod_name)
        TaurusQtMod = _import(taurus_qt_mod_name)
        OrigQtMod = _import(orig_qt_mod_name)
        taurus_qt_mod_members = [m for m in dir(TaurusQtMod)
                                 if not m.startswith("_")]
        orig_qt_mod_members = [m for m in dir(OrigQtMod)
                               if not m.startswith("_")]

        for orig_member_name in orig_qt_mod_members:
            self.assertTrue(
                orig_member_name in taurus_qt_mod_members,
                "Taurus {0} does not contain {1}".format(qt_mod_name,
                                                         orig_member_name)
            )

    def test_qt_core(self):
        """Check the QtCore shim"""
        return self.__test_qt_module("QtCore")

    def test_qt_gui(self):
        """Check the QtGui shim"""
        return self.__test_qt_module("QtGui")


def main():
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()

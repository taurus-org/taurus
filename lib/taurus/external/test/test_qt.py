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
from taurus import tauruscustomsettings
from taurus.external import unittest

_QtAPIs = ["PyQt4", "PySide", "PyQt5"]


def _import(name):
    __import__(name)
    return sys.modules[name]


class QtTestCase(unittest.TestCase):

    QtAPI = None

    def setUp(self):
        taurus.setLogLevel(taurus.Critical)

        for qt in _QtAPIs:
            if qt in sys.modules:
                self.QtAPI = qt
                break
        else:
            self.QtAPI = "PyQt4"

        self.opt_mods = ("QtDesigner", "QtNetwork", "Qt", "QtSvg",
                         "QtUiTools", "QtWebKit", "Qwt5", "uic")

        # store a "snapshot" of the currently loaded modules
        self._orig_mods = set(sys.modules.keys())

        # auto initialize Qt by taurus using forcibly the self.QtAPI
        tauruscustomsettings.QT_AUTO_INIT = True
        tauruscustomsettings.QT_AUTO_API = self.QtAPI
        tauruscustomsettings.QT_AUTO_STRICT = True

        # this import initializes Qt in case it is not loaded
        from taurus.external.qt import Qt
        self.__qt = Qt

    def test_qt_base_import(self):
        mods = set(sys.modules.keys())

        other_apis = set(_QtAPIs)
        other_apis.remove(self.QtAPI)

        from taurus.external.qt import getQtName

        self.assertEquals(getQtName(), self.QtAPI)

        for other_api in other_apis:
            self.assertFalse(other_api in mods, other_api + " loaded in " + self.QtAPI + " test")

        self.assertTrue(self.QtAPI in mods, self.QtAPI + " not loaded")
        self.assertTrue(self.QtAPI + ".QtCore" in mods, "QtCore not loaded")

        for opt_mod in self.opt_mods:
            mod = "{0}.{1}".format(self.QtAPI, opt_mod)
            self.assertFalse(mod in mods-self._orig_mods, mod + " is loaded")

    def __test_qt_module(self, qt_mod_name):
        taurus_qt_mod_name = "taurus.external.qt.{0}".format(qt_mod_name)
        orig_qt_mod_name = "{0}.{1}".format(self.QtAPI, qt_mod_name)
        TaurusQtMod = _import(taurus_qt_mod_name)
        OrigQtMod = _import(orig_qt_mod_name)
        taurus_qt_mod_members = [ m for m in dir(TaurusQtMod) if not m.startswith("_") ]
        orig_qt_mod_members = [ m for m in dir(OrigQtMod) if not m.startswith("_") ]

        for orig_member_name in orig_qt_mod_members:
            self.assertTrue(orig_member_name in taurus_qt_mod_members,
                            "Taurus {0} does not contain {1}".format(qt_mod_name, orig_member_name))

    def test_qt_core(self):
        return self.__test_qt_module("QtCore")

    def test_qt_gui(self):
        return self.__test_qt_module("QtGui")

    def test_icons(self):
        '''check that theme icons work'''
        from taurus.external.qt import Qt
        icon = Qt.QIcon.fromTheme("folder-open")
        msg = ('Theme icons not available ' + 
               '(if PyQt<4.6, make sure to build resources first!)')
        self.assertFalse(icon.isNull(), msg)


def  main():
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()

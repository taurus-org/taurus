# -*- coding: utf-8 -*-

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
##
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
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
#############################################################################

import os.path as osp

import taurus
taurus.setLogLevel(taurus.Critical)

#TODO change imports 
import unittest2 as unittest
from taurus.qt import Qt
#from taurus.external import unittest
#from taurus.external.qt import Qt

from taurus.qt.qtgui.util.ui import UILoadable

__APP = None

def Application():
    global __APP
    app = Qt.QApplication.instance()
    if app is None:
        app = Qt.QApplication([])
        __APP = app
    return app


@UILoadable
class MyWidget1(Qt.QWidget):

    def __init__(self, parent=None):
        Qt.QWidget.__init__(self, parent)
        self.loadUi()
        self.my_button.setText("This is MY1 button")


@UILoadable(with_ui="ui")
class MyWidget2(Qt.QWidget):

    def __init__(self, parent=None):
        Qt.QWidget.__init__(self, parent)
        self.loadUi(filename="mywidget2_custom.ui",
                    path=osp.join(osp.dirname(__file__), "ui", "mywidget2"))
        self.ui.my_button.setText("This is MY2 button")
        

class UILoadableTestCase(unittest.TestCase):

    def setUp(self):
        taurus.setLogLevel(taurus.Critical)

    def test_uiloadable_default(self):
        Application()
        widget = MyWidget1()
        self.assertEquals(widget.my_button.text(), "This is MY1 button")

    def test_uiloadable_customized(self):
        Application()
        widget = MyWidget2()
        self.assertEquals(widget.ui.my_button.text(), "This is MY2 button")
        

def main():
    unittest.main()


if __name__ == "__main__":
    main()

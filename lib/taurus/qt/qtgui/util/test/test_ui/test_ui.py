# -*- coding: utf-8 -*-

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

"""Unit tests for UILoadable decorator"""

from __future__ import absolute_import

import os.path

import unittest
from taurus.external.qt import Qt
from taurus.qt.qtgui.util.ui import UILoadable
from .mywidget3 import MyWidget3


class UILoadableTestCase(unittest.TestCase):
    """
    Test cases for UILoadable decorator
    """

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
        path = os.path.join(os.path.dirname(__file__), "ui", "mywidget2")
        self.loadUi(filename="mywidget2_custom.ui", path=path)
        self.ui.my_button.setText("This is MY2 button")


class Bug151_Widget(MyWidget3):
    pass


def test_uiloadable_default(qtbot):
    """Test UILoadable with default arguments"""
    w = MyWidget1()
    qtbot.addWidget(w)
    assert w.my_button.text() == "This is MY1 button"


def test_uiloadable_customized(qtbot):
    """Test UILoadable with customized filename and path"""
    w = MyWidget2()
    qtbot.addWidget(w)
    assert hasattr(w, "ui")
    assert hasattr(w.ui, "my_button")
    assert not hasattr(w, "my_button")
    assert w.ui.my_button.text() == "This is MY2 button"


def test_bug151(qtbot):
    """Check inheritance of UILoadable classes across packages (bug #151)"""

    w = Bug151_Widget()
    qtbot.addWidget(w)

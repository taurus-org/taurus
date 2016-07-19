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

import os.path

from taurus.external import unittest
from taurus.external.qt import Qt
from taurus.qt.qtgui.util.ui import UILoadable
from taurus.qt.qtgui.test import BaseWidgetTestCase
from mywidget3 import MyWidget3


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

    def setUp(self):
        app = Qt.QApplication.instance()
        if app is None:
            app = Qt.QApplication([])
        self.__app = app

    def test_uiloadable_default(self):
        """Test UILoadable with default arguments"""
        widget = self.MyWidget1()
        self.assertEquals(widget.my_button.text(), "This is MY1 button",
                          "button text differs from expected")

    def test_uiloadable_customized(self):
        """Test UILoadable with customized filename and path"""
        widget = self.MyWidget2()
        self.assertTrue(hasattr(widget, "ui"),
                        "widget doesn't have 'ui' member")
        self.assertTrue(hasattr(widget.ui, "my_button"),
                        "widget.ui doesn't have a 'my_button' member")
        self.assertFalse(hasattr(widget, "my_button"),
                         "widget has a my_button member")
        self.assertEquals(widget.ui.my_button.text(), "This is MY2 button",
                          "button text differs from expected")


class Bug151_TestCase(BaseWidgetTestCase, unittest.TestCase):
    '''Test for bug 151: https://sourceforge.net/p/tauruslib/tickets/151/'''

    def test_bug151(self):
        '''Check inheritance of UILoadable classes across packages (bug #151)
        '''
        class Bug151_Widget(MyWidget3):
            pass
        try:
            Bug151_Widget()
        except:
            self.fail('Inheriting from UILoadable from another package fails')


def main():
    unittest.main()


if __name__ == "__main__":
    main()

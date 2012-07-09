#!/usr/bin/env python

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

"""This module provides a set of dialog based widgets"""

__all__ = ["TaurusDialog"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt
from taurus.qt.qtgui.panel import InputPanel


class TaurusInputDialog(Qt.QDialog):
    """A panel intended to get a value from the user."""
    
    input_panel = InputPanel
    
    def __init__(self, input_data=None, parent=None, designMode=False):
        Qt.QDialog.__init__(self, parent)
        layout = Qt.QVBoxLayout()
        self.setLayout(layout)
        self._panel = self.input_panel(input_data, self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._panel)
        self.connect(self.panel().buttonBox(), Qt.SIGNAL("accepted()"),
                     self.accept)
        self._panel.setInputFocus()

    def panel(self):
        """Returns the :class:`taurus.qt.qtgui.panel.TaurusMessagePanel`.
        
        :return: the internal panel
        :rtype: taurus.qt.qtgui.panel.TaurusMessagePanel"""
        return self._panel
    
    def addButton(self, button, role=Qt.QDialogButtonBox.ActionRole):
        """Adds the given button with the given to the button box
        
        :param button: the button to be added
        :type button: PyQt4.QtGui.QPushButton
        :param role: button role
        :type role: PyQt4.Qt.QDialogButtonBox.ButtonRole"""
        self.panel().addButton(button, role)
    
    def setIconPixmap(self, pixmap):
        """Sets the icon to the dialog
        
        :param pixmap: the icon pixmap
        :type pixmap: PyQt4.Qt.QPixmap"""
        self._panel.setIconPixmap(pixmap)
    
    def setText(self, text):
        """Sets the text of the dialog
        
        :param text: the new text
        :type text: str"""
        self._panel.setText(text)
    
    def getText(self):
        """Returns the current text of this panel
        
        :return: the text for this panel
        :rtype: str"""
        return self._panel.getText()


def demo():

    d1 = dict(prompt="What's your name?", data_type="String")
    d2 = dict(prompt="What's your age?", data_type="Integer",
              default_value=4, maximum=100, key="Age", unit="years")
    d3 = dict(prompt="What's your favourite number?", data_type="Float", 
              default_value=0.1, maximum=88.8, key="Number")
    d4 = dict(prompt="What's your favourite car brand?",
              data_type=["Mazda", "Skoda", "Citroen", "Mercedes", "Audi", "Ferrari"], 
              default_value="Mercedes")
    d5 = dict(prompt="Select some car brands", allow_multiple=True,
              data_type=["Mazda", "Skoda", "Citroen", "Mercedes", "Audi", "Ferrari"], 
              default_value=["Mercedes", "Citroen"])
    d6 = dict(prompt="What's your favourite color?", key="Color",
              data_type=["blue", "red", "green"], default_value="red")
    d7 = dict(prompt="Do you like bears?",
              data_type='Boolean', key="Yes/No", default_value=True)
    d8 = dict(prompt="Please write your memo",
              data_type='Text', key="Memo", default_value="By default a memo is\na long thing")
    w = TaurusInputDialog(d5)
    w.show()
    return w


def main():
    
    import sys
    import taurus.qt.qtgui.application

    Application = taurus.qt.qtgui.application.TaurusApplication
    
    app = Application.instance()
    owns_app = app is None
    
    if owns_app:
        app = Qt.QApplication([])
        app.setApplicationName("Taurus input dialog demo")
        app.setApplicationVersion("1.0")

    w = demo()
    w.exec_()
    print w._panel.get_value()
        
if __name__ == "__main__":
    main()
    

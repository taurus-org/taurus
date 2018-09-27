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

"""This module provides a set of dialog based widgets"""
from __future__ import print_function

from taurus.external.qt import Qt


__all__ = ["TaurusInputDialog", "get_input"]

__docformat__ = 'restructuredtext'


def get_input(input_data, parent=None, input_panel_klass=None):
    """Static convenience function to get an input from the user using a
    dialog. The dialog will be modal.

    The input_data is a dictionary which contains information on how to build
    the input dialog. It **must** contains the following keys:

        - *prompt* <str>: message to be displayed

    The following are optional keys (and their corresponding default values):

        - *title* <str> (doesn't have default value)
        - *key* <str> (doesn't have default value):
          a label to be presented left to the input box represeting the label
        - *unit* <str> (doesn't have default value):
          a label to be presented right to the input box representing the units
        - *data_type* <str or sequence> ('String'):
          type of data to be requested. Standard
          accepted data types are 'String', 'Integer', 'Float', 'Boolean',
          'Text'. A list of elements will be interpreted as a selection.
          Default TaurusInputPanel class will interpret any custom data types as
          'String' and will display input widget accordingly. Custom
          data types can be handled differently by supplying a different
          input_panel_klass.
        - *minimum* <int/float> (-sys.maxint):
          minimum value (makes sence when data_type is 'Integer' or 'Float')
        - *maximum* <int/float> (sys.maxint):
          maximum value (makes sence when data_type is 'Integer' or 'Float')
        - *step* <int/float> (1):
          step size value (makes sence when data_type is 'Integer' or 'Float')
        - *decimals* <int> (1):
          number of decimal places to show (makes sence when data_type is
          'Float')
        - *default_value* <obj> (doesn't have default value):
          default value
        - *allow_multiple* <bool> (False):
          allow more than one value to be selected (makes sence when data_type
          is a sequence of possibilities)

    :param input_data: a dictionary with information on how to build the input dialog
    :type input_data: :py:obj:`dict`
    :param parent: parent widget
    :type parent: PyQt4.QtGui.QWidget
    :param input_panel_klass: python class to be used as input panel [default: :class:`~taurus.qt.qtgui.panel.TaurusInputPanel`]
    :type input_panel_klass: :class:`~taurus.qt.qtgui.panel.TaurusInputPanel`

    :return: a tuple containing value selected and boolean which is true if
             user accepted the dialog (pressed Ok) or false otherwise
    :rtype: tuple< obj, bool >

    Examples::

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
                  data_type='Text', key="Memo", default_value="By default a memo is a long thing")
        for d in [d1, d2, d3, d4, d5, d6, d7, d8]:
            get_input(input_data=d, title=d['prompt'])

    """

    if input_panel_klass is None:
        from taurus.qt.qtgui.panel import TaurusInputPanel
        input_panel_klass = TaurusInputPanel
    dialog = TaurusInputDialog(input_data=input_data, parent=parent,
                               input_panel_klass=input_panel_klass)
    dialog.exec_()
    return dialog.value(), dialog.result()


class TaurusInputDialog(Qt.QDialog):
    """The TaurusInputDialog class provides a simple convenience dialog to get
    a single value from the user.
    """

    def __init__(self, input_data=None, parent=None,
                 input_panel_klass=None, designMode=False):
        if input_panel_klass is None:
            from taurus.qt.qtgui.panel import TaurusInputPanel
            input_panel_klass = TaurusInputPanel
        self.input_data = input_data
        self.input_panel_klass = input_panel_klass
        Qt.QDialog.__init__(self, parent)
        if input_data and 'title' in input_data:
            self.setWindowTitle(input_data['title'])
        layout = Qt.QVBoxLayout()
        self.setLayout(layout)
        self._panel = panel = input_panel_klass(input_data, self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._panel)
        panel.buttonBox().accepted.connect(self.accept)
        panel.buttonBox().rejected.connect(self.reject)
        self._panel.setInputFocus()

    def panel(self):
        """Returns the :class:`taurus.qt.qtgui.panel.TaurusInputPanel`.

        :return: the internal panel
        :rtype: taurus.qt.qtgui.panel.TaurusInputPanel"""
        return self._panel

    def value(self):
        """Returns the value selected by the user.

        :return: the value selected by the user"""
        return self.panel().value()


def demo():
    """Input Dialog"""

    input_data = dict(prompt="What's your favourite car brand?",
                      data_type=["Mazda", "Skoda", "Citroen",
                                 "Mercedes", "Audi", "Ferrari"],
                      default_value="Mercedes")
    w = TaurusInputDialog(input_data=input_data)
    w.show()
    return w


def main():
    import taurus.qt.qtgui.application

    Application = taurus.qt.qtgui.application.TaurusApplication

    app = Application.instance()
    owns_app = app is None

    if owns_app:
        app = Qt.QApplication([])
        app.setApplicationName("Taurus input dialog demo")
        app.setApplicationVersion("1.0")

    d1 = dict(prompt="What's your name?", data_type="String")
    d2 = dict(prompt="What's your age?", data_type="Integer",
              default_value=4, maximum=100, key="Age", unit="years")
    d3 = dict(prompt="What's your favourite number?", data_type="Float",
              default_value=0.1, maximum=88.8, key="Number")
    d4 = dict(prompt="What's your favourite car brand?",
              data_type=["Mazda", "Skoda", "Citroen",
                         "Mercedes", "Audi", "Ferrari"],
              default_value="Mercedes")
    d5 = dict(prompt="Select some car brands", allow_multiple=True,
              data_type=["Mazda", "Skoda", "Citroen",
                         "Mercedes", "Audi", "Ferrari"],
              default_value=["Mercedes", "Citroen"])
    d6 = dict(prompt="What's your favourite color?", key="Color",
              data_type=["blue", "red", "green"], default_value="red")
    d7 = dict(prompt="Do you like bears?",
              data_type='Boolean', key="Yes/No", default_value=True)
    d8 = dict(prompt="Please write your memo",
              data_type='Text', key="Memo", default_value="By default a memo is\na long thing")

    for d in [d1, d2, d3, d4, d5, d6, d7, d8]:
        print(get_input(input_data=d, title=d['prompt']))

if __name__ == "__main__":
    main()

#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus, a Tango User Interface Library
##
# http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
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

from __future__ import print_function
import sys
import click

import taurus.core.util
import taurus.qt.qtgui.util
import taurus.qt.qtgui.application

from taurus.external.qt import Qt


class TaurusDemoPanel(Qt.QWidget):

    def __init__(self, parent=None):
        Qt.QWidget.__init__(self, parent)
        self._groups = {}

        layout = Qt.QGridLayout()
        self.setLayout(layout)

        wf = taurus.qt.qtgui.util.TaurusWidgetFactory()

        taurus_widgets = wf.getWidgets()

        demos = {}
        for widget_name in taurus_widgets:
            widget_module_name, widget_class = taurus_widgets[widget_name]
            internal_widget_module_name = widget_class.__module__
            if internal_widget_module_name in demos:
                continue
            internal_widget_module = sys.modules[internal_widget_module_name]
            if hasattr(internal_widget_module, "demo"):
                if hasattr(internal_widget_module.demo, '__call__'):
                    demos[internal_widget_module_name] = internal_widget_module.demo

        groups = set()

        for demo_name in demos:
            parts = demo_name.split(".")
            group = parts[-2]
            groups.add(group)

        for group in sorted(groups):
            self.addGroup(group)

        for demo_name in sorted(demos):
            demo_func = demos[demo_name]
            parts = demo_name.split(".")
            group = parts[-2]
            if not demo_func.__doc__:
                continue
            try:
                self.addDemo(demo_func.__doc__, demo_func, group)
            except Exception as e:
                print(80 * "-")
                print("Problems adding demo", demo_name)
                print(e)

    def addGroup(self, name):
        g = Qt.QGroupBox(name)
        layout = self.layout()
        layout.addWidget(g, layout.rowCount(), 0)
        l = Qt.QGridLayout()
        g.setLayout(l)
        self._groups[name] = g

    def addDemo(self, name, f, group):
        g = self._groups[group]
        layout = g.layout()
        row = layout.rowCount()
        #label = Qt.QLabel(name, self)
        button = Qt.QPushButton(name, self)
        button._f = f
        layout.addWidget(button, row, 0)
        button.clicked.connect(self.go)

    def go(self):
        b = self.sender()
        f = b._f
        dialog = None
        try:
            w = f()
            if w is None or not isinstance(w, Qt.QWidget):
                raise Exception("demo function does not return a valid widget")
            dialog = Qt.QDialog()
            layout = Qt.QVBoxLayout()
            dialog.setLayout(layout)
            layout.addWidget(w)
            dialog.exec_()
        except Exception as e:
            if dialog is not None:
                dialog.done(0)
                dialog.hide()
                dialog = None
            print(str(e))
            return
            d = Qt.QErrorMessage()
            d.showMessage(str(e))


@click.command('demo')
def demo_cmd():
    """A demo application for taurus"""
    from taurus.qt.qtgui.application import TaurusApplication
    app = TaurusApplication(cmd_line_parser=None)
    gui = TaurusDemoPanel()
    gui.setWindowTitle('Taurus demo')
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

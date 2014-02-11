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

"""A Qt MainWindow for the TaurusConsole

This is a tabbed pseudo-terminal of IPython sessions, with a menu bar for
common actions.
"""

__all__ = ["TaurusConsoleWindow"]

__docformat__ = 'restructuredtext'

import functools

from taurus.qt import Qt
try:
    from IPython.qt.console.mainwindow import MainWindow
except ImportError:
    from IPython.frontend.qt.console.mainwindow import MainWindow


class TaurusConsoleWindow(MainWindow):
    
    def __init__(self, *args, **kwargs):
        self._pending_kernel_actions = []
        self.new_kernel_menu = None
        MainWindow.__init__(self, *args, **kwargs)
    
    def add_tab_with_frontend(self, frontend, name=None):
        init_menu = self.tab_widget.count() == 0
        super(TaurusConsoleWindow, self).add_tab_with_frontend(frontend, name=name)
        if init_menu:
            self.init_menu_bar()
    
    def remove_menu_action(self, menu, action):
        menu.removeAction(action)
        self.removeAction(action)
    
    def add_new_kernel_action(self, action):
        self.add_menu_action(self.new_kernel_menu, action) 
    
    def init_file_menu(self):
        super(TaurusConsoleWindow, self).init_file_menu()
        file_menu = self.file_menu
        self.remove_menu_action(file_menu, self.new_kernel_tab_act)
        
        self.new_kernel_menu = new_kernel_menu = Qt.QMenu(self.new_kernel_tab_act.text())
        file_menu.insertMenu(self.slave_kernel_tab_act, new_kernel_menu)
        
        #self.new_kernel_tab_act.setText("IPython")
        #self.add_menu_action(new_kernel_menu, self.new_kernel_tab_act)
        
        for kernel_action in self._pending_kernel_actions:
            self.add_new_kernel_action(kernel_action)
        
    def add_new_tango_action(self):
        tango_action = Qt.QAction("Tango", self,
            triggered=self.create_tab_with_new_tango_frontend)
        self.add_new_kernel_action(tango_action)

    def create_tab_with_new_frontend(self, name='ipython', label=None):
        widget = self.new_frontend_factory(name=name)
        self.add_tab_with_frontend(widget, name=label)
    
    def register_kernel_extension(self, extension):
        f = functools.partial(self.create_tab_with_new_frontend,
                              name=extension.Name,
                              label=extension.Label)
        action = Qt.QAction(extension.Label, self, triggered=f)
        
        if self.new_kernel_menu is None:
            self._pending_kernel_actions.append(action)
        else:
            self.add_new_kernel_action(action)
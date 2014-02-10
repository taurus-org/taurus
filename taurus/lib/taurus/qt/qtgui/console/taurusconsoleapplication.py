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

""" A minimal application using the Qt console-style IPython frontend.

This is not a complete console app, as subprocess will not be able to receive
input, there is no real readline support, among other limitations.
"""

__all__ = ["TaurusConsoleApplication"]

__docformat__ = 'restructuredtext'


from taurus.qt import Qt

try:
    from IPython.qt.console.qtconsoleapp import IPythonQtConsoleApp
except ImportError: #for IPython v<1.x
    from IPython.frontend.qt.console.qtconsoleapp import IPythonQtConsoleApp
     

class TaurusConsoleApplication(IPythonQtConsoleApp):

    name='taurusconsole'

    def init_qt_elements(self):
        self.app = Qt.QApplication.instance()
        self.app.icon = Qt.QIcon()

    def init_signal(self):
        pass

    def init_kernel_manager(self):
        # avoid starting a default kernel 
        self.kernel_manager = None

    



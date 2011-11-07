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

"""This package contains a collection of taurus console widgets"""

__docformat__ = 'restructuredtext'

from IPython.frontend.qt.console.qtconsoleapp import IPythonQtConsoleApp

from taurus.qt import Qt, QtGui
if hasattr(Qt, 'QString'):
    raise Exception, "Using Qt SIP API v1. IPython requires Qt SIP API v2"


class TaurusConsoleApp(IPythonQtConsoleApp):
    pass


class TaurusConsole(QtGui.QWidget):
    
    def __init__(self, parent=None, designMode=False):
        QtGui.QWidget.__init__(self, parent)
        l = QtGui.QVBoxLayout()
        l.setContentsMargins(0,0,0,0)
        l.setSpacing(0)
        self.setLayout(l)
        self.app = app = TaurusConsoleApp()
        app.initialize(argv=["--pylab=inline"])
        l.addWidget(app.widget)
    
    
    
#-----------------------------------------------------------------------------
# Main entry point
#-----------------------------------------------------------------------------

def main():
    import taurus.qt.qtgui.application
    
    #app = taurus.qt.qtgui.application.TaurusApplication()
    
    taurus_app = TaurusConsoleApp()
    taurus_app.initialize()
    taurus_app.start()


if __name__ == '__main__':
    main()

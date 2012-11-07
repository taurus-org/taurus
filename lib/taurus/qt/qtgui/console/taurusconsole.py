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

__all__ = ["TaurusConsole"]

__docformat__ = 'restructuredtext'

from taurus.qt import Qt
from taurusconsolefactory import TaurusConsoleFactory


class TaurusConsole(Qt.QWidget):
    
    def __init__(self, parent=None, kernels=None):
        super(TaurusConsole, self).__init__(parent)
        l = Qt.QVBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)
        self.setLayout(l)
        self._window = window = TaurusConsoleFactory().new_window(kernels=kernels)
        l.addWidget(window)

    def window(self):
        return self._window

    def __getattr__(self, name):
        return getattr(self.window(), name)
    

def main(argv=None):
    import taurus.core.util.argparse
    import taurus.qt.qtgui.application
    
    targp = taurus.core.util.argparse
    
    if argv is None:
        import sys
        argv = sys.argv

    parser = targp.get_taurus_parser()
    taurus_args, ipython_args = targp.split_taurus_args(parser, args=argv)

    app = taurus.qt.qtgui.application.TaurusApplication(taurus_args,
                                                        cmd_line_parser=parser)
    TaurusConsoleFactory(ipython_args=ipython_args)
    console = TaurusConsole()
    console.window().create_tab_with_new_frontend(name='tango', label="Tango")
    console.show()
    app.exec_()


if __name__ == '__main__':
    main()
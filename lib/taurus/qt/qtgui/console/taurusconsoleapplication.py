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

__docformat__ = 'restructuredtext'

from IPython.frontend.qt.console.qtconsoleapp import IPythonQtConsoleApp
from IPython.lib.kernel import find_connection_file

from taurusconsolewidget import TaurusConsoleWidget


class TaurusConsoleApplication(IPythonQtConsoleApp):

    name='taurusconsole'

    def __init__(self, *args, **kwargs):
        super(TaurusConsoleApplication, self).__init__(*args, **kwargs)
        self.widget_factory = TaurusConsoleWidget

    def init_qt_elements(self):
        pass

    def init_signal(self):
        pass

    def new_frontend_from_existing(self):
        """Create and return new frontend from connection file basename"""
        cf = find_connection_file(self.existing, profile=self.profile)
        kernel_manager = self.kernel_manager_class(connection_file=cf,
                                                   config=self.config)
        kernel_manager.load_connection_file()
        kernel_manager.start_channels()
        widget = self.widget_factory(config=self.config, local_kernel=False)
        widget._existing = True
        widget._may_close = False
        widget._confirm_exit = False
        widget.kernel_manager = kernel_manager

#        widget.exit_requested.connect(self.close_tab)

        return widget


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
    iapp = app.create_ipython_application(ipython_args)

    w = iapp.new_frontend_from_existing()
    w.show()

    app.exec_()


if __name__ == '__main__':
    main()

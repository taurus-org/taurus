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

__all__ = ["TaurusConsoleWidget"]

__docformat__ = 'restructuredtext'

from IPython.utils.traitlets import Unicode
from IPython.utils.localinterfaces import LOCALHOST, LOCAL_IPS
from IPython.frontend.qt.console.rich_ipython_widget import RichIPythonWidget

from taurus.qt import Qt

if hasattr(Qt, 'QString'):
    raise Exception("Using Qt SIP API v1. IPython requires Qt SIP API v2")

default_gui_banner = """\
Taurus console -- An enhanced IPython console for taurus.

?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.
%guiref   -> A brief reference about the graphical user interface.
"""


class TaurusConsoleWidget(RichIPythonWidget):

    banner = Unicode(config=True)

    def __init__(self, *args, **kwargs):
        super(TaurusConsoleWidget, self).__init__(*args, **kwargs)

    #------ Trait default initializers ---------------------------------------
    def _banner_default(self):
        return default_gui_banner


def new_frontend_widget(iapp=None, from_kernel_manager=None, args=None):
    """Create and return new frontend attached to new kernel,
    launched on localhost."""

    is_master = from_kernel_manager is None

    if iapp is None:
        import taurus.core.util.argparse
        import taurus.qt.qtgui.application
        qt_app = taurus.qt.qtgui.application.TaurusApplication.instance()
        if qt_app is None:
            qt_app = taurus.qt.qtgui.application.TaurusApplication()
        parser = qt_app.get_command_line_parser()
        taurus_args, ipython_args = taurus.core.util.argparse.split_taurus_args(parser, args=args)
        iapp = qt_app.create_ipython_application(ipython_args)

    config = iapp.config

    km_kwargs = dict(config=config)
    if is_master:
        km_kwargs['ip'] = iapp.ip if iapp.ip in LOCAL_IPS else LOCALHOST
        km_kwargs['connection_file'] = iapp._new_connection_file()
    else:
        km_kwargs['connection_file'] = from_kernel_manager.connection_file

    kernel_manager = iapp.kernel_manager_class(**km_kwargs)

    if is_master:
        print kernel_manager.start_kernel(ipython=not iapp.pure,
                                    extra_arguments=iapp.kernel_argv)
    else:
        kernel_manager.load_connection_file()
    kernel_manager.start_channels()
    
    widget = iapp.widget_factory(config=config, local_kernel=is_master)
    iapp.init_colors(widget)
    widget.kernel_manager = kernel_manager
    widget._existing = not is_master
    widget._may_close = False
    widget._confirm_exit = iapp.confirm_exit
    return widget


def TaurusConsole(args=None):
    return new_frontend_widget(args=args)

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
    w = TaurusConsole()
    w.show()

    app.exec_()

if __name__ == "__main__":
    main()

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

__all__ = ["TaurusConsole"]

__docformat__ = 'restructuredtext'

#import sys
#if not hasattr(sys, 'argv'):
#    sys.argv = ['taurus']

from IPython.lib.kernel import find_connection_file
from IPython.config.application import catch_config_error
from IPython.utils.traitlets import Unicode
from IPython.utils.localinterfaces import LOCALHOST, LOCAL_IPS
from IPython.frontend.qt.console.qtconsoleapp import IPythonQtConsoleApp
#from IPython.frontend.qt.console.ipython_widget import IPythonWidget
from IPython.frontend.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.frontend.qt.console.mainwindow import MainWindow

from taurus import Release
from taurus.qt import Qt
from taurus.qt.qtgui.resource import getThemeIcon

#if hasattr(Qt, 'QString'):
#    raise Exception("Using Qt SIP API v1. IPython requires Qt SIP API v2")

default_gui_banner = """\
Taurus console -- An enhanced IPython console for taurus.

?         -> Introduction and overview of features.
%quickref -> Quick reference.
help      -> Help system.
object?   -> Details about 'object', use 'object??' for extra details.
%guiref   -> A brief reference about the graphical user interface.
"""

        
class TaurusIPythonApp(IPythonQtConsoleApp):

    name='taurusconsole'
    description = Unicode(u'TaurusConsole: An enhanced IPython console for taurus.')
    version = Unicode(Release.version)

    def __init__(self, *args, **kwargs):
        super(TaurusIPythonApp, self).__init__(*args, **kwargs)
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

    @catch_config_error
    def initialize(self, argv=None):
        super(TaurusIPythonApp, self).initialize(argv=argv)


class TaurusConsoleWidget(RichIPythonWidget):

    banner = Unicode(config=True)

    def __init__(self, *args, **kwargs):
        super(TaurusConsoleWidget, self).__init__(*args, **kwargs)

    #------ Trait default initializers ---------------------------------------
    
    def _banner_default(self):
        return default_gui_banner


def new_frontend_widget(iapp=None, args=None):
    """Create and return new frontend attached to new kernel,
    launched on localhost."""
    is_master = iapp is None

    if is_master is None:
        import taurus.core.util.argparse
        import taurus.qt.qtgui.application
        targp = taurus.core.util.argparse
        tapp = taurus.qt.qtgui.application
        qt_app = tapp.TaurusApplication.instance()
        if qt_app is None:
            qt_app = tapp.TaurusApplication()
        parser = qt_app.get_command_line_parser()
        taurus_args, ipython_args = targp.split_taurus_args(parser, args=args)
        iapp = qt_app.create_ipython_application()
        iapp.initialize(argv=ipython_args)

    config = iapp.config

    km_kwargs = dict(config=config)
    if is_master:
        km_kwargs['ip'] = iapp.ip if iapp.ip in LOCAL_IPS else LOCALHOST
        km_kwargs['connection_file'] = iapp._new_connection_file()
    else:
        km_kwargs['connection_file'] = iapp.connection_file

    kernel_manager = iapp.kernel_manager_class(**km_kwargs)

    if is_master:
        kernel_manager.start_kernel(ipython=not iapp.pure,
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


class TaurusConsole(RichIPythonWidget):

    banner = Unicode(config=True)

    def __init__(self, *args, **kwargs):
        ipython_args = kwargs.pop('ipython_args', [])

        self.iapp = iapp = TaurusIPythonApp()
        iapp.initialize(argv=ipython_args)

        config = iapp.config

        kwargs['local_kernel'] = True
        kwargs['config'] = config
        super(TaurusConsole, self).__init__(*args, **kwargs)

        iapp.init_colors(self)
        self.kernel_manager = iapp.kernel_manager
        self._existing = True
        self._may_close = False
        self._confirm_exit = iapp.confirm_exit

    #------ Trait default initializers ---------------------------------------
    
    def _banner_default(self):
        return default_gui_banner

    @classmethod
    def getQtDesignerPluginInfo(cls):
        
        return { 
            'module'    : 'taurus.qt.qtgui.console',
            'group'     : 'Taurus Display',
            'icon'      : ":/utilities-terminal.svg",
            'container' : False
        }

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
    w = TaurusConsole(ipython_args=ipython_args)
    w.show()

    app.exec_()

if __name__ == "__main__":
    main()

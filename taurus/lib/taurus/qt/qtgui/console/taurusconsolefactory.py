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

__all__ = ["TaurusConsoleFactory"]

__docformat__ = 'restructuredtext'

from taurus.core.util.singleton import Singleton
from taurus.qt import Qt

from taurusconsolewidget import TaurusConsoleWidget
from taurusconsolewindow import TaurusConsoleWindow
from taurusconsoleapplication import TaurusConsoleApplication

import taurusconsoleextensions
try:
    from IPython.qt.kernelmanager import QtKernelManager
except ImportError:
    from IPython.frontend.qt.kernelmanager import QtKernelManager


class TaurusConsoleFactory(Singleton):

    ipython_application_class = TaurusConsoleApplication
    widget_factory_class = TaurusConsoleWidget
    kernel_manager_class = QtKernelManager
    
    def init(self, *args, **kwargs):
        self.ipython_application = None
        self.ipython_args = kwargs.pop('ipython_args', [])
    
    def get_ipython_application(self):
        app = self.ipython_application
        if app is None:
            self.ipython_application = app = self.ipython_application_class()
            app.kernel_manager_class = self.new_kernel_manager
            app.initialize(argv=self.ipython_args)
            app.widget_factory = self.new_frontend_widget
            self.orig_config = app.config.copy()
        return app

    def get_extensions(self):
        import inspect
        ret = {}
        for obj_name in dir(taurusconsoleextensions):
            if obj_name.startswith("_"):
                continue
            obj = getattr(taurusconsoleextensions, obj_name)
            if inspect.isclass(obj):
                if issubclass(obj, taurusconsoleextensions.BaseConsoleExtension):
                    if obj.is_enabled():
                        ret[obj.Name] = obj 
        return ret
    
    def get_extension(self, name):
        import inspect
        ret = {}
        for obj_name in dir(taurusconsoleextensions):
            if obj_name.startswith("_"):
                continue
            obj = getattr(taurusconsoleextensions, obj_name)
            if inspect.isclass(obj):
                if issubclass(obj, taurusconsoleextensions.BaseConsoleExtension):
                    if obj.is_enabled():
                        if obj.Name == name:
                            return obj
                        ret[obj.Name] = obj 
    
    def new_kernel_manager(self, **kwargs):
        return self.kernel_manager_class(**kwargs)
    
    def new_frontend_widget(self, *args, **kwargs):
        return self.widget_factory_class(*args, **kwargs)
    
    def new_frontend_slave(self, widget):
        app = self.get_ipython_application()
        new_widget = app.new_frontend_slave(widget)
        return new_widget
    
    def new_frontend_master(self, name="ipython"):
        app = self.get_ipython_application()
        extension = self.get_extension(name)
        with extension(self):
            return app.new_frontend_master()

    def new_window(self, kernels=None):
        qtapp = Qt.QApplication.instance()
        window = TaurusConsoleWindow(qtapp,
            new_frontend_factory=self.new_frontend_master, 
            slave_frontend_factory=self.new_frontend_slave)
        extensions = self.get_extensions()
        for extension in extensions.values():
            window.register_kernel_extension(extension)
        if kernels is not None:
            for kernel in kernels:
                if isinstance(kernel, tuple):
                    name, label = kernel
                else:
                    name, label = kernel, kernel
                window.create_tab_with_new_frontend(name=name, label=label)
        return window

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

    console_factory = TaurusConsoleFactory(ipython_args=ipython_args)
    window = console_factory.new_window(kernels=[('ipython', 'IPython')])
    window.create_tab_with_new_frontend(name='tango', label="Tango")
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
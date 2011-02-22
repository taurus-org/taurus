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

"""This module provides the base :class:`taurus.qt.qtgui.application.TaurusApplication` 
class."""

__all__ = ["TaurusApplication"]

__docformat__ = 'restructuredtext'

from PyQt4 import Qt

import taurus.core.util.argparse

class TaurusApplication(Qt.QApplication):
    """A QApplication that additionally parses the command line looking
    for taurus options. This is done using the :mod:`taurus.core.util.argparse`.
    To create a TaurusApplication object you should use the same parameters
    as in QApplication. 
    
    The optional keyword parameters:
        - app_name: (str) application name
        - app_version: (str) application version
        - org_name: (str) organization name
        - org_domain: (str) organization domain
    
    ...And at last the 'cmd_line_parser' which should be an instance of 
    :class:`optparse.OptionParser`. Simple example::

        import sys
        import taurus.qt.qtgui.application
        import taurus.qt.qtgui.display
                
        app = taurus.qt.qtgui.application.TaurusApplication()
        
        w = taurus.qt.qtgui.display.TaurusLabel()
        w.model = 'sys/tg_test/1/double_scalar'
        w.show()

        sys.exit(app.exec_())
    
    A more complex example showing how to add options and a usage help::
    
        import sys
        import taurus.core.util.argparse
        import taurus.qt.qtgui.application
        import taurus.qt.qtgui.display
                
        parser = taurus.core.util.argparse.get_taurus_parser()
        parser.usage = "%prog [options] <model>"
        parser.add_option("--hello")
        
        app = taurus.qt.qtgui.application.TaurusApplication(cmd_line_parser=parser)
        args = app.get_command_line_args()
        if len(args) < 1:
            sys.stderr.write("Need to supply model attribute")
            sys.exit(1)
        
        w = taurus.qt.qtgui.display.TaurusLabel()
        w.model = args[1]
        w.show()

        sys.exit(app.exec_())
        
    For more details on taurus command line parsing check 
    :mod:`taurus.core.util.argparse`.
    """
    
    def __init__(self, *args, **kwargs):
        """The constructor. Parameters are the same as QApplication plus a
        keyword parameter: 'cmd_line_parser' which should be an instance of
        :class:`optparse.OptionParser`"""
        if len(args) == 0:
            args = ([],)
        parser=None
        app_name, app_version, org_name, org_domain = None, None, None, None
        if kwargs.has_key('app_name'):
            app_name = kwargs.pop('app_name')
        if kwargs.has_key('app_version'):
            app_version = kwargs.pop('app_version')
        if kwargs.has_key('org_name'):
            org_name = kwargs.pop('org_name')
        if kwargs.has_key('org_domain'):
            org_domain = kwargs.pop('org_domain')
        if kwargs.has_key('cmd_line_parser'):
            parser = kwargs.pop('cmd_line_parser')

        try:
            Qt.QApplication.__init__(self, *args, **kwargs)
        except TypeError:
            Qt.QApplication.__init__(self, *args)

        if app_name is not None:
            self.setApplicationName(app_name)
        if app_version is not None:
            self.setApplicationVersion(app_version)
        if org_name is not None:
            self.setOrganizationName(org_name)
        if org_domain is not None:
            self.setOrganizationDomain(org_domain)
        
        p, opt, args = taurus.core.util.argparse.init_taurus_args(parser=parser)
        
        self._cmd_line_parser = p
        self._cmd_line_options = opt
        self._cmd_line_args = args
        self.__registerQtLogger()
        self.__registerExtensions()
    
    def __registerQtLogger(self):
        import taurus.qt.qtcore.util
        taurus.qt.qtcore.util.initTaurusQtLogger()
    
    def __registerExtensions(self):
        """Registers taurus Qt extensions"""
        try:
            import taurus.qt.qtcore.tango.macroserver
            taurus.qt.qtcore.tango.macroserver.registerExtensions()
        except:
            pass
        try:
            import taurus.core.tango.img
            taurus.core.tango.img.registerExtensions()
        except:
            pass
        
    def get_command_line_parser(self):
        """Returns the :class:`optparse.OptionParser` used to parse the command
        line parameters.
        
        :return: the parser used in the command line
        :rtype: :class:`optparse.OptionParser`"""
        return self._cmd_line_parser
        
    def get_command_line_options(self):
        """Returns the :class:`optparse.Option` that resulted from parsing the
        command line parameters.
        
        :return: the command line options
        :rtype: :class:`optparse.Option`"""
        return self._cmd_line_options
        
    def get_command_line_args(self):
        """Returns the list of arguments that resulted from parsing the
        command line parameters.
        
        :return: the command line arguments
        :rtype: list of strings"""
        return self._cmd_line_args
        
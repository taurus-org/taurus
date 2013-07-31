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

"""This module provides the base
:class:`taurus.qt.qtgui.application.TaurusApplication` class."""

from __future__ import with_statement

__all__ = ["TaurusApplication"]

__docformat__ = 'restructuredtext'

import os
import sys
import logging
import optparse
import threading

from taurus.qt import Qt

from taurus.core.util.log import LogExceptHook, Logger
import taurus.core.util.argparse


class STD(Logger):

    FlushWaterMark = 1000

    def __init__(self, name='', parent=None, format=None, std=None,
                 pure_text=True):
        """The STD Logger constructor

        :param name: (str) the logger name (default is empty string)
        :param parent: (Logger) the parent logger or None if no parent exists
                       (default is None)
        :param format: (str) the log message format or None to use the default
                       log format (default is None)
        :param std: std to forward write
        :param pure_text: if True, writes the 'message' parameter of the log
                          message in a separate line preserving the
                          indentation
        """
        Logger.__init__(self, name=name, parent=parent, format=format)
        self.buffer = ''
        self.log_obj.propagate = False
        self.std = std

    def addLogHandler(self, handler):
        """When called, set to use a private handler and DON'T send messages
        to parent loggers (basically will act as an independent logging system
        by itself)

        :param handler: new handler"""
        Logger.addLogHandler(self, handler)
        self.log_obj.propagate = not len(self.log_handlers)

    def write(self, msg):
        try:
            self.buffer += msg
            # while there is no new line, just accumulate the buffer
            msgl = len(msg)
            if msgl > 0 and \
               (msg[-1] == '\n' or msg.index('\n') >= 0 or \
                msgl >= self.FlushWaterMark):
                self.flush()
        except ValueError:
            pass
        finally:
            if self.std is not None:
                try:
                    self.std.write(msg)
                except:
                    pass
            pass

    def flush(self):
        try:
            buff = self.buffer
            if buff is None or len(buff) == 0:
                return
            #take the '\n' because the output is a list of strings, each to be
            #interpreted as a separate line in the client
            if buff[-1] == '\n':
                buff = buff[:-1]
            if self.log_handlers:
                self.log(Logger.Console, '\n' + buff)
            self.buffer = ""
        finally:
            if self.std is not None:
                try:
                    self.std.flush()
                except:
                    pass
            pass


class TaurusApplication(Qt.QApplication, Logger):
    """A QApplication that additionally parses the command line looking
    for taurus options. This is done using the
    :mod:`taurus.core.util.argparse`.
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

        # lock to safely get singleton elements (like IPython taurus
        # console app)
        self._lock = threading.Lock()
        
        if len(args) == 0:
            args = getattr(sys, 'argv', []),

        parser=None
        app_name, app_version, org_name, org_domain = None, None, None, None
        if 'app_name' in kwargs:
            app_name = kwargs.pop('app_name')
        if 'app_version' in kwargs:
            app_version = kwargs.pop('app_version')
        if 'org_name' in kwargs:
            org_name = kwargs.pop('org_name')
        if 'org_domain' in kwargs:
            org_domain = kwargs.pop('org_domain')
        if 'cmd_line_parser' in kwargs:
            parser = kwargs.pop('cmd_line_parser')

        try:
            Qt.QApplication.__init__(self, *args, **kwargs)
        except TypeError:
            Qt.QApplication.__init__(self, *args)

        Logger.__init__(self)

        self._out = None
        self._err = None

        if app_name is not None:
            self.setApplicationName(app_name)
        if app_version is not None:
            self.setApplicationVersion(app_version)
        if org_name is not None:
            self.setOrganizationName(org_name)
        if org_domain is not None:
            self.setOrganizationDomain(org_domain)

        # if the constructor was called without a parser or with a parser that
        # doesn't contain version information and with an application
        # name and/or version, then add the --version capability
        if (parser is None or parser.version is None) and app_version:
            v = app_version
            if app_name:
                v = app_name + " " + app_version
            if parser is None:
                parser = optparse.OptionParser(version=v)
            elif parser.version is None:
                parser.version = v
                parser._add_version_option()

        p, opt, args = \
            taurus.core.util.argparse.init_taurus_args(parser=parser, args=args[0][1:])

        self._cmd_line_parser = p
        self._cmd_line_options = opt
        self._cmd_line_args = args
        self.__registerQtLogger()
        self.__registerExtensions()
        self.__redirect_std()

    def __registerQtLogger(self):
        import taurus.qt.qtcore.util
        taurus.qt.qtcore.util.initTaurusQtLogger()

    def __registerExtensions(self):
        """Registers taurus Qt extensions"""
        try:
            import taurus.qt.qtcore.tango.sardana
            taurus.qt.qtcore.tango.sardana.registerExtensions()
        except:
            self.info("Failed to load sardana extensions", exc_info=1)
        try:
            import taurus.core.tango.img
            taurus.core.tango.img.registerExtensions()
        except:
            self.info("Failed to load image extensions", exc_info=1)

    def __redirect_std(self):
        """Internal method to redirect stdout and stderr to log messages"""
        Logger.addLevelName(Logger.Critical + 10, 'CONSOLE')
        # only redirect if display hook has not been set (IPython does it)
        if sys.displayhook == sys.__displayhook__:
            self._out = STD(name="OUT", std=sys.stdout)
            sys.stdout = self._out
            self._err = STD(name="ERR", std=sys.stderr)
            sys.stderr = self._err

    def __buildLogFileName(self, prefix=None, name=None):
        if prefix is None:
            prefix = os.path.expanduser('~/tmp')
        appName = str(self.applicationName())
        if not appName:
            appName = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        dirName = os.path.join(prefix, appName)
        if not os.path.isdir(dirName):
            os.makedirs(dirName)
        if name is None:
            name = appName + '.log'
        fileName = os.path.join(dirName, name)
        return fileName

    def get_command_line_parser(self):
        """Returns the :class:`optparse.OptionParser` used to parse the
        command line parameters.

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

    def setTaurusStyle(self, styleName):
        """Sets taurus application style to the given style name

        :param styleName: the new style name to be applied
        :type styleName: str"""
        import taurus.qt.qtgui.style
        taurus.qt.qtgui.style.setTaurusStyle(styleName)

    def basicConfig(self, log_file_name=None, maxBytes=1E7, backupCount=5,
                    with_gui_exc_handler=True):

        # prepare exception handler to report exceptions as error log messages
        # and to taurus message box (if with_gui is set)
        hook_to = None
        if with_gui_exc_handler:
            import taurus.qt.qtgui.dialog
            hook_to = taurus.qt.qtgui.dialog.TaurusExceptHookMessageBox()
        sys.excepthook = LogExceptHook(hook_to=hook_to)

        # create a file log handler
        try:
            if log_file_name is None:
                log_file_name = self.__buildLogFileName()
            f_h = logging.handlers.RotatingFileHandler(log_file_name,
                maxBytes=maxBytes, backupCount=backupCount)
            Logger.addRootLogHandler(f_h)
            if self._out is not None:
                self._out.std = sys.__stdout__
                self._out.addLogHandler(f_h)
            if self._out is not None:
                self._err.std = sys.__stderr__
                self._err.addLogHandler(f_h)
            self.info("Logs will be saved in %s", log_file_name)
        except:
            self.warning("'%s' could not be created. Logs will not be stored",
                         log_file_name)
            self.debug("Error description", exc_info=1)


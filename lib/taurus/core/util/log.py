#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This module contains a set of useful logging elements based on python's
:mod:`logging` system."""
from __future__ import print_function
from __future__ import absolute_import

from builtins import str
from builtins import object

import io
import os
import sys
import logging.handlers
import weakref
import warnings
import traceback
import inspect
import threading
import functools

from .object import Object
from .wrap import wraps
from .excepthook import BaseExceptHook

# ------------------------------------------------------------------------------
# TODO: substitute this ugly hack (below) by a more general mechanism
from collections import defaultdict


__all__ = ["LogIt", "TraceIt", "DebugIt", "InfoIt", "WarnIt", "ErrorIt",
           "CriticalIt", "MemoryLogHandler", "LogExceptHook", "Logger",
           "LogFilter",
           "_log", "trace", "debug", "info", "warning", "error", "fatal",
           "critical", "deprecated", "deprecation_decorator",
           "taurus4_deprecation"]

__docformat__ = "restructuredtext"


class _DeprecationCounter(defaultdict):

    def __init__(self):
        defaultdict.__init__(self, int)

    def getTotal(self):
        c = 0
        for v in self.values():
            c += v
        return c

    def pretty(self):
        from operator import itemgetter
        sorted_items = sorted(self.items(), key=itemgetter(1), reverse=True)
        ret = '\n'.join(['\t%d * "%s"' % (v, k) for k, v in sorted_items])
        return "< Deprecation Counts (%d):\n%s >" % (self.getTotal(), ret)

_DEPRECATION_COUNT = _DeprecationCounter()
# ------------------------------------------------------------------------------

TRACE = 5
logging.addLevelName(TRACE, "TRACE")

#
# _srcfile is used when walking the stack to check when we've got the first
# caller stack frame.
#
if hasattr(sys, 'frozen'):  # support for py2exe
    _srcfile = "logging%s__init__%s" % (os.sep, __file__[-4:])
elif __file__[-4:].lower() in ['.pyc', '.pyo']:
    _srcfile = __file__[:-4] + '.py'
else:
    _srcfile = __file__
_srcfile = os.path.normcase(_srcfile)

# next bit filched from 1.5.2's inspect.py


def currentframe():
    """Return the frame object for the caller's stack frame."""
    try:
        raise Exception
    except:
        return sys.exc_info()[2].tb_frame.f_back

if hasattr(sys, '_getframe'):
    currentframe = lambda: sys._getframe(3)
# done filching


class LogIt(object):
    """A function designed to be a decorator of any method of a Logger subclass.
    The idea is to log the entrance and exit of any decorated method of a Logger
    subclass.
    Example::

        from taurus.core.util.log import Logger, LogIt

        class Example(Logger):

            @LogIt(Logger.Debug)
            def go(self):
                print "Hello world "

    This will generate two log messages of Debug level, one before the function
    go is called and another when go finishes. Example output::

        MainThread     DEBUG    2010-11-15 15:36:11,440 Example: -> go
        Hello world of mine
        MainThread     DEBUG    2010-11-15 15:36:11,441 Example: <- go

    This decorator can receive two optional arguments **showargs** and **showret**
    which are set to False by default. Enabling them will had verbose infomation
    about the parameters and return value. The following example::

        from taurus.core.uti.log import Logger, LogIt

        class Example(Logger):

            @LogIt(Logger.Debug, showargs=True, showret=True)
            def go(self, msg):
                msg = "Hello world",msg
                print msg
                return msg

    would generate an output like::

        MainThread     DEBUG    2010-11-15 15:42:02,353 Example: -> go('of mine',)
        Hello world of mine
        MainThread     DEBUG    2010-11-15 15:42:02,353 Example: <- go = Hello world of mine

    .. note::
        it may happen that in these examples that the output of the method
        appears before or after the log messages. This is because log
        messages are, by default, written to the *stardard error* while the print
        message inside the go method outputs to the *standard ouput*. On many
        systems these two targets are not synchronized.
    """

    def __init__(self, level=logging.DEBUG, showargs=False, showret=False, col_limit=0):
        self._level = level
        self._showargs = showargs
        self._showret = showret
        self._col_limit = col_limit

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            f_self = args[0]
            if f_self.log_level > self._level:
                return f(*args, **kwargs)

            has_log = hasattr(f_self, "log")
            fname = f.__name__
            log_obj = f_self
            if not has_log:
                log_obj = logging.getLogger()
                try:
                    fname = "%s.%s" % (f_self.__class__.__name__, fname)
                except:
                    pass
            in_msg = "-> %s" % fname
            if self._showargs:
                if len(args) > 1:
                    in_msg += str(args[1:])
                if len(kwargs):
                    in_msg += str(kwargs)
            if self._col_limit and len(in_msg) > self._col_limit:
                in_msg = "%s [...]" % in_msg[:self._col_limit - 6]
            log_obj.log(self._level, in_msg)
            out_msg = "<-"
            try:
                ret = f(*args, **kwargs)
            except Exception as e:
                exc_info = sys.exc_info()
                out_msg += " (with %s) %s" % (e.__class__.__name__, fname)
                log_obj.log(self._level, out_msg, exc_info=exc_info)
                raise
            out_msg += " %s" % fname
            if not ret is None and self._showret:
                out_msg += " = %s" % str(ret)
            if self._col_limit and len(out_msg) > self._col_limit:
                out_msg = "%s [...]" % out_msg[:self._col_limit - 6]
            log_obj.log(self._level, out_msg)
            return ret
        return wrapper


class TraceIt(LogIt):
    """Specialization of LogIt for trace level messages.
    Example::

        from taurus.core.util.log import Logger, TraceIt
        class Example(Logger):

            @TraceIt()
            def go(self):
                print "Hello world"

    .. seealso:: :class:`LogIt`"""

    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=TRACE, showargs=showargs, showret=showret)


class DebugIt(LogIt):
    """Specialization of LogIt for debug level messages.
    Example::

        from taurus.core.util.log import Logger, DebugIt
        class Example(Logger):

            @DebugIt()
            def go(self):
                print "Hello world"

    .. seealso:: :class:`LogIt`"""

    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.DEBUG,
                       showargs=showargs, showret=showret)


class InfoIt(LogIt):
    """Specialization of LogIt for info level messages.
    Example::

        from taurus.core.util.log import Logger, InfoIt
        class Example(Logger):

            @InfoIt()
            def go(self):
                print "Hello world"

    .. seealso:: :class:`LogIt`"""

    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.INFO,
                       showargs=showargs, showret=showret)


class WarnIt(LogIt):
    """Specialization of LogIt for warn level messages.
    Example::

        from taurus.core.util.log import Logger, WarnIt
        class Example(Logger):

            @WarnIt()
            def go(self):
                print "Hello world"

    .. seealso:: :class:`LogIt`"""

    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.WARN,
                       showargs=showargs, showret=showret)


class ErrorIt(LogIt):
    """Specialization of LogIt for error level messages.
    Example::

        from taurus.core.util.log import Logger, ErrorIt
        class Example(Logger):

            @ErrorIt()
            def go(self):
                print "Hello world"

    .. seealso:: :class:`LogIt`"""

    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.ERROR,
                       showargs=showargs, showret=showret)


class CriticalIt(LogIt):
    """Specialization of LogIt for critical level messages.
    Example::

        from taurus.core.util.log import Logger, CriticalIt
        class Example(Logger):

            @CriticalIt()
            def go(self):
                print "Hello world"

    .. seealso:: :class:`LogIt`"""

    def __init__(self, showargs=False, showret=False):
        LogIt.__init__(self, level=logging.CRITICAL,
                       showargs=showargs, showret=showret)


class PrintIt(object):
    '''A decorator similar to TraceIt, DebugIt,... etc but which does not
    require the decorated class to inherit from Logger.
    It just uses print statements instead of logging. It is here just to be
    used as a replacement of those decorators if you cannot use them on a
    non-logger class.
    '''

    def __init__(self, showargs=False, showret=False):
        self._showargs = showargs
        self._showret = showret

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            fname = f.__name__
            in_msg = "-> %s" % fname
            if self._showargs:
                if len(args) > 1:
                    in_msg += str(args[1:])
                if len(kwargs):
                    in_msg += str(kwargs)
            print()
            print(in_msg)
            out_msg = "<-"
            try:
                ret = f(*args, **kwargs)
            except Exception as e:
                out_msg += " (with %s) %s" % (e.__class__.__name__, fname)
                print(out_msg)
                raise
            out_msg += " %s" % fname
            if not ret is None and self._showret:
                out_msg += " = %s" % str(ret)
            print(out_msg)
            print()
            return ret
        return wrapper


class MemoryLogHandler(list, logging.handlers.BufferingHandler):
    """An experimental log handler that stores temporary records in memory.
       When flushed it passes the records to another handler"""

    def __init__(self, capacity=1000):
        list.__init__(self)
        logging.handlers.BufferingHandler.__init__(self, capacity=capacity)
        self._handler_list_changed = False

    def shouldFlush(self, record):
        """Determines if the given record should trigger the flush

           :param record: (logging.LogRecord) a log record
           :return: (bool) wheter or not the handler should be flushed
        """
        return (len(self.buffer) >= self.capacity) or \
            (record.levelno >= Logger.getLogLevel()) or \
            self._handler_list_changed

    def flush(self):
        """Flushes this handler"""
        for record in self.buffer:
            for handler in self:
                handler.handle(record)
        self.buffer = []

    def close(self):
        """Closes this handler"""
        self.flush()
        del self[:]
        logging.handlers.BufferingHandler.close(self)


class LogExceptHook(BaseExceptHook):
    """A callable class that acts as an excepthook that logs the exception in
    the python logging system.

    :param hook_to: callable excepthook that will be called at the end of
                    this hook handling [default: None]
    :type hook_to: callable
    :param name: logger name [default: None meaning use class name]
    :type name: str
    :param level: log level [default: logging.ERROR]
    :type level: int"""

    def __init__(self, hook_to=None, name=None, level=logging.ERROR):
        BaseExceptHook.__init__(self, hook_to=hook_to)
        name = name or self.__class__.__name__
        self._level = level
        self._log = Logger(name=name)

    def report(self, *exc_info):
        text = "".join(traceback.format_exception(*exc_info))
        if text[-1] == '\n':
            text = text[:-1]
        self._log.log(self._level, "Unhandled exception:\n%s", text)


class Logger(Object):
    """The taurus logger class. All taurus pertinent classes should inherit
    directly or indirectly from this class if they need taurus logging
    facilities."""

    #: Internal usage
    root_inited = False

    #: Internal usage
    root_init_lock = threading.Lock()

    #: Critical message level (constant)
    Critical = logging.CRITICAL

    #: Fatal message level (constant)
    Fatal = logging.FATAL

    #: Error message level (constant)
    Error = logging.ERROR

    #: Warning message level (constant)
    Warning = logging.WARNING

    #: Info message level (constant)
    Info = logging.INFO

    #: Debug message level (constant)
    Debug = logging.DEBUG

    #: Trace message level (constant)
    Trace = TRACE

    #: Default log level (constant)
    DftLogLevel = Info

    #: Default log message format (constant)
    DftLogMessageFormat = '%(threadName)-14s %(levelname)-8s %(asctime)s %(name)s: %(message)s'

    #: Default log format (constant)
    DftLogFormat = logging.Formatter(DftLogMessageFormat)

    #: Current global log level
    log_level = DftLogLevel

    #: Default log message format
    log_format = DftLogFormat

    #: the main stream handler
    stream_handler = None

    def __init__(self, name='', parent=None, format=None):
        """The Logger constructor

        :param name: (str) the logger name (default is empty string)
        :param parent: (Logger) the parent logger or None if no parent exists (default is None)
        :param format: (str) the log message format or None to use the default log format (default is None)
        """
        self.call__init__(Object)

        if format:
            self.log_format = format
        Logger.initRoot()

        if name is None or len(name) == 0:
            name = self.__class__.__name__
        self.log_name = name
        if parent is not None:
            self.log_full_name = '%s.%s' % (parent.log_full_name, name)
        else:
            self.log_full_name = name

        self.log_obj = self._getLogger(self.log_full_name)
        self.log_handlers = []

        self.log_parent = None
        self.log_children = {}
        if parent is not None:
            self.log_parent = weakref.ref(parent)
            parent.addChild(self)

    def cleanUp(self):
        """The cleanUp. Default implementation does nothing
           Overwrite when necessary"""
        pass

    @classmethod
    def initRoot(cls):
        """Class method to initialize the root logger. Do **NOT** call this
           method directly in your code
        """
        if cls.root_inited:
            return cls._getLogger()

        try:
            cls.root_init_lock.acquire()
            root_logger = cls._getLogger()
            logging.addLevelName(cls.Trace, "TRACE")
            cls.stream_handler = logging.StreamHandler(sys.__stderr__)
            cls.stream_handler.setFormatter(cls.log_format)
            root_logger.addHandler(cls.stream_handler)

            console_log_level = os.environ.get("TAURUSLOGLEVEL", None)
            if console_log_level is not None:
                console_log_level = console_log_level.capitalize()
                if hasattr(cls, console_log_level):
                    cls.log_level = getattr(cls, console_log_level)
            root_logger.setLevel(cls.log_level)
            Logger.root_inited = True
        finally:
            cls.root_init_lock.release()
        return root_logger

    @classmethod
    def addRootLogHandler(cls, h):
        """Adds a new handler to the root logger

           :param h: (logging.Handler) the new log handler
        """
        h.setFormatter(cls.getLogFormat())
        cls.initRoot().addHandler(h)

    @classmethod
    def removeRootLogHandler(cls, h):
        """Removes the given handler from the root logger

           :param h: (logging.Handler) the handler to be removed
        """
        cls.initRoot().removeHandler(h)

    @classmethod
    def enableLogOutput(cls):
        """Enables the :class:`logging.StreamHandler` which dumps log records,
           by default, to the stderr.
        """
        cls.initRoot().addHandler(cls.stream_handler)

    @classmethod
    def disableLogOutput(cls):
        """Disables the :class:`logging.StreamHandler` which dumps log records,
           by default, to the stderr.
        """
        cls.initRoot().removeHandler(cls.stream_handler)

    @classmethod
    def setLogLevel(cls, level):
        """sets the new log level (the root log level)

           :param level: (int) the new log level
        """
        cls.log_level = level
        cls.initRoot().setLevel(level)

    @classmethod
    def getLogLevel(cls):
        """Retuns the current log level (the root log level)

           :return: (int) a number representing the log level
        """
        return cls.log_level

    @classmethod
    def setLogFormat(cls, format):
        """sets the new log message format

           :param level: (str) the new log message format
        """
        cls.log_format = logging.Formatter(format)
        root_logger = cls.initRoot()
        for h in root_logger.handlers:
            h.setFormatter(cls.log_format)

    @classmethod
    def getLogFormat(cls):
        """Retuns the current log message format (the root log format)

           :return: (str) the log message format
        """
        return cls.log_format

    @classmethod
    def resetLogLevel(cls):
        """Resets the log level (the root log level)"""
        cls.setLogLevel(cls.DftLogLevel)

    @classmethod
    def resetLogFormat(cls):
        """Resets the log message format (the root log format)"""
        cls.setLogFormat(cls.DftLogFormat)

    @classmethod
    def addLevelName(cls, level_no, level_name):
        """Registers a new log level

           :param level_no: (int) the level number
           :param level_name: (str) the corresponding name
        """
        logging.addLevelName(level_no, level_name)
        level_name = level_name.capitalize()
        if not hasattr(cls, level_name):
            setattr(cls, level_name, level_no)

    @classmethod
    def getRootLog(cls):
        """Retuns the root logger

           :return: (logging.Logger) the root logger
        """
        return cls.initRoot()

    @staticmethod
    def _getLogger(name=None):
        orig_logger_class = logging.getLoggerClass()
        try:
            logging.setLoggerClass(logging.Logger)
            ret = logging.getLogger(name)
            return ret
        finally:
            logging.setLoggerClass(orig_logger_class)

    @classmethod
    def getLogger(cls, name=None):
        cls.initRoot()
        return cls._getLogger(name=name)

    def getLogObj(self):
        """Returns the log object for this object

           :return: (logging.Logger) the log object
        """
        return self.log_obj

    def getParent(self):
        """Returns the log parent for this object or None if no parent exists

           :return: (logging.Logger or None) the log parent for this object
        """
        if self.log_parent is None:
            return None
        return self.log_parent()

    def getChildren(self):
        """Returns the log children for this object

           :return: (sequence<logging.Logger) the list of log children
        """
        children = []
        for _, ref in self.log_children.items():
            child = ref()
            if child is not None:
                children.append(child)
        return children

    def addChild(self, child):
        """Adds a new logging child

           :param child: (logging.Logger) the new child
        """
        if not self.log_children.get(id(child)):
            self.log_children[id(child)] = weakref.ref(child)

    def addLogHandler(self, handler):
        """Registers a new handler in this object's logger

           :param handler: (logging.Handler) the new handler to be added
        """
        self.log_obj.addHandler(handler)
        self.log_handlers.append(handler)

    def removeLogHandler(self, handler):
        """Removes the given handler from this object's logger

           :param handler: (logging.Handler) the handler to be removed
        """
        self.log_obj.removeHandler(handler)
        self.log_handlers.remove(handler)

    def copyLogHandlers(self, other):
        """Copies the log handlers of other object to this object

           :param other: (object) object which contains 'log_handlers'
        """
        for handler in other.log_handlers:
            self.addLogHandler(handler)

    def trace(self, msg, *args, **kw):
        """Record a trace message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.log`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        self.log_obj.log(self.Trace, msg, *args, **kw)

    def traceback(self, level=Trace, extended=True):
        """Log the usual traceback information, followed by a listing of all the
           local variables in each frame.

           :param level: (int) the log level assigned to the traceback record
           :param extended: (bool) if True, the log record message will have multiple lines

           :return: (str) The traceback string representation
        """
        out = traceback.format_exc()
        if extended:
            out += "\n"
            out += self._format_trace()

        self.log_obj.log(level, out)
        return out

    def stack(self, target=Trace):
        """Log the usual stack information, followed by a listing of all the
           local variables in each frame.

           :param target: (int) the log level assigned to the record

           :return: (str) The stack string representation
        """
        out = self._format_stack()
        self.log_obj.log(target, out)
        return out

    def _format_trace(self):
        return self._format_stack(inspect.trace)

    def _format_stack(self, stack_func=inspect.stack):
        line_count = 3
        stack = stack_func(line_count)
        out = ''
        for frame_record in stack:
            out += '\n\t' + 60 * '-'
            frame, filename, line, funcname, lines, index = frame_record
            #out += '\n\t    depth = %d' % frame[5]
            out += '\n\t filename = %s' % filename
            out += '\n\t function = %s' % funcname
            if lines is None:
                code = '<code could not be found>'
                out += '\n\t     line = [%d]: %s' % (line, code)
            else:
                lines, line_nb = [s.strip(' \n') for s in lines], len(lines)
                if line_nb >= 3:
                    out += '\n\t     line = [%d]: %s' % (line - 1, lines[0])
                    out += '\n\t  -> line = [%d]: %s' % (line, lines[1])
                    out += '\n\t     line = [%d]: %s' % (line + 1, lines[2])
                elif line_nb > 0:
                    out += '\n\t  -> line = [%d]: %s' % (line, lines[0])
            if frame:
                out += '\n\t   locals = '
                for k, v in frame.f_locals.items():
                    out += '\n\t\t%20s = ' % k
                    try:
                        cut = False
                        v = str(v)
                        i = v.find('\n')
                        if i == -1:
                            i = 80
                        else:
                            i = min(i, 80)
                            cut = True
                        if len(v) > 80:
                            cut = True
                        out += v[:i]
                        if cut:
                            out += '[...]'
                    except:
                        out += '<could not find suitable string representation>'
        return out

    def log(self, level, msg, *args, **kw):
        """Record a log message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.log`.

           :param level: (int) the record level
           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        self.log_obj.log(level, msg, *args, **kw)

    def debug(self, msg, *args, **kw):
        """Record a debug message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.debug`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        self.log_obj.debug(msg, *args, **kw)

    def info(self, msg, *args, **kw):
        """Record an info message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.info`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        self.log_obj.info(msg, *args, **kw)

    def warning(self, msg, *args, **kw):
        """Record a warning message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.warning`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        self.log_obj.warning(msg, *args, **kw)

    def deprecated(self, msg=None, dep=None, alt=None, rel=None, dbg_msg=None,
                   _callerinfo=None, **kw):
        """Record a deprecated warning message in this object's logger.
           If message is not passed, a estandard deprecation message is
           constructued using dep, alt, rel arguments.
           Also, an extra debug message can be recorded, followed by traceback
           info.

           :param msg: (str) the message to be recorded (if None passed, it will
                       be constructed using dep (and, optionally, alt and rel)
           :param dep: (str) name of deprecated feature (in case msg is None)
           :param alt: (str) name of alternative feature (in case msg is None)
           :param rel: (str) name of release from which the feature was
                       deprecated (in case msg is None)
           :param dbg_msg: (str) msg for debug (or None to log only the warning)
           :param _callerinfo: for internal use only. Do not use this argument.
           :param kw: any additional keyword arguments, are passed to
                     :meth:`logging.Logger.warning`
        """
        if msg is None:
            if dep is None:
                raise TypeError('deprecated takes either msg or dep argument')
            msg = '%s is deprecated' % dep
            if rel is not None:
                msg += ' since %s' % rel
            if alt is not None:
                msg += '. Use %s instead' % alt

        # count the number of calls (classified by msg)
        # TODO: substitute this ugly hack (below) by a more general mechanism
        _DEPRECATION_COUNT[msg] += 1
        # limit the output to 1 deprecation message of each type
        from taurus import tauruscustomsettings
        _MAX_DEPRECATIONS_LOGGED = getattr(tauruscustomsettings,
                                           '_MAX_DEPRECATIONS_LOGGED', None)
        if _MAX_DEPRECATIONS_LOGGED is not None:
            if _MAX_DEPRECATIONS_LOGGED < 0:
                self.stack(self.Warning)
                raise Exception(msg)
            if _DEPRECATION_COUNT[msg] > _MAX_DEPRECATIONS_LOGGED:
                return
        if _callerinfo is None:
            _callerinfo = self.log_obj.findCaller()
        filename, lineno = _callerinfo[:2]
        depr_msg = warnings.formatwarning(
            msg, DeprecationWarning, filename, lineno)
        self.log_obj.warning(depr_msg, **kw)
        if dbg_msg:
            self.debug(dbg_msg)
            self.stack()

    def error(self, msg, *args, **kw):
        """Record an error message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.error`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        self.log_obj.error(msg, *args, **kw)

    def fatal(self, msg, *args, **kw):
        """Record a fatal message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.fatal`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        self.log_obj.fatal(msg, *args, **kw)

    def critical(self, msg, *args, **kw):
        """Record a critical message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.critical`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        self.log_obj.critical(msg, *args, **kw)

    def exception(self, msg, *args):
        """Log a message with severity 'ERROR' on the root logger, with
           exception information.. Accepted *args* are the same as
           :meth:`logging.Logger.exception`.

           :param msg: (str) the message to be recorded
           :param args: list of arguments
        """
        self.log_obj.exception(msg, *args)

    def flushOutput(self):
        """Flushes the log output"""
        self.syncLog()

    def syncLog(self):
        """Synchronises the log output"""
        logger = self
        synced = []
        while logger is not None:
            for handler in logger.log_handlers:
                if handler in synced:
                    continue
                try:
                    sync = getattr(handler, 'sync')
                except:
                    continue
                sync()
                synced.append(handler)
            logger = logger.getParent()

    def getLogName(self):
        """Gets the log name for this object

           :return: (str) the log name
        """
        return self.log_name

    def getLogFullName(self):
        """Gets the full log name for this object

           :return: (str) the full log name
        """
        return self.log_full_name

    def changeLogName(self, name):
        """Change the log name for this object.

           :param name: (str) the new log name
        """
        self.log_name = name
        p = self.getParent()
        if p is not None:
            self.log_full_name = '%s.%s' % (p.log_full_name, name)
        else:
            self.log_full_name = name

        self.log_obj = logging.getLogger(self.log_full_name)
        for handler in self.log_handlers:
            self.log_obj.addHandler(handler)

        for child in self.getChildren():
            child.changeLogName(child.log_name)


class LogFilter(logging.Filter):
    """Experimental log filter"""

    def __init__(self, level):
        self.filter_level = level
        logging.Filter.__init__(self)

    def filter(self, record):
        ok = (record.levelno == self.filter_level)
        return ok


def __getrootlogger():
    return Logger.getLogger("TaurusRootLogger")

# cannot export log because upper package taurus.core.util imports this 'log'
# module and it would itself be overwritten by this log function


def _log(level, msg, *args, **kw):
    return __getrootlogger().log(level, msg, *args, **kw)


def trace(msg, *args, **kw):
    return _log(Logger.Trace, msg, *args, **kw)


def debug(msg, *args, **kw):
    return __getrootlogger().debug(msg, *args, **kw)


def info(msg, *args, **kw):
    return __getrootlogger().info(msg, *args, **kw)


def warning(msg, *args, **kw):
    return __getrootlogger().warning(msg, *args, **kw)


def error(msg, *args, **kw):
    return __getrootlogger().error(msg, *args, **kw)


def fatal(msg, *args, **kw):
    return __getrootlogger().fatal(msg, *args, **kw)


def critical(msg, *args, **kw):
    return __getrootlogger().critical(msg, *args, **kw)


def deprecated(*args, **kw):
    kw['_callerinfo'] = __getrootlogger().findCaller()
    return Logger("TaurusRootLogger").deprecated(*args, **kw)


def deprecation_decorator(func=None, alt=None, rel=None, dbg_msg=None):
    """decorator to mark methods as deprecated"""
    if func is None:
        return functools.partial(deprecation_decorator, alt=alt, rel=rel,
                                 dbg_msg=dbg_msg)

    def new_func(*args, **kwargs):
        deprecated(dep=func.__name__, alt=alt, rel=rel, dbg_msg=dbg_msg)
        return func(*args, **kwargs)

    doc = (func.__doc__ or '')
    doc += '\n\n.. deprecated:: %s\n' % (rel or '')
    if alt:
        doc += '   Use %s instead\n' % alt

    new_func.__name__ = func.__name__
    new_func.__doc__ = doc
    new_func.__dict__.update(func.__dict__)
    return new_func


taurus4_deprecation = functools.partial(deprecation_decorator, rel='4.0')


if __name__ == '__main__':

    @taurus4_deprecation(alt='bar')
    def foo(x):
        """Does this and that and also:

        - baz
        - zab
        """

    print(foo.__doc__)

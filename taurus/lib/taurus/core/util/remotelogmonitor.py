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

"""Useful module for remote logging"""

from __future__ import print_function
from __future__ import with_statement

__all__ = ["LogRecordStreamHandler", "LogRecordSocketReceiver", "log"]

import time
import socket
import pickle
import logging
import logging.handlers
import struct
import weakref

try:
    import socketserver
except:
    import SocketServer as socketserver


class LogRecordStreamHandler(socketserver.StreamRequestHandler):

    def handle(self):
        try:
            return self._handle()
        except:
            pass

    def _handle(self):
        self._stop = stop = 0
        self.hostName = self.server.hostName
        self.server.registerHandler(self)
        while not stop:
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.connection.recv(slen - len(chunk))
            obj = self.unPickle(chunk)
            record = self.makeLogRecord(obj)
            self.handleLogRecord(record)
            stop = self._stop
        
    def unPickle(self, data):
        return pickle.loads(data)

    def makeLogRecord(self, obj):
        record = logging.makeLogRecord(obj)
        if not hasattr(record, 'hostName'):
            record.hostName = self.hostName
        return record

    def handleLogRecord(self, record):
        logger = self.server.data.get("logger")
        if logger is None:
            logger = logging.getLogger(record.name)
        if not logger.isEnabledFor(record.levelno):
            return
        logger.handle(record)

    def stop(self):
        self._stop = 1


class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    """
    Simple TCP socket-based logging receiver suitable for testing.
    """

    allow_reuse_address = 1
    daemon_threads = True

    def __init__(self, host='localhost',
                 port=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
                 handler=LogRecordStreamHandler, **kwargs):
        socketserver.ThreadingTCPServer.__init__(self, (host, port), handler)
        self.hostName = socket.gethostbyaddr(host)[0]
        self.port = port
        self._stop = 0
        self._stopped = 0
        self.timeout = 1
        self.data = kwargs
        self.__handlers = []

    def registerHandler(self, handler):
        if handler is not None:
            self.__handlers.append(weakref.ref(handler))

    def unregisterHandler(self, handler):
        try:
            self.__handlers.remove(handler)
        except ValueError:
            pass

    def serve_until_stopped(self):
        import select
        stop = 0
        while not stop:
            rd, wr, ex = select.select([self.socket.fileno()],
                                       [], [],
                                       self.timeout)
            if rd:
                self.handle_request()
            stop = self._stop
        self._stopped = 1
    
    def stop(self):
        self._stop = True
        while not self._stopped:
            time.sleep(0.1)
        for handler in self.__handlers:
            h = handler()
            if h is not None:
                h.stop()
                h.finish()
                self.close_request(h.connection)
        self.socket.close()


class LogNameFilter(logging.Filter):

    def __init__(self, name=None):
        self.name = name

    def filter(self, record):
        name = self.name
        if name is None:
            return True
        return record.name == name


def log(host, port, name=None, level=None):
    local_logger_name = "RemoteLogger.%s.%d" % (host, port)
    local_logger = logging.getLogger(local_logger_name)

    if name is not None:
        local_logger.addFilter(LogNameFilter(name=name))

    if level is not None:
        local_logger.setLevel(level)

    tcpserver = LogRecordSocketReceiver(host=host, port=port,
                                        logger=local_logger)
    msg = "logging for '%s' on port %d" % (host, port)
    if name is not None:
        msg += " for " + name
    print("Start", msg)

    try:
        tcpserver.serve_until_stopped()
    except KeyboardInterrupt:
        print("\nCancelled", msg)


def main(argv=None):
    import optparse
    import socket

    import taurus.core.util.log

    taurus.setLogLevel(taurus.Trace)

    dft_port = logging.handlers.DEFAULT_TCP_LOGGING_PORT

    host = socket.gethostname()

    help_port = "port where log server is running [default: %d]" % dft_port
    help_name = "filter specific log object [default: None, meaning don't " \
                "filter]"
    help_level = "filter specific log level." \
                 "Allowed values are (case insensitive): critical, "\
                 "error, warning/warn, info, debug, trace [default: debug]."

    parser = optparse.OptionParser()
    parser.add_option("--log-port", dest="log_port", default=dft_port,
                      type="int", help=help_port)
    parser.add_option("--log-name", dest="log_name", default=None,
                      type="string", help=help_name)
    parser.add_option("--log-level", dest="log_level", default="debug",
                      type="string", help=help_level)

    if argv is None:
        import sys
        argv = sys.argv

    options, args = parser.parse_args(args=argv)

    port, name = options.log_port, options.log_name
    level_str = options.log_level.capitalize()

    level = None
    if hasattr(taurus, level_str):
        level = getattr(taurus, level_str)

    log(host, port, name=name, level=level)

if __name__ == '__main__':
    main()

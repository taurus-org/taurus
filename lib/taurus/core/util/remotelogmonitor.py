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

"""Useful module for remote logging"""

from __future__ import print_function
from __future__ import with_statement

from future import standard_library
standard_library.install_aliases()

import time
import socket
import pickle
import logging
import logging.handlers
import struct
import weakref
import click

import socketserver

import taurus.cli.common


_all__ = ["LogRecordStreamHandler", "LogRecordSocketReceiver", "log"]


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


@click.command('logmon')
@click.option(
    '--port', 'port', type=int,
    default=logging.handlers.DEFAULT_TCP_LOGGING_PORT,
    show_default=True,
    help='Port where log server is running',
)
@click.option(
    '--log-name', 'log_name',
    default=None,
    help='Filter specific log object',
)
@taurus.cli.common.log_level
def logmon_cmd(port, log_name, log_level):
    """Show the console-based Taurus Remote Log Monitor"""
    import taurus
    host = socket.gethostname()
    level = getattr(taurus, log_level.capitalize(), taurus.Trace)

    log(host=host, port=port, name=log_name, level=level)


if __name__ == '__main__':
    logmon_cmd()

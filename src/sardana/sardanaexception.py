#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""This module is part of the Python Sardana libray. It defines the base classes
for sardana exceptions"""

from __future__ import absolute_import

__all__ = [ "AbortException", "SardanaException", "SardanaExceptionList",
           "UnknownCode", "UnknownLibrary", "LibraryError",
           "format_exception_only", "format_exception_only_str"]

__docformat__ = 'restructuredtext'

import sys
import traceback


def format_exception_only(etype, value):
    msg = traceback.format_exception_only(etype, value)
    if msg[-1].endswith("\n"):
        msg[-1] = msg[-1][:-1]
    return msg

def format_exception_only_str(etype, value):
    return "".join(format_exception_only(etype, value))

class AbortException(Exception):
    pass


class SardanaException(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)
        if args:
            a1 = args[0]
            if isinstance(a1, dict):
                self.msg = a1.get("message", a1.get("msg", None))
                self.traceback = a1.get("traceback", a1.get("tb", None))
                self.type = a1.get("type", self.__class__.__name__)
            else:
                self.msg = str(a1)
                self.traceback = None
                self.type = self.__class__.__name__
        else:
            exc_info = kwargs.get("exc_info")
            if exc_info is None:
                self.msg = "Unknown sardana exception"
            else:
                msg = format_exception_only_str(*exc_info[:2])
                self.msg = msg
            self.traceback = None
            self.type = self.__class__.__name__
        if 'exc_info' in kwargs:
            self.exc_info = kwargs['exc_info']
        else:
            self.exc_info = kwargs.get('exc_info', sys.exc_info())

    def __str__(self):
        return self.msg

    def __repr__(self):
        return "%s: %s" % (self.type, self.msg)


class SardanaExceptionList(SardanaException):
    def __init__(self, *args):
        SardanaException.__init__(self, *args)
        self.exceptions = args[0]


class UnknownCode(SardanaException):
    pass


class UnknownLibrary(SardanaException):
    pass


class LibraryError(SardanaException):
    pass


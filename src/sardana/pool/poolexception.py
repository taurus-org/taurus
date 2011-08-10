#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
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

"""This module is part of the Python Pool libray. It defines the base classes
for pool exceptions"""

__all__ = [ "AbortException", "PoolException", "PoolExceptionList", 
           "UnknownController", "ControllerOfflineException"]

__docformat__ = 'restructuredtext'

class AbortException(Exception):
    pass

class PoolException(Exception):
    
    def __init__(self, *args):
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

    def __str__(self):
        return "%s: %s" % (self.type, self.msg)


class PoolExceptionList(PoolException):
    def __init__(self, *args):
        PoolException.__init__(self, *args)
        self.exceptions = args[0]


class UnknownController(PoolException):
    pass


class UnknownLib(PoolException):
    pass


class LibError(Exception):
    pass

class ControllerOfflineException(Exception):
    """An exception to be thrown when an operation is requested on a controller
    which is offline"""
    pass
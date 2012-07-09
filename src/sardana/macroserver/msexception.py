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

"""This module contains the class definition for the MacroServer environment
manager"""

__all__ = ["MacroServerException", "MacroServerExceptionList", "MissingEnv",
           "UnknownEnv", "UnknownMacro", "UnknownMacroLibrary",
           "MacroWrongParameterType", "LibraryError",
           "InterruptException", "StopException", "AbortException",
           "InputCancelled"]

__docformat__ = 'restructuredtext'

from taurus.core.tango.sardana.pool import InterruptException, \
    StopException, AbortException

from sardana.sardanaexception import SardanaException, SardanaExceptionList, \
    UnknownCode, UnknownLibrary, LibraryError


class MacroServerException(SardanaException):
    pass


class MacroServerExceptionList(SardanaExceptionList):
    pass


class MissingEnv(MacroServerException):
    pass


class UnknownEnv(MacroServerException):
    pass


class UnknownMacro(UnknownCode):
    pass


class UnknownMacroLibrary(UnknownLibrary):
    pass


class MacroWrongParameterType(MacroServerException):
    pass
    
class InputCancelled(MacroServerException):
    pass

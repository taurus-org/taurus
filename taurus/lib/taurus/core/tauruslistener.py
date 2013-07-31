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

"""This module contains the taurus base listeners classes"""

__all__ = ["TaurusListener", "TaurusExceptionListener"]

__docformat__ = "restructuredtext"

from .util.log import Logger

class TaurusListener(Logger):
    """ TaurusListener Interface"""
    
    def __init__(self, name, parent=None):
        self.call__init__(Logger, name, parent)
    
    def eventReceived(self, src, type, evt_value):
        """ Method to implement the event notification"""
        pass

    def attributeList(self):
        """ Method to return the attributes of the widget"""
        return []


class TaurusExceptionListener(object):
    """Class for handling ConnectionFailed, DevFailed and TaurusException exceptions."""

    def connectionFailed(self, ex):
        self._printException(ex)

    def devFailed(self, exception):
        self._printException(self)

    def exceptionReceived(self, exception):
        import PyTango
        if isinstance(exception, PyTango.ConnectionFailed):
            self.connectionFailed(exception)

        elif isinstance(exception, PyTango.DevFailed):
            self.devFailed(exception)

        else:
            self._printException(exception)

    def _printException(self, exception):
        print self.__class__.__name__, "received", exception.__class__.__name__, str(exception)


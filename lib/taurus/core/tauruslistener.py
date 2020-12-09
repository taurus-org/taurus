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

"""This module contains the taurus base listeners classes"""

from __future__ import print_function
from builtins import object
from .util.log import Logger


__all__ = ["TaurusListener", "TaurusExceptionListener"]

__docformat__ = "restructuredtext"


class TaurusListener(Logger):
    """ TaurusListener Interface"""

    def __init__(self, name='', parent=None):
        self.call__init__(Logger, name, parent)

    def eventReceived(self, src, type, evt_value):
        """ Method to implement the event notification"""
        pass

    def attributeList(self):
        """ Method to return the attributes of the widget"""
        return []


class TaurusExceptionListener(object):
    """Class for handling ConnectionFailed, DevFailed and TaurusException exceptions."""

    def connectionFailed(self, exception):
        msg = 'Deprecation warning: please note that the "connectionFailed" ' +\
              'method is deprecated. Scheme-specific exceptions should be ' +\
              'implemented in each model and be transformed into taurus ' +\
              'exceptions according Sep3 specifications'
        self.info(msg)
        self._printException(exception)

    def devFailed(self, exception):
        msg = 'Deprecation warning: please note that the "devFailed" ' +\
              'method is deprecated. Scheme-specific exceptions should be ' +\
              'implemented in each model and be transformed into taurus ' +\
              'exception according Sep3 specifications'
        self.info(msg)
        self._printException(exception)

    def exceptionReceived(self, exception):
        self._printException(exception)

    def _printException(self, exception):
        print(self.__class__.__name__, "received", exception.__class__.__name__, str(exception))

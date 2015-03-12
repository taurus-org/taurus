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


__all__ = ["MacroServerManager"]

__docformat__ = 'restructuredtext'

import weakref

from taurus.core import ManagerState
from taurus.core.util.log import Logger


class MacroServerManager(Logger):
    """Base Class for macro server managers"""

    def __init__(self, macro_server):
        name = macro_server.name + "." + self.__class__.__name__
        self._state = ManagerState.UNINITIALIZED
        self._macro_server = weakref.ref(macro_server)
        self.call__init__(Logger, name)
        self.reInit()

    def reInit(self):
        self._state = ManagerState.INITED

    def cleanUp(self):
        self._state = ManagerState.CLEANED

    @property
    def macro_server(self):
        return self._macro_server()

    def is_initialized(self):
        return self._state == ManagerState.INITED

    def is_cleaned(self):
        return self._state == ManagerState.CLEANED

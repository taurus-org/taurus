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

"""This module contains the base taurus operation classes"""

__all__ = ["TaurusOperation", "WriteAttrOperation"]

__docformat__ = "restructuredtext"

from .util.log import Logger


class TaurusOperation(Logger):

    def __init__(self, name='TaurusOperation', parent=None, callbacks=None):
        self.call__init__(Logger, name, parent)
        if callbacks is None:
            callbacks = []
        self._callbacks = callbacks
        self._dangerMessage = None
        self._isDangerous = False

    def getDevice(self):
        pass

    def setCallbacks(self, callbacks):
        self._callbacks = callbacks

    def getCallbacks(self):
        return self._callbacks

    def execute(self):
        for f in self._callbacks:
            f(operation=self)

    def isDangerous(self):
        return self._isDangerous

    def setDangerMessage(self, dangerMessage=None):
        '''if dangerMessage is None, the operation is considered safe'''
        self._dangerMessage = dangerMessage
        self._isDangerous = dangerMessage is not None

    def getDangerMessage(self):
        return self._dangerMessage

    def resetDangerMessage(self):
        self.setDangerMessage(None)


class WriteAttrOperation(TaurusOperation):

    def __init__(self, attr, value, callbacks=None):
        self.call__init__(TaurusOperation, 'WriteAttrOperation',
                          attr, callbacks=callbacks)
        self.attr = attr
        self.value = value

    def execute(self):
        self.attr.write(self.value)
        TaurusOperation.execute(self)

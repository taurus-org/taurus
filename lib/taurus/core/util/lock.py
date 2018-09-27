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

"""This module defines a *slow* lock class that provides additional debugging
information"""

from builtins import object
import threading
import logging

__all__ = ["TaurusLock"]

__docformat__ = 'restructuredtext'

_VERBOSE = False


def TaurusLock(verbose=None, name=None, lock=None):
    if verbose is None:
        verbose = _VERBOSE
    if verbose:
        return _TaurusLock(name=name, lock=lock)
    if lock is None:
        return threading.Lock()
    return lock


class _TaurusLock(object):
    """A sardana lock"""

    def __init__(self, name=None, lock=None, level=logging.DEBUG):
        name = name or self.__class__.__name__
        self.__name = name
        self.__logger = logging.getLogger(name=name)
        self.__level = level
        if lock is None:
            lock = threading.Lock()
        self.__block = lock
        self.__owner = None

    def __repr__(self):
        owner = self.__owner
        if owner is not None:
            owner = owner.name
        return "<%s owner=%r>" % (self.__name, owner)

    def owner_name(self):
        owner = self.__owner
        if owner is not None:
            return owner.name

    def _note(self, msg, *args):
        self.__logger.log(self.__level, msg, *args)

    def acquire(self, blocking=1):
        if __debug__:
            self._note("[START] acquire(%s) [owner=%s]", blocking,
                       self.owner_name())
        rc = self.__block.acquire(blocking)
        me = threading.current_thread()
        if rc:
            self.__owner = me
            state = "success"
        else:
            state = "failure"
        if __debug__:
            self._note("[ END ] acquire(%s) %s [owner=%s]", blocking, state,
                       self.owner_name())
        return rc

    __enter__ = acquire

    def release(self):
        if __debug__:
            self._note("[START] release() [owner=%s]", self.owner_name())
        self.__block.release()
        self.__owner = None
        if __debug__:
            self._note("[ END ] release() [owner=%s]", self.owner_name())

    def __exit__(self, t, v, tb):
        self.release()

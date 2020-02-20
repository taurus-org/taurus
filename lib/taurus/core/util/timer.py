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

"""This module contains a :class:`Timer` class"""

__all__ = ["Timer"]

__docformat__ = "restructuredtext"

import time
import threading

from .log import Logger


class Timer(Logger):
    """
    Timer Object.

    Interval in seconds (The argument may be a floating point number for
    subsecond precision).
    If strict_timing is True, the timer will try to compensate for drifting
    due to the time it takes to execute function in each loop.
    """

    def __init__(self, interval, function, parent, strict_timing=True,
                 *args, **kwargs):
        Logger.__init__(self, 'Timer on ' + function.__name__, parent)
        self.__lock = threading.Lock()
        self.__interval = interval
        self.__function = function
        self.__args = args
        self.__kwargs = kwargs
        self.__loop = False
        self.__alive = False
        self.__start_nb = 0
        self.__thread = None
        self.__strict_timing = strict_timing

    def start(self):
        """ Start Timer Object """
        self.__lock.acquire()
        try:
            if not self.__alive:
                self.debug("Timer::start()")
                self.__loop = True
                self.__alive = True
                self.__start_nb += 1
                thread_name = "TimerLoop %d" % self.__start_nb
                self.__thread = threading.Thread(
                    target=self.__run, name=thread_name)
                self.__thread.setDaemon(True)
                self.__thread.start()
        finally:
            self.__lock.release()

    def stop(self, sync=False):
        """ Stop Timer Object """
        self.debug("Timer::stop()")
        self.__lock.acquire()
        self.__loop = False
        self.__lock.release()
        if sync and self.__thread is not None:
            self.__thread.join()

    def __run(self):
        """ Private Thread Function """
        self.debug("Timer thread starting")
        next_time = time.time() + self.__interval
        while self.__loop:
            self.__function(*self.__args, **self.__kwargs)
            nap = self.__interval
            if self.__strict_timing:
                curr_time = time.time()
                nap = max(0, next_time - curr_time)
                if curr_time > next_time:
                    self.warning("loop function took more than loop interval (%ss)",
                                 self.__interval)
            next_time += self.__interval
            time.sleep(nap)
        self.__alive = False
        self.debug("Timer thread ending")

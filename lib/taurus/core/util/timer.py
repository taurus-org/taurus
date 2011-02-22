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

"""This module contains a :class:`Timer` class"""

__all__ = ["Timer"]

__docformat__ = "restructuredtext"

import threading
import time
import log

class Timer(log.Logger):

    def __init__(self, interval, function, parent, *args, **kwargs):
        """Create Timer Object. Interval in seconds (The argument may be a 
        floating point number for subsecond precision)"""
        
        self.call__init__(log.Logger, 'Timer on ' + function.__name__, parent)
        self.__lock = threading.Lock()
        self.__interval = interval
        self.__function = function
        self.__args = args
        self.__kwargs = kwargs
        self.__loop = False
        self.__alive = False
        self.__start_nb = 0
        self.__thread = None
        
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
                self.__thread = threading.Thread(target=self.__run, name = thread_name)
                self.__thread.setDaemon(True)
                self.__thread.start()
        finally:
            self.__lock.release()
    
    def stop(self):
        """ Stop Timer Object """
        self.debug("Timer::stop()")
        self.__lock.acquire()
        self.__loop = False
        self.__lock.release()
    
    def __run(self):
        """ Private Thread Function """
        self.debug("Timer thread starting")
        while self.__loop:
            self.__function(*self.__args, **self.__kwargs)
            time.sleep(self.__interval)
        self.__alive = False
        self.debug("Timer thread ending")
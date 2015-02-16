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

"""This module contains the function to access sardana thread pool"""

from __future__ import with_statement
from __future__ import absolute_import

__all__ = ["get_thread_pool"]

__docformat__ = 'restructuredtext'

import threading

from taurus.core.util.threadpool import ThreadPool

__thread_pool_lock = threading.Lock()
__thread_pool = None


def get_thread_pool():
    """Returns the global pool of threads for Sardana
    
    :return: the global pool of threads object
    :rtype: taurus.core.util.ThreadPool"""

    global __thread_pool
    global __thread_pool_lock
    with __thread_pool_lock:
        if __thread_pool is None:
            __thread_pool = ThreadPool(name="SardanaTP", Psize=10)
        return __thread_pool

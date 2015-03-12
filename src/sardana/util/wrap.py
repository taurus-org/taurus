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

""""""

__all__ = ["wraps", "wrapped", "is_wrapping", "is_wrapped"]

import weakref
from functools import wraps as _wraps

__WRAPPED = "__wrapped__"
__WRAPPER = "__wrapper__"

def wraps(wrapped, *args, **kwargs):
    """A wrap decorator which stores in the returned function a reference to
    the wrapped function (in member '__wrapped__')"""
    wrapper = _wraps(wrapped, *args, **kwargs)
    setattr(wrapper, __WRAPPED, weakref.ref(wrapped))
    setattr(wrapped, __WRAPPER, weakref.ref(wrapper))
    return wrapper

def is_wrapping(wrapper):
    """Determines if the given callable is a wrapper for another callable"""
    return hasattr(wrapper, __WRAPPED)

def is_wrapped(wrapped):
    """Determines if the given callable is being wrapped by another callable"""
    return hasattr(wrapped, __WRAPPER)

def wrapped(wrapper, recursive=True):
    """Returns the wrapped function around the given wrapper. If the given
    callable is not "wrapping" any function, the wrapper itself is returned"""
    if is_wrapping(wrapper):
        _wrapped = wrapper.__wrapped__()
    else:
        return wrapper

    if recursive:
        return wrapped(_wrapped)
    return _wrapped


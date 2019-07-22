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

"""
Provides a decorator to decorate decorators so that they can be used both
with and without args
"""

__all__ = ["decorator"]

__docformat__ = "restructuredtext"

import functools
import inspect


def decorator(func):
    """
    Allow to use decorator either with arguments or not. Example::

        @decorator
        def apply(func, *args, **kw):
            return func(*args, **kw)

        @decorator
        class apply:
            def __init__(self, *args, **kw):
                self.args = args
                self.kw   = kw

            def __call__(self, func):
                return func(*self.args, **self.kw)

        #
        # Usage in both cases:
        #
        @apply
        def test():
            return 'test'

        assert test == 'test'

        @apply(2, 3)
        def test(a, b):
            return a + b

        assert test == 5

    """

    def isFuncArg(*args, **kw):
        return len(args) == 1 and len(kw) == 0 and (
            inspect.isfunction(args[0]) or isinstance(args[0], type))

    if isinstance(func, type):
        def class_wrapper(*args, **kw):
            if isFuncArg(*args, **kw):
                return func()(*args, **kw)  # create class before usage
            return func(*args, **kw)
        class_wrapper.__name__ = func.__name__
        class_wrapper.__module__ = func.__module__
        return class_wrapper

    @functools.wraps(func)
    def func_wrapper(*args, **kw):
        if isFuncArg(*args, **kw):
            return func(*args, **kw)

        def functor(userFunc):
            return func(userFunc, *args, **kw)

        return functor

    return func_wrapper

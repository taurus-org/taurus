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

"""This module contains a decorator to simplify the use of property."""
from __future__ import print_function
from __future__ import absolute_import


__all__ = ["propertx"]

__docformat__ = "restructuredtext"


def propertx(fct):
    '''
        Decorator to simplify the use of property.
        Like @property for attrs who need more than a getter.
        For getter only property use @property.

        adapted from http://code.activestate.com/recipes/502243/
    '''
    arg = [None, None, None, None]
    for i, f in enumerate(fct()):
        arg[i] = f
    if not arg[3]:
        arg[3] = fct.__doc__
    return property(*arg)

if __name__ == '__main__':

    from .log import Logger

    class example(object, Logger):

        def __init__(self):
            Logger.__init__(self, "example")
            self._a = 100
            self.bar = "why"

        @propertx
        def bar():
            # BAR doc
            def get(self):
                print("\tgetting", self._a)
                return self._a

            def set(self, val):
                print("\tsetting", val)
                self._a = val
            return get, set

    foo = example()
    print(foo.bar)
    # foo.bar='egg'
    # print foo.bar

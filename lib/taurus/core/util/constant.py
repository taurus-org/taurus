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
This is a variation on "Constants in Python" by Alex Martelli, from which the
solution idea was borrowed, and enhanced according suggestions of Zoran Isailovski.

In Python, any variable can be re-bound at will -- and modules don't let you
define special methods such as an instance's __setattr__ to stop attribute
re-binding. Easy solution (in Python 2.1 and up): use an instance as "module"...

In Python 2.1 and up, no check is made any more to force entries in sys.modules
to be actually module objects. You can install an instance object there and take
advantage of its attribute-access special methods (e.g., as in this snippet, to
prevent type rebindings.

Usage::

  import consttype
  consttype.magic = 23    # Bind an attribute to a type ONCE
  consttype.magic = 88    # Re-bind it to a same type again
  consttype.magic = "one" # But NOT re-bind it to another type: this raises consttype._ConstError
  del consttype.magic     # Remove an named attribute
  consttype.__del__()     # Remove all attributes
"""

from builtins import object

__docformat__ = "restructuredtext"


class _consttype(object):

    class _ConstTypeError(TypeError):
        pass

    def __repr__(self):
        return "Constant type definitions."

    def __setattr__(self, name, value):
        v = self.__dict__.get(name, value)
        if type(v) is not type(value):
            raise self._ConstTypeError("Can't rebind %s to %s" % (
                type(v), type(value)))
        self.__dict__[name] = value

    def __del__(self):
        self.__dict__.clear()


if __name__ == '__main__':
    import sys
    sys.modules[__name__] = _consttype()

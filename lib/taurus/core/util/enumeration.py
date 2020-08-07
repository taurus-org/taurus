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

"""Enumeration module.
In C, enums allow you to declare a bunch of constants with unique values,
without necessarily specifying the actual values (except in cases where you
need to). Python has an accepted idiom that's fine for very small numbers of
constants (A, B, C, D = range(4)) but it doesn't scale well to large numbers,
and it doesn't allow you to specify values for some constants while leaving
others unspecified. This approach does those things, while verifying that all
values (specified and unspecified) are unique. Enum values then are attributes
of an Enumeration class (Volkswagen.BEETLE, Volkswagen.PASSAT, etc.)."""

from builtins import int
from builtins import str
from builtins import object
from future.utils import string_types


__all__ = ["EnumException", "Enumeration"]
__docformat__ = "restructuredtext"


class EnumException(Exception):
    """Exception thrown by :class:`Enumeration` when trying to declare an
    invalid enumeration."""
    pass


class Enumeration(object):
    """ Enumeration class intended to provide the 'enum' feature present in many
    programming languages.
    The elements of the enumeration can be accessed in an "object member way" or
    as elements of a dictionary.
    Usage::

        from taurus.core.util.enumeration import Enumeration

        Volkswagen = Enumeration("Volkswagen",
            ["JETTA",
             "RABBIT",
             "BEETLE",
             ("THING", 400),
             "PASSAT",
             "GOLF",
             ("CABRIO", 700),
             "EURO_VAN",
             "CLASSIC_BEETLE",
             "CLASSIC_VAN"
             ])

    In the command line::

        >>> my_car = Volkswagen.BEETLE
        >>> homer_car = Volkswagen.PASSAT

        >>> print Volkswagen.BEETLE
        2

        >>> print Volkswagen['BEETLE']
        2

        >>>print Volkswagen.whatis(homer_car)
        'PASSAT'
    """

    def __init__(self, name, enumList, flaggable=False, no_doc=False):
        self._name = name
        lookup = {}
        reverseLookup = {}
        uniqueNames = set()
        self._flaggable = flaggable
        self._uniqueValues = uniqueValues = set()
        self._uniqueId = 0
        for x in enumList:
            if isinstance(x, tuple):
                if flaggable:
                    raise EnumException(
                        "flagable enum does not accept tuple items")
                x, i = x
                if not isinstance(x, string_types):
                    raise EnumException("enum name is not a string: " + str(x))
                if not isinstance(i, int):
                    raise EnumException(
                        "enum value is not an integer: " + str(i))
                if x in uniqueNames:
                    raise EnumException("enum name is not unique: " + str(x))
                if i in uniqueValues:
                    raise EnumException(
                        "enum value is not unique for " + str(x))
                uniqueNames.add(x)
                uniqueValues.add(i)
                lookup[x] = i
                reverseLookup[i] = x
        for x in enumList:
            if not isinstance(x, tuple):
                if not isinstance(x, string_types):
                    raise EnumException("enum name is not a string: " + str(x))
                if x in uniqueNames:
                    raise EnumException("enum name is not unique: " + str(x))
                uniqueNames.add(x)
                i = self._generateUniqueId()
                uniqueValues.add(i)
                lookup[x] = i
                reverseLookup[i] = x
        self.lookup = lookup
        self.reverseLookup = reverseLookup
        if not no_doc:
            self.__doc_enum()

    def __call__(self, i):
        # TODO: Dummy implementation to simulate Python Enum behaviour.
        # It is not a complete replacement because although we can use
        # Enumeration as Callable, it still return an int instead of an
        # Enumeration member.
        return self.lookup[self.whatis(i)]

    def __len__(self):
        return len(self.lookup)

    def _generateUniqueId(self):
        if self._flaggable:
            n = 2 ** self._uniqueId
        else:
            while self._uniqueId in self._uniqueValues:
                self._uniqueId += 1
            n = self._uniqueId
        self._uniqueId += 1
        return n

    def __contains__(self, i):
        if isinstance(i, int):
            return i in self.reverseLookup
        elif isinstance(i, string_types):
            return i in self.lookup

    def __getitem__(self, i):
        if isinstance(i, int):
            return self.whatis(i)
        elif isinstance(i, string_types):
            return self.lookup[i]

    def __getattr__(self, attr):
        if attr not in self:
            raise AttributeError
        return self.lookup[attr]

    def __doc_enum(self):
        rl = self.reverseLookup
        keys = list(rl)
        keys.sort()
        values = "\n".join(["    - {0} ({1})".format(rl[k], k) for k in keys])
        self.__doc__ = self._name + " enumeration. " + \
            "Possible values are:\n\n" + values

    def __str__(self):
        rl = self.reverseLookup
        keys = list(rl)
        keys.sort()
        values = ", ".join([rl[k] for k in keys])
        return self._name + "(" + values + ")"

    def __repr__(self):
        rl = self.reverseLookup
        keys = list(rl)
        keys.sort()
        values = [rl[k] for k in keys]
        return "Enumeration('" + self._name + "', " + str(values) + ")"

    def has_key(self, key):
        """Determines if the enumeration contains the given key
        :param key: the key
        :type  key: str
        :return: True if the key is in the enumeration or False otherswise
        :rtype: bool"""
        return key in self.lookup

    def keys(self):
        """Returns an iterable containning the valid enumeration keys
        :return: an interable containning the valid enumeration keys
        :rtype: iter<str>"""
        return list(self.lookup.keys())

    def whatis(self, value):
        """Returns a string representation of the value in the enumeration.
        :param value: a valid enumeration element
        :return: a string representation of the given enumeration element
        :rtype: str"""
        return self.reverseLookup[value]

    def get(self, i):
        """Returns the element for the given key/value"""
        return self[i]

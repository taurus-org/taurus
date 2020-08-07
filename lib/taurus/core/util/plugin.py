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
Utilities for plugin loading and selection
"""

__all__ = ["selectEntryPoints", "EntryPointAlike"]

import re
import pkg_resources
try:
    from re import fullmatch
except ImportError:  # TODO: remove this when dropping support of py2
    def fullmatch(regex, string, flags=0):
        """
        Emulate python-3.4 re.fullmatch()...  mostly
        See: https://stackoverflow.com/a/30212414
        """
        m = re.match(regex, string, flags=flags)
        if m and m.span()[1] == len(string):
            return m


class EntryPointAlike(object):
    """
    A dummy EntryPoint substitute to be used with :func:`selectEntryPoints`
    for wrapping arbitrary objects and imitate the `name` and `load()` API of
    a :class:`pkg_resources.EntryPoint` instance.

    Pass an object and optionally a name to the constructor to get the wrapped
    `EntryPointAlike` instance. The `repr` of the object is used as the name
    if `name` arg is not provided.
    """
    def __init__(self, obj, name=None):
        self._obj = obj
        if name is None:
            name = repr(obj)
        self.name = name

    def load(self):
        """Returns the wrapped object"""
        return self._obj


def selectEntryPoints(group=None, include=('.*',), exclude=()):
    """
    Selects and prioritizes entry points from an entry point group.

    The entry points are selected using their name.

    The selection is done by regex matching on the names: first the entry
    points whose name matches any of the patterns in `excluded` are discarded;
    then each pattern in `included` is used to select from the names of the
    remaining entry points (from highest to lowest priority).

    In this way, the entry points are selected in the order dictated by
    the `included` pattern list. If a pattern matches several names, these
    will be sorted alphabetically. If a name is matched by several patterns,
    it is only selected by the first pattern.

    For example, if there are the following registered entry point names:
    ['foo1', 'foo2', 'baz1', 'baz2', 'bar1', 'bar2']
    And we use `exclude=("foo2",)` and `include=("bar2", "b.*1", "f.*")` ,
    then the selection will be: ["bar2","bar1","baz1","foo1"]

    Note: apart from regex patterns (strings or compiled) the `include` list
    can also contain :class:`pkg_resources`EntryPoint`-like instances
    (more specifically, an object having `.name` and `.load()` members), in
    which case they are added directly to the selected list. If a member is
    something other than a pattern or an EntryPoint-like object, it will be
    wrapped in an :class:`EntryPointAlike` instance and also included in the
    selection.

    :param group: (str) entry point group name from which the entry points
                  are obtained.
    :param include: (`tuple`). The members of the tuple can either be
                    patterns (both in the form of strings or of
                    :class:`re.Pattern` objects), which will be matched against
                    registered names in group; or EntryPoint-like objects which
                    will be included as they are; or an arbitrary object which
                    will be wrapped as an EntryPoint-like object before being
                    included. Default is `(".*",)`, which matches all
                    registered names in group and the sort is purely
                    alphabetical.
    :param exclude: (`tuple`). Regexp patterns (either `str` or
                    :class:`re.Pattern` objects) matching names to be excluded.
                    Default is `()`, so no entry point is excluded.

    :return: (list of :class:`pkg_resources.EntryPoint`) the selected entry
             points.
    """
    ret = []

    remaining = list(pkg_resources.iter_entry_points(group))

    # filter out the entry points whose name matches a exclude pattern
    for p in exclude:
        remaining = [e for e in remaining if not fullmatch(p, e.name)]

    # sort the remaining entry points alphabetically
    remaining.sort(key=lambda e: e.name)

    # fill the ret list with the entry points whose name matches a pattern in
    # the `include` tuple. The inclusion order follows the order of the
    # patterns in `include` (and alphabetically for a pattern that produces
    # multiple matches)
    for p in include:
        try:
            # check if it is a pattern string or pattern object
            p = re.compile(p)
        except TypeError:
            # if p is not an entry point -like object, create one
            if not hasattr(p, 'name') or not hasattr(p, 'load'):
                p = EntryPointAlike(p)
            # and add it directly
            ret.append(p)
            continue
        # if it is a pattern, match it against remaining entry points
        tmp = remaining
        remaining = []
        for e in tmp:
            if fullmatch(p, e.name):
                ret.append(e)
            else:
                remaining.append(e)
    return ret

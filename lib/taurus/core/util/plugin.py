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

import re
import pkg_resources

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
    it is only selected byt the first pattern.

    For example, if there are the following registered entry point names:
    ['foo1', 'foo2', 'baz1', 'baz2', 'bar1', 'bar2']
    And we use `exclude=("foo2",)` and `include=("bar2", "b.*1", "f.*")` ,
    then the selection will be: ["bar2","bar1","baz1","foo1"]

    :param group: (`str`) entry point group name from which the entry points
    are obtained.
    :param include: (`tuple` of `str` or `re.Pattern`). Regexp patterns for
    names to be included in the selection. Default is `(".*",)`, which matches
    all registered names and the sort is purely alphabetical.
    :param exclude: (`tuple` of `str` or `re.Pattern`). Regexp patterns for
    names to be excluded. Default is `()`, so no entry point is excluded.
    """
    ret = []

    remaining = list(pkg_resources.iter_entry_points(group))

    # filter out the entry points whose name matches a exclude pattern
    for p in exclude:
        remaining = [e for e in remaining if not re.match(p, e.name)]

    # sort the remaining entry points alphabetically
    remaining.sort(key=lambda e: e.name)

    # fill the ret list with the entry points whose name matches a pattern in
    # the `include` tuple. The inclusion order follows the order of the
    # patterns in `include` (and alphabetically for a pattern that produces
    # multiple matches)
    for p in include:
        tmp = remaining
        remaining = []
        for e in tmp:
            if re.fullmatch(p, e.name):
                ret.append(e)
            else:
                remaining.append(e)
    return ret

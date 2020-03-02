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

from __future__ import print_function
from ast import literal_eval


def parse_args(s, strip_pars=False):
    """
    Parse a string representing arguments to a method to return the
    corresponding args and kwargs.

    :param s: string representing arguments to a method
    :param strip_pars: (bool) If True, expect s to include surrounding
          parenthesis
    :return: args, kwargs (a list of positional arguments and a dict of keyword
             arguments)
    """
    s = s.strip()
    if strip_pars:
        # remove parentheses
        if s.startswith('(') and s.endswith(')'):
            s = s[1:-1].strip()
    if not s:
        # empty arg list
        return [], {}
    a = []
    kw = {}
    for e in s.split(','):
        if '=' in e:
            k, v = e.split('=')
            kw[k.strip()] = literal_eval(v.strip())
        else:
            if kw:
                # a non-kwarg found after we already have at least one kwarg
                raise SyntaxError('non-keyword arg after keyword arg')
            a.append(literal_eval(e.strip()))
    return a, kw

if __name__ == "__main__":

    print(parse_args('1, 2, b=3, c=4'))
    print(parse_args(' (1, 2, b=3, c=4 )', strip_pars=True))

    print(parse_args('1, 2, b=3, c=4, 5'))  # <--this should raise a SyntaxError

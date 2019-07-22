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

"""Find path of executable specified by filename"""

__all__ = ["whichfile"]

__docformat__ = "restructuredtext"


import os


def whichfile(filename, exts=None):
    '''Find path of executable specified by filename.
    It Takes into consideration
    the PATHEXT variable (found in MS Windows systems) to try also executable
    names extended with executable extensions.

    Example::

      # on a debian machine with taurus installed in the default path:
      whichfile('taurus') --> '/usr/bin/taurus'

      # or, on a winXP machine:
      whichfile('command') --> 'C:\\WINDOWS\\system32\\command.COM'

    :param filename: (str) executable name.
    :param exts: (list<str>) a list of valid executable extensions.
                 If None given, the PATHEXT environmental variable is used
                 if available.

    :return: (str) absolute path to the executable in the file system
    '''
    path = os.getenv('PATH', '').split(os.path.pathsep)
    if exts is None:
        exts = os.getenv('PATHEXT', '').split(os.path.pathsep)
    if '' not in exts:
        exts.insert(0, '')
    for p in path:
        p = os.path.join(p, filename)
        for e in exts:
            pext = p + e
            if os.access(pext, os.X_OK):
                return pext
    return None

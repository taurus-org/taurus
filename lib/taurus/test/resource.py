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
###########################################################################

'''Utility code for working with test resources'''
from __future__ import print_function

import os
import sys


def getResourcePath(resmodule, fname=''):
    '''
    Returns the absolute path to the directory in which the
    resource module named `resmodule` is implemented.
    If filename is passed, the path to the filename in such directory is
    returned, e.g.:

    getResourcePath('foo.test.res', 'bar.txt') -->
     absolute path to <taurus>/foo/test/res/bar.txt


    It raises ImportError if resmodule does not exist and
    RuntimeError if fname does not exist)

    :param resmodule: (str) name of a resource module
    :param fname: (str) the name of a resource file present in the
                  resmodule directory

    :return: (str) absolute path to the resource file
             (or to the resource directory if fname is not passed)

    '''
    __import__(resmodule)
    module = sys.modules[resmodule]  # We use this because __import__('x.y')
    # returns x instead of y !!
    dirpath = os.path.abspath(os.path.dirname(module.__file__))
    path = os.path.join(dirpath, fname)
    if not os.path.exists(path):
        raise RuntimeError('File "%s" does not exist' % path)
    return path


if __name__ == "__main__":
    print(getResourcePath('taurus.test'))
    print(getResourcePath('taurus.test', 'resource.py'))
    # print getResourcePath('taurus.qt.qtgui.plot', 'taurusplot.py')
    # print getResourcePath('taurus.test', 'dummy.py')
    # print getResourcePath('taurus.kk', 'resource.py')

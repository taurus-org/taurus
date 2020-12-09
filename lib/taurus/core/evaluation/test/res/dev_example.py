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
Examples on using the evaluation scheme for exposing arbitrary non-tango quantities as taurus attributes
"""


from __future__ import print_function
import os
import platform
import ctypes
from taurus.core.evaluation import EvaluationDevice
from taurus.core.units import Quantity


__all__ = ['FreeSpaceDevice']



class FreeSpaceDevice(EvaluationDevice):
    '''A simple example of usage of the evaluation scheme for
    creating a device that allows to obtain available space in a dir.

    Important: note that only those members listed in `_symbols` will be available
    '''
    _symbols = ['getFreeSpace']

    _x =1

    def getFreeSpace(self, dir):
        """ return free space (in bytes).
        (Recipe adapted from `http://stackoverflow.com/questions/51658`)
        """
        if platform.system() == 'Windows':
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(dir), None, None, ctypes.pointer(free_bytes))
            ret = free_bytes.value
        else:
            s = os.statvfs(dir)
            ret = s.f_bsize * s.f_bavail

        return Quantity(ret, 'B')


#=========================================================================
# Just for testing
#=========================================================================

def test1():
    import taurus
    # calculates free space in Gb
    a = taurus.Attribute(
        'eval:@taurus.core.evaluation.test.res.dev_example.FreeSpaceDevice/getFreeSpace("/").to("GiB")')
    print("Free space: {:s}".format(a.read().rvalue), a.read().rvalue.units)


def test2():
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.panel import TaurusForm
    app = TaurusApplication(cmd_line_parser=None)

    w = TaurusForm()
    attrname = 'eval:@taurus.core.evaluation.test.res.dev_example.FreeSpaceDevice/getFreeSpace("/")'

    w.setModel(attrname)

    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    test1()
    test2()

#!/usr/bin/env python
#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

'''
Examples on using the evaluation scheme for exposing arbitrary non-tango quantities as taurus attributes
'''

__all__ = ['FreeSpaceDevice']

from taurus.core.evaluation import EvaluationDevice
import os, platform, ctypes

class FreeSpaceDevice(EvaluationDevice):
    '''A simple example of usage of the evaluation scheme for 
    creating a device that allows to obtain available space in a dir.
    
    Important: note that only those members listed in `_symbols` will be available
    '''
    _symbols = ['getFreeSpace']
        
    def getFreeSpace(self, dir):
        """ return free space (in bytes). 
        (Recipe adapted from `http://stackoverflow.com/questions/51658`)
        """
        if platform.system() == 'Windows':
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dir), None, None, ctypes.pointer(free_bytes))
            return free_bytes.value
        else:
            s =  os.statvfs(dir)
            return s.f_bsize * s.f_bavail
        

#===============================================================================
# Just for testing
#===============================================================================

def test1():
    import taurus
    a = taurus.Attribute('eval://dev=taurus.core.evaluation.dev_example.FreeSpaceDevice;getFreeSpace("/")/1024/1024') #calculates free space in Mb
    print "Free space: %iMb"%a.read().value
    
def test2():
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.display import TaurusLabel
    app = TaurusApplication()
    
    w = TaurusLabel()
    attrname='eval://dev=taurus.core.evaluation.dev_example.FreeSpaceDevice;getFreeSpace("/")' #calculates free space in Mb
    
    w.setModel(attrname)

    w.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    test2()
    
            
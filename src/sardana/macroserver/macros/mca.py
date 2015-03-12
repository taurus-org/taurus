##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""MCA related macros"""

__docformat__ = 'restructuredtext'

__all__ = ["mca_start", "mca_stop"]

from sardana.macroserver.macro import *

import array

class mca_start(Macro):
    """Starts an mca"""
    
    param_def = [
       ['mca', Type.ExpChannel, None, 'mca']
    ]
    
    def run(self, mca):
        name = mca.getName()
        mca.Start()
        o = "Starting " +  name
        self.output(o)

class mca_stop(Macro):
    """Stops an mca"""
    
    param_def = [
       ['mca', Type.ExpChannel, None, 'mca']
    ]
    
    def run(self, mca):
        name = mca.getName()
        mca.Abort()
        o = "Stopping " +  name
        self.output(o)

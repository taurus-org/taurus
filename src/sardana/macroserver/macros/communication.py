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

"""This is the standard macro module"""

__docformat__ = 'restructuredtext'

__all__ = ["get", "put"]

from sardana.macroserver.macro import *

import array

class put(Macro):
    """Sends a string to the communication channel"""
    param_def = [
       ['communication channel', Type.ComChannel, None, 'the communication channel'],
       ['data', Type.String, None, 'data to be sent']
    ]
    
    def run(self, comch, data):
        name = comch.getName()
        nb = comch.write(data)
        o = str(nb) + " bytes sent to " + name
        self.output(o)


class get(Macro):
    """Reads and outputs the data from the communication channel"""
    
    param_def = [
       ['communication channel', Type.ComChannel, None, 'the communication channel'],
       ['maximum length', Type.String, -1, 'maximum number of bytes to read']
    ]
    
    def run(self, comch, maxlen):
        name = comch.getName()
        data = comch.command_inout("read",maxlen)
        
        datastr = array.array('B',data).tostring()
        self.output("'" + datastr + "'")
        self.output(data)
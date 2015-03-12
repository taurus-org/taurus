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

"""IORegister related macros"""

__docformat__ = 'restructuredtext'

__all__ = ["write_ioreg", "read_ioreg"]

from sardana.macroserver.macro import *

import array


class write_ioreg(Macro):
    """Writes a value to an input register"""
    
    param_def = [
       ['input/output register', Type.IORegister, None, 'input/output register'],
       ['data', Type.Integer, None, 'value to be send']
    ]
    
    def run(self, ioreg, data):
        name = ioreg.getName()
        o = "Writing " + str(data) + " to " + name + " register "
        self.debug(o)
        data = ioreg.writeIORegister(data)



class read_ioreg(Macro):
    """Reads an output register"""
    
    param_def = [
       ['input/output register', Type.IORegister, None, 'input/output register']
    ]
    
    result_def = [
       ['input/output register value', Type.Integer, None, 'value read from ' +
                                                    'the input/output register']
    ]

    def run(self, ioreg):
        name = ioreg.getName()
        data = ioreg.readIORegister(force=True)
        o = "Reading " +  name + " register "
        self.debug(o)
        return data

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

"""This module contains the definition of a I/I0 pseudo counter controller
for the Sardana Device Pool"""

__all__ = ["IoverI0"]

__docformat__ = 'restructuredtext'

from sardana.pool.controller import PseudoCounterController


class IoverI0(PseudoCounterController):
    """ A simple pseudo counter which receives two counter values (I and I0) 
        and returns I/I0"""
    
    gender = "IoverI0"
    model  = "Default I/I0"
    organization = "Sardana team"
    
    counter_roles = "I", "I0"

    def Calc(self, axis, counter_values):
        i, i0 = counter_values
        try:
            i = float(i/i0)
        except ZeroDivisionError:
            pass
        return i

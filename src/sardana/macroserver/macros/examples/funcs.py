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

"""Examples of macro functions"""

from __future__ import print_function

__all__ = ["mfunc1", "mfunc2", "mfunc3", "mfunc4", "mfunc5"]

__docformat__ = 'restructuredtext'

from sardana.macroserver.macro import Type, Macro, macro


@macro()
def mfunc1(self):
    """First macro function. No parameters whatsoever"""
    self.output("Executing %s", self.getName())
    self.print("Hello",1)
    self.wa()

@macro()
def mfunc2(self, p1):
    """Second macro function. One parameter of unknown type"""
    self.output("parameter: %s", p1)

@macro([ ["moveable", Type.Moveable, None, "motor to watch"] ])
def mfunc3(self, moveable):
    """Third macro function. A proper moveable parameter"""
    self.output("Moveable %s is at %s", moveable.getName(), moveable.getPosition())
    self.ascan(moveable, 0, 10, 10, 0.1)
    self.mfunc1()
    
@macro()
def mfunc4(self, *args):
    """Fourth macro function. A list of parameters of unknown type"""
    self.output("parameters %s", args)
    
@macro()
def mfunc5(self, *args):
    """Fifth macro function. A list of parameters of unknown type"""
    self.output("parameters %s", args)

@macro([ ["moveable", Type.Moveable, None, "moveable to move"],
         ["position", Type.Float, None, "absolute position"] ])
def move(self, moveable, position):
    """This macro moves a motor to the specified position"""
    moveable.move(position)
    self.print("Motor ended at ", moveable.getPosition())

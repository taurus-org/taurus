#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
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

"""This module contains the definition of the macroserver base types for
macros"""

__all__ = ["Integer", "Float", "Boolean", "String", "User", "Filename",
           "File", "Macro", "MacroLib", "Env", "Motor", "MotorParam",
           "MotorGroup", "ExpChannel", "MeasurementGroup", "ComChannel",
           "IORegister", "Controller", "Instrument", "ControllerClass" ]

__docformat__ = 'restructuredtext'

from sardana.macroserver.parameter import ParamType, AttrParamType, ElementParamType

# Basic types

class Integer(ParamType):
    type_class = int

class Float(ParamType):
    type_class = float

class Boolean(ParamType):
    type_class = bool

    def getObj(self, str_repr):
        return str_repr.lower() == "true"
    
class String(ParamType):
    type_class = str

class User(ParamType):
    type_class = str

class Filename(ParamType):
    type_class = str

class File(ParamType):
    type_class = str
    
    def __init__(self, name):
        ParamType.__init__(self, name)
        self.filename = None
        #self.data is supposed to be a array.array object
        self.data = None
    
    def set(self, filename, data):
        self.filename = filename
        self.data = data
        

class Macro(ParamType):
    type_class = str


class MacroLib(ParamType):
    type_class = str

class Env(ParamType):
    type_class = str

# Hardware types

class MotorParam(AttrParamType):
    """ Class designed to represent a motor parameter name. Usual values
    are acceleration,deceleration,velocity,backlash,steps_per_unit,etc"""
    
    def __init__(self, name):
        AttrParamType.__init__(self, name)
        self.attr_item_list = ["Acceleration","Backlash","Base_rate","Step_per_unit",
                "Deceleration","Velocity","Offset"]
        self.non_attr_item_list = ["Controller"]
    
    def getItemList(self):
        return self.non_attr_item_list + self.attr_item_list
    
    def getAttrItemList(self):
        return self.attr_item_list
    
    def getNonAttrItemList(self):
        return self.non_attr_item_list


class Element(ElementParamType):
    
    def accepts(self, elem):
        return True


class PoolElement(ElementParamType):

    def accepts(self, elem):
        return hasattr(elem, 'pool')


class Motor(ElementParamType):
    """ Class designed to represend a generic movement parameter. Could in fact
    be a Motor, PseudoMotor or even a MotorGroup object 
    """
    _types = "Motor", "PseudoMotor"
    def accepts(self, elem):
        return elem.getType() in self._types


class MotorGroup(ElementParamType):
    """ Class designed to represend a generic motor group."""
    pass


class ExpChannel(ElementParamType):
    """ Class designed to represend a generic experiment channel parameter.
    Could in fact be a Counter/Timer, 0D, 1D or 2D channel or a PseudoCounter
    """
    _types = "CounterTimer", "ZeroDExpChannel", "OneDExpChannel", \
             "TwoDExpChannel", "PseudoCounter"

    def accepts(self, elem):
        return elem.getType() in self._types


class MeasurementGroup(ElementParamType):
    """ Class designed to represend a generic experiment."""
    pass


class ComChannel(ElementParamType):
    """ Class designed to represend a generic communication channel."""
    pass


class IORegister(ElementParamType):
    """ Class designed to represend a generic input/output register. """
    pass


class Controller(ElementParamType):
    """ Class designed to represent a generic controller."""
    pass


class Instrument(ElementParamType):
    """ Class designed to represent a generic instrument."""
    pass


class ControllerClass(ElementParamType):
    """ Class designed to represent a generic controller class."""
    pass


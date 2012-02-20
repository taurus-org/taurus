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
           "File", "Macro", "MacroLibrary", "Env", "Motor", "MotorParam",
           "MotorGroup", "ExpChannel", "MeasurementGroup", "ComChannel",
           "IORegister", "Controller", "Instrument", "ControllerClass" ]

__docformat__ = 'restructuredtext'

from sardana import INTERFACES
from sardana.macroserver.msparameter import ParamType, AttrParamType, \
    ElementParamInterface

# Basic types
class Any(ParamType):
    type_class = lambda p : p

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
    
    def __init__(self, macro_server, name):
        ParamType.__init__(self, macro_server, name)
        self.filename = None
        #self.data is supposed to be a array.array object
        self.data = None
    
    def set(self, filename, data):
        self.filename = filename
        self.data = data

class Env(ParamType):
    type_class = str

# Hardware types

class MotorParam(AttrParamType):
    """ Class designed to represent a motor parameter name. Usual values
    are acceleration,deceleration,velocity,backlash,steps_per_unit,etc"""
    
    def __init__(self, macro_server, name):
        AttrParamType.__init__(self, macro_server, name)
        self.attr_item_list = ["Acceleration","Backlash","Base_rate","Step_per_unit",
                "Deceleration","Velocity","Offset"]
        self.non_attr_item_list = ["Controller"]
    
    def getItemList(self):
        return self.non_attr_item_list + self.attr_item_list
    
    def getAttrItemList(self):
        return self.attr_item_list
    
    def getNonAttrItemList(self):
        return self.non_attr_item_list


for sardana_type in INTERFACES:
    class _(ElementParamInterface):
        pass
    _.__name__ = sardana_type
    globals()[sardana_type] = _



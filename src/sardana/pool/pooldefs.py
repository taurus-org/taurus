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

"""This file contains the basic pool definitions"""

__docformat__ = 'restructuredtext'

from taurus.core.util import Enumeration

InvalidId = 0
InvalidAxis = 0
EpsilonError = 1E-9

ElementType = Enumeration("ElementType", ( \
    "Undef",
    "Pool",
    "Ctrl",
    "Motor",
    "CTExpChannel",
    "ZeroDExpChannel",
    "OneDExpChannel",
    "TwoDExpChannel",
    "Communication",
    "IORegister",
    "PseudoMotor",
    "PseudoCounter",
    "Constraint",
    "MotorGroup",
    "MeasurementGroup",
    "Instrument") )

TYPE_ELEMENTS = ElementType.Motor, ElementType.CTExpChannel, ElementType.ZeroDExpChannel, \
    ElementType.OneDExpChannel, ElementType.TwoDExpChannel, ElementType.ZeroDExpChannel, \
    ElementType.Communication, ElementType.IORegister, ElementType.PseudoMotor, \
    ElementType.PseudoCounter, ElementType.Constraint
    
TYPE_GROUP_ELEMENTS = ElementType.MotorGroup, ElementType.MeasurementGroup

TYPE_MOVEABLE_ELEMENTS = ElementType.Motor, ElementType.PseudoMotor, ElementType.MotorGroup

State = Enumeration("State", ( \
    "On",
    "Off",
    "Close",
    "Open",
    "Insert",
    "Extract",
    "Moving",
    "Standby",
    "Fault",
    "Init",
    "Running",
    "Alarm",
    "Disable",
    "Unknown") )

DataType = Enumeration("DataType", ( \
    "Integer",
    "Double",
    "String",
    "Boolean",
    "Encoded") )
    
DataFormat = Enumeration("DataFormat", ( \
    "Scalar",
    "OneD",
    "TwoD") )
    
DataAccess = Enumeration("DataAccess", ( \
    "ReadOnly",
    "ReadWrite") )

AcquisitionTerminationMode = Enumeration("AcquisitionTerminationMode", ( \
    "TerminateOnMaster",
    "TerminateOnAll") )
    
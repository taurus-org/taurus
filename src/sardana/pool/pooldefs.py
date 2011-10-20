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

"""This file contains the basic pool definitions."""

__all__ = ["InvalidId", "InvalidAxis", "ControllerAPI", "ElementType",
           "TYPE_ELEMENTS", "TYPE_GROUP_ELEMENTS", "TYPE_MOVEABLE_ELEMENTS",
           "TYPE_PHYSICAL_ELEMENTS", "TYPE_ACQUIRABLE_ELEMENTS",
           "TYPE_PSEUDO_ELEMENTS", "AcqTriggerType", "AcqMode"]

__docformat__ = 'restructuredtext'

from taurus.core.util import Enumeration
from taurus.core.tango.sardana import AcqTriggerType, AcqMode

#: A constant representing  an invalid ID
InvalidId = 0

#: A constant representing an invalid axis
InvalidAxis = 0

#: A constant defining the controller API version currently supported
ControllerAPI = 1

#: An enumeration describing the all possible element types in the device pool
ElementType = Enumeration("ElementType", ( \
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
    "Instrument",
    "ControllerClass",
    "ControllerLib",
    "External",
    "Unknown") )

ET = ElementType

#: a set containning all "controllable" element types
TYPE_ELEMENTS = set((ET.Motor, ET.CTExpChannel, ET.ZeroDExpChannel, \
    ET.OneDExpChannel, ET.TwoDExpChannel, \
    ET.Communication, ET.IORegister, ET.PseudoMotor, \
    ET.PseudoCounter, ET.Constraint))

#: a set containing all group element types
TYPE_GROUP_ELEMENTS = set((ET.MotorGroup, ET.MeasurementGroup))

#: a set containing the type of elements which are moveable
TYPE_MOVEABLE_ELEMENTS = set((ET.Motor, ET.PseudoMotor, ET.MotorGroup))

TYPE_PHYSICAL_ELEMENTS = set((ET.Motor, ET.CTExpChannel, ET.ZeroDExpChannel, \
    ET.OneDExpChannel, ET.TwoDExpChannel, \
    ET.Communication, ET.IORegister))

TYPE_ACQUIRABLE_ELEMENTS = set((ET.Motor, ET.CTExpChannel, ET.ZeroDExpChannel, \
    ET.OneDExpChannel, ET.TwoDExpChannel, \
    ET.Communication, ET.IORegister, ET.PseudoMotor, \
    ET.PseudoCounter))

TYPE_PSEUDO_ELEMENTS = set((ET.PseudoMotor, ET.PseudoCounter))






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

__all__ = ["InvalidId", "InvalidAxis", "ElementType", "TYPE_ELEMENTS",
           "TYPE_GROUP_ELEMENTS", "TYPE_MOVEABLE_ELEMENTS",
           "AcqMode", "AcqTriggerType",
           "ControllerOfflineException"]

__docformat__ = 'restructuredtext'

from taurus.core.util import Enumeration

InvalidId = 0
InvalidAxis = 0

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

ET = ElementType
TYPE_ELEMENTS = ET.Motor, ET.CTExpChannel, ET.ZeroDExpChannel, \
    ET.OneDExpChannel, ET.TwoDExpChannel, ET.ZeroDExpChannel, \
    ET.Communication, ET.IORegister, ET.PseudoMotor, \
    ET.PseudoCounter, ET.Constraint
    
TYPE_GROUP_ELEMENTS = ET.MotorGroup, ET.MeasurementGroup

TYPE_MOVEABLE_ELEMENTS = ET.Motor, ET.PseudoMotor, ET.MotorGroup

AcqTriggerType = Enumeration("AcqTriggerType", ( \
    "Software", # channel triggered by software - start and stop by software
    "Gate",     # channel triggered by HW - start and stop by external 
    "Unknown") )

AcqMode = Enumeration("AcqMode", ( \
    "Timer",
    "Monitor",
    "Unknown") )

class ControllerOfflineException(Exception):
    """An exception to be thrown when an operation is requested on a controller
    which is offline"""
    pass

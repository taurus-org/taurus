#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""The core module"""

__docformat__ = "restructuredtext"

from taurus.core import *

## renamed classes in taurus 2.0
# enums.py
TauSWDevState = TaurusSWDevState
TauSWDevHealth = TaurusSWDevHealth
TauEventType = TaurusEventType
TauElementType = TaurusElementType
TauAttrValue = TaurusAttrValue
TauConfigValue = TaurusConfigValue

TauException = TaurusException
TaurusModel = TaurusModel
TauListener = TaurusListener
TauExceptionListener = TaurusExceptionListener
TauDeviceQuery = None
TauDevice = TaurusDevice
TauAttribute = TaurusAttribute
TauStateAttribute = TaurusStateAttribute
TauConfiguration = TaurusConfiguration
TauConfigurationProxy = TaurusConfigurationProxy
TauInfo = TaurusInfo
TauDevInfo = TaurusDevInfo
TauDevClassInfo = TaurusDevClassInfo
TauServInfo = TaurusServInfo
TauAttrInfo = TaurusAttrInfo
TauDevTree = TaurusDevTree
TauServerTree = TaurusServerTree
TauDatabase = TaurusDatabase
TauDatabaseCache = TaurusDatabaseCache
TauDatabaseQuery = None
TauFactory = TaurusFactory
TauManager = TaurusManager
TauOperation = TaurusOperation
TauPollingTimer = TaurusPollingTimer

# taurusvalidator.py

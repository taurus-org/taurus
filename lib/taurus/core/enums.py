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

"""This module contains all basic taurus enumerations"""

__all__ = ["TaurusSWDevState", "TaurusSWDevHealth", "OperationMode", 
           "TaurusEventType", "MatchLevel", "TaurusElementType", "DataFormat",
           "AttrQuality", "AttrType", "DisplayLevel", "ManagerState", 
           "TaurusAttrValue", "TaurusConfigValue"]

__docformat__ = "restructuredtext"

import util

TaurusSWDevState = util.Enumeration(
'TaurusSWDevState', (
    'Uninitialized',
    'Running', 
    'Shutdown', 
    'Crash', 
    'EventSystemShutdown'
))

TaurusSWDevHealth = util.Enumeration(
'TaurusSWDevHealth', (
    'Exported',           # device reported exported
    'ExportedAlive',      # device reported exported and confirmed connection
    'ExportedNotAlive',   # device reported exported but connection failed!!
    'NotExported',        # device didn't report exported
    'NotExportedAlive',   # device didn't report exported but connection confirmed!
    'NotExportedNotAlive' # device didn't report exported and connection failed
))

OperationMode = util.Enumeration(
'OperationMode', (
    'OFFLINE',
    'ONLINE'
))

TaurusEventType = util.Enumeration(
'TaurusEventType', (
    'Change',
    'Config',
    'Periodic',
    'Error'
))

MatchLevel = util.Enumeration(
'MatchLevel', (
    'ANY', 
    'SHORT', 
    'NORMAL', 
    'COMPLETE', 
    'SHORT_NORMAL', 
    'NORMAL_COMPLETE'
))

TaurusElementType = util.Enumeration(
'TaurusElementType', (
    'Unknown',
    'Name',
    'DeviceClass',
    'Device',
    'DeviceAlias',
    'Domain',
    'Family',
    'Member',
    'Server',
    'ServerName',
    'ServerInstance',
    'Exported',
    'Host',
    'Attribute',
    'AttributeAlias',
    'Command',
    'Property',
    'Configuration',
    'Database',
))

#################
# Not in use yet:

DataFormat = util.Enumeration(
'DataFormat', (
    '_0D', 
    '_1D', 
    '_2D'
))

AttrQuality = util.Enumeration(
'AttrQuality', (
    'ATTR_VALID', 
    'ATTR_INVALID', 
    'ATTR_ALARM'
))

AttrType = util.Enumeration(
'AttrType', (
    'READ', 
    'READ_WITH_WRITE', 
    'WRITE', 
    'READ_WRITE' 
))

DisplayLevel = util.Enumeration(
'DisplayLevel', (
    'OPERATOR', 
    'EXPERT', 
    'DEVELOPER'
))

ManagerState =  util.Enumeration(
'ManagerState', (
    'UNINITIALIZED', 
    'INITED', 
    'CLEANED'
)) 

class TaurusAttrValue:
    def __init__(self):
        self.read_value = None
        self.write_value = None
        self.time_stamp = None
        self.quality = AttrQuality.ATTR_VALID
        self.format = 0

class TaurusConfigValue:
    def __init__(self):
        self.name = None
        self.writable = None
        self.data_format = None
        self.data_type = None
        self.max_dim = 1, 1
        self.label = None
        self.unit = None
        self.standard_unit = None
        self. display_unit= None
        self.format = None
        self.range = float('-inf'), float('inf')
        self.alarm = float('-inf'), float('inf')
        self.warning = float('-inf'), float('inf')
        self.disp_level = None
    

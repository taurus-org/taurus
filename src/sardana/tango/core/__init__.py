#!/usr/bin/env python

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

""" """

__docformat__ = 'restructuredtext'

import PyTango.constants


def __init_pytango_devfailed(mod):
    consts = (
"API_AttrConfig", "API_AttrEventProp", "API_AttrIncorrectDataNumber",
"API_AttrNoAlarm", "API_AttrNotAllowed", "API_AttrNotFound",
"API_AttrNotWritable", "API_AttrOptProp", "API_AttrPropValueNotSet",
"API_AttrValueNotSet", "API_AttrWrongDefined", "API_AttrWrongMemValue",
"API_BadConfigurationProperty", "API_BlackBoxArgument", "API_BlackBoxEmpty",
"API_CannotCheckAccessControl", "API_CannotOpenFile",
"API_CantActivatePOAManager", "API_CantCreateClassPoa",
"API_CantCreateLockingThread", "API_CantFindLockingThread",
"API_CantGetClientIdent", "API_CantGetDevObjectId",
"API_CantInstallSignal", "API_CantRetrieveClass", "API_CantRetrieveClassList",
"API_CantStoreDeviceClass", "API_ClassNotFound",
"API_CmdArgumentTypeNotSupported", "API_CommandNotAllowed",
"API_CommandNotFound", "API_CorbaSysException", "API_CorruptedDatabase",
"API_DatabaseAccess", "API_DeviceLocked", "API_DeviceNotFound",
"API_DeviceNotLocked", "API_DeviceUnlockable", "API_DeviceUnlocked",
"API_EventSupplierNotConstructed", "API_IncoherentDbData",
"API_IncoherentDevData", "API_IncoherentValues", "API_IncompatibleAttrDataType",
"API_IncompatibleCmdArgumentType", "API_InitMethodNotFound",
"API_InitNotPublic", "API_InitThrowsException",
"API_JavaRuntimeSecurityException", "API_MemoryAllocation",
"API_MethodArgument", "API_MethodNotFound", "API_MissedEvents",
"API_NotSupportedFeature", "API_NtDebugWindowError",
"API_OverloadingNotSupported", "API_PolledDeviceNotInPoolConf",
"API_PolledDeviceNotInPoolMap", "API_PollingThreadNotFound",
"API_ReadOnlyMode", "API_SignalOutOfRange", "API_SystemCallFailed",
"API_WAttrOutsideLimit", "API_WizardConfError", "API_WrongEventData",
"API_WrongHistoryDataBuffer", "API_WrongLockingStatus", "API_ZmqInitFailed")

    for const in consts:
        setattr(mod, const, const)


def __prepare_pytango():

    if not hasattr(PyTango.constants, "API_DeviceNotFound"):
        __init_pytango_devfailed(PyTango.constants)

__prepare_pytango()

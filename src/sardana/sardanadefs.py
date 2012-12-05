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

"""This module contains the most generic sardana constants and enumerations"""

__all__ = ["EpsilonError", "SardanaServer", "ServerRunMode", "State",
           "DataType", "DataFormat", "DataAccess", "DTYPE_MAP", "R_DTYPE_MAP",
           "DACCESS_MAP",
           "from_dtype_str", "from_access_str", "to_dtype_dformat",
           "to_daccess", "InvalidId", "InvalidAxis", "ElementType",
           "Interface", "Interfaces", "InterfacesExpanded",
           "TYPE_ELEMENTS", "TYPE_GROUP_ELEMENTS", "TYPE_MOVEABLE_ELEMENTS",
           "TYPE_PHYSICAL_ELEMENTS", "TYPE_ACQUIRABLE_ELEMENTS",
           "TYPE_EXP_CHANNEL_ELEMENTS", "TYPE_TIMERABLE_ELEMENTS",
           "TYPE_PSEUDO_ELEMENTS", "INTERFACES", "INTERFACES_EXPANDED",
           "ScalarNumberFilter"]

__docformat__ = 'restructuredtext'

import math

from taurus.core.util import Enumeration

#: maximum difference between two floats so that they are considered equal
EpsilonError = 1E-16

#: sardana element state enumeration
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
    "Unknown",
    "Invalid") )


class _SardanaServer(object):
    """Class representing the current sardana server state"""
    
    def __init__(self):
        self.server_state = State.Invalid
    
    def __repr__(self):
        return "SardanaServer()"
    
    
#: the global object containing the SardanaServer information
SardanaServer = _SardanaServer()

#:
#: The sardana server run mode:
#:
#: - **SynchPure** : Pure synchronous: Start the server and run the server loop
#:   until it stops
#: - **SynchThread** : separate thread synchronous: start a thread running the
#:   server loop. Block until the server loop ends
#: - **SynchProcess** : separate process synchronous: start a sub-process
#:   running the server loop. Block until the server loop ends
#: - **AsynchThread** : separate thread asynchronous: start a thread running the
#:   server loop. Return immediately
#: - **ASynchProcess** : separate process asynchronous: start a sub-process
#:   running the server loop. Return immediately
ServerRunMode = Enumeration("ServerRunMode", \
                            ("SynchPure", "SynchThread", "SynchProcess", \
                             "AsynchThread", "AsynchProcess"))

#: sardana data types (used by device pool controllers)
DataType = Enumeration("DataType", ( \
    "Integer",
    "Double",
    "String",
    "Boolean",
    "Encoded",
    "Invalid") )

#: sardana data format enumeration (used by device pool controllers)
DataFormat = Enumeration("DataFormat", ( \
    "Scalar",
    "OneD",
    "TwoD",
    "Invalid") )

#: sardana data access (used by device pool controllers)
DataAccess = Enumeration("DataAccess", ( \
    "ReadOnly",
    "ReadWrite",
    "Invalid") )

#: dictionary dict<data type, :class:`sardana.DataType`>
DTYPE_MAP = { 
    'int'            : DataType.Integer,
    'integer'        : DataType.Integer,
    int              : DataType.Integer,
    long             : DataType.Integer,
    'long'           : DataType.Integer,
    DataType.Integer : DataType.Integer,
    'float'          : DataType.Double,
    'double'         : DataType.Double,
    float            : DataType.Double,
    DataType.Double  : DataType.Double,
    'str'            : DataType.String,
    'string'         : DataType.String,
    str              : DataType.String,
    DataType.String  : DataType.String,
    'bool'           : DataType.Boolean,
    'boolean'        : DataType.Boolean,
    bool             : DataType.Boolean,
    DataType.Boolean : DataType.Boolean,
}

#: dictionary dict<data type, :class:`sardana.DataType`>
R_DTYPE_MAP = { 
    'int'            : int,
    'integer'        : int,
    int              : int,
    long             : int,
    'long'           : int,
    DataType.Integer : int,
    'float'          : float,
    'double'         : float,
    float            : float,
    DataType.Double  : float,
    'str'            : str,
    'string'         : str,
    str              : str,
    DataType.String  : str,
    'bool'           : bool,
    'boolean'        : bool,
    bool             : bool,
    DataType.Boolean : bool,
}

#DTYPE_MAP.setdefault(DataType.Invalid)

#: dictionary dict<access type, :class:`sardana.DataAccess`>
DACCESS_MAP = { 
    'read'               : DataAccess.ReadOnly,
    DataAccess.ReadOnly  : DataAccess.ReadOnly,
    'readwrite'          : DataAccess.ReadWrite,
    'read_write'         : DataAccess.ReadWrite,
    DataAccess.ReadWrite : DataAccess.ReadWrite,
}
#DACCESS_MAP.setdefault(DataAccess.Invalid)

def from_dtype_str(dtype):
    """Transforms the given dtype parameter (string/:obj:`DataType` or None)
    into a tuple of two elements (str, :obj:`DataFormat`) where the first
    element is a string with a simplified data type.
    
        - If None is given, it returns
          ('float', :obj:`DataFormat.Scalar`)
        - If :obj:`DataType` is given, it returns
          (:obj:`DataType`, :obj:`DataFormat.Scalar`)
          
    :param dtype: the data type to be transformed
    :type dtype: str or None or :obj:`DataType`
    :return: a tuple <str, :obj:`DataFormat`> for the given dtype
    :rtype: tuple<str, :obj:`DataFormat`>"""
    dformat = DataFormat.Scalar
    if dtype is None:
        dtype = 'float'
    elif isinstance(dtype, (str, unicode)):
        dtype = dtype.lower()
        if dtype.startswith("pytango."):
            dtype = dtype[len("pytango."):]
        if dtype.startswith("dev"):
            dtype = dtype[len("dev"):]
        if dtype.startswith("var"):
            dtype = dtype[len("var"):]
        if dtype.endswith("array"):
            dtype = dtype[:dtype.index("array")]
            dformat = DataFormat.OneD
    return dtype, dformat

def from_access_str(access):
    """Transforms the given access parameter (string or :obj:`DataAccess`) into
    a simplified data access string.
    
    :param dtype: the access to be transformed
    :type dtype: str
    :return: a simple string for the given access
    :rtype: str"""
    if isinstance(access, (str, unicode)):
        access = access.lower()
        if access.startswith("pytango."):
            access = access[len("pytango."):]
    return access

def to_dtype_dformat(data):
    """Transforms the given data parameter (string/ or sequence of string or
    sequence of sequence of string/:obj:`DataType`) into a tuple of two
    elements (:obj:`DataType`, :obj:`DataFormat`).
    
    :param data: the data information to be transformed
    :type data: str or seq<str> or seq<seq<str>>
    :return: a tuple <:obj:`DataType`, :obj:`DataFormat`> for the given data
    :rtype: tuple<:obj:`DataType`, :obj:`DataFormat`>
    """
    import operator
    dtype, dformat = data, DataFormat.Scalar
    if isinstance(data, (str, unicode)):
        dtype, dformat = from_dtype_str(data)
    elif operator.isSequenceType(data):
        dformat = DataFormat.OneD
        dtype = data[0]
        if type(dtype) == str:
            dtype, dformat2 = from_dtype_str(dtype)
            if dformat2 == DataFormat.OneD:
                dformat = DataFormat.TwoD
        elif operator.isSequenceType(dtype):
            dformat = DataFormat.TwoD
            dtype = dtype[0]
            if type(dtype) == str:
                dtype, _ = from_dtype_str(dtype)
    dtype = DTYPE_MAP.get(dtype, DataType.Invalid)
    return dtype, dformat

def to_daccess(daccess):
    """Transforms the given access parameter (string or None) into a
    :obj:`DataAccess`. If None is given returns :obj:`DataAccess.ReadWrite`
    
    :param dtype: the access to be transformed
    :type dtype: str
    :return: a :obj:`DataAccess` for the given access
    :rtype: :obj:`DataAccess`"""
    if daccess is None:
        daccess = DataAccess.ReadWrite
    elif isinstance(daccess , (str, unicode)):
        daccess = DACCESS_MAP.get(from_access_str(daccess), DataAccess.ReadWrite)
    return daccess

#: A constant representing  an invalid ID
InvalidId = 0

#: A constant representing an invalid axis
InvalidAxis = 0

#: An enumeration describing the all possible element types in sardana
ElementType = Enumeration("ElementType", ( \
    "Pool",
    "Controller",
    "Motor",
    "CTExpChannel",
    "ZeroDExpChannel",
    "OneDExpChannel",
    "TwoDExpChannel",
    "ComChannel",
    "IORegister",
    "PseudoMotor",
    "PseudoCounter",
    "Constraint",
    "MotorGroup",
    "MeasurementGroup",
    "Instrument",
    "ControllerClass",
    "ControllerLibrary",
    "MacroServer",
    "Door",
    "MacroClass",
    "MacroLibrary",
    "MacroFunction",
    "External",
    "Meta",
    "ParameterType",
    "Unknown") )

ET = ElementType

#: a set containning all "controllable" element types.
#: Constant values belong to :class:`~sardana.sardanadefs.ElementType`
TYPE_ELEMENTS = set((ET.Motor, ET.CTExpChannel, ET.ZeroDExpChannel, \
    ET.OneDExpChannel, ET.TwoDExpChannel, \
    ET.ComChannel, ET.IORegister, ET.PseudoMotor, \
    ET.PseudoCounter, ET.Constraint))

#: a set containing all group element types.
#: Constant values belong to :class:`~sardana.sardanadefs.ElementType`
TYPE_GROUP_ELEMENTS = set((ET.MotorGroup, ET.MeasurementGroup))

#: a set containing the type of elements which are moveable.
#: Constant values belong to :class:`~sardana.sardanadefs.ElementType`
TYPE_MOVEABLE_ELEMENTS = set((ET.Motor, ET.PseudoMotor, ET.MotorGroup))

#: a set containing the possible types of physical elements.
#: Constant values belong to :class:`~sardana.sardanadefs.ElementType`
TYPE_PHYSICAL_ELEMENTS = set((ET.Motor, ET.CTExpChannel, ET.ZeroDExpChannel, \
    ET.OneDExpChannel, ET.TwoDExpChannel, \
    ET.ComChannel, ET.IORegister))

#: a set containing the possible types of acquirable elements.
#: Constant values belong to :class:`~sardana.sardanadefs.ElementType`
TYPE_ACQUIRABLE_ELEMENTS = set((ET.Motor, ET.CTExpChannel, ET.ZeroDExpChannel, \
    ET.OneDExpChannel, ET.TwoDExpChannel, \
    ET.ComChannel, ET.IORegister, ET.PseudoMotor, \
    ET.PseudoCounter))

#: a set containing the possible types of experimental channel elements.
#: Constant values belong to :class:`~sardana.sardanadefs.ElementType`
TYPE_EXP_CHANNEL_ELEMENTS = set((ET.CTExpChannel, ET.ZeroDExpChannel, \
    ET.OneDExpChannel, ET.TwoDExpChannel, ET.PseudoCounter))

#: a set containing the possible timer-able elements.
#: Constant values belong to :class:`~sardana.sardanadefs.ElementType`
TYPE_TIMERABLE_ELEMENTS = set((ET.CTExpChannel, ET.OneDExpChannel, 
    ET.TwoDExpChannel))

#: a set containing the possible types of pseudo elements.
#: Constant values belong to :class:`~sardana.sardanadefs.ElementType`
TYPE_PSEUDO_ELEMENTS = set((ET.PseudoMotor, ET.PseudoCounter))

##: An enumeration describing the all possible sardana interfaces
#SardanaInterface = Enumeration("SardanaInterface", ( \
#    ("Object",            0b0000000000000001),
#    ("Element",           0b0000000000000011),
#    ("Class",             0b0000000000000101),
#    ("Library",           0b0000000000001001),
#    ("PoolObject",        0b0000000000010001),
#    ("PoolElement",       0b0000000000010011),
#    ("Pool",              0b0000000000110011),
#    ("Controller",        0b0000000001000001),
#    ("Moveable",          0b0000000010000001),
#    ("Acquirable",        0b0000000100000001),
#    ("Instrument",        0b0000001000000001),
#    ("Motor",             0b0000010000000001),
#    ("PseudoMotor",       0b0000100000000001),
#    ("IORegister",        0b0001000000000001),
#    ("ExpChannel",        0b0010000000000001),
#    ("CTExpChannel",      0b0100000000000001),
#    ("ZeroDExpChannel",   0b1000000000000001),
#    ("OneDExpChannel",    0b0000000000000001),
#    ("TwoDExpChannel",    0b0000000000000001),
#    ("PseudoCounter",     0b0000000000000001),
#    ("ComChannel",        0b0000000000000001),
#    ("MotorGroup",        0b0000000000000001),
#    ("MeasurementGroup",  0b0000000000000001),
#    ("ControllerLibrary", 0b0000000000000001),
#    ("ControllerClass",   0b0000000000000001),
#    ("Constraint",        0b0000000000000001),
#    ("External",          0b0000000000000001),
    
#    ("MacroServerObject", 0b0000000000000001),
#    ("MacroServerElement",0b0000000000000001),
#    ("MacroServer",       0b0000000000000001),
#    ("MacroLibrary",      0b0000000000000001),
#    ("MacroClass",        0b0000000000000001),
#    ("Macro",             0b0000000000000001), ) )

#: a dictionary containing the direct interfaces supported by each type
#: (:obj:`dict`\<:obj:`str`\, :obj:`tuple`\<:obj:`set`\<:obj:`str`\, :obj:`str`\>>>)
INTERFACES = {
    "Meta" : (set(), "A generic sardana meta object"),
    "Object" : (set(), "A generic sardana object"),
    "Element" : (set(("Object",)), "A generic sardana element"),
    "Class" : (set(("Object",)), "A generic sardana class"),
    "Function" : (set(("Object",)), "A generic sardana function"),
    "Library" : (set(("Object",)), "A generic sardana library"),
    "PoolObject" : (set(("Object",)), "A Pool object"),
    "PoolElement" : (set(("Element", "PoolObject")), "A Pool element"),
    "Pool" : (set(("PoolElement",)), "A Pool"),
    "Controller" : (set(("PoolElement",)), "A controller"),
    "Moveable" : (set(("PoolElement",)), "A moveable element"),
    "Acquirable" : (set(("PoolElement",)), "An acquirable element"),
    "Instrument" : (set(("PoolElement",)), "An instrument"),
    "Motor" : (set(("Moveable", "Acquirable")), "a motor"),
    "PseudoMotor" : (set(("Moveable", "Acquirable")), "A pseudo motor"),
    "IORegister" : (set(("Acquirable",)), "An IO register"),
    "ExpChannel" : (set(("Acquirable",)), "A generic experimental channel"),
    "CTExpChannel" : (set(("ExpChannel",)), "A counter/timer experimental channel"),
    "ZeroDExpChannel" : (set(("ExpChannel",)), "A 0D experimental channel"),
    "OneDExpChannel" : (set(("ExpChannel",)), "A 1D experimental channel"),
    "TwoDExpChannel" : (set(("ExpChannel",)), "A 2D experimental channel"),
    "PseudoCounter" : (set(("ExpChannel",)), "A pseudo counter"),
    "ComChannel" : (set(("PoolElement",)), "A communication channel"),
    "MotorGroup" : (set(("PoolElement",),), "A motor group"),
    "MeasurementGroup" : (set(("PoolElement",),), "A measurement group"),
    "ControllerLibrary" : (set(("Library", "PoolObject")), "A controller library"),
    "ControllerClass" : (set(("Class", "PoolObject")), "A controller class"),
    "Constraint" : (set(("PoolObject",)), "A constraint"),
    "External" : (set(("Object",)), "An external object"),
    
    "MacroServerObject" : (set(("Object",)), "A generic macro server object"),
    "MacroServerElement" : (set(("Element", "MacroServerObject")), "A generic macro server element"),
    "MacroServer" : (set(("MacroServerElement",)), "A MacroServer"),
    "Door" : (set(("MacroServerElement",)), "A macro server door"),
    "MacroLibrary" : (set(("Library", "MacroServerObject")), "A macro server library"),
    "MacroCode" : (set(("MacroServerObject",)), "A macro server macro code"),
    "MacroClass" : (set(("Class", "MacroCode")), "A macro server macro class"),
    "MacroFunction" : (set(("Function", "MacroCode")), "A macro server macro function"),
    "Macro" : (set(("MacroClass", "MacroFunction")), "A macro server macro"),
    
    "ParameterType" : (set(("Meta",)), "A generic macro server parameter type"),
}

#: a dictionary containing the *all* interfaces supported by each type
#: (:obj:`dict` <:obj:`str`, :obj:`set` < :obj:`str`> >)
INTERFACES_EXPANDED = {}

def __expand(name):
    direct_expansion, _ = INTERFACES[name]
    if isinstance(direct_expansion, (str, unicode)):
        direct_expansion = direct_expansion,
    exp = set(direct_expansion)
    for e in direct_expansion:
        e_value = INTERFACES_EXPANDED.get(e)
        if e_value is None:
            exp.update(__expand(e))
        else:
            exp.update(e_value[0])
    exp.add(name)
    return exp

def __build_interfaces_expanded():
    global INTERFACES_EXPANDED
    for i in INTERFACES:
        INTERFACES_EXPANDED[i] = __expand(i), INTERFACES[i][1]

__build_interfaces_expanded()

def __expand_sardana_interface_data(si_map, name, curr_id):
    if name in si_map:
        return curr_id
    d = 0
    i_expanded = set(INTERFACES_EXPANDED[name][0])
    i_expanded.remove(name)
    for interface in i_expanded:
        if interface not in si_map:
            curr_id = __expand_sardana_interface_data(si_map, interface, curr_id)
        d |= si_map[interface]
    si_map[name] = long(d | curr_id)
    return 2*curr_id

def __root_expand_sardana_interface_data():
    curr_id = 1
    si_map = {}
    for interface in INTERFACES_EXPANDED:
        curr_id = __expand_sardana_interface_data(si_map, interface, curr_id)
    return si_map

#: An enumeration describing the all possible sardana interfaces
Interface = Enumeration("Interface",
                        __root_expand_sardana_interface_data().items())

def __create_sardana_interfaces():
    interfaces, interfaces_expanded = {}, {}
    for i in INTERFACES:
        i_enum = Interface[i]
        i_items, i_items_expanded = INTERFACES[i][0], INTERFACES_EXPANDED[i][0]
        i_enum_items = set(map(Interface.get, i_items))
        i_enum_items_expanded = set(map(Interface.get, i_items_expanded))
        interfaces[i_enum] = i_enum_items
        interfaces_expanded[i_enum] = i_enum_items_expanded
    return interfaces, interfaces_expanded

_Interfaces, _InterfacesExpanded = __create_sardana_interfaces()


#: a dictionary containing the direct interfaces supported by each type
#: (:obj:`dict` <:obj:`sardana.sardanadefs.Interface`, :obj:`set` < :obj:`sardana.sardanadefs.Interface`> >)
Interfaces = _Interfaces

#: a dictionary containing the *all* interfaces supported by each type. 
#: (:obj:`dict` <:obj:`sardana.sardanadefs.Interface`, :obj:`set` < :obj:`sardana.sardanadefs.Interface`> >)
InterfacesExpanded = _InterfacesExpanded


class ScalarNumberFilter(object):
    """A simple scalar number filter that returns ``False`` if two numbers are
    indentical (i.e. |a-b| < error)"""
    
    def __call__(self, a, b):
        try:
            return math.fabs(a-b) > EpsilonError
        except:
            return a != b

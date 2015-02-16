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

"""This module is part of the Python Pool libray. It defines the base classes
for"""

__all__ = ["CONTROLLER_TEMPLATE", "CTRL_TYPE_MAP", "TYPE_MAP", "TYPE_MAP_OBJ",
           "TypeData", "DTYPE_MAP", "DACCESS_MAP", "DataInfo",
           "ControllerLibrary", "ControllerClass"]

__docformat__ = 'restructuredtext'

import types
import inspect

from taurus.core.util.containers import CaselessDict

from sardana import DataType, DataFormat, DataAccess, \
    to_dtype_dformat, to_daccess, \
    ElementType, TYPE_ELEMENTS, InvalidId
from sardana.sardanameta import SardanaLibrary, SardanaClass
from sardana.pool.poolmotor import PoolMotor
from sardana.pool.poolpseudomotor import PoolPseudoMotor
from sardana.pool.poolmotorgroup import PoolMotorGroup
from sardana.pool.poolmeasurementgroup import PoolMeasurementGroup
from sardana.pool.poolcountertimer import PoolCounterTimer
from sardana.pool.poolzerodexpchannel import Pool0DExpChannel
from sardana.pool.poolonedexpchannel import Pool1DExpChannel
from sardana.pool.pooltwodexpchannel import Pool2DExpChannel
from sardana.pool.poolpseudocounter import PoolPseudoCounter
from sardana.pool.poolinstrument import PoolInstrument
from sardana.pool.poolioregister import PoolIORegister
from sardana.pool.poolcontroller import PoolController, \
    PoolPseudoMotorController, PoolPseudoCounterController
from sardana.pool.controller import Controller, MotorController, \
    CounterTimerController, ZeroDController, OneDController, TwoDController, \
    PseudoMotorController, PseudoCounterController, IORegisterController
from sardana.pool.controller import Type, Access, Description, DefaultValue, \
    FGet, FSet, Memorize, Memorized, MaxDimSize


#: String containing template code for a controller class
CONTROLLER_TEMPLATE = """class @controller_name@(@controller_type@):
    \"\"\"@controller_name@ description.\"\"\"

"""

ET = ElementType

#: a dictionary dict<:data:`~sardana.ElementType`, class>
#: mapping element type enumeration with the corresponding controller pool class
#: (:class:`~sardana.pool.poolcontroller.PoolController` or sub-class of it).
CTRL_TYPE_MAP = {
    ET.Motor          : PoolController,
    ET.CTExpChannel   : PoolController,
    ET.OneDExpChannel : PoolController,
    ET.TwoDExpChannel : PoolController,
    ET.PseudoMotor    : PoolPseudoMotorController,
    ET.PseudoCounter  : PoolPseudoCounterController,
    ET.IORegister     : PoolController,
}

#: dictionary dict<:data:`~sardana.ElementType`, :class:`tuple`>
#: where tuple is a sequence:
#:
#: #. type string representation
#: #. family
#: #. internal pool class
#: #. automatic full name
#: #. controller class
TYPE_MAP = {
    ET.Controller       : ("Controller", "Controller", CTRL_TYPE_MAP, "controller/{klass}/{name}", Controller),
    ET.Instrument       : ("Instrument", "Instrument", PoolInstrument, "{full_name}", None),
    ET.Motor            : ("Motor", "Motor", PoolMotor, "motor/{ctrl_name}/{axis}", MotorController),
    ET.CTExpChannel     : ("CTExpChannel", "ExpChannel", PoolCounterTimer, "expchan/{ctrl_name}/{axis}", CounterTimerController),
    ET.ZeroDExpChannel  : ("ZeroDExpChannel", "ExpChannel", Pool0DExpChannel, "expchan/{ctrl_name}/{axis}", ZeroDController),
    ET.OneDExpChannel   : ("OneDExpChannel", "ExpChannel", Pool1DExpChannel, "expchan/{ctrl_name}/{axis}", OneDController),
    ET.TwoDExpChannel   : ("TwoDExpChannel", "ExpChannel", Pool2DExpChannel, "expchan/{ctrl_name}/{axis}", TwoDController),
    ET.PseudoMotor      : ("PseudoMotor", "Motor", PoolPseudoMotor, "pm/{ctrl_name}/{axis}", PseudoMotorController),
    ET.PseudoCounter    : ("PseudoCounter", "ExpChannel", PoolPseudoCounter, "pc/{ctrl_name}/{axis}", PseudoCounterController),
    ET.MotorGroup       : ("MotorGroup", "MotorGroup", PoolMotorGroup, "mg/{pool_name}/{name}", None),
    ET.MeasurementGroup : ("MeasurementGroup", "MeasurementGroup", PoolMeasurementGroup, "mntgrp/{pool_name}/{name}", None),
    ET.IORegister       : ("IORegister", "IORegister"      , PoolIORegister, "ioregister/{ctrl_name}/{axis}", IORegisterController),
}

class TypeData(object):
    """Information for a specific Element type"""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

#: dictionary
#: dict<:data:`~sardana.ElementType`, :class:`~sardana.pool.poolmetacontroller.TypeData`>
TYPE_MAP_OBJ = {}
for t, d in TYPE_MAP.items():
    o = TypeData(type=t, name=d[0], family=d[1], klass=d[2] ,
                 auto_full_name=d[3], ctrl_klass=d[4])
    TYPE_MAP_OBJ[t] = o


class ControllerLibrary(SardanaLibrary):
    """Object representing a python module containning controller classes.
    Public members:

        - module - reference to python module
        - f_path - complete (absolute) path and filename
        - f_name - filename (including file extension)
        - path - complete (absolute) path
        - name - module name (without file extension)
        - controller_list - list<ControllerClass>
        - exc_info - exception information if an error occured when loading
                     the module
    """

    def __init__(self, **kwargs):
        kwargs['manager'] = kwargs.pop('pool')
        kwargs['elem_type'] = ElementType.ControllerLibrary
        SardanaLibrary.__init__(self, **kwargs)

    add_controller = SardanaLibrary.add_meta_class
    get_controller = SardanaLibrary.get_meta_class
    get_controllers = SardanaLibrary.get_meta_classes
    has_controller = SardanaLibrary.has_meta_class

    def serialize(self, *args, **kwargs):
        kwargs = SardanaLibrary.serialize(self, *args, **kwargs)
        kwargs['pool'] = self.get_manager().name
        kwargs['id'] = InvalidId
        return kwargs

    @property
    def controllers(self):
        return self.meta_classes


class DataInfo(object):

    def __init__(self, name, dtype, dformat=DataFormat.Scalar,
                 access=DataAccess.ReadWrite, description="",
                 default_value=None, memorized='true',
                 fget=None, fset=None, maxdimsize=None):
        self.name = name
        self.dtype = dtype
        self.dformat = dformat
        self.access = access
        self.description = description
        self.default_value = default_value
        self.memorized = memorized
        self.fget = fget or "get%s" % name
        self.fset = fset or "set%s" % name
        if maxdimsize == None:
            if dformat == DataFormat.Scalar:
                maxdimsize = ()
            elif dformat == DataFormat.OneD:
                maxdimsize = 2048,
            elif dformat == DataFormat.TwoD:
                maxdimsize = 2048, 2048
        self.maxdimsize = maxdimsize

    def copy(self):
        s = self
        d = DataInfo(s.name, s.dtype, dformat=s.dformat, access=s.access,
                     description=s.description, default_value=s.default_value,
                     memorized=s.memorized, fget=s.fget, fset=s.fset,
                     maxdimsize=self.maxdimsize)
        return d

    @classmethod
    def toDataInfo(klass, name, info):
        info = CaselessDict(info)
        dtype = info[Type]
        dtype, dformat = to_dtype_dformat(dtype)
        default_value = info.get(DefaultValue)
        description = info.get(Description, '')
        daccess = info.get(Access, DataAccess.ReadWrite)
        daccess = to_daccess(daccess)
        memorized = info.get(Memorize, Memorized)
        maxdimsize = info.get(MaxDimSize)
        fget = info.get(FGet)
        fset = info.get(FSet)
        if default_value is not None and dtype != DataType.String:
            if type(default_value) in types.StringTypes:
                default_value = eval(default_value)
        return DataInfo(name, dtype, dformat=dformat, access=daccess,
                        description=description, default_value=default_value,
                        memorized=memorized, fget=fget, fset=fset,
                        maxdimsize=maxdimsize)

    def toDict(self):
        return { 'name' : self.name, 'type' : DataType.whatis(self.dtype),
                 'format' : DataFormat.whatis(self.dformat),
                 'access' : DataAccess.whatis(self.access),
                 'description' : self.description,
                 'default_value' : self.default_value,
                 'memorized' : self.memorized,
                 'maxdimsize' : self.maxdimsize }

    def serialize(self, *args, **kwargs):
        kwargs.update(self.toDict())
        return kwargs

    def __repr__(self):
        return "{0}(name={1}, type={2}, format={3}, access={4})".format(
            self.__class__.__name__, self.name, DataType[self.dtype],
            DataFormat[self.dformat], DataAccess[self.access])

#class PropertyInfo(DataInfo):

#    def __init__(self, name, dtype, dformat=DataFormat.Scalar,
#                 description="", default_value=None):
#        DataInfo.__init__(self, name, dtype, dformat, access=DataAcces.ReadWrite,
#                          description=description, default_value=default_value)


#class AttributeInfo(DataInfo):

#    def __init__(self, name, dtype, dformat=DataFormat.Scalar,
#                 access=DataAccess.ReadWrite, description=""):
#        DataInfo.__init__(self, name, dtype, dformat, access=DataAcces.ReadWrite,
#                          description=description, default_value=None)

class ControllerClass(SardanaClass):
    """Object representing a python controller class.
       Public members:

           - name - class name
           - klass - python class object
           - lib - ControllerLibrary object representing the module where the
             controller is."""

    def __init__(self, **kwargs):
        kwargs['manager'] = kwargs.pop('pool')
        kwargs['elem_type'] = ElementType.ControllerClass
        SardanaClass.__init__(self, **kwargs)

        self.types = []
        self.dict_extra = {}
        self.api_version = 1

        klass = self.klass
        # Generic controller information
        self.ctrl_features = tuple(klass.ctrl_features)

        self.ctrl_properties = props = CaselessDict()
        for k, v in klass.class_prop.items():  # old member
            props[k] = DataInfo.toDataInfo(k, v)
        for k, v in klass.ctrl_properties.items():
            props[k] = DataInfo.toDataInfo(k, v)

        self.ctrl_attributes = ctrl_attrs = CaselessDict()
        for k, v in klass.ctrl_attributes.items():
            ctrl_attrs[k] = DataInfo.toDataInfo(k, v)

        self.axis_attributes = axis_attrs = CaselessDict()
        for k, v in klass.ctrl_extra_attributes.items():  # old member
            axis_attrs[k] = DataInfo.toDataInfo(k, v)
        for k, v in klass.axis_attributes.items():
            axis_attrs[k] = DataInfo.toDataInfo(k, v)

        self.types = types = self.__build_types()
        self.type_names = map(ElementType.whatis, types)

        if ElementType.PseudoMotor in types:
            self.motor_roles = tuple(klass.motor_roles)
            self.pseudo_motor_roles = tuple(klass.pseudo_motor_roles)
            if len(self.pseudo_motor_roles) == 0:
                self.pseudo_motor_roles = (klass.__name__,)
            self.dict_extra['motor_roles'] = self.motor_roles
            self.dict_extra['pseudo_motor_roles'] = self.pseudo_motor_roles

        if ElementType.PseudoCounter in types:
            self.counter_roles = tuple(klass.counter_roles)
            self.pseudo_counter_roles = tuple(klass.pseudo_counter_roles)
            if len(self.pseudo_counter_roles) == 0:
                self.pseudo_counter_roles = (klass.__name__,)
            self.dict_extra['counter_roles'] = self.counter_roles
            self.dict_extra['pseudo_counter_roles'] = self.pseudo_counter_roles

        if ElementType.IORegister in types:
            self.dict_extra['predefined_values'] = klass.predefined_values

        init_args = inspect.getargspec(klass.__init__)
        if init_args.varargs is None or init_args.keywords is None:
            self.api_version = 0

    def __build_types(self):
        types = []
        klass = self.klass
        for _type, type_data in TYPE_MAP_OBJ.items():
            if not _type in TYPE_ELEMENTS:
                continue
            if issubclass(klass, type_data.ctrl_klass):
                types.append(_type)
        return types

    def serialize(self, *args, **kwargs):
        kwargs = SardanaClass.serialize(self, *args, **kwargs)
        kwargs['id'] = InvalidId
        kwargs['pool'] = self.get_manager().name
        kwargs['gender'] = self.gender
        kwargs['model'] = self.model
        kwargs['organization'] = self.organization
        kwargs['types'] = self.type_names
        if len(self.type_names):
            kwargs['main_type'] = self.type_names[0]
        else:
            kwargs['main_type'] = None
        kwargs['api_version'] = self.api_version
        kwargs.update(self.dict_extra)
        return kwargs

    @property
    def controller_class(self):
        return self.klass

    @property
    def gender(self):
        return self.klass.gender

    @property
    def model(self):
        return self.klass.model

    @property
    def organization(self):
        return self.klass.organization



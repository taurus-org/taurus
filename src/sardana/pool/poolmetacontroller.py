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

"""This module is part of the Python Pool libray. It defines the base classes
for"""

__all__ = ["ControllerLib", "DTYPE_MAP", "DACCESS_MAP", "DataInfo",
           "ControllerClass"]

__docformat__ = 'restructuredtext'

import inspect
import os
import operator
import types
import json

from taurus.core.util import CaselessDict, CodecFactory

from sardana import DataType, DataFormat, DataAccess
from pooldefs import *

class ControllerLib(object):
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
    
    def __init__(self, module=None, f_path=None, exc_info=None):
        self.module = module
        if module is not None:
            f_path = os.path.abspath(module.__file__)
        self.f_path = f_path
        if f_path is None:
            self.path= None
            self.f_name = None
            self.name = None
        else:
            if self.f_path.endswith(".pyc"):
                self.f_path = self.f_path[:-1]
            self.path, self.f_name = os.path.split(self.f_path)
            self.name, _ = os.path.splitext(self.f_name)
        self.controller_list = []
        self.exc_info = exc_info
    
    def __cmp__(self, o):
        return cmp(self.name, o.name)

    def __str__(self):
        return self.getModuleName()
    
    def addController(self,controller_data):
        self.controller_list.append(controller_data)
        
    def getController(self,controller_name):
        for m in self.controller_list:
            if m.name == controller_name:
                return m
        return None

    def getControllers(self):
        return self.controller_list

    def hasController(self,controller_name):
        return not self.getController(controller_name) is None
    
    def getName(self):
        return self.name
    
    def getModuleName(self):
        return self.name
    
    def getModule(self):
        return self.module

    def getCode(self):
        """Returns a sequence of sourcelines corresponding to the module code.
           :return: list of source code lines
           :rtype: list
        """
        mod = self.getModule()
        if mod is None:
            raise Exception("Source code not available")
        return inspect.getsourcelines(mod)[0]

    def getFileName(self):
        if self.f_path is None:
            return None
        if self.f_path.endswith('.pyc'):
            return self.f_path[:-1]
        return self.f_path
    
    def getSimpleFileName(self):
        return self.f_name
    
    def hasErrors(self):
        return self.exc_info != None
    
    def setError(self, exc_info):
        self.exc_info = exc_info
        if exc_info is None:
            self.controller_list = []
    
    def getError(self):
        return self.exc_info


class ControllerClassJSONEncoder(json.JSONEncoder):
    
    def default(self, obj):
        if isinstance(obj, ControllerClass):
            return self.controllerClass(obj)
        else:
            return json.JSONEncoder.default(self, ret)
    
    def controllerClass(self, obj):
        return obj.toDict()

DTYPE_MAP = { 'int'            : DataType.Integer,
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
              DataType.Boolean : DataType.Boolean, }

DACCESS_MAP = { 'read'               : DataAccess.ReadOnly,
                DataAccess.ReadOnly  : DataAccess.ReadOnly,
                'readwrite'          : DataAccess.ReadWrite,
                DataAccess.ReadWrite : DataAccess.ReadWrite,}

def from_dtype_str(dtype):
    dformat = DataFormat.Scalar
    if type(dtype) == str:
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

class DataInfo(object):
    
    def __init__(self, name, dtype, dformat=DataFormat.Scalar,
                 access=DataAccess.ReadWrite, description="", default_value=None,
                 fget=None, fset=None):
        self.name = name
        self.dtype = dtype
        self.dformat = dformat
        self.access = access
        self.description = description
        self.default_value = default_value
        self.fget = fget or "get%s" % name
        self.fset = fset or "set%s" % name
    
    @classmethod
    def toDataInfo(klass, name, info):
        info = CaselessDict(info)
        dformat = DataFormat.Scalar
        dtype = info['type']
        if type(dtype) == str:
            dtype, dformat = from_dtype_str(dtype)
        elif operator.isSequenceType(dtype):
            dformat = DataFormat.OneD
            dtype = dtype[0]
            if type(dtype) == str:
                dtype, dformat2 = from_dtype_str(dtype)
                if dformat2 == DataFormat.OneD:
                    dformat = DataFormat.TwoD
            elif operator.isSequenceType(dtype):
                dformat = DataFormat.TwoD
                dtype = dtype[0]
                if type(dtype) == str:
                    dtype, _ = from_dtype_str(dtype)
        dtype = DTYPE_MAP[dtype]
        default_value = info.get('defaultvalue')
        description = info.get('description', '')
        access = info.get('r/w type', DataAccess.ReadWrite)
        access = DACCESS_MAP[access]
        fget = info.get('fget')
        fset = info.get('fset')
        if default_value is not None and dtype != DataType.String:
            if type(default_value) in types.StringTypes:
                default_value = eval(default_value)
        return DataInfo(name, dtype, dformat, access, description, default_value,
                        fget, fset)
    
    def toDict(self):
        return { 'name' : self.name, 'type' : DataType.whatis(self.dtype),
                 'format' : DataFormat.whatis(self.dformat),
                 'access' : DataAccess.whatis(self.access),
                 'description' : self.description,
                 'default_value' : self.default_value }
        
    def getJSON(self):
        return json.dumps(self.toDict())


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


class ControllerClass(object):
    """Object representing a python controller class. 
       Public members:
           name - class name
           klass - python class object
           lib - ControllerLib object representing the module where the controller is.
    """
    
    NoDoc = '<Undocumented controller>'
    
    def __init__(self, lib, klass, name=None):
        self.klass = klass
        self.name = name or klass.__name__
        self.lib = lib
        self.types = []
        self.errors = []
        self.__init()
        
    def __init(self):
        klass = self.klass
        self._ctrl_features = tuple(klass.ctrl_features)
        
        self._ctrl_properties = props = CaselessDict()
        for k, v in klass.class_prop.items(): # old member
            props[k] = DataInfo.toDataInfo(k, v)
        for k, v in klass.ctrl_properties.items():
            props[k] = DataInfo.toDataInfo(k, v)
        
        self._ctrl_attributes = ctrl_attrs = CaselessDict()
        for k, v in klass.ctrl_attributes.items():
            ctrl_attrs[k] = DataInfo.toDataInfo(k, v)
        
        self._axis_attributes = axis_attrs = CaselessDict()
        for k, v in klass.ctrl_extra_attributes.items(): # old member
            axis_attrs[k] = DataInfo.toDataInfo(k, v)
        for k, v in klass.axis_attributes.items():
            axis_attrs[k] = DataInfo.toDataInfo(k, v)
        
    def __cmp__(self, o):
        if o is None: return cmp(self.getName(), None)
        return cmp(self.getName(), o.getName())

    def __str__(self):
        return self.getName()

    def toDict(self):
        ret = { 'name' : self.getName(),
          'module' : self.getModuleName(),
          'filename' : self.getFileName(),
          'description' : self.getDescription(),
          'gender' : self.getGender(),
          'model' : self.getModel(),
          'organization' : self.getOrganization(),}
        
        ctrl_props = {}
        for name, ctrl_prop in self.getControllerProperties().items():
            ctrl_props[name] = ctrl_prop.toDict()
        ctrl_attrs = {}
        for name, ctrl_attr in self.getControllerAttributes().items():
            ctrl_attrs[name] = ctrl_attr.toDict()
        axis_attrs = {}
        for name, axis_attr in self.getAxisAttributes().items():
            axis_attrs[name] = axis_attr.toDict()
        
        ret['ctrl_properties'] = ctrl_props
        ret['ctrl_attributes'] = ctrl_attrs
        ret['axis_attributes'] = axis_attrs
        ret['ctrl_features'] = self.getControllerFeatures()
        return ret

    def getJSON(self):
        json_codec = CodecFactory().getCodec('json')
        format, data = json_codec.encode(('', self), cls=ControllerClassJSONEncoder)
        return data

    def setTypes(self, types):
        self.types = types

    def getTypes(self):
        return self.types

    def getControllerLib(self):
        return self.lib
    
    def getControllerClass(self):
        return self.klass

    def getName(self):
        return self.name

    def getFullName(self):
        return '%s.%s' % (self.getModuleName(), self.getName())

    def getModuleName(self):
        return self.getControllerLib().getModuleName()

    def getFileName(self):
        return self.getControllerLib().getFileName()
    
    def getSimpleFileName(self):
        return self.getControllerLib().getSimpleFileName()
    
    def getDescription(self):
        return self.getControllerClass().__doc__ or ControllerClass.NoDoc

    def getBriefDescription(self, max_chars=60):
        d = self.getControllerClass().__doc__ or ControllerClass.NoDoc
        d = d.replace('\n',' ')
        if len(d) > max_chars: d = d[:max_chars-5] + '[...]'
        return d
    
    def getCode(self):
        """Returns a tuple (sourcelines, firstline) corresponding to the 
        definition of the controller class. sourcelines is a list of source code 
        lines. firstline is the line number of the first source code line.
        """
        return inspect.getsourcelines(self.getControllerClass())
    
    def getGender(self):
        return self.getControllerClass().gender
    
    def getModel(self):
        return self.getControllerClass().model
    
    def getOrganization(self):
        return self.getControllerClass().organization
    
    def getImage(self):
        return self.getControllerClass().image
    
    def getLogo(self):
        return self.getControllerClass().logo
    
    def getControllerProperties(self):
        return self._ctrl_properties
    
    def getControllerAttributes(self):
        return self._ctrl_attributes
    
    def getAxisAttributes(self):
        return self._axis_attributes
    
    def getControllerFeatures(self):
        return self._ctrl_features

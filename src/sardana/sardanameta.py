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

"""This module is part of the Python Sardana libray. It defines the base classes
for MetaLib and MetaClass"""

__all__ = ["SardanaMetaLib", "SardanaMetaClass"]

__docformat__ = 'restructuredtext'

import inspect
import os
import operator
import types

from taurus.core.util import CaselessDict, CodecFactory

from sardanabase import SardanaBaseObject


class SardanaMetaLib(SardanaBaseObject):
    """Object representing a python module containning sardana classes.
       Public members:
       
           - module - reference to python module
           - f_path - complete (absolute) path (with file name at the end)
           - f_name - file name (including file extension)
           - path - complete (absolute) path
           - name - module name (without file extension)
           - meta_classes - dict<str, SardanMetaClass>
           - exc_info - exception information if an error occured when loading 
                        the module"""
    def __init__(self, **kwargs):
        self.module = module = kwargs.pop('module', None)
        self.f_path = f_path = kwargs.pop('f_path', None)
        self.exc_info = exc_info = kwargs.pop('exc_info', None)
        if module is not None:
            f_path = os.path.abspath(module.__file__)
        self.f_path = f_path
        if f_path is None:
            self.path= kwargs.get('path', None)
            self.f_name = kwargs.get('f_name', None)
            name = kwargs.get('name', None)
        else:
            if self.f_path.endswith(".pyc"):
                self.f_path = self.f_path[:-1]
            self.path, self.f_name = os.path.split(self.f_path)
            name, _ = os.path.splitext(self.f_name)
        self.meta_classes = {}
        kwargs['name'] = name
        kwargs['full_name'] = f_path
        SardanaBaseObject.__init__(self, **kwargs)
    
    def __cmp__(self, o):
        return cmp(self.full_name, o.full_name)
    
    def __str__(self):
        return self.name
    
    def add_meta_class(self, meta_class):
        self.meta_classes[meta_class.name] = meta_class
        
    def get_meta_class(self, meta_class_name):
        return self.meta_classes.get(meta_class_name)

    def get_meta_classes(self):
        return self.meta_classes.values()

    def has_meta_class(self, meta_class_name):
        return meta_class_name in self.meta_classes
    
    def get_name(self):
        return self.name
    
    def get_module_name(self):
        return self.name
    
    def get_module(self):
        return self.module

    def get_description(self):
        mod = self.get_module()
        if mod is None:
            return None
        return mod.__doc__
    
    def get_code(self):
        """Returns a sequence of sourcelines corresponding to the module code.
           :return: list of source code lines
           :rtype: list
        """
        mod = self.get_module()
        if mod is None:
            raise Exception("Source code not available")
        return inspect.getsourcelines(mod)[0]

    def get_file_name(self):
        if self.f_path is None:
            return None
        if self.f_path.endswith('.pyc'):
            return self.f_path[:-1]
        return self.f_path
    
    def get_simple_file_name(self):
        return self.f_name
    
    def has_errors(self):
        return self.exc_info != None
    
    def set_error(self, exc_info):
        self.exc_info = exc_info
        if exc_info is None:
            self.meta_classes = {}
    
    def get_error(self):
        return self.exc_info
    
    def serialize(self, *args, **kwargs):
        kwargs = SardanaBaseObject.serialize(self, *args, **kwargs)
        kwargs['id'] = 0
        kwargs['module'] = self.name
        kwargs['f_name'] = self.f_path
        kwargs['filename'] = self.f_name
        kwargs['path'] = self.path
        kwargs['description'] = self.get_description()
        kwargs['elements'] = self.meta_classes.keys()
        return kwargs
    
    def str(self, *args, **kwargs):
        raise NotImplementedError


class SardanaMetaClass(SardanaBaseObject):
    pass

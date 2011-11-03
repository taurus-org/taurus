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

import os
import inspect
import weakref
import operator
import types

from taurus.core.util import CaselessDict, CodecFactory

from sardanabase import SardanaBaseObject


class SardanaMetaLib(SardanaBaseObject):
    """Object representing a python module containning sardana classes.
       Public members:
       
           - module - reference to python module
           - file_path - complete (absolute) path (with file name at the end)
           - file_name - file name (including file extension)
           - path - complete (absolute) path
           - name - (=module name) module name (without file extension)
           - meta_classes - dict<str, SardanMetaClass>
           - exc_info - exception information if an error occured when loading 
                        the module"""
    
    description = '<Undocumented>'
    
    def __init__(self, **kwargs):
        self.module = module = kwargs.pop('module', None)
        self.file_path = file_path = kwargs.pop('file_path', None)
        self.exc_info = exc_info = kwargs.pop('exc_info', None)
        if module is not None:
            file_path = os.path.abspath(module.__file__)
        self.file_path = file_path
        if file_path is None:
            self.path= kwargs.get('path', None)
            self.file_name = kwargs.get('file_name', None)
            name = kwargs.get('name', None)
        else:
            if self.file_path.endswith(".pyc"):
                self.file_path = self.file_path[:-1]
            self.path, self.file_name = os.path.split(self.file_path)
            name, _ = os.path.splitext(self.file_name)
        self.meta_classes = {}
        if module is not None and module.__doc__:
            self.description = module.__doc__
        kwargs['name'] = name
        kwargs['full_name'] = file_path
        SardanaBaseObject.__init__(self, **kwargs)
    
    def __cmp__(self, o):
        return cmp(self.full_name, o.full_name)
    
    def __str__(self):
        return self.name
    
    @property
    def module_name(self):
        """Returns the module name for this library.
        
        :return: the module name
        :rtype: str"""
        return self.name
    
    @property
    def code(self):
        """Returns a sequence of sourcelines corresponding to the module code.
        
           :return: list of source code lines
           :rtype: list<str>"""
        mod = self.get_module()
        if mod is None:
            raise Exception("Source code not available")
        return inspect.getsourcelines(mod)[0]
    
    def add_meta_class(self, meta_class):
        """Adds a new :class:~`sardana.sardanameta.SardanaMetaClass` to this
        library.
        
        :param meta_class: the meta class to be added to this library
        :type meta_class: :class:~`sardana.sardanameta.SardanaMetaClass`"""
        self.meta_classes[meta_class.name] = meta_class
    
    def get_meta_class(self, meta_class_name):
        """Returns a :class:~`sardana.sardanameta.SardanaMetaClass` for the
        given meta class name or None if the meta class does not exist in this
        library.
        
        :param meta_class_name: the meta class name
        :type meta_class_name: str
        :return: a meta class or None
        :rtype: :class:~`sardana.sardanameta.SardanaMetaClass`"""
        return self.meta_classes.get(meta_class_name)
    
    def get_meta_classes(self):
        """Returns a sequence of the meta classes that belong to this library.
        
        :return: a sequence of meta classes that belong to this library
        :rtype: seq<:class:~`sardana.sardanameta.SardanaMetaClass`>"""
        return self.meta_classes.values()

    def has_meta_class(self, meta_class_name):
        """Returns True if the given meta class name belongs to this library
        or False otherwise.
        
        :param meta_class_name: the meta class name
        :type meta_class_name: str
        
        :return: True if the given meta class name belongs to this library
                 or False otherwise
        :rtype: bool"""
        return meta_class_name in self.meta_classes
    
    def get_name(self):
        """Returns the module name for this library (same as
        :meth:~sardana.sardanameta.SardanaMetaLib.get_module_name).
        
        :return: the module name
        :rtype: str"""
        return self.name
    
    def get_module_name(self):
        """Returns the module name for this library (same as
        :meth:~sardana.sardanameta.SardanaMetaLib.get_name).
        
        :return: the module name
        :rtype: str"""
        return self.module_name
    
    def get_module(self):
        """Returns the python module for this library.
        
        :return: the python module
        :rtype: object"""
        return self.module
    
    def get_description(self):
        """Returns the this library documentation or "<Undocumented>" if no
        documentation exists.
        
        :return: this library documentation or None
        :rtype: str"""
        return self.description
    
    def get_code(self):
        """Returns a sequence of sourcelines corresponding to the module code.
        
       :return: list of source code lines
       :rtype: list<str>"""
        return self.code
    
    def get_file_path(self):
        """Returns the file path for this library. On posix systems is something
        like: /abs/path/filename.py
        
        :return: this library file path
        :rtype: str"""
        if self.file_path is None:
            return None
        if self.file_path.endswith('.pyc'):
            return self.file_path[:-1]
        return self.file_path
    
    def get_file_name(self):
        """Returns the file name for this library. On posix systems is something
        like: filename.py
        
        :return: this library file name
        :rtype: str"""
        return self.file_name
    
    def has_errors(self):
        """Returns True if this library has syntax errors or False otherwise.
        
        :return: True if this library has syntax errors or False otherwise
        :rtype: bool"""
        return self.exc_info != None
    
    def set_error(self, exc_info):
        """Sets the error information for this library
        
        :param exc_info: error information. It must be an object similar to the
                         one returned by :func:`sys.exc_info`
        :type exc_info: tuple<type, value, traceback>"""
        self.exc_info = exc_info
        if exc_info is None:
            self.meta_classes = {}
    
    def get_error(self):
        """Gets the error information for this library or None if no error
        exists
        
        :return: error information. An object similar to the one returned by
                 :func:`sys.exc_info`
        :rtype: tuple<type, value, traceback>"""
        return self.exc_info
    
    def serialize(self, *args, **kwargs):
        """Returns a serializable object describing this object.
        
        :return: a serializable dict
        :rtype: dict"""
        kwargs = SardanaBaseObject.serialize(self, *args, **kwargs)
        kwargs['id'] = 0
        kwargs['module'] = self.name
        kwargs['file_path'] = self.file_path
        kwargs['file_name'] = self.file_name
        kwargs['path'] = self.path
        kwargs['description'] = self.description
        kwargs['elements'] = self.meta_classes.keys()
        return kwargs


class SardanaMetaClass(SardanaBaseObject):
    """Object representing a python class."""
    
    description = '<Undocumented>'
    
    def __init__(self, **kwargs):
        lib = kwargs.pop('lib')
        self._lib = weakref.ref(lib)
        self.klass = kwargs.pop('klass')
        doc = self.klass.__doc__
        if doc:
            self.description = doc
        kwargs['name'] = name = kwargs.pop('name', self.klass.__name__)
        kwargs['full_name'] = "{0}.{1}".format(lib.name, name)
        kwargs['parent'] = kwargs.pop('parent', self.lib)
        SardanaBaseObject.__init__(self, **kwargs)
    
    @property
    def lib(self):
        """Returns the library :class:~`sardana.sardanameta.SardanaMetaLib` for
        this class.
        
        :return: a reference to the library where this class is located
        :rtype: :class:~`sardana.sardanameta.SardanaMetaLib`"""
        return self._lib()
    
    @property
    def module(self):
        """Returns the python module for this class.
        
        :return: the python module
        :rtype: object"""
        return self.lib.module
    
    @property
    def module_name(self):
        """Returns the module name for this class.
        
        :return: the module name
        :rtype: str"""
        return self.lib.get_module_name()
    
    @property
    def file_path(self):
        """Returns the file path for for the library where this class is. On
        posix systems is something like: /abs/path/filename.py
        
        :return: the file path for for the library where this class is
        :rtype: str"""
        return self.lib.file_path
    
    @property
    def file_name(self):
        """Returns the file name for the library where this class is. On posix
        systems is something like: filename.py
        
        :return: the file name for the library where this class is
        :rtype: str"""
        return self.lib.file_name

    @property
    def path(self):
        """Returns the absolute path for the library where this class is. On
        posix systems is something like: /abs/path
        
        :return: the absolute path for the library where this class is
        :rtype: str"""
        return self.lib.path
    
    @property
    def code(self):
        """Returns a tuple (sourcelines, firstline) corresponding to the 
        definition of the controller class. sourcelines is a list of source code
        lines. firstline is the line number of the first source code line."""
        return inspect.getsourcelines(self.klass)
    
    def get_code(self):
        """Returns a tuple (sourcelines, firstline) corresponding to the 
        definition of the controller class. sourcelines is a list of source code
        lines. firstline is the line number of the first source code line."""
        return self.code
        
    def serialize(self, *args, **kwargs):
        """Returns a serializable object describing this object.
        
        :return: a serializable dict
        :rtype: dict"""
        kwargs = SardanaBaseObject.serialize(self, *args, **kwargs)
        kwargs['id'] = 0
        kwargs['module'] = self.module_name
        kwargs['file_name'] = self.file_name
        kwargs['file_path'] = self.file_path
        kwargs['path'] = self.path
        kwargs['description'] = self.description
        return kwargs
    
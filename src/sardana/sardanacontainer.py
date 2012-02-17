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
for a pool container element"""

__all__ = ["SardanaContainer"]

__docformat__ = 'restructuredtext'

from taurus.core.util import CaselessDict
from sardanadefs import InvalidId, ElementType

class SardanaContainer(object):
    """A container class for sardana elements"""
    
    def __init__(self):
        
        # map of all elements
        # key - element ID
        # value - pointer to the element object
        self._element_ids = {}

        # map of all elements by name
        # key - element name
        # value - pointer to the element object
        self._element_names = CaselessDict()

        # map of all elements by name
        # key - element full name
        # value - pointer to the element object
        self._element_full_names = CaselessDict()
    
        # map of all elements by type
        # key - element type
        # value - map where:
        #    key - element ID
        #    value - pointer to the element object
        self._element_types = {}
        
    def add_element(self, e):
        """Adds a new :class:`pool.PoolObject` to this container
           
           :param e: the pool element to be added
           :type e: :class:`pool.PoolObject`
        """
        name, full_name, id = e.get_name(), e.get_full_name(), e.get_id()
        elem_type = e.get_type()
        self._element_ids[id] = e
        self._element_names[name] = e
        self._element_full_names[full_name] = e
        type_elems = self._element_types.get(elem_type)
        if type_elems is None:
            self._element_types[elem_type] = type_elems = {}
        type_elems[id] = e
        return e
    
    def remove_element(self, e):
        """Removes the :class:`pool.PoolObject` from this container
           
           :param e: the pool object to be removed
           :type e: :class:`pool.PoolObject`
           
           :throw: KeyError
        """
        name, full_name, id = e.get_name(), e.get_full_name(), e.get_id()
        elem_type = e.get_type()
        del self._element_ids[id]
        del self._element_names[name]
        del self._element_full_names[full_name]
        type_elems = self._element_types.get(elem_type)
        del type_elems[id]
        
    def get_element_id_map(self):
        """Returns a reference to the internal pool object ID map
           
           :return: the internal pool object ID map
           :rtype: dict<id, pool.PoolObject>
        """
        return self._element_ids
    
    def get_element_name_map(self):
        """Returns a reference to the internal pool object name map
           
           :return: the internal pool object name map
           :rtype: dict<str, pool.PoolObject>
        """
        return self._element_names
    
    def get_element_type_map(self):
        """Returns a reference to the internal pool object type map
           
           :return: the internal pool object type map
           :rtype: dict<pool.ElementType, dict<id, pool.PoolObject>>
        """
        return self._element_types
    
    def get_element(self, **kwargs):
        """Returns a reference to the requested pool object
           
           :param kwargs: if key 'id' given: search by ID
                          else if key 'full_name' given: search by full name
                          else if key 'name' given: search by name
           
           :return: the pool object 
           :rtype: pool.PoolObject
           
           :throw: KeyError
        """
        if kwargs.has_key("id"):
            id = kwargs.pop("id")
            return self.get_element_by_id(id, **kwargs)
        
        if kwargs.has_key("full_name"):
            full_name = kwargs.pop("full_name")
            return self.get_element_by_full_name(full_name, **kwargs)
        
        name = kwargs.pop("name")
        return self.get_element_by_name(name, **kwargs)
    
    def get_element_by_name(self, name, **kwargs):
        """Returns a reference to the requested pool object
           
           :param name: pool object name
           :type name: str
           
           :return: the pool object 
           :rtype: pool.PoolObject
           
           :throw: KeyError
        """
        ret = self._element_names.get(name)
        if ret is None:
            raise KeyError("There is no element with name '%s'" % name)
        return ret
    
    def get_element_by_full_name(self, full_name, **kwargs):
        """Returns a reference to the requested pool object
           
           :param name: pool object full name
           :type name: str
           
           :return: the pool object 
           :rtype: pool.PoolObject
           
           :throw: KeyError
        """
        ret = self._element_full_names.get(full_name)
        if ret is None: 
            raise KeyError("There is no element with full name '%s'" % full_name)
        return ret
        
    def get_element_by_id(self, id, **kwargs):
        """Returns a reference to the requested pool object
           
           :param id: pool object ID
           :type id: int
           
           :return: the pool object 
           :rtype: pool.PoolObject
           
           :throw: KeyError
        """
        ret = self._element_ids.get(id)
        if ret is None: 
            raise KeyError("There is no element with ID '%d'" % id)
        return ret
    
    def get_elements_by_type(self, t):
        """Returns a list of all pool objects of the given type
           
           :param t: element type
           :type t: pool.ElementType
           
           :return: list of pool objects
           :rtype: seq<pool.PoolObject>
        """
        elem_types_dict = self._element_types.get(t)
        if elem_types_dict is None:
            return  []
        return elem_types_dict.values()

    def get_element_names_by_type(self, t):
        """Returns a list of all pool object names of the given type
           
           :param t: element type
           :type t: pool.ElementType
           
           :return: list of pool object names
           :rtype: seq<str>
        """
        return [ elem.get_name() for elem in self.get_elements_by_type(t) ]
        
    def rename_element(self, old_name, new_name):
        """Rename a pool object
           
           :param old_name: old pool object name
           :type old_name: str
           :param new_name: new pool object name
           :type new_name: str
        """
        raise NotImplementedError

    def check_element(self, name, full_name):
        raise_element_name = True
        try:
            elem = self.get_element(name=name)
        except:
            raise_element_name = False
        if raise_element_name:
            elem_type = ElementType[elem.get_type()]
            raise Exception("A %s with name '%s' already exists"
                            % (elem_type, name))
        
        raise_element_full_name = True
        try:
            elem = self.get_element(full_name=full_name)
        except:
            raise_element_full_name = False
        if raise_element_full_name:
            elem_type = ElementType[elem.get_type()]
            raise Exception("A %s with full name '%s' already exists"
                            % (elem_type, full_name))
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

__all__ = [ "PoolGroupElement" ]

__docformat__ = 'restructuredtext'

from pooldefs import *
from poolelement import PoolBaseElement
from poolcontainer import PoolContainer

class PoolGroupElement(PoolContainer, PoolBaseElement):

    def __init__(self, **kwargs):
        user_elem_ids = kwargs.pop('user_elements')
        PoolContainer.__init__(self)
        PoolBaseElement.__init__(self, **kwargs)
        
        self._user_elements = []

        pool = self.pool
        for id in user_elem_ids:
            self.add_user_element(pool.get_element(id=id))

    def on_element_changed(self, evt_src, evt_type, evt_value):
        pass

    def get_action_cache(self):
        return self._action_cache
    
    def set_action_cache(self, action_cache):
        if self._action_cache is not None:
            for element in self._user_elements:
                action_cache.remove_element(element)
            
        self._action_cache = action_cache
        
        for element in self._user_elements:
            action_cache.add_element(element)
    
    def get_user_elements(self):
        return self._user_elements
    
    def add_user_element(self, element, index=None):
        if element in self._user_elements:
            raise Exception("Group already contains %s" % element.name)
        if index is None:
            index = len(self._user_elements)
        self._user_elements.insert(index, element)
        self.add_element(element)
        if self._action_cache:
            self._action_cache.add_element(element)
        element.add_listener(self.on_element_changed)
        
    def remove_user_element(self, element):
        try:
            idx = self._user_elements.index(element)
        except ValueError:
            raise Exception("Group doesn't contain %s" % element.name)
        element.remove_listener(self.on_element_changed)
        del self._user_elements[idx]
        self.remove_element(element)

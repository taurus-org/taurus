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

"""This module is part of the Python Pool libray. It defines the
PoolPseudoCounter class"""

__all__ = [ "PoolPseudoCounter" ]

__docformat__ = 'restructuredtext'

from sardana import State, ElementType, TYPE_PHYSICAL_ELEMENTS
from sardana.sardanaevent import EventType
from sardana.sardanaattribute import SardanaAttribute

from poolelement import PoolBaseElement, PoolElement
from poolgroupelement import PoolBaseGroup


class Value(SardanaAttribute):
    pass


class PoolPseudoCounter(PoolBaseGroup, PoolElement):
    """A class representing a Pseudo Counter in the Sardana Device Pool"""
    
    def __init__(self, **kwargs):
        self._physical_values = {}
        self._low_level_physical_values = {}
        self._value = Value(self)
        self._siblings = None
        user_elements = kwargs.pop('user_elements')
        PoolElement.__init__(self, **kwargs)
        PoolBaseGroup.__init__(self, user_elements=user_elements)
    
    def serialize(self, *args, **kwargs):
        kwargs = PoolElement.serialize(self, *args, **kwargs)
        elements = [ elem.name for elem in self.get_user_elements() ]
        physical_elements = []
        for elem_list in self.get_physical_elements().values():
            for elem in elem_list:
                physical_elements.append(elem.name)
        cl_name = self.__class__.__name__
        cl_name = cl_name[4:]
        kwargs['elements'] = elements
        kwargs['physical_elements'] = physical_elements
        return kwargs
    
    def _get_pool(self):
        return self.pool

    def get_type(self):
        return ElementType.PseudoCounter
    
    def calc(self, physical_values=None):
        """Calculate the pseudo counter value.
        
        :param physical_values:
            current values of underlying elements. Default is None meaning fetch
            values
        :return:
            the pseudo counter value info
        :rtype:
            :obj:`tuple` <:class:`~numbers.Number`/:obj:`None`, exc_info/:obj:`None`>"""
        if physical_values is None:
            physical_values = self.get_physical_values()
        user_elements = self.get_user_elements()
        phy_values = [ physical_values[elem].value for elem in user_elements ]
        return self.controller.calc(self.axis, phy_values, None)
    
    def get_value(self, cache=True, propagate=1):
        """Returns the pseudo counter value.
        
        :param cache:
            if ``True`` (default) return value in cache, otherwise read value
            from hardware
        :type cache:
            bool
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int
        :return:
            the pseudo counter value
        :rtype:
            :class:`~sardana.sardanaattribute.SardanaAttribute`"""
        value = self._value
        if cache and value.has_value():
            return value
        physical_values = self.get_physical_values(cache=cache, propagate=0)
        value_info = self.calc(physical_values)
        self._set_value(value_info, propagate=propagate)
        return value
    
    def put_value(self, value_info, propagate=1):
        """Sets a new pseudo counter value.
           
        :param value_info:
            the new pseudo counter value info
        :type value_info:
            :obj:`tuple` <:class:`~numbers.Number`/:obj:`None`, exc_info/:obj:`None`>
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int"""
        self._set_value(value_info, propagate=propagate)
    
    def set_value(self, value, propagate=1):
        """Sets a new pseudo counter value.
           
        :param value_info:
            the new pseudo counter value
        :type value:
            :class:`~numbers.Number`
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int"""
        self._value.set_value(value, propagate=propagate)
    
    def _set_value(self, value_info, propagate=1):
        """Sets a new pseudo counter value.
           
        :param value_info:
            the new pseudo counter value
        :type value_info:
            :obj:`tuple` <:class:`~numbers.Number`/:obj:`None`, exc_info/:obj:`None`>
        :param propagate:
            0 for not propagating, 1 to propagate, 2 propagate with priority
        :type propagate:
            int"""
        self._value.set_value(*value_info, propagate=propagate)
    
    def put_physical_element_value(self, element, value, propagate=1):
        self._physical_values[element] = value
        if not propagate or len(self._physical_values) < len(self.get_user_elements()):
            return
        value_info = self.calc()
        self.put_value(value_info, propagate=propagate)
        
    value = property(get_value, set_value, doc="pseudo counter value")
    
    # --------------------------------------------------------------------------
    # default acquisition channel
    # --------------------------------------------------------------------------
    
    def get_default_acquisition_channel(self):
        return 'value'
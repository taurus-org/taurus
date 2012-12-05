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

"""This module is part of the Python Sardana library. It defines the base
classes for Sardana object"""

__all__ = ["SardanaBaseObject", "SardanaObjectID"]

__docformat__ = 'restructuredtext'

import weakref

from taurus.core.util import Logger

from sardanadefs import ElementType, Interface, InterfacesExpanded, InvalidId
from sardanaevent import EventGenerator, EventReceiver


class SardanaBaseObject(EventGenerator, EventReceiver, Logger):
    """The Sardana most abstract object. It contains only two members:
    
       - _manager : a weak reference to the manager (pool or ms) where it
         belongs
       - _name : the name
       - _full_name : the name (usually a tango device name, but can be
         anything else.)"""
    
    def __init__(self, **kwargs):
        EventGenerator.__init__(self)
        EventReceiver.__init__(self)
        self._type = kwargs.pop('elem_type')
        self._name = intern(kwargs.pop('name'))
        self._full_name = intern(kwargs.pop('full_name'))
        self._frontend = None
        Logger.__init__(self, self._name)
        self._manager = weakref.ref(kwargs.pop('manager'))
        self._parent = weakref.ref(kwargs.pop('parent', self.manager))
        
    def get_manager(self):
        """Return the :class:`sardana.Manager` which *owns* this sardana
        object.
        
        :return: the manager which *owns* this pool object.
        :rtype: :class:`sardana.Manager`"""
        return self._manager()
    
    def get_name(self):
        """Returns this sardana object name
        
        :return: this sardana object name
        :rtype: str"""
        return self._name

    def get_full_name(self):
        """Returns this sardana object full name
        
        :return: this sardana object full name
        :rtype: str"""
        return self._full_name
    
    def get_type(self):
        """Returns this sardana object type.
        
        :return: this sardana object type
        :rtype: :obj:`~sardana.sardanadefs.ElementType`"""
        return self._type
    
    def get_parent(self):
        """Returns this pool object parent.
        
        :return: this objects parent
        :rtype: :class:`~sardana.sardanabase.SardanaBaseObject`"""
        return self._parent()

    def get_parent_name(self):
        """Returns this sardana object parent's name.
        
        :return: this objects parent
        :rtype: str"""
        parent = self.get_parent()
        if parent and hasattr(parent, 'name'):
            return parent.name
    
    def get_frontend(self):
        """Returns this sardana frontend object or None if no frontend is
        registered
        
        :return: this objects frontend
        :rtype: :obj:`object`"""        
        f = self._frontend
        if f is None:
            return None
        return f()
    
    def fire_event(self, event_type, event_value, listeners=None, protected=True):
        if protected:
            try:
                return EventGenerator.fire_event(self, event_type, event_value,
                                                 listeners=listeners)
            except:
                self.warning("Error firing event <%r, %r>", event_type, event_value)
                self.debug("Details", exc_info=1)
        else:
            return EventGenerator.fire_event(self, event_type, event_value,
                                             listeners=listeners)
    
    def get_interfaces(self):
        """Returns the set of interfaces this object implements.
        
        :return:
            The set of interfaces this object implements.
        :rtype:
            class:`set` <:class:`sardana.sardanadefs.Interface`>"""
        return InterfacesExpanded[self.get_interface()]
    
    def get_interface(self):
        """Returns the interface this object implements.
        
        :return:
            The interface this object implements.
        :rtype:
            :class:`sardana.sardanadefs.Interface`"""
        return Interface[ElementType[self.get_type()]]
    
    def get_interface_names(self):
        """Returns a sequence of interface names this object implements.
        
        :return:
            The sequence of interfaces this object implements.
        :rtype:
            sequence<:obj:`str`>"""
        return map(Interface.get, self.get_interfaces())
    
    def serialize(self, *args, **kwargs):
        kwargs['name'] = self.name
        kwargs['full_name'] = self.full_name
        kwargs['type'] = ElementType.whatis(self.get_type())
        kwargs['manager'] = self.manager.name
        kwargs['parent'] = self.get_parent_name()
        kwargs['interfaces'] = self.get_interface_names()
        return kwargs
    
    def serialized(self, *args, **kwargs):
        return self.manager.serialize_element(self, *args, **kwargs)
    
    def str(self, *args, **kwargs):
        return self.manager.str_element(self, *args, **kwargs)
    
    def __str__(self):
        return self._name
    
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self._name)
    
    manager = property(get_manager,
                       doc="reference to the :class:`sardana.Manager`")
    name = property(get_name, doc="object name")
    full_name = property(get_full_name, doc="object full name")
    frontend = property(get_frontend, doc="the object frontend")
    

class SardanaObjectID(object):
    """To be used by sardana objects which have an ID associated to them."""
    
    def __init__(self, id=InvalidId):
        self._id = id
    
    def get_id(self):
        """Returns this sardana object ID
        
        :return: this sardana object ID
        :rtype: int"""
        return self._id
    
    def serialize(self, *args, **kwargs):
        kwargs['id'] = self.id
        return kwargs
    
    id = property(get_id, doc="object ID")

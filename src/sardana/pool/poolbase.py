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

__all__ = ["PoolBaseObject", "PoolObject"]

__docformat__ = 'restructuredtext'

import json
import weakref

from taurus.core.util import Logger

from poolevent import EventGenerator, EventReceiver


class PoolBaseObject(EventGenerator, EventReceiver, Logger):
    """The Pool most abstract object. It contains only two members:
    
       - _pool : a weak reference to the pool where it belongs
       - _name : the name"""
       
    def __init__(self, **kwargs):
        EventGenerator.__init__(self)
        EventReceiver.__init__(self)
        self._name = intern(kwargs['name'])
        Logger.__init__(self, self._name)
        self._pool = weakref.ref(kwargs['pool'])
    
    def get_pool(self):
        """Return the :class:`sardana.pool.pool.Pool` which *owns* this pool
        object.
        
        :return: the pool which *owns* this pool object.
        :rtype: :class:`sardana.pool.pool.Pool`"""
        return self._pool()
    
    def get_name(self):
        """Returns this pool object name
        
        :return: this pool object name
        :rtype: str"""
        return self._name

    def fire_event(self, event_type, event_value, listeners=None):
        try:
            return EventGenerator.fire_event(self, event_type, event_value,
                                             listeners=listeners)
        except:
            self.warning("Error firing event", exc_info=1)

    def to_json(self, *args, **kwargs):
        cl_name = self.__class__.__name__
        if cl_name.startswith("Pool"):
            cl_name = cl_name[4:]
        data = dict(name=self.name, pool=self.pool.name, type=cl_name)
        data.update(kwargs)
        return data

    def str(self, *args, **kwargs):
        return json.dumps(self.to_json(*args, **kwargs))
    
    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self._name)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self._name)
    
    pool = property(get_pool, doc="reference to the :class:`sardana.pool.pool.Pool`")
    name = property(get_name, doc="object name")
    

class PoolObject(PoolBaseObject):
    """A Pool object that besides the name and reference to the pool has:
       
       - _id : the internal identifier
       - _full_name : the name (usually a tango device name, but can be 
         anything else.)
       - _user_full_name : "[alias] '('[full_name]')' [class-of_device] \
         [extra_info]" """
       
    def __init__(self, **kwargs):
        self._full_name = kwargs.pop('full_name')
        self._id = kwargs.pop('id')
        PoolBaseObject.__init__(self, **kwargs)

    def get_full_name(self):
        """Returns this pool object full name
        
        :return: this pool object full name
        :rtype: str"""
        return self._full_name

    def get_id(self):
        """Returns this pool object ID
        
        :return: this pool object ID
        :rtype: int"""
        return self._id

    def get_type(self):
        """Returns this pool object type. Default implementation raises
        NotImplementedError.
        
        :return: this pool object type
        :rtype: :obj:'"""
        raise NotImplementedError

    def to_json(self, *args, **kwargs):
        kwargs['id'] = self.id
        kwargs['full_name'] = self.full_name
        ret = PoolBaseObject.to_json(self, *args, **kwargs)
        return ret

    full_name = property(get_full_name, doc="object full name")
    id = property(get_id, doc="object ID")

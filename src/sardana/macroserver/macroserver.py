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

from sardana import InvalidId, ElementType
from sardana.sardanamanager import SardanaBaseManager

from msbase import MSObject


class MacroServer(MSObject, SardanaBaseManager):
    
    max_paralell_macros = 5
    
    def __init__(self, full_name, name=None):
        MSObject.__init__(self, full_name=full_name, name=name,
                          macro_server=self)

    def serialize(self, *args, **kwargs):
        kwargs = MSObject.serialize(self, *args, **kwargs)
        kwargs['type'] = self.__class__.__name__
        kwargs['id'] = InvalidId
        kwargs['parent'] = None
        return kwargs
    
    def get_type(self):
        return ElementType.MacroServer
    
    def set_environment(self, env):
        pass
    
    def set_macro_path(self, path):
        pass
    
    def add_pool(self, pool):
        pass
    
    def set_max_parallel_macros(self, nb):
        self._max_parallel_macros = nb
        
    def get_max_parallel_macros(self):
        return self._max_parallel_macros
    
    max_parallel_macros = property(get_max_parallel_macros,
        set_max_parallel_macros, doc="maximum number of macros which can "
        "execute at the same time")
    
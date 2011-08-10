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

"""This module is part of the Python Pool libray. It defines the PoolPseudoMotor
class"""

__all__ = [ "PoolPseudoMotor" ]

__docformat__ = 'restructuredtext'

from pooldefs import ElementType
from poolelement import PoolElement
from poolmotion import PoolMotion


class PoolPseudoMotor(PoolElement):
    
    def __init__(self, **kwargs):
        PoolElement.__init__(self, **kwargs)
        self._position = None
        pool = self.pool
        self.set_action_cache(PoolMotion("%s.Motion" % self._name))
        self._user_elements = elems = []
        user_elem_ids = kwargs.pop('user_elements')
        
        for id in user_elem_ids:
            elem = pool.get_element(id=id)
            elems.append(elem)
            self._action_cache.add_element(elem)
        
    def get_type(self):
        return ElementType.PseudoMotor
    
    def set_position(self, position):
        self.start_move(position)
    
    def start_move(self, new_position):
        self._aborted = False
        pos, dial, do_backlash, dial_backlash = self._calculate_move(new_position)
        if not self._simulation_mode:
            items = { self : (pos, dial, do_backlash, dial_backlash) }
            self.motion.run(items=items)
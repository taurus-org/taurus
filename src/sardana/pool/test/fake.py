#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
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

__all__ = ['FakePool']

from sardana.pool.poolcontrollermanager import ControllerManager

class FakePool(object):
    ''' Fake class to simulate the behaviour of the Pool class
    '''
    acq_loop_sleep_time = 0.1
    acq_loop_states_per_value = 10

    elements = {}

    def __init__(self):
        self.ctrl_manager = ControllerManager()
        self.ctrl_manager.set_pool(self)
        self.ctrl_manager.setControllerPath([])

    def add_element(self, element):
        self.elements[element.id] = element

    def get_element(self, id):
        return self.elements[id]

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

"""This module is part of the Python Pool libray. It defines the class for a
motion"""

__all__ = [ "PoolMotion" ]

__docformat__ = 'restructuredtext'

import time

import taurus.core.util

from sardana import State
from poolaction import *

class PoolMotionItem(PoolActionItem):
    
    def __init__(self, moveable, position, do_backlash, backlash):
        PoolActionItem.__init__(self, moveable)
        self.moveable = moveable
        self.position = position
        self.do_backlash = do_backlash
        self.backlash = backlash


class PoolMotion(PoolAction):
    
    def __init__(self, name="GlobalMotion"):
        PoolAction.__init__(self, name)

    def start_action(self, *args, **kwargs):
        """items -> dict<moveable, (pos, dial, do_backlash, backlash)"""
        
        items = kwargs.pop("items")
        
        # prepare data structures
        self._aborted = False
        motion_info = {}
        for k, v in items.items():
            motion_info[k] = PoolMotionItem(*v)
        self._motion_info = motion_info
        
        pool_ctrls = self._pool_ctrls.keys()
        moveables = [ moveable() for moveable in self._elements ]
        
        # PreStartAll on all controllers
        for pool_ctrl in pool_ctrls: pool_ctrl.ctrl.PreStartAll()
        
        # PreStartOne on all elements
        for m in moveables:
            ctrl, axis, dial_position = m.controller.ctrl, m.axis, items[m][1]
            ret = ctrl.PreStartOne(axis, dial_position)
            if not ret:
                raise Exception("PreStartOne(%d, %f) returns False" % (axis, dial_position))

        # StartOne on all elements
        for m in moveables:
            ctrl, axis, dial_position = m.controller.ctrl, m.axis, items[m][1]
            ctrl.StartOne(axis, dial_position)
        
        # set the state of all elements to move and inform their listeners
        for m in moveables:
            m.set_state(State.Moving)
        
        # StartAll on all controllers
        for pool_ctrl in pool_ctrls: pool_ctrl.ctrl.StartAll()
    
    @taurus.core.util.DebugIt()
    def action_loop(self):
        i = 0
        
        states, positions = {}, {}
        for k in self._elements:
            k = k()
            states[k] = None
            positions[k] = None

        # read positions to send a first event when starting to move
        self.read_dial_position(ret=positions)
        for moveable, position in positions.items():
            moveable.put_dial_position(position, propagate=2)
            
        while True:
            self.read_state_info(ret=states)
            in_motion = False
            for moveable, state_info in states.items():
                state_info = moveable._from_ctrl_state_info(state_info)
                state = state_info[0]
                well_stopped = state == State.On
                moving = self._is_in_action(state)
                aborted = moveable.was_aborted()
                mi = self._motion_info[moveable]
                do_backlash = mi.do_backlash
                # if motor stopped 'well' and there is a backlash to do...
                if not aborted and do_backlash and well_stopped:
                    mi.do_backlash = False
                    # TODO: Do backlash
                elif not moving:
                    # first update the motor state so that position calculation
                    # that is done after takes the updated state into account
                    moveable.set_state_info(state_info, propagate=0)
                    
                    # try to read a last position to force an event
                    moveable.get_position(cache=False, propagate=2)
                    
                    # Then update the state
                    moveable.set_state_info(state_info)
                    del states[moveable]
                    del positions[moveable]
                    
                if moving:
                    in_motion = True
            
            if not in_motion:
                break
            
            # read position every n times
            if not i % 5:
                self.read_dial_position(ret=positions)
                for moveable, position in positions.items():
                    moveable.put_dial_position(position)
                
            i += 1
            time.sleep(0.01)
    
    def read_value(self, ret=None):
        return PoolAction.read_value(self, ret=ret)
        
    read_dial_position = read_value
    
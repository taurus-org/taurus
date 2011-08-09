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

__all__ = [ "MotionState", "PoolMotion", "PoolMotionItem" ]

__docformat__ = 'restructuredtext'

import time

from taurus.core.util import Enumeration, DebugIt

from sardana import State
from poolaction import PoolAction, PoolActionItem

MotionState = Enumeration("MotionSate", ( \
    "Stopped",
    "StoppedOnError",
    "Aborted",
    "Moving",
    "MovingBacklash",
    "MovingInstability",
    "Unknown",
    "Invalid") )

MS = MotionState
MovingStates = MS.Moving, MS.MovingBacklash, MS.MovingInstability

class PoolMotionItem(PoolActionItem):
    
    def __init__(self, moveable, position, dial_position, do_backlash,
                 backlash, instability_time=None):
        PoolActionItem.__init__(self, moveable)
        self.position = position
        self.aborted = False
        self.dial_position = dial_position
        self.do_backlash = do_backlash
        self.backlash = backlash
        self.instability_time = instability_time
        self.old_motion_state = MS.Unknown
        self.motion_state = MS.Stopped
        self.start_time = None
        self.stop_time = None
        self.stop_final_time = None
        self.old_state = State.Unknown
        self.state = State.Unknown
        
    def has_instability_time(self):
        return self.instability_time is not None

    def in_motion(self):
        return self.motion_state in MovingStates

    def get_moveable(self):
        return self.element
    
    moveable = property(fget=get_moveable)
    
    def on_state_switch(self, state, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        self.old_state = self.state
        self.state = state
        new_ms = ms = self.motion_state
        moveable = self.moveable
        self.aborted = moveable.was_aborted()
        instability_time = self.instability_time
        
        if self.aborted:
            new_ms = MS.Aborted
        elif ms == MS.Stopped:
            if state == State.Moving:
                self.start_time = timestamp
                new_ms = MS.Moving
        elif ms == MS.Moving:
            if state != State.Moving:
                if self.do_backlash:
                    if state == State.On:
                        new_ms = MS.MovingBacklash
                    else:
                        if instability_time is None:
                            new_ms = MS.StoppedOnError
                        else:
                            new_ms = MS.MovingInstability
                else:
                    self.stop_time = timestamp
                    if instability_time is None:
                        self.stop_final_time = timestamp
                        if state == State.On:
                            new_ms = MS.Stopped
                        else:
                            new_ms = MS.StoppedOnError
                    else:
                        new_ms = MS.MovingInstability
        elif ms == MS.MovingBacklash:
            if state != State.Moving:
                self.stop_time = timestamp
                if instability_time is None:
                    self.stop_final_time = timestamp
                    if state == State.On:
                        new_ms = MS.Stopped
                    else:
                        new_ms = MS.StoppedOnError
                else:
                    new_ms = MS.MovingInstability
        elif ms == MS.MovingInstability:
            dt = timestamp - self.stop_time
            if dt >= instability_time:
                self.stop_final_time = timestamp
                if state == State.On:
                    new_ms = MS.Stopped
                else:
                    new_ms = MS.StoppedOnError
        self.old_motion_state, self.motion_state = ms, new_ms
        return ms, new_ms
    
    
class PoolMotion(PoolAction):
    
    def __init__(self, name="GlobalMotion"):
        PoolAction.__init__(self, name)

    def start_action(self, *args, **kwargs):
        """items -> dict<moveable, (pos, dial, do_backlash, backlash)"""
        
        items = kwargs.pop("items")
        
        # prepare data structures
        self._aborted = False
        
        motion_info = {}
        for moveable, motion_data in items.items():
            moveable.prepare_to_move()
            it = moveable.instability_time
            motion_info[moveable] = PoolMotionItem(moveable, *motion_data,
                                                   instability_time=it)
            
        self._motion_info = motion_info
        
        pool_ctrls = self._pool_ctrls.keys()
        moveables = self.get_elements()
        
        # PreStartAll on all controllers
        for pool_ctrl in pool_ctrls:
            pool_ctrl.ctrl.PreStartAll()
        
        # PreStartOne on all elements
        for moveable in moveables:
            controller = moveable.controller
            ctrl, axis = controller.ctrl, moveable.axis
            dial_position = items[moveable][1]
            ret = ctrl.PreStartOne(axis, dial_position)
            if not ret:
                raise Exception("%s.PreStartOne(%d, %f) returns False" \
                                % (controller.name, axis, dial_position))

        # StartOne on all elements
        for moveable in moveables:
            ctrl = moveable.controller.ctrl
            axis = moveable.axis
            dial_position = motion_info[moveable].dial_position
            ctrl.StartOne(axis, dial_position)
        
        # set the state of all elements to move and inform their listeners
        for moveable in moveables:
            motion_info[moveable].motion_state = MotionState.Moving
            moveable.set_state(State.Moving, propagate=2)
        
        #update local motion information
        for motion_item in motion_info.values():
            state = motion_item.moveable.inspect_state()
            motion_item.on_state_switch(state)
        
        # StartAll on all controllers
        for pool_ctrl in pool_ctrls:
            pool_ctrl.ctrl.StartAll()
    
    def backlash_item(self, motion_item):
        moveable = motion_item.moveable
        controller = moveable.controller
        axis = moveable.axis
        position = motion_item.backlash
        try:
            controller.move({axis:position})
        except:
            self.warning("could not start backlash on %s", moveable.name,
                         exc_info=1)
    
    @DebugIt()
    def action_loop(self):
        i = 0
        
        states, positions = {}, {}
        for k in self.get_elements():
            states[k] = None
            positions[k] = None

        # read positions to send a first event when starting to move
        self.read_dial_position(ret=positions)
        for moveable, position in positions.items():
            moveable.put_dial_position(position, propagate=2)
        while True:
            self.read_state_info(ret=states)
            timestamp = time.time()
            in_motion = False
            for moveable, state_info in states.items():
                motion_item = self._motion_info[moveable]
                state_info = moveable._from_ctrl_state_info(state_info)
                state = state_info[0]
                old_motion_state, motion_state = \
                    motion_item.on_state_switch(state, timestamp=timestamp)
                
                aborted = moveable.was_aborted()
                well_stopped = state == State.On and not aborted
                moving = motion_item.in_motion()
                
                start_backlash = motion_state == MS.MovingBacklash and \
                    old_motion_state != MS.MovingBacklash
                start_instability = motion_state == MS.MovingInstability and \
                    old_motion_state != MS.MovingInstability
                    
                # if motor stopped 'well' and there is a backlash to do...
                if start_backlash:
                    # make sure the last position after the first motion is
                    # sent before starting the backlash motion
                    moveable.get_position(cache=False, propagate=2)
                    self.backlash_item(motion_item)
                    moving = motion_item.in_motion()
                elif start_instability:
                    # make sure the last position after the first motion is
                    # sent before starting the backlash motion
                    moveable.get_position(cache=False, propagate=2)
                elif not moving:
                    # first update the motor state so that position calculation
                    # that is done after takes the updated state into account
                    moveable.set_state_info(state_info, propagate=0)
                    
                    # try to read a last position to force an event
                    moveable.get_position(cache=False, propagate=2)
                    
                    # Then update the state
                    moveable.set_state_info(state_info, propagate=2)
                    
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
    
    def read_value(self, ret=None, serial=False):
        return PoolAction.read_value(self, ret=ret, serial=serial)
    
    read_dial_position = read_value
    
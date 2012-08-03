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

"""This module contains the definition for a simulated motor"""

__all__ = ["MotionPath", "Motion", "Motor", "DemoMotor"]

__docformat__ = 'restructuredtext'

import time
from math import pow, sqrt


class MotionPath(object):
    """Active motion path description"""

    #: True if motion in positive direction or False otherwise
    positive_displacement = True
    
    #: True if motion is not long enough to reach maximum velocity or False 
    #: otherwise
    small_motion = False

    #: position where maximum velocity will be reached
    max_vel_pos  = -1

    #: necessary displacement to reach maximum velocity
    displacement_reach_max_vel = -1

    #: necessary diplacement to reach minimum velocity
    displacement_reach_min_vel = -1

    #: maximum velocity possible
    max_vel = -1

    #: displacement at maximum velocity
    at_max_vel_displacement = -1

    #: time to reach maximum velocity
    max_vel_time = -1

    #: time to reach minimum velocity
    min_vel_time = -1

    #: time at maximum velocity
    at_max_vel_time = -1

    #: time the motion will take
    duration = -1
    
    def __init__(self, motor, initial_user_pos, final_user_pos):
        self.motor = motor
        self.initial_user_pos = initial_user_pos
        self.final_user_pos = final_user_pos

        self.__calculateMotionPath()
        
    def adjustMaxVelocityForNewDuration(self, duration):
        if self.small_motion:
            raise NotImplementedError
        motor = self.motor
        total_accel_time = motor.accel_time + motor.decel_time
        if duration <= total_accel_time:
            raise Exception("Duration too short. Must be bigger than %f" % total_accel_time)
        new_at_max_vel_time = duration - total_accel_time
        new_max_vel = self.at_max_vel_displacement / new_at_max_vel_time
 
        self.motor.setMaxVelocity(new_max_vel)
        self.__calculateMotionPath()
        return new_max_vel
    
    def setInitialUserPos(self, initial_user_pos):
        self.initial_user_pos = initial_user_pos
        self.__calculateMotionPath()

    def setFinalUserPos(self, final_user_pos):
        self.final_user_pos = final_user_pos
        self.__calculateMotionPath()
        
    def __calculateMotionPath(self):
        motor = self.motor
        initial_user_pos = self.initial_user_pos
        final_user_pos = self.final_user_pos        
    
        initial_pos = initial_user_pos * motor.step_per_unit
        final_pos = final_user_pos * motor.step_per_unit

        displacement = abs(final_pos - initial_pos)

        positive_displacement = final_pos >= initial_pos

        displmnt_not_cnst = motor.displacement_reach_max_vel + motor.displacement_reach_min_vel
        small_motion = displacement < displmnt_not_cnst

        if positive_displacement:
            accel = motor.accel
            decel = motor.decel
        else:
            accel = -motor.accel
            decel = -motor.decel

        if not small_motion:
            # necessary displacement to reach maximum velocity
            displacement_reach_max_vel = motor.displacement_reach_max_vel
            # necessary diplacement to reach minimum velocity
            displacement_reach_min_vel = motor.displacement_reach_min_vel

            if positive_displacement:
                max_vel = motor.max_vel
                min_vel = motor.min_vel
                # position where maximum velocity will be reached
                max_vel_pos = initial_pos + displacement_reach_max_vel
            else:
                max_vel = -motor.max_vel
                min_vel = -motor.min_vel
                # position where maximum velocity will be reached
                max_vel_pos = initial_pos - displacement_reach_max_vel

            # displacement at maximum velocity
            at_max_vel_displacement = displacement - (displacement_reach_max_vel + displacement_reach_min_vel)

        else:  # Small movement
            # position where maximum velocity will be reached
            max_vel_pos  = initial_pos * accel - final_pos * decel
            max_vel_pos /= accel - decel

            # necessary displacement to reach maximum velocity
            displacement_reach_max_vel = abs(max_vel_pos - initial_pos)

            # necessary diplacement to reach minimum velocity
            displacement_reach_min_vel = abs(final_pos - max_vel_pos)

            # maximum velocity possible
            cnst = 2 * accel * decel * displacement / (decel - accel)
            max_vel_2 = pow(motor.min_vel, 2) + cnst

            max_vel = sqrt(abs(max_vel_2))

            if positive_displacement:
                min_vel = motor.min_vel
            else:
                max_vel = -max_vel
                min_vel = -motor.min_vel

            # displacement at maximum velocity
            at_max_vel_displacement = 0.0

        # time to reach maximum velocity
        max_vel_time = abs((max_vel - min_vel) / accel)

        # time to reach minimum velocity
        min_vel_time = abs((min_vel - max_vel) / decel)

        # time at maximum velocity
        at_max_vel_time = abs(at_max_vel_displacement / max_vel)

        # time the motion will take
        duration = max_vel_time + at_max_vel_time + min_vel_time

        # ASSERTIONS
        if positive_displacement:
            assert(max_vel_pos >= initial_pos)
            assert(max_vel_pos <= final_pos)
        else:
            assert(max_vel_pos <= initial_pos)
            assert(max_vel_pos >= final_pos)

        assert(displacement_reach_max_vel >= 0.0)
        assert(displacement_reach_min_vel >= 0.0)

        assert(max_vel <= motor.max_vel)

        assert(max_vel_time >= 0.0)
        assert(min_vel_time >= 0.0)
        assert(duration >= 0.0)

        if self.small_motion:
            assert(at_max_vel_time == 0.0)
        else:
            assert(at_max_vel_time >= 0.0)
                    
        self.initial_pos = initial_pos
        self.final_pos = final_pos
        self.displacement = displacement
        
        self.positive_displacement = positive_displacement
        self.small_motion = small_motion

        self.accel = accel
        self.decel = decel        
        
        self.displacement_reach_max_vel = displacement_reach_max_vel
        self.displacement_reach_min_vel = displacement_reach_min_vel
        self.max_vel = max_vel
        self.min_vel = min_vel
        self.max_vel_pos = max_vel_pos
        self.at_max_vel_displacement = at_max_vel_displacement
        self.max_vel_time = max_vel_time
        self.min_vel_time = min_vel_time
        self.at_max_vel_time = at_max_vel_time
        self.duration = duration

    def info(self):
        print "Small movement =",self.small_motion
        print "length =",self.displacement
        print "position where maximum velocity will be reached =",self.max_vel_pos
        print "necessary displacement to reach maximum velocity =",self.displacement_reach_max_vel
        print "necessary displacement to stop from maximum velocity =",self.displacement_reach_min_vel
        print "maximum velocity possible =",self.max_vel
        print "time at top velocity =",self.at_max_vel_time
        print "displacement at top velocity =",self.at_max_vel_displacement
        print "time to reach maximum velocity =",self.max_vel_time
        print "time to reach minimum velocity =",self.min_vel_time
        print "time the motion will take =",self.duration
        print ""
        print "For long movements (where top vel is possible), necessary displacement to reach maximum velocity =",self.displacement_reach_max_vel
        print "For long movements (where top vel is possible), necessary displacement to stop from maximum velocity =",self.displacement_reach_min_vel


class Motion(object):
    """Active motion description"""

    #: instant this motion started
    start_instant = -1
    
    #: instant when maximum velocity should be reached
    max_vel_instant = -1
    
    #: instant when should start decelerating
    min_vel_instant = -1

    #: instant the motion will end
    final_instant = -1

    def __init__(self, motor, initial_user_pos, final_user_pos, start_instant=None):
        self.motion_path = mp = MotionPath(motor, initial_user_pos, final_user_pos)
        start_instant = start_instant or time.time()

        max_vel_instant = start_instant + mp.max_vel_time
        min_vel_instant = max_vel_instant + mp.at_max_vel_time
        final_instant = start_instant + mp.duration
        
        self.start_instant = start_instant
        self.max_vel_instant = max_vel_instant
        self.min_vel_instant = min_vel_instant
        self.final_instant = final_instant

        assert(final_instant >= start_instant)
        assert(start_instant <= max_vel_instant)
        assert(final_instant >= min_vel_instant)

        if self.motion_path.small_motion:
            assert(max_vel_instant == min_vel_instant)
        else:
            assert(max_vel_instant <= min_vel_instant)

    def __getattr__(self, name):
        return getattr(self.motion_path, name)


class BaseMotor(object):

    min_vel = -1
    max_vel = -1
    accel_time = -1
    decel_time = -1
    accel = -1
    decel = -1

    current_position = float('nan')


class Motor(BaseMotor):
    """The motor definition"""

    #: necessary displacement to reach maximum velocity from minimum velocity
    displacement_reach_max_vel = -1
    
    #: necessary displacement to reach minimum velocity from maximum velocity
    displacement_reach_min_vel = -1

    #: steps per unit
    step_per_unit = 1

    #: lower limit switch position
    lower_ls = float('-inf')

    #: upper limit switch position
    upper_ls = float('+inf')
    
    #: True if motor is powered or False otherwise
    power = True
    
    #: True if motor is enabled or False otherwise
    enabled = True

    #: internal member describing current motion
    current_motion = None

    
    def __init__(self, min_vel=None, max_vel=None, accel_time=None, decel_time=None):
        super(Motor, self).__init__()
        
        if min_vel is not None:
            self.setMinVelocity(min_vel)
        if max_vel is not None:
            self.setMaxVelocity(max_vel)
        if accel_time is not None:
            self.setAccelerationTime(accel_time)
        if decel_time is not None:
            self.setDecelerationTime(decel_time)
        
        self.__recalculate_acc_constants()

    def setMinVelocity(self, vi):
        """ Sets the minimum velocity in ms^-1. A.k.a. base rate"""
        vi = float(vi)
        if vi < 0:
            raise "Minimum velocity must be >= 0"

        self.min_vel = vi

        if self.max_vel < self.min_vel:
            self.max_vel = self.min_vel

        # force recalculation of accelerations
        if self.accel_time >= 0:
            self.setAccelerationTime(self.accel_time)
        if self.decel_time >= 0:
            self.setDecelerationTime(self.decel_time)

    def getMinVelocity(self):
        return self.min_vel

    def setMaxVelocity(self, vf):
        """ Sets the maximum velocity in ms^-1."""
        vf = float(vf)
        if vf <= 0:
            raise "Maximum velocity must be > 0"

        self.max_vel = vf

        if self.min_vel > self.max_vel:
            self.min_vel = self.max_vel

        # force recalculation of accelerations
        if self.accel_time >= 0:
            self.setAccelerationTime(self.accel_time)
        if self.decel_time >= 0:
            self.setDecelerationTime(self.decel_time)

    def getMaxVelocity(self):
        return self.max_vel

    def setAccelerationTime(self, at):
        """Sets the time to go from minimum velocity to maximum velocity in seconds"""
        at = float(at)
        if at < 0:
            raise "Acceleration time must be >= 0"

        self.accel_time = at
        try:
            self.accel = (self.max_vel - self.min_vel) / at
        except ZeroDivisionError:
            self.accel = float('inf')

        self.__recalculate_acc_constants()

    def getAccelerationTime(self):
        return self.accel_time

    def setDecelerationTime(self,dt):
        """Sets the time to go from maximum velocity to minimum velocity in seconds"""
        dt = float(dt)
        if dt < 0:
            raise "Deceleration time must be >= 0"

        self.decel_time = dt
        try:
            self.decel = (self.min_vel - self.max_vel) / dt
        except ZeroDivisionError:
            self.decel = float('inf')
            
        self.__recalculate_acc_constants()

    def getDecelerationTime(self):
        return self.decel_time

    def setAcceleration(self, a):
        """Sets the acceleration in ms^-2"""
        a = float(a)
        if a < 0:
            raise "Acceleration must be >= 0"

        self.accel = float(a)

        if a > 0:
            self.accel_time = (self.max_vel - self.min_vel) / a
        else:
            self.accel_time = float('INF')

        self.__recalculate_acc_constants()

    def setDeceleration(self, d):
        """Sets the deceleration in ms^-2"""
        d = float(d)
        if d > 0:
            raise "Deceleration must be <= 0"

        self.decel = d

        if d < 0:
            self.decel_time = (self.min_vel - self.max_vel) / d
        else:
            self.decel_time = float('INF')

        self.__recalculate_acc_constants()

    def getStepPerUnit(self):
        return self.step_per_unit

    def setStepPerUnit(self, spu):
        self.step_per_unit = spu

    def __recalculate_acc_constants(self):
        """precomputations assuming maximum speed can be reached in a motion"""
        
        if self.accel_time == 0:
            self.displacement_reach_max_vel = 0.0
        else:    
            self.displacement_reach_max_vel = 0.5 * self.accel * pow(self.accel_time,2)
            self.displacement_reach_max_vel += self.min_vel * self.accel_time

        if self.decel_time == 0:
            self.displacement_reach_min_vel = 0.0
        else:    
            self.displacement_reach_min_vel = 0.5 * self.decel * pow(self.decel_time,2)
            self.displacement_reach_min_vel += self.max_vel * self.decel_time

    def startMotion(self, initial_user_pos, final_user_pos, start_instant=None):
        
        if not self.power:
            raise Exception("Motor is powered off")

        if self.isInMotion():
            raise Exception("Already in motion")

        initial_pos = initial_user_pos * self.step_per_unit
        final_pos = final_user_pos * self.step_per_unit

        if initial_pos == final_pos:
            return
        
        motion = Motion(self, initial_user_pos, final_user_pos, start_instant)
        motion_path = motion.motion_path
        
        self.current_position = motion.initial_pos
        self.current_motion = motion

    def abortMotion(self, curr_instant=None):
        curr_instant = curr_instant or time.time()
        if not self.current_motion:
            return self.current_position

        self.current_position = self.getCurrentPosition(curr_instant)
        self.current_motion = None
        return self.current_position

    def isInMotion(self, curr_instant=None):
        curr_instant = curr_instant or time.time()
        #we call getCurrentPosition because inside it updates the current_motion flag
        self.getCurrentPosition(curr_instant)
        return self.current_motion is not None

    def setCurrentPosition(self, curr_pos):
        self.current_position = curr_pos

    def getCurrentPosition(self, curr_instant=None):
        curr_instant = curr_instant or time.time()
        pos = None
        if self.current_motion:
            motion = self.current_motion
            # if motion should be ended...
            if curr_instant >= motion.final_instant:
                self.current_motion = None
                pos = motion.final_pos
            else:
                pos  = motion.initial_pos
                if curr_instant > motion.min_vel_instant:
                    if motion.positive_displacement:
                        pos += motion.displacement_reach_max_vel
                        pos += motion.at_max_vel_displacement
                    else:
                        pos -= motion.displacement_reach_max_vel
                        pos -= motion.at_max_vel_displacement
                    dt = curr_instant - motion.min_vel_instant
                    pos += motion.max_vel * dt + 0.5 * motion.decel * pow(dt,2)
                elif curr_instant > motion.max_vel_instant:
                    if motion.positive_displacement:
                        pos += motion.displacement_reach_max_vel
                    else:
                        pos -= motion.displacement_reach_max_vel
                    dt = curr_instant - motion.max_vel_instant
                    pos += motion.max_vel * dt
                else:
                    dt  = curr_instant - motion.start_instant
                    pos += motion.min_vel * dt + 0.5 * motion.accel * pow(dt,2)
        else:
            pos = self.current_position
        if pos <= self.lower_ls:
            pos = self.lower_ls
            self.current_motion = None
        elif pos >= self.upper_ls:
            pos = self.upper_ls
            self.current_motion = None
        self.current_position = pos
        return pos

    def setCurrentUserPosition(self, user_pos):
        self.setCurrentPosition(user_pos*self.step_per_unit)

    def getCurrentUserPosition(self, curr_instant=None):
        return self.getCurrentPosition(curr_instant=curr_instant) / self.step_per_unit

    def hitLowerLimit(self):
        user_pos = self.current_position / self.step_per_unit
        return user_pos <= self.lower_ls

    def hitUpperLimit(self):
        user_pos = self.current_position / self.step_per_unit
        return user_pos >= self.upper_ls

    def getLowerLimitSwitch(self):
        return self.lower_ls

    def setLowerLimitSwitch(self, user_lower_ls):
        self.lower_ls = user_lower_ls

    def getUpperLimitSwitch(self):
        return self.upper_ls

    def setUpperLimitSwitch(self, user_upper_ls):
        self.upper_ls = user_upper_ls

    def turnOn(self):
        self.power = True

    def turnOff(self):
        self.power = False

    def isTurnedOn(self):
        return self.power

    def hasPower(self):
        return self.power

    def setPower(self, power):
        self.power = power

    def info(self):
        if self.current_motion is not None:
            print self.current_motion.info()
    

class DemoMotor(Motor):

    def __init__(self):
        super(DemoMotor, self).__init__(2, 100, 2, 2)
        self.setCurrentPosition(0)

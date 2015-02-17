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

"""This module contains the definition for a simulated motor"""

__all__ = ["MotionPath", "Motion", "BaseMotor", "Motor", "DemoMotor"]

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
    max_vel_pos = -1

    #: necessary displacement to reach maximum velocity
    displacement_reach_max_vel = 0

    #: necessary diplacement to reach minimum velocity
    displacement_reach_min_vel = 0

    #: maximum velocity possible
    max_vel = 0

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

    def __init__(self, motor,
                       initial_user_pos,
                       final_user_pos,
                       active_time=None):
        """MotionPath constructor - creates and calculates 
        motion path parameters.
        :param initial_user_pos: position at which constant vel 
                                 should be reached
        :param final_user_pos: position at which deceleration should 
                               start
        :param active_time: if passed, will fix the constant velocity 
                            (abs(final_user_pos - initial_user_pos)/active_time)
                            otherwise motor constant velocity
                            will be selected as high as possible"""
        self.motor = motor
        self.initial_user_pos = initial_user_pos
        self.final_user_pos = final_user_pos
        self.active_time = active_time
        self._calculateMotionPath()

    def setInitialUserPos(self, initial_user_pos):
        self.initial_user_pos = initial_user_pos
        self._calculateMotionPath()

    def setFinalUserPos(self, final_user_pos):
        self.final_user_pos = final_user_pos
        self._calculateMotionPath()

    def _calculateMotionPath(self):
        motor = self.motor
        initial_user_pos = self.initial_user_pos
        final_user_pos = self.final_user_pos

        initial_pos = initial_user_pos * motor.step_per_unit
        final_pos = final_user_pos * motor.step_per_unit

        displacement = abs(final_pos - initial_pos)

        # in this case active_time forces that the user range
        # correspond to the constant velocity
        # and
        if self.active_time != None:
            velocity = displacement / self.active_time
            self.motor.setMaxVelocity(velocity)
            sign = final_pos > initial_pos and 1 or -1
            accel_time = motor.getAccelerationTime()
            decel_time = motor.getDecelerationTime()
            base_vel = motor.getMinVelocity()
            accel_displacement = accel_time * 0.5 * (velocity + base_vel)
            decel_displacement = decel_time * 0.5 * (velocity + base_vel)
            initial_pos -= sign * accel_displacement
            final_pos += sign * decel_displacement
            displacement = abs(final_pos - initial_pos)
            self.initial_user_pos = initial_pos
            self.final_user_pos = final_pos

        if displacement == 0:
            positive_displacement = False
            small_motion = True

            accel = 0
            decel = 0

            displacement_reach_max_vel = 0
            displacement_reach_min_vel = 0
            max_vel = 0
            min_vel = 0
            max_vel_pos = initial_pos
            at_max_vel_displacement = 0
            max_vel_time = 0
            min_vel_time = 0
            at_max_vel_time = 0
            duration = 0
        else:
            positive_displacement = final_pos > initial_pos

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
                max_vel_pos = initial_pos * accel - final_pos * decel
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

            delta_vel = abs(max_vel - min_vel)

            # time to reach maximum velocity
            if accel == 0 or delta_vel == float('inf'):
                max_vel_time = 0
            else:
                max_vel_time = abs(delta_vel / accel)

            # time to reach minimum velocity
            if decel == 0 or delta_vel == float('inf'):
                min_vel_time = 0
            else:
                min_vel_time = abs(delta_vel / decel)

            # time at maximum velocity
            if abs(max_vel) == float('inf'):
                at_max_vel_time = 0
            else:
                at_max_vel_time = abs(at_max_vel_displacement / max_vel)

            # time the motion will take
            duration = max_vel_time + at_max_vel_time + min_vel_time

        self.initial_pos = initial_pos
        self.final_pos = final_pos
        self.displacement = displacement

        self.positive_displacement = positive_displacement
        self.small_motion = small_motion

        self.accel = accel
        self.decel = decel

        self.displacement_reach_max_vel = displacement_reach_max_vel
        self.displacement_reach_min_vel = displacement_reach_min_vel
        self.max_vel = abs(max_vel)  #velocity must be a positive value
        self.min_vel = abs(min_vel)
        self.max_vel_pos = max_vel_pos
        self.at_max_vel_displacement = at_max_vel_displacement
        self.max_vel_time = max_vel_time
        self.min_vel_time = min_vel_time
        self.at_max_vel_time = at_max_vel_time
        self.duration = duration

    def info(self):
        print "Small movement =", self.small_motion
        print "length =", self.displacement
        print "position where maximum velocity will be reached =", self.max_vel_pos
        print "necessary displacement to reach maximum velocity =", self.displacement_reach_max_vel
        print "necessary displacement to stop from maximum velocity =", self.displacement_reach_min_vel
        print "maximum velocity possible =", self.max_vel
        print "time at top velocity =", self.at_max_vel_time
        print "displacement at top velocity =", self.at_max_vel_displacement
        print "time to reach maximum velocity =", self.max_vel_time
        print "time to reach minimum velocity =", self.min_vel_time
        print "time the motion will take =", self.duration
        print ""
        print "For long movements (where top vel is possible), necessary displacement to reach maximum velocity =", self.displacement_reach_max_vel
        print "For long movements (where top vel is possible), necessary displacement to stop from maximum velocity =", self.displacement_reach_min_vel


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

    # base velocity (<units length>/s)
    min_vel = 0

    # top velocity (<units length>/s)
    max_vel = float('+inf')

    # acceleration time (s)
    accel_time = 0

    # deceleration time (s)
    decel_time = 0

    # acceleration (<units length>/s^2)
    accel = float('+inf')

    # acceleration (<units length>/s^2)
    decel = float('+inf')

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

    #: necessary displacement to reach maximum velocity from minimum velocity
    displacement_reach_max_vel = 0

    #: necessary displacement to reach minimum velocity from maximum velocity
    displacement_reach_min_vel = 0

    #: internal member describing current motion
    current_motion = None

    current_position = float('nan')

    def __init__(self):
        pass

    def setMinVelocity(self, vi):
        pass

    def getMinVelocity(self):
        return self.min_vel

    def setMaxVelocity(self, vf):
        pass

    def getMaxVelocity(self):
        return self.max_vel

    def setAccelerationTime(self, at):
        """Sets the time to go from minimum velocity to maximum velocity in seconds"""
        pass

    def getAccelerationTime(self):
        return self.accel_time

    def setDecelerationTime(self, dt):
        """Sets the time to go from maximum velocity to minimum velocity in seconds"""
        pass

    def getDecelerationTime(self):
        return self.decel_time

    def setAcceleration(self, a):
        """Sets the acceleration in ms^-2"""
        pass

    def setDeceleration(self, d):
        """Sets the deceleration in ms^-2"""
        pass

    def getStepPerUnit(self):
        return self.step_per_unit

    def setStepPerUnit(self, spu):
        self.step_per_unit = spu

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
                pos = motion.initial_pos
                if curr_instant > motion.min_vel_instant:
                    if motion.positive_displacement:
                        pos += motion.displacement_reach_max_vel
                        pos += motion.at_max_vel_displacement
                    else:
                        pos -= motion.displacement_reach_max_vel
                        pos -= motion.at_max_vel_displacement
                    dt = curr_instant - motion.min_vel_instant
                    pos += motion.max_vel * dt + 0.5 * motion.decel * pow(dt, 2)
                elif curr_instant > motion.max_vel_instant:
                    if motion.positive_displacement:
                        pos += motion.displacement_reach_max_vel
                    else:
                        pos -= motion.displacement_reach_max_vel
                    dt = curr_instant - motion.max_vel_instant
                    pos += motion.max_vel * dt
                else:
                    dt = curr_instant - motion.start_instant
                    pos += motion.min_vel * dt + 0.5 * motion.accel * pow(dt, 2)
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
        self.setCurrentPosition(user_pos * self.step_per_unit)

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


class Motor(BaseMotor):
    """The motor definition"""

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
            raise Exception("Minimum velocity must be >= 0")

        self.min_vel = vi

        #TODO: consult this solution with others
        if self.max_vel < self.min_vel:
            pass
            #self.max_vel = self.min_vel (original version)

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
            raise Exception("Maximum velocity must be > 0")

        self.max_vel = vf

        #TODO: consult this solution with others
        if self.min_vel > self.max_vel:
            pass
            #self.min_vel = self.max_vel #accel set to zero (original version)
            #self.setMinVelocity(0) another solution could be to set it to 0

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
            raise Exception("Acceleration time must be >= 0")

        self.accel_time = at
        try:
            self.accel = (self.max_vel - self.min_vel) / at
        except ZeroDivisionError:
            self.accel = float('inf')

        self.__recalculate_acc_constants()


    def getAccelerationTime(self):
        return self.accel_time

    def setDecelerationTime(self, dt):
        """Sets the time to go from maximum velocity to minimum velocity in seconds"""
        dt = float(dt)
        if dt < 0:
            raise Exception("Deceleration time must be >= 0")

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
            raise Exception("Acceleration must be >= 0")

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
            raise Exception("Deceleration must be <= 0")

        self.decel = d

        if d < 0:
            self.decel_time = (self.min_vel - self.max_vel) / d
        else:
            self.decel_time = float('INF')

        self.__recalculate_acc_constants()

    def __recalculate_acc_constants(self):
        """precomputations assuming maximum speed can be reached in a motion"""

        if self.accel_time == 0:
            self.displacement_reach_max_vel = 0.0
        else:
            self.displacement_reach_max_vel = 0.5 * self.accel * pow(self.accel_time, 2)
            self.displacement_reach_max_vel += self.min_vel * self.accel_time

        if self.decel_time == 0:
            self.displacement_reach_min_vel = 0.0
        else:
            self.displacement_reach_min_vel = 0.5 * self.decel * pow(self.decel_time, 2)
            self.displacement_reach_min_vel += self.max_vel * self.decel_time

    @staticmethod
    def fromMotor(motor):
        try:
            import sardana.taurus.core.tango.sardana.pool
            if isinstance(motor, sardana.taurus.core.tango.sardana.pool.PoolElement):
                min_vel = motor.getBaseRate()
                max_vel = motor.getVelocity()
                accel_time = motor.getAcceleration()
                decel_time = motor.getDeceleration()
                return Motor(min_vel=min_vel, max_vel=max_vel,
                             accel_time=accel_time, decel_time=decel_time)
        except Exception, e :
            print e
        return Motor._fromTangoMotor(motor)

    @staticmethod
    def _fromTangoMotor(motor):
        import PyTango
        attrs = "base_rate", "velocity", "acceleration", "deceleration"
        attr_values = motor.read_attributes(attrs)
        v = []
        for attr_value in attr_values:
            if attr_value.has_failed:
                raise PyTango.DevFailed(*attr_value.get_err_stack())
            v.append(attr_value.value)
        return Motor(min_vel=v[0], max_vel=v[1], accel_time=v[2], decel_time=v[3])



class DemoMotor(Motor):

    def __init__(self):
        super(DemoMotor, self).__init__(2, 100, 2, 2)
        self.setCurrentPosition(0)

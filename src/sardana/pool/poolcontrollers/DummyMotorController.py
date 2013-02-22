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

import time
from math import pow, sqrt

from sardana import State, SardanaValue
from sardana.pool.controller import MotorController
from sardana.pool.controller import DefaultValue, Description, FGet, FSet, Type


class BaseMotion(object):

    def __init__(self):
        self.min_vel = -1
        self.max_vel = -1
        self.accel_time = -1
        self.decel_time = -1
        self.accel = -1
        self.decel = -1

        self.init_pos = -1
        self.final_pos = -1
        self.curr_pos = -1


class Motion(BaseMotion):

    def __init__(self):
        BaseMotion.__init__(self)

        self.dsplmnt_reach_max_vel = -1
        self.dsplmnt_reach_min_vel = -1
        self.dsplmnt = -1

        self.curr_instant = -1
        self.start_instant = -1

        self.positive_dsplmnt = True
        self.small_motion = False

        # position where maximum velocity will be reached
        self.curr_max_vel_pos  = -1

        # necessary displacement to reach maximum velocity
        self.curr_dsplmnt_reach_max_vel = -1

        # necessary displacement to reach minimum velocity
        self.curr_dsplmnt_reach_min_vel = -1

        # maximum velocity possible
        self.curr_max_vel = -1

        # time at maximum velocity
        self.curr_at_max_vel_dsplmnt = -1

        # time to reach maximum velocity
        self.curr_max_vel_time = -1

        # time to reach minimum velocity
        self.curr_min_vel_time = -1

        # time at maximum velocity
        self.curr_at_max_vel_time = -1

        # instant when maximum velocity should be reached
        self.curr_max_vel_instant = -1

        # instant when should start decelerating
        self.curr_min_vel_instant = -1

        # time the motion will take
        self.duration = -1

        # instant the motion will end
        self.final_instant = -1

        # steps per unit
        self.step_per_unit = 1

        self.inMotion = False

        self.lower_ls = float('-inf')
        self.upper_ls = float('+inf')

        self.power = True
        self.enabled = True

        self.__recalculate_acc_constants()

    def setMinVelocity(self,vi):
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

    def setMaxVelocity(self,vf):
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

    def setAccelerationTime(self,at):
        """Sets the time to go from minimum velocity to maximum velocity in seconds"""
        at = float(at)
        if at <= 0:
            raise "Acceleration time must be > 0"

        self.accel_time = at
        self.accel = (self.max_vel - self.min_vel) / at

        self.__recalculate_acc_constants()

    def getAccelerationTime(self):
        return self.accel_time

    def setDecelerationTime(self,dt):
        """Sets the time to go from maximum velocity to minimum velocity in seconds"""
        dt = float(dt)
        if dt <= 0:
            raise "Deceleration time must be > 0"

        self.decel_time = dt
        self.decel = (self.min_vel - self.max_vel) / dt

        self.__recalculate_acc_constants()

    def getDecelerationTime(self):
        return self.decel_time

    def setAcceleration(self,a):
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

    def setDeceleration(self,d):
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
        """pre-computations assuming maximum speed can be reached in a motion"""

        self.dsplmnt_reach_max_vel = 0.5 * self.accel * pow(self.accel_time,2)
        self.dsplmnt_reach_max_vel += self.min_vel * self.accel_time

        self.dsplmnt_reach_min_vel = 0.5 * self.decel * pow(self.decel_time,2)
        self.dsplmnt_reach_min_vel += self.max_vel * self.decel_time

    def startMotion(self, initial_user_pos, final_user_pos, start_instant=None):
        """starts a new motion"""

        if not self.power:
            raise Exception("Motor is powered off")

        initial_pos = initial_user_pos * self.step_per_unit
        final_pos = final_user_pos * self.step_per_unit

        if self.inMotion:
            raise Exception("Already in motion")

        if initial_pos == final_pos:
            return

        self.init_pos = initial_pos
        self.final_pos = final_pos
        self.curr_pos = initial_pos
        self.dsplmnt = abs(final_pos - initial_pos)

        start_instant = start_instant or time.time()
        self.curr_instant = start_instant
        self.start_instant = start_instant

        self.positive_dsplmnt = final_pos >= initial_pos

        displmnt_not_cnst = self.dsplmnt_reach_max_vel + self.dsplmnt_reach_min_vel
        self.small_motion = self.dsplmnt < displmnt_not_cnst

        if self.positive_dsplmnt:
            self.curr_accel = self.accel
            self.curr_decel = self.decel
        else:
            self.curr_accel = -self.accel
            self.curr_decel = -self.decel


        if not self.small_motion:

            # necessary displacement to reach maximum velocity
            self.curr_dsplmnt_reach_max_vel = self.dsplmnt_reach_max_vel
            # necessary diplacement to reach minimum velocity
            self.curr_dsplmnt_reach_min_vel = self.dsplmnt_reach_min_vel

            if self.positive_dsplmnt:
                self.curr_max_vel = self.max_vel
                self.curr_min_vel = self.min_vel
                # position where maximum velocity will be reached
                self.curr_max_vel_pos = self.init_pos + self.curr_dsplmnt_reach_max_vel
            else:
                self.curr_max_vel = -self.max_vel
                self.curr_min_vel = -self.min_vel
                # position where maximum velocity will be reached
                self.curr_max_vel_pos = self.init_pos - self.curr_dsplmnt_reach_max_vel

            # displacement at maximum velocity
            self.curr_at_max_vel_dsplmnt = self.dsplmnt - (self.curr_dsplmnt_reach_max_vel + self.curr_dsplmnt_reach_min_vel)

        else:  # Small movement
            # position where maximum velocity will be reached
            self.curr_max_vel_pos  = self.init_pos * self.curr_accel - self.final_pos * self.curr_decel
            self.curr_max_vel_pos /= self.curr_accel - self.curr_decel

            # necessary displacement to reach maximum velocity
            self.curr_dsplmnt_reach_max_vel = abs(self.curr_max_vel_pos - self.init_pos)

            # necessary diplacement to reach minimum velocity
            self.curr_dsplmnt_reach_min_vel = abs(self.final_pos - self.curr_max_vel_pos)

            # maximum velocity possible
            cnst = 2 * self.curr_accel * self.curr_decel * self.dsplmnt / (self.curr_decel - self.curr_accel)
            max_vel_2 = pow(self.min_vel, 2) + cnst

            self.curr_max_vel = sqrt(abs(max_vel_2))

            if self.positive_dsplmnt:
                self.curr_min_vel = self.min_vel
            else:
                self.curr_max_vel = -self.curr_max_vel
                self.curr_min_vel = -self.min_vel

            # displacement at maximum velocity
            self.curr_at_max_vel_dsplmnt = 0.0

        # time to reach maximum velocity
        self.curr_max_vel_time = abs((self.curr_max_vel - self.curr_min_vel) / self.curr_accel)

        # time to reach minimum velocity
        self.curr_min_vel_time = abs((self.curr_min_vel - self.curr_max_vel) / self.curr_decel)

        # time at maximum velocity
        self.curr_at_max_vel_time = abs(self.curr_at_max_vel_dsplmnt / self.curr_max_vel)

        # instant when maximum velocity should be reached
        self.curr_max_vel_instant = self.start_instant + self.curr_max_vel_time

        # instant when should start decelerating
        self.curr_min_vel_instant = self.curr_max_vel_instant + self.curr_at_max_vel_time

        # time the motion will take
        self.duration = self.curr_max_vel_time + self.curr_at_max_vel_time + self.curr_min_vel_time

        # instant the motion will end
        self.final_instant = self.start_instant + self.duration

        # uncomment following line if need output concerning the movement that
        # has just started
        # self.info()

        # ASSERTIONS
        if self.positive_dsplmnt:
            assert(self.curr_max_vel_pos >= self.init_pos)
            assert(self.curr_max_vel_pos <= self.final_pos)
        else:
            assert(self.curr_max_vel_pos <= self.init_pos)
            assert(self.curr_max_vel_pos >= self.final_pos)

        assert(self.curr_dsplmnt_reach_max_vel >= 0.0)
        assert(self.curr_dsplmnt_reach_min_vel >= 0.0)

        assert(self.final_instant >= self.start_instant)
        assert(self.curr_max_vel <= self.max_vel)
        assert(self.start_instant <= self.curr_max_vel_instant)
        assert(self.final_instant >= self.curr_min_vel_instant)

        assert(self.curr_max_vel_time > 0.0)
        assert(self.curr_min_vel_time > 0.0)
        assert(self.duration > 0.0)

        if self.small_motion:
            assert(self.curr_max_vel_instant == self.curr_min_vel_instant)
            assert(self.curr_at_max_vel_time == 0.0)
        else:
            assert(self.curr_max_vel_instant <= self.curr_min_vel_instant)
            assert(self.curr_at_max_vel_time >= 0.0)

        self.inMotion = True

    def abortMotion(self, curr_instant=None):
        curr_instant = curr_instant or time.time()
        if not self.inMotion:
            return self.curr_pos

        self.curr_pos = self.getCurrentPosition(curr_instant)
        self.inMotion = False
        return self.curr_pos

    def isInMotion(self,curr_instant=None):
        curr_instant = curr_instant or time.time()
        #we call getCurrentPosition because inside it updates the inMotion flag
        self.getCurrentPosition(curr_instant)
        return self.inMotion

    def setCurrentPosition(self, curr_pos):
        self.curr_pos = curr_pos
        self.init_pos = curr_pos

    def getCurrentPosition(self, curr_instant=None):
        curr_instant = curr_instant or time.time()
        self.curr_instant = curr_instant
        pos = None
        if self.inMotion:
            # if motion should be ended...
            if self.curr_instant >= self.final_instant:
                self.inMotion = False
                pos = self.final_pos
            else:
                pos  = self.init_pos
                if curr_instant > self.curr_min_vel_instant:
                    if self.positive_dsplmnt:
                        pos += self.curr_dsplmnt_reach_max_vel
                        pos += self.curr_at_max_vel_dsplmnt
                    else:
                        pos -= self.curr_dsplmnt_reach_max_vel
                        pos -= self.curr_at_max_vel_dsplmnt
                    dt = curr_instant - self.curr_min_vel_instant
                    pos += self.curr_max_vel * dt + 0.5 * self.curr_decel * pow(dt,2)
                elif curr_instant > self.curr_max_vel_instant:
                    if self.positive_dsplmnt:
                        pos += self.curr_dsplmnt_reach_max_vel
                    else:
                        pos -= self.curr_dsplmnt_reach_max_vel
                    dt = curr_instant - self.curr_max_vel_instant
                    pos += self.curr_max_vel * dt
                else:
                    dt  = curr_instant - self.start_instant
                    pos += self.curr_min_vel * dt + 0.5 * self.curr_accel * pow(dt,2)
        else:
            pos = self.curr_pos
        if pos <= self.lower_ls:
            pos = self.lower_ls
            self.inMotion = False
        elif pos >= self.upper_ls:
            pos = self.upper_ls
            self.inMotion = False
        self.curr_pos = pos
        return pos

    def setCurrentUserPosition(self, user_pos):
        self.setCurrentPosition(user_pos*self.step_per_unit)

    def getCurrentUserPosition(self, curr_instant=None):
        return self.getCurrentPosition(curr_instant=curr_instant) / self.step_per_unit

    def hitLowerLimit(self):
        user_pos = self.curr_pos / self.step_per_unit
        return user_pos <= self.lower_ls

    def hitUpperLimit(self):
        user_pos = self.curr_pos / self.step_per_unit
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
        print "Small movement =",self.small_motion
        print "length =",self.dsplmnt
        print "position where maximum velocity will be reached =",self.curr_max_vel_pos
        print "necessary displacement to reach maximum velocity =",self.curr_dsplmnt_reach_max_vel
        print "necessary displacement to stop from maximum velocity =",self.curr_dsplmnt_reach_min_vel
        print "maximum velocity possible =",self.curr_max_vel
        print "time at top velocity =",self.curr_at_max_vel_time
        print "displacement at top velocity =",self.curr_at_max_vel_dsplmnt
        print "time to reach maximum velocity =",self.curr_max_vel_time
        print "time to reach minimum velocity =",self.curr_min_vel_time
        print "time the motion will take =",self.duration
        print "instant when maximum velocity should be reached =",self.curr_max_vel_instant
        print "instant when should start decelerating =",self.curr_min_vel_instant
        print "instant the motion will end",self.final_instant
        print ""
        print "For long movements (where top vel is possible), necessary displacement to reach maximum velocity =",self.dsplmnt_reach_max_vel
        print "For long movements (where top vel is possible), necessary displacement to stop from maximum velocity =",self.dsplmnt_reach_min_vel


class BasicDummyMotorController(MotorController):
    """This class represents a basic, dummy Sardana motor controller."""

    gender = "Simulation"
    model  = "Basic"
    organization = "Sardana team"

    MaxDevice = 1024

    def __init__(self, inst, props, *args, **kwargs):
        MotorController.__init__(self, inst, props, *args, **kwargs)
        self.m = self.MaxDevice*[None,]

    def GetAxisAttributes(self, axis):
        axis_attrs = MotorController.GetAxisAttributes(self, axis)
        new_axis_attrs = {}
        for attr in ('Position', 'Limit_switches'):
            new_axis_attrs[attr] = axis_attrs[attr]
        return new_axis_attrs

    def AddDevice(self,axis):
        MotorController.AddDevice(self, axis)
        idx = axis - 1
        if len(self.m) < axis:
            raise Exception("Invalid axis %d" % axis)
        if self.m[idx] is None:
            m = Motion()
            m.setMinVelocity(2)
            m.setMaxVelocity(100)
            m.setAccelerationTime(2)
            m.setDecelerationTime(2)
            m.setCurrentPosition(0)
            self.m[idx] = m

    def DeleteDevice(self, axis):
        MotorController.DeleteDevice(self, axis)
        idx = axis - 1
        if len(self.m) < axis or not self.m[idx]:
            self._log.error("Invalid axis %d" % axis)
        #self.m[idx] = None

    def StateOne(self, axis):
        #self._log.debug("StateOne(%d)", axis)
        #raise Exception("Cannot StateOne %d" % axis)
        idx = axis - 1
        m = self.m[idx]
        state = State.On
        status = "Motor HW is ON"
        if m.isInMotion():
            state = State.Moving
            status = "Motor HW is MOVING"
        m.getCurrentUserPosition()
        switchstate = 0
        if m.hitLowerLimit():
            switchstate |= MotorController.LowerLimitSwitch
            state = State.Alarm
            status = "Motor HW is in ALARM. Hit hardware lower limit switch"
        if m.hitUpperLimit():
            switchstate |= MotorController.UpperLimitSwitch
            state = State.Alarm
            status = "Motor HW is in ALARM. Hit hardware upper limit switch"
        if state != State.Alarm and not m.hasPower():
            state = State.Off
            status = "Motor is powered off"
        #self._log.info("StateOne(%s) = %s", axis, (state, status, switchstate))
        return state, status, switchstate

    def ReadOne(self, axis):
        #self._log.debug("ReadOne(%d)", axis)
        #raise Exception("Cannot ReadOne")
        idx = axis - 1
        m = self.m[idx]
        ts = time.time() #simulate as if we got it from hardware
        return SardanaValue(m.getCurrentUserPosition(), timestamp=ts)
        #return m.getCurrentUserPosition()

    def PreStartAll(self):
        #raise Exception("Cannot move on PreStartAll")
        self.motions = {}

    def PreStartOne(self, axis, pos):
        #raise Exception("Cannot move on PreStartOne")
        idx = axis - 1
        m = self.m[idx]
        return m.hasPower()

    def StartOne(self, axis, pos):
        #raise Exception("Cannot move on StartOne")
        idx = axis - 1
        self.motions[self.m[idx]] = pos

    def StartAll(self):
        #raise Exception("Cannot move on StartAll")
        t = time.time()
        for motion, pos in self.motions.items():
            motion.startMotion(motion.getCurrentUserPosition(t), pos, t)

    def AbortOne(self, axis):
        self._log.info("AbortOne(%d)", axis)
        idx = axis - 1
        self.m[idx].abortMotion()

    def SendToCtrl(self, stream):
        return stream

class FastDummyMotorController(MotorController):

    gender = "Simulation"
    model  = "Basic"
    organization = "Sardana team"

    MaxDevice = 1024

    def __init__(self, inst, props, *args, **kwargs):
        MotorController.__init__(self, inst, props, *args, **kwargs)
        self.m = self.MaxDevice*[None,]

    def GetAxisAttributes(self, axis):
        axis_attrs = MotorController.GetAxisAttributes(self, axis)
        new_axis_attrs = {}
        for attr in ('Position', 'Limit_switches'):
            new_axis_attrs[attr] = axis_attrs[attr]
        return new_axis_attrs

    def AddDevice(self,axis):
        MotorController.AddDevice(self, axis)
        idx = axis - 1
        if len(self.m) < axis:
            raise Exception("Invalid axis %d" % axis)
        if self.m[idx] is None:
            self.m[idx] = BaseMotion()

    def DeleteDevice(self, axis):
        MotorController.DeleteDevice(self, axis)
        idx = axis - 1
        if len(self.m) < axis or not self.m[idx]:
            self._log.error("Invalid axis %d" % axis)
        #self.m[idx] = None

    def StateOne(self, axis):
        #self._log.debug("StateOne(%d)", axis)
        state = State.On
        status = "Motor HW is ON"
        switchstate = 0
        return state, status, switchstate

    def ReadOne(self, axis):
        self._log.debug("ReadOne(%d)", axis)
        idx = axis - 1
        m = self.m[idx]
        return m.curr_pos

    def PreStartAll(self):
        self.motions = {}

    def PreStartOne(self, axis, pos):
        return True

    def StartOne(self, axis, pos):
        idx = axis - 1
        self.motions[self.m[idx]] = pos

    def StartAll(self):
        for motion, pos in self.motions.items():
            motion.curr_pos = pos

    def AbortOne(self, axis):
        pass


class DiscreteDummyMotorController(BasicDummyMotorController):
    """This class represents a discrete, dummy Sardana motor controller."""

    def __init__(self, inst, props, *args, **kwargs):
        BasicDummyMotorController.__init__(self, inst, props, *args, **kwargs)

    def GetAxisAttributes(self, axis):
        axis_attrs = MotorController.GetAxisAttributes(self, axis)
        new_axis_attrs = dict(Position=axis_attrs['Position'])
        new_axis_attrs['Position'][Type] = int
        return new_axis_attrs

    def AddDevice(self, axis):
        BasicDummyMotorController.AddDevice(self, axis)
        idx = axis - 1
        m = self.m[idx]
        m.setMinVelocity(0)
        m.setMaxVelocity(1)
        m.setAccelerationTime(0.01)
        m.setDecelerationTime(0.01)
        m.setCurrentPosition(0)

    def ReadOne(self, axis):
        pos = BasicDummyMotorController.ReadOne(self, axis)
        return int(pos)

    
class DummyMotorController(BasicDummyMotorController):
    """This class represents a dummy Sardana motor controller."""

    ctrl_features = []

    model = "Best"

    ctrl_attributes = {
        'LowerLimitSwitch' : { Type : float,
                               Description : 'lower limit switch position',
                               FGet : 'getLowerLimitSwitch',
                               FSet : 'setLowerLimitSwitch',
                               DefaultValue: -9999.9999, },
        'UpperLimitSwitch' : { Type : float,
                               Description : 'upper limit switch position',
                               DefaultValue: 8888.8888 }
    }

    axis_attributes = {
        'LowerLimitSwitch' : { Type : float,
                               Description : 'lower limit switch position',
                               FGet : 'getLLS',
                               FSet : 'setLLS',
                               DefaultValue: -9999.9999 },
        'UpperLimitSwitch' : { Type : float,
                               Description : 'upper limit switch position',
                               FGet : 'getULS',
                               FSet : 'setULS',
                               DefaultValue: 8888.8888 },
        'Power'            : { Type : bool,
                               Description : 'motor power',
                               FGet : 'getPower',
                               FSet : 'setPower',
                               DefaultValue: True },
    }

    ctrl_properties = {
        'Prop1' : { Type : str,
                    Description  : 'demo property 1',
                    DefaultValue : 'test property 1'},
        'Prop2' : { Type : int,
                    Description  : 'demo property 1',
                    DefaultValue : 531},
    }

    def __init__(self, inst, props, *args, **kwargs):
        BasicDummyMotorController.__init__(self, inst, props, *args, **kwargs)
        self._lowerLS = float("-inf")
        self._upperLS = float("+inf")

    def GetAxisAttributes(self, axis):
        return MotorController.GetAxisAttributes(self, axis)

    def SetAxisPar(self, axis, name, value):
        idx = axis - 1
        m = self.m[idx]
        name = name.lower()
        if name == "acceleration":
            m.setAccelerationTime(value)
        elif name == "deceleration":
            m.setDecelerationTime(value)
        elif name == "base_rate":
            m.setMinVelocity(value)
        elif name == "velocity":
            m.setMaxVelocity(value)
        elif name == "step_per_unit":
            m.setStepPerUnit(value)

    def GetAxisPar(self, axis, name):
        idx = axis - 1
        m = self.m[idx]
        name = name.lower()
        if name == "acceleration":
            v = m.getAccelerationTime()
        elif name == "deceleration":
            v = m.getDecelerationTime()
        elif name == "base_rate":
            v = m.getMinVelocity()
        elif name == "velocity":
            v = m.getMaxVelocity()
        elif name == "step_per_unit":
            v = m.getStepPerUnit()
        return v

    def DefinePosition(self, axis, position):
        idx = axis - 1
        m = self.m[idx]
        m.offset = position - m.getCurrentUserPosition()
        m.setCurrentUserPosition(position)

    def getLowerLimitSwitch(self):
        return self._lowerLS

    def setLowerLimitSwitch(self, value):
        self._lowerLS = value

    def getUpperLimitSwitch(self):
        return self._upperLS

    def setUpperLimitSwitch(self, value):
        self._upperLS = value

    def getLLS(self, axis):
        return self.m[axis - 1].getLowerLimitSwitch()

    def setLLS(self, axis, ls):
        self.m[axis - 1].setLowerLimitSwitch(ls)

    def getULS(self, axis):
        return self.m[axis - 1].getUpperLimitSwitch()

    def setULS(self, axis, ls):
        self.m[axis - 1].setUpperLimitSwitch(ls)

    def getPower(self, axis):
        return self.m[axis - 1].hasPower()

    def setPower(self, axis, power):
        self.m[axis - 1].setPower(power)

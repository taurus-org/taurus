import PyTango
import pool
from pool import MotorController
import array
import sys
import time

from math import pow,sqrt

class Motor:
    def __init__(self):
        self.velocity = 0.0
        self.acceleration = 0.0
        self.deceleration = 0.0
        self.backlash = 0.0
        self.step_per_unit = 0.0
        self.offset = 0.0
        self.base_rate = 0.0
        self.comch = None
        self.comch_name = None
        self.currpos = 0.0
        self.pos_w = None


class Motion(object):
    
    def __init__(self):
        self.min_vel = -1
        self.max_vel = -1
        self.accel_time = -1
        self.decel_time = -1
        self.accel = -1
        self.decel = -1
        self.dsplmnt_reach_max_vel = -1
        self.dsplmnt_reach_min_vel = -1
        
        self.init_pos = -1
        self.final_pos = -1
        self.curr_pos = -1
        self.dsplmnt = -1
        
        self.curr_instant = -1
        self.start_instant = -1
        
        self.positive_dsplmnt = True
        self.small_motion = False
        
        # position where maximum velocity will be reached
        self.curr_max_vel_pos  = -1
        
        # necessary displacement to reach maximum velocity
        self.curr_dsplmnt_reach_max_vel = -1
        
        # necessary diplacement to reach minimum velocity 
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
        self.step_per_unit = 1.0
        
        self.inMotion = False
        
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
    
    def getAcceleration(self):
        return self.accel
        
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

    def getDeceleration(self):
        return self.decel
    
    def __recalculate_acc_constants(self):
        """precomputations assuming maximum speed can be reached in a motion"""
        
        self.dsplmnt_reach_max_vel = 0.5 * self.accel * pow(self.accel_time,2)
        self.dsplmnt_reach_max_vel += self.min_vel * self.accel_time

        self.dsplmnt_reach_min_vel = 0.5 * self.decel * pow(self.decel_time,2)
        self.dsplmnt_reach_min_vel += self.max_vel * self.decel_time

    def startMotion(self, initial_pos, final_pos, start_instant):
        """starts a new motion"""
        
        if self.inMotion:
            raise Exception("Already in motion")
        
        if initial_pos == final_pos:
            return

        self.init_pos = initial_pos
        self.final_pos = final_pos
        self.curr_pos = initial_pos
        self.dsplmnt = abs(final_pos - initial_pos)
        
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
        
        assert(self.final_instant > self.start_instant)
        assert(self.curr_max_vel <= self.max_vel)
        assert(self.start_instant < self.curr_max_vel_instant)
        assert(self.final_instant > self.curr_min_vel_instant)
        
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
    
    def abortMotion(self, curr_instant):
        if not self.inMotion:
            return self.curr_pos
        
        pos = self.curr_pos = self.getCurrentPosition(curr_instant)
        self.inMotion = False
        return self.curr_pos
    
    def isInMotion(self,curr_instant):
        #we call getCurrentPosition because inside it updates the inMotion flag
        self.getCurrentPosition(curr_instant)
        return self.inMotion
    
    def setCurrentPosition(self, curr_pos):
        self.curr_pos = curr_pos
        self.init_pos = curr_pos
    
    def getCurrentPosition(self, curr_instant):
        self.curr_instant = curr_instant
        if self.inMotion:
            # if motion should be ended...
            if self.curr_instant >= self.final_instant:
                self.inMotion = False
                self.curr_pos = self.final_pos
            else:
                self.curr_pos  = self.init_pos
                if curr_instant > self.curr_min_vel_instant:
                    if self.positive_dsplmnt:
                        self.curr_pos += self.curr_dsplmnt_reach_max_vel
                        self.curr_pos += self.curr_at_max_vel_dsplmnt
                    else:
                        self.curr_pos -= self.curr_dsplmnt_reach_max_vel
                        self.curr_pos -= self.curr_at_max_vel_dsplmnt
                    dt = curr_instant - self.curr_min_vel_instant
                    self.curr_pos += self.curr_max_vel * dt + 0.5 * self.curr_decel * pow(dt,2)
                    
                elif curr_instant > self.curr_max_vel_instant:
                    if self.positive_dsplmnt:
                        self.curr_pos += self.curr_dsplmnt_reach_max_vel
                    else:
                        self.curr_pos -= self.curr_dsplmnt_reach_max_vel
                    dt = curr_instant - self.curr_max_vel_instant
                    self.curr_pos += self.curr_max_vel * dt
                    
                else:
                    dt  = curr_instant - self.start_instant
                    self.curr_pos += self.curr_min_vel * dt + 0.5 * self.curr_accel * pow(dt,2)
        
        return self.curr_pos

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


class DummyMotorController(MotorController):
    """This class is the Tango Sardana motor controller. It uses a EchoCommunicationChannel"""

    ctrl_features = ['Home_speed','Home_acceleration']

    gender = "Simulation"
    model  = "Basic"
    organization = "CELLS - ALBA"
    image = "dummy_motor_ctrl.png"
    logo = "ALBA_logo.png"

    MaxDevice = 1024
    
    def __init__(self,inst,props):
        MotorController.__init__(self,inst,props)
        self.m = self.MaxDevice*[None,]

    def AddDevice(self,axis):
        idx = axis - 1
        if len(self.m) < axis:
            raise Exception("Invalid axis %d" % axis)
        if not self.m[idx]:
            self.m[idx] = Motor()
            
    def DeleteDevice(self,axis):
        idx = axis - 1
        if len(self.m) < axis or not self.m[idx]:
            self._log.error("Invalid axis %d" % axis)
    
    def StateOne(self,axis):
        state = PyTango.DevState.ON
        switchstate = 0
        return (int(state), switchstate)

    def ReadOne(self,axis):
        idx = axis - 1
        return self.m[idx].currpos
    
    def PreStartOne(self,axis,pos):
        return True

    def StartOne(self,axis,pos):
        idx = axis - 1
        self.m[idx].pos_w = pos
        
    def StartAll(self):
        for i,mot in enumerate(self.m):
            if mot and mot.pos_w is not None:
                mot.currpos = mot.pos_w
                mot.pos_w = None

    def AbortOne(self,axis):
        pass

    def StopOne(self,axis):
        pass

    def SetPar(self,axis,name,value):
        idx = axis - 1
        setattr(self.m[idx],name.lower(),value)

    def GetPar(self,axis,name):
        idx = axis - 1
        return getattr(self.m[idx],name.lower())

    def DefinePosition(self, axis, position):
        idx = axis - 1
        self.m[idx].offset = position - self.m[idx].currpos
        self.m[idx].currpos = position


class DummyMotorControllerV2(MotorController):
    """This class is the Tango Sardana motor controller."""

    ctrl_features = []

    gender = "Simulation"
    model  = "Best"
    organization = "CELLS - ALBA"
    image = "dummy_motor_ctrl.png"
    logo = "ALBA_logo.png"

    MaxDevice = 1024
    
    def __init__(self,inst,props):
        MotorController.__init__(self,inst,props)
        self.m = self.MaxDevice*[None,]
        
    def AddDevice(self,axis):
        idx = axis - 1
        if len(self.m) < axis:
            raise Exception("Invalid axis %d" % axis)
        if not self.m[idx]:
            m = Motion()
            m.setCurrentPosition(0.0)
            m.setMaxVelocity(100.0)
            m.setMinVelocity(2.0)
            m.setAccelerationTime(2.0)
            m.setDecelerationTime(2.0)
            self.m[idx] = m
    
    def DeleteDevice(self,axis):
        idx = axis - 1
        if len(self.m) < axis or not self.m[idx]:
            self._log.error("Invalid axis %d" % axis)
    
    def StateOne(self,axis):
        idx = axis - 1
        m = self.m[idx]
        state = PyTango.DevState.ON
        switchstate = 0
        if m.getCurrentPosition(time.time())>100:
            switchstate |= 0x2 # upper limit switch active
        if m.getCurrentPosition(time.time())<-100:
            switchstate |= 0x4 # lower limit switch active
        if m.isInMotion(time.time()):
            state = PyTango.DevState.MOVING
        return (int(state), switchstate)

    def ReadOne(self,axis):
        idx = axis - 1
        m = self.m[idx]
        return m.getCurrentPosition(time.time()) / m.step_per_unit
    
    def PreStartAll(self):
        self._motors_to_move = []
        return True
    
    def PreStartOne(self,axis,pos):
        idx = axis - 1
        m = self.m[idx]
        pos *= m.step_per_unit
        self._motors_to_move.append((m, pos))
        return True
        
    def StartOne(self,axis,pos):
        pass
                
    def StartAll(self):
        try:
            t = time.time()
            for motion, pos_stop in self._motors_to_move:
                pos_start = motion.getCurrentPosition(t)
                motion.startMotion(pos_start, pos_stop, t)
        except Exception,e:
            print 80*"="
            print "'%s'" % str(e)
            print 80*"="
            import traceback
            traceback.print_exc()
            print 80*"="
            raise e

    def AbortOne(self,axis):
        pass

    def SetPar(self,axis,name,value):
        idx = axis - 1
        name=name.lower()
        if name == "velocity":
            self.m[idx].setMaxVelocity(value)
        elif name == "acceleration":
            self.m[idx].setAccelerationTime(value)
        elif name == "deceleration":
            self.m[idx].setDecelerationTime(value)
        elif name == "base_rate":
            self.m[idx].setMinVelocity(value)
        elif name == "step_per_unit":
            self.m[idx].step_per_unit = value

    def GetPar(self,axis,name):
        idx = axis - 1
        name=name.lower()
        if name == "velocity":
            return self.m[idx].getMaxVelocity()
        elif name == "acceleration":
            return self.m[idx].getAccelerationTime()
        elif name == "deceleration":
            return self.m[idx].getDecelerationTime()
        elif name == "base_rate":
            return self.m[idx].getMaxVelocity()
        elif name == "step_per_unit":
            return self.m[idx].step_per_unit

    def DefinePosition(self, axis, position):
        idx = axis - 1
        self.m[idx].offset = position - self.m[idx].getCurrentPosition()
        self.m[idx].setCurrentPosition(position)



class DummyMotorControllerExtra(MotorController):
    """This class is the Tango Sardana motor controller. It uses a DummyCommunicationChannel"""

    ctrl_features = ['Home_speed','Home_acceleration']

    class_prop = {'CommunicationChannel':{'Type':'PyTango.DevVarStringArray','Description':'Communication channel names'}}
    
    gender = "Null"
    model  = "Simplest Null"
    organization = "CELLS - ALBA"

    MaxDevice = 1024
    
    def __init__(self,inst,props):
        MotorController.__init__(self,inst,props)
        self.m = self.MaxDevice*[None,]

    def AddDevice(self,axis):
        idx = axis - 1
        if len(self.m) < axis:
            raise Exception("CommunicationChannel property does not define a valid communication channel for axis %d" % axis)
        if not self.m[idx]:
            self.m[idx] = Motor()
            self.m[idx].comch_name = self.CommunicationChannel[idx]
            self.m[idx].comch = pool.PoolUtil().get_com_channel(self.inst_name,self.m[idx].comch_name)
            
    def DeleteDevice(self,axis):
        idx = axis - 1
        if len(self.m) < axis:
            self._log.error("CommunicationChannel property does not define a valid communication channel for axis %d" % axis)
            return
        self.m[idx].comch = None
        self.m[idx].comch_name = None
    
    def StateOne(self,axis):
        state = PyTango.DevState.ON
        switchstate = 0
        return (state, "OK", switchstate)

    def ReadOne(self,axis):
        idx = axis - 1
        res = self.m[idx].comch.read(-1)
        s = array.array('B', res).tostring()
        try:
            self.m[idx].currpos = float(s)
        except:
            self.m[idx].currpos = 0.0
        return self.m[idx].currpos
    
    def PreStartOne(self,axis,pos):
        return True

    def StartOne(self,axis,pos):
        idx = axis - 1
        self.m[idx].pos_w = str(pos)
        
    def StartAll(self):
        for i,mot in enumerate(self.m):
            if mot and mot.pos_w:
                cmdarray = array.array('B', mot.pos_w)
                mot.comch.write(cmdarray)
                mot.pos_w = None
        
    def SetPar(self,axis,name,value):
        idx = axis - 1
        setattr(self.m[idx],name.lower(),value)

    def GetPar(self,axis,name):
        idx = axis - 1
        return getattr(self.m[idx],name.lower())

    def AbortOne(self,axis):
        pass

    def StopOne(self,axis):
        pass

    def DefinePosition(self, axis, position):
        idx = axis - 1
        self.m[idx].offset = position - self.m[idx].currpos
        self.m[idx].currpos = position

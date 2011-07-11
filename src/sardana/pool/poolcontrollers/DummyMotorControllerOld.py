import PyTango
import sardana.pool
from sardana.pool import MotorController
import array
import sys

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
            self.m[idx].comch = sardana.pool.PoolUtil().get_com_channel(self.inst_name,self.m[idx].comch_name)
            
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

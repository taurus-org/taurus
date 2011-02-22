from PyTango import DevState
from pool import IORegisterController
import pool

class IOR:
    def __init__(self, axis):
        self.axis = axis
        self.state = DevState.ON
        self.status = "OK"
        self.value = 0
        self.is_started = False
        self.active = False
        
class DummyIORController(IORegisterController):
    "This class is the Tango Sardana IORegister controller for tests."
    
    predefined_values = ( "0", "Up", "1" , "Down", "2", "Changing" )

    gender = "Simulation"
    model  = "Basic"
    organization = "CELLS - ALBA"
    image = "dummy_ior_ctrl.png"
    logo = "ALBA_logo.png"
    
    MaxDevice = 1024

    def __init__(self,inst,props):
        IORegisterController.__init__(self, inst, props)
        self.iors = [ IOR(i+1) for i in xrange(self.MaxDevice) ]
        
    def AddDevice(self, axis):
        idx = axis - 1
        self.iors[idx].active = True
        
    def DeleteDevice(self, axis):
        idx = axis - 1
        self.iors[idx].active = False
    
    def StateOne(self, axis):
        idx = axis - 1
        return (self.iors[idx].state, self.iors[idx].status)

    def PreReadAll(self):
        pass

    def PreReadOne(self, axis):
        pass

    def ReadAll(self):
        pass

    def ReadOne(self, axis):
        idx = axis - 1
        return self.iors[idx].value

    def WriteOne(self, axis, value):
        idx = axis - 1
        self.iors[idx].value = value

    def GetExtraAttributePar(self, axis, name):
        ior = self.iors[axis-1]
        return getattr(ior, name)

    def SetExtraAttributePar(self, axis, name, value):
        ior = self.iors[axis-1]
        setattr(ior, name, value)
        
    def SendToCtrl(self, in_data):
        return "Adios"

if __name__ == "__main__":
    obj = DummyIORController('test')


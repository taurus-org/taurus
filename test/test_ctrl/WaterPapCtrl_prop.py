import PyTango
import socket
import MotorController

class IcePapController(MotorController.MotorController):
    "This class is the Tango Sardana motor controller for the ICEPAP with properties"

    ctrl_features = ['Encoder','Home_speed','Home_acceleration']

    class_prop = {'A_Class_Prop':{'Type':'PyTango.DevLong','Description':'A class property','DefaultValue':20},
                  'Another_Class_Prop':{'Type':'PyTango.DevDouble','Description':'Bla bla bla','DefaultValue':2.345},
		  'Host':{'Type':'PyTango.DevString','Description':'The host name'},
                  'Port':{'Type':'PyTango.DevLong','Description':'The port number'}}

    ctrl_extra_attributes = {'First_extra':{'Type':'PyTango.DevDouble','R/W Type':'PyTango.READ_WRITE'},
			     'Second_extra':{'Type':'PyTango.DevLong','R/W Type':'PyTango.READ'}}
    MaxDevice = 22

    def __init__(self,inst,props):
        MotorController.MotorController.__init__(self,inst,props)
        print "PYTHON -> IcePapController ctor for instance",inst

        self.home_speed = 0.0
        self.nb_call = 0;
        self.timeout = 3
 
        print "PYTHON -> IcePap on",self.Host," and port",self.Port," with timeout = ",self.timeout   
        print "PYTHON -> Connected to", self.Host, " on port", self.Port
        
        
    def AddDevice(self,axis):
        print "PYTHON -> IcePapController/",self.inst_name,": In AddDevice method for axis",axis
        
    def DeleteDevice(self,axis):
        print "PYTHON -> IcePapController/",self.inst_name,": In DeleteDevice method for axis",axis
        
    def StateOne(self,axis):
        print "PYTHON -> IcePapController/",self.inst_name,": In StateOne method for axis",axis
        tup = (PyTango.DevState.ON,0)
        return tup

    def PreReadAll(self):
        print "PYTHON -> IcePapController/",self.inst_name,": In PreReadAll method"

    def PreReadOne(self,axis):
        print "PYTHON -> IcePapController/",self.inst_name,": In PreReadOne method for axis",axis

    def ReadAll(self):
        print "PYTHON -> IcePapController/",self.inst_name,": In ReadAll method"

    def ReadOne(self,axis):
        print "PYTHON -> IcePapController/",self.inst_name,": In ReadOne method for axis",axis
        return 123

    def PreStartAll(self):
        print "PYTHON -> IcePapController/",self.inst_name,": In PreStartAll method"

    def PreStartOne(self,axis,pos):
        print "PYTHON -> IcePapController/",self.inst_name,": In PreStartOne method for axis",axis," with pos",pos
        return True

    def StartOne(self,axis,pos):
        print "PYTHON -> IcePapController/",self.inst_name,": In StartOne method for axis",axis," with pos",pos

    def StartAll(self):
        print "PYTHON -> IcePapController/",self.inst_name,": In StartAll method"

    def SetPar(self,axis,name,value):
        print "PYTHON -> IcePapController/",self.inst_name,": In SetPar method for axis",axis," name=",name," value=",value

    def GetPar(self,axis,name):
        print "PYTHON -> IcePapController/",self.inst_name,": In GetPar method for axis",axis," name=",name
        return 12.34

    def GetExtraAttributePar(self,axis,name):
        print "PYTHON -> IcePapController/",self.inst_name,": In GetExtraAttributePar method for axis",axis," name=",name
        return 2233

    def SetExtraAttributePar(self,axis,name,value):
        print "PYTHON -> IcePapController/",self.inst_name,": In SetExtraAttributePar method for axis",axis," name=",name," value=",value
        
    def __del__(self):
        print "PYTHON -> IcePapController/",self.inst_name,": Aarrrrrg, I am dying"
        
if __name__ == "__main__":
    obj = IcePapController('test')

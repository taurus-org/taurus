import PyTango
import ZeroDController
import time

class ElecMeterController(ZeroDController.ZeroDController):
    "This class is the Tango Sardana Zero D controller for an Electrometer"

    ctrl_extra_attributes = {'Py0D_extra_1':{'Type':'PyTango.DevDouble','R/W Type':'PyTango.READ_WRITE'},
			     'Py0D_extra_2':{'Type':'PyTango.DevLong','R/W Type':'PyTango.READ'},
			     'Py0D_extra_3':{'Type':'PyTango.DevBoolean','R/W Type':'PyTango.READ'}}
			     
#    class_prop = {'CtrlDevName':{'Type':'PyTango.DevString','Description':'The ctrl simulator Tango device name'}}
			     
    MaxDevice = 1

    def __init__(self,inst,props):
        ZeroDController.ZeroDController.__init__(self,inst,props)
        print "PYTHON -> ZeroDController ctor for instance",inst
#	raise NameError,"Ouuups"

        self.ct_name = "ZeroDController/" + self.inst_name
#        self.simu_ctrl = None
#        self.simu_ctrl = PyTango.DeviceProxy(self.CtrlDevName)
#	self.started = False
	
#        try:
#            self.simu_ctrl.ping()
#        except:
#            self.simu_ctrl = None
#            raise
        
        
    def AddDevice(self,ind)
        print "PYTHON -> ZeroDController/",self.inst_name,": In AddDevice method for index",ind
#        raise RuntimeError,"Hola la la"
        
    def DeleteDevice(self,ind):
        print "PYTHON -> ZeroDController/",self.inst_name,": In DeleteDevice method for index",ind
        
    def StateOne(self,ind):
        print "PYTHON -> ZeroDController/",self.inst_name,": In StateOne method for index",ind
#        if self.simu_ctrl != None:
#	    if self.started == True:
#	        now = time.time()
#		delta_t = now - self.start_time
#		print "delta_t =",delta_t
#		if delta_t > 2.0:
#		     self.simu_ctrl.command_inout("Stop",self.wantedCT[0])
#		     self.started = False
#            sta = self.simu_ctrl.command_inout("GetCounterState",ind)
#            print "State in controller =",sta
#            tup = (sta,"Status error string from controller")
#        else:
#            raise RuntimeError,"Ctrl Tango's proxy null!!!"
        tup = (PyTango.DevState.ON,"Status error string from controller")
        return tup

    def PreReadAll(self):
        print "PYTHON -> ZeroDController/",self.inst_name,": In PreReadAll method"

    def PreReadOne(self,ind):
        print "PYTHON -> ZeroDController/",self.inst_name,": In PreReadOne method for index",ind

    def ReadAll(self):
        print "PYTHON -> ZeroDController/",self.inst_name,": In ReadAll method"

    def ReadOne(self,ind):
        print "PYTHON -> ZeroDController/",self.inst_name,": In ReadOne method for index",ind
#	if self.simu_ctrl != None:
#            return self.simu_ctrl.command_inout("GetCounterValue",ind)
#	else:
#	    raise RuntimeError,"Ctrl Tango's proxy null!!!"
        return 1.234
	
    def GetExtraAttributePar(self,ind,name):
        print "PYTHON -> ZeroDController/",self.inst_name,": In GetExtraFeaturePar method for index",ind," name=",name
	if name == "Py0D_extra_1":
	    return 88.99
	    
	if name == "Py0D_extra_2":
	    return 33
        return 2233

    def SetExtraAttributePar(self,ind,name,value):
        print "PYTHON -> ZeroDController/",self.inst_name,": In SetExtraFeaturePar method for index",ind," name=",name," value=",value
        
    def SendToCtrl(self,in_data):
        print "Received value =",in_data
        return "Adios"

    def __del__(self):
        print "PYTHON -> ZeroDController/",self.inst_name,": Aarrrrrg, I am dying"

        
if __name__ == "__main__":
    obj = ZeroDController('test')
#    obj.AddDevice(2)
#    obj.DeleteDevice(2)

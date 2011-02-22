import PyTango
import CounterTimerController

class Vct6Controller(CounterTimerController.CounterTimerController):
    "This class is the Tango Sardana CounterTimer controller for the VCT6"

    ctrl_extra_attributes = {'PyCT_extra_1':{'Type':'PyTango.DevDouble','R/W Type':'PyTango.READ_WRITE'},
			     'PyCT_extra_2':{'Type':'PyTango.DevLong','R/W Type':'PyTango.READ'},
			     'PyCT_extra_3':{'Type':'PyTango.DevBoolean','R/W Type':'PyTango.READ'}}
			     
    class_prop = {'CtrlDevName':{'Type':'PyTango.DevString','Description':'The ctrl simulator Tango device name'}}
			     
    MaxDevice = 6

    def __init__(self,inst,props):
        CounterTimerController.CounterTimerController.__init__(self,inst,props)
        print "PYTHON -> Vct6Controller ctor for instance",inst
#	raise NameError,"Ouuups"

        self.ct_name = "Vct6Controller/" + self.inst_name
        self.simu_ctrl = None
        self.simu_ctrl = PyTango.DeviceProxy(self.CtrlDevName)
	
        try
            self.simu_ctrl.ping()
        except:
            self.simu_ctrl = None
            raise
        
        
    def AddDevice(self,ind):
        print "PYTHON -> Vct6Controller/",self.inst_name,": In AddDevice method for index",ind
#        raise RuntimeError,"Hola la la"
        
    def DeleteDevice(self,ind):
        print "PYTHON -> Vct6Controller/",self.inst_name,": In DeleteDevice method for index",ind
        
    def StateOne(self,ind):
        print "PYTHON -> Vct6Controller/",self.inst_name,": In StateOne method for index",ind
        if self.simu_ctrl != None:
            sta = self.simu_ctrl.command_inout("GetCounterState",ind)
            print "State in controller =",sta
            tup = (sta,"Status error string from controller")
        else:
            raise RuntimeError,"Ctrl Tango's proxy null!!!"
        return tup

    def PreReadAll(self):
        print "PYTHON -> Vct6Controller/",self.inst_name,": In PreReadAll method"

    def PreReadOne(self,ind):
        print "PYTHON -> Vct6Controller/",self.inst_name,": In PreReadOne method for index",ind

    def ReadAll(self):
        print "PYTHON -> Vct6Controller/",self.inst_name,": In ReadAll method"

    def ReadOne(self,ind):
        print "PYTHON -> Vct6Controller/",self.inst_name,": In ReadOne method for index",ind
        return 123

    def GetExtraAttributePar(self,ind,name):
        print "PYTHON -> Vct6Controller/",self.inst_name,": In GetExtraFeaturePar method for index",ind," name=",name
	if name == "PyCT_extra_1":
	    return 88.99
	    
	if name == "PyCT_extra_2":
	    return 33
        return 2233

    def SetExtraAttributePar(self,ind,name,value):
        print "PYTHON -> Vct6Controller/",self.inst_name,": In SetExtraFeaturePar method for index",ind," name=",name," value=",value
        
    def SendToCtrl(self,in_data):
        print "Received value =",in_data
        return "Adios"

    def __del__(self):
        print "PYTHON -> Vct6Controller/",self.inst_name,": Aarrrrrg, I am dying"

        
if __name__ == "__main__":
    obj = Vct6Controller('test')
#    obj.AddDevice(2)
#    obj.DeleteDevice(2)

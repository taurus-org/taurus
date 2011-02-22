import PyTango
import CounterTimerController
import time

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
        self.started = False

        self.dft_PyCT_extra_1 = 88.99
        self.dft_PyCT_extra_2 = 33
        self.dft_PyCT_extra_3 = True

        self.PyCT_extra_1 = []
        self.PyCT_extra_2 = []
        self.PyCT_extra_3 = []

        try:
            self.simu_ctrl.ping()
        except:
            self.simu_ctrl = None
            raise
        
        
    def AddDevice(self,ind):
        print "PYTHON -> Vct6Controller/",self.inst_name,": In AddDevice method for index",ind
        self.PyCT_extra_1.append(self.dft_PyCT_extra_1)
        self.PyCT_extra_2.append(self.dft_PyCT_extra_2)
        self.PyCT_extra_3.append(self.dft_PyCT_extra_3)        
#        raise RuntimeError,"Hola la la"
        
    def DeleteDevice(self,ind):
        print "PYTHON -> Vct6Controller/",self.inst_name,": In DeleteDevice method for index",ind
        
    def StateOne(self,ind):
        #print "PYTHON -> Vct6Controller/",self.inst_name,": In StateOne method for index",ind
        if self.simu_ctrl != None:
            if self.started == True:
                now = time.time()
                delta_t = now - self.start_time
                print "delta_t =",delta_t
                if delta_t > 2.0:
                    for index in self.wantedCT:
                        self.simu_ctrl.command_inout("Stop",index)
                    self.started = False
            sta = self.simu_ctrl.command_inout("GetCounterState",ind)
            #print "State in controller =",sta
            tup = (sta,"Status error string from controller")
        else:
            raise RuntimeError,"Ctrl Tango's proxy null!!!"
        return tup

    def PreReadAll(self):
        #print "PYTHON -> Vct6Controller/",self.inst_name,": In PreReadAll method"
        pass
        

    def PreReadOne(self,ind):
        #print "PYTHON -> Vct6Controller/",self.inst_name,": In PreReadOne method for index",ind
        pass

    def ReadAll(self):
        #print "PYTHON -> Vct6Controller/",self.inst_name,": In ReadAll method"
        pass

    def ReadOne(self,ind):
        #print "PYTHON -> Vct6Controller/",self.inst_name,": In ReadOne method for index",ind
        pass
        if self.simu_ctrl != None:
            return self.simu_ctrl.command_inout("GetCounterValue",ind)
        else:
            raise RuntimeError,"Ctrl Tango's proxy null!!!"
	
    def AbortOne(self,ind):
        print "PYTHON -> Vct6Controller/",self.inst_name,": In AbortOne method for index",ind
        if self.simu_ctrl != None:
            self.simu_ctrl.command_inout("Stop",ind)
            self.started = False
        else:
            raise RuntimeError,"Ctrl Tango's proxy null!!!"
        
    def PreStartAllCT(self):
        #print "PYTHON -> Vct6Controller/",self.inst_name,": In PreStartAllCT method"
        self.wantedCT = []
	
    def StartOneCT(self,ind):
        #print "PYTHON -> Vct6Controller/",self.inst_name,": In StartOneCT method for index",ind
        self.wantedCT.append(ind)
	
    def StartAllCT(self):
        #print "PYTHON -> Vct6Controller/",self.inst_name,": In StartAllCT method"
        for index in self.wantedCT:
            self.simu_ctrl.command_inout("Start",index)
        self.started = True
        self.start_time = time.time()
		     	
    def LoadOne(self,ind,value):
        #print "PYTHON -> Vct6Controller/",self.inst_name,": In LoadOne method for index",ind," with value",value
        if self.simu_ctrl != None:
            self.simu_ctrl.command_inout("Clear",ind)
        else:
            raise RuntimeError,"Ctrl Tango's proxy null!!!"
	
    def GetExtraAttributePar(self,ind,name):
        if name == "PyCT_extra_1":
            return self.PyCT_extra_1[ind]
        if name == "PyCT_extra_2":
            return self.PyCT_extra_2[ind]
        return self.PyCT_extra_3[ind]

    def SetExtraAttributePar(self,ind,name,value):
        if name == "PyCT_extra_1":
            self.PyCT_extra_1[ind] = value
        elif name == "PyCT_extra_2":
            self.PyCT_extra_2[ind] = value
        else:
            self.PyCT_extra_3[ind] = value
        
    def SendToCtrl(self,in_data):
        print "Received value =",in_data
        return "Adios"

    def __del__(self):
        print "PYTHON -> Vct6Controller/",self.inst_name,": Aarrrrrg, I am dying"

        
if __name__ == "__main__":
    obj = Vct6Controller('test')
#    obj.AddDevice(2)
#    obj.DeleteDevice(2)

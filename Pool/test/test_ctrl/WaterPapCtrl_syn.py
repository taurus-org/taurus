import PyTango
import socket
import MotorController

class IcePapController(MotorController.MotorController):
    def __init__(self,inst,props):
        print "PYTHON -> IcePapController ctor for instance",inst
        MotorController.MotorController.__init__(self,inst,props)
        self.nb_call = 0;
        self.socket_connected = False;
        self.db = PyTango.Database()
        self.ct_name = "IcePapController/" + self.inst_name

#
# Get controller properties
#

        prop_list = ['host','port','timeout']
        prop = self.db.get_property(self.ct_name,prop_list)
        
        if len(prop["host"]) != 0
            self.host = prop["host"][0]
        else:
            print "Property host not defined for controller",self.ct_name
            self.host = "nada"
            
        if len(prop["port"]) != 0:
            self.port = int(prop["port"][0])
        else:
            print "Property port not defined for controller",self.ct_name
            self.port = 0
            
        if len(prop["timeout"]) != 0:
            self.timeout = int(prop["timeout"][0])
        else:
            print "Property timeout not defined for controller",self.ct_name
            self.timeout = 3
 
 #
 # Connect to the icepap
 #
            
        print "PYTHON -> IcePap on",self.host," and port",self.port," with timeout = ",self.timeout
        
#        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        self.sock.settimeout(self.timeout)
#        self.sock.connect(("icepap", self.port))
#        self.socket_connected = True
        
        print "PYTHON -> Connected to", self.host, " on port", self.port
        
#
# Check that the Icepap is OK
#

#        ans = self.IceWriteRead("?ID")
        
        
    def AddDevice(self,axis):
        print "PYTHON -> IcePapController/",self.inst_name,": In AddDevice method for axis",axis
#        raise RuntimeError,"Hola la la"
        
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

    def IceWrite(self,data):
        data = data + "\n"
        byteSent = self.sock.send(data)
        print "PYTHON -> Sent", byteSent, "bytes to icepap"
        
    def IceWriteRead(self,data):
        self.IceWrite(data)
        byteReceived = self.sock.recv(1024)
        print "PYTHON -> Icepap answered:",byteReceived
        return byteReceived

    def IceResetFifo(self):
        self.IceWrite("fiforst")
        
    def IceCheckError(self,ice_answer):
        if (ice_answer.find("ERROR") != -1):
            new_ans = self.IceWriteRead("?ERR 1")
            print "Error from IcePap =",new_ans
        
    def __del__(self):
        print "PYTHON -> IcePapController/",self.inst_name,": Aarrrrrg, I am dying"
        
#
# Reset IcePap FIFO
#

        if (self.socket_connected == True):
            print "PYTHON -> Closing connection"
            self.IceResetFifo()
            self.sock.close()

        
if __name__ == "__main__":
    obj = IcePapController('test')
#    obj.AddDevice(2)
#    obj.DeleteDevice(2)

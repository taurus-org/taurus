import unittest
import PyTango
import sys
import os
import time
import PoolTestUtil
import posix        
            
                        
#---------------------------------------------------------------------------------------------------------------------            
class SendCtrl(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.admin_name = "dserver/" + ds_full_name
        
        self.ctrl_added = False
        self.prop_added = False
        
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        if self.pool_configured(self.pool) == False:
            self.empty_pool(self.pool)
            self.create_ctrl_mot(self.pool)
            
#---------------------------------------------------------------------------------------------------------------------
               
    def SendCtrl_test(self):
        """Pool SendToCtrl command"""

#
# Check command on a Cpp and Python controller
#
      
        ret = self.pool.command_inout("SendToController",["hello controller","cpp_ctrl"])
        self.assertEqual(ret,"Hasta luego")
        
        ret = self.pool.command_inout("SendToController",["hello controller","first"])
        self.assertEqual(ret,"Adios")
        
        ret = self.pool.command_inout("SendToController",["hello C/T controller","Py_Vct6"])
        self.assertEqual(ret,"Adios")
        
        ret = self.pool.command_inout("SendToController",["hello C/T controller","Cpp_ZeroD"])
        self.assertEqual(ret,"Hasta luego")

#
# Create a controller without SendToCtrl defined
#
        
        self.db = PyTango.Database()
        prop = {'Host':["icepap"],'Port':['5555']}
        self.db.put_property("IcePapController/222",prop)
        self.prop_added = True
        
        self.pool.command_inout("CreateController",["Motor","WaterPapCtrl_prop.py","IcePapController","222"])
        self.ctrl_added = True
        
        self.wrong_argument(self.pool,"SendToController",["hello controller","222"],"PyCtrl_CantSendToCtrl")
                       
#---------------------------------------------------------------------------------------------------------------------
               
    def StupidSendCtrl_test(self):
        """Pool sutpid SendToCtrl command arguments"""
        
        self.wrong_argument(self.pool,"SendToController",["first"],"Pool_WrongArgument")
        self.wrong_argument(self.pool,"SendToController",["first","second","third"],"Pool_WrongArgument")
        self.wrong_argument(self.pool,"SendToController",["aaa","truc"],"Pool_ControllerNotFound")
                     
#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self): 
        if self.prop_added == True:
            self.db.delete_property("IcePapController/222",["Host","Port"])
            
        if self.ctrl_added == True:
            self.pool.command_inout("DeleteController","222") 
        
        
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

          
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print len(sys.argv)
        print "SendCtrl usage = SendCtrl <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)

    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,SendCtrl,dev_name,sys.argv[1],"StupidSendCtrl_test")
    PoolTestUtil.start_test(runner,SendCtrl,dev_name,sys.argv[1],"SendCtrl_test")

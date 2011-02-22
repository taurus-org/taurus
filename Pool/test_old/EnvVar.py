import unittest
import PyTango
import sys
import os
import time
import PoolTestUtil

class NoEnvVarPool(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,t_num,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.ds_full_name = ds_full_name
        self.ds_exec,self.ds_inst = self.ds_full_name.split('/')
        self.start_ds_str = self.ds_exec + " " + self.ds_inst + " 2>&1 >/dev/null &"
        self.admin_dev = "dserver/" + self.ds_full_name
        self.test_number = t_num
        
    def setUp(self):
        self.ld_lib_path = os.environ["LD_LIBRARY_PATH"]
        self.python_path = os.environ["PYTHONPATH"]

        wrong_ld_lib = "/home/etaurel/bin/et-glibc-2.3.4:/storage00/etaurel/tango/install/suse93/lib:/local/tango/omniORB-4.0.6//lib:/local/tango/omniNotify-2.1/lib:/local/tango/tango-5.3.0/lib:/storage00/etaurel/tango/python_binding/src/bin/boost/libs/python/build/libboost_python.so/gcc/release/shared-linkable-true"
        if (self.test_number == 0):
            os.environ["LD_LIBRARY_PATH"] = wrong_ld_lib
            os.unsetenv("PYTHONPATH")
        elif (self.test_number == 1):
            os.environ["PYTHONPATH"] = "/usr"
        elif (self.test_number == 2):
            os.environ["LD_LIBRARY_PATH"] = wrong_ld_lib    
 
        os.system(self.start_ds_str)
        time.sleep(2)
               
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)
        
        self.pool_admin = PyTango.DeviceProxy(self.admin_dev)

    def emptyvar(self):
        """PYTHONPATH environment variable not defined"""
        self.wrong_argument(self.pool,"CreateController",["Motor","a.py","b","x"],"Pool_EnvVarNotDefined")
        self.wrong_argument(self.pool,"CreateController",["Motor","a.so","b","x"],"Pool_ControllerNotFound")
        
    def badvar(self):
        """Bad environment variables"""
        self.wrong_argument(self.pool,"CreateController",["Motor","a.py","b","x"],"Pool_ExternalElementNotFound")
        self.wrong_argument(self.pool,"CreateController",["Motor","a.so","b","x"],"Pool_ControllerNotFound")
        
    def goodpy_badld(self):
        """Good PYTHONPATH but bad LD_LIBRARY_PATH"""
        self.wrong_argument(self.pool,"CreateController",["Motor","WaterPapCtrl.py","b","x"],"Pool_CantLoadPyControllerInterLibrary")
        self.wrong_argument(self.pool,"CreateController",["Motor","a.so","b","x"],"Pool_ControllerNotFound")
                               
    def tearDown(self):
        os.environ["PYTHONPATH"] = self.python_path
        os.environ["LD_LIBRARY_PATH"] = self.ld_lib_path
        
        self.pool_admin.command_inout("kill")
        time.sleep(1)

#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------                  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print len(sys.argv)
        print "EnvVar usage = EnvVar <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)

    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,NoEnvVarPool,dev_name,sys.argv[1],0,"emptyvar")
    PoolTestUtil.start_test(runner,NoEnvVarPool,dev_name,sys.argv[1],1,"badvar")
    PoolTestUtil.start_test(runner,NoEnvVarPool,dev_name,sys.argv[1],2,"goodpy_badld")
    
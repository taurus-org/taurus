import unittest
#import unittestgui
import PyTango
import sys
import os
import time
import user
import PoolTestUtil

class TestPool(PoolTestUtil.TestUtil):
    
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.__testMethodName = methodName
        self.dev_name = dev_name
        self.ds_full_name = ds_full_name
        self.ds_exec,self.ds_inst = self.ds_full_name.split('/')
        self.start_ds_str = self.ds_exec + " " + self.ds_inst + " 1> /dev/null  2>&1 &"
        self.admin_dev = "dserver/" + self.ds_full_name
        
        self.bdir = PoolTestUtil.GetBasePath()
        self.pydir = self.bdir + "/test/pseudo_motor/test_pm"

#---------------------------------------------------------------------------------------------------------------------

    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)
# VALGRIND        self.pool.set_timeout_millis(10000)

        os.system('/bin/cp %s/PseudoLib.py.original %s/PseudoLib.py' % (self.pydir,self.pydir))
        
        self.empty_pool(self.pool)
        
        if self.__testMethodName in ["CreateRem_PseudoMotor","GetPseudoMotorInfo","ReloadPseudoMotorCode","ReloadEmptyPseudoMotorCode"]:
            self.pool.command_inout("CreateController",["Motor","DummyCtrl.so","DummyController","cpp_ctrl"])
            self.pool.command_inout("CreateMotor",([1],["testmotor01","cpp_ctrl"]))
            self.pool.command_inout("CreateMotor",([2],["testmotor02","cpp_ctrl"]))
            self.pool.command_inout("CreateMotor",([3],["testmotor03","cpp_ctrl"]))
            self.pool.command_inout("CreateMotor",([4],["testmotor04","cpp_ctrl"]))

#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        if self.__testMethodName in ["CreateRem_PseudoMotor","GetPseudoMotorInfo","ReloadPseudoMotorCode","ReloadEmptyPseudoMotorCode"]:
            self.pool.command_inout("DeleteMotor","testmotor01")
            self.pool.command_inout("DeleteMotor","testmotor02")
            self.pool.command_inout("DeleteMotor","testmotor03")
            self.pool.command_inout("DeleteMotor","testmotor04")
            self.pool.command_inout("DeleteController","cpp_ctrl")
        
        if self.__testMethodName == "GetPseudoMotorInfo":
            PyTango.Database().delete_property("PseudoLibProps.P2/P2_pm_testmotor01",["p_no_dft"])

        os.system('/bin/cp %s/PseudoLib.py.original %s/PseudoLib.py' % (self.pydir,self.pydir))

#----------------------------------------------------------------------------------------------------------------------
            
    def emptypool(self):
        """Checking an empty pool"""
        sta = self.pool.command_inout("State")
        self.assertEqual(sta,PyTango.DevState.ON,"State must be ON and is %s"% (sta))
        
        sta = self.pool.command_inout("Status")
        the_sta = '''The device is in ON state.'''
        self.assertEqual(sta,the_sta,"Status must be\n%s\n and is\n%s" % (the_sta,sta))

#
# These attributes must be empty
#

        self.check_empty_attribute(self.pool,"ControllerList")
        self.check_empty_attribute(self.pool,"MotorList")
        self.check_empty_attribute(self.pool,"MotorGroupList")
        self.check_empty_attribute(self.pool,"ExpChannelList")
        
 #
 # Simulation mode must be False
 #
        
        sim = self.pool.read_attribute("SimulationMode")
        self.assertEqual(sim.value,False)
        

#----------------------------------------------------------------------------------------------------------------------
            
    def stupidCreatePseudoMotorArgs(self):
        """Stupid argument(s) for the CreatePseudoMotor command"""
        self.wrong_argument(self.pool,"CreatePseudoMotor",[],"Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool,"CreatePseudoMotor",["PseudoLib.py"],"Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool,"CreatePseudoMotor",["PseudoLib.py","Slit"],"Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool,"CreatePseudoMotor",["PseudoLib.py","Slit","testgap01"],"Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool,"CreatePseudoMotor",["PseudoLib.py","Slit","testgap01","testoffset01"],"Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool,"CreatePseudoMotor",["PseudoLib.py","Slit","testgap01","testoffset01","testmotor01"],"Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool,"CreatePseudoMotor",["InexistingLib.py","Slit","testgap01","testoffset01","testmotor01","testmotor02"],"Pool_CantLocatePythonModule")
        self.wrong_argument(self.pool,"CreatePseudoMotor",["PseudoLib.py","InexistingPseudoMotorControllerClass","testgap01","testoffset01","testmotor01","testmotor02"],"Pool_CantLocatePythonClass")
        self.wrong_argument(self.pool,"CreatePseudoMotor",["PseudoLib.py","Slit","testgap01","testoffset01","inexistingmotor","testmotor02"],"Pool_MotorNotDefined")        
        
#----------------------------------------------------------------------------------------------------------------------
            
    def stupidGetPseudoMotorInfoArgs(self):
        """Stupid argument(s) for the GetPseudoMotorInfo command"""
        self.wrong_argument(self.pool,"GetPseudoMotorInfo",["Slit"],"Pool_WrongArgument")
        self.wrong_argument(self.pool,"GetPseudoMotorInfo",["InexistingLib.py","Slit"],"Pool_CantLocatePythonModule")
        self.wrong_argument(self.pool,"GetPseudoMotorInfo",["PseudoLib.py","InexistingPseudoMotorControllerClass"],"Pool_CantLocatePythonClass")
        self.wrong_argument(self.pool,"GetPseudoMotorInfo",["PseudoLib.py","DontInheritFromPseudoMotor"],"Pool_CantLocatePythonClass")
#        self.wrong_argument(self.pool,"GetPseudoMotorInfo",["PseudoLib.py","DontImplementMethods"],"Pool_PythonMethodNotFound")

#----------------------------------------------------------------------------------------------------------------------
            
    def CreateRem_PseudoMotor(self):
        """Create - Delete Pseudo Motor"""
        
#
# Create a Pseudo Motor system
#
        self.pool.command_inout("CreatePseudoMotor",["PseudoLib.py","Slit","testgap01","testoffset01","testmotor01","testmotor02"])

#
# Creating 2 times the same Pseudo Motor is an error
#
        self.wrong_argument(self.pool,"CreatePseudoMotor",["PseudoLib.py","Slit","testgap01","testoffset01","testmotor01","testmotor02"],"Pool_PseudoMotorAlreadyCreated")

#
# Create a second Pseudo Motor
#
        self.pool.command_inout("CreatePseudoMotor",["PseudoLib.py","Slit","testgap02","testoffset02","testmotor03","testmotor04"])

#
# Check the list of existing pseudo motors
#
        pseudo_list = self.pool.read_attribute("PseudoMotorList")
        self.assertEqual(pseudo_list.dim_x,4)
        self.assertEqual(pseudo_list.value[0],"testgap01 (pm/pseudolib.slit/testgap01) Motor list: testmotor01, testmotor02")
        self.assertEqual(pseudo_list.value[1],"testoffset01 (pm/pseudolib.slit/testoffset01) Motor list: testmotor01, testmotor02")
        self.assertEqual(pseudo_list.value[2],"testgap02 (pm/pseudolib.slit/testgap02) Motor list: testmotor03, testmotor04")
        self.assertEqual(pseudo_list.value[3],"testoffset02 (pm/pseudolib.slit/testoffset02) Motor list: testmotor03, testmotor04")
        mg_list = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(mg_list.dim_x,2)
        
#
# Delete one pseudo motor and check pseudo motor list attribute
#       
        self.pool.command_inout("DeletePseudoMotor","testoffset02")
        pseudo_list = self.pool.read_attribute("PseudoMotorList")
        self.assertEqual(pseudo_list.dim_x,3)
        self.assertEqual(pseudo_list.value[0],"testgap01 (pm/pseudolib.slit/testgap01) Motor list: testmotor01, testmotor02")
        self.assertEqual(pseudo_list.value[1],"testoffset01 (pm/pseudolib.slit/testoffset01) Motor list: testmotor01, testmotor02")
        self.assertEqual(pseudo_list.value[2],"testgap02 (pm/pseudolib.slit/testgap02) Motor list: testmotor03, testmotor04")
        mg_list = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(mg_list.dim_x,2)

#
# Delete one pseudo motor and check pseudo motor list attribute
#       
        self.pool.command_inout("DeletePseudoMotor","testgap02")
        pseudo_list = self.pool.read_attribute("PseudoMotorList")
        self.assertEqual(pseudo_list.dim_x,2)
        self.assertEqual(pseudo_list.value[0],"testgap01 (pm/pseudolib.slit/testgap01) Motor list: testmotor01, testmotor02")
        self.assertEqual(pseudo_list.value[1],"testoffset01 (pm/pseudolib.slit/testoffset01) Motor list: testmotor01, testmotor02")
        mg_list = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(mg_list.dim_x,1)

#
# Delete one pseudo motor and check pseudo motor list attribute
#       
        self.pool.command_inout("DeletePseudoMotor","testoffset01")
        pseudo_list = self.pool.read_attribute("PseudoMotorList")
        self.assertEqual(pseudo_list.dim_x,1)
        self.assertEqual(pseudo_list.value[0],"testgap01 (pm/pseudolib.slit/testgap01) Motor list: testmotor01, testmotor02")
        mg_list = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(mg_list.dim_x,1)

#
# Delete an uncreated controller
#
        self.wrong_argument(self.pool,"DeletePseudoMotor","sillypseudomotor","Pool_PseudoMotorNotFound")            
        
#
# Delete the last pseudomotor. The Pseudo Motor list attribute is now empty
#
        self.pool.command_inout("DeletePseudoMotor","testgap01")
        self.check_empty_attribute(self.pool,"PseudoMotorList")
        self.check_empty_attribute(self.pool,"MotorGroupList")
    
#----------------------------------------------------------------------------------------------------------------------

    def aux_check_property(self,seq,name,type,descr,dftvalue = None):
        index = seq.index(name)
        self.failIf(index < 0)
        self.assertEqual(seq[index+1],type)
        self.assertEqual(seq[index+2],descr)
        
        if dftvalue != None:
            self.assertEqual(seq[index+3],dftvalue)
        else:
            self.assertEqual(seq[index+3],"")

#----------------------------------------------------------------------------------------------------------------------
            
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print len(sys.argv)
        print "PoolTst usage = PoolTst <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,TestPool,dev_name,sys.argv[1],"emptypool")
    PoolTestUtil.start_test(runner,TestPool,dev_name,sys.argv[1],"stupidCreatePseudoMotorArgs")
    PoolTestUtil.start_test(runner,TestPool,dev_name,sys.argv[1],"stupidGetPseudoMotorInfoArgs")
    PoolTestUtil.start_test(runner,TestPool,dev_name,sys.argv[1],"CreateRem_PseudoMotor")
    
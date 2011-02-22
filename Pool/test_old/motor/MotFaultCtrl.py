import unittest
import PyTango
import sys
import os
import time
import PoolTestUtil
import posix      

#-------------------------------------------------------------------------------------------------------------------
#
#        New test class
#
#-------------------------------------------------------------------------------------------------------------------

class FaultyCtrl(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.admin_name = "dserver/" + ds_full_name
        
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)
        
        self.admin = PyTango.DeviceProxy(self.admin_name)
        self.admin.set_transparency_reconnection(True)
        
        self.empty_pool(self.pool)

        self.pool.command_inout("CreateController",["Motor","WaterPapCtrl.py","IcePapController","first"])
        self.pool.command_inout("CreateController",["Motor","DummyCtrl.so","DummyController","cpp_ctrl"])
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,2)
        ctrl1_str = "first (WaterPapCtrl.IcePapController/first) - Motor Python ctrl (WaterPapCtrl.py)"
        ctrl2_str = "cpp_ctrl (DummyCtrl.DummyController/cpp_ctrl) - Motor Cpp ctrl (DummyCtrl.so)"
        self.assertEqual(ctrl_list.value[0],ctrl1_str)
        self.assertEqual(ctrl_list.value[1],ctrl2_str)
        
        self.pool.command_inout("CreateMotor",([0],["First_Motor","first"]))
        self.pool.command_inout("CreateMotor",([1],["Test_Motor","cpp_ctrl"]))

        mot_list = self.pool.read_attribute("MotorList")
        self.assertEqual(mot_list.dim_x,2)
        mot1_str = "First_Motor (motor/first/0)"
        mot2_str = "Test_Motor (motor/cpp_ctrl/1)"
        self.assertEqual(mot_list.value[0],mot1_str)
        self.assertEqual(mot_list.value[1],mot2_str)
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.mot1 = PyTango.DeviceProxy("First_Motor")
        self.assertEqual(self.mot1.state(),PyTango.DevState.ON)
        self.mot2 = PyTango.DeviceProxy("Test_Motor")
        self.assertEqual(self.mot2.state(),PyTango.DevState.ON)

        self.simu_ctrl_admin = PyTango.DeviceProxy("dserver/SimuMotorCtrl/test")
        
#---------------------------------------------------------------------------------------------------------------------
               
    def FaultyCtrl_test(self):
        """Motor with a wrong controller"""
        
#
# This should work
#

        self.assertEqual(self.mot2.state(),PyTango.DevState.ON)
        
#
# Kill the motor simulator device server
#

        self.simu_ctrl_admin.command_inout("Kill")
        time.sleep(4)
        
#
# The motor state is UNKNOWN
#

        self.assertEqual(self.mot2.state(),PyTango.DevState.UNKNOWN)
        mot_status = self.mot2.status()
        self.assertNotEqual(mot_status.find("Error reported from controller"),-1)

#
# It is not possible to read any attributes nor to execute any command
#

        self.attribute_error(self.mot2,"Position","API_AttrNotAllowed")
        self.attribute_error(self.mot2,"SimulationMode","API_AttrNotAllowed")
        self.attribute_error(self.mot2,"Acceleration","API_AttrNotAllowed")
        self.attribute_error(self.mot2,"Deceleration","API_AttrNotAllowed")
        self.attribute_error(self.mot2,"Base_rate","API_AttrNotAllowed")
        self.attribute_error(self.mot2,"Velocity","API_AttrNotAllowed")
        
        self.wrong_argument(self.mot2,"Abort",[],"API_CommandNotAllowed")
        self.wrong_argument(self.mot2,"DefinePosition",0,"API_CommandNotAllowed")
        self.wrong_argument(self.mot2,"SaveConfig",[],"API_CommandNotAllowed") 

        att_val = PyTango.AttributeValue()
        att_val.name = "Position"
        att_val.value = 0.0
        self.wr_attribute_error(self.mot2,att_val,"API_AttrNotAllowed")
        att_val.name = "Acceleration"
        self.wr_attribute_error(self.mot2,att_val,"API_AttrNotAllowed")
        att_val.name = "Deceleration"
        self.wr_attribute_error(self.mot2,att_val,"API_AttrNotAllowed")
        att_val.name = "Base_rate"
        self.wr_attribute_error(self.mot2,att_val,"API_AttrNotAllowed")
        att_val.name = "Velocity"
        self.wr_attribute_error(self.mot2,att_val,"API_AttrNotAllowed") 
        
        self.assertEqual(self.mot2.state(),PyTango.DevState.UNKNOWN)
        mot_status = self.mot2.status()
        self.assertNotEqual(mot_status.find("Error reported from controller"),-1)  


#---------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "MotTst usage = MotTst <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,FaultyCtrl,dev_name,sys.argv[1],"FaultyCtrl_test")
    

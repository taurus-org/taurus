import unittest
import PyTango
import sys
import os
import time
import PoolTestUtil
import posix        
            
                        
#---------------------------------------------------------------------------------------------------------------------            
class InitCtrl(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.admin_name = "dserver/" + ds_full_name
        
        self.file_changed = False
        self.coti_file_changed = False
        self.zerod_file_changed = False
        
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)

        self.admin = PyTango.DeviceProxy(self.admin_name)
        self.admin.set_transparency_reconnection(True)
# VALGRIND        self.admin.set_timeout_millis(10000)
                
        self.empty_pool(self.pool)
        
        self.pool.command_inout("CreateController",["Motor","FirePapCtrl.py","FirePapController","the_good_one"])
        
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,1)
        ctrl_str = "the_good_one (FirePapCtrl.FirePapController/the_good_one) - Motor Python ctrl (FirePapCtrl.py)"
        self.assertEqual(ctrl_list.value[0],ctrl_str)
        
        id_mot = self.pool.command_inout("CreateMotor",([0],["Good_Motor","the_good_one"]))

        mot_list = self.pool.read_attribute("MotorList")
        self.assertEqual(mot_list.dim_x,1)
        mot_str = "Good_Motor (motor/the_good_one/0)"
        self.assertEqual(mot_list.value[0],mot_str)
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.mot_first_ctrl = PyTango.DeviceProxy("Good_Motor")
        self.assertEqual(self.mot_first_ctrl.state(),PyTango.DevState.ON)
            
#---------------------------------------------------------------------------------------------------------------------
               
    def InitCtrl_test(self):
        """Pool InitController command on motor controller"""
        
#
# Load a correct controller and create on motor using this controller
#

        self.pool.command_inout("CreateController",["Motor","WaterPapCtrl.py","IcePapController","the_ctrl"])
        self.pool.command_inout("CreateMotor",([0],["the_motor","the_ctrl"]))
        self.proxy_mot = PyTango.DeviceProxy("the_motor")
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.assertEqual(self.proxy_mot.state(),PyTango.DevState.ON)

#
# InitController on a valid controller does nothing
#
        
        self.pool.command_inout("InitController","the_ctrl")

#
# Change the controller with one generating exception at startup phase
#

        posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_ok.py")
        posix.rename("ctrl/test_ctrl/WaterPapCtrl_init.py","ctrl/test_ctrl/WaterPapCtrl.py")
        self.file_changed = True
        
#
# Send an init command to the admin device
#

        self.admin.command_inout("Init")
        
#
# Check pool/motor state
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ALARM)
        self.assertEqual(self.proxy_mot.state(),PyTango.DevState.FAULT)

        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,2)
        mot_list = self.pool.read_attribute("MotorList")
        self.assertEqual(mot_list.dim_x,2)
                
        pool_status = self.pool.status()
        self.assertNotEqual(pool_status.find("Error reported when trying to create controller"),-1)
        py24msg_result = pool_status.find("Name or service not known")
        if py24msg_result == -1:
            py25msg_result = pool_status.find("No address associated with hostname")
            if py25msg_result == -1:
                self.assertFalse("Unexpected message from socket")
        mot_status = self.proxy_mot.status()
        self.assertNotEqual(mot_status.find("The device is in FAULT state"),-1)
        
#
# Send the InitController command but the result should still be wrong
#

        self.wrong_argument(self.pool,"InitController","the_ctrl","Pool_PythonControllerError")
        pool_status = self.pool.status()
        self.assertNotEqual(pool_status.find("Error reported when trying to create controller"),-1)
        py24msg_result = pool_status.find("Name or service not known")
        if py24msg_result == -1:
            py25msg_result = pool_status.find("No address associated with hostname")
            if py25msg_result == -1:
                self.assertFalse("Unexpected message from socket")
        mot_status = self.proxy_mot.status()
        self.assertNotEqual(mot_status.find("The device is in FAULT state"),-1)
        
#
# Send the InitController command
#

        self.pool.command_inout("InitController","the_ctrl")
        
#
# Check pool/motor state
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.assertEqual(self.proxy_mot.state(),PyTango.DevState.ON)

        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,2)
        mot_list = self.pool.read_attribute("MotorList")
        self.assertEqual(mot_list.dim_x,2)
                
        pool_status = self.pool.status()
        mot_status = self.proxy_mot.status()
        
#---------------------------------------------------------------------------------------------------------------------
               
    def InitCTCtrl_test(self):
        """Pool InitController command on Counter Timer controller"""
        
#
# Load a correct controller and create on CT using this controller
#

        self.pool.command_inout("CreateController",["CounterTimer","Vct6Ctrl.py","Vct6Controller","Py_Vct6"])
        self.pool.command_inout("CreateExpChannel",([0],["the_CT","Py_Vct6"]))
        self.proxy_ct = PyTango.DeviceProxy("the_CT")
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.assertEqual(self.proxy_ct.state(),PyTango.DevState.ON)

#
# InitController on a valid controller does nothing
#
        
        self.pool.command_inout("InitController","Py_Vct6")

#
# Change the controller with one generating exception at startup phase
#

        posix.rename("ctrl/coti_ctrl/Vct6Ctrl.py","ctrl/coti_ctrl/Vct6Ctrl_ok.py")
        posix.rename("ctrl/coti_ctrl/Vct6Ctrl_init.py","ctrl/coti_ctrl/Vct6Ctrl.py")
        self.coti_file_changed = True
        
#
# Send an init command to the admin device
#

        self.admin.command_inout("Init")
        
#
# Check pool/counter state
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ALARM)
        self.assertEqual(self.proxy_ct.state(),PyTango.DevState.FAULT)

        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,2)
        ct_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(ct_list.dim_x,1)
                
        pool_status = self.pool.status()
        self.assertNotEqual(pool_status.find("Error reported when trying to create controller"),-1)
        self.assertNotEqual(pool_status.find("NameError: Ouuups"),-1)
        ct_status = self.proxy_ct.status()
        self.assertNotEqual(ct_status.find("The device is in FAULT state"),-1)
        
#
# Send the InitController command but the result should still be wrong
#

        self.wrong_argument(self.pool,"InitController","Py_Vct6","Pool_PythonControllerError")
        pool_status = self.pool.status()
        self.assertNotEqual(pool_status.find("Error reported when trying to create controller"),-1)
        self.assertNotEqual(pool_status.find("NameError: Ouuups"),-1)
        ct_status = self.proxy_ct.status()
        self.assertNotEqual(ct_status.find("The device is in FAULT state"),-1)
        
#
# Send the InitController command
#

        self.pool.command_inout("InitController","Py_Vct6")
        
#
# Check pool/CT state
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.assertEqual(self.proxy_ct.state(),PyTango.DevState.ON)

        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,2)
        ct_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(ct_list.dim_x,1)
                
        pool_status = self.pool.status()
        ct_status = self.proxy_ct.status()
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Init0DCtrl_test(self):
        """Pool InitController command on Zero D Exp Channel controller"""
        
#
# Load a correct controller and create on Exp Channel using this controller
#

        self.pool.command_inout("CreateController",["ZeroDExpChannel","ElecMeter.py","ElecMeterController","Py_ZeroD"])
        self.pool.command_inout("CreateExpChannel",([0],["the_ZeroD","Py_ZeroD"]))
        self.proxy_zerod = PyTango.DeviceProxy("the_ZeroD")
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.assertEqual(self.proxy_zerod.state(),PyTango.DevState.ON)

#
# InitController on a valid controller does nothing
#
        
        self.pool.command_inout("InitController","Py_ZeroD")

#
# Change the controller with one generating exception at startup phase
#

        posix.rename("ctrl/zerod_ctrl/ElecMeter.py","ctrl/zerod_ctrl/ElecMeter_ok.py")
        posix.rename("ctrl/zerod_ctrl/ElecMeter_init.py","ctrl/zerod_ctrl/ElecMeter.py")
        self.zerod_file_changed = True
        
#
# Send an init command to the admin device
#

        self.admin.command_inout("Init")
        
#
# Check pool/counter state
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ALARM)
        self.assertEqual(self.proxy_zerod.state(),PyTango.DevState.FAULT)

        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,2)
        zero_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(zero_list.dim_x,1)
                
        pool_status = self.pool.status()
        self.assertNotEqual(pool_status.find("Error reported when trying to create controller"),-1)
        self.assertNotEqual(pool_status.find("NameError: Aille Aille Aille"),-1)
        zero_status = self.proxy_zerod.status()
        self.assertNotEqual(zero_status.find("The device is in FAULT state"),-1)
        
#
# Send the InitController command but the result should still be wrong
#

        self.wrong_argument(self.pool,"InitController","Py_ZeroD","Pool_PythonControllerError")
        pool_status = self.pool.status()
        self.assertNotEqual(pool_status.find("Error reported when trying to create controller"),-1)
        self.assertNotEqual(pool_status.find("NameError: Aille Aille Aille"),-1)
        zero_status = self.proxy_zerod.status()
        self.assertNotEqual(zero_status.find("The device is in FAULT state"),-1)
        
#
# Send the InitController command
#

        self.pool.command_inout("InitController","Py_ZeroD")
        
#
# Check pool/ZeroD state
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.assertEqual(self.proxy_zerod.state(),PyTango.DevState.ON)

        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,2)
        ct_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(ct_list.dim_x,1)
                
#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        if self.file_changed == True:
            posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_init.py")
            posix.rename("ctrl/test_ctrl/WaterPapCtrl_ok.py","ctrl/test_ctrl/WaterPapCtrl.py")
            
        if self.coti_file_changed == True:
            posix.rename("ctrl/coti_ctrl/Vct6Ctrl.py","ctrl/coti_ctrl/Vct6Ctrl_init.py")
            posix.rename("ctrl/coti_ctrl/Vct6Ctrl_ok.py","ctrl/coti_ctrl/Vct6Ctrl.py")
            
        if self.zerod_file_changed == True:
            posix.rename("ctrl/zerod_ctrl/ElecMeter.py","ctrl/zerod_ctrl/ElecMeter_init.py")
            posix.rename("ctrl/zerod_ctrl/ElecMeter_ok.py","ctrl/zerod_ctrl/ElecMeter.py")
        
        self.empty_pool(self.pool)
        
#-------------------------------------------------------------------------------------------------------------------
#
#        New test class
#
#-------------------------------------------------------------------------------------------------------------------


class StupidInitCtrl(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.admin_name = "dserver/" + ds_full_name
        
        self.file_changed = False
        
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)

        self.admin = PyTango.DeviceProxy(self.admin_name)
        self.admin.set_transparency_reconnection(True)
                
        self.empty_pool(self.pool)
        self.id_ctrl = self.pool.command_inout("CreateController",["Motor","WaterPapCtrl.py","IcePapController","the_bad_one"])
        
        posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_ok.py")
        posix.rename("ctrl/test_ctrl/WaterPapCtrl_mis.py","ctrl/test_ctrl/WaterPapCtrl.py")
        
        self.admin.command_inout("Init")
            
        
#---------------------------------------------------------------------------------------------------------------------
               
    def StupidInitCtrl_test(self):
        """Stupid Pool InitController command arguments"""
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ALARM)
        self.wrong_argument(self.pool,"InitController","aaa","Pool_ControllerNotFound")
        
#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_mis.py")
        posix.rename("ctrl/test_ctrl/WaterPapCtrl_ok.py","ctrl/test_ctrl/WaterPapCtrl.py")
        
        self.empty_pool(self.pool)
        
        
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

          
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print len(sys.argv)
        print "InitCtrl usage = InitCtrl <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)

    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,StupidInitCtrl,dev_name,sys.argv[1],"StupidInitCtrl_test")
    PoolTestUtil.start_test(runner,InitCtrl,dev_name,sys.argv[1],"InitCtrl_test")
    PoolTestUtil.start_test(runner,InitCtrl,dev_name,sys.argv[1],"InitCTCtrl_test")
    PoolTestUtil.start_test(runner,InitCtrl,dev_name,sys.argv[1],"Init0DCtrl_test")

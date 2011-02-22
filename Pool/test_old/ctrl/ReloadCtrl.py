import unittest
import PyTango
import sys
import os
import time
import PoolTestUtil
import posix        
            
                        
#---------------------------------------------------------------------------------------------------------------------            
class ReloadCtrl(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.admin_name = "dserver/" + ds_full_name
        self.admin = PyTango.DeviceProxy(self.admin_name)
        self.admin.set_timeout_millis(5000)
        
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        if self.pool_configured(self.pool) == False:
            self.empty_pool(self.pool)
            self.create_ctrl_mot(self.pool)
            
        self.added_ctrls = False
        self.added_zero_ctrls = False
        self.coti_file_changed = False
        self.zerod_file_changed = False
        
#---------------------------------------------------------------------------------------------------------------------
               
    def ReloadCtrl_test(self):
        """Pool ReloadController command"""

#
# A simple reload with one instance of one class ni one file
#
        
        self.pool.command_inout("ReloadControllerCode","WaterPapCtrl.py")
        self.pool.command_inout("ReloadControllerCode","DummyCtrl.so")
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        
#
# Create a second instance and reload code
#

        self.pool.command_inout("CreateController",["Motor","WaterPapCtrl.py","IcePapController","second"])
        self.added_ctrls = True
        self.pool.command_inout("ReloadControllerCode","WaterPapCtrl.py")
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        
        self.pool.command_inout("CreateController",["Motor","DummyCtrl.so","DummyController","2"])
        self.pool.command_inout("ReloadControllerCode","DummyCtrl.so")
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,6)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def ReloadCTCtrl_test(self):
        """Pool CounterTimer ReloadController command"""

#
# Rename files
#

        posix.rename("ctrl/coti_ctrl/Vct6Ctrl.py","ctrl/coti_ctrl/Vct6Ctrl_ok.py")
        posix.rename("ctrl/coti_ctrl/Vct6Ctrl_syn.py","ctrl/coti_ctrl/Vct6Ctrl.py")
        self.coti_file_changed = True
        
#
# Send an init command on the admin device
#

        self.admin.command_inout("Init")
        
#
# Check that we still have 4 controllers, 7 motors and 3 Exp Channel
#

        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,4)
        
        mot_list = self.pool.read_attribute("MotorList")
        self.assertEqual(mot_list.dim_x,7)
        
        ct_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(ct_list.dim_x,3)
        
#
# The Pool state should be ALARM and two CT state should be FAULT
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ALARM)
        ct1 = PyTango.DeviceProxy("First_CT")
        self.assertEqual(ct1.state(),PyTango.DevState.FAULT)
        ct2 = PyTango.DeviceProxy("Second_CT")
        self.assertEqual(ct2.state(),PyTango.DevState.FAULT)
        
        pool_status = self.pool.status()
        self.assertNotEqual(pool_status.find("SyntaxError: invalid syntax"),-1)

#
# Rename file
#
        
        posix.rename("ctrl/coti_ctrl/Vct6Ctrl.py","ctrl/coti_ctrl/Vct6Ctrl_syn.py")
        posix.rename("ctrl/coti_ctrl/Vct6Ctrl_ok.py","ctrl/coti_ctrl/Vct6Ctrl.py")
        self.coti_file_changed = False
        
#
# Relead controller
#

        self.pool.command_inout("ReloadControllerCode","Vct6Ctrl.py")
        
#
# The Pool state should be ON and two CT state should be ON
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.assertEqual(ct1.state(),PyTango.DevState.ON)
        self.assertEqual(ct2.state(),PyTango.DevState.ON)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Reload0DCtrl_test(self):
        """Pool zero D Exp Channel ReloadController command"""

        self.pool.command_inout("CreateController",["ZeroDExpChannel","ElecMeter.py","ElecMeterController","Py_ZeroD"])
        self.pool.command_inout("CreateExpChannel",([0],["the_ZeroD","Py_ZeroD"]))
        self.added_zero_ctrls == True

        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        zerod = PyTango.DeviceProxy("the_ZeroD")
        self.assertEqual(zerod.state(),PyTango.DevState.ON)
                
#
# Rename files
#

        posix.rename("ctrl/zerod_ctrl/ElecMeter.py","ctrl/zerod_ctrl/ElecMeter_ok.py")
        posix.rename("ctrl/zerod_ctrl/ElecMeter_syn.py","ctrl/zerod_ctrl/ElecMeter.py")
        self.zerod_file_changed = True
        
#
# Send an init command on the admin device
#

        self.admin.command_inout("Init")
        
#
# Check that we still have 5 controllers, 7 motors and 4 ExpChannel
#

        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,5)
        
        mot_list = self.pool.read_attribute("MotorList")
        self.assertEqual(mot_list.dim_x,7)
        
        ct_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(ct_list.dim_x,4)
        
#
# The Pool state should be ALARM and the ZeroD state should be FAULT
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ALARM)
        ct1 = PyTango.DeviceProxy("First_CT")
        self.assertEqual(ct1.state(),PyTango.DevState.ON)
        self.assertEqual(zerod.state(),PyTango.DevState.FAULT)
        
        pool_status = self.pool.status()
        self.assertNotEqual(pool_status.find("SyntaxError: invalid syntax"),-1)

#
# Rename file
#
        
        posix.rename("ctrl/zerod_ctrl/ElecMeter.py","ctrl/zerod_ctrl/ElecMeter_syn.py")
        posix.rename("ctrl/zerod_ctrl/ElecMeter_ok.py","ctrl/zerod_ctrl/ElecMeter.py")
        self.zerod_file_changed = False
        
#
# Relead controller
#

        self.pool.command_inout("ReloadControllerCode","ElecMeter.py")
        
#
# The Pool state should be ON and two CT state should be ON
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.assertEqual(ct1.state(),PyTango.DevState.ON)
        self.assertEqual(zerod.state(),PyTango.DevState.ON)
        
        
#---------------------------------------------------------------------------------------------------------------------
               
    def StupidReloadCtrl_test(self):
        """Pool sutpid ReloadController command arguments"""
        
        self.wrong_argument(self.pool,"ReloadControllerCode","a/WaterPapCtrl.py","Pool_FileUnsupportedType")
        self.wrong_argument(self.pool,"reloadControllerCode","abc.py","Pool_ControllerNotFound")
                     
#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        if self.added_ctrls == True:
            self.pool.command_inout("DeleteController","second")
            self.pool.command_inout("DeleteController","2")
            
        if self.added_zero_ctrls == True:
            self.pool.command_inout("DeleteExpChannel","The_ZeroD")
            self.pool.command_inout("DeleteController","Py_ZeroD")
            
        if self.coti_file_changed == True:
            posix.rename("ctrl/coti_ctrl/Vct6Ctrl.py","ctrl/coti_ctrl/Vct6Ctrl_syn.py")
            posix.rename("ctrl/coti_ctrl/Vct6Ctrl_ok.py","ctrl/coti_ctrl/Vct6Ctrl.py")
            
        if self.zerod_file_changed == True:
            posix.rename("ctrl/zerod_ctrl/ElecMeter.py","ctrl/zerod_ctrl/ElecMeter_syn.py")
            posix.rename("ctrl/zerod_ctrl/ElecMeter_ok.py","ctrl/zerod_ctrl/ElecMeter.py")
            
        self.admin.command_inout("Init")
        
        
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

          
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print len(sys.argv)
        print "InitCtrl usage = ReloadCtrl <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)

    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,ReloadCtrl,dev_name,sys.argv[1],"StupidReloadCtrl_test")
    PoolTestUtil.start_test(runner,ReloadCtrl,dev_name,sys.argv[1],"ReloadCtrl_test")
    PoolTestUtil.start_test(runner,ReloadCtrl,dev_name,sys.argv[1],"ReloadCTCtrl_test")
    PoolTestUtil.start_test(runner,ReloadCtrl,dev_name,sys.argv[1],"Reload0DCtrl_test")

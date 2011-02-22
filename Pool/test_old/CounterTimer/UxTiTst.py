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

class UnixTimer(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)
        
        if self.pool_configured(self.pool) == False:
            self.empty_pool(self.pool)
            self.create_ctrl_mot(self.pool)

#
# Add the Unix Timer controller with one EXPChannel
#
            
        self.pool.command_inout("CreateController",["CounterTimer","UxTimer.so","UnixTimer","Tst_unix_timer"])
        
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,5)
        self.assertEqual(ctrl_list.value[4],"Tst_unix_timer (UxTimer.UnixTimer/Tst_unix_timer) - CounterTimer Cpp ctrl (UxTimer.so)")

        self.pool.command_inout("CreateExpChannel",([0],["Ux_Ti","Tst_unix_timer"]))
        
        ct_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(ct_list.dim_x,4)
        self.assertEqual(ct_list.value[0],"First_CT (expchan/py_vct6/0) Counter/Timer Experiment Channel")
        self.assertEqual(ct_list.value[1],"Second_CT (expchan/py_vct6/1) Counter/Timer Experiment Channel")
        self.assertEqual(ct_list.value[2],"Ux_Ti (expchan/tst_unix_timer/0) Counter/Timer Experiment Channel")
        self.assertEqual(ct_list.value[3],"First_ZeroD (expchan/cpp_zerod/0) Zero D Experiment Channel")
                        
        self.unix_ti = PyTango.DeviceProxy("Ux_Ti")
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Counting_test(self):
        """Start the Unix timer (polling mode)"""
                                 
        self.assertEqual(self.unix_ti.state(),PyTango.DevState.ON)

#
# Clear counter value
#

        val_att = PyTango.AttributeValue()
        val_att.name = "Value"
        val_att.value = 0.0
        self.unix_ti.write_attribute(val_att)
                
#
# Read value
#

        val_att = self.unix_ti.read_attribute("Value")
        self.assertEqual(val_att.value,0.0)
        
#
# Write a value
#

        val_att.value = 1.0
        self.unix_ti.write_attribute(val_att)
        
        read_val = self.unix_ti.read_attribute("Value")
        self.assertEqual(read_val.value,0.0)
        
#
# Start counting
#
        
        self.unix_ti.command_inout("Start")
        self.assertEqual(self.unix_ti.state(),PyTango.DevState.MOVING)
        old_att_val = 0
        
        while self.unix_ti.state() == PyTango.DevState.MOVING:
            time.sleep(0.2)
            val_att = self.unix_ti.read_attribute("Value")
            self.assert_(val_att.value >= old_att_val)
            old_att_val = val_att.value
            
        self.assertEqual(self.unix_ti.state(),PyTango.DevState.ON)
        val_att = self.unix_ti.read_attribute("Value")
        self.assertEqual(val_att.value,1.0)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def AbortCounting_test(self):
        """Abort the Unix timer (polling mode)"""
                                 
        self.assertEqual(self.unix_ti.state(),PyTango.DevState.ON)

#
# Write a value in the counter
#

        val = PyTango.AttributeValue()
        val.name = "Value"
        val.value = 2.0
        self.unix_ti.write_attribute(val)
            
#
# Read value
#

        read_val = self.unix_ti.read_attribute("Value")
        self.assertEqual(read_val.value,0.0)
        
#
# Start counting
#
        
        self.unix_ti.command_inout("Start")
        self.assertEqual(self.unix_ti.state(),PyTango.DevState.MOVING)
        
        time.sleep(0.5)
        self.unix_ti.command_inout("stop")
        
        self.assertEqual(self.unix_ti.state(),PyTango.DevState.ON)
        read_val = self.unix_ti.read_attribute("Value")
        self.assert_(read_val.value > 0.350)
        self.assert_(read_val.value < 0.650)
        
#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        self.pool.command_inout("DeleteExpChannel","Ux_Ti")
        self.pool.command_inout("DeleteController","Tst_unix_timer")
        pass
                        
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "UxTiTst usage = UxTiTst <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,UnixTimer,dev_name,sys.argv[1],"Counting_test")
    PoolTestUtil.start_test(runner,UnixTimer,dev_name,sys.argv[1],"AbortCounting_test")


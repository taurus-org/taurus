import unittest
import PyTango
import sys
import os
import time
import PoolTestUtil
import posix     
import random

class ReadWrite(PoolTestUtil.TestUtil):
    def __init__(self, dev_name, ds_full_name, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)
        self.__testMethodName = methodName
        self.dev_name = dev_name
        self.ds_full_name = ds_full_name
        self.ds_exec, self.ds_inst = self.ds_full_name.split('/')
        self.start_ds_str = self.ds_exec + " " + self.ds_inst + " 1>/dev/null 2>&1 &"
        self.admin_dev = "dserver/" + self.ds_full_name
        self.admin_name = "dserver/" + ds_full_name    
        
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)
# VALGRIND        self.pool.set_timeout_millis(10000)

        if self.pool_configured(self.pool) == False:
            self.empty_pool(self.pool)
            self.create_ctrl_mot(self.pool)

        self.admin = PyTango.DeviceProxy(self.admin_name)
        self.admin.set_transparency_reconnection(True)
        
        self.assertEqual(self.pool.state(), PyTango.DevState.ON)
        self.test_mot1 = PyTango.DeviceProxy("Test_Motor")
        self.assertEqual(self.test_mot1.state(), PyTango.DevState.ON)
        self.test_mot2 = PyTango.DeviceProxy("Test_Motor2")
        self.assertEqual(self.test_mot2.state(), PyTango.DevState.ON)
        self.test_pm_gap = PyTango.DeviceProxy("testgap01")
        self.assertEqual(self.test_pm_gap.state(), PyTango.DevState.ON)
        self.test_pm_offset = PyTango.DeviceProxy("testoffset01")
        self.assertEqual(self.test_pm_offset.state(), PyTango.DevState.ON)
        
        self.test_mot1.command_inout("DefinePosition", 1200)
        new_pos = self.test_mot1.read_attribute("Position")
        self.assertEqual(new_pos.value, 1200)
        self.test_mot2.command_inout("DefinePosition", 1700)
        new_pos = self.test_mot2.read_attribute("Position")
        self.assertEqual(new_pos.value, 1700)
        
        self.gap = PyTango.DeviceProxy("testgap01")
        self.offset = PyTango.DeviceProxy("testoffset01")
        
    def tearDown(self):
        try:
            self.empty_pool(self.pool)
        except PyTango.DevFailed, e:
            print "Failed on PM ReadWrite tearDown"
        
    def Read_test(self):
        """Testing reading Position on pseudo device"""

        pos_m1 = self.test_mot1.read_attribute("Position").value
        self.assertEqual(pos_m1,1200)
        pos_m2 = self.test_mot2.read_attribute("Position").value
        self.assertEqual(pos_m2,1700)
        
        gap_shouldbe = pos_m2 - pos_m1
        offset_shoudbe = (pos_m2 + pos_m1) / 2.0
#
# Basic read
#
        gap = self.gap.read_attribute("Position")
        offset = self.offset.read_attribute("Position")
        self.assertEqual(gap.value, gap_shouldbe, "Gap differs")
        self.assertEqual(offset.value, offset_shoudbe, "Offset Differs")
        
    def Write_test(self):
        """Testing writing Position on pseudo motor device"""


        class PyCb:
            def __init__(self):
                self.cb_executed = 0
                self.cb_error = 0
                self.alarm_eve = False
                self.verbose = False
                
            def push_event(self,event):
                self.cb_executed += 1
                if not event.err:
                    if event.attr_value.value == PyTango.DevState.ALARM:
                        self.alarm_eve = True
                    if self.verbose == True:
                        print "Event received:",event.attr_name,", value =",event.attr_value.value
                else:
                    self.cb_error += 1
                    if self.verbose == True:
                        print event.errors
                        
        class Pos_PyCb:
            def __init__(self):
                self.cb_executed = 0
                self.cb_error = 0
                self.verbose = False
                
            def push_event(self,event):
                self.cb_executed += 1
                if not event.err:
                    if self.verbose == True:
                        print "Event received:",event.attr_name,", value =",event.attr_value.value
                else:
                    self.cb_error += 1
                    if self.verbose == True:
                        print event.errors        

        pos = self.gap.read_attribute("Position")
        
#
# Impossible to move a group if one of the group element is
# already moving
#    
        mot_pos = PyTango.AttributeValue()
        mot_pos.name = "Position"
        mot_pos.value = 1250
        self.test_mot1.write_attribute(mot_pos)
        
        pos.value=600
        self.wr_attribute_error(self.gap,pos,"API_AttrNotAllowed")
        
        self.test_mot1.command_inout("Abort")
#
# subscribe to events (on group and on motors member of the group)
#
       
    
    def areEqualError(self,a,b,max_error):
        return (b >= (a - max_error)) and (b <= (a + max_error))
        
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print len(sys.argv)
        print "ReadWrite usage = ReadWrite <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,ReadWrite,dev_name,sys.argv[1],"Read_test")
    PoolTestUtil.start_test(runner,ReadWrite,dev_name,sys.argv[1],"Write_test")
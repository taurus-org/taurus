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

class MotErr(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.ev_error = -1
        self.ev_fault = -1
        self.ev_except = -1
        
        
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)
        
        self.empty_pool(self.pool)
        self.create_ctrl_mot(self.pool)
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.mot1 = PyTango.DeviceProxy("First_Motor")
        self.assertEqual(self.mot1.state(),PyTango.DevState.ON)
        self.mot2 = PyTango.DeviceProxy("Test_Motor")
        self.assertEqual(self.mot2.state(),PyTango.DevState.ON)
        self.mot_error = PyTango.DeviceProxy("Error_Motor")
        self.assertEqual(self.mot_error.state(),PyTango.DevState.ON)
        self.mot_fault = PyTango.DeviceProxy("Fault_Motor")
        self.assertEqual(self.mot_fault.state(),PyTango.DevState.ON)
        self.mot_except = PyTango.DeviceProxy("Except_Motor")
        self.assertEqual(self.mot_except.state(),PyTango.DevState.ON)
        
        class PyCb:
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
#
# subscribe to event
#

        self.cb_error = PyCb()
        self.cb_fault = PyCb()
        self.cb_except = PyCb()
        self.cb_error.verbose = True
        self.cb_fault.verbose = True
        self.cb_except.verbose = True
        
        self.ev_error = self.mot_error.subscribe_event("State",PyTango.EventType.CHANGE,self.cb_error,[])
        self.ev_fault = self.mot_fault.subscribe_event("State",PyTango.EventType.CHANGE,self.cb_fault,[])
        self.ev_except = self.mot_except.subscribe_event("State",PyTango.EventType.CHANGE,self.cb_except,[])
        
#---------------------------------------------------------------------------------------------------------------------
               
    def MotErr_test(self):
        """Moving a motor with faults (event mode)"""
        
#
# First a motor which fails during controller communication
# Force position to 1500
#

        self.mot_error.command_inout("DefinePosition",1500)
        pos = self.mot_error.read_attribute("Position")
        self.assertEqual(pos.value,1500.0)
 
#
# Try to move motor
#
        
        pos.value = pos.value + 20.0
        self.wr_attribute_error(self.mot_error,pos,"Aaaaaa")
 
        time.sleep(0.2)
        self.assertEqual(self.cb_error.cb_executed,3)
        self.assertEqual(self.mot_error.state(),PyTango.DevState.ON)
        
#
# Then a motor in FAULT
#

        self.mot_fault.command_inout("DefinePosition",1500)
        pos = self.mot_fault.read_attribute("Position")
        self.assertEqual(pos.value,1500.0)
 
#
# Try to move motor
#
        
        pos.value = pos.value + 200.0
        self.mot_fault.write_attribute(pos)
        
        time.sleep(0.2)
        
        self.assertEqual(self.mot_fault.state(),PyTango.DevState.FAULT)
        self.assertEqual(self.cb_fault.cb_executed,3)

        self.assertEqual(self.mot_fault.state(),PyTango.DevState.FAULT)
        mot_fault_status = self.mot_fault.status()
        self.assertNotEqual(mot_fault_status,"Testing FAULT state in movement")
        
#
# Then a motor which throws an exception during the move
#

        self.mot_except.command_inout("DefinePosition",1500)
        pos = self.mot_except.read_attribute("Position")
        self.assertEqual(pos.value,1500.0)
 
#
# Try to move motor
#
        
        pos.value = pos.value + 200.0
        self.mot_except.write_attribute(pos)
        
        time.sleep(0.3)
        
        self.assertEqual(self.mot_except.state(),PyTango.DevState.UNKNOWN)
        self.assertEqual(self.cb_except.cb_executed,3)

        self.assertEqual(self.mot_fault.state(),PyTango.DevState.FAULT)
        mot_fault_status = self.mot_fault.status()
        self.assertNotEqual(mot_fault_status,"Testing FAULT state in movement")
                
#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        if self.ev_error == -1:
            self.mot_error.unsubscribe_event(self.ev_error)
            
        if self.ev_fault == -1:
            self.mot_fault.unsubscribe_event(self.ev_fault)
            
        if self.ev_except == -1:
            self.mot_except.unsubscribe_event(self.ev_except)

        simu_ctrl = PyTango.DeviceProxy("Simu/test/motctrl")
        simu_ctrl.command_inout("Init")

        self.pool.command_inout("ReloadControllerCode","DummyCtrl.so")
        time.sleep(0.1)


#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "MotErr usage = MotErr <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,MotErr,dev_name,sys.argv[1],"MotErr_test")

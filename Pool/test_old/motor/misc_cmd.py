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

class Misc(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.pool = PyTango.DeviceProxy(self.dev_name)
        
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
        
        self.ev_id = -1
        
        class PyCb:
            def __init__(self):
                self.cb_executed = 0
                self.cb_error = 0
                self.verbose = False
                self.moving = False
                
            def push_event(self,event):
                self.cb_executed += 1
                if not event.err:
                    if self.verbose == True:
                        print "Event received:",event.attr_name,", value =",event.attr_value.value
                    if event.attr_value.value == PyTango.DevState.MOVING:
                        self.moving = True
                    else:
                        self.moving = False
                else:
                    self.cb_error += 1
                    self.moving = False
                    if self.verbose == True:
                        print event.errors    
#
# subscribe to event
#

        self.cb = PyCb()
        self.cb.verbose = True
        
        self.ev_id = self.mot2.subscribe_event("State",PyTango.EventType.CHANGE,self.cb,[])
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Misc_test(self):
        """Testing motor Abort and DefinePosition commands"""

#
# Check a DefinePosition command
#
        
        self.mot2.command_inout("DefinePosition",1500)
        pos = self.mot2.read_attribute("Position")
        self.assertEqual(pos.value,1500.0)

#
# SetPosition not allowed while it is moving
#

        pos.value = pos.value - 10.0
        self.mot2.write_attribute(pos) 
        
        time.sleep(0.3)
        self.wrong_argument(self.mot2,"DefinePosition",1700,"API_CommandNotAllowed")
        
        while self.cb.moving == True:
            time.sleep(0.1)
            
#
# Check the Abort command
#

        pos = self.mot2.read_attribute("Position")
        self.assertEqual(pos.value,1490.0)
        
        pos.value = pos.value + 300.0
        self.mot2.write_attribute(pos)
        
        time.sleep(1)
        self.mot2.command_inout("Abort")

        time.sleep(1)
        self.assertEqual(self.mot2.state(),PyTango.DevState.ON)
        
#
# We need to sleep a litle while otherwise, the thread executing this code will not give up the
# CPU and the thread executing the callback will not be executed beefore we do the following
# test
#

        time.sleep(0.1)
        self.assertEqual(self.cb.cb_executed,5)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Rounding_test(self):
        """Testing Rounding features"""

#
# Set Offset to 0
#

        off_att = self.mot2.read_attribute("Offset")
        if off_att.value != 0.0:
            off_att.value = 0.0
            self.mot2.write_attribute(off_att)
            
#
# Set step per unit to 5
#

        step_att = PyTango.AttributeValue()
        step_att.name = "Step_per_unit"
        step_att.value = 5
        self.mot2.write_attribute(step_att)
 
 #
 # Set motor position
 #
        
        self.mot2.command_inout("DefinePosition",1500)
        pos = self.mot2.read_attribute("Position")
        self.assertEqual(pos.value,1500.0)
 
#
# This should be rounded to the  lower value
#
       
        pos.value = 1504.08
        self.mot2.write_attribute(pos)
        self.cb.moving = True
        while self.cb.moving == True:
            time.sleep(0.1)
        pos = self.mot2.read_attribute("Position")
        self.assertEqual(pos.value,1504)
 
#
# This should be rounded to the upper value
#
       
        pos.value = 1508.12
        self.mot2.write_attribute(pos)
        self.cb.moving = True
        while self.cb.moving == True:
            time.sleep(0.1)
        pos = self.mot2.read_attribute("Position")
        self.assertEqual(pos.value,1508.2)

#
# this is just in the middle and should be rounded to the
# lower value
#
        
        pos.value = 1512.10
        self.mot2.write_attribute(pos)
        self.cb.moving = True
        while self.cb.moving == True:
            time.sleep(0.1)
        pos = self.mot2.read_attribute("Position")
        self.assertEqual(pos.value,1512)
        
        time.sleep(0.1)
        
#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        if self.ev_id != -1:
            self.mot2.unsubscribe_event(self.ev_id) 
            
        step_att = PyTango.AttributeValue()
        step_att.name = "Step_per_unit"
        step_att.value = 1
        self.mot2.write_attribute(step_att)          
        
        
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "misc_cmd usage = misc_cmd <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,Misc,dev_name,sys.argv[1],"Misc_test")
    PoolTestUtil.start_test(runner,Misc,dev_name,sys.argv[1],"Rounding_test")

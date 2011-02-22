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

class Shut(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.admin_name = "dserver/" + ds_full_name
        self.ev = -1
        
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)

        if self.pool_configured(self.pool) == False:
            self.empty_pool(self.pool)
            self.create_ctrl_mot(self.pool)
            
        self.admin = PyTango.DeviceProxy(self.admin_name)
        self.admin.set_transparency_reconnection(True)
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.mot2 = PyTango.DeviceProxy("Test_Motor")
        self.assertEqual(self.mot2.state(),PyTango.DevState.ON)
        
        self.mot2.command_inout("DefinePosition",1500)
        new_pos = self.mot2.read_attribute("Position")
        self.assertEqual(new_pos.value,1500)
        
        self.pool.command_inout("CreateMotor",([3],["Another_Motor","cpp_ctrl"]))
        self.pool.command_inout("CreateMotor",([4],["Yet_Another","cpp_ctrl"]))
        
        self.another_motor = PyTango.DeviceProxy("Another_Motor")
        self.another_motor.set_transparency_reconnection(True)
        
        self.yam = PyTango.DeviceProxy("Yet_Another")
        
        self.another_motor.command_inout("DefinePosition",1500)
        ano_pos = self.another_motor.read_attribute("Position")
        self.assertEqual(ano_pos.value,1500)
        
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

        cb = PyCb()
        cb.verbose = True
        self.ev = self.pool.subscribe_event("State",PyTango.EventType.CHANGE,cb,[])
        
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Shut_test(self):
        """Testing pool shutdown sequence"""
        
#
# Move one motor
#

        pos = self.another_motor.read_attribute("Position")
        pos.value = pos.value + 50.0
        self.another_motor.write_attribute(pos)
        
        self.assertEqual(self.another_motor.state(),PyTango.DevState.MOVING)
        time.sleep(0.1)
        
#
# Kill the pool
#

        self.admin.command_inout("Kill")
        
#
# Check pool state
#

        time.sleep(2.5)
        self.assertEqual(self.pool.state(),PyTango.DevState.MOVING)
        self.assertEqual(self.another_motor.state(),PyTango.DevState.MOVING)     
        
#
# It is not possible to move another motor
#

        self.attribute_error(self.mot2,"Position","API_DeviceNotExported")
        self.wr_attribute_error(self.yam,pos,"API_AttrNotAllowed")

#
# End for end of movement
#
        
        time.sleep(5)
        
#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self): 
        pass
        
        
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Shut usage = Shut <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,Shut,dev_name,sys.argv[1],"Shut_test")
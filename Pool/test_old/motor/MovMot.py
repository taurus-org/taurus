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

class MovMot(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.pool = PyTango.DeviceProxy(self.dev_name)
        
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)

        if self.pool_configured(self.pool) == False:
            self.empty_pool(self.pool)
            self.create_ctrl_mot(self.pool)
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.mot2 = PyTango.DeviceProxy("Test_Motor")
        self.assertEqual(self.mot2.state(),PyTango.DevState.ON)
        
        self.mot2.command_inout("DefinePosition",1500)
        new_pos = self.mot2.read_attribute("Position")
        self.assertEqual(new_pos.value,1500)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def MovMot_test(self):
        """Testing forbidden commands while motor is moving"""
        
#
# It is not possible to delete a moving motor
#

        pos = self.mot2.read_attribute("Position")
        pos.value = pos.value + 20.0
        self.mot2.write_attribute(pos)
        
        self.assertEqual(self.mot2.state(),PyTango.DevState.MOVING)
        self.wrong_argument(self.pool,"DeleteMotor","Test_Motor","Pool_CantDeleteMotor")
        
#
# It is also not possible to request another movement whiel a motor is moving
#
  
        pos.value = pos.value + 20.0
        self.wr_attribute_error(self.mot2,pos,"API_AttrNotAllowed")
        pos.value = pos.value - 20.0
          
#
# Wait for end of movement
#
        while self.mot2.state() == PyTango.DevState.MOVING:
            time.sleep(0.2)
            
#
# Cannot Reload controller if one of its motor is moving
#

        pos.value = pos.value - 20.0
        self.mot2.write_attribute(pos)
        
        self.assertEqual(self.mot2.state(),PyTango.DevState.MOVING)
        self.wrong_argument(self.pool,"ReloadControllerCode","DummyCtrl.so","Pool_CantUnloadController")
        
#
# Not possible to do a Init command on a moving motor
#

        self.wrong_argument(self.mot2,"Init",[],"Motor_InitNotAllowed")
        
#
# Abort movement
#

        self.mot2.command_inout("Abort")
        
        
#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self): 
        
#
# Give time for motor to decelerate
#
  
        while self.mot2.state() == PyTango.DevState.MOVING:
            time.sleep(0.2)
        
        
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "MovMot usage = MovMot <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,MovMot,dev_name,sys.argv[1],"MovMot_test")

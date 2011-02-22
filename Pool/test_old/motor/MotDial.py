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

class MotDial(PoolTestUtil.TestUtil):
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
               
    def MotDial_test(self):
        """Motor Dial/Offset/Position"""

#
# Set an offset
#

        off = self.mot2.read_attribute("Offset")
        self.assertEqual(off.value, 0.0)
        
        off.value = -200.0
        self.mot2.write_attribute(off)
        
        off = self.mot2.read_attribute("Offset")
        self.assertEqual(off.value,-200)
        
#
# Read Position
#

        pos = self.mot2.read_attribute("Position")
        self.assertEqual(pos.value,1300.0)
        
#
# Read DialPosition
#

        dial_pos = self.mot2.read_attribute("DialPosition")
        self.assertEqual(dial_pos.value,1500)
        
#
# Move the motor
#

        pos.value = pos.value + 20.0
        self.mot2.write_attribute(pos)
        
        while self.mot2.state() == PyTango.DevState.MOVING:
            time.sleep(0.5)
        
#
# Read position and dial position
#

        pos = self.mot2.read_attribute("Position")
        self.assertEqual(pos.value,1320.0)
        dial_pos = self.mot2.read_attribute("DialPosition")
        self.assertEqual(dial_pos.value,1520)
        
#
# Set the simulation mode ON
#

        sim = PyTango.AttributeValue()
        sim.name = "SimulationMode"
        sim.value = True
        self.pool.write_attribute(sim)
        
        mot_sim = self.mot2.read_attribute("SimulationMode")
        self.assertEqual(mot_sim.value,True)
        
#
# Change the offset
#
  
        sim_off = self.mot2.read_attribute("Offset")
        self.assertEqual(sim_off.value,-200.0)
 
        sim_off.value = 500
        self.mot2.write_attribute(sim_off)
        sim_off = self.mot2.read_attribute("Offset")
        self.assertEqual(sim_off.value,500.0)
        
#
# Read positions
#

        sim_pos = self.mot2.read_attribute("Position")
        self.assertEqual(sim_pos.value,2020.0)
        
        sim_dial_pos = self.mot2.read_attribute("DialPosition")
        self.assertEqual(sim_dial_pos.value,1520.0)
        
#
# Write a position
#

        sim_pos.value = sim_pos.value + 150.0
        self.mot2.write_attribute(sim_pos)
        
        sim_pos = self.mot2.read_attribute("Position")
        self.assertEqual(sim_pos.value,2170.0)
        
        sim_dial_pos = self.mot2.read_attribute("DialPosition")
        self.assertEqual(sim_dial_pos.value,1670.0)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Pos_limit(self):
        """Motor Position limit and offset/dial"""

#
# We start with min_value and max_value not specified and
# with an offset set to 0
#
       
        attr_info = self.mot2.attribute_query("Position")
        self.assertEqual(attr_info.min_value,"Not specified")
        self.assertEqual(attr_info.max_value,"Not specified")
        
        off = self.mot2.read_attribute("Offset")
        self.assertEqual(off.value,0)
        
#
# Set min_value and max_value
#

        attr_info.min_value = str(1000)
        attr_info.max_value = str(1500)
        self.mot2.set_attribute_config_ex([attr_info])
        
#
# Check them
#

        attr_info = self.mot2.attribute_query("Position")
        self.assertEqual(attr_info.min_value,str(1000))
        self.assertEqual(attr_info.max_value,str(1500))
        
#
# Change the offset
#

        off.value = -1000
        self.mot2.write_attribute(off)
        
#
# Get new limits
#

        attr_info = self.mot2.attribute_query("Position")
        self.assertEqual(attr_info.min_value,str(0))
        self.assertEqual(attr_info.max_value,str(500))
        
#
# Reset the offset
#

        off.value = 0
        self.mot2.write_attribute(off)
        
#
# Check limits
#

        attr_info = self.mot2.attribute_query("Position")
        self.assertEqual(attr_info.min_value,str(1000))
        self.assertEqual(attr_info.max_value,str(1500))
               
#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        sim = PyTango.AttributeValue()
        sim.name = "SimulationMode"
        sim.value = False
        self.pool.write_attribute(sim)
        
        off = PyTango.AttributeValue()
        off.name = "Offset"
        off.value = 0.0  
        self.mot2.write_attribute(off)
        
        attr_info = self.mot2.attribute_query("Position")
        attr_info.min_value = "NaN"
        attr_info.max_value = "NaN"
        self.mot2.set_attribute_config_ex([attr_info])
        
        
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "MotDial usage = MotDial <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,MotDial,dev_name,sys.argv[1],"MotDial_test")
    PoolTestUtil.start_test(runner,MotDial,dev_name,sys.argv[1],"Pos_limit")
    

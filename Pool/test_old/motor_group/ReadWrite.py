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

class ReadWrite(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.admin_name = "dserver/" + ds_full_name
        
        self.ev_group = -1
        self.ev_mot = -1
        self.ev_ano_mot = -1
        self.ev_pos = -1
        
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)
        self.pool.set_timeout_millis(10000)

        if self.pool_configured(self.pool) == False:
            self.empty_pool(self.pool)
            self.create_ctrl_mot(self.pool)
            
        self.admin = PyTango.DeviceProxy(self.admin_name)
        self.admin.set_transparency_reconnection(True)
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.test_mot = PyTango.DeviceProxy("Test_Motor")
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ON)
        
        self.test_mot.command_inout("DefinePosition",1500)
        new_pos = self.test_mot.read_attribute("Position")
        self.assertEqual(new_pos.value,1500)
        
        id_another_mot = self.pool.command_inout("CreateMotor",([3],["Another_Motor","cpp_ctrl"]))
        
        self.another_motor = PyTango.DeviceProxy("Another_Motor")
        self.another_motor.set_transparency_reconnection(True)
        
        self.another_motor.command_inout("DefinePosition",1400)
        ano_pos = self.another_motor.read_attribute("Position")
        self.assertEqual(ano_pos.value,1400)
        
        self.pool.command_inout("CreateMotorGroup",["ReadGrp","Test_motor","Another_motor"])
        self.grp_proxy = PyTango.DeviceProxy("ReadGrp")
        
        self.pool.command_inout("CreateMotorgroup",["ErrorGroup","Test_motor","ErrorRead_motor"])
        self.grp_error_proxy = PyTango.DeviceProxy("ErrorGroup")
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Read_test(self):
        """Testing reading Position on group device"""
        
        self.assertEqual(self.grp_proxy.state(),PyTango.DevState.ON)

#
# Basic read
#
        
        pos = self.grp_proxy.read_attribute("Position")
        self.assertEqual(pos.dim_x,2)
        self.assertEqual(pos.value[0],1500.0)
        self.assertEqual(pos.value[1],1400.0)
        
#
# Read a group with a faulty motor
#

        self.attribute_error(self.grp_error_proxy,"Position","Aaaaaa")
        
#
# Set offset on one motor
#

        off = PyTango.AttributeValue()
        off.name = "Offset"
        off.value = -100
        self.another_motor.write_attribute(off)
        
        off_read = self.another_motor.read_attribute("Offset")
        self.assertEqual(off_read.value,-100)
        
        pos = self.grp_proxy.read_attribute("Position")
        self.assertEqual(pos.dim_x,2)
        self.assertEqual(pos.value[0],1500.0)
        self.assertEqual(pos.value[1],1300.0)
        
#
# Start moving the group
#

        pos.value = [1520.0,1280.0]
        self.grp_proxy.write_attribute(pos)
        
        self.assertEqual(self.grp_proxy.state(),PyTango.DevState.MOVING)
        
        time.sleep(0.1)
        pos = self.grp_proxy.read_attribute("Position")
        self.assertEqual(pos.dim_x,2)
        self.assert_(pos.value[0] > 1500.0 and pos.value[0] < 1520)
        self.assert_(pos.value[1] > 1280.0 and pos.value[1] < 1300)
        self.assertEqual(pos.value[2],1520.0)
        self.assertEqual(pos.value[3],1280.0)
        
        ind_pos = self.test_mot.read_attribute("Position")
        self.assert_(ind_pos.value > 1500.0 and ind_pos.value < 1520)
        ind_pos = self.another_motor.read_attribute("Position")
        self.assert_(ind_pos.value > 1280.0 and ind_pos.value < 1300)

        while self.grp_proxy.state() == PyTango.DevState.MOVING:
            time.sleep(0.2)
        
        self.assertEqual(self.grp_proxy.state(),PyTango.DevState.ON)
        pos1 = self.test_mot.read_attribute("position")
        print "Motor pos =",pos1.value
        new_pos = self.grp_proxy.read_attribute("Position")
        self.assertEqual(new_pos.dim_x,2)
        self.assertEqual(new_pos.value[0],1520)
        self.assertEqual(new_pos.value[1],1280)        
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Write_test(self):
        """Testing writing Position on group device"""


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
                                   
#
# It is an error to write motor group positions with the wrong
# number of position
#

        pos = self.grp_proxy.read_attribute("Position")
        pos.value=[1500]
        self.wr_attribute_error(self.grp_proxy,pos,"Motor_CantMoveGroup")
        
#
# Impossible to move a group if one of the group element is
# already moving
#

        mot_pos = PyTango.AttributeValue()
        mot_pos.name = "Position"
        mot_pos.value = 1480
        self.test_mot.write_attribute(mot_pos)
        
        pos.value=[1520,1400]
        self.wr_attribute_error(self.grp_proxy,pos,"API_AttrNotAllowed")
        
        self.test_mot.command_inout("Abort")
        
#
# subscribe to events (on group and on motors member of the group)
# Sleep a while before subsribing to event to be sure that the motor
# we have just aborted has finished its motion
#

        while self.test_mot.state() == PyTango.DevState.MOVING:
            time.sleep(0.2)

        cb_group = PyCb()
        cb_group.verbose = True
        self.ev_group = self.grp_proxy.subscribe_event("State",PyTango.EventType.CHANGE,cb_group,[])
        
        cb_ano_mot = PyCb()
        cb_ano_mot.verbose = True
        self.ev_ano_mot = self.another_motor.subscribe_event("State",PyTango.EventType.CHANGE,cb_ano_mot,[])
        
        cb_mot = PyCb()
        cb_mot.verbose = True
        self.ev_mot = self.test_mot.subscribe_event("State",PyTango.EventType.CHANGE,cb_mot,[])
        
        cb_pos = Pos_PyCb()
        cb_pos.verbose = True
        self.ev_pos = self.grp_proxy.subscribe_event("Position",PyTango.EventType.CHANGE,cb_pos,[])
        
#
# Move a group
#

        pos.value = [1550,1400]
        self.grp_proxy.write_attribute(pos)
        self.assertEqual(self.grp_proxy.state(),PyTango.DevState.MOVING)  
        
        while self.grp_proxy.state() == PyTango.DevState.MOVING:
            time.sleep(2)
        time.sleep(0.1)
        
#
# Check that everything is OK
#

        self.assertEqual(self.grp_proxy.state(),PyTango.DevState.ON)
        self.assertEqual(self.another_motor.state(),PyTango.DevState.ON)
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ON)
        
        self.assertEqual(cb_group.cb_executed,3)
        self.assertEqual(cb_ano_mot.cb_executed,3)
        self.assertEqual(cb_mot.cb_executed,3)
        self.assert_(cb_pos.cb_executed > 7)
        
#
# Try another movement and an abort command
#

        pos.value = [1560,1300]
        self.grp_proxy.write_attribute(pos)
        self.assertEqual(self.grp_proxy.state(),PyTango.DevState.MOVING)  
 
        time.sleep(0.3)
        self.grp_proxy.command_inout("Abort")

        while self.another_motor.state() == PyTango.DevState.MOVING:
            time.sleep(0.3)
        time.sleep(0.1)
        
#
# Check that everything is OK
#

        self.assertEqual(self.grp_proxy.state(),PyTango.DevState.ON)
        self.assertEqual(self.another_motor.state(),PyTango.DevState.ON)
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ON)
        
        self.assertEqual(cb_group.cb_executed,5)
        self.assertEqual(cb_ano_mot.cb_executed,5)
        self.assertEqual(cb_mot.cb_executed,5)
        
#
# Try another movement and an abort command on one of the motor
#

        pos.value = [1570,1300]
        self.grp_proxy.write_attribute(pos)
        self.assertEqual(self.grp_proxy.state(),PyTango.DevState.MOVING)  
 
        time.sleep(0.5)

        self.another_motor.command_inout("Abort")
        
        while self.grp_proxy.state() == PyTango.DevState.MOVING:
            time.sleep(2)
        time.sleep(0.1)
        
#
# Check that a group motion is aborted if one of the group element hit a limit switch
#

        self.test_mot.command_inout("DefinePosition",1980)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1980.0)
        
        pos.value = [2100,1800]
        self.grp_proxy.write_attribute(pos)
        self.assertEqual(self.grp_proxy.state(),PyTango.DevState.MOVING)

        while self.grp_proxy.state() == PyTango.DevState.MOVING:
            time.sleep(2)
        
#
# In case of, wait for alarm_event to be received (it's another thread
# which execute the callback...)
#

        if cb_group.alarm_eve == False:
            time.sleep(0.1)
            
        self.assertEqual(self.grp_proxy.state(),PyTango.DevState.ALARM)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,2000)
        pos = self.another_motor.read_attribute("Position")
        self.assert_(pos.value < 1450)
        
        
           
#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        self.pool.command_inout("DeleteMotorGroup","ErrorGroup")
        
        while self.grp_proxy.state() == PyTango.DevState.MOVING:
           time.sleep(0.2)
           
        self.pool.command_inout("DeleteMotorGroup","ReadGrp")

        off = PyTango.AttributeValue()
        off.name = "Offset"
        off.value = 0
        while self.another_motor.state() == PyTango.DevState.MOVING:
            time.sleep(0.1)
        self.another_motor.write_attribute(off)
        
        self.pool.command_inout("DeleteMotor","Another_Motor")
 
        time.sleep(0.1)
        if self.ev_group != -1:
            self.grp_proxy.unsubscribe_event(self.ev_group)
        if self.ev_mot != -1:
            self.test_mot.unsubscribe_event(self.ev_mot)
        if self.ev_ano_mot != -1:
            self.another_motor.unsubscribe_event(self.ev_ano_mot)
        if self.ev_pos != -1:
            self.grp_proxy.unsubscribe_event(self.ev_pos)
            
        pos_att = self.test_mot.read_attribute("Position")
        pos_att.value = pos_att.value - 10
        self.test_mot.write_attribute(pos_att)
        
        while self.test_mot.state() == PyTango.DevState.MOVING:
            time.sleep(0.1)
        
        
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "ReadWrite usage = ReadWrite <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,ReadWrite,dev_name,sys.argv[1],"Read_test")
    PoolTestUtil.start_test(runner,ReadWrite,dev_name,sys.argv[1],"Write_test")

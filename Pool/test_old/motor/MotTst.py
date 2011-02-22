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

class Mot(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.ev = -1
        self.ev_pos = -1
        self.ev_limit = -1
        self.ev_pos_simu = -1
        self.ev_state_simu = -1
        
#---------------------------------------------------------------------------------------------------------------------

    def create_ctrl_mot(self):
        self.pool.command_inout("CreateController",["Motor","WaterPapCtrl.py","IcePapController","first"])
        self.pool.command_inout("CreateController",["Motor","DummyCtrl.so","DummyController","cpp_ctrl"])
        
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,2)
        ctrl1_str = "first (WaterPapCtrl.IcePapController/first) - Motor Python ctrl (WaterPapCtrl.py)"
        ctrl2_str = "cpp_ctrl (DummyCtrl.DummyController/cpp_ctrl) - Motor Cpp ctrl (DummyCtrl.so)"
        self.assertEqual(ctrl_list.value[0],ctrl1_str)
        self.assertEqual(ctrl_list.value[1],ctrl2_str)
        
        self.pool.command_inout("CreateMotor",([0],["First_Motor","first"]))
        self.pool.command_inout("CreateMotor",([1],["Test_Motor","cpp_ctrl"]))

        mot_list = self.pool.read_attribute("MotorList")
        self.assertEqual(mot_list.dim_x,2)
        mot1_str = "First_Motor (motor/first/0)"
        mot2_str = "Test_Motor (motor/cpp_ctrl/1)"
        self.assertEqual(mot_list.value[0],mot1_str)
        self.assertEqual(mot_list.value[1],mot2_str)
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        mot1 = PyTango.DeviceProxy("First_Motor")
        self.assertEqual(mot1.state(),PyTango.DevState.ON)
        mot2 = PyTango.DeviceProxy("Test_Motor")
        self.assertEqual(mot2.state(),PyTango.DevState.ON)
        
#
# Set simulated motor limit to reasonable values and send an Init command
# to the simulated motor
#

        mot_limits = {'UpperSwitch':['2000'],'LowerSwitch':["1000"]}
        db = PyTango.Database()
        db.put_device_property("simu/test/mot01",mot_limits)
        simu_mot = PyTango.DeviceProxy("simu/test/mot01")
        simu_mot.command_inout("Init")
        
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)

        try:
            ctrl_list = self.pool.read_attribute("ControllerList")
        except:
            self.create_ctrl_mot()
            ctrl_list = self.pool.read_attribute("ControllerList")
        
        if ctrl_list.dim_x != 2:
            self.empty_pool(self.pool)
            self.create_ctrl_mot()
        else :
            if ctrl_list.value[0].find("IcePapController/first") == -1:
                self.empty_pool(self.pool)
                self.create_ctrl_mot()
            else:
                if ctrl_list.value[1].find("DummyController/cpp_ctrl") == -1:
                    self.empty_pool(self.pool)
                    self.create_ctrl_mot()
                
        mot_list = self.pool.read_attribute("MotorList")
        
        if mot_list.dim_x != 2:
            self.empty_pool(self.pool)
            self.create_ctrl_mot()
        else:
            if mot_list.value[0].find("First_Motor") == -1:
                self.empty_pool(self.pool)
                self.create_ctrl_mot()
            else:
                if mot_list.value[1].find("Test_Motor") == -1:
                    self.empty_pool(self.pool)
                    self.create_ctrl_mot()

        self.test_mot = PyTango.DeviceProxy("Test_Motor")
                
#---------------------------------------------------------------------------------------------------------------------
               
    def Mot_test(self):
        """Acc/Dec/Vel/Base motor attributes"""

#
# For a new motor without any SaveConfig command, the default values are
# acceleration = deceleration = 25, velocity = 200, base_rate = 2
#
         
        acc = self.test_mot.read_attribute("Acceleration")
#        self.assertEqual(acc.value,25.0)
        self.assertEqual(acc.value,0.5)
        
        dec = self.test_mot.read_attribute("Deceleration")
#        self.assertEqual(dec.value,25.0)
        self.assertEqual(dec.value,0.5)
        
        vel = self.test_mot.read_attribute("Velocity")
#        self.assertEqual(vel.value,200.0)
        self.assertEqual(vel.value,10.0)
        
        base = self.test_mot.read_attribute("Base_rate")
        self.assertEqual(base.value,2.0)
        
        sim = self.test_mot.read_attribute("SimulationMode")
        self.assertEqual(sim.value,False)
        
#
# Change these parameters
#

        acc.value = 50.0
        self.test_mot.write_attribute(acc)
        dec.value = 30.0
        self.test_mot.write_attribute(dec)
        vel.value = 180.0
        self.test_mot.write_attribute(vel)
        base.value = 5.0
        self.test_mot.write_attribute(base)
        
#
# Check new values
#

        acc_2 = self.test_mot.read_attribute("Acceleration")
        self.assertEqual(acc_2.value,50.0)
        
        dec_2 = self.test_mot.read_attribute("Deceleration")
        self.assertEqual(dec_2.value,30.0)
        
        vel_2 = self.test_mot.read_attribute("Velocity")
        self.assertEqual(vel_2.value,180.0)
        
        base_2 = self.test_mot.read_attribute("Base_rate")
        self.assertEqual(base_2.value,5.0)
        
#
# Some error cases
#

        acc.value = -10.0
        self.wr_attribute_error(self.test_mot,acc,"Motor_BadArgument")
        
        vel.value = -10.0
        self.wr_attribute_error(self.test_mot,vel,"Motor_BadArgument")
        vel.value = 3.0
        self.wr_attribute_error(self.test_mot,vel,"Motor_BadArgument")
        
        base.value = -10.0
        self.wr_attribute_error(self.test_mot,base,"Motor_BadArgument")
        base.value = 200.0
        self.wr_attribute_error(self.test_mot,base,"Motor_BadArgument")
        
        dec.value = -10.0
        self.wr_attribute_error(self.test_mot,dec,"Motor_BadArgument")

#
# Save these values in db
#

        self.test_mot.command_inout("SaveConfig")
        
#
# Change these parameters and check them once more
#

        acc.value = 100.0
        self.test_mot.write_attribute(acc)
        dec.value = 35.0
        self.test_mot.write_attribute(dec)
        vel.value = 280.0
        self.test_mot.write_attribute(vel)
        base.value = 1.0
        self.test_mot.write_attribute(base)
        
        acc_2 = self.test_mot.read_attribute("Acceleration")
        self.assertEqual(acc_2.value,100.0)
        dec_2 = self.test_mot.read_attribute("Deceleration")
        self.assertEqual(dec_2.value,35.0)
        vel_2 = self.test_mot.read_attribute("Velocity")
        self.assertEqual(vel_2.value,280.0)
        base_2 = self.test_mot.read_attribute("Base_rate")
        self.assertEqual(base_2.value,1.0)

#
# After a SaveConfig, an Init command on the motor, we must retrieve the original values
#

        self.test_mot.command_inout("Init")

        acc = self.test_mot.read_attribute("Acceleration")
        self.assertEqual(acc.value,50.0)
        
        dec = self.test_mot.read_attribute("Deceleration")
        self.assertEqual(dec.value,30.0)
        
        vel = self.test_mot.read_attribute("Velocity")
        self.assertEqual(vel.value,180.0)
        
        base = self.test_mot.read_attribute("Base_rate")
        self.assertEqual(base.value,5.0)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Mot_extra(self):
        """Motor extra attributes"""
                
#
# Check that we have the attributes for the extra attributes for the C++ controller
#

        attr_info = self.test_mot.attribute_query("Aaa")
        self.assertEqual(attr_info.name,"Aaa")
        self.assertEqual(attr_info.writable,PyTango.AttrWriteType.READ)
        self.assertEqual(attr_info.data_format,PyTango.AttrDataFormat.SCALAR)
        self.assertEqual(attr_info.data_type,PyTango.ArgType.DevLong)
        self.assertEqual(attr_info.disp_level,PyTango.DispLevel.EXPERT)
        
        attr_info = self.test_mot.attribute_query("Bbb")
        self.assertEqual(attr_info.name,"Bbb")
        self.assertEqual(attr_info.writable,PyTango.AttrWriteType.READ_WRITE)
        self.assertEqual(attr_info.data_format,PyTango.AttrDataFormat.SCALAR)
        self.assertEqual(attr_info.data_type,PyTango.ArgType.DevDouble)
        self.assertEqual(attr_info.disp_level,PyTango.DispLevel.EXPERT)
        
        attr_info = self.test_mot.attribute_query("Ccc")
        self.assertEqual(attr_info.name,"Ccc")
        self.assertEqual(attr_info.writable,PyTango.AttrWriteType.READ)
        self.assertEqual(attr_info.data_format,PyTango.AttrDataFormat.SCALAR)
        self.assertEqual(attr_info.data_type,PyTango.ArgType.DevString)
        self.assertEqual(attr_info.disp_level,PyTango.DispLevel.EXPERT)
        
#
# The same for the Python controller
#

        py_mot = PyTango.DeviceProxy("motor/first/0")

        attr_info = py_mot.attribute_query("First_extra")
        self.assertEqual(attr_info.name,"First_extra")
        self.assertEqual(attr_info.writable,PyTango.AttrWriteType.READ_WRITE)
        self.assertEqual(attr_info.data_format,PyTango.AttrDataFormat.SCALAR)
        self.assertEqual(attr_info.data_type,PyTango.ArgType.DevDouble)
        self.assertEqual(attr_info.disp_level,PyTango.DispLevel.EXPERT)
        
        attr_info = py_mot.attribute_query("Second_extra")
        self.assertEqual(attr_info.name,"Second_extra")
        self.assertEqual(attr_info.writable,PyTango.AttrWriteType.READ)
        self.assertEqual(attr_info.data_format,PyTango.AttrDataFormat.SCALAR)
        self.assertEqual(attr_info.data_type,PyTango.ArgType.DevLong)
        self.assertEqual(attr_info.disp_level,PyTango.DispLevel.EXPERT)
        
#
# Attributex created for the C++ motors should not exist in the Python's one
# and vice versa
#

        received_except = False
        try:
            py_mot.attribute_query("Aaa")
        except:
            received_except = True
        self.assertEqual(received_except,True)
            
        received_except = False
        try:
            self.test_mot.attribute_query("Second_extra")
        except:
            received_except = True
        self.assertEqual(received_except,True)
                
#
# Read and Write some of these attributes for C++ and Python
#

        bbb_att = self.test_mot.read_attribute("Bbb")
        self.assertEqual(bbb_att.dim_x,1)
        self.assertEqual(bbb_att.value,7.8899)
        
        bbb_att.value = 1.222
        self.test_mot.write_attribute(bbb_att)  
        
        fi_att = py_mot.read_attribute("Second_extra")
        self.assertEqual(fi_att.dim_x,1)
        self.assertEqual(fi_att.value,2233)
       
#---------------------------------------------------------------------------------------------------------------------
               
    def SimuMot_test(self):
        """Acc/Dec/Vel/Base and position motor attributes in simulation mode"""

        class PyCb_Simu:
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
# Subscribe to events
#

        cbs = PyCb_Simu()
        cbs.verbose = True
        cbss = PyCb_Simu()
        cbss.verbose = True
        self.ev_pos_simu = self.test_mot.subscribe_event("Position",PyTango.EventType.CHANGE,cbs,[])
        self.ev_state_simu = self.test_mot.subscribe_event("State",PyTango.EventType.CHANGE,cbss,[])
        
        self.assertEqual(cbs.cb_executed,1)
        self.assertEqual(cbss.cb_executed,1)
                                
#
# Check parameters before doing something
#
         
        acc = self.test_mot.read_attribute("Acceleration")
#        self.assertEqual(acc.value,25.0)
        self.assertEqual(acc.value,0.5)        
        
        dec = self.test_mot.read_attribute("Deceleration")
#        self.assertEqual(dec.value,25.0)
        self.assertEqual(dec.value,0.5)
        
        vel = self.test_mot.read_attribute("Velocity")
#        self.assertEqual(vel.value,200.0)
        self.assertEqual(vel.value,10.0)
        
        base = self.test_mot.read_attribute("Base_rate")
        self.assertEqual(base.value,2.0)
        
        sim = self.test_mot.read_attribute("SimulationMode")
        self.assertEqual(sim.value,False)
        
#
# Change these parameters after setting the simulation mode on the pool device
#

        sim = PyTango.AttributeValue()
        sim.name = "SimulationMode"
        sim.value = True
        self.pool.write_attribute(sim)
        
        acc.value = 50.0
        self.test_mot.write_attribute(acc)
        dec.value = 30.0
        self.test_mot.write_attribute(dec)
        vel.value = 180.0
        self.test_mot.write_attribute(vel)
        base.value = 5.0
        self.test_mot.write_attribute(base)
        
#
# Check new values
#

        acc_2 = self.test_mot.read_attribute("Acceleration")
        self.assertEqual(acc_2.value,50.0)
        
        dec_2 = self.test_mot.read_attribute("Deceleration")
        self.assertEqual(dec_2.value,30.0)
        
        vel_2 = self.test_mot.read_attribute("Velocity")
        self.assertEqual(vel_2.value,180.0)
        
        base_2 = self.test_mot.read_attribute("Base_rate")
        self.assertEqual(base_2.value,5.0)
        
#
# SaveConfig command should be an error
#

        self.wrong_argument(self.test_mot,"SaveConfig",[],"Motor_SimuMode")
        
#
# Change the position and check that we receive the same events
# when the simulation mode is OFF
#

        pos_att = self.test_mot.read_attribute("Position")
        pos_att.value = pos_att.value + 20
        self.test_mot.write_attribute(pos_att)
        
        time.sleep(0.1)
        
        self.assertEqual(cbs.cb_executed,2)
        self.assertEqual(cbss.cb_executed,3)
        
#
# Change the simulation mode to False
#

        sim.value = False
        self.pool.write_attribute(sim)
        
#
# We must retrieve the original values
#

        acc = self.test_mot.read_attribute("Acceleration")
        self.assertEqual(acc.value,0.5)
        
        dec = self.test_mot.read_attribute("Deceleration")
        self.assertEqual(dec.value,0.5)
        
        vel = self.test_mot.read_attribute("Velocity")
        self.assertEqual(vel.value,10.0)
        
        base = self.test_mot.read_attribute("Base_rate")
        self.assertEqual(base.value,2.0)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def MovingMot_test(self):
        """Moving the motor (polling mode) plus upper and lower switches"""


        class PyCb_Limit:
            def __init__(self):
                self.cb_executed = 0
                self.cb_error = 0
                self.verbose = False
                
            def push_event(self,event):
                self.cb_executed += 1
                self.when = time.time()
                if not event.err:
                    if self.verbose == True:
                        print "Event received at",self.when,":",event.attr_name,", value =",event.attr_value.value
                else:
                    self.cb_error += 1
                    if self.verbose == True:
                        print event.errors

#
# Subscribe to event
#

        cbl = PyCb_Limit()
        cbl.verbose = True
        self.ev_limit = self.test_mot.subscribe_event("Limit_Switches",PyTango.EventType.CHANGE,cbl,[])
        
                                 
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ON)
        self.assertEqual(cbl.cb_executed,1)
        
#
# Force position to 1500
#

        self.test_mot.command_inout("DefinePosition",1500)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1500.0)
        
#
# read switches
#

        switches = self.test_mot.read_attribute("Limit_switches")
        self.assertEqual(switches.value[0],False)
        self.assertEqual(switches.value[1],False)
        self.assertEqual(switches.value[2],False)
 
#
# Move motor to 1600
#
        
        pos.value = pos.value + 20.0
        
        self.test_mot.write_attribute(pos)
        self.assertEqual(self.test_mot.state(),PyTango.DevState.MOVING)
        
        while self.test_mot.state() == PyTango.DevState.MOVING:
            time.sleep(2)
            
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ON)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1520.0)
        
#
# Move motor close to upper switch
#

        self.test_mot.command_inout("DefinePosition",1980)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1980.0)
        
#
# Try to go to 2100
#

        pos.value = 2100.0
        
        self.test_mot.write_attribute(pos)
        self.assertEqual(self.test_mot.state(),PyTango.DevState.MOVING)        
        while self.test_mot.state() == PyTango.DevState.MOVING:
            time.sleep(2)
            
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ALARM)
        mot_status = self.test_mot.status()
        self.assertNotEqual(mot_status.find("upper switch"),-1)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,2000.0)
        
        switches = self.test_mot.read_attribute("Limit_switches")
        self.assertEqual(switches.value[0],False)
        self.assertEqual(switches.value[1],True)
        self.assertEqual(switches.value[2],False)

        time.sleep(0.05)
        self.assertEqual(cbl.cb_executed,2)
        
#
# Move motor close to lower switch
#

        pos.value = pos.value - 20.0
        self.test_mot.write_attribute(pos)
        while self.test_mot.state() == PyTango.DevState.MOVING:
            time.sleep(2)
            
        switches = self.test_mot.read_attribute("Limit_switches")
        self.assertEqual(switches.value[0],False)
        self.assertEqual(switches.value[1],False)
        self.assertEqual(switches.value[2],False)
        
        time.sleep(0.05)
        self.assertEqual(cbl.cb_executed,3)
                    
        self.test_mot.command_inout("DefinePosition",1020)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1020.0)
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ON)
        
#
# Try to go to 900
#

        pos.value = 900.0
        
        self.test_mot.write_attribute(pos)
        self.assertEqual(self.test_mot.state(),PyTango.DevState.MOVING)        
        while self.test_mot.state() == PyTango.DevState.MOVING:
            time.sleep(2)
            
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ALARM)
        mot_status = self.test_mot.status()
        self.assertNotEqual(mot_status.find("lower switch"),-1)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1000.0)
        
        switches = self.test_mot.read_attribute("Limit_switches")
        self.assertEqual(switches.value[0],False)
        self.assertEqual(switches.value[1],False)
        self.assertEqual(switches.value[2],True)

        time.sleep(0.05)
        self.assertEqual(cbl.cb_executed,4)

        pos.value = pos.value + 20.0
        self.test_mot.write_attribute(pos)
        while self.test_mot.state() == PyTango.DevState.MOVING:
            time.sleep(2)  
            
        switches = self.test_mot.read_attribute("Limit_switches")
        self.assertEqual(switches.value[0],False)
        self.assertEqual(switches.value[1],False)
        self.assertEqual(switches.value[2],False)
        self.assertEqual(cbl.cb_executed,5)
              
        self.test_mot.command_inout("DefinePosition",1200)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1200.0)
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ON)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def MovingMotEvent_test(self):
        """Moving the motor (event mode on state and position)"""

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
                        
        class PyCbPos:
            def __init__(self):
                self.cb_executed = 0
                self.cb_error = 0
                self.verbose = False
                
            def push_event(self,event):
                self.cb_executed += 1
                if not event.err:
                    self.last_value = event.attr_value.value
                    if self.verbose == True:
                        print "Event received:",event.attr_name,", value =",event.attr_value.value
                else:
                    self.cb_error += 1
                    if self.verbose == True:
                        print event.errors   
 
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ON)
        
#
# subscribe to event
#

        cb = PyCb()
        cb.verbose = True
        self.ev = self.test_mot.subscribe_event("State",PyTango.EventType.CHANGE,cb,[])
        
        cb_pos = PyCbPos()
        cb_pos.verbose = True
        self.ev_pos = self.test_mot.subscribe_event("Position",PyTango.EventType.CHANGE,cb_pos,[])
        
#
# Force position to 1500
#

        self.test_mot.command_inout("DefinePosition",1500)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1500.0)
 
#
# Move motor to 1520
#
        
        pos.value = pos.value + 20.0
        
        self.test_mot.write_attribute(pos)
        self.assertEqual(self.test_mot.state(),PyTango.DevState.MOVING)
        
        while self.test_mot.state() == PyTango.DevState.MOVING:
            time.sleep(2)
        time.sleep(0.1)
            
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ON)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1520.0)
        
        self.assertEqual(cb.cb_executed,3)
        self.assertEqual(cb.cb_error,0)
        
        self.assert_(cb_pos.cb_executed >= 5)
        self.assertEqual(cb_pos.last_value,1520.0)
        
#
# Move motor close to upper switch
#

        self.test_mot.command_inout("DefinePosition",1980)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1980.0)
        
#
# Try to go to 2100
#

        pos.value = 2100.0
        
        self.test_mot.write_attribute(pos)
        self.assertEqual(self.test_mot.state(),PyTango.DevState.MOVING)        
        while self.test_mot.state() == PyTango.DevState.MOVING:
            time.sleep(2)
        time.sleep(0.1)
            
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ALARM)
        mot_status = self.test_mot.status()
        self.assertNotEqual(mot_status.find("upper switch"),-1)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,2000.0)

        time.sleep(0.1)        
        self.assertEqual(cb.cb_executed,5)
        self.assertEqual(cb.cb_error,0)
        self.assert_(cb_pos.cb_executed >= 10)
        self.assertEqual(cb_pos.last_value,2000.0)
        
#
# Move motor close to lower switch
#

        pos.value = pos.value - 20.0
        self.test_mot.write_attribute(pos)
        while self.test_mot.state() == PyTango.DevState.MOVING:
            time.sleep(2)
        time.sleep(0.1)

        self.assertEqual(cb.cb_executed,7)
        self.assertEqual(cb.cb_error,0)
        self.assert_(cb_pos.cb_executed >= 15)
        self.assertEqual(cb_pos.last_value,1980.0)
                            
        self.test_mot.command_inout("DefinePosition",1020)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1020.0)
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ON)
        
#
# Try to go to 900
#

        pos.value = 900.0
        
        self.test_mot.write_attribute(pos)
        self.assertEqual(self.test_mot.state(),PyTango.DevState.MOVING)        
        while self.test_mot.state() == PyTango.DevState.MOVING:
            time.sleep(2)
        time.sleep(0.1)
            
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ALARM)
        mot_status = self.test_mot.status()
        self.assertNotEqual(mot_status.find("lower switch"),-1)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1000.0)
        
        self.assertEqual(cb.cb_executed,9)
        self.assertEqual(cb.cb_error,0)
        self.assert_(cb_pos.cb_executed >= 18)
        self.assertEqual(cb_pos.last_value,1000.0)

#
# Motor back to 1200
#

        pos.value = pos.value + 20.0
        self.test_mot.write_attribute(pos)
        while self.test_mot.state() == PyTango.DevState.MOVING:
            time.sleep(2)
        time.sleep(0.1) 
        self.assert_(cb_pos.cb_executed >= 25)
        self.assertEqual(cb_pos.last_value,1020.0)
               
        self.test_mot.command_inout("DefinePosition",1200)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1200.0)
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ON)
        
        self.assertEqual(cb.cb_executed,11)
        self.assertEqual(cb.cb_error,0)
        
#
# Check a no movement order
#

        self.test_mot.write_attribute(pos)
        time.sleep(0.1)
        
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1200.0)
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ON)
        
        self.assertEqual(cb.cb_executed,13)
        self.assertEqual(cb.cb_error,0)
        
#---------------------------------------------------------------------------------------------------------------------
        
    def MotBacklash_test(self):
        """Motor backlash and read position from Tango cache while moving"""

        self.assertEqual(self.test_mot.state(),PyTango.DevState.ON)
        
#
# Set a backlash to + 20
#

        back = self.test_mot.read_attribute("Backlash")
        self.assertEqual(back.value,0.0)
        
        back.value = 20.0
        self.test_mot.write_attribute(back)
        other_back = self.test_mot.read_attribute("Backlash")
        self.assertEqual(other_back.value,20.0)
        
#
# Set motor pos to 1200
#

        self.test_mot.command_inout("DefinePosition",1200)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1200)

#
# Do a positive movment (backlash should not be applied)
#
        
        max = 1200
        pos.value = 1220
        self.test_mot.write_attribute(pos)
 
        sleep_time = 0.1
        pos_list = []
        while self.test_mot.state() == PyTango.DevState.MOVING:
            tmp_pos = self.test_mot.read_attribute("Position")
            if tmp_pos.value > max:
                max = tmp_pos.value
            if max >= 1210 and len(pos_list) <= 5:
                pos_list.append(tmp_pos.value)
                sleep_time = 0.01
            else:
                sleep_time = 0.1
            time.sleep(sleep_time)
        
        tmp_pos = self.test_mot.read_attribute("Position")
        if tmp_pos.value > max:
            max = tmp_pos.value
        
        print "max = ",max
        self.assert_(max <= 1221)

#
# Compute the number of change in the list of pos
# we stored during the previous move
# The position comes from the Tango cache which is updated
# every 100 mS. This means that we should not have more than
# one change in the list
#

        ref_val = 0
        nb_change = 0
        for one_val in pos_list:
#            print "one_val = ",one_val
            if ref_val == 0:
                ref_val = one_val
            if one_val != ref_val:
                nb_change = nb_change + 1
                ref_val = one_val
                
        self.assert_(nb_change <= 1)
            
#
# Do a negative movment (backlash should be applied)
#
        
        min = 1220
        pos.value = 1200
        self.test_mot.write_attribute(pos)
        
        while self.test_mot.state() == PyTango.DevState.MOVING:
            tmp_pos = self.test_mot.read_attribute("Position")
            if tmp_pos.value < min:
                min = tmp_pos.value
            time.sleep(0.1)
        
        tmp_pos = self.test_mot.read_attribute("Position")
        if tmp_pos.value < min:
            min = tmp_pos.value
        
        print "min = ",min
        self.assert_(min <= 1190)
        
#
# Set the backlash to -20
#

        back.value = -20.0
        self.test_mot.write_attribute(back)
        other_back = self.test_mot.read_attribute("Backlash")
        self.assertEqual(other_back.value,-20.0)
        
#
# Do a negative movment (backlash should not be applied)
#
        
        min = 1200
        pos.value = 1180
        self.test_mot.write_attribute(pos)
        
        while self.test_mot.state() == PyTango.DevState.MOVING:
            tmp_pos = self.test_mot.read_attribute("Position")
            if tmp_pos.value < min:
                min = tmp_pos.value
            time.sleep(0.1)
        
        tmp_pos = self.test_mot.read_attribute("Position")
        if tmp_pos.value < min:
            min = tmp_pos.value
        
        print "min = ",min
        self.assert_(min >= 1180)
        
#
# Do a positive movment (backlash should be applied)
#
        
        max = 1180
        pos.value = 1200
        self.test_mot.write_attribute(pos)
        
        while self.test_mot.state() == PyTango.DevState.MOVING:
            tmp_pos = self.test_mot.read_attribute("Position")
            if tmp_pos.value > max:
                max = tmp_pos.value
            time.sleep(0.1)
        
        tmp_pos = self.test_mot.read_attribute("Position")
        if tmp_pos.value > max:
            max = tmp_pos.value
        
        print "max = ",max
        self.assert_(max >= 1218)
        
#---------------------------------------------------------------------------------------------------------------------
        
    def MotBacklashEvent_test(self):
        """Motor backlash and event"""

        class PyCb:
            def __init__(self,dev):
                self.cb_executed = 0
                self.cb_error = 0
                self.verbose = False
                self.dev = dev
                
            def push_event(self,event):
                self.cb_executed += 1
                if not event.err:
                    pos = self.dev.read_attribute("Position")
                    self.last_value = pos.value
                    if self.verbose == True:
                        print "Event received:",event.attr_name,", value =",event.attr_value.value
                else:
                    self.cb_error += 1
                    if self.verbose == True:
                        print event.errors   
                        
                        
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ON)
        
#
# subscribe to event
#

        cb = PyCb(self.test_mot)
        cb.verbose = True
        self.ev = self.test_mot.subscribe_event("State",PyTango.EventType.CHANGE,cb,[])
        
#
# Set a backlash to + 20
#

        back = self.test_mot.read_attribute("Backlash")
        self.assertEqual(back.value,0.0)
        
        back.value = 20.0
        self.test_mot.write_attribute(back)
        other_back = self.test_mot.read_attribute("Backlash")
        self.assertEqual(other_back.value,20.0)
        
#
# Set motor pos to 1200
#

        self.test_mot.command_inout("DefinePosition",1200)
        pos = self.test_mot.read_attribute("Position")
        self.assertEqual(pos.value,1200)
        
#
# Do a negative movment (backlash should be applied)
# but the ON event must be received only after the backlash is applied
#
        
        pos.value = 1180
        self.test_mot.write_attribute(pos)
        
        while self.test_mot.state() == PyTango.DevState.MOVING:
            time.sleep(2)
        
        self.assertEqual(cb.last_value,1180)
        
#
# Set the backlash to -20
#

        back.value = -20.0
        self.test_mot.write_attribute(back)
        other_back = self.test_mot.read_attribute("Backlash")
        self.assertEqual(other_back.value,-20.0)
        
#
# Do a positive movment (backlash should be applied)
#
        
        pos.value = 1200
        self.test_mot.write_attribute(pos)
        
        while self.test_mot.state() == PyTango.DevState.MOVING:
            time.sleep(2)
        
        self.assertEqual(cb.last_value,1200)
                      
#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        db = PyTango.Database()
        db.delete_device_property("dummycontroller/cpp_ctrl/1",["_Acceleration","_Deceleration","_Velocity","_Base_rate"])
        
        if self.ev != -1:
            self.test_mot.unsubscribe_event(self.ev)
            self.ev = -1
        if self.ev_pos != -1:
            self.test_mot.unsubscribe_event(self.ev_pos)
            self.ev_pos = -1
        if self.ev_limit != -1:
            self.test_mot.unsubscribe_event(self.ev_limit)
            self.ev_limit = -1
        if self.ev_pos_simu != -1:
            self.test_mot.unsubscribe_event(self.ev_pos_simu)
            self.ev_pos_simu = -1
        if self.ev_state_simu != -1:
            self.test_mot.unsubscribe_event(self.ev_state_simu)
            self.ev_state_simu = -1
        
        acc = self.test_mot.read_attribute("Acceleration")
        acc.value = 25.0
        self.test_mot.write_attribute(acc)
        
        dec = self.test_mot.read_attribute("Deceleration")
        dec.value = 25.0
        self.test_mot.write_attribute(dec)
        
        vel = self.test_mot.read_attribute("Velocity")
        vel.value = 200.0
        self.test_mot.write_attribute(vel)
        
        base = self.test_mot.read_attribute("Base_rate")
        base.value = 2.0
        self.test_mot.write_attribute(base) 
        
        back = self.test_mot.read_attribute("Backlash")
        back.value = 0.0
        self.test_mot.write_attribute(back) 
        
        self.test_mot.command_inout("DefinePosition",1500) 
        simu_mot = PyTango.DeviceProxy("Simu/test/mot01")
        simu_mot.command_inout("Init")  
        pos = self.test_mot.read_attribute("Position") 
                
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "MotTst usage = MotTst <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,Mot,dev_name,sys.argv[1],"Mot_test")
    PoolTestUtil.start_test(runner,Mot,dev_name,sys.argv[1],"Mot_extra")
    PoolTestUtil.start_test(runner,Mot,dev_name,sys.argv[1],"SimuMot_test")
    PoolTestUtil.start_test(runner,Mot,dev_name,sys.argv[1],"MovingMot_test")
    PoolTestUtil.start_test(runner,Mot,dev_name,sys.argv[1],"MovingMotEvent_test")
    PoolTestUtil.start_test(runner,Mot,dev_name,sys.argv[1],"MotBacklash_test")
    PoolTestUtil.start_test(runner,Mot,dev_name,sys.argv[1],"MotBacklashEvent_test")
    
               

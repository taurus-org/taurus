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

class ZeroD(PoolTestUtil.TestUtil):
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
# Add a Python ZeroD controller with one EXPChannel
#
            
        self.pool.command_inout("CreateController",["ZeroDExpChannel","ElecMeter.py","ElecMeterController","Py_ZeroD"])
        
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,5)
        self.assertEqual(ctrl_list.value[4],"Py_ZeroD (ElecMeter.ElecMeterController/Py_ZeroD) - ZeroDExpChannel Python ctrl (ElecMeter.py)")

        self.pool.command_inout("CreateExpChannel",([0],["Py_0","Py_ZeroD"]))
        
        ct_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(ct_list.dim_x,4)
        self.assertEqual(ct_list.value[0],"First_CT (expchan/py_vct6/0) Counter/Timer Experiment Channel")
        self.assertEqual(ct_list.value[1],"Second_CT (expchan/py_vct6/1) Counter/Timer Experiment Channel")
        self.assertEqual(ct_list.value[2],"First_ZeroD (expchan/cpp_zerod/0) Zero D Experiment Channel")
        self.assertEqual(ct_list.value[3],"Py_0 (expchan/py_zerod/0) Zero D Experiment Channel")
                     
        self.test_zero = PyTango.DeviceProxy("First_ZeroD")
        self.prop_changed = False
        self.created_chan = False
        self.ev_val = -1
        self.ev_state = -1
                
#---------------------------------------------------------------------------------------------------------------------
               
    def ZeroD_extra(self):
        """Zero D Exp Channel extra attributes"""
                
#
# Check that we have the three extra attributes for the PY controller
#

        attr_info = self.test_zero.attribute_query("CppZeroD_extra_1")
        self.assertEqual(attr_info.name,"CppZeroD_extra_1")
        self.assertEqual(attr_info.writable,PyTango.AttrWriteType.READ)
        self.assertEqual(attr_info.data_format,PyTango.AttrDataFormat.SCALAR)
        self.assertEqual(attr_info.data_type,PyTango.ArgType.DevLong)
        self.assertEqual(attr_info.disp_level,PyTango.DispLevel.EXPERT)
        
        attr_info = self.test_zero.attribute_query("CppZeroD_extra_2")
        self.assertEqual(attr_info.name,"CppZeroD_extra_2")
        self.assertEqual(attr_info.writable,PyTango.AttrWriteType.READ_WRITE)
        self.assertEqual(attr_info.data_format,PyTango.AttrDataFormat.SCALAR)
        self.assertEqual(attr_info.data_type,PyTango.ArgType.DevDouble)
        self.assertEqual(attr_info.disp_level,PyTango.DispLevel.EXPERT)
        
#
# The same for the Py controller
#

        py_zero = PyTango.DeviceProxy("expchan/py_zerod/0")

        attr_info = py_zero.attribute_query("Py0D_extra_1")
        self.assertEqual(attr_info.name,"Py0D_extra_1")
        self.assertEqual(attr_info.writable,PyTango.AttrWriteType.READ_WRITE)
        self.assertEqual(attr_info.data_format,PyTango.AttrDataFormat.SCALAR)
        self.assertEqual(attr_info.data_type,PyTango.ArgType.DevDouble)
        self.assertEqual(attr_info.disp_level,PyTango.DispLevel.EXPERT)
        
        attr_info = py_zero.attribute_query("Py0D_extra_2")
        self.assertEqual(attr_info.name,"Py0D_extra_2")
        self.assertEqual(attr_info.writable,PyTango.AttrWriteType.READ)
        self.assertEqual(attr_info.data_format,PyTango.AttrDataFormat.SCALAR)
        self.assertEqual(attr_info.data_type,PyTango.ArgType.DevLong)
        self.assertEqual(attr_info.disp_level,PyTango.DispLevel.EXPERT)
        
        attr_info = py_zero.attribute_query("Py0D_extra_3")
        self.assertEqual(attr_info.name,"Py0D_extra_3")
        self.assertEqual(attr_info.writable,PyTango.AttrWriteType.READ)
        self.assertEqual(attr_info.data_format,PyTango.AttrDataFormat.SCALAR)
        self.assertEqual(attr_info.data_type,PyTango.ArgType.DevBoolean)
        self.assertEqual(attr_info.disp_level,PyTango.DispLevel.EXPERT)
        
#
# Attribute created for the C++ CT should not exist in the Python's one
# and vice versa
#

        received_except = False
        try:
            test_zero.attribute_query("Py0D_extra_2")
        except:
            received_except = True
        self.assertEqual(received_except,True)
            
        received_except = False
        try:
            self.py_zero.attribute_query("CppZerod_extra_2")
        except:
            received_except = True
        self.assertEqual(received_except,True)
                
#
# Read and Write some of these attributes for CPP controller
#

        a_att = self.test_zero.read_attribute("CppZeroD_extra_1")
        self.assertEqual(a_att.dim_x,1)
        self.assertEqual(a_att.value,1234)
        
        b_att = self.test_zero.read_attribute("CppZeroD_extra_2")
        self.assertEqual(b_att.dim_x,1)
        self.assertEqual(b_att.value,7.8899)
        
        b_att.value = 11.22
        self.test_zero.write_attribute(b_att)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Live_Read(self):
        """Zero D Exp Channel live reading""" 
        
#
# Read a value
#

        val = self.test_zero.read_attribute("Value")
        self.assert_(val.value > 10 and val.value < 11)
 
#
# Set the simulation mode
#
       
        sim = PyTango.AttributeProxy(self.pool,"SimulationMode")
        att_val = PyTango.AttributeValue()
        att_val.name = "SimulationMode"
        att_val.value = True
        sim.write(att_val)
        self.assertEqual(sim.read().value,True)
        
        val = self.test_zero.read_attribute("Value")
        self.assertEqual(val.value,0)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Cum_Read(self):
        """Zero D Exp Channel cumulated reading without Cumulation Time""" 
        
#
# Read a CumulatedValue which must failed until the first acquisition
#

        self.attribute_error(self.test_zero,"CumulatedValue","ZeroDExpChannel_BadController")

#
# Read and Set the Cumulation type attribute to Sum
#

        type = self.test_zero.read_attribute("CumulationType")
        self.assertEqual(type.value,0)
        
        type.value = 1
        self.test_zero.write_attribute(type)
        new_type = self.test_zero.read_attribute("CumulationType")
        self.assertEqual(new_type.value,1)
        
#
# Check CumulatedPointsxxx attributes
#

        points_nb = self.test_zero.read_attribute("CumulatedPointsNumber")
        self.assertEqual(points_nb.value,0)
        err_nb = self.test_zero.read_attribute("CumulatedPointsError")
        self.assertEqual(err_nb.value,0)
        
#
# Start an acquisition
#

        self.test_zero.command_inout("Start")
        time.sleep(0.5)
        life_val = self.test_zero.read_attribute("Value")
        self.assert_(life_val.value > 10 and life_val.value < 11)
        time.sleep(0.5)
        self.test_zero.command_inout("Stop")
        
#
# Read cumulated value, points and error
#

        cum_val = self.test_zero.read_attribute("CumulatedValue")
        print cum_val.value
        self.assert_(cum_val.value > 80)
        err_nb = self.test_zero.read_attribute("CumulatedPointsError")
        self.assertEqual(err_nb.value,0)
        points_nb = self.test_zero.read_attribute("CumulatedPointsNumber")
        self.assert_(points_nb.value == 8 or points_nb.value == 9)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Cum_Read_Time(self):
        """Zero D Exp Channel cumulated reading with Cumulation Time""" 
        
#
# Zero D in sum with cumulation time set to 2 seconds
#

        self._write_attribute(self.test_zero,"CumulationType",1)
        self._write_attribute(self.test_zero,"CumulationTime",2.0)
        
#
# Start acquiring
#

        self.test_zero.command_inout("Start")
        time.sleep(1)
        self.assertEqual(self.test_zero.state(),PyTango.DevState.MOVING)
        time.sleep(1.1)
        
#
# The acquisition should be finished
#

        self.assertEqual(self.test_zero.state(),PyTango.DevState.ON)
        
        cum_val = self.test_zero.read_attribute("CumulatedValue")
        self.assert_(cum_val.value > 150)
        
        life_val = self.test_zero.read_attribute("Value")
        self.assert_(life_val.value > 10 and life_val.value < 11)
        
        err_nb = self.test_zero.read_attribute("CumulatedPointsError")
        self.assertEqual(err_nb.value,0)

# 16 * 102 + 16 * 20 = 1952
        
        points_nb = self.test_zero.read_attribute("CumulatedPointsNumber")
        print points_nb.value
        self.assert_(points_nb.value == 15 or points_nb.value == 16)
        
#
# Change the StopIfNoTime property and Init the device
#

        p_dict = {"StopIfNoTime":["False"]}
        self.test_zero.put_property(p_dict)
        self.prop_changed = True
        self.test_zero.command_inout("Init")
        
        self.test_zero.command_inout("Start")
        time.sleep(2.3)
        
#
# The acquisition should be finished
#

        self.assertEqual(self.test_zero.state(),PyTango.DevState.ON)
        
        cum_val = self.test_zero.read_attribute("CumulatedValue")
        self.assert_(cum_val.value > 160)
        
        err_nb = self.test_zero.read_attribute("CumulatedPointsError")
        self.assertEqual(err_nb.value,0)
        
        points_nb = self.test_zero.read_attribute("CumulatedPointsNumber")
        self.assert_(points_nb.value == 16 or points_nb.value == 17)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Cum_Read_Error(self):
        """Zero D Exp Channel cumulated reading with Error"""
        
#
# First, create the channel which fails
#

        self.pool.command_inout("CreateExpChannel",([1],["Zd_Error","Cpp_ZeroD"]))
        self.created_chan = True
        self.zero_err = PyTango.DeviceProxy("Zd_Error")
        
#
# Set its integration time and type
#

        self._write_attribute(self.zero_err,"CumulationType",1)
        self._write_attribute(self.zero_err,"CumulationTime",2.0)
        
#
# Start an acquisition and wait for its end
#

        self.zero_err.command_inout("Start")

        self.assertEqual(self.zero_err.state(),PyTango.DevState.MOVING)
        time.sleep(1.0)
        self.assertEqual(self.zero_err.state(),PyTango.DevState.MOVING)
        time.sleep(1.2)

#
#
#

        cum_val = self.zero_err.read_attribute("CumulatedValue")
        self.assert_(cum_val.value > 90)

        self.assertEqual(cum_val.quality,PyTango.AttrQuality.ATTR_ALARM)
        err_nb = self.zero_err.read_attribute("CumulatedPointsError")
        self.assert_(err_nb.value == 3 or err_nb.value == 4)
             
        self.assertEqual(self.zero_err.state(),PyTango.DevState.ALARM)       
        
#
# Change the ContinueOnError property and Init the device
#

        p_dict = {"ContinueOnError":["False"]}
        self.zero_err.put_property(p_dict)
        self.prop_changed = True
        self.zero_err.command_inout("Init")
        
#
# Start another acquisition
#

        self.zero_err.command_inout("Start")
        time.sleep(0.6)
        
#
# Device should be in ALARM
#

        err_nb = self.zero_err.read_attribute("CumulatedPointsError")
        self.assertEqual(err_nb.value,1)
        
        cum_val = self.zero_err.read_attribute("CumulatedValue")
        self.assert_(cum_val.value > 30)
        self.assertEqual(self.zero_err.state(),PyTango.DevState.ALARM)
        self.assertEqual(cum_val.quality,PyTango.AttrQuality.ATTR_ALARM)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Cum_Read_Event(self):
        """Zero D Exp Channel cumulated reading with Event""" 
        
        class ZeroCb:
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
                        
        class ZeroValueCb:
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

        cb = ZeroCb()
        cb.verbose = True
        self.ev_state = self.test_zero.subscribe_event("State",PyTango.EventType.CHANGE,cb,[])
        
        cb_val = ZeroValueCb()
        self.ev_val = self.test_zero.subscribe_event("CumulatedValue",PyTango.EventType.CHANGE,cb_val,[])
        cb_val.verbose = True
        
#
# Set its integration time
#

        self._write_attribute(self.test_zero,"CumulationType",1)
        self._write_attribute(self.test_zero,"CumulationTime",2.3)
        
#
# Start an acquisition
#

        self.test_zero.command_inout("Start")
        time.sleep(2.5)
        
#
# Check events number
#

        self.assertEqual(cb.cb_executed,3)
        self.assertEqual(cb_val.cb_executed,5)
        self.assertEqual(self.test_zero.state(),PyTango.DevState.ON)
        
              
#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        self.pool.command_inout("DeleteExpChannel","Py_0")
        self.pool.command_inout("DeleteController","Py_ZeroD")

        self._write_attribute(self.pool,"SimulationMode",False)

        self.test_zero.command_inout("Stop")
        self._write_attribute(self.test_zero,"CumulationType",0)
        
        if self.prop_changed == True:
            p_dict = {"StopIfNoTime":["True"]}
            self.test_zero.put_property(p_dict)
            
        if self.created_chan == True:
            self.zero_err.command_inout("Stop")
            self._write_attribute(self.zero_err,"CumulationType",0)
            
            p_dict = {"ContinueOnError":["True"]}
            self.zero_err.put_property(p_dict)
            
            self.pool.command_inout("DeleteExpChannel","Zd_Error")
            
        if self.ev_val != -1:
            self.test_zero.unsubscribe_event(self.ev_val)
            
        if self.ev_state != -1:
            self.test_zero.unsubscribe_event(self.ev_state)
        
                
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "ZeroTst usage = ZeroTst <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,ZeroD,dev_name,sys.argv[1],"ZeroD_extra")
    PoolTestUtil.start_test(runner,ZeroD,dev_name,sys.argv[1],"Live_Read")
    PoolTestUtil.start_test(runner,ZeroD,dev_name,sys.argv[1],"Cum_Read")
    PoolTestUtil.start_test(runner,ZeroD,dev_name,sys.argv[1],"Cum_Read_Time")
    PoolTestUtil.start_test(runner,ZeroD,dev_name,sys.argv[1],"Cum_Read_Error")
    PoolTestUtil.start_test(runner,ZeroD,dev_name,sys.argv[1],"Cum_Read_Event")
               

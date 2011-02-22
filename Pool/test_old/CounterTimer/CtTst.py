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

class CounterTimer(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.ev = -1
        self.ev_val = -1
        self.ev_abort = -1
        self.ev_val_abort = -1
        self.ev_val_simu = -1
        self.ev_state_simu = -1
        
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)
        
        if self.pool_configured(self.pool) == False:
            self.empty_pool(self.pool)
            self.create_ctrl_mot(self.pool)

#
# Add a CPP CoTi controller with one EXPChannel
#
            
        self.pool.command_inout("CreateController",["CounterTimer","DummyCoTiCtrl.so","DummyCoTiController","Cpp_Vct6"])
        
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,5)
        self.assertEqual(ctrl_list.value[4],"Cpp_Vct6 (DummyCoTiCtrl.DummyCoTiController/Cpp_Vct6) - CounterTimer Cpp ctrl (DummyCoTiCtrl.so)")

        self.pool.command_inout("CreateExpChannel",([0],["Cpp_CT","Cpp_Vct6"]))
        
        ct_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(ct_list.dim_x,4)
        self.assertEqual(ct_list.value[0],"First_CT (expchan/py_vct6/0) Counter/Timer Experiment Channel")
        self.assertEqual(ct_list.value[1],"Second_CT (expchan/py_vct6/1) Counter/Timer Experiment Channel")
        self.assertEqual(ct_list.value[2],"Cpp_CT (expchan/cpp_vct6/0) Counter/Timer Experiment Channel")
        
                
        self.test_ct = PyTango.DeviceProxy("First_CT")
        
#
# Counter is associated to motor Test_Motor (motor/cpp_ctrl/1)
#

        self.assoc_mot = PyTango.DeviceProxy("Test_Motor")
        self.assoc_mot.command_inout("DefinePosition",1500)
        pos = self.assoc_mot.read_attribute("Position")
        self.assertEqual(pos.value,1500.0)
                
#---------------------------------------------------------------------------------------------------------------------
               
    def CT_extra(self):
        """CounterTimer extra attributes"""
                
#
# Check that we have the three extra attributes for the PY controller
#

        attr_info = self.test_ct.attribute_query("PyCT_extra_1")
        self.assertEqual(attr_info.name,"PyCT_extra_1")
        self.assertEqual(attr_info.writable,PyTango.AttrWriteType.READ_WRITE)
        self.assertEqual(attr_info.data_format,PyTango.AttrDataFormat.SCALAR)
        self.assertEqual(attr_info.data_type,PyTango.ArgType.DevDouble)
        self.assertEqual(attr_info.disp_level,PyTango.DispLevel.EXPERT)
        
        attr_info = self.test_ct.attribute_query("PyCT_extra_2")
        self.assertEqual(attr_info.name,"PyCT_extra_2")
        self.assertEqual(attr_info.writable,PyTango.AttrWriteType.READ)
        self.assertEqual(attr_info.data_format,PyTango.AttrDataFormat.SCALAR)
        self.assertEqual(attr_info.data_type,PyTango.ArgType.DevLong)
        self.assertEqual(attr_info.disp_level,PyTango.DispLevel.EXPERT)
        
        attr_info = self.test_ct.attribute_query("PyCT_extra_3")
        self.assertEqual(attr_info.name,"PyCT_extra_3")
        self.assertEqual(attr_info.writable,PyTango.AttrWriteType.READ)
        self.assertEqual(attr_info.data_format,PyTango.AttrDataFormat.SCALAR)
        self.assertEqual(attr_info.data_type,PyTango.ArgType.DevBoolean)
        self.assertEqual(attr_info.disp_level,PyTango.DispLevel.EXPERT)
        
#
# The same for the CPP controller
#

        cpp_ct = PyTango.DeviceProxy("expchan/cpp_vct6/0")

        attr_info = cpp_ct.attribute_query("CppCT_extra_1")
        self.assertEqual(attr_info.name,"CppCT_extra_1")
        self.assertEqual(attr_info.writable,PyTango.AttrWriteType.READ)
        self.assertEqual(attr_info.data_format,PyTango.AttrDataFormat.SCALAR)
        self.assertEqual(attr_info.data_type,PyTango.ArgType.DevLong)
        self.assertEqual(attr_info.disp_level,PyTango.DispLevel.EXPERT)
        
        attr_info = cpp_ct.attribute_query("CppCT_extra_2")
        self.assertEqual(attr_info.name,"CppCT_extra_2")
        self.assertEqual(attr_info.writable,PyTango.AttrWriteType.READ_WRITE)
        self.assertEqual(attr_info.data_format,PyTango.AttrDataFormat.SCALAR)
        self.assertEqual(attr_info.data_type,PyTango.ArgType.DevDouble)
        self.assertEqual(attr_info.disp_level,PyTango.DispLevel.EXPERT)
        
#
# Attribute created for the C++ CT should not exist in the Python's one
# and vice versa
#

        received_except = False
        try:
            test_ct.attribute_query("CppCT_extra_2")
        except:
            received_except = True
        self.assertEqual(received_except,True)
            
        received_except = False
        try:
            self.cpp_ct.attribute_query("PyCT_extra_2")
        except:
            received_except = True
        self.assertEqual(received_except,True)
                
#
# Read and Write some of these attributes for Python controller
#

        a_att = self.test_ct.read_attribute("PyCT_extra_2")
        self.assertEqual(a_att.dim_x,1)
        self.assertEqual(a_att.value,33)

        b_att = self.test_ct.read_attribute("PyCT_extra_1")
        b_att.value = 11.22
        self.test_ct.write_attribute(b_att)
        
        self.assertEqual(b_att.dim_x,1)
        self.assertEqual(b_att.value,11.22)
        
        b_att.value = 88.99
        self.test_ct.write_attribute(b_att)

        b_att = self.test_ct.read_attribute("PyCT_extra_1")
        self.assertEqual(b_att.dim_x,1)
        self.assertEqual(b_att.value,88.99)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Counting_test(self):
        """Start a counter (polling mode)"""
                                 
        self.assertEqual(self.test_ct.state(),PyTango.DevState.ON)

#
# Clear counter value
#

        zero = PyTango.AttributeValue()
        zero.name = "Value"
        zero.value = 0
        self.test_ct.write_attribute(zero)
                
#
# Read value
#

        val = self.test_ct.read_attribute("Value")
        self.assertEqual(val.value,0)
        
#
# Start counting
# Note that the controller we are using for test purposes automatically 
# stops the counter after 2 seconds
#
        
        self.test_ct.command_inout("Start")
        self.assertEqual(self.test_ct.state(),PyTango.DevState.MOVING)
        
        while self.test_ct.state() == PyTango.DevState.MOVING:
            time.sleep(0.2)
            
        self.assertEqual(self.test_ct.state(),PyTango.DevState.ON)
        val = self.test_ct.read_attribute("Value")
        self.assert_(val.value > 195)
        self.assert_(val.value < 205)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def CountingEvent_test(self):
        """Start a Counter (event mode on state and value)"""

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
                        
        class PyCbVal:
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
 
        self.assertEqual(self.test_ct.state(),PyTango.DevState.ON)
        
#
# subscribe to event
#

        cb = PyCb()
        cb.verbose = True
        self.ev = self.test_ct.subscribe_event("State",PyTango.EventType.CHANGE,cb,[])
        
        cb_val = PyCbVal()
        cb_val.verbose = True
        self.ev_val = self.test_ct.subscribe_event("Value",PyTango.EventType.CHANGE,cb_val,[])

#
# Clear counter value
#

        zero = PyTango.AttributeValue()
        zero.name = "Value"
        zero.value = 0
        self.test_ct.write_attribute(zero)
        
#
# Start a counter
#

        val = self.test_ct.read_attribute("Value")
        self.assertEqual(val.value,0)
        
        self.test_ct.command_inout("Start")
        self.assertEqual(self.test_ct.state(),PyTango.DevState.MOVING)
        
        while self.test_ct.state() == PyTango.DevState.MOVING:
            time.sleep(0.2)
        time.sleep(0.1)
            
        self.assertEqual(self.test_ct.state(),PyTango.DevState.ON)
        val = self.test_ct.read_attribute("Value")
        self.assert_(val.value > 195)
        self.assert_(val.value < 205)
        
        self.assertEqual(cb.cb_executed,3)
        self.assertEqual(cb.cb_error,0)
        
        self.assert_(cb_val.cb_executed >= 12)
        self.assert_(cb_val.last_value > 195)
        self.assert_(cb_val.last_value < 205)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def AbortCounting_test(self):
        """Abort a counter (polling mode)"""
                                 
        self.assertEqual(self.test_ct.state(),PyTango.DevState.ON)

#
# Clear counter value
#

        zero = PyTango.AttributeValue()
        zero.name = "Value"
        zero.value = 0
        self.test_ct.write_attribute(zero)
            
#
# Read value
#

        val = self.test_ct.read_attribute("Value")
        self.assertEqual(val.value,0)
        
#
# Start counting
#
        
        self.test_ct.command_inout("Start")
        self.assertEqual(self.test_ct.state(),PyTango.DevState.MOVING)
        
        time.sleep(0.5)
        self.test_ct.command_inout("stop")
        
        self.assertEqual(self.test_ct.state(),PyTango.DevState.ON)
        val = self.test_ct.read_attribute("Value")
        print val.value
        self.assert_(val.value > 35)
        self.assert_(val.value < 60)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def AbortCountingEvent_test(self):
        """Abort a Counter (event mode on state and value)"""

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
                        
        class PyCbVal:
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
 
        self.assertEqual(self.test_ct.state(),PyTango.DevState.ON)
        
#
# subscribe to event
#

        cb = PyCb()
        cb.verbose = True
        self.ev_abort = self.test_ct.subscribe_event("State",PyTango.EventType.CHANGE,cb,[])
        
        cb_val = PyCbVal()
        self.ev_val_abort = self.test_ct.subscribe_event("Value",PyTango.EventType.CHANGE,cb_val,[])

#
# Clear counter value
#

        zero = PyTango.AttributeValue()
        zero.name = "Value"
        zero.value = 0
        self.test_ct.write_attribute(zero)
        
#
# Start a counter
#

        val = self.test_ct.read_attribute("Value")
        self.assertEqual(val.value,0)
        
        self.test_ct.command_inout("Start")
        self.assertEqual(self.test_ct.state(),PyTango.DevState.MOVING)
        
        time.sleep(1)
        self.test_ct.command_inout("Stop")
        time.sleep(0.1)
            
        self.assertEqual(self.test_ct.state(),PyTango.DevState.ON)
        val = self.test_ct.read_attribute("Value")
        self.assert_(val.value > 95)
        self.assert_(val.value < 105)
        
        self.assertEqual(cb.cb_executed,3)
        self.assertEqual(cb.cb_error,0)
        
        self.assert_(cb_val.cb_executed >= 6)
        self.assert_(cb_val.last_value > 95)
        self.assert_(cb_val.last_value < 105)

#---------------------------------------------------------------------------------------------------------------------
               
    def SimuCT_test(self):
        """Counter Value attribute in simulation mode"""

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
        self.ev_val_simu = self.test_ct.subscribe_event("Value",PyTango.EventType.CHANGE,cbs,[])
        self.ev_state_simu = self.test_ct.subscribe_event("State",PyTango.EventType.CHANGE,cbss,[])
        
        self.assertEqual(cbs.cb_executed,1)
        self.assertEqual(cbss.cb_executed,1)
                                      
#
# Set the simulation mode on the pool device
#

        sim = PyTango.AttributeValue()
        sim.name = "SimulationMode"
        sim.value = True
        self.pool.write_attribute(sim)
        
#
# Start counting and check that we receive the same events
# when the simulation mode is OFF
#

        self.test_ct.command_inout("Start")
        
        time.sleep(0.1)
        
        self.assertEqual(cbs.cb_executed,2)
        self.assertEqual(cbss.cb_executed,3)
                      
#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        time.sleep(5)
        self.pool.command_inout("DeleteExpChannel","Cpp_CT")
        self.pool.command_inout("DeleteController","Cpp_Vct6")
        
        if self.ev != -1:
            self.test_ct.unsubscribe_event(self.ev)
            self.ev = -1
        if self.ev_val != -1:
            self.test_ct.unsubscribe_event(self.ev_val)
            self.ev_val = -1
        if self.ev_abort != -1:
            self.test_ct.unsubscribe_event(self.ev_abort)
            self.ev_abort = -1
        if self.ev_val_abort != -1:
            self.test_ct.unsubscribe_event(self.ev_val_abort)
            self.ev_val_abort = -1
        if self.ev_val_simu != -1:
            self.test_ct.unsubscribe_event(self.ev_val_simu)
            self.ev_val_simu = -1
        if self.ev_state_simu != -1:
            self.test_ct.unsubscribe_event(self.ev_state_simu)
            self.ev_state_simu = -1
            
        sim = PyTango.AttributeValue()
        sim.name = "SimulationMode"
        sim.value = False
        self.pool.write_attribute(sim)
                
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "CtTst usage = CtTst <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,CounterTimer,dev_name,sys.argv[1],"CT_extra")
    PoolTestUtil.start_test(runner,CounterTimer,dev_name,sys.argv[1],"Counting_test")
    PoolTestUtil.start_test(runner,CounterTimer,dev_name,sys.argv[1],"CountingEvent_test")
    PoolTestUtil.start_test(runner,CounterTimer,dev_name,sys.argv[1],"AbortCounting_test")
    PoolTestUtil.start_test(runner,CounterTimer,dev_name,sys.argv[1],"AbortCountingEvent_test")
    PoolTestUtil.start_test(runner,CounterTimer,dev_name,sys.argv[1],"SimuCT_test")
               

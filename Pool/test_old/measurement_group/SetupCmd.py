import unittest
import PyTango
import sys
import os
import time
import PoolTestUtil
import posix      

class GeneralEventListener:
    def __init__(self,dev,attr_name):
        self.dev = dev
        self.attr_name = attr_name
        #self.received = 0
        self.value_list = []
        self.shouldbe_list = []
        self.verbose = False
        self.id = dev.subscribe_event(attr_name,PyTango.EventType.CHANGE,self,[])
    
    def push_event(self,event):
        if not event.err:
            if self.verbose == True:
                print "Event received ", event.attr_name, "(",event.attr_value.value,")"
            self.value_list.append(event.attr_value.value)
        else:
            print "EVENT ERROR"
    
    def unsubscribe_event(self):
        self.dev.unsubscribe_event(self.id)
    
#-------------------------------------------------------------------------------------------------------------------
#
#        New test class
#
#-------------------------------------------------------------------------------------------------------------------

class SetupCmd(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.admin_name = "dserver/" + ds_full_name
        
        self.state_listener = None
        self.timer_listener = None
        self.monitor_listener = None
        self.counters_listener = None
        self.it_listener = None
        self.ic_listener = None
        
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
        
        self.test_ct1 = PyTango.DeviceProxy("First_CT")
        self.assertEqual(self.test_ct1.state(),PyTango.DevState.ON)

        self.test_ct2 = PyTango.DeviceProxy("Second_CT")
        self.assertEqual(self.test_ct2.state(),PyTango.DevState.ON)
        
        self.pool.command_inout("CreateController",["CounterTimer","UxTimer.so","UnixTimer","test_unixtimerctrl"])
        self.pool.command_inout("CreateExpChannel",([0],["test_unixtimer","test_unixtimerctrl"]))
        
             
#---------------------------------------------------------------------------------------------------------------------
               
    def SetupGrp_test(self):
        """Setup commands/attributes on MeasurementGroup & Pool devices (with events):
           - State/Status/Timer/Monitor/Integration_time/Integration_count
           - Init
           - ActiveMeasurementGroup"""
        
#
# Create a group
#
        self.pool.command_inout("CreateMeasurementGroup",["test_mntgrp1","test_unixtimer","First_CT","Second_CT"])
        grp_proxy = PyTango.DeviceProxy("test_mntgrp1")
 
#
# Execute state, status and Init
#
        # No timer/monitor defined: Therefore it must be in ALARM
        self.assertEqual(grp_proxy.state(),PyTango.DevState.ALARM)

        grp_status = grp_proxy.status()
        self.assertEqual(grp_status,"The measurement group definition is not correct (No Timer/Monitor defined)")
        
        self.state_listener = GeneralEventListener(grp_proxy,'state')
        self.timer_listener = GeneralEventListener(grp_proxy,'timer')
        self.monitor_listener = GeneralEventListener(grp_proxy,'monitor')
        self.counters_listener = GeneralEventListener(grp_proxy,'counters')
        self.it_listener = GeneralEventListener(grp_proxy,'Integration_time')
        self.ic_listener = GeneralEventListener(grp_proxy,'Integration_count')

        self.state_listener.shouldbe_list.append(PyTango.DevState.ALARM)
        self.timer_listener.shouldbe_list.append('Not Initialized')
        self.monitor_listener.shouldbe_list.append('Not Initialized')
        self.counters_listener.shouldbe_list.append(["test_unixtimer","First_CT","Second_CT"])
        self.it_listener.shouldbe_list.append(0.0)
        self.ic_listener.shouldbe_list.append(0)
        
#
# Define a timer - and make state change from ALARM to ON (and counters change as well)
#
        attr = PyTango.AttributeValue()
        attr.name = "timer"
        attr.value = "test_unixtimer"
        grp_proxy.write_attribute(attr)
        
        self.state_listener.shouldbe_list.append(PyTango.DevState.ON)
        self.timer_listener.shouldbe_list.append('test_unixtimer')
        self.counters_listener.shouldbe_list.append(["First_CT","Second_CT"])
        
        grp_status = grp_proxy.status()
        self.assertEqual(grp_status,"The device is in ON state.")
        
#
# Define a monitor - assert that no unnecessary events for state and counters were received
#
        attr = PyTango.AttributeValue()
        attr.name = "monitor"
        attr.value = "First_CT"
        grp_proxy.write_attribute(attr)

        self.monitor_listener.shouldbe_list.append('First_CT')
        
        grp_status = grp_proxy.status()
        self.assertEqual(grp_status,"The device is in ON state.")

#
# Try to change the integration count with negative value is an error
#
        attr = PyTango.AttributeValue()
        attr.name = "Integration_count"
        attr.value = -103439
        self.wr_attribute_error(grp_proxy,attr,"Pool_InvalidIntegrationCount")
 
#
# Try to change the integration time with negative value is an error
#
        attr = PyTango.AttributeValue()
        attr.name = "Integration_time"
        attr.value = -10.23456
        self.wr_attribute_error(grp_proxy,attr,"Pool_InvalidIntegrationTime")

#
# Change the integration time
#
        attr = PyTango.AttributeValue()
        attr.name = "Integration_time"
        attr.value = 1.23456
        grp_proxy.write_attribute(attr)

        self.it_listener.shouldbe_list.append(1.23456)
        self.ic_listener.shouldbe_list.append(0)
        
#
# Change the integration count
#
        attr = PyTango.AttributeValue()
        attr.name = "Integration_count"
        attr.value = 234567
        grp_proxy.write_attribute(attr)

        self.it_listener.shouldbe_list.append(0.0)
        self.ic_listener.shouldbe_list.append(234567)

#
# Ok, finally check if the events received are correct
#
        # wait just a by to assure all events were properly received
        time.sleep(0.5)
        self.assertEqual(self.state_listener.value_list,self.state_listener.shouldbe_list)
        self.assertEqual(self.timer_listener.value_list,self.timer_listener.shouldbe_list)
        self.assertEqual(self.monitor_listener.value_list,self.monitor_listener.shouldbe_list)
        self.assertEqual(self.counters_listener.value_list,self.counters_listener.shouldbe_list)
        self.assertEqual(self.it_listener.value_list,self.it_listener.shouldbe_list)
        self.assertEqual(self.ic_listener.value_list,self.ic_listener.shouldbe_list)

#
# Test Init commnad
#
        grp_proxy.command_inout("Init")
        
#        self.timer_listener.shouldbe_list.append('Not Initialized')
#        self.monitor_listener.shouldbe_list.append('Not Initialized')
        self.counters_listener.shouldbe_list.append(["test_unixtimer","First_CT","Second_CT"])
        self.it_listener.shouldbe_list.append(0.0)
        self.ic_listener.shouldbe_list.append(0)

#        self.assertEqual(grp_proxy.state(),PyTango.DevState.ALARM)
        self.assertEqual(grp_proxy.state(),PyTango.DevState.ON)
#
# Define a timer 
#
        
        attr = PyTango.AttributeValue()
        attr.name = "timer"
        attr.value = "test_unixtimer"
        grp_proxy.write_attribute(attr)
        
#        self.state_listener.shouldbe_list.append(PyTango.DevState.ON)
#        self.timer_listener.shouldbe_list.append('test_unixtimer')
        self.counters_listener.shouldbe_list.append(["First_CT","Second_CT"])
        
        grp_status = grp_proxy.status()
        self.assertEqual(grp_status,"The device is in ON state.")

#
# Delete a measurement group 
#
        self.pool.command_inout("DeleteMeasurementGroup","test_mntgrp1")
        
#
# Final check if the received events are correct
#
        # wait just a by to assure all events were properly received
        time.sleep(0.5)
        self.assertEqual(self.state_listener.value_list,self.state_listener.shouldbe_list)
        self.assertEqual(self.timer_listener.value_list,self.timer_listener.shouldbe_list)
        self.assertEqual(self.monitor_listener.value_list,self.monitor_listener.shouldbe_list)
#        self.assertEqual(self.counters_listener.value_list,self.counters_listener.shouldbe_list)
#        self.assertEqual(self.it_listener.value_list,self.it_listener.shouldbe_list)
#        self.assertEqual(self.ic_listener.value_list,self.ic_listener.shouldbe_list)

        self.state_listener.unsubscribe_event()
        self.timer_listener.unsubscribe_event()
        self.monitor_listener.unsubscribe_event()
        self.counters_listener.unsubscribe_event()
        self.it_listener.unsubscribe_event()
        self.ic_listener.unsubscribe_event()
        
        self.state_listener = None
        self.timer_listener = None
        self.monitor_listener = None
        self.counters_listener = None
        self.it_listener = None
        self.ic_listener = None
        grp_proxy = None

#---------------------------------------------------------------------------------------------------------------------
               
    def ConfigGrp_test(self):
        """Channel configuration tests"""
 
        c1_proxy = PyTango.DeviceProxy("First_CT")
        c2_proxy = PyTango.DeviceProxy("First_ZeroD")
#
# Make sure all channels have the desired value
#
        c1_extra_attr = c1_proxy.read_attribute("PyCT_extra_1")
        c2_cum_type_attr = c2_proxy.read_attribute("CumulationType")
        
        c1_extra_attr.value = 100.45678
        c1_proxy.write_attribute(c1_extra_attr)
        
        c2_cum_type_attr.value = 1
        c2_proxy.write_attribute(c2_cum_type_attr)
        
#
# Create a group
#
        self.pool.command_inout("CreateMeasurementGroup",["test_mntgrp1","test_unixtimer","First_CT","First_ZeroD"])
        grp_proxy = PyTango.DeviceProxy("test_mntgrp1")
        
        db = PyTango.Database()
        
        attr_props = db.get_device_attribute_property("mntgrp/test/test_mntgrp1",['first_ct_value','first_zerod_value'])
        
        self.assertEqual(float(attr_props['first_ct_value']['pyct_extra_1'][0]),100.45678)
        self.assertEqual(int(attr_props['first_zerod_value']['cumulationtype'][0]),1)
        
#
# Change channels values
#
        c1_extra_attr.value = -999.98765
        c1_proxy.write_attribute(c1_extra_attr)

        # Change this value to 2 when implemented
        c2_cum_type_attr.value = 1
        c2_proxy.write_attribute(c2_cum_type_attr)

#
# Save the new configuration and check it
#
        grp_proxy.command_inout('SaveConfig')

        attr_props = db.get_device_attribute_property("mntgrp/test/test_mntgrp1",['first_ct_value','first_zerod_value'])
        
        self.assertEqual(float(attr_props['first_ct_value']['pyct_extra_1'][0]),-999.98765)
        self.assertEqual(int(attr_props['first_zerod_value']['cumulationtype'][0]),1)


#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        if self.state_listener != None:
            self.state_listener.unsubscribe_event()
            self.state_listener = None

        if self.timer_listener != None:
            self.timer_listener.unsubscribe_event()
            self.timer_listener = None

        if self.monitor_listener != None:
            self.monitor_listener.unsubscribe_event()
            self.monitor_listener = None

        if self.counters_listener != None:
            self.counters_listener.unsubscribe_event()
            self.counters_listener = None

        if self.it_listener != None:
            self.it_listener.unsubscribe_event()
            self.it_listener = None

        if self.ic_listener != None:
            self.ic_listener.unsubscribe_event()
            self.ic_listener = None

        
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "SetupCmd usage = BasicCmd <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,SetupCmd,dev_name,sys.argv[1],"SetupGrp_test")
    #PoolTestUtil.start_test(runner,SetupCmd,dev_name,sys.argv[1],"ConfigGrp_test")

    

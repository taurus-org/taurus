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
        self.last_value = None
        self.shouldbe_list = []
        self.verbose = False
        self.id = dev.subscribe_event(attr_name,PyTango.EventType.CHANGE,self,[])
    
    def push_event(self,event):
        if not event.err:
            if self.verbose == True:
                print "Event received ", event.attr_name, "(",event.attr_value.value,")"
            self.value_list.append(event.attr_value.value)
            self.last_value = event.attr_value.value
        else:
            print "EVENT ERROR"
    
    def unsubscribe_event(self):
        self.dev.unsubscribe_event(self.id)
        
#-------------------------------------------------------------------------------------------------------------------
#
#        New test class
#
#-------------------------------------------------------------------------------------------------------------------

class MgTst(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.admin_name = "dserver/" + ds_full_name
        
        self.ev_group = -1
        self.ev_mot = -1
        self.ev_ano_mot = -1
        self.ev_pos = -1
        
        self.state_listener = None
        self.timer_listener = None
        self.monitor_listener = None
        self.counters_listener = None
        self.it_listener = None
        self.ic_listener = None
        self.c0_value_mg_listener= None
        self.c1_value_mg_listener= None
        self.c2_value_mg_listener= None
        self.ind_ch_state_listener = []
        
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

        zerod_proxy = PyTango.DeviceProxy('First_ZeroD')
        attr = PyTango.AttributeValue()
        attr.name = "CumulationType"
        attr.value = 1
        zerod_proxy.write_attribute(attr)

        self.pool.command_inout("CreateMeasurementGroup",["test_mntgrp1","test_unixtimer","First_CT","Second_CT"])

#---------------------------------------------------------------------------------------------------------------------     
        
    def CountingTimer_test(self):
        """Start command (polling) in timer mode"""
        
        c0_proxy = PyTango.DeviceProxy("test_unixtimer")
        c1_proxy = PyTango.DeviceProxy("First_CT")
        c2_proxy = PyTango.DeviceProxy("Second_CT")
        grp_proxy = PyTango.DeviceProxy("test_mntgrp1")
        
        self.assertEqual(grp_proxy.state(),PyTango.DevState.ALARM)
        
        attr = PyTango.AttributeValue()
        attr.name = "Integration_time"
        attr.value = 1.5
        grp_proxy.write_attribute(attr)
        
        attr.name = "Timer"
        attr.value = "test_unixtimer"
        grp_proxy.write_attribute(attr)
        
        self.assertEqual(grp_proxy.state(),PyTango.DevState.STANDBY)
        
        grp_proxy.command_inout("Start")

        self.assertEqual(grp_proxy.state(),PyTango.DevState.MOVING)
        self.assertEqual(c0_proxy.state(),PyTango.DevState.MOVING)
        self.assertEqual(c1_proxy.state(),PyTango.DevState.MOVING)
        self.assertEqual(c2_proxy.state(),PyTango.DevState.MOVING)
        
        while grp_proxy.state() == PyTango.DevState.MOVING:
            time.sleep(0.2)
        
        self.assertEqual(grp_proxy.state(),PyTango.DevState.ON)
        self.assertEqual(c0_proxy.state(),PyTango.DevState.ON)
        self.assertEqual(c1_proxy.state(),PyTango.DevState.ON)
        self.assertEqual(c2_proxy.state(),PyTango.DevState.ON)
        
        val_c0_mg = grp_proxy.read_attribute("test_unixtimer_value")
        val_c0 = c0_proxy.read_attribute("value")
        self.assert_(val_c0_mg.value >= 1.48)
        self.assert_(val_c0_mg.value <= 1.52)
        self.assertEqual(val_c0_mg.value,val_c0.value)
        
        val_c1_mg = grp_proxy.read_attribute("first_ct_value")
        val_c1 = c1_proxy.read_attribute("value")
        self.assert_(val_c1_mg.value >= 147.0)
        self.assert_(val_c1_mg.value <= 157.0)
        self.assertEqual(val_c1_mg.value,val_c1.value)

        val_c2_mg = grp_proxy.read_attribute("second_ct_value")
        val_c2 = c2_proxy.read_attribute("value")
        self.assert_(val_c2_mg.value >= 180.0)
        self.assert_(val_c2_mg.value <= 195.0)
        self.assertEqual(val_c2_mg.value,val_c2.value)

#---------------------------------------------------------------------------------------------------------------------
               
    def CountingMonitor_test(self):
        """Start command (polling) in monitor mode"""
        pass

#---------------------------------------------------------------------------------------------------------------------
               
    def CountingTimerEvent_test(self):
        """Start command (events on state and value) in timer mode"""
        
        c0_proxy = PyTango.DeviceProxy("test_unixtimer")
        c1_proxy = PyTango.DeviceProxy("First_CT")
        c2_proxy = PyTango.DeviceProxy("Second_CT")
        grp_proxy = PyTango.DeviceProxy("test_mntgrp1")
        
        self.assertEqual(grp_proxy.state(),PyTango.DevState.ALARM)
        
        attr = PyTango.AttributeValue()
        attr.name = "Integration_time"
        attr.value = 1.5
        grp_proxy.write_attribute(attr)
        
        attr.name = "Timer"
        attr.value = "test_unixtimer"
        grp_proxy.write_attribute(attr)
        
        self.state_listener = GeneralEventListener(grp_proxy,'state')
        self.c0_value_mg_listener = GeneralEventListener(grp_proxy,'test_unixtimer_value')
        self.c1_value_mg_listener = GeneralEventListener(grp_proxy,'first_ct_value')
        self.c2_value_mg_listener = GeneralEventListener(grp_proxy,'second_ct_value')
        
        self.state_listener.shouldbe_list.append(PyTango.DevState.STANDBY)
                
        grp_proxy.command_inout("Start")
        
        self.state_listener.shouldbe_list.append(PyTango.DevState.ON)
        self.state_listener.shouldbe_list.append(PyTango.DevState.MOVING)
        
        while grp_proxy.state() == PyTango.DevState.MOVING:
            time.sleep(0.2)

        # wait a little to make sure all events arrived
        time.sleep(0.5)

        self.state_listener.shouldbe_list.append(PyTango.DevState.ON)

        self.assertEqual(self.state_listener.value_list,self.state_listener.shouldbe_list)

        val_c0 = c0_proxy.read_attribute("value")
        val_c1 = c1_proxy.read_attribute("value")
        val_c2 = c2_proxy.read_attribute("value")
        
        self.assert_(self.c0_value_mg_listener.last_value >= 1.48)
        self.assert_(self.c0_value_mg_listener.last_value <= 1.52)
        self.assertEqual(self.c0_value_mg_listener.last_value,val_c0.value)
        
        self.assert_(self.c1_value_mg_listener.last_value >= 147.0)
        self.assert_(self.c1_value_mg_listener.last_value <= 157.0)
        self.assertEqual(self.c1_value_mg_listener.last_value,val_c1.value)
        
        self.assert_(self.c2_value_mg_listener.last_value >= 180.0)
        self.assert_(self.c2_value_mg_listener.last_value <= 195.0)
        self.assertEqual(self.c2_value_mg_listener.last_value,val_c2.value)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def AbortCounting_test(self):
        """Abort acquisition (polling mode)"""
        
        c0_proxy = PyTango.DeviceProxy("test_unixtimer")
        c1_proxy = PyTango.DeviceProxy("First_CT")
        c2_proxy = PyTango.DeviceProxy("Second_CT")
        grp_proxy = PyTango.DeviceProxy("test_mntgrp1")
        
        self.assertEqual(grp_proxy.state(),PyTango.DevState.ALARM)
        
        attr = PyTango.AttributeValue()
        attr.name = "Integration_time"
        attr.value = 1.5
        grp_proxy.write_attribute(attr)
        
        attr.name = "Timer"
        attr.value = "test_unixtimer"
        grp_proxy.write_attribute(attr)
        
        self.assertEqual(grp_proxy.state(),PyTango.DevState.STANDBY)
        
        grp_proxy.command_inout("Start")

        self.assertEqual(grp_proxy.state(),PyTango.DevState.MOVING)
        self.assertEqual(c0_proxy.state(),PyTango.DevState.MOVING)
        self.assertEqual(c1_proxy.state(),PyTango.DevState.MOVING)
        self.assertEqual(c2_proxy.state(),PyTango.DevState.MOVING)
        
        time.sleep(1.0)
        
        grp_proxy.command_inout("Abort")
        
        self.assertEqual(grp_proxy.state(),PyTango.DevState.ON)
        self.assertEqual(c0_proxy.state(),PyTango.DevState.ON)
        self.assertEqual(c1_proxy.state(),PyTango.DevState.ON)
        self.assertEqual(c2_proxy.state(),PyTango.DevState.ON)
        
        # wait a little to make sure all events arrived
        time.sleep(0.5)
        
        val_c0_mg = grp_proxy.read_attribute("test_unixtimer_value")
        val_c0 = c0_proxy.read_attribute("value")
        print val_c0_mg.value
        self.assert_(val_c0_mg.value >= 1.0)
        self.assert_(val_c0_mg.value <= 1.2)
        self.assertEqual(val_c0_mg.value,val_c0.value)

        val_c1_mg = grp_proxy.read_attribute("first_ct_value")
        val_c1 = c1_proxy.read_attribute("value")
        self.assert_(val_c1_mg.value >= 95.0)
        self.assert_(val_c1_mg.value <= 105.0)
        self.assertEqual(val_c1_mg.value,val_c1.value)
        
        val_c2_mg = grp_proxy.read_attribute("second_ct_value")
        val_c2 = c2_proxy.read_attribute("value")
        self.assert_(val_c2_mg.value >= 125.0)
        self.assert_(val_c2_mg.value <= 135.0)
        self.assertEqual(val_c2_mg.value,val_c2.value)        

#---------------------------------------------------------------------------------------------------------------------
               
    def AbortCountingEvent_test(self):
        """Abort acquisition (events on state and channel attributes)"""
        c0_proxy = PyTango.DeviceProxy("test_unixtimer")
        c1_proxy = PyTango.DeviceProxy("First_CT")
        c2_proxy = PyTango.DeviceProxy("Second_CT")
        grp_proxy = PyTango.DeviceProxy("test_mntgrp1")
        
        self.assertEqual(grp_proxy.state(),PyTango.DevState.ALARM)

        self.state_listener = GeneralEventListener(grp_proxy,'state')
        self.c0_value_mg_listener = GeneralEventListener(grp_proxy,'test_unixtimer_value')
        self.c1_value_mg_listener = GeneralEventListener(grp_proxy,'first_ct_value')
        self.c2_value_mg_listener = GeneralEventListener(grp_proxy,'second_ct_value')
        
        self.ind_ch_state_listener.append(GeneralEventListener(c0_proxy,'state'))
        self.ind_ch_state_listener.append(GeneralEventListener(c1_proxy,'state'))
        self.ind_ch_state_listener.append(GeneralEventListener(c2_proxy,'state'))
        
        self.state_listener.shouldbe_list.append(PyTango.DevState.ALARM)
        self.ind_ch_state_listener[0].shouldbe_list.append(PyTango.DevState.ON)
        self.ind_ch_state_listener[1].shouldbe_list.append(PyTango.DevState.ON)
        self.ind_ch_state_listener[2].shouldbe_list.append(PyTango.DevState.ON)
        
        attr = PyTango.AttributeValue()
        attr.name = "Integration_time"
        attr.value = 1.5
        grp_proxy.write_attribute(attr)
        
        attr.name = "Timer"
        attr.value = "test_unixtimer"
        grp_proxy.write_attribute(attr)
        
        self.state_listener.shouldbe_list.append(PyTango.DevState.STANDBY)        
                
        grp_proxy.command_inout("Start")
        
        self.state_listener.shouldbe_list.append(PyTango.DevState.ON)
        self.state_listener.shouldbe_list.append(PyTango.DevState.MOVING)
        self.ind_ch_state_listener[0].shouldbe_list.append(PyTango.DevState.MOVING)
        self.ind_ch_state_listener[1].shouldbe_list.append(PyTango.DevState.MOVING)
        self.ind_ch_state_listener[2].shouldbe_list.append(PyTango.DevState.MOVING)

        time.sleep(1.0)
        
        grp_proxy.command_inout("Abort")

        # wait a little to make sure all events arrived
        time.sleep(0.5)
        
        self.state_listener.shouldbe_list.append(PyTango.DevState.ON)
        self.ind_ch_state_listener[0].shouldbe_list.append(PyTango.DevState.ON)
        self.ind_ch_state_listener[1].shouldbe_list.append(PyTango.DevState.ON)
        self.ind_ch_state_listener[2].shouldbe_list.append(PyTango.DevState.ON)
        
        val_c0 = c0_proxy.read_attribute("value")
        self.assert_(self.c0_value_mg_listener.last_value >= 1.0)
        self.assert_(self.c0_value_mg_listener.last_value <= 1.2)
        self.assertEqual(self.c0_value_mg_listener.last_value,val_c0.value)

        val_c1 = c1_proxy.read_attribute("value")
        self.assert_(self.c1_value_mg_listener.last_value >= 95.0)
        self.assert_(self.c1_value_mg_listener.last_value <= 105.0)
        self.assertEqual(self.c1_value_mg_listener.last_value,val_c1.value)
        
        val_c2 = c2_proxy.read_attribute("value")
        self.assert_(self.c2_value_mg_listener.last_value >= 125.0)
        self.assert_(self.c2_value_mg_listener.last_value <= 135.0)
        self.assertEqual(self.c2_value_mg_listener.last_value,val_c2.value)
        
        
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

        if self.c0_value_mg_listener != None:
            self.c0_value_mg_listener.unsubscribe_event()
            self.c0_value_mg_listener = None

        if self.c1_value_mg_listener != None:
            self.c1_value_mg_listener.unsubscribe_event()
            self.c1_value_mg_listener = None

        if self.c2_value_mg_listener != None:
            self.c2_value_mg_listener.unsubscribe_event()
            self.c2_value_mg_listener = None
        
        for ch_listener in self.ind_ch_state_listener:
            ch_listener.unsubscribe_event()
        self.ind_ch_state_listener = None
        
        try:
            grp_proxy = PyTango.DeviceProxy("test_mntgrp1")
            grp_proxy.command_inout("Abort")
            #self.pool.command_inout("DeleteMeasurementGroup","test_mntgrp1")
            self.pool.command_inout("DeleteExpChannel","test_unixtimer")
            self.pool.command_inout("DeleteController","test_unixtimerctrl")
        except Exception, e:
            pass
        
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "MgTst usage = ReadWrite <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,MgTst,dev_name,sys.argv[1],"CountingTimer_test")
    PoolTestUtil.start_test(runner,MgTst,dev_name,sys.argv[1],"CountingTimerEvent_test")
    PoolTestUtil.start_test(runner,MgTst,dev_name,sys.argv[1],"AbortCounting_test")
    PoolTestUtil.start_test(runner,MgTst,dev_name,sys.argv[1],"AbortCountingEvent_test")
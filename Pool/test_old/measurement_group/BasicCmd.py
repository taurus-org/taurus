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
        self.received = 0
        self.last_value = None
        self.verbose = False
        self.id = dev.subscribe_event(attr_name,PyTango.EventType.CHANGE,self,[])
    
    def push_event(self,event):
        if not event.err:
            if self.verbose == True:
                print "Event received ", event.attr_name, "(",event.attr_value.value,")"
            self.last_value = event.attr_value.value
            self.received = self.received + 1
        else:
            print "EVENT ERROR"
    
    def unsubscribe_event(self):
        self.dev.unsubscribe_event(self.id)
    
#-------------------------------------------------------------------------------------------------------------------
#
#        New test class
#
#-------------------------------------------------------------------------------------------------------------------

class BasicCmd(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.admin_name = "dserver/" + ds_full_name
        
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
               
    def BasicCmd_test(self):
        """Basic commands/attribute for MeasurementGroup (Create/Delete/Info)"""
        
#
# Create Measurement Group command with bad arguments
#
        self.wrong_argument(self.pool,"CreateMeasurementGroup",["MyGrp"],"Pool_BadArgument")
        self.wrong_argument(self.pool,"CreateMeasurementGroup",["MyGrp","test_unixtimer","First_CT","Error_channel"],"Pool_BadArgument")

        self.pool.command_inout("CreateMeasurementGroup",["test_mntgrp1","test_unixtimer","First_CT","Second_CT"])
        self.pool.command_inout("CreateMeasurementGroup",["test_mntgrp2","test_unixtimer","First_CT","First_ZeroD","Second_CT"])

        test_mntgrp1 = PyTango.DeviceProxy("test_mntgrp1")
        self.assertEqual(test_mntgrp1.state(),PyTango.DevState.ALARM)
        
        test_mntgrp2 = PyTango.DeviceProxy("test_mntgrp2")
        self.assertEqual(test_mntgrp2.state(),PyTango.DevState.ALARM)
        
#
# Configuration checks
#
        self.assertEqual(test_mntgrp1.read_attribute("Integration_time").value,0.0)
        self.assertEqual(test_mntgrp1.read_attribute("Integration_count").value,0)
        self.assertEqual(test_mntgrp1.read_attribute("Timer").value,"Not Initialized")
        self.assertEqual(test_mntgrp1.read_attribute("Monitor").value,"Not Initialized")
        self.assertEqual(test_mntgrp1.read_attribute("Counters").value,["test_unixtimer","First_CT","Second_CT"])
        self.check_empty_attribute(test_mntgrp1,"ZeroDExpChannels")
        self.check_empty_attribute(test_mntgrp1,"OneDExpChannels")
        self.check_empty_attribute(test_mntgrp1,"TwoDExpChannels")
        
        self.assertEqual(test_mntgrp2.read_attribute("Integration_time").value,0.0)
        self.assertEqual(test_mntgrp2.read_attribute("Integration_count").value,0)
        self.assertEqual(test_mntgrp2.read_attribute("Timer").value,"Not Initialized")
        self.assertEqual(test_mntgrp2.read_attribute("Monitor").value,"Not Initialized")
        self.assertEqual(test_mntgrp2.read_attribute("Counters").value,["test_unixtimer","First_CT","Second_CT"])
        self.assertEqual(test_mntgrp2.read_attribute("ZeroDExpChannels").value,["First_ZeroD"])
        self.check_empty_attribute(test_mntgrp1,"OneDExpChannels")
        self.check_empty_attribute(test_mntgrp1,"TwoDExpChannels")

#
# Try to create a measurement group with the same name as an existing mnt grp is an error
#
        self.wrong_argument(self.pool,"CreateMeasurementGroup",["test_mntgrp1","test_unixtimer","First_CT"],"Pool_WrongMeasurementGroupName")

#
# Try to create a measurement group with the same elements as an existing mnt grp is NOT an error
#
        self.pool.command_inout("CreateMeasurementGroup",["same_mntgrp","test_unixtimer","First_CT","Second_CT"])
        
        mgl = self.pool.read_attribute("MeasurementGroupList")
        self.assertEqual(mgl.dim_x,3)
        
        self.pool.command_inout("DeleteMeasurementGroup","same_mntgrp")

        mgl = self.pool.read_attribute("MeasurementGroupList")
        self.assertEqual(mgl.dim_x,2)

#
# Try to create a measurement group with several times the same element is an error
#
        self.wrong_argument(self.pool,"CreateMeasurementGroup",["my_mntgrp","test_unixtimer","First_CT","test_unixtimer"],"Pool_WrongMeasurementGroup")
        
#
# Check MeasurementGroupList attribute
#
        mgl = self.pool.read_attribute("MeasurementGroupList")
        self.assertEqual(mgl.dim_x,2)

        grp_1_str = "test_mntgrp1 (mntgrp/test/test_mntgrp1) Channel list: test_unixtimer, First_CT, Second_CT"
        grp_2_str = "test_mntgrp2 (mntgrp/test/test_mntgrp2) Channel list: test_unixtimer, First_CT, Second_CT, First_ZeroD"
        self.assertEqual(mgl.value[0],grp_1_str)
        self.assertEqual(mgl.value[1],grp_2_str)

#
# Try to delete an inexisting measurement group is an error
#
        self.wrong_argument(self.pool,"DeleteMeasurementGroup","AaAa","Pool_MeasurementGroupNotFound")

#
# Try to delete a channel that belongs to a measurement group is an error
#
        self.wrong_argument(self.pool,"DeleteExpChannel","test_unixtimer","Pool_CantDeleteChannel")
        self.wrong_argument(self.pool,"DeleteExpChannel","First_CT","Pool_CantDeleteChannel")
        self.wrong_argument(self.pool,"DeleteExpChannel","Second_CT","Pool_CantDeleteChannel")
        self.wrong_argument(self.pool,"DeleteExpChannel","First_ZeroD","Pool_CantDeleteChannel")

#
# Delete a measurement group
#
        self.pool.command_inout("DeleteMeasurementGroup","test_mntgrp1")
        
        mgl = self.pool.read_attribute("MeasurementGroupList")
        self.assertEqual(mgl.dim_x,1)

        grp_1_str = "test_mntgrp2 (mntgrp/test/test_mntgrp2) Channel list: test_unixtimer, First_CT, Second_CT, First_ZeroD"
        self.assertEqual(mgl.value[0],grp_1_str)
        
#
# Delete a measurement group
#
        self.pool.command_inout("DeleteMeasurementGroup","test_mntgrp2")
        
        self.check_empty_attribute(self.pool,"MeasurementGroupList")

#---------------------------------------------------------------------------------------------------------------------
               
    def BasicCmd_AddRemove_test(self):
        """Add/Remove Exp channel commands for MeasurementGroup"""

        self.pool.command_inout("CreateMeasurementGroup",["test_mntgrp1","test_unixtimer","First_CT",])

        mgl = self.pool.read_attribute("MeasurementGroupList")
        self.assertEqual(mgl.dim_x,1)

        grp_1_str = "test_mntgrp1 (mntgrp/test/test_mntgrp1) Channel list: test_unixtimer, First_CT"
        self.assertEqual(mgl.value[0],grp_1_str)

        
        grp_proxy = PyTango.DeviceProxy("test_mntgrp1")

#
# Try to add an inexisting channel to the measurement group
#
        self.wrong_argument(grp_proxy,"AddExpChannel","inexisting_channel","Pool_ExpChannelNotFound")
        
#
# Try to add a channel that already belongs to the measurement group
#
        self.wrong_argument(grp_proxy,"AddExpChannel","test_unixtimer","MeasurementGroup_BadArgument")

#
# Add a new channel to the group
#
        grp_proxy.command_inout("AddExpChannel","Second_CT")
        
        mgl = self.pool.read_attribute("MeasurementGroupList")
        self.assertEqual(mgl.dim_x,1)

        grp_1_str = "test_mntgrp1 (mntgrp/test/test_mntgrp1) Channel list: test_unixtimer, First_CT, Second_CT"
        self.assertEqual(mgl.value[0],grp_1_str)

        db = PyTango.Database()
        props = db.get_device_property(grp_proxy.name(),["Ct_List"])
        self.assertEqual(props["Ct_List"],["test_unixtimer","First_CT","Second_CT"])
        
        attr_info_lst = grp_proxy.get_attribute_config_ex(["second_ct_value"])
        
        self.assertEqual(attr_info_lst[0].name,"second_ct_value")
        self.assertEqual(attr_info_lst[0].data_type,PyTango.DevDouble)
        self.assertEqual(attr_info_lst[0].data_format,PyTango.SCALAR)
        
#
# Try to remove an inexisting channel from the measurement group
#
        self.wrong_argument(grp_proxy,"RemoveExpChannel","inexisting_channel","Pool_ExpChannelNotFound")

#
# Try to remove a channel that does not belong to the measurement group
#
        self.wrong_argument(grp_proxy,"RemoveExpChannel","First_ZeroD","MeasurementGroup_BadArgument")
        
#
# Delete a channel
#        
        grp_proxy.command_inout("RemoveExpChannel","test_unixtimer")
        
        mgl = self.pool.read_attribute("MeasurementGroupList")
        self.assertEqual(mgl.dim_x,1)

        grp_1_str = "test_mntgrp1 (mntgrp/test/test_mntgrp1) Channel list: First_CT, Second_CT"
        self.assertEqual(mgl.value[0],grp_1_str)

#---------------------------------------------------------------------------------------------------------------------
               
    def BasicGrp_test(self):
        """Basic commands/attribute on MeasurementGroup device (Init/State/Status)"""
        
#
# Create a group
#

        self.pool.command_inout("CreateMeasurementGroup",["test_mntgrp1","test_unixtimer","First_CT","Second_CT"])
        grp_proxy = PyTango.DeviceProxy("test_mntgrp1")
        
#
# Execute state, status and Init
#

        self.assertEqual(grp_proxy.state(),PyTango.DevState.ALARM)
        grp_status = grp_proxy.status()
        self.assertEqual(grp_status,"The measurement group definition is not correct (No Timer/Monitor defined)")
        
#
# Define a timer
#
        attr = PyTango.AttributeValue()
        attr.name = "timer"
        attr.value = "test_unixtimer"
        grp_proxy.write_attribute(attr)
        
        self.assertEqual(grp_proxy.state(),PyTango.DevState.ON)
        grp_status = grp_proxy.status()
        self.assertEqual(grp_status,"The device is in ON state.")
        
#
# Undefine a timer
#
        attr = PyTango.AttributeValue()
        attr.name = "timer"
        attr.value = "Not Initialized"
        grp_proxy.write_attribute(attr)
        
        self.assertEqual(grp_proxy.state(),PyTango.DevState.ALARM)
        grp_status = grp_proxy.status()
        self.assertEqual(grp_status,"The measurement group definition is not correct (No Timer/Monitor defined)")
        
#
# Define a monitor
#
        attr = PyTango.AttributeValue()
        attr.name = "timer"
        attr.value = "test_unixtimer"
        grp_proxy.write_attribute(attr)
        
        self.assertEqual(grp_proxy.state(),PyTango.DevState.ON)
        grp_status = grp_proxy.status()
        self.assertEqual(grp_status,"The device is in ON state.")
             
        grp_proxy.command_inout("Init")
#        self.assertEqual(grp_proxy.state(),PyTango.DevState.ALARM)
        self.assertEqual(grp_proxy.state(),PyTango.DevState.ON)
              
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
        print "BasicCmd usage = BasicCmd <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,BasicCmd,dev_name,sys.argv[1],"BasicCmd_test")
    PoolTestUtil.start_test(runner,BasicCmd,dev_name,sys.argv[1],"BasicCmd_AddRemove_test")
    PoolTestUtil.start_test(runner,BasicCmd,dev_name,sys.argv[1],"BasicGrp_test")
    
    

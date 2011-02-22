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

class EventProp(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.pool = PyTango.DeviceProxy(self.dev_name)
        
        self.ev_first_group = -1
        self.ev_second_group = -1
        self.ev_mot = -1
        
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)

        if self.pool_configured(self.pool) == False:
            self.empty_pool(self.pool)
            self.create_ctrl_mot(self.pool)
            
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        
        self.pool.command_inout("CreateMotor",([3],["Another_Motor","cpp_ctrl"]))
        self.mot = PyTango.DeviceProxy("Another_Motor")
        self.assertEqual(self.mot.state(),PyTango.DevState.ON)
        
        self.pool.command_inout("CreateMotorGroup",["FirstMotGrp","Test_motor","Another_motor"])
        self.first_grp_proxy = PyTango.DeviceProxy("FirstMotGrp")
        
        self.pool.command_inout("CreateMotorgroup",["SecondMotGrp","FirstMotGrp","Test_Motor2"])
        self.second_grp_proxy = PyTango.DeviceProxy("SecondMotGrp")
        
        self.simu_ctrl_admin = PyTango.DeviceProxy("dserver/SimuMotorCtrl/test")
        
#---------------------------------------------------------------------------------------------------------------------
               
    def Event_propagation(self):
        """Testing some event propagation cases (from ghost witout motion)"""

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
                    self.last_state = event.attr_value.value
                else:
                    self.cb_error += 1
                    if self.verbose == True:
                        print event.errors
        
#
# subscribe to events (on one motor and on the two groups)
#

        cb_mot = PyCb()
        cb_mot.verbose = True
        self.ev_mot = self.mot.subscribe_event("State",PyTango.EventType.CHANGE,cb_mot,[])
        
        cb_group = PyCb()
        cb_group.verbose = True
        self.ev_first_group = self.first_grp_proxy.subscribe_event("State",PyTango.EventType.CHANGE,cb_group,[])
              
        cb_sec_group = PyCb()
        cb_sec_group.verbose = True
        self.ev_mot = self.second_grp_proxy.subscribe_event("State",PyTango.EventType.CHANGE,cb_sec_group,[])
        
        self.assertEqual(cb_mot.cb_executed,1)
        self.assertEqual(cb_group.cb_executed,1)
        self.assertEqual(cb_sec_group.cb_executed,1)

#
# Kill the motor simulator device server and wat at least 7 seconds to allow the ghost group
# to notice this
#

        self.simu_ctrl_admin.command_inout("Kill")
        time.sleep(7)

        self.assertEqual(cb_mot.cb_executed,2)
        self.assertEqual(cb_group.cb_executed,2)
        self.assertEqual(cb_sec_group.cb_executed,2)
        
        self.assertEqual(cb_mot.cb_error,0)
        self.assertEqual(cb_mot.last_state,PyTango.DevState.UNKNOWN)
        
        self.assertEqual(cb_group.cb_error,0)
        self.assertEqual(cb_group.last_state,PyTango.DevState.UNKNOWN)
        
        self.assertEqual(cb_sec_group.cb_error,0)
        self.assertEqual(cb_sec_group.last_state,PyTango.DevState.UNKNOWN)
                        
        print "Start the MOTOR SIMULATOR device server and HIT A KEY WHEN DONE",
        c = sys.stdin.read(1)
        
        time.sleep(7)
        
        self.assertEqual(cb_mot.cb_executed,3)
        self.assertEqual(cb_group.cb_executed,3)
        self.assertEqual(cb_sec_group.cb_executed,3)
        
        self.assertEqual(cb_mot.cb_error,0)
        self.assertEqual(cb_mot.last_state,PyTango.DevState.ON)
        
        self.assertEqual(cb_group.cb_error,0)
        self.assertEqual(cb_group.last_state,PyTango.DevState.ON)
        
        self.assertEqual(cb_sec_group.cb_error,0)
        self.assertEqual(cb_sec_group.last_state,PyTango.DevState.ON)
           
#---------------------------------------------------------------------------------------------------------------------
               
    def Event_propagation_state(self):
        """Testing some event propagation cases (from state command witout motion)"""

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
                    self.last_state = event.attr_value.value
                else:
                    self.cb_error += 1
                    if self.verbose == True:
                        print event.errors
        
#
# subscribe to events (on the two groups)
#
        
        cb_group = PyCb()
        cb_group.verbose = True
        self.ev_first_group = self.first_grp_proxy.subscribe_event("State",PyTango.EventType.CHANGE,cb_group,[])
              
        cb_sec_group = PyCb()
        cb_sec_group.verbose = True
        self.ev_mot = self.second_grp_proxy.subscribe_event("State",PyTango.EventType.CHANGE,cb_sec_group,[])
        
        self.assertEqual(cb_group.cb_executed,1)
        self.assertEqual(cb_sec_group.cb_executed,1)

#
# Kill the motor simulator device server
#

        self.simu_ctrl_admin.command_inout("Kill")
        time.sleep(.1)
        
#
# Get motor state
#

        self.assertEqual(self.mot.state(),PyTango.DevState.UNKNOWN)
        
#
# Wait for .3 sec and check groups state
#

        time.sleep(0.3)
 
        self.assertEqual(cb_group.last_state,PyTango.DevState.UNKNOWN)
        self.assertEqual(cb_group.cb_executed,2)
        self.assertEqual(cb_sec_group.cb_executed,2)
        
#
# Restart simulator
#

        print "Start the MOTOR SIMULATOR device server and HIT A KEY WHEN DONE",
        c = sys.stdin.read(1)
              
#---------------------------------------------------------------------------------------------------------------------


    def tearDown(self):
        self.pool.command_inout("DeleteMotorGroup","SecondMotGrp")
        self.pool.command_inout("DeleteMotorGroup","FirstMotGrp")
           
        self.pool.command_inout("DeleteMotor","Another_Motor")
        
        if self.ev_mot != -1:
            self.mot.unsubscribe_event(self.ev_mot)
        if self.ev_first_group != -1:
            self.first_grp_proxy.unsubscribe_event(self.ev_first_group)
        if self.ev_second_group != -1:
            self.second_grp_proxy.unsubscribe_event(self.ev_second_group)
                 
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "ev_prop usage = ev_prop <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,EventProp,dev_name,sys.argv[1],"Event_propagation")
    PoolTestUtil.start_test(runner,EventProp,dev_name,sys.argv[1],"Event_propagation_state")
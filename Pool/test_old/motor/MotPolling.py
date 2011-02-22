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

class MotPolling(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.admin_name = "dserver/" + ds_full_name
        spl = ds_full_name.split('/')
        self.ds_inst_name = spl[1]
                
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.admin = PyTango.DeviceProxy(self.admin_name)

        if self.pool_configured(self.pool) == False:
            self.empty_pool(self.pool)
            self.create_ctrl_mot(self.pool)
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.polled_dev_name = "mg/" + self.ds_inst_name + "/ghost"
        
#---------------------------------------------------------------------------------------------------------------------
               
    def MotPolling_test(self):
        """Motor polling from the ghost group"""
        
#
# Get polled device list
#

        polled_dev = self.admin.command_inout("PolledDevice")
        # one for motor group and another for measurement group
        self.assertEqual(len(polled_dev),2) 
        self.assertEqual(polled_dev[0],self.polled_dev_name)
        
#
# Get polling status
#

        poll_status = self.admin.command_inout("DevPollStatus",polled_dev[0])
        p_status_lines = poll_status[0].splitlines()
        self.assertEqual(p_status_lines[0],"Polled command name = State")
        self.assertEqual(p_status_lines[1],"Polling period (mS) = 5000")
        self.assertEqual(p_status_lines[2],"Polling ring buffer depth = 10")
        s_list = p_status_lines[4].split(' ')
        if s_list[5] != 'mS':
            self.assert_(int(s_list[4]) < 5)
                       
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
        print "MotPolling usage = MotPolling <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,MotPolling,dev_name,sys.argv[1],"MotPolling_test")
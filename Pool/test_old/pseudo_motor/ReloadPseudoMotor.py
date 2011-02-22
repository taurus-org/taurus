import unittest
#import unittestgui
import PyTango
import sys
import os
import time
import user
import PoolTestUtil

class TestPool(PoolTestUtil.TestUtil):
    
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.__testMethodName = methodName
        self.dev_name = dev_name
        self.ds_full_name = ds_full_name
        self.ds_exec,self.ds_inst = self.ds_full_name.split('/')
        self.start_ds_str = self.ds_exec + " " + self.ds_inst + " 1> /dev/null  2>&1 &"
        self.admin_dev = "dserver/" + self.ds_full_name
        
        self.bdir = PoolTestUtil.GetBasePath()
        self.pydir = self.bdir + "/test/pseudo_motor/test_pm"

#---------------------------------------------------------------------------------------------------------------------

    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)
# VALGRIND        self.pool.set_timeout_millis(10000)

        os.system('/bin/cp %s/PseudoLib.py.original %s/PseudoLib.py' % (self.pydir,self.pydir))
        
        if self.pool_configured(self.pool) == False:
            self.empty_pool(self.pool)
            self.create_ctrl_mot(self.pool)

#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        os.system('/bin/cp %s/PseudoLib.py.original %s/PseudoLib.py' % (self.pydir,self.pydir))


    def ReloadEmptyPseudoMotorCode(self):
        """Checking reload of Pseudo Motor python module after pseudo motors have been deleted"""
  
#
# Check that everything is as expected
#      
        pseudo_info = self.pool.command_inout("GetPseudoMotorInfo",["PseudoLib.py","Slit"])
        self.assertEqual(pseudo_info[0],"A Slit pseudo motor system for controlling gap and offset pseudo motors.")
        self.assertEqual(pseudo_info[1],"2") # number of physical motors
        self.assertEqual(pseudo_info[2],"sl2t") # sl2t physical motor role
        self.assertEqual(pseudo_info[3],"sl2b") # sl2b physical motor role
        self.assertEqual(pseudo_info[4],"2") # number of pseudo motors
        self.assertEqual(pseudo_info[5],"Gap") # gap pseudo motor role
        self.assertEqual(pseudo_info[6],"Offset") # offset pseudo motor role
        self.assertEqual(pseudo_info[7],"1") # number of properties
       
#
# Replace the file
#               
        os.system('/bin/cp -f %s/PseudoLib.py.reloaded %s/PseudoLib.py' % (self.pydir,self.pydir))

#
# Delete the pseudo motors
#
        self.pool.command_inout("DeletePseudoMotor","testoffset01")
        self.pool.command_inout("DeletePseudoMotor","testgap01")        
#
# The Pseudo Motor list attribute is now empty
#
        self.check_empty_attribute(self.pool,"PseudoMotorList")       
        
#       
# Reload the code
#
        self.pool.command_inout("ReloadPseudoMotorCode","PseudoLib.py")

#
# Check the new information
#       
        pseudo_info = self.pool.command_inout("GetPseudoMotorInfo",["PseudoLib.py","Slit"])
        self.assertEqual(pseudo_info[0],"A Slit pseudo motor system for controlling gap and offset pseudo motors. Reloaded!")
        self.assertEqual(pseudo_info[1],"2") # number of physical motors
        self.assertEqual(pseudo_info[2],"Motor on blade 1") # sl2t physical motor role
        self.assertEqual(pseudo_info[3],"Motor on blade 2") # sl2b physical motor role
        self.assertEqual(pseudo_info[4],"2") # number of pseudo motors
        self.assertEqual(pseudo_info[5],"Gap") # gap pseudo motor role
        self.assertEqual(pseudo_info[6],"Offset") # offset pseudo motor role
        self.assertEqual(pseudo_info[7],"1") # number of properties

#----------------------------------------------------------------------------------------------------------------------

    def ReloadPseudoMotorCode(self):
        """Checking reload of Pseudo Motor python module"""

#
# Check that everything is as expected
#
        pseudo_info = self.pool.command_inout("GetPseudoMotorInfo",["PseudoLib.py","Slit"])
        self.assertEqual(pseudo_info[0],"A Slit pseudo motor system for controlling gap and offset pseudo motors.")
        self.assertEqual(pseudo_info[1],"2") # number of physical motors
        self.assertEqual(pseudo_info[2],"sl2t") # sl2t physical motor role
        self.assertEqual(pseudo_info[3],"sl2b") # sl2b physical motor role
        self.assertEqual(pseudo_info[4],"2") # number of pseudo motors
        self.assertEqual(pseudo_info[5],"Gap") # gap pseudo motor role
        self.assertEqual(pseudo_info[6],"Offset") # offset pseudo motor role
        self.assertEqual(pseudo_info[7],"1") # number of properties
               
#
# Replace the file
#
        os.system('/bin/cp -f %s/PseudoLib.py.reloaded %s/PseudoLib.py' % (self.pydir,self.pydir))

#
# Check that for new information at class level
#       
        pseudo_info = self.pool.command_inout("GetPseudoMotorInfo",["PseudoLib.py","Slit"])
        self.assertEqual(pseudo_info[0],"A Slit pseudo motor system for controlling gap and offset pseudo motors. Reloaded!")
        self.assertEqual(pseudo_info[1],"2") # number of physical motors
        self.assertEqual(pseudo_info[2],"Motor on blade 1") # sl2t physical motor role
        self.assertEqual(pseudo_info[3],"Motor on blade 2") # sl2b physical motor role
        self.assertEqual(pseudo_info[4],"2") # number of pseudo motors
        self.assertEqual(pseudo_info[5],"Gap") # gap pseudo motor role
        self.assertEqual(pseudo_info[6],"Offset") # offset pseudo motor role
        self.assertEqual(pseudo_info[7],"1") # number of properties
 
#
# Check that the existing pseudo motors still have the old information (note that there is an additional parameter to the GetPseudoMotorInfo)
#       
        pseudo_info = self.pool.command_inout("GetPseudoMotorInfo",["PseudoLib.py","Slit","testgap01"])
        self.assertEqual(pseudo_info[0],"A Slit pseudo motor system for controlling gap and offset pseudo motors.")
        self.assertEqual(pseudo_info[1],"2") # number of physical motors
        self.assertEqual(pseudo_info[2],"sl2t") # sl2t physical motor role
        self.assertEqual(pseudo_info[3],"sl2b") # sl2b physical motor role
        self.assertEqual(pseudo_info[4],"2") # number of pseudo motors
        self.assertEqual(pseudo_info[5],"Gap") # gap pseudo motor role
        self.assertEqual(pseudo_info[6],"Offset") # offset pseudo motor role
        self.assertEqual(pseudo_info[7],"1") # number of properties
        
#       
# Reload the code
#
        self.pool.command_inout("ReloadPseudoMotorCode","PseudoLib.py")

#
# Check the new information in the pseudo motors (note that there is an additional parameter to the GetPseudoMotorInfo)
#       
        pseudo_info = self.pool.command_inout("GetPseudoMotorInfo",["PseudoLib.py","Slit","testgap01"])
        self.assertEqual(pseudo_info[0],"A Slit pseudo motor system for controlling gap and offset pseudo motors.")
        self.assertEqual(pseudo_info[1],"2") # number of physical motors
        self.assertEqual(pseudo_info[2],"sl2t") # sl2t physical motor role
        self.assertEqual(pseudo_info[3],"sl2b") # sl2b physical motor role
        self.assertEqual(pseudo_info[4],"2") # number of pseudo motors
        self.assertEqual(pseudo_info[5],"Gap") # gap pseudo motor role
        self.assertEqual(pseudo_info[6],"Offset") # offset pseudo motor role
        self.assertEqual(pseudo_info[7],"1") # number of properties

#
# Back to the original file
#
        os.system('/bin/cp -f %s/PseudoLib.py.original %s/PseudoLib.py' % (self.pydir,self.pydir))
        
#       
# Reload the code
#
        self.pool.command_inout("ReloadPseudoMotorCode","PseudoLib.py")

#
# Check that for new information at class level
#       
        pseudo_info = self.pool.command_inout("GetPseudoMotorInfo",["PseudoLib.py","Slit"])
        self.assertEqual(pseudo_info[0],"A Slit pseudo motor system for controlling gap and offset pseudo motors. Reloaded!")
        self.assertEqual(pseudo_info[1],"2") # number of physical motors
        self.assertEqual(pseudo_info[2],"Motor on blade 1") # sl2t physical motor role
        self.assertEqual(pseudo_info[3],"Motor on blade 2") # sl2b physical motor role
        self.assertEqual(pseudo_info[4],"2") # number of pseudo motors
        self.assertEqual(pseudo_info[5],"Gap") # gap pseudo motor role
        self.assertEqual(pseudo_info[6],"Offset") # offset pseudo motor role
        self.assertEqual(pseudo_info[7],"1") # number of properties

#
# Check that the existing pseudo motors have the new information (note that there is an additional parameter to the GetPseudoMotorInfo)
#       
        pseudo_info = self.pool.command_inout("GetPseudoMotorInfo",["PseudoLib.py","Slit","testgap01"])
        self.assertEqual(pseudo_info[0],"A Slit pseudo motor system for controlling gap and offset pseudo motors.")
        self.assertEqual(pseudo_info[1],"2") # number of physical motors
        self.assertEqual(pseudo_info[2],"sl2t") # sl2t physical motor role
        self.assertEqual(pseudo_info[3],"sl2b") # sl2b physical motor role
        self.assertEqual(pseudo_info[4],"2") # number of pseudo motors
        self.assertEqual(pseudo_info[5],"Gap") # gap pseudo motor role
        self.assertEqual(pseudo_info[6],"Offset") # offset pseudo motor role
        self.assertEqual(pseudo_info[7],"1") # number of properties
#
# Delete the pseudo motors
#
        self.pool.command_inout("DeletePseudoMotor","testoffset01")
        self.pool.command_inout("DeletePseudoMotor","testgap01")

#
# The Pseudo Motor list attribute is now empty
#
        self.check_empty_attribute(self.pool,"PseudoMotorList")

#----------------------------------------------------------------------------------------------------------------------

    def aux_check_property(self,seq,name,type,descr,dftvalue = None):
        index = seq.index(name)
        self.failIf(index < 0)
        self.assertEqual(seq[index+1],type)
        self.assertEqual(seq[index+2],descr)
        
        if dftvalue != None:
            self.assertEqual(seq[index+3],dftvalue)
        else:
            self.assertEqual(seq[index+3],"")

#----------------------------------------------------------------------------------------------------------------------
            
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print len(sys.argv)
        print "PoolTst usage = PoolTst <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,TestPool,dev_name,sys.argv[1],"ReloadEmptyPseudoMotorCode")
    PoolTestUtil.start_test(runner,TestPool,dev_name,sys.argv[1],"ReloadPseudoMotorCode")
    
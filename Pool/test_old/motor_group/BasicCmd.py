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
        self.test_mot = PyTango.DeviceProxy("Test_Motor")
        self.assertEqual(self.test_mot.state(),PyTango.DevState.ON)

        self.test_mot.command_inout("DefinePosition",1500)
        new_pos = self.test_mot.read_attribute("Position")
        self.assertEqual(new_pos.value,1500)
        
        id_another_mot = self.pool.command_inout("CreateMotor",([3],["Another_Motor","cpp_ctrl"]))
        
        self.another_motor = PyTango.DeviceProxy("Another_Motor")
        self.another_motor.set_transparency_reconnection(True)
        
        self.another_motor.command_inout("DefinePosition",1500)
        ano_pos = self.another_motor.read_attribute("Position")
        self.assertEqual(ano_pos.value,1500)
        
#---------------------------------------------------------------------------------------------------------------------
               
    def BasicCmd_test(self):
        """Basic commands/attribute for MotorGroup (Create/Delete/GetId)"""
        
#
# Create Motor Group command with bad arguments
#

        self.wrong_argument(self.pool,"CreateMotorGroup",["MyGrp"],"Pool_BadArgument")
        self.wrong_argument(self.pool,"CreateMotorGroup",["MyGrp","Test_Motor","bid","Error_Motor"],"Pool_BadArgument")
        
#
# Create a group
#

        self.pool.command_inout("CreateMotorGroup",["MyGrp","Test_Motor","Error_Motor","another_MOTor"])
        self.wrong_argument(self.pool,"CreateMotorGroup",["myGrp","First_Motor","Fault_Motor"],"Pool_WrongMotorGroupName")
        self.pool.command_inout("CreateMotorGroup",["SecondGrp","First_Motor","Test_Motor"])
        
#
# Check MotorGroupList attribute
#

        mgl = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(mgl.dim_x,3)
        
        #first motor group was created by a pseudo motor. The exact name may change 
        self.failUnless(mgl.value[0].startswith("_pm_"))
        self.failUnless(mgl.value[0].endswith("Motor list: Test_Motor, Test_Motor2"))

        grp_1_str = "MyGrp (mg/test/MyGrp) Motor list: Test_Motor, Error_Motor, another_MOTor"
        grp_2_str = "SecondGrp (mg/test/SecondGrp) Motor list: First_Motor, Test_Motor"
        self.assertEqual(mgl.value[1],grp_1_str)
        self.assertEqual(mgl.value[2],grp_2_str)
        
#
# It's allowed to create another group with the same definition
#
        
        self.pool.command_inout("CreateMotorGroup",["SameGrp","Test_Motor","another_Motor","error_motor"])
        
        mgl = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(mgl.dim_x,4)

        self.pool.command_inout("DeleteMotorGroup","SameGrp")
        mgl = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(mgl.dim_x,3)
        
#
# Check a group with several times the same element and with group in group
#

        self.wrong_argument(self.pool,"CreateMotorGroup",["Two_Motors","Test_motor","another_Motor","Test_Motor"],"Pool_WrongMotorGroup")
        
        self.pool.command_inout("CreateMotorGroup",["GrpInGrp","MyGrp","First_Motor"])
        self.wrong_argument(self.pool,"CreateMotorGroup",["GrpBid","MyGrp","Error_Motor"],"Pool_WrongMotorGroup")

#
# Check DeleteMotorGroup command
#
        
        self.wrong_argument(self.pool,"DeleteMotorGroup","AaAa","Pool_MotorGroupNotFound")
        self.wrong_argument(self.pool,"DeleteMotorGroup","MyGRP","Pool_CantDeleteGroup")
        
        mgl = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(mgl.dim_x,4)
        self.failUnless(mgl.value[0].startswith("_pm_"))
        self.failUnless(mgl.value[0].endswith("Motor list: Test_Motor, Test_Motor2"))
        self.assertEqual(mgl.value[3],'GrpInGrp (mg/test/GrpInGrp) Motor list: MyGrp, First_Motor (test_motor, error_motor, another_motor, first_motor)')
       
        self.pool.command_inout("DeleteMotorGroup","GrpInGrp")
        self.pool.command_inout("DeleteMotorGroup","MyGRP")
                         
#
# Remove last classical motor group (last one is the one for pseudo-motors)
#
        
        self.pool.command_inout("DeleteMotorGroup","SeCoNdGRP")
        mgl = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(mgl.dim_x,1)
        self.failUnless(mgl.value[0].startswith("_pm_"))
        self.failUnless(mgl.value[0].endswith("Motor list: Test_Motor, Test_Motor2"))

        
#---------------------------------------------------------------------------------------------------------------------
               
    def BasicCmd_AddRemove_test(self):
        """Add/Remove elements from a MotorGroup device"""
        
        self.pool.command_inout("CreateMotorGroup",["MyGrp1","Test_Motor","Test_Motor2"])
        self.pool.command_inout("CreateMotorGroup",["MyGrp2","Test_Motor","Another_Motor"])
        self.pool.command_inout("CreateMotorGroup",["MyGrp3","Another_Motor"])
#
# Try to add an element that does not exist
#
        grp_proxy = PyTango.DeviceProxy("MyGrp1")
        
        self.wrong_argument(grp_proxy,"AddElement","inexisting_element","MotorGroup_BadArgument")

#
# Try to add a motor that already belongs to the motor group
#
        self.wrong_argument(grp_proxy,"AddElement","Test_Motor","MotorGroup_BadArgument")

#
# Try to add a new motor group that contains a common element with the motor group
#
        self.wrong_argument(grp_proxy,"AddElement","MyGrp2","MotorGroup_BadArgument")
        
#
# Try to remove an element that does not belong to the motor group
#
        self.wrong_argument(grp_proxy,"RemoveElement","Another_Motor","MotorGroup_BadArgument")

#
# Add a motor group
# 
        grp_proxy.command_inout("AddElement","MyGrp3")
        
        mgl = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(mgl.dim_x,4)

        grp_1_str = "MyGrp1 (mg/test/MyGrp1) Motor list: Test_Motor, Test_Motor2, MyGrp3 (test_motor, test_motor2, another_motor)"
        self.assertEqual(mgl.value[1],grp_1_str)

        db = PyTango.Database()
        props = db.get_device_property(grp_proxy.name(),["User_group_elt","Phys_group_elt","Motor_list","Motor_group_list"])
        self.assertEqual(props["User_group_elt"],["Test_Motor","Test_Motor2","MyGrp3"])
        self.assertEqual(props["Phys_group_elt"],["test_motor","test_motor2","another_motor"])
        self.assertEqual(props["Motor_list"],["Test_Motor","Test_Motor2"])
        self.assertEqual(props["Motor_group_list"],["MyGrp3"])

#
# Remove motors
#        
        grp_proxy.command_inout("RemoveElement","Test_Motor")
        grp_proxy.command_inout("RemoveElement","Test_Motor2")
        mgl = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(mgl.dim_x,4)

        grp_1_str = "MyGrp1 (mg/test/MyGrp1) Motor list: MyGrp3 (another_motor)"
        self.assertEqual(mgl.value[1],grp_1_str)

        props = db.get_device_property(grp_proxy.name(),["User_group_elt","Phys_group_elt","Motor_list","Motor_group_list"])
        self.assertEqual(props["User_group_elt"],["MyGrp3"])
        self.assertEqual(props["Phys_group_elt"],["another_motor"])
        self.assertEqual(props["Motor_list"],[])
        self.assertEqual(props["Motor_group_list"],["MyGrp3"])

#
# Add pseudo motors
#
        grp_proxy.command_inout("AddElement","testgap01")
        mgl = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(mgl.dim_x,4)

        grp_1_str = "MyGrp1 (mg/test/MyGrp1) Motor list: MyGrp3, testgap01 (another_motor, test_motor, test_motor2)"
        self.assertEqual(mgl.value[1],grp_1_str)

        props = db.get_device_property(grp_proxy.name(),["User_group_elt","Phys_group_elt","Motor_list","Motor_group_list","Pseudo_motor_list"])
        self.assertEqual(props["User_group_elt"],["MyGrp3","testgap01"])
        self.assertEqual(props["Phys_group_elt"],["another_motor", "test_motor", "test_motor2"])
        self.assertEqual(props["Motor_list"],[])
        self.assertEqual(props["Motor_group_list"],["MyGrp3"])
        self.assertEqual(props["Pseudo_motor_list"],["testgap01"])

        grp_proxy.command_inout("AddElement","testoffset01")
        mgl = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(mgl.dim_x,4)

        grp_1_str = "MyGrp1 (mg/test/MyGrp1) Motor list: MyGrp3, testgap01, testoffset01 (another_motor, test_motor, test_motor2)"
        self.assertEqual(mgl.value[1],grp_1_str)

        props = db.get_device_property(grp_proxy.name(),["User_group_elt","Phys_group_elt","Motor_list","Motor_group_list","Pseudo_motor_list"])
        self.assertEqual(props["User_group_elt"],["MyGrp3","testgap01","testoffset01"])
        self.assertEqual(props["Phys_group_elt"],["another_motor", "test_motor", "test_motor2"])
        self.assertEqual(props["Motor_list"],[])
        self.assertEqual(props["Motor_group_list"],["MyGrp3"])
        self.assertEqual(props["Pseudo_motor_list"],["testgap01","testoffset01"])

#
# Remove pseudo motors
#
        grp_proxy.command_inout("RemoveElement","testgap01")
        mgl = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(mgl.dim_x,4)

        grp_1_str = "MyGrp1 (mg/test/MyGrp1) Motor list: MyGrp3, testoffset01 (another_motor, test_motor, test_motor2)"
        self.assertEqual(mgl.value[1],grp_1_str)

        props = db.get_device_property(grp_proxy.name(),["User_group_elt","Phys_group_elt","Motor_list","Motor_group_list","Pseudo_motor_list"])
        self.assertEqual(props["User_group_elt"],["MyGrp3","testoffset01"])
        self.assertEqual(props["Phys_group_elt"],["another_motor", "test_motor", "test_motor2"])
        self.assertEqual(props["Motor_list"],[])
        self.assertEqual(props["Motor_group_list"],["MyGrp3"])
        self.assertEqual(props["Pseudo_motor_list"],["testoffset01"])

        grp_proxy.command_inout("RemoveElement","testoffset01")
        mgl = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(mgl.dim_x,4)

        grp_1_str = "MyGrp1 (mg/test/MyGrp1) Motor list: MyGrp3 (another_motor)"
        self.assertEqual(mgl.value[1],grp_1_str)

        props = db.get_device_property(grp_proxy.name(),["User_group_elt","Phys_group_elt","Motor_list","Motor_group_list","Pseudo_motor_list"])
        self.assertEqual(props["User_group_elt"],["MyGrp3"])
        self.assertEqual(props["Phys_group_elt"],["another_motor"])
        self.assertEqual(props["Motor_list"],[])
        self.assertEqual(props["Motor_group_list"],["MyGrp3"])
        self.assertEqual(props["Pseudo_motor_list"],[])


        
#---------------------------------------------------------------------------------------------------------------------

    def BasicGrp_test(self):
        """Basic commands/attribute on MotorGroup device (Init/State/Status)"""
        
#
# Create a group
#

        self.pool.command_inout("CreateMotorGroup",["AnotherGrp","Test_Motor","Another_Motor"])
        grp_proxy = PyTango.DeviceProxy("AnotherGrp")
        
#
# Execute state, status and Init
#

        self.assertEqual(grp_proxy.state(),PyTango.DevState.ON)
        grp_status = grp_proxy.status()
        self.assertEqual(grp_status,"The device is in ON state.")
        
        grp_proxy.command_inout("Init")
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

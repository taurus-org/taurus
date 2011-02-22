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
        
        self.empty_pool(self.pool)
        
        if self.__testMethodName == "GetPseudoMotorInfo":
            self.pool.command_inout("CreateController",["Motor","DummyCtrl.so","DummyController","cpp_ctrl"])
            self.pool.command_inout("CreateMotor",([1],["testmotor01","cpp_ctrl"]))
            self.pool.command_inout("CreateMotor",([2],["testmotor02","cpp_ctrl"]))
            self.pool.command_inout("CreateMotor",([3],["testmotor03","cpp_ctrl"]))
            self.pool.command_inout("CreateMotor",([4],["testmotor04","cpp_ctrl"]))

#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):

        if self.__testMethodName == "GetPseudoMotorInfo":
            self.pool.command_inout("DeleteMotor","testmotor01")
            self.pool.command_inout("DeleteMotor","testmotor02")
            self.pool.command_inout("DeleteMotor","testmotor03")
            self.pool.command_inout("DeleteMotor","testmotor04")
            self.pool.command_inout("DeleteController","cpp_ctrl")
        
            PyTango.Database().delete_property("PseudoLibProps.P2/P2_pm_testmotor01",["p_no_dft"])

#----------------------------------------------------------------------------------------------------------------------
            
    def PseudoMotorClasslist(self):
        """Checking Pseudo Motor Class List attribute"""
        
        pseudo_class_list = self.pool.read_attribute("PseudoMotorClassList")
        self.assertEqual(pseudo_class_list.dim_x,10)

        self.assertRaises(ValueError,pseudo_class_list.value.index,'Class: ErrorPseudoMotor')
        self.assertRaises(ValueError,pseudo_class_list.value.index,'Class: DummyGarbage')
        self.failUnless(pseudo_class_list.value.index('Class: Slit - File: %s/PseudoLib.py' % self.pydir) >= 0)
        self.failUnless(pseudo_class_list.value.index('Class: TableHeight - File: %s/PseudoLib.py' % self.pydir) >= 0)
        self.failUnless(pseudo_class_list.value.index('Class: DummyMotor01 - File: %s/PseudoLibExtra.py' % self.pydir) >= 0)
        self.failUnless(pseudo_class_list.value.index('Class: Silly01 - File: %s/PseudoLibExtra.py' % self.pydir) >= 0)
        self.failUnless(pseudo_class_list.value.index('Class: Silly02 - File: %s/PseudoLibExtra.py' % self.pydir) >= 0)
        self.failUnless(pseudo_class_list.value.index('Class: P1 - File: %s/PseudoLibProps.py' % self.pydir) >= 0)
        self.failUnless(pseudo_class_list.value.index('Class: P2 - File: %s/PseudoLibProps.py' % self.pydir) >= 0)
        self.failUnless(pseudo_class_list.value.index('Class: P3 - File: %s/PseudoLibProps.py' % self.pydir) >= 0)
        self.failUnless(pseudo_class_list.value.index('Class: P4 - File: %s/PseudoLibProps.py' % self.pydir) >= 0)
            
#----------------------------------------------------------------------------------------------------------------------

    def GetPseudoMotorInfo(self):
        """Checking GetPseudoMotorInfo"""
#
#  Simple check for a class with a long property and a default value
#        
        pseudo_info = self.pool.command_inout("GetPseudoMotorInfo",["PseudoLibProps.py","P1"])
        self.assertEqual(pseudo_info[0],"A pseudo motor system for testing properties feature.")
        self.assertEqual(pseudo_info[1],"1") # number of physical motors
        self.assertEqual(pseudo_info[2],"m1") # sl2t physical motor role
        self.assertEqual(pseudo_info[3],"1") # sl2b physical motor role
        self.assertEqual(pseudo_info[4],"P1") # number of pseudo motors
        self.assertEqual(pseudo_info[5],"1") # number of properties
        self.aux_check_property(pseudo_info,"p_long","DevLong","A property for demonstrating a long property","987654321")
        self.failIf(len(pseudo_info) != 10)

#
#  Simple check for a class with a long property and without a default value
#        
        pseudo_info = self.pool.command_inout("GetPseudoMotorInfo",["PseudoLibProps.py","P2"])
        self.assertEqual(pseudo_info[0],"A pseudo motor system for testing properties feature: without default value.")
        self.assertEqual(pseudo_info[1],"1") # number of physical motors
        self.assertEqual(pseudo_info[2],"m1") # sl2t physical motor role
        self.assertEqual(pseudo_info[3],"1") # sl2b physical motor role
        self.assertEqual(pseudo_info[4],"P2") # number of pseudo motors
        self.assertEqual(pseudo_info[5],"1") # number of properties
        self.aux_check_property(pseudo_info,"p_no_dft","DevLong","A property for demonstrating a long property without default value")
        self.failIf(len(pseudo_info) != 10)

#
#  Check for a class with a property for each type of data. A long list indeed!!!
#        
        pseudo_info = self.pool.command_inout("GetPseudoMotorInfo",["PseudoLibProps.py","P3"])
        self.assertEqual(pseudo_info[0],"A pseudo motor system for testing properties feature: All types of data")
        self.assertEqual(pseudo_info[1],"1") # number of physical motors
        self.assertEqual(pseudo_info[2],"m1") # sl2t physical motor role
        self.assertEqual(pseudo_info[3],"1") # sl2b physical motor role
        self.assertEqual(pseudo_info[4],"P3") # number of pseudo motors
        self.assertEqual(pseudo_info[5],"12") # number of properties
        self.aux_check_property(pseudo_info,"p_long","DevLong","A property for demonstrating a long property","987654321")
        self.aux_check_property(pseudo_info,"p_double","DevDouble","A property for demonstrating a double property","123456.654321")
        self.aux_check_property(pseudo_info,"p_bool","DevBoolean","A property for demonstrating a boolean property","True")
        self.aux_check_property(pseudo_info,"p_string","DevString","A property for demonstrating a string property","Some silly default content for a string property")
        self.aux_check_property(pseudo_info,"p_longArray_tuple","DevVarLongArray","A property for demonstrating a long array property as a tuple","9876\n12345")
        self.aux_check_property(pseudo_info,"p_longArray_list","DevVarLongArray","A property for demonstrating a long array property as a list","9876\n54321")
        self.aux_check_property(pseudo_info,"p_doubleArray_tuple","DevVarDoubleArray","A property for demonstrating a double array property as a tuple","5.1\n0.44\n333")
        self.aux_check_property(pseudo_info,"p_doubleArray_list","DevVarDoubleArray","A property for demonstrating a double array property as a list","5.1\n0.44\n333")
        self.aux_check_property(pseudo_info,"p_boolArray_tuple","DevVarBooleanArray","A property for demonstrating a boolean array property as a tuple","True\nFalse\nTrue")
        self.aux_check_property(pseudo_info,"p_boolArray_list","DevVarBooleanArray","A property for demonstrating a boolean array property as a list","True\nFalse\nTrue")
        self.aux_check_property(pseudo_info,"p_stringArray_tuple","DevVarStringArray","A property for demonstrating a string array property","Some silly default content for a string array property\nas a tuple!")
        self.aux_check_property(pseudo_info,"p_stringArray_list","DevVarStringArray","A property for demonstrating a string array property","Some silly default content for a string array property\nas a list!")         
    
#
# Trying to create a pseudo motor without a mandatory property value is an error
#
        self.wrong_argument(self.pool,"CreatePseudoMotor",["PseudoLibProps.py","P2","testP2","testmotor01"],"Pool_MissingDatabaseProperty")
        
#
# Trying to create a pseudo motor with a mandatory property value defined in the database
#
        db = PyTango.Database()
        db.put_property("PseudoLibProps.P2/P2_pm_testmotor01",{"p_no_dft" : ["98765"]})
        self.pool.command_inout("CreatePseudoMotor",["PseudoLibProps.py","P2","testP2","testmotor01"])

        pseudo_list = self.pool.read_attribute("PseudoMotorList")
        self.assertEqual(pseudo_list.dim_x,1)

        self.pool.command_inout("DeletePseudoMotor","testP2")
        self.check_empty_attribute(self.pool,"PseudoMotorList")
        self.check_empty_attribute(self.pool,"MotorGroupList")
        
        prop_dict = db.get_property("PseudoLibProps.P2/P2_pm_testmotor01",["p_no_dft"])
        #self.failIf(len(prop_dict["p_no_dft"]) != 0)
        
#
# Trying to create a pseudo motor with a wrong default Value data type
#
        self.wrong_argument(self.pool,"GetPseudoMotorInfo",["PseudoLibProps.py","P4"],"Pool_InvalidPythonPropertyValue")
        self.wrong_argument(self.pool,"CreatePseudoMotor",["PseudoLibProps.py","P4","testP4","testmotor01"],"Pool_InvalidPythonPropertyValue")

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
    PoolTestUtil.start_test(runner,TestPool,dev_name,sys.argv[1],"PseudoMotorClasslist")
    PoolTestUtil.start_test(runner,TestPool,dev_name,sys.argv[1],"GetPseudoMotorInfo")
    
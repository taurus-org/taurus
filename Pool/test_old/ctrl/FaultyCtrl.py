import unittest
import PyTango
import sys
import os
import time
import posix
import PoolTestUtil      

         
class FaultCtrl(unittest.TestCase):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.admin_name = "dserver/" + ds_full_name
        
#---------------------------------------------------------------------------------------------------------------------

    def base_setUp(self):
        self.pool.command_inout("CreateController",["Motor","WaterPapCtrl.py","IcePapController","first"])
        self.pool.command_inout("CreateController",["Motor","FirePapCtrl.py","FirePapController","second"])
        
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,4)
        ctrl0_str = "Second_Py_Vct6 (Vct6Ctrl.Vct6Controller/Second_Py_Vct6) - CounterTimer Python ctrl (Vct6Ctrl.py)"
        ctrl1_str = "Second_Cpp_ZeroD (DummyZeroDCtrl.DummyZeroDController/Second_Cpp_ZeroD) - ZeroDExpChannel Cpp ctrl (DummyZeroDCtrl.so)"
        ctrl2_str = "first (WaterPapCtrl.IcePapController/first) - Motor Python ctrl (WaterPapCtrl.py)"
        ctrl3_str = "second (FirePapCtrl.FirePapController/second) - Motor Python ctrl (FirePapCtrl.py)"
        self.assertEqual(ctrl_list.value[0],ctrl0_str)
        self.assertEqual(ctrl_list.value[1],ctrl1_str)
        self.assertEqual(ctrl_list.value[2],ctrl2_str)
        self.assertEqual(ctrl_list.value[3],ctrl3_str)
        
        self.pool.command_inout("CreateMotor",([0],["First_Motor","first"]))
        self.pool.command_inout("CreateMotor",([1],["Second_Motor","FiRsT"]))
        self.pool.command_inout("CreateMotor",([0],["Third_Motor","second"]))

        mot_list = self.pool.read_attribute("MotorList")
        self.assertEqual(mot_list.dim_x,3)
        mot1_str = "First_Motor (motor/first/0)"
        mot2_str = "Second_Motor (motor/first/1)"
        mot3_str = "Third_Motor (motor/second/0)"
        self.assertEqual(mot_list.value[0],mot1_str)
        self.assertEqual(mot_list.value[1],mot2_str)
        self.assertEqual(mot_list.value[2],mot3_str)
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        mot1 = PyTango.DeviceProxy("First_Motor")
        self.assertEqual(mot1.state(),PyTango.DevState.ON)
        mot2 = PyTango.DeviceProxy("Second_Motor")
        self.assertEqual(mot2.state(),PyTango.DevState.ON)
        mot3 = PyTango.DeviceProxy("Third_Motor")
        self.assertEqual(mot3.state(),PyTango.DevState.ON)
        
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)
# VALGRIND        self.pool.set_timeout_millis(10000)
        self.pool.set_timeout_millis(10000)
        
        self.admin = PyTango.DeviceProxy(self.admin_name)
        self.admin.set_transparency_reconnection(True)
# VALGRIND        self.admin.set_timeout_millis(10000)
        self.admin.set_timeout_millis(10000)
        
        self.base_setUp()
        
        posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_ok.py")
        posix.rename("ctrl/test_ctrl/WaterPapCtrl_syn.py","ctrl/test_ctrl/WaterPapCtrl.py")
            
#---------------------------------------------------------------------------------------------------------------------
               
    def Wrong_Syntax(self):
        """Python controller with wrong syntax"""
        
#
# Send an init command on the admin device
#

        self.admin.command_inout("Init")
        
#
# Check that we still have 3 controllers and 3 motors
#

        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,4)
        
        mot_list = self.pool.read_attribute("MotorList")
        self.assertEqual(mot_list.dim_x,3)
        
#
# The Pool state should be ALARM and two motors state should be FAULT
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ALARM)
        mot1 = PyTango.DeviceProxy("First_Motor")
        self.assertEqual(mot1.state(),PyTango.DevState.FAULT)
        mot2 = PyTango.DeviceProxy("Second_Motor")
        self.assertEqual(mot2.state(),PyTango.DevState.FAULT)
        mot3 = PyTango.DeviceProxy("Third_Motor")
        self.assertEqual(mot3.state(),PyTango.DevState.ON)
        
        pool_status = self.pool.status()
        self.assertNotEqual(pool_status.find("SyntaxError: invalid syntax"),-1)
        
#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_syn.py")
        posix.rename("ctrl/test_ctrl/WaterPapCtrl_ok.py","ctrl/test_ctrl/WaterPapCtrl.py")
        
#-------------------------------------------------------------------------------------------------------------------
#
#        New test class
#
#-------------------------------------------------------------------------------------------------------------------
        
class ReLoadCtrl(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name       
#---------------------------------------------------------------------------------------------------------------------                         
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)
        
        posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_ok.py")
        posix.rename("ctrl/test_ctrl/WaterPapCtrl_syn.py","ctrl/test_ctrl/WaterPapCtrl.py")           
#---------------------------------------------------------------------------------------------------------------------              
    def stupidReloadCtrl(self):
        """Stupid argument(s) for the ReloadController command"""
        
        self.wrong_argument(self.pool,"ReloadControllerCode","a/b","Pool_FileUnsupportedType")
        self.wrong_argument(self.pool,"ReloadControllerCode","a","Pool_ControllerNotFound")
        self.wrong_argument(self.pool,"ReloadControllerCode","a.py","Pool_ControllerNotFound")        
#---------------------------------------------------------------------------------------------------------------------              
    def ReloadCtrl_test(self):
        """ReloadControllerCode command (Reload a ctrl with wrong syntax)"""
        
#
# Reload a faulty controller
#
        
        self.wrong_argument(self.pool,"ReloadControllerCode","WaterPapCtrl.py","Pool_PythonControllerError")
        
#
# The Pool state should be ALARM and two motors state should be FAULT
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ALARM)
        mot1 = PyTango.DeviceProxy("First_Motor")
        self.assertEqual(mot1.state(),PyTango.DevState.FAULT)
        mot2 = PyTango.DeviceProxy("Second_Motor")
        self.assertEqual(mot2.state(),PyTango.DevState.FAULT)
        mot3 = PyTango.DeviceProxy("Third_Motor")
        self.assertEqual(mot3.state(),PyTango.DevState.ON)
        
        pool_status = self.pool.status()
        self.assertNotEqual(pool_status.find("SyntaxError: invalid syntax"),-1)           
#---------------------------------------------------------------------------------------------------------------------
    def tearDown(self):
        posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_syn.py")
        posix.rename("ctrl/test_ctrl/WaterPapCtrl_ok.py","ctrl/test_ctrl/WaterPapCtrl.py")
#---------------------------------------------------------------------------------------------------------------------            

#-------------------------------------------------------------------------------------------------------------------
#
#        New test class
#
#-------------------------------------------------------------------------------------------------------------------
        
class ReLoadCtrlOk(unittest.TestCase):
    def __init__(self,dev_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name       
#---------------------------------------------------------------------------------------------------------------------                           
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True) 
        self.pool.set_timeout_millis(10000)      
#---------------------------------------------------------------------------------------------------------------------              
    def ReloadCtrlOk_test(self):
        """ReloadControllerCode command (Reload a good ctrl code)"""
        
#
# Reload a good controller
#
        
        self.pool.command_inout("ReloadControllerCode","WaterPapCtrl.py")
        
#
# The Pool state should be ON and two motors state should be ON
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        mot1 = PyTango.DeviceProxy("First_Motor")
        self.assertEqual(mot1.state(),PyTango.DevState.ON)
        mot2 = PyTango.DeviceProxy("Second_Motor")
        self.assertEqual(mot2.state(),PyTango.DevState.ON)
        mot3 = PyTango.DeviceProxy("Third_Motor")
        self.assertEqual(mot3.state(),PyTango.DevState.ON)          
#---------------------------------------------------------------------------------------------------------------------
    def tearDown(self):
        pass
    
    
#-------------------------------------------------------------------------------------------------------------------
#
#        New test class
#
#-------------------------------------------------------------------------------------------------------------------
        
class ReLoadCtrlMiss(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name       
#---------------------------------------------------------------------------------------------------------------------                           
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)
# VALGRIND        self.pool.set_timeout_millis(10000)
        self.pool.set_timeout_millis(10000)
        
        posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_ok.py")
        posix.rename("ctrl/test_ctrl/WaterPapCtrl_mis.py","ctrl/test_ctrl/WaterPapCtrl.py")                 
#---------------------------------------------------------------------------------------------------------------------              
    def ReloadCtrlMiss_test(self):
        """ReloadControllerCode command (Reload a ctrl code with missing methods)"""
        
#
# Reload a good controller
#
        
        self.wrong_argument(self.pool,"ReloadControllerCode","WaterPapCtrl.py","Pool_CantCreateController")
        pool_status = self.pool.status()
        self.assertNotEqual(pool_status.find("Method StateOne does not exist"),-1)
        
#
# The Pool state should be ALARM and two motors state should be FAULT
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ALARM)
        mot1 = PyTango.DeviceProxy("First_Motor")
        self.assertEqual(mot1.state(),PyTango.DevState.FAULT)
        mot2 = PyTango.DeviceProxy("Second_Motor")
        self.assertEqual(mot2.state(),PyTango.DevState.FAULT)
        mot3 = PyTango.DeviceProxy("Third_Motor")
        self.assertEqual(mot3.state(),PyTango.DevState.ON)
        
        pool_status = self.pool.status()
        self.assertNotEqual(pool_status.find("Method"),-1)
        self.assertNotEqual(pool_status.find("does not exist"),-1)         
#---------------------------------------------------------------------------------------------------------------------
    def tearDown(self):
        posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_mis.py")
        posix.rename("ctrl/test_ctrl/WaterPapCtrl_ok.py","ctrl/test_ctrl/WaterPapCtrl.py") 
        
#-------------------------------------------------------------------------------------------------------------------
#
#        New test class
#
#-------------------------------------------------------------------------------------------------------------------
        
class InitReLoadCtrlMiss(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.admin_name = "dserver/" + ds_full_name       
        self.bdir = PoolTestUtil.GetBasePath()
        
#---------------------------------------------------------------------------------------------------------------------                           
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)
        
        self.admin = PyTango.DeviceProxy(self.admin_name)
        self.admin.set_transparency_reconnection(True) 
# VALGRIND        self.admin.set_timeout_millis(10000)
        self.admin.set_timeout_millis(10000)
        
        posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_ok.py")
        posix.rename("ctrl/test_ctrl/WaterPapCtrl_mis.py","ctrl/test_ctrl/WaterPapCtrl.py")                 
#---------------------------------------------------------------------------------------------------------------------              
    def InitReloadCtrlMiss_test(self):
        """Restart a pool with one controller with missing method"""
        
#
# Reload a faulty controller
#
        
        self.wrong_argument(self.pool,"ReloadControllerCode","WaterPapCtrl.py","Pool_CantCreateController")
        pool_status = self.pool.status()
        self.assertNotEqual(pool_status.find("Method StateOne does not exist"),-1)

#
# The Pool state should be ALARM and two motors state should be FAULT
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ALARM)
        mot1 = PyTango.DeviceProxy("First_Motor")
        self.assertEqual(mot1.state(),PyTango.DevState.FAULT)
        mot2 = PyTango.DeviceProxy("Second_Motor")
        self.assertEqual(mot2.state(),PyTango.DevState.FAULT)
        mot3 = PyTango.DeviceProxy("Third_Motor")
        self.assertEqual(mot3.state(),PyTango.DevState.ON)
        
        pool_status = self.pool.status()
        self.assertNotEqual(pool_status.find("Method"),-1)
        self.assertNotEqual(pool_status.find("does not exist"),-1)
        
#
# Send an init command on the admin device
#

        self.admin.command_inout("Init")
        
#
# Check that we still have 3 controllers and 3 motors
#

        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,4)
        
        mot_list = self.pool.read_attribute("MotorList")
        self.assertEqual(mot_list.dim_x,3)
        
#
# The Pool state should be ALARM and two motors state should be FAULT
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ALARM)
        mot1 = PyTango.DeviceProxy("First_Motor")
        self.assertEqual(mot1.state(),PyTango.DevState.FAULT)
        mot2 = PyTango.DeviceProxy("Second_Motor")
        self.assertEqual(mot2.state(),PyTango.DevState.FAULT)
        mot3 = PyTango.DeviceProxy("Third_Motor")
        self.assertEqual(mot3.state(),PyTango.DevState.ON)
        
        pool_status = self.pool.status()
        self.assertNotEqual(pool_status.find("Method"),-1)
        self.assertNotEqual(pool_status.find("does not exist"),-1)
        
#
# Check a ControlleClassList attribute just in case
#

        ctrls = self.pool.read_attribute("ControllerClasslist")
        self.assertEqual(ctrls.dim_x,19)
        self.assertEqual(ctrls.value[0],"Type: CounterTimer - Class: DummyCoTiController - File: %s/ctrl/DummyCoTiCtrl.so"% self.bdir)
        self.assertEqual(ctrls.value[1],"Type: CounterTimer - Class: Machin - File: %s/ctrl/DummyCoTiCtrl.so" % self.bdir)
        self.assertEqual(ctrls.value[2],"Type: CounterTimer - Class: UnixTimer - File: %s/ctrl/UxTimer.so" % self.bdir)
        self.assertEqual(ctrls.value[3],"Type: CounterTimer - Class: Vct6Controller - File: %s/test/ctrl/coti_ctrl/Vct6Ctrl.py" % self.bdir)
        self.assertEqual(ctrls.value[4],"Type: CounterTimer - Class: Vct6Controller - File: %s/test/ctrl/coti_ctrl/Vct6Ctrl_init.py" % self.bdir)
        self.assertEqual(ctrls.value[5],"Type: Motor - Class: DummyController - File: %s/ctrl/DummyCtrl.so" % self.bdir)
        self.assertEqual(ctrls.value[6],"Type: Motor - Class: FirePapController - File: %s/test/ctrl/test_ctrl/FirePapCtrl.py" % self.bdir)
        self.assertEqual(ctrls.value[7],"Type: Motor - Class: IcePapController - File: %s/test/ctrl/test_ctrl/WaterPapCtrl_init.py" % self.bdir)
        self.assertEqual(ctrls.value[8],"Type: Motor - Class: IcePapController - File: %s/test/ctrl/test_ctrl/WaterPapCtrl_mis_extra.py" % self.bdir)
        self.assertEqual(ctrls.value[9],"Type: Motor - Class: IcePapController - File: %s/test/ctrl/test_ctrl/WaterPapCtrl_mis_feat.py" % self.bdir)
        self.assertEqual(ctrls.value[10],"Type: Motor - Class: IcePapController - File: %s/test/ctrl/test_ctrl/WaterPapCtrl_ok.py" % self.bdir)
        self.assertEqual(ctrls.value[11],"Type: Motor - Class: IcePapController - File: %s/test/ctrl/test_ctrl/WaterPapCtrl_prop.py" % self.bdir)
        self.assertEqual(ctrls.value[12],"Type: Motor - Class: IcePapController - File: %s/test/ctrl/test_ctrl/WaterPapCtrl_stat1.py" % self.bdir)
        self.assertEqual(ctrls.value[13],"Type: Motor - Class: IcePapController - File: %s/test/ctrl/test_ctrl/WaterPapCtrl_stat2.py" % self.bdir)
        self.assertEqual(ctrls.value[14],"Type: Motor - Class: Toto - File: %s/ctrl/DummyCtrl.so" % self.bdir)
        self.assertEqual(ctrls.value[15],"Type: ZeroDExpChannel - Class: DummyZeroDController - File: %s/ctrl/DummyZeroDCtrl.so" % self.bdir)
        self.assertEqual(ctrls.value[16],"Type: ZeroDExpChannel - Class: ElecMeterController - File: %s/test/ctrl/zerod_ctrl/ElecMeter.py" % self.bdir)
        self.assertEqual(ctrls.value[17],"Type: ZeroDExpChannel - Class: ElecMeterController - File: %s/test/ctrl/zerod_ctrl/ElecMeter_init.py" % self.bdir)
        self.assertEqual(ctrls.value[18],"Type: ZeroDExpChannel - Class: Glop - File: %s/ctrl/DummyZeroDCtrl.so" % self.bdir)
                        
#---------------------------------------------------------------------------------------------------------------------
    def tearDown(self):
        posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_mis.py")
        posix.rename("ctrl/test_ctrl/WaterPapCtrl_ok.py","ctrl/test_ctrl/WaterPapCtrl.py") 
        
        
#-------------------------------------------------------------------------------------------------------------------
#
#        New test class
#
#-------------------------------------------------------------------------------------------------------------------
        
class Classical_ReLoadCtrl(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
#---------------------------------------------------------------------------------------------------------------------                           
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)

        self.mot = PyTango.DeviceProxy("Second_Motor")
        self.second_rename = False
                
        posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_ok.py")
        posix.rename("ctrl/test_ctrl/WaterPapCtrl_stat1.py","ctrl/test_ctrl/WaterPapCtrl.py")                 
#---------------------------------------------------------------------------------------------------------------------              
    def Classical_ReloadCtrl_test(self):
        """Classical reload controller call"""
        
#
# Reload the controller
#
        
        self.pool.command_inout("ReloadControllerCode","WaterPapCtrl.py")
        
#
# The Pool state should be ON. This controller set the motor in FAULT
# state to used the status string returned by the GetState controller method
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.assertEqual(self.mot.state(),PyTango.DevState.FAULT)

        mot_status = self.mot.status()
        self.assertNotEqual(mot_status.find("Hola tio"),-1)
        
        posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_stat1.py")
        posix.rename("ctrl/test_ctrl/WaterPapCtrl_stat2.py","ctrl/test_ctrl/WaterPapCtrl.py")
        self.second_rename = True
        
#
# Reload again the controller
#
        
        self.pool.command_inout("ReloadControllerCode","WaterPapCtrl.py")
        
#
# The Pool state should be ON. This controller set the motor in FAULT
# state to used the status string returned by the GetState controller method
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        self.assertEqual(self.mot.state(),PyTango.DevState.FAULT)

        mot_status = self.mot.status()
        self.assertNotEqual(mot_status.find("Hola mujeres de Barcelona"),-1)
                
#---------------------------------------------------------------------------------------------------------------------
    def tearDown(self):
        if self.second_rename == False:
            posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_stat1.py")
        else:
            posix.rename("ctrl/test_ctrl/WaterPapCtrl.py","ctrl/test_ctrl/WaterPapCtrl_stat2.py")
        posix.rename("ctrl/test_ctrl/WaterPapCtrl_ok.py","ctrl/test_ctrl/WaterPapCtrl.py")
        
        self.pool.command_inout("ReloadControllerCode","WaterPapCtrl.py")
        
        
#-------------------------------------------------------------------------------------------------------------------
#
#        New test class
#
#-------------------------------------------------------------------------------------------------------------------
        
class ExtraFeatures_Miss_Ctrl(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
#---------------------------------------------------------------------------------------------------------------------                           
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)
        
        self.assertEqual(self.pool.state(),PyTango.DevState.ON)

        self.mot = PyTango.DeviceProxy("Second_Motor")
               
#---------------------------------------------------------------------------------------------------------------------              
    def ExtraFeatures_Miss_Ctrl_test(self):
        """Controller with wrong definition of extra features"""

        self.wrong_argument(self.pool,"CreateController",["Motor","WaterPapCtrl_mis_extra.py","IcePapController","extra"],"Pool_PythonMethodNotFound")
 
 #---------------------------------------------------------------------------------------------------------------------              
    def Features_Miss_Ctrl_test(self):
        """Controller with wrong definition of extra attributes"""

        self.wrong_argument(self.pool,"CreateController",["Motor","WaterPapCtrl_mis_feat.py","IcePapController","extra"],"Pool_PythonMethodNotFound")
               
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
        print len(sys.argv)
        print "FaultyCtrl usage = FaultyCtrl <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)

    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,FaultCtrl,dev_name,sys.argv[1],"Wrong_Syntax")
    PoolTestUtil.start_test(runner,ReLoadCtrl,dev_name,"stupidReloadCtrl")
    PoolTestUtil.start_test(runner,ReLoadCtrl,dev_name,"ReloadCtrl_test")
    PoolTestUtil.start_test(runner,ReLoadCtrlOk,dev_name,"ReloadCtrlOk_test")
    PoolTestUtil.start_test(runner,ReLoadCtrlMiss,dev_name,"ReloadCtrlMiss_test")
    PoolTestUtil.start_test(runner,ReLoadCtrlOk,dev_name,"ReloadCtrlOk_test")
    PoolTestUtil.start_test(runner,InitReLoadCtrlMiss,dev_name,sys.argv[1],"InitReloadCtrlMiss_test")
    PoolTestUtil.start_test(runner,ReLoadCtrlOk,dev_name,"ReloadCtrlOk_test")
    PoolTestUtil.start_test(runner,Classical_ReLoadCtrl,dev_name,"Classical_ReloadCtrl_test")
    PoolTestUtil.start_test(runner,ExtraFeatures_Miss_Ctrl,dev_name,"ExtraFeatures_Miss_Ctrl_test")
    PoolTestUtil.start_test(runner,ExtraFeatures_Miss_Ctrl,dev_name,"Features_Miss_Ctrl_test")
    

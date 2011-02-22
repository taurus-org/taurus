import unittest
import PyTango
import sys
import os
import PoolTestUtil


class TestPool(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.bdir = PoolTestUtil.GetBasePath();
        
    def setUp(self):
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.pool.set_transparency_reconnection(True)
# VALGRIND        self.pool.set_timeout_millis(10000)
        self.pool.set_timeout_millis(10000)

    def emptypool(self):
        """Checking an empty pool"""
        sta = self.pool.command_inout("State")
        self.assertEqual(sta,PyTango.DevState.ON,"State must be ON and is %s"% (sta))
        
        sta = self.pool.command_inout("Status")
        the_sta = '''The device is in ON state.'''
        self.assertEqual(sta,the_sta,"Status must be\n%s\n and is\n%s" % (the_sta,sta))

#
# These attributes must be empty
#

        self.check_empty_attribute(self.pool,"ControllerList")
        self.check_empty_attribute(self.pool,"MotorList")
        self.check_empty_attribute(self.pool,"MotorGroupList")
        self.check_empty_attribute(self.pool,"ExpChannelList")
 
 #
 # Simulation mode must be False
 #
        
        sim = self.pool.read_attribute("SimulationMode")
        self.assertEqual(sim.value,False)

#----------------------------------------------------------------------------------------------------------------------
        
    def stupidArgs(self):
        """Stupid argument(s) for the CreateController command"""
        
        self.wrong_argument(self.pool,"CreateController",["a","b","c"],"Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool,"CreateController",["Motor","a/b","ctrl","inst"], "Pool_FileUnsupportedType")
        self.wrong_argument(self.pool,"CreateController",["Motor","a/b.truc","ctrl","inst"], "Pool_FileUnsupportedType")
        self.wrong_argument(self.pool,"createController",["Mot","a","b","x"],"Pool_FileUnsupportedType")
        
        self.wrong_argument(self.pool,"CreateController",["Motor","a.py","b","x"],"Pool_ControllerNotFound")
        self.wrong_argument(self.pool,"CreateController",["Motor","a.so","b","x"],"Pool_ControllerNotFound")

        self.wrong_argument(self.pool,"CreateController",["Motor","WaterPapCtrl.py","b","x"],"Pool_CantLocatePythonClass")
        self.wrong_argument(self.pool,"CreateController",["Motor","WaterPapCtrl_mis.py","IcePapController","x"],"Pool_PythonMethodNotFound")

#----------------------------------------------------------------------------------------------------------------------
            
    def CtrlClasslist(self):
        """ControllerClassList attribute"""
        
        ctrls = self.pool.read_attribute("ControllerClasslist")
        self.assertEqual(ctrls.dim_x,19)
        self.assertEqual(ctrls.value[0],"Type: CounterTimer - Class: DummyCoTiController - File: %s/ctrl/DummyCoTiCtrl.so" % self.bdir)
        self.assertEqual(ctrls.value[1],"Type: CounterTimer - Class: Machin - File: %s/ctrl/DummyCoTiCtrl.so" % self.bdir)
        self.assertEqual(ctrls.value[2],"Type: CounterTimer - Class: UnixTimer - File: %s/ctrl/UxTimer.so" % self.bdir)
        self.assertEqual(ctrls.value[3],"Type: CounterTimer - Class: Vct6Controller - File: %s/test/ctrl/coti_ctrl/Vct6Ctrl.py" % self.bdir)
        self.assertEqual(ctrls.value[4],"Type: CounterTimer - Class: Vct6Controller - File: %s/test/ctrl/coti_ctrl/Vct6Ctrl_init.py" % self.bdir)
        self.assertEqual(ctrls.value[5],"Type: Motor - Class: DummyController - File: %s/ctrl/DummyCtrl.so" % self.bdir)
        self.assertEqual(ctrls.value[6],"Type: Motor - Class: FirePapController - File: %s/test/ctrl/test_ctrl/FirePapCtrl.py" % self.bdir)
        self.assertEqual(ctrls.value[7],"Type: Motor - Class: IcePapController - File: %s/test/ctrl/test_ctrl/WaterPapCtrl.py" % self.bdir)
        self.assertEqual(ctrls.value[8],"Type: Motor - Class: IcePapController - File: %s/test/ctrl/test_ctrl/WaterPapCtrl_init.py" % self.bdir)
        self.assertEqual(ctrls.value[9],"Type: Motor - Class: IcePapController - File: %s/test/ctrl/test_ctrl/WaterPapCtrl_mis_extra.py" % self.bdir)
        self.assertEqual(ctrls.value[10],"Type: Motor - Class: IcePapController - File: %s/test/ctrl/test_ctrl/WaterPapCtrl_mis_feat.py" % self.bdir)
        self.assertEqual(ctrls.value[11],"Type: Motor - Class: IcePapController - File: %s/test/ctrl/test_ctrl/WaterPapCtrl_prop.py" % self.bdir)
        self.assertEqual(ctrls.value[12],"Type: Motor - Class: IcePapController - File: %s/test/ctrl/test_ctrl/WaterPapCtrl_stat1.py" % self.bdir)
        self.assertEqual(ctrls.value[13],"Type: Motor - Class: IcePapController - File: %s/test/ctrl/test_ctrl/WaterPapCtrl_stat2.py" % self.bdir)
        self.assertEqual(ctrls.value[14],"Type: Motor - Class: Toto - File: %s/ctrl/DummyCtrl.so" % self.bdir)
        self.assertEqual(ctrls.value[15],"Type: ZeroDExpChannel - Class: DummyZeroDController - File: %s/ctrl/DummyZeroDCtrl.so" % self.bdir)
        self.assertEqual(ctrls.value[16],"Type: ZeroDExpChannel - Class: ElecMeterController - File: %s/test/ctrl/zerod_ctrl/ElecMeter.py" % self.bdir)
        self.assertEqual(ctrls.value[17],"Type: ZeroDExpChannel - Class: ElecMeterController - File: %s/test/ctrl/zerod_ctrl/ElecMeter_init.py" % self.bdir)
        self.assertEqual(ctrls.value[18],"Type: ZeroDExpChannel - Class: Glop - File: %s/ctrl/DummyZeroDCtrl.so" % self.bdir)

#----------------------------------------------------------------------------------------------------------------------
            
    def CreateRem_Controller(self):
        """Create - Delete Motor controller"""
        
#
# Create one controller
#
        
        self.pool.command_inout("CreateController",["Motor","WaterPapCtrl.py","IcePapController","first"])
        
#
# Creating 2 times the same controller is an error
#
       
        self.wrong_argument(self.pool,"CreateController",["Motor","WaterPapCtrl.py","IcePapController","first"],"Pool_ControllerAlreadyCreated")

#
# Create a new controller
#
        
        self.pool.command_inout("CreateController",["Motor","WaterPapCtrl.py","IcePapController","second"])

#
# Check controller list attribute
#
        
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,2)
        self.assertEqual(ctrl_list.value[0],"first (WaterPapCtrl.IcePapController/first) - Motor Python ctrl (WaterPapCtrl.py)")
        self.assertEqual(ctrl_list.value[1],"second (WaterPapCtrl.IcePapController/second) - Motor Python ctrl (WaterPapCtrl.py)")
        
#
# Creating the controller without defining its MaxDevice property is an error
#

        self.wrong_argument(self.pool,"CreateController",["Motor","FirePapCtrl.py","FirePapController","third"],"Pool_MissingPropertyValue")
        db = PyTango.Database()
        db.put_property("FirePapController/third",{"MaxDevice":["8"]})
        self.pool.command_inout("CreateController",["Motor","FirePapCtrl.py","FirePapController","third"])
        self.pool.command_inout("DeleteController","third")

#
# Delete one controller and check controller list attribute
#
        
        self.pool.command_inout("DeleteController","second")
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,1)
        self.assertEqual(ctrl_list.value[0],"first (WaterPapCtrl.IcePapController/first) - Motor Python ctrl (WaterPapCtrl.py)")

#
# Delete an uncreated controller
#

        self.wrong_argument(self.pool,"DeleteController","Aaaa","Pool_ControllerNotFound")        
        
#
# Delete the last controller. The Controller list attribute is now empty
#
        
        self.pool.command_inout("DeleteController","first")
        self.check_empty_attribute(self.pool,"ControllerList")
        
#----------------------------------------------------------------------------------------------------------------------
            
    def CreateRem_CoTiController(self):
        """Create - Delete CounterTimer controller"""
        
#
# Create one controller
#
        
        self.pool.command_inout("CreateController",["CounterTimer","Vct6Ctrl.py","Vct6Controller","Py_Vct6"])
        
#
# Creating 2 times the same controller is an error
#
       
        self.wrong_argument(self.pool,"CreateController",["CounterTimer","Vct6Ctrl.py","Vct6Controller","Py_Vct6"],"Pool_ControllerAlreadyCreated")

#
# Create a new controller
#
        
        self.pool.command_inout("CreateController",["CounterTimer","Vct6Ctrl.py","Vct6Controller","Second_Py_Vct6"])

#
# Check controller list attribute
#
        
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,2)
        self.assertEqual(ctrl_list.value[0],"Py_Vct6 (Vct6Ctrl.Vct6Controller/Py_Vct6) - CounterTimer Python ctrl (Vct6Ctrl.py)")
        self.assertEqual(ctrl_list.value[1],"Second_Py_Vct6 (Vct6Ctrl.Vct6Controller/Second_Py_Vct6) - CounterTimer Python ctrl (Vct6Ctrl.py)")
        
#
# Delete one controller and check controller list attribute
#
        
        self.pool.command_inout("DeleteController","Second_Py_Vct6")
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,1)
        self.assertEqual(ctrl_list.value[0],"Py_Vct6 (Vct6Ctrl.Vct6Controller/Py_Vct6) - CounterTimer Python ctrl (Vct6Ctrl.py)")

#
# Delete an uncreated controller
#

        self.wrong_argument(self.pool,"DeleteController","Aaaa","Pool_ControllerNotFound")        
        
#
# Delete the last controller. The Controller list attribute is now empty
#
        
        self.pool.command_inout("DeleteController","Py_Vct6")
        self.check_empty_attribute(self.pool,"ControllerList")


#----------------------------------------------------------------------------------------------------------------------
            
    def CreateRem_ZeroDController(self):
        """Create - Delete Zero D controller"""
        
#
# Create one controller
#
        
        self.pool.command_inout("CreateController",["ZeroDExpChannel","ElecMeter.py","ElecMeterController","Py_ZeroD"])
        
#
# Creating 2 times the same controller is an error
#
       
        self.wrong_argument(self.pool,"CreateController",["ZeroDExpChannel","ElecMeter.py","ElecMeterController","Py_ZeroD"],"Pool_ControllerAlreadyCreated")

#
# Create a new controller
#
        
        self.pool.command_inout("CreateController",["ZeroDExpChannel","ElecMeter.py","ElecMeterController","Second_Py_ZeroD"])

#
# Check controller list attribute
#
        
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,2)
        self.assertEqual(ctrl_list.value[0],"Py_ZeroD (ElecMeter.ElecMeterController/Py_ZeroD) - ZeroDExpChannel Python ctrl (ElecMeter.py)")
        self.assertEqual(ctrl_list.value[1],"Second_Py_ZeroD (ElecMeter.ElecMeterController/Second_Py_ZeroD) - ZeroDExpChannel Python ctrl (ElecMeter.py)")
        
#
# Delete one controller and check controller list attribute
#
        
        self.pool.command_inout("DeleteController","Second_Py_ZeroD")
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,1)
        self.assertEqual(ctrl_list.value[0],"Py_ZeroD (ElecMeter.ElecMeterController/Py_ZeroD) - ZeroDExpChannel Python ctrl (ElecMeter.py)")

#
# Delete an uncreated controller
#

        self.wrong_argument(self.pool,"DeleteController","Aaaa","Pool_ControllerNotFound")        
        
#
# Delete the last controller. The Controller list attribute is now empty
#
        
        self.pool.command_inout("DeleteController","Py_ZeroD")
        self.check_empty_attribute(self.pool,"ControllerList")


#----------------------------------------------------------------------------------------------------------------------

    def stupidMotorArgs(self):
        """Stupid argument(s) for the CreateMotor command"""
        
        self.wrong_argument(self.pool,"CreateMotor",([1,2,3],["a","b"]),"Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool,"CreateMotor",([1],["a"]),"Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool,"CreateMotor",([1],["a","b","c"]),"Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool,"createMotor",([1],["My_motor","aaa"]),"Pool_ControllerNotFound")
        
#--------------------------------------------------------------------------------------------------------------------
        
    def CreateRem_Motor(self):
        """Create - Delete motor"""

# VALGRIND        self.pool.set_timeout_millis(15000)
               
#
# First, create two controllers
#

        self.pool.command_inout("CreateController",["Motor","WaterPapCtrl.py","IcePapController","first"])
        self.pool.command_inout("CreateController",["Motor","WaterPapCtrl.py","IcePapController","second"])
        
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,2)
        self.assertEqual(ctrl_list.value[0],"first (WaterPapCtrl.IcePapController/first) - Motor Python ctrl (WaterPapCtrl.py)")
        self.assertEqual(ctrl_list.value[1],"second (WaterPapCtrl.IcePapController/second) - Motor Python ctrl (WaterPapCtrl.py)")
                                                          
#
# Create one motor
#
        
        self.pool.command_inout("CreateMotor",([0],["First_Motor","first"]))
 
#
# Creating 2 times the same motor is an error
#
       
        self.wrong_argument(self.pool,"CreateMotor",([0],["Second_Motor","first"]),"Pool_WrongMotorName")
        self.wrong_argument(self.pool,"CreateMotor",([1],["First_Motor","first"]),"Pool_WrongMotorName")

#
# Create a new motor
#
        
        self.pool.command_inout("CreateMotor",([1],["Second_Motor","first"]))

#
# Check motor list attribute
#
        
        mot_list = self.pool.read_attribute("MotorList")
        self.assertEqual(mot_list.dim_x,2)
        self.assertEqual(mot_list.value[0],"First_Motor (motor/first/0)")
        self.assertEqual(mot_list.value[1],"Second_Motor (motor/first/1)")
        
#
# Check pool and motor state
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        mot1 = PyTango.DeviceProxy("First_Motor")
        self.assertEqual(mot1.state(),PyTango.DevState.ON)
        mot2 = PyTango.DeviceProxy("Second_Motor")
        self.assertEqual(mot2.state(),PyTango.DevState.ON)

#
# Deleting a controller with associated motor(s) is an error
#

        self.wrong_argument(self.pool,"DeleteController","first","Pool_CantDeleteController")
        
#
# Delete one motor and check motor list attribute
#
        
        self.pool.command_inout("DeleteMotor","Second_MoToR")
        mot_list = self.pool.read_attribute("MotorList")
        self.assertEqual(mot_list.dim_x,1)
        self.assertEqual(mot_list.value[0],"First_Motor (motor/first/0)")

#
# Delete an uncreated motor
#

        self.wrong_argument(self.pool,"DeleteMotor","AaAa","Pool_MotorNotFound")        
        
#
# Delete the last motor. The motor list attribute is now empty
#
        
        self.pool.command_inout("DeleteMotor","First_Motor")
        self.check_empty_attribute(self.pool,"MotorList")
        
#--------------------------------------------------------------------------------------------------------------------
        
    def CreateRem_CoTi(self):
        """Create - Delete counter/timer"""

# VALGRIND        self.pool.set_timeout_millis(15000)
               
#
# First, create two controllers
#

        self.pool.command_inout("CreateController",["CounterTimer","Vct6Ctrl.py","Vct6Controller","Py_Vct6"])
        self.pool.command_inout("CreateController",["CounterTimer","Vct6Ctrl.py","Vct6Controller","Second_Py_Vct6"])
        
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,4)
        self.assertEqual(ctrl_list.value[2],"Py_Vct6 (Vct6Ctrl.Vct6Controller/Py_Vct6) - CounterTimer Python ctrl (Vct6Ctrl.py)")
        self.assertEqual(ctrl_list.value[3],"Second_Py_Vct6 (Vct6Ctrl.Vct6Controller/Second_Py_Vct6) - CounterTimer Python ctrl (Vct6Ctrl.py)")
                                                          
#
# Create one Counter Timer
#
        
        self.pool.command_inout("CreateExpChannel",([0],["First_CT","Py_Vct6"]))
 
#
# Creating 2 times the same CT is an error
#
       
        self.wrong_argument(self.pool,"CreateExpChannel",([0],["Second_CT","Py_Vct6"]),"Pool_WrongExpChannelName")
        self.wrong_argument(self.pool,"CreateExpChannel",([1],["First_CT","Py_Vct6"]),"Pool_WrongExpChannelName")
        
#
# Create a new counter timer
#
        
        self.pool.command_inout("CreateExpChannel",([1],["Second_CT","Py_Vct6"]))

#
# Check exp channel list attribute
#
        
        chan_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(chan_list.dim_x,2)
        self.assertEqual(chan_list.value[0],"First_CT (expchan/py_vct6/0) Counter/Timer Experiment Channel")
        self.assertEqual(chan_list.value[1],"Second_CT (expchan/py_vct6/1) Counter/Timer Experiment Channel")
        
#
# Check pool and experiment channel state
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        chan1 = PyTango.DeviceProxy("First_CT")
        self.assertEqual(chan1.state(),PyTango.DevState.ON)
        chan2 = PyTango.DeviceProxy("Second_CT")
        self.assertEqual(chan2.state(),PyTango.DevState.ON)

#
# Deleting a controller with associated channel(s) is an error
#

        self.wrong_argument(self.pool,"DeleteController","Py_Vct6","Pool_CantDeleteController")
        
#
# Delete one channel and check motor list attribute
#
        
        self.pool.command_inout("DeleteExpChannel","Second_ct")
        chan_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(chan_list.dim_x,1)
        self.assertEqual(chan_list.value[0],"First_CT (expchan/py_vct6/0) Counter/Timer Experiment Channel")

#
# Delete an uncreated channel
#

        self.wrong_argument(self.pool,"DeleteExpChannel","AaAa","Pool_ExpChannelNotFound")        
        
#
# Delete the last channel. The channel list attribute is now empty
#
        
        self.pool.command_inout("DeleteExpChannel","First_CT")
        self.check_empty_attribute(self.pool,"ExpChannelList")
        
#--------------------------------------------------------------------------------------------------------------------
        
    def CreateRem_ZeroD(self):
        """Create - Delete Zero D Experiment Channel"""

# VALGRIND        self.pool.set_timeout_millis(15000)
               
#
# First, create two controllers
#

        self.pool.command_inout("CreateController",["ZeroDExpChannel","DummyZeroDCtrl.so","DummyZeroDController","Cpp_ZeroD"])
        self.pool.command_inout("CreateController",["ZeroDExpChannel","DummyZeroDCtrl.so","DummyZeroDController","Second_Cpp_ZeroD"])
        
        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,6)
        self.assertEqual(ctrl_list.value[4],"Cpp_ZeroD (DummyZeroDCtrl.DummyZeroDController/Cpp_ZeroD) - ZeroDExpChannel Cpp ctrl (DummyZeroDCtrl.so)")
        self.assertEqual(ctrl_list.value[5],"Second_Cpp_ZeroD (DummyZeroDCtrl.DummyZeroDController/Second_Cpp_ZeroD) - ZeroDExpChannel Cpp ctrl (DummyZeroDCtrl.so)")
                                                          
#
# Create one Zero D Exp Channel
#
        
        self.pool.command_inout("CreateExpChannel",([0],["First_ZeroD","Cpp_ZeroD"]))
 
#
# Creating 2 times the same Zero D Exp Channel is an error
#
       
        self.wrong_argument(self.pool,"CreateExpChannel",([0],["Second_ZeroD","Cpp_ZeroD"]),"Pool_WrongExpChannelName")
        self.wrong_argument(self.pool,"CreateExpChannel",([1],["First_ZeroD","Cpp_ZeroD"]),"Pool_WrongExpChannelName")
        
#
# Create a new Zero D exp channel
#
        
        self.pool.command_inout("CreateExpChannel",([1],["Second_ZeroD","Cpp_ZeroD"]))

#
# Check exp channel list attribute
#
        
        chan_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(chan_list.dim_x,2)
        self.assertEqual(chan_list.value[0],"First_ZeroD (expchan/cpp_zerod/0) Zero D Experiment Channel")
        self.assertEqual(chan_list.value[1],"Second_ZeroD (expchan/cpp_zerod/1) Zero D Experiment Channel")
        
#
# Check pool and experiment channel state
#

        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        chan1 = PyTango.DeviceProxy("First_ZeroD")
        self.assertEqual(chan1.state(),PyTango.DevState.ON)
        chan2 = PyTango.DeviceProxy("Second_ZeroD")
        self.assertEqual(chan2.state(),PyTango.DevState.ON)

#
# Deleting a controller with associated channel(s) is an error
#

        self.wrong_argument(self.pool,"DeleteController","Cpp_ZeroD","Pool_CantDeleteController")
        
#
# Delete one channel and check channel list attribute
#
        
        self.pool.command_inout("DeleteExpChannel","Second_zerod")
        chan_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(chan_list.dim_x,1)
        self.assertEqual(chan_list.value[0],"First_ZeroD (expchan/cpp_zerod/0) Zero D Experiment Channel")

#
# Delete an uncreated channel
#

        self.wrong_argument(self.pool,"DeleteExpChannel","AaAa","Pool_ExpChannelNotFound")        
        
#
# Delete the last channel. The channel list attribute is now empty
#
        
        self.pool.command_inout("DeleteExpChannel","First_zeroD")
        self.check_empty_attribute(self.pool,"ExpChannelList")


#----------------------------------------------------------------------------------------------------------------------

    def Init_Pool(self):
        """Init command on pool device"""
        
#
# First, we create two motors
#

        self.pool.command_inout("CreateMotor",([0],["First_Motor","second"]))
        self.pool.command_inout("CreateMotor",([1],["Second_Motor","second"]))

        mot_list = self.pool.read_attribute("MotorList")
        self.assertEqual(mot_list.dim_x,2)
        self.assertEqual(mot_list.value[0],"First_Motor (motor/second/0)")
        self.assertEqual(mot_list.value[1],"Second_Motor (motor/second/1)")
        
#
# Now, we create a group
#

        self.pool.command_inout("CreateMotorGroup",["The_grp","Second_Motor","First_Motor"])
        
        grp_list = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(grp_list.dim_x,1)
        self.assertEqual(grp_list.value[0],"The_grp (mg/test/The_grp) Motor list: Second_Motor, First_Motor")
        
        self.grp_dev = PyTango.DeviceProxy("The_grp")
        self.grp_dev.state()
        
#
# We also create a Counter Timer
#

        self.pool.command_inout("CreateExpChannel",([0],["First_CT","Py_Vct6"]))
        
        ct_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(ct_list.dim_x,1)
        self.assertEqual(ct_list.value[0],"First_CT (expchan/py_vct6/0) Counter/Timer Experiment Channel")
        
#
# We also create a Zero D Exp Channel
#

        self.pool.command_inout("CreateExpChannel",([2],["First_ZeroD","Cpp_ZeroD"]))
        
        zero_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(zero_list.dim_x,2)
        self.assertEqual(zero_list.value[1],"First_ZeroD (expchan/cpp_zerod/2) Zero D Experiment Channel")
        
#
# Send the init command
#

        self.pool.command_inout("Init")
        
#
# Check that everything is like before the Init command
#

        ctrl_list = self.pool.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,6)
        self.assertEqual(ctrl_list.value[0],"first (WaterPapCtrl.IcePapController/first) - Motor Python ctrl (WaterPapCtrl.py)")
        self.assertEqual(ctrl_list.value[1],"second (WaterPapCtrl.IcePapController/second) - Motor Python ctrl (WaterPapCtrl.py)")
        self.assertEqual(ctrl_list.value[2],"Py_Vct6 (Vct6Ctrl.Vct6Controller/Py_Vct6) - CounterTimer Python ctrl (Vct6Ctrl.py)")
        self.assertEqual(ctrl_list.value[3],"Second_Py_Vct6 (Vct6Ctrl.Vct6Controller/Second_Py_Vct6) - CounterTimer Python ctrl (Vct6Ctrl.py)")
        self.assertEqual(ctrl_list.value[4],"Cpp_ZeroD (DummyZeroDCtrl.DummyZeroDController/Cpp_ZeroD) - ZeroDExpChannel Cpp ctrl (DummyZeroDCtrl.so)")
        self.assertEqual(ctrl_list.value[5],"Second_Cpp_ZeroD (DummyZeroDCtrl.DummyZeroDController/Second_Cpp_ZeroD) - ZeroDExpChannel Cpp ctrl (DummyZeroDCtrl.so)")
                
        mot_list = self.pool.read_attribute("MotorList")
        self.assertEqual(mot_list.dim_x,2)
        self.assertEqual(mot_list.value[0],"First_Motor (motor/second/0)")
        self.assertEqual(mot_list.value[1],"Second_Motor (motor/second/1)")

        self.assertEqual(self.pool.state(),PyTango.DevState.ON)
        mot1 = PyTango.DeviceProxy("First_Motor")
        self.assertEqual(mot1.state(),PyTango.DevState.ON)
        mot2 = PyTango.DeviceProxy("Second_Motor")
        self.assertEqual(mot2.state(),PyTango.DevState.ON)

        grp_list = self.pool.read_attribute("MotorGroupList")
        self.assertEqual(grp_list.dim_x,1)
        self.assertEqual(grp_list.value[0],"The_grp (mg/test/The_grp) Motor list: Second_Motor, First_Motor")
        
        chan_list = self.pool.read_attribute("ExpChannelList")
        self.assertEqual(chan_list.dim_x,2)
        self.assertEqual(chan_list.value[0],"First_CT (expchan/py_vct6/0) Counter/Timer Experiment Channel")
        self.assertEqual(chan_list.value[1],"First_ZeroD (expchan/cpp_zerod/2) Zero D Experiment Channel")

#
# Delete the group, the motors, the exp channel and the controllers
#                

        self.pool.command_inout("DeleteMotorGroup","The_grp")
        self.pool.command_inout("DeleteMotor","First_Motor")
        self.pool.command_inout("DeleteMotor","Second_Motor")
        self.pool.command_inout("DeleteController","first")
        self.pool.command_inout("DeleteController","second")
        self.pool.command_inout("DeleteExpChannel","First_CT")
        self.pool.command_inout("DeleteController","Py_Vct6")
        self.pool.command_inout("DeleteExpChannel","First_ZeroD")
        self.pool.command_inout("DeleteController","Cpp_zerod")
        
#---------------------------------------------------------------------------------------------------------------------- 


    def MaxMotor(self):
        """MaxDevice controller property management"""

#
# Set a by controller instance property
#

        db = PyTango.Database()
        db.put_property("FirePapController/Max",{"MaxDevice":["2"]})
        
#
# Create the controller
#

        self.pool.command_inout("CreateController",["Motor","FirePapCtrl.py","FirePapController","Max"])
        
#
# Create 2 motors
#

        self.pool.command_inout("CreateMotor",([0],["Mot1","Max"]))
        self.pool.command_inout("CreateMotor",([1],["Mot2","Max"]))
        
#
# Create a third motor should fail
#

        self.wrong_argument(self.pool,"CreateMotor",([2],["Mot3","Max"]),"Pool_MaxNbMotorInCtrl")
        
#
# remove motors and controller
#

        self.pool.command_inout("DeleteMotor","Mot1")
        self.pool.command_inout("DeleteMotor","Mot2")
        self.pool.command_inout("DeleteController","Max")
        
#
# Remove property from db
#

        db.delete_property("FirePapCtrl.FirePapController/Max",["MaxMotor"])
               
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------     

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
    PoolTestUtil.start_test(runner,TestPool,dev_name,"emptypool")
    PoolTestUtil.start_test(runner,TestPool,dev_name,"stupidArgs")
    PoolTestUtil.start_test(runner,TestPool,dev_name,"CreateRem_Controller")
    PoolTestUtil.start_test(runner,TestPool,dev_name,"CreateRem_CoTiController")
    PoolTestUtil.start_test(runner,TestPool,dev_name,"CreateRem_ZeroDController")
    PoolTestUtil.start_test(runner,TestPool,dev_name,"stupidMotorArgs")
    PoolTestUtil.start_test(runner,TestPool,dev_name,"CreateRem_Motor")
    PoolTestUtil.start_test(runner,TestPool,dev_name,"CreateRem_CoTi")
    PoolTestUtil.start_test(runner,TestPool,dev_name,"CreateRem_ZeroD")
    PoolTestUtil.start_test(runner,TestPool,dev_name,"Init_Pool")
    PoolTestUtil.start_test(runner,TestPool,dev_name,"CtrlClasslist")
    PoolTestUtil.start_test(runner,TestPool,dev_name,"MaxMotor")
    

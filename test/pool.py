"""
  Pool Test cases like start, stop and kill the device server, checking for
  emptyness, checking creation of elements with wrong arguments 
"""

import os
from taurus.external import unittest
import poolunittest
import HTMLTestRunner
import time
import PyTango

class EmptyPoolTestCase(poolunittest.PoolTestCase):
    """Start, Stop, Kill and check emptyness of Device Pool"""
    
    EmptyStartStopStates = [PyTango.DevState.ON, PyTango.DevState.UNKNOWN]
      
    def setUp(self):
        poolunittest.PoolTestCase.setUp(self)
        self.pool_state_cb = poolunittest.DefaultTangoEventCallBack()
        self.pool_state_cb_id = self.pool_dp.subscribe_event("state",
                                                             PyTango.EventType.CHANGE,
                                                             self.pool_state_cb,[])
        
    def tearDown(self):
        if not self.pool_state_cb_id is None:
            try:
                self.pool_dp.unsubscribe_event(self.pool_state_cb_id)
                self.pool_state_cb_id = None
            except:
                pass
        self.pool_state_cb = None
        poolunittest.PoolTestCase.tearDown(self)
            
    def testStartStopWithKill(self):
        """Start & stop(kill) an empty Device Pool"""
        
        # Pool was started by setUp
        
        self.assertEqual(self.pool_dp.state(), PyTango.DevState.ON)
        
        self.stopPool()

        evt_values = self.pool_state_cb.getEventValues()
        self.assertEqual(evt_values, self.EmptyStartStopStates,
                         "State Event list(%s) does not match expected" % evt_values)
         
    def testStartStopWithAdminKill(self):
        """Start & stop(admin device kill) an empty Device Pool"""
        
        # Pool was started by setUp
        
        self.assertEqual(self.pool_dp.state(), PyTango.DevState.ON)
        
        self.pool_admin_dp = PyTango.DeviceProxy("dserver/Pool/%s" % self.pool_ds_instance)
        
        self.pool_admin_dp.command_inout("Kill")
        
        self.waitPoolStop()
        
        evt_values = self.pool_state_cb.getEventValues()
        self.assertEqual(evt_values, self.EmptyStartStopStates,
                         "State Event list(%s) does not match expected" % evt_values)
    
    def testPing(self):
        """Empty Device Pool ping()"""
        
        ret = self.pool_dp.ping()
        self.assert_(ret > 0, "ping returned %d" % ret)
            
        
    def testLists(self):
        """Empty pool 'XList' attributes"""
        lst_attrs = [ attr.name for attr in self.pool_dp.attribute_list_query_ex() 
                      if attr.name.endswith('List') and attr.name.find("ControllerClass") == -1 ]

        for attr in lst_attrs:
            self.check_empty_attribute(self.pool_dp, attr)


class ControllerTestCase(poolunittest.PoolTestCase):
    """Test ControllerClassList, wrong controller creation"""
    
    def testCtrlClasslist(self):
        """ControllerClassList attribute"""
        
        ctrls = self.pool_dp.read_attribute("ControllerClasslist")
        
        v = ctrls.value
        
        len_v = len(v)
        
        self.assertNotEqual(len_v,0,"Controller class list is empty")

        self.assert_(len_v>=13,"Insufficient number of Controller classes found." \
                     "Found %d. Should have at least 5")

        pool_path = self.getPoolPath()
        test_path = pool_path[1]
        cpp_path = pool_path[2]
        py_path = pool_path[3]
        
        ctrl = "Type: Motor - Class: SimuMotorController - File: %s/SimuMotorCtrl.la" % cpp_path
        self.assert_(ctrl in v, "SimuMotor controller not found")
        
        ctrl = "Type: CounterTimer - Class: UnixTimer - File: %s/UxTimerCtrl.la" % cpp_path
        self.assert_(ctrl in v, "Unix Timer controller not found")
        
        ctrl = "Type: CounterTimer - Class: SimuCoTiController - File: %s/SimuCTCtrl.py" % py_path
        self.assert_(ctrl in v, "SimuCoTi controller not found")
                
        ctrl = "Type: ZeroDExpChannel - Class: SimuZeroDController - File: %s/SimuZeroDCtrl.la" % cpp_path
        self.assert_(ctrl in v, "Simu0D controller not found")

        ctrl = "Type: PseudoMotor - Class: Slit - File: %s/PseudoMotorLib.py" % py_path
        self.assert_(ctrl in v, "Pseudo Motor controller not found")
        
        ctrl = "Type: Communication - Class: DummyCommunicationController - File: %s/DummyCommunicationController.py" % py_path
        self.assert_(ctrl in v, "DummyCommunication controller not found")
        
        ctrl = "Type: Motor - Class: FirePapController - File: %s/FirePapCtrl.py" % test_path
        self.assert_(ctrl in v, "FirePap controller not found")

        ctrl = "Type: Motor - Class: IcePapController - File: %s/WaterPapCtrl.py" % test_path
        self.assert_(ctrl in v, "IcePap controller not found")

        ctrl = "Type: Motor - Class: IcePapController - File: %s/WaterPapCtrl_init.py" % test_path
        self.assert_(ctrl in v, "IcePap controller not found")
        
        ctrl = "Type: Motor - Class: IcePapController - File: %s/WaterPapCtrl_mis_extra.py" % test_path
        self.assert_(ctrl in v, "IcePap controller not found")
        
        ctrl = "Type: Motor - Class: IcePapController - File: %s/WaterPapCtrl_mis_feat.py" % test_path
        self.assert_(ctrl in v, "IcePap controller not found")
        
        ctrl = "Type: Motor - Class: IcePapController - File: %s/WaterPapCtrl_prop.py" % test_path
        self.assert_(ctrl in v, "IcePap controller not found")
        
        ctrl = "Type: Motor - Class: IcePapController - File: %s/WaterPapCtrl_stat1.py" % test_path
        self.assert_(ctrl in v, "IcePap controller not found")
        
        ctrl = "Type: Motor - Class: IcePapController - File: %s/WaterPapCtrl_stat2.py" % test_path
        self.assert_(ctrl in v, "IcePap controller not found")
        
        ctrl = "Type: ZeroDExpChannel - Class: ElecMeterController - File: %s/ElecMeter.py" % test_path
        self.assert_(ctrl in v, "ElecMeter controller not found")
        
        ctrl = "Type: ZeroDExpChannel - Class: ElecMeterController - File: %s/ElecMeter_init.py" % test_path
        self.assert_(ctrl in v, "ElecMeter controller not found")


class MotorControllerTestCase(poolunittest.PoolTestCase):
    """Test motor controller creation, deletion, listing"""

    def needsMotorSimulator(self):
        return True
    
    def testCreateMotorControllerWrongArguments(self):
        """Create Motor controller with wrong arguments"""
        
        p = self.pool_dp 
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["a","b","c"], "Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["Motor","a/b","ctrl","inst"], "Pool_FileUnsupportedType")
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["Motor","a/b.truc","ctrl","inst"], "Pool_FileUnsupportedType")
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["Motor","a","b","x"], "Pool_FileUnsupportedType")
        
        self.wrong_argument(self.pool_dp,"CreateController",
                            ["Motor","a.py","b","x"], "Pool_ControllerNotFound")
        self.wrong_argument(self.pool_dp,"CreateController",
                            ["Motor","a.la","b","x"], "Pool_ControllerNotFound")

        self.wrong_argument(self.pool_dp,"CreateController",
                            ["Motor","WaterPapCtrl.py","b","x"],
                            "Pool_CantLocatePythonClass")
        self.wrong_argument(self.pool_dp,"CreateController",
                            ["Motor","WaterPapCtrl_mis.py","IcePapController","x"],
                            "Pool_PythonMethodNotFound")    
        
        self.wrong_argument(p,"CreateController",
                            ["Motor","FirePapCtrl.py","FirePapController","third"],
                            "Pool_MissingPropertyValue")
    
    def testCreateDeleteMotorController(self):
        """Create/Delete Motor controller"""
        
        p = self.pool_dp 
        p.command_inout("CreateController",
                        ["Motor","WaterPapCtrl.py","IcePapController","first_mot_ctrl"])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x,1)
        self.assertEqual(ctrl_list.value[0],
                         "first_mot_ctrl (WaterPapCtrl.IcePapController/first_mot_ctrl) - Motor Python ctrl (WaterPapCtrl.py)")

        p.command_inout("DeleteController","first_mot_ctrl")
        self.check_empty_attribute(p,"ControllerList")
        
    def testDeleteInexistingMotorController(self):
        """Try to delete inexisting motor controller"""
        
        p = self.pool_dp 
        p.command_inout("CreateController",
                        ["Motor","WaterPapCtrl.py","IcePapController","first_mot_ctrl"])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x,1)
        self.assertEqual(ctrl_list.value[0],
                         "first_mot_ctrl (WaterPapCtrl.IcePapController/first_mot_ctrl) - Motor Python ctrl (WaterPapCtrl.py)")
        
        self.wrong_argument(p,"DeleteController","Aaaa","Pool_ControllerNotFound")
        
        p.command_inout("DeleteController","first_mot_ctrl")
        self.check_empty_attribute(p,"ControllerList")

    def testDeleteMotorControllerWithMotors(self):
        """Try to delete a motor controller with motors"""
        
        p = self.pool_dp 
        p.command_inout("CreateController",
                        ["Motor","WaterPapCtrl.py","IcePapController","first_mot_ctrl"])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x,1)
        self.assertEqual(ctrl_list.value[0],
                         "first_mot_ctrl (WaterPapCtrl.IcePapController/first_mot_ctrl) - Motor Python ctrl (WaterPapCtrl.py)")
        
        p.command_inout("CreateMotor", ([0], ["first_mot","first_mot_ctrl"]))
        
        self.wrong_argument(p, "DeleteController", "first_mot_ctrl", 
                            "Pool_CantDeleteController")
        
        p.command_inout("DeleteMotor","first_mot")
        
        p.command_inout("DeleteController","first_mot_ctrl")
        self.check_empty_attribute(p,"ControllerList")

    def testCreateSameMotorControllerTwice(self):
        """Try to create same motor controller twice"""
        
        p = self.pool_dp 
        p.command_inout("CreateController",
                        ["Motor","WaterPapCtrl.py","IcePapController","first_mot_ctrl"])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x,1)
        self.assertEqual(ctrl_list.value[0],
                         "first_mot_ctrl (WaterPapCtrl.IcePapController/first_mot_ctrl) - Motor Python ctrl (WaterPapCtrl.py)")
        
        self.wrong_argument(p, "CreateController",
                            ["Motor","WaterPapCtrl.py","IcePapController","first_mot_ctrl"],
                            "Pool_ControllerAlreadyCreated")

        p.command_inout("DeleteController","first_mot_ctrl")
        self.check_empty_attribute(p,"ControllerList")

    def testCreateDeleteTwoMotorControllers(self):
        """Create/Delete two motor controllers"""
        
        p = self.pool_dp 
        p.command_inout("CreateController",
                        ["Motor","WaterPapCtrl.py","IcePapController","first_mot_ctrl"])
        p.command_inout("CreateController",
                        ["Motor","WaterPapCtrl.py","IcePapController","second_mot_ctrl"])

        # Check controller list attribute
        ctrl_list = p.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,2)
        self.assertEqual(ctrl_list.value[0],
                         "first_mot_ctrl (WaterPapCtrl.IcePapController/first_mot_ctrl) - Motor Python ctrl (WaterPapCtrl.py)")
        self.assertEqual(ctrl_list.value[1],
                         "second_mot_ctrl (WaterPapCtrl.IcePapController/second_mot_ctrl) - Motor Python ctrl (WaterPapCtrl.py)")

        # Delete one controller and check controller list attribute
        p.command_inout("DeleteController","second_mot_ctrl")
        ctrl_list = p.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,1)
        self.assertEqual(ctrl_list.value[0],
                         "first_mot_ctrl (WaterPapCtrl.IcePapController/first_mot_ctrl) - Motor Python ctrl (WaterPapCtrl.py)")

        p.command_inout("DeleteController","first_mot_ctrl")
        self.check_empty_attribute(p,"ControllerList")
        
    def testCreateMotorControllersWithMaxDevice(self):
        """Create a motor controller defining its mandatory MaxDevice property """
        
        p = self.pool_dp 
        p.command_inout("CreateController",
                        ["Motor","FirePapCtrl.py","FirePapController",
                         "third","MaxDevice","8"])
        p.command_inout("DeleteController","third")
        self.check_empty_attribute(p,"ControllerList")
        
        
class CounterTimerControllerTestCase(poolunittest.PoolTestCase):
    """Test CounterTimer controller creation, deletion, listing"""
    
    # The CounterTimer simulator needs the motor simulator to work so the motor
    # simulator becomes a requirement
    def needsMotorSimulator(self):
        return True
    
    def needsCounterTimerSimulator(self):
        return True
    
    def testCreateCounterTimerControllerWrongArguments(self):
        """Create CounterTimer controller with wrong arguments"""
        
        p = self.pool_dp 
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["a","b","c"], "Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["CounterTimer","a/b","ctrl","inst"], "Pool_FileUnsupportedType")
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["CounterTimer","a/b.truc","ctrl","inst"], "Pool_FileUnsupportedType")
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["CounterTimer","a","b","x"], "Pool_FileUnsupportedType")
        
        self.wrong_argument(self.pool_dp,"CreateController",
                            ["CounterTimer","a.py","b","x"], "Pool_ControllerNotFound")
        self.wrong_argument(self.pool_dp,"CreateController",
                            ["CounterTimer","a.la","b","x"], "Pool_ControllerNotFound")

        self.wrong_argument(self.pool_dp,"CreateController",
                            ["CounterTimer","Vct6Ctrl.py","b","x"],
                            "Pool_CantLocatePythonClass")
    
        self.wrong_argument(p,"CreateController",
                            ["CounterTimer","Vct6Ctrl.py","Vct6Controller",
                             "first_ct_ctrl"],
                            "Pool_MissingPropertyValue")    
    
    def testCreateDeleteCounterTimerController(self):
        """Create/Delete CounterTimer controller"""
        
        p = self.pool_dp 
        p.command_inout("CreateController",
                        ["CounterTimer", "Vct6Ctrl.py", "Vct6Controller",
                         "first_ct_ctrl", "CtrlDevName", 
                         self.ctsim_ctrl_dev_name])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_ct_ctrl (Vct6Ctrl.Vct6Controller/first_ct_ctrl) - CounterTimer Python ctrl (Vct6Ctrl.py)")

        p.command_inout("DeleteController", "first_ct_ctrl")
        self.check_empty_attribute(p, "ControllerList")
        
    def testDeleteInexistingCounterTimerController(self):
        """Try to delete inexisting CounterTimer controller"""
        
        p = self.pool_dp 
        p.command_inout("CreateController",
                        ["CounterTimer", "Vct6Ctrl.py", "Vct6Controller",
                         "first_ct_ctrl", "CtrlDevName",
                         self.ctsim_ctrl_dev_name])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_ct_ctrl (Vct6Ctrl.Vct6Controller/first_ct_ctrl) - CounterTimer Python ctrl (Vct6Ctrl.py)")
        
        self.wrong_argument(p,"DeleteController", "Aaaa", 
                            "Pool_ControllerNotFound")
        
        p.command_inout("DeleteController", "first_ct_ctrl")
        self.check_empty_attribute(p, "ControllerList")

    def testDeleteCounterTimerControllerWithCounters(self):
        """Try to delete a CounterTimer controller with counters"""
        
        p = self.pool_dp 
        p.command_inout("CreateController",
                        ["CounterTimer", "Vct6Ctrl.py", "Vct6Controller",
                         "first_ct_ctrl", "CtrlDevName",
                         self.ctsim_ctrl_dev_name])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x,1)
        self.assertEqual(ctrl_list.value[0],
                         "first_ct_ctrl (Vct6Ctrl.Vct6Controller/first_ct_ctrl) - CounterTimer Python ctrl (Vct6Ctrl.py)")
        
        p.command_inout("CreateExpChannel", ([0], ["first_ct","first_ct_ctrl"]))
        
        self.wrong_argument(p, "DeleteController", "first_ct_ctrl", 
                            "Pool_CantDeleteController")
        
        p.command_inout("DeleteExpChannel", "first_ct")
        
        p.command_inout("DeleteController", "first_ct_ctrl")
        self.check_empty_attribute(p, "ControllerList")
        
    def testCreateSameCounterTimerControllerTwice(self):
        """Try to create same CounterTimer controller twice"""

        p = self.pool_dp 
        p.command_inout("CreateController",
                        ["CounterTimer", "Vct6Ctrl.py", "Vct6Controller",
                         "first_ct_ctrl", "CtrlDevName",
                         self.ctsim_ctrl_dev_name])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_ct_ctrl (Vct6Ctrl.Vct6Controller/first_ct_ctrl) - CounterTimer Python ctrl (Vct6Ctrl.py)")
        
        self.wrong_argument(p,"CreateController",
                            ["CounterTimer", "Vct6Ctrl.py", "Vct6Controller",
                             "first_ct_ctrl", "CtrlDevName",
                             self.ctsim_ctrl_dev_name],
                             "Pool_ControllerAlreadyCreated")

        p.command_inout("DeleteController", "first_ct_ctrl")
        self.check_empty_attribute(p, "ControllerList")

    def testCreateDeleteTwoCounterTimerControllers(self):
        """Create/Delete two CounterTimer controllers"""
        
        p = self.pool_dp 
        p.command_inout("CreateController",
                        ["CounterTimer", "Vct6Ctrl.py", "Vct6Controller",
                         "first_ct_ctrl", "CtrlDevName",
                         self.ctsim_ctrl_dev_name])
        p.command_inout("CreateController",
                        ["CounterTimer", "Vct6Ctrl.py", "Vct6Controller",
                         "second_ct_ctrl", "CtrlDevName",
                         self.ctsim_ctrl_dev_name])

        # Check controller list attribute
        ctrl_list = p.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x, 2)
        self.assertEqual(ctrl_list.value[0],
                         "first_ct_ctrl (Vct6Ctrl.Vct6Controller/first_ct_ctrl) - CounterTimer Python ctrl (Vct6Ctrl.py)")
        self.assertEqual(ctrl_list.value[1],
                         "second_ct_ctrl (Vct6Ctrl.Vct6Controller/second_ct_ctrl) - CounterTimer Python ctrl (Vct6Ctrl.py)")

        # Delete one controller and check controller list attribute
        p.command_inout("DeleteController", "second_ct_ctrl")
        ctrl_list = p.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_ct_ctrl (Vct6Ctrl.Vct6Controller/first_ct_ctrl) - CounterTimer Python ctrl (Vct6Ctrl.py)")

        self.pool_dp.command_inout("DeleteController", "first_ct_ctrl")
        self.check_empty_attribute(p, "ControllerList")


class ZeroDControllerTestCase(poolunittest.PoolTestCase):
    """Test 0D controller creation, deletion, listing"""
    
    def testCreate0DControllerWrongArguments(self):
        """Create 0D controller with wrong arguments"""
        
        p = self.pool_dp 
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["a","b","c"], "Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["ZeroDExpChannel","a/b","ctrl","inst"], "Pool_FileUnsupportedType")
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["ZeroDExpChannel","a/b.truc","ctrl","inst"], "Pool_FileUnsupportedType")
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["ZeroDExpChannel","a","b","x"], "Pool_FileUnsupportedType")
        
        self.wrong_argument(self.pool_dp,"CreateController",
                            ["ZeroDExpChannel","a.py","b","x"], "Pool_ControllerNotFound")
        self.wrong_argument(self.pool_dp,"CreateController",
                            ["ZeroDExpChannel","a.la","b","x"], "Pool_ControllerNotFound")

        self.wrong_argument(self.pool_dp,"CreateController",
                            ["ZeroDExpChannel","ElecMeter.py","b","x"],
                            "Pool_CantLocatePythonClass")
    
    def testCreateDelete0DController(self):
        """Create/Delete 0D controller"""
        
        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["ZeroDExpChannel", "ElecMeter.py",
                         "ElecMeterController", "first_0d_ctrl"])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_0d_ctrl (ElecMeter.ElecMeterController/first_0d_ctrl) - ZeroDExpChannel Python ctrl (ElecMeter.py)")

        p.command_inout("DeleteController", "first_0d_ctrl")
        self.check_empty_attribute(p, "ControllerList")
        
    def testDeleteInexisting0DController(self):
        """Try to delete inexisting 0D controller"""
        
        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["ZeroDExpChannel", "ElecMeter.py",
                         "ElecMeterController", "first_0d_ctrl"])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_0d_ctrl (ElecMeter.ElecMeterController/first_0d_ctrl) - ZeroDExpChannel Python ctrl (ElecMeter.py)")
        
        self.wrong_argument(p, "DeleteController", "Aaaa", 
                            "Pool_ControllerNotFound")
        
        p.command_inout("DeleteController", "first_0d_ctrl")
        self.check_empty_attribute(p, "ControllerList")

    def testDelete0DControllerWithChannels(self):
        """Try to delete a 0D controller with channels"""
        
        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["ZeroDExpChannel", "ElecMeter.py",
                         "ElecMeterController", "first_0d_ctrl"])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_0d_ctrl (ElecMeter.ElecMeterController/first_0d_ctrl) - ZeroDExpChannel Python ctrl (ElecMeter.py)")
        
        p.command_inout("CreateExpChannel", ([0], ["first_0d","first_0d_ctrl"]))
        
        self.wrong_argument(p, "DeleteController", "first_0d_ctrl", 
                            "Pool_CantDeleteController")
        
        p.command_inout("DeleteExpChannel","first_0d")
        
        p.command_inout("DeleteController", "first_0d_ctrl")
        self.check_empty_attribute(p, "ControllerList")
        
    def testCreateSame0DControllerTwice(self):
        """Try create same 0D controller twice"""

        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["ZeroDExpChannel", "ElecMeter.py",
                         "ElecMeterController", "first_0d_ctrl"])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_0d_ctrl (ElecMeter.ElecMeterController/first_0d_ctrl) - ZeroDExpChannel Python ctrl (ElecMeter.py)")

        self.wrong_argument(p, "CreateController",
                            ["ZeroDExpChannel", "ElecMeter.py", 
                             "ElecMeterController", "first_0d_ctrl"],
                            "Pool_ControllerAlreadyCreated")

        p.command_inout("DeleteController", "first_0d_ctrl")
        self.check_empty_attribute(p, "ControllerList")

    def testCreateDeleteTwo0DControllers(self):
        """Create/Delete two 0D controllers"""
        
        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["ZeroDExpChannel", "ElecMeter.py",
                         "ElecMeterController", "first_0d_ctrl"])
        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["ZeroDExpChannel", "ElecMeter.py",
                         "ElecMeterController", "second_0d_ctrl"])

        # Check controller list attribute
        ctrl_list = p.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x, 2)
        self.assertEqual(ctrl_list.value[0],
                         "first_0d_ctrl (ElecMeter.ElecMeterController/first_0d_ctrl) - ZeroDExpChannel Python ctrl (ElecMeter.py)")
        self.assertEqual(ctrl_list.value[1],
                         "second_0d_ctrl (ElecMeter.ElecMeterController/second_0d_ctrl) - ZeroDExpChannel Python ctrl (ElecMeter.py)")

        # Delete one controller and check controller list attribute
        p.command_inout("DeleteController", "second_0d_ctrl")
        ctrl_list = p.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_0d_ctrl (ElecMeter.ElecMeterController/first_0d_ctrl) - ZeroDExpChannel Python ctrl (ElecMeter.py)")

        self.pool_dp.command_inout("DeleteController", "first_0d_ctrl")
        self.check_empty_attribute(p, "ControllerList")


class CommunicationControllerTestCase(poolunittest.PoolTestCase):
    """Test communication controller creation, deletion, listing"""
    
    def testCreateCommunicationControllerWrongArguments(self):
        """Create Communication controller with wrong arguments"""
        
        p = self.pool_dp 
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["a","b","c"], "Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["Communication","a/b","ctrl","inst"], "Pool_FileUnsupportedType")
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["Communication","a/b.truc","ctrl","inst"], "Pool_FileUnsupportedType")
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["Communication","a","b","x"], "Pool_FileUnsupportedType")
        
        self.wrong_argument(self.pool_dp,"CreateController",
                            ["Communication","a.py","b","x"], "Pool_ControllerNotFound")
        self.wrong_argument(self.pool_dp,"CreateController",
                            ["Communication","a.la","b","x"], "Pool_ControllerNotFound")

        self.wrong_argument(self.pool_dp,"CreateController",
                            ["Communication","DummyCommunicationController.py","b","x"],
                            "Pool_CantLocatePythonClass")    
    
    def testCreateDeleteCommunicationController(self):
        """Create/Delete Communication controller"""
        
        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["Communication", "DummyCommunicationController.py",
                         "DummyCommunicationController", "first_com_ctrl"])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_com_ctrl (DummyCommunicationController.DummyCommunicationController/first_com_ctrl) - Communication Python ctrl (DummyCommunicationController.py)")

        p.command_inout("DeleteController", "first_com_ctrl")
        self.check_empty_attribute(p, "ControllerList")
        
    def testDeleteInexistingCommunicationController(self):
        """Try to delete inexisting Communication controller"""
        
        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["Communication", "DummyCommunicationController.py",
                         "DummyCommunicationController", "first_com_ctrl"])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_com_ctrl (DummyCommunicationController.DummyCommunicationController/first_com_ctrl) - Communication Python ctrl (DummyCommunicationController.py)")
        
        self.wrong_argument(p, "DeleteController", "Aaaa", 
                            "Pool_ControllerNotFound")
        
        p.command_inout("DeleteController", "first_com_ctrl")
        self.check_empty_attribute(p, "ControllerList")

    def testDeleteCommunicationControllerWithChannels(self):
        """Try to delete a Communication controller with channels"""
        
        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["Communication", "DummyCommunicationController.py",
                         "DummyCommunicationController", "first_com_ctrl"])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_com_ctrl (DummyCommunicationController.DummyCommunicationController/first_com_ctrl) - Communication Python ctrl (DummyCommunicationController.py)")
        
        p.command_inout("CreateComChannel", ([0], ["first_comch","first_com_ctrl"]))
        
        self.wrong_argument(p, "DeleteController", "first_com_ctrl", 
                            "Pool_CantDeleteController")
        
        p.command_inout("DeleteComChannel","first_comch")
        
        p.command_inout("DeleteController", "first_com_ctrl")
        self.check_empty_attribute(p, "ControllerList")
        
    def testCreateSameCommunicationControllerTwice(self):
        """Try create same Communication controller twice"""

        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["Communication", "DummyCommunicationController.py",
                         "DummyCommunicationController", "first_com_ctrl"])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_com_ctrl (DummyCommunicationController.DummyCommunicationController/first_com_ctrl) - Communication Python ctrl (DummyCommunicationController.py)")

        self.wrong_argument(p, "CreateController",
                            ["Communication", "DummyCommunicationController.py", 
                             "DummyCommunicationController", "first_com_ctrl"],
                            "Pool_ControllerAlreadyCreated")

        p.command_inout("DeleteController", "first_com_ctrl")
        self.check_empty_attribute(p, "ControllerList")

    def testCreateDeleteTwoCommunicationControllers(self):
        """Create/Delete two Communication controllers"""
        
        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["Communication", "DummyCommunicationController.py",
                         "DummyCommunicationController", "first_com_ctrl"])
        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["Communication", "DummyCommunicationController.py",
                         "DummyCommunicationController", "second_com_ctrl"])

        # Check controller list attribute
        ctrl_list = p.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x, 2)
        self.assertEqual(ctrl_list.value[0],
                         "first_com_ctrl (DummyCommunicationController.DummyCommunicationController/first_com_ctrl) - Communication Python ctrl (DummyCommunicationController.py)")
        self.assertEqual(ctrl_list.value[1],
                         "second_com_ctrl (DummyCommunicationController.DummyCommunicationController/second_com_ctrl) - Communication Python ctrl (DummyCommunicationController.py)")

        # Delete one controller and check controller list attribute
        p.command_inout("DeleteController", "second_com_ctrl")
        ctrl_list = p.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_com_ctrl (DummyCommunicationController.DummyCommunicationController/first_com_ctrl) - Communication Python ctrl (DummyCommunicationController.py)")

        self.pool_dp.command_inout("DeleteController", "first_com_ctrl")
        self.check_empty_attribute(p, "ControllerList")


class PseudoMotorControllerTestCase(poolunittest.PoolTestCase):
    """Test PseudoMotor controller creation, deletion, listing"""
    
    def needsMotorSimulator(self):
        return True
    
    def setUp(self):
        poolunittest.PoolTestCase.setUp(self)
        p = self.pool_dp
        p.command_inout("CreateController",
                        ["Motor", "SimuMotorCtrl.la", "SimuMotorController",
                         "first_simumot_ctrl", 
                         "DevName", self.motsim_ctrl_dev_name])
        
        p.command_inout("CreateMotor", ([0], ["first_simu_mot","first_simumot_ctrl"]))
        p.command_inout("CreateMotor", ([1], ["second_simu_mot","first_simumot_ctrl"]))
        
    def tearDown(self):
        p = self.pool_dp
        
        p.command_inout("DeleteMotor", "first_simu_mot")
        p.command_inout("DeleteMotor", "second_simu_mot")
        p.command_inout("DeleteController", "first_simumot_ctrl")
        poolunittest.PoolTestCase.tearDown(self)

    def testCreatePseudoMotorControllerWrongArguments(self):
        """Create Pseudo Motor controller with wrong arguments"""
        
        p = self.pool_dp 
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["a","b","c"], "Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["PseudoMotor","a/b","ctrl","inst"], "Pool_FileUnsupportedType")
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["PseudoMotor","a/b.truc","ctrl","inst"], "Pool_FileUnsupportedType")
        self.wrong_argument(self.pool_dp, "CreateController",
                            ["PseudoMotor","a","b","x"], "Pool_FileUnsupportedType")
        
        self.wrong_argument(self.pool_dp,"CreateController",
                            ["PseudoMotor","a.py","b","x"], "Pool_ControllerNotFound")
        self.wrong_argument(self.pool_dp,"CreateController",
                            ["PseudoMotor","a.la","b","x"], "Pool_ControllerNotFound")

        self.wrong_argument(self.pool_dp,"CreateController",
                            ["PseudoMotor","PseudoMotorLib.py","b","x"],
                            "Pool_CantLocatePythonClass")

        self.wrong_argument(self.pool_dp,"CreateController",
                            ["PseudoMotor","PseudoMotorLib.py","b","x"],
                            "Pool_CantLocatePythonClass")
        
        self.wrong_argument(p,"CreateController",
                            ["PseudoMotor", "PseudoMotorLib.py","Slit",
                             "first_slit_ctrl", 
                             "inexisting_simu_mot", "second_simu_mot",
                             "first_gap_mot", "first_offset_mot"],
                            "Pool_MotorNotDefined")

        self.wrong_argument(p,"CreateController",
                            ["PseudoMotor", "PseudoMotorLib.py","Slit",
                             "first_slit_ctrl", 
                             "first_simu_mot", "second_simu_mot",
                             "first_gap_mot"],
                            "Pool_WrongArgumentNumber")
            
    def testCreateDeletePseudoMotorController(self):
        """Create/Delete PseudoMotor controller"""
        
        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["PseudoMotor", "PseudoMotorLib.py",
                         "Slit", "first_slit_ctrl", 
                         "first_simu_mot", "second_simu_mot",
                         "first_gap_mot", "first_offset_mot"])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x, 2)
        self.assertEqual(ctrl_list.value[0],
                         "first_simumot_ctrl (SimuMotorCtrl.SimuMotorController/first_simumot_ctrl) - Motor Cpp ctrl (SimuMotorCtrl.la)")
        self.assertEqual(ctrl_list.value[1],
                         "first_slit_ctrl (PseudoMotorLib.Slit/first_slit_ctrl) - PseudoMotor Python ctrl (PseudoMotorLib.py)")

        p.command_inout("DeletePseudoMotor", "first_gap_mot")
        p.command_inout("DeletePseudoMotor", "first_offset_mot")

        p.command_inout("DeleteController", "first_slit_ctrl")
        
        ctrl_list = p.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_simumot_ctrl (SimuMotorCtrl.SimuMotorController/first_simumot_ctrl) - Motor Cpp ctrl (SimuMotorCtrl.la)")
        
    def testDeleteInexistingPseudoMotorController(self):
        """Try to delete inexisting PseudoMotor controller"""
        
        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["PseudoMotor", "PseudoMotorLib.py",
                         "Slit", "first_slit_ctrl", 
                         "first_simu_mot", "second_simu_mot",
                         "first_gap_mot", "first_offset_mot"])

        self.wrong_argument(p, "DeleteController", "Aaaa", 
                            "Pool_ControllerNotFound")

        p.command_inout("DeletePseudoMotor", "first_gap_mot")
        p.command_inout("DeletePseudoMotor", "first_offset_mot")
        
        p.command_inout("DeleteController", "first_slit_ctrl")
        ctrl_list = p.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_simumot_ctrl (SimuMotorCtrl.SimuMotorController/first_simumot_ctrl) - Motor Cpp ctrl (SimuMotorCtrl.la)")

    def testDeletePseudoMotorControllerWithPseudoMotors(self):
        """Try to delete a PseudoMotor controller with pseudo motors"""
        
        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["PseudoMotor", "PseudoMotorLib.py",
                         "Slit", "first_slit_ctrl", 
                         "first_simu_mot", "second_simu_mot",
                         "first_gap_mot", "first_offset_mot"])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x, 2)
        self.assertEqual(ctrl_list.value[0],
                         "first_simumot_ctrl (SimuMotorCtrl.SimuMotorController/first_simumot_ctrl) - Motor Cpp ctrl (SimuMotorCtrl.la)")
        self.assertEqual(ctrl_list.value[1],
                         "first_slit_ctrl (PseudoMotorLib.Slit/first_slit_ctrl) - PseudoMotor Python ctrl (PseudoMotorLib.py)")

        self.wrong_argument(p, "DeleteController", "first_slit_ctrl", 
                            "Pool_CantDeleteController")

        self.wrong_argument(p, "DeleteMotor", "first_simu_mot", 
                            "Pool_CantDeleteMotor")
        self.wrong_argument(p, "DeleteMotor", "second_simu_mot", 
                            "Pool_CantDeleteMotor")

        p.command_inout("DeletePseudoMotor", "first_gap_mot")
        p.command_inout("DeletePseudoMotor", "first_offset_mot")

        p.command_inout("DeleteController", "first_slit_ctrl")
        
        ctrl_list = p.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_simumot_ctrl (SimuMotorCtrl.SimuMotorController/first_simumot_ctrl) - Motor Cpp ctrl (SimuMotorCtrl.la)")
        
    def testCreateSamePseudoMotorControllerTwice(self):
        """Try create same PseudoMotor controller twice"""

        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["PseudoMotor", "PseudoMotorLib.py",
                         "Slit", "first_slit_ctrl", 
                         "first_simu_mot", "second_simu_mot",
                         "first_gap_mot", "first_offset_mot"])

        ctrl_list = p.read_attribute("ControllerList")

        self.assertEqual(ctrl_list.dim_x, 2)
        self.assertEqual(ctrl_list.value[0],
                         "first_simumot_ctrl (SimuMotorCtrl.SimuMotorController/first_simumot_ctrl) - Motor Cpp ctrl (SimuMotorCtrl.la)")
        self.assertEqual(ctrl_list.value[1],
                         "first_slit_ctrl (PseudoMotorLib.Slit/first_slit_ctrl) - PseudoMotor Python ctrl (PseudoMotorLib.py)")

        self.wrong_argument(p, "CreateController",
                            ["PseudoMotor", "PseudoMotorLib.py", 
                             "Slit", "first_slit_ctrl", 
                             "first_simu_mot", "second_simu_mot",
                             "first_gap_mot", "first_offset_mot"],
                            "Pool_ControllerAlreadyCreated")

        p.command_inout("DeletePseudoMotor", "first_gap_mot")
        p.command_inout("DeletePseudoMotor", "first_offset_mot")

        p.command_inout("DeleteController", "first_slit_ctrl")

        ctrl_list = p.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_simumot_ctrl (SimuMotorCtrl.SimuMotorController/first_simumot_ctrl) - Motor Cpp ctrl (SimuMotorCtrl.la)")

    def testCreateDeleteTwoPseudoMotorControllers(self):
        """Create/Delete two PseudoMotor controllers"""
        
        p = self.pool_dp 
        p.command_inout("CreateController", 
                        ["PseudoMotor", "PseudoMotorLib.py",
                         "Slit", "first_slit_ctrl", 
                         "first_simu_mot", "second_simu_mot",
                         "first_gap_mot", "first_offset_mot"])
        
        #
        # Repeating pseudo motor names is an error
        #
        self.wrong_argument(p,"CreateController", 
                            ["PseudoMotor", "PseudoMotorLib.py",
                             "Slit", "second_slit_ctrl", 
                             "first_simu_mot", "second_simu_mot",
                             "first_gap_mot", "second_offset_mot"],
                            "Pool_PseudoMotorAlreadyCreated")

        p.command_inout("CreateController", 
                        ["PseudoMotor", "PseudoMotorLib.py",
                         "Slit", "second_slit_ctrl", 
                         "first_simu_mot", "second_simu_mot",
                         "second_gap_mot", "second_offset_mot"])

        # Check controller list attribute
        ctrl_list = p.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x, 3)
        self.assertEqual(ctrl_list.value[0],
                         "first_simumot_ctrl (SimuMotorCtrl.SimuMotorController/first_simumot_ctrl) - Motor Cpp ctrl (SimuMotorCtrl.la)")
        self.assertEqual(ctrl_list.value[1],
                         "first_slit_ctrl (PseudoMotorLib.Slit/first_slit_ctrl) - PseudoMotor Python ctrl (PseudoMotorLib.py)")
        self.assertEqual(ctrl_list.value[2],
                         "second_slit_ctrl (PseudoMotorLib.Slit/second_slit_ctrl) - PseudoMotor Python ctrl (PseudoMotorLib.py)")

        # Delete one controller and check controller list attribute
        p.command_inout("DeletePseudoMotor", "second_gap_mot")
        p.command_inout("DeletePseudoMotor", "second_offset_mot")
        
        p.command_inout("DeleteController", "second_slit_ctrl")
        ctrl_list = p.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x, 2)
        self.assertEqual(ctrl_list.value[0],
                         "first_simumot_ctrl (SimuMotorCtrl.SimuMotorController/first_simumot_ctrl) - Motor Cpp ctrl (SimuMotorCtrl.la)")
        self.assertEqual(ctrl_list.value[1],
                         "first_slit_ctrl (PseudoMotorLib.Slit/first_slit_ctrl) - PseudoMotor Python ctrl (PseudoMotorLib.py)")

        p.command_inout("DeletePseudoMotor", "first_gap_mot")
        p.command_inout("DeletePseudoMotor", "first_offset_mot")

        self.pool_dp.command_inout("DeleteController", "first_slit_ctrl")
        ctrl_list = p.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x, 1)
        self.assertEqual(ctrl_list.value[0],
                         "first_simumot_ctrl (SimuMotorCtrl.SimuMotorController/first_simumot_ctrl) - Motor Cpp ctrl (SimuMotorCtrl.la)")
                               
def suite():
    s = poolunittest.PoolTestSuite()
    
    empty_pool_suite = unittest.makeSuite(EmptyPoolTestCase, 'test')
    ctrl_pool_suite = unittest.makeSuite(ControllerTestCase, 'test')
    mot_ctrl_pool_suite = unittest.makeSuite(MotorControllerTestCase, 'test')
    ct_ctrl_pool_suite = unittest.makeSuite(CounterTimerControllerTestCase, 'test')
    zd_ctrl_pool_suite = unittest.makeSuite(ZeroDControllerTestCase, 'test')
    com_ctrl_pool_suite = unittest.makeSuite(CommunicationControllerTestCase, 'test')
    pm_ctrl_pool_suite = unittest.makeSuite(PseudoMotorControllerTestCase, 'test')

    s.addTest(empty_pool_suite)
    s.addTest(ctrl_pool_suite)
    s.addTest(mot_ctrl_pool_suite)
    s.addTest(ct_ctrl_pool_suite)
    s.addTest(zd_ctrl_pool_suite)
    s.addTest(com_ctrl_pool_suite)
    s.addTest(pm_ctrl_pool_suite)
    
    return s

def m1():
    unittest.main()

def m2(test_output):
    test_output_file = open(test_output, "w")
    runner = poolunittest.PoolTestRunner(verbosity=2, stream=test_output_file)
    unittest.main(testRunner=runner, testLoader=poolunittest.PoolTestLoader())
    
def m3(test_output):
    test_output_file = file(test_output, 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(
                stream=test_output_file,
                title='Device Pool Unit Test',
                description='Device Pool Unit Test package',
                verbosity=2)    
    runner.run(suite())
        
if __name__ == "__main__":
    test_output = "test_result.html"
    m3(test_output)
    
import unittest
import PyTango
import sys
import os
import time
import PoolTestUtil
import posix        
            
                        
#---------------------------------------------------------------------------------------------------------------------            
class InfoCtrl(PoolTestUtil.TestUtil):
    def __init__(self,dev_name,ds_full_name,methodName='runTest'):
        unittest.TestCase.__init__(self,methodName)
        self.dev_name = dev_name
        self.pool = PyTango.DeviceProxy(self.dev_name)
        self.admin_name = "dserver/" + ds_full_name
        
        self.prop_added = False
        self.ctrl_added = False
        
#---------------------------------------------------------------------------------------------------------------------
                            
    def setUp(self):
        if self.pool_configured(self.pool) == False:
            self.empty_pool(self.pool)
            self.create_ctrl_mot(self.pool)
            
#---------------------------------------------------------------------------------------------------------------------
               
    def InfoCtrl_test(self):
        """Pool GetControllerInfo command"""

        ctrl_info = self.pool.command_inout("GetControllerInfo",["Motor","WaterPapCtrl.py","IcePapController"])
        self.assertEqual(len(ctrl_info),6)
        self.assertNotEqual(ctrl_info[0].find("This class is the Tango Sardana motor controller for the ICEPAP"),-1)
        self.assertEqual(ctrl_info[1],"1")
        self.assertEqual(ctrl_info[2],"MaxDevice")
        self.assertEqual(ctrl_info[3],"DevLong")
        self.assertEqual(ctrl_info[4],"The maximum number of device supported by the controller")
        self.assertEqual(ctrl_info[5],"10")
                
        ctrl_info = self.pool.command_inout("GetControllerInfo",["Motor","DummyCtrl.so","DummyController"])
        self.assertEqual(len(ctrl_info),18)
        self.assertNotEqual(ctrl_info[0].find("This is the C++ controller for the DummyController class"),-1)
        self.assertEqual(ctrl_info[1],"4")
        self.assertEqual(ctrl_info[2],"MaxDevice")
        self.assertEqual(ctrl_info[3],"DevLong")
        self.assertEqual(ctrl_info[4],"The maximum number of device supported by the controller")
        self.assertEqual(ctrl_info[5],"16")
        self.assertEqual(ctrl_info[6],"The prop")
        self.assertEqual(ctrl_info[7],"DevLong")
        self.assertEqual(ctrl_info[8],"The first CPP property")
        self.assertEqual(ctrl_info[9],"12")
        self.assertEqual(ctrl_info[10],"Another_Prop")
        self.assertEqual(ctrl_info[11],"DevString")
        self.assertEqual(ctrl_info[12],"The second CPP property")
        self.assertEqual(ctrl_info[13],"Hola")
        self.assertEqual(ctrl_info[14],"Third_Prop")
        self.assertEqual(ctrl_info[15],"DevVarLongArray")
        self.assertEqual(ctrl_info[16],"The third CPP property")
        self.assertEqual(ctrl_info[17],"11\n22\n33")
        
        ctrl_info = self.pool.command_inout("GetControllerInfo",["Motor","DummyCtrl.so","DummyController","cpp_ctrl"])
        self.assertEqual(len(ctrl_info),18)
        self.assertNotEqual(ctrl_info[0].find("This is the C++ controller for the DummyController class"),-1)
        self.assertEqual(ctrl_info[1],"4")
        self.assertEqual(ctrl_info[2],"MaxDevice")
        self.assertEqual(ctrl_info[3],"DevLong")
        self.assertEqual(ctrl_info[4],"The maximum number of device supported by the controller")
        self.assertEqual(ctrl_info[5],"16")
        self.assertEqual(ctrl_info[6],"The prop")
        self.assertEqual(ctrl_info[7],"DevLong")
        self.assertEqual(ctrl_info[8],"The first CPP property")
        self.assertEqual(ctrl_info[9],"12")
        self.assertEqual(ctrl_info[10],"Another_Prop")
        self.assertEqual(ctrl_info[11],"DevString")
        self.assertEqual(ctrl_info[12],"The second CPP property")
        self.assertEqual(ctrl_info[13],"Hola")
        self.assertEqual(ctrl_info[14],"Third_Prop")
        self.assertEqual(ctrl_info[15],"DevVarLongArray")
        self.assertEqual(ctrl_info[16],"The third CPP property")
        self.assertEqual(ctrl_info[17],"11\n22\n33")
        
        ctrl_info = self.pool.command_inout("GetControllerInfo",["Motor","WaterPapCtrl_prop.py","IcePapController"])
        self.assertEqual(len(ctrl_info),22)
        self.assertNotEqual(ctrl_info[0].find("This class is the Tango Sardana motor controller for the ICEPAP with properties"),-1)
        self.assertEqual(ctrl_info[1],"5")
        self.assertEqual(ctrl_info[2],"MaxDevice")
        self.assertEqual(ctrl_info[3],"DevLong")
        self.assertEqual(ctrl_info[4],"The maximum number of device supported by the controller")
        self.assertEqual(ctrl_info[5],"22")
        self.assertEqual(ctrl_info[6],"A_Class_Prop")
        self.assertEqual(ctrl_info[7],"DevLong")
        self.assertEqual(ctrl_info[8],"A class property")
        self.assertEqual(ctrl_info[9],"20")
        self.assertEqual(ctrl_info[10],"Host")
        self.assertEqual(ctrl_info[11],"DevString")
        self.assertEqual(ctrl_info[12],"The host name")
        self.assertEqual(ctrl_info[13],"")
        self.assertEqual(ctrl_info[14],"Port")
        self.assertEqual(ctrl_info[15],"DevLong")
        self.assertEqual(ctrl_info[16],"The port number")
        self.assertEqual(ctrl_info[17],"")
        self.assertEqual(ctrl_info[18],"Another_Class_Prop")
        self.assertEqual(ctrl_info[19],"DevDouble")
        self.assertEqual(ctrl_info[20],"Bla bla bla")
        self.assertEqual(ctrl_info[21],"2.345")

#
# Try to create a controller with missing instance properties
#
        
        self.wrong_argument(self.pool,"CreateController",["Motor","WaterPapCtrl_prop.py","IcePapController","222"],"Pool_MissingPropertyValue")
 
        self.db = PyTango.Database()
        prop = {'Host':["icepap"],'Port':['5555']}
        self.db.put_property("IcePapController/222",prop)
        self.prop_added = True
        
        self.pool.command_inout("CreateController",["Motor","WaterPapCtrl_prop.py","IcePapController","222"])
        self.ctrl_added = True
       
        ctrl_info = self.pool.command_inout("GetControllerInfo",["Motor","WaterPapCtrl_prop.py","IcePapController","222"])
        self.assertEqual(len(ctrl_info),22)
        self.assertNotEqual(ctrl_info[0].find("This class is the Tango Sardana motor controller for the ICEPAP with properties"),-1)
        self.assertEqual(ctrl_info[1],"5")
        self.assertEqual(ctrl_info[2],"MaxDevice")
        self.assertEqual(ctrl_info[3],"DevLong")
        self.assertEqual(ctrl_info[4],"The maximum number of device supported by the controller")
        self.assertEqual(ctrl_info[5],"22")
        self.assertEqual(ctrl_info[6],"A_Class_Prop")
        self.assertEqual(ctrl_info[7],"DevLong")
        self.assertEqual(ctrl_info[8],"A class property")
        self.assertEqual(ctrl_info[9],"20")
        self.assertEqual(ctrl_info[10],"Host")
        self.assertEqual(ctrl_info[11],"DevString")
        self.assertEqual(ctrl_info[12],"The host name")
        self.assertEqual(ctrl_info[13],"icepap")
        self.assertEqual(ctrl_info[14],"Port")
        self.assertEqual(ctrl_info[15],"DevLong")
        self.assertEqual(ctrl_info[16],"The port number")
        self.assertEqual(ctrl_info[17],"5555")
        self.assertEqual(ctrl_info[18],"Another_Class_Prop")
        self.assertEqual(ctrl_info[19],"DevDouble")
        self.assertEqual(ctrl_info[20],"Bla bla bla")
        self.assertEqual(ctrl_info[21],"2.345")

#
# Get info for CounterTimer controller
#
       
        ctrl_info = self.pool.command_inout("GetControllerInfo",["CounterTimer","Vct6Ctrl.py","Vct6Controller"])
        self.assertEqual(len(ctrl_info),10)
        self.assertNotEqual(ctrl_info[0].find("This class is the Tango Sardana CounterTimer controller for the VCT6"),-1)
        self.assertEqual(ctrl_info[1],"2")
        self.assertEqual(ctrl_info[2],"MaxDevice")
        self.assertEqual(ctrl_info[3],"DevLong")
        self.assertEqual(ctrl_info[4],"The maximum number of device supported by the controller")
        self.assertEqual(ctrl_info[5],"6")
        self.assertEqual(ctrl_info[6],"CtrlDevName")
        self.assertEqual(ctrl_info[7],"DevString")
        self.assertEqual(ctrl_info[8],"The ctrl simulator Tango device name")
        self.assertEqual(ctrl_info[9],"")
        
#
# The same for a C++ instance
#

        ctrl_info = self.pool.command_inout("GetControllerInfo",["CounterTimer","DummyCoTiCtrl.so","DummyCoTiController"])
        self.assertEqual(len(ctrl_info),18)
        self.assertNotEqual(ctrl_info[0].find("This is the C++ controller for the DummyCoTiController class"),-1)
        self.assertEqual(ctrl_info[1],"4")
        self.assertEqual(ctrl_info[2],"MaxDevice")
        self.assertEqual(ctrl_info[3],"DevLong")
        self.assertEqual(ctrl_info[4],"The maximum number of device supported by the controller")
        self.assertEqual(ctrl_info[5],"12")
        self.assertEqual(ctrl_info[6],"The prop")
        self.assertEqual(ctrl_info[7],"DevLong")
        self.assertEqual(ctrl_info[8],"The first CPP property")
        self.assertEqual(ctrl_info[9],"12")
        self.assertEqual(ctrl_info[10],"Another_Prop")
        self.assertEqual(ctrl_info[11],"DevString")
        self.assertEqual(ctrl_info[12],"The second CPP property")
        self.assertEqual(ctrl_info[13],"Hola")
        self.assertEqual(ctrl_info[14],"Third_Prop")
        self.assertEqual(ctrl_info[15],"DevVarLongArray")
        self.assertEqual(ctrl_info[16],"The third CPP property")
        self.assertEqual(ctrl_info[17],"11\n22\n33")
        
#
# Get info for Zero D controller
#
       
        ctrl_info = self.pool.command_inout("GetControllerInfo",["ZeroDExpChannel","DummyZeroDCtrl.so","DummyZeroDController","Cpp_ZeroD"])
        self.assertEqual(len(ctrl_info),18)
        self.assertNotEqual(ctrl_info[0].find("This is the C++ controller for the DummyZeroDController class"),-1)
        self.assertEqual(ctrl_info[1],"4")
        self.assertEqual(ctrl_info[2],"MaxDevice")
        self.assertEqual(ctrl_info[3],"DevLong")
        self.assertEqual(ctrl_info[4],"The maximum number of device supported by the controller")
        self.assertEqual(ctrl_info[5],"2")
        self.assertEqual(ctrl_info[6],"The prop")
        self.assertEqual(ctrl_info[7],"DevLong")
        self.assertEqual(ctrl_info[8],"The first CPP property")
        self.assertEqual(ctrl_info[9],"12")
        self.assertEqual(ctrl_info[10],"Another_Prop")
        self.assertEqual(ctrl_info[11],"DevString")
        self.assertEqual(ctrl_info[12],"The second CPP property")
        self.assertEqual(ctrl_info[13],"Hola")
        self.assertEqual(ctrl_info[14],"Third_Prop")
        self.assertEqual(ctrl_info[15],"DevVarLongArray")
        self.assertEqual(ctrl_info[16],"The third CPP property")
        self.assertEqual(ctrl_info[17],"11\n22\n33")
        
#
# the same for a Python Zero D controller
#

        ctrl_info = self.pool.command_inout("GetControllerInfo",["ZeroDExpChannel","ElecMeter.py","ElecMeterController"])
        self.assertEqual(len(ctrl_info),6)
        
        self.assertNotEqual(ctrl_info[0].find("This class is the Tango Sardana Zero D controller for an Electrometer"),-1)
        self.assertEqual(ctrl_info[1],"1")
        self.assertEqual(ctrl_info[2],"MaxDevice")
        self.assertEqual(ctrl_info[3],"DevLong")
        self.assertEqual(ctrl_info[4],"The maximum number of device supported by the controller")
        self.assertEqual(ctrl_info[5],"1")
                       
#---------------------------------------------------------------------------------------------------------------------
               
    def StupidInfoCtrl_test(self):
        """Pool sutpid GetControllerInfo command arguments"""
        
        self.wrong_argument(self.pool,"GetControllerInfo",["WaterPapCtrl"],"Pool_WrongArgumentNumber")
        self.wrong_argument(self.pool,"GetControllerInfo",["Motor","WaterPapCtrl","IcePapController"],"Pool_FileUnsupportedType")
        self.wrong_argument(self.pool,"GetControllerInfo",["Motor","WaterPapCtrl.pp","IcePapController"],"Pool_FileUnsupportedType")
        self.wrong_argument(self.pool,"GetControllerInfo",["motor","aa.py","cl"],"Pool_CantLocateControllerFile")
        self.wrong_argument(self.pool,"GetControllerInfo",["MoTor","WaterPapCtrl.py","IcePapController","truc"],"Pool_CantLocateControllerInstance")
        self.wrong_argument(self.pool,"GetControllerInfo",["Mottt","WaterPapCtrl.py","IcePapController"],"Pool_UnknownControllerType")

#---------------------------------------------------------------------------------------------------------------------

    def tearDown(self):
        if self.prop_added == True:
            self.db.delete_property("IcePapController/222",["Host","Port"])
            
        if self.ctrl_added == True:
            self.pool.command_inout("DeleteController","222")
            
        
        
#-------------------------------------------------------------------------------------------------------------------
#
#        Test sequencement
#
#-------------------------------------------------------------------------------------------------------------------  

          
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print len(sys.argv)
        print "InfoCtrl usage = InfoCtrl <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)

    runner = unittest.TextTestRunner(verbosity=3)
    PoolTestUtil.start_test(runner,InfoCtrl,dev_name,sys.argv[1],"StupidInfoCtrl_test")
    PoolTestUtil.start_test(runner,InfoCtrl,dev_name,sys.argv[1],"InfoCtrl_test")

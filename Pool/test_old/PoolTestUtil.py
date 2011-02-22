import unittest
import PyTango
import sys
import os
import user

def start_test(runner,cl,*args):
    test_res = runner.run(cl(*args))
    if len(test_res.errors) != 0 or len(test_res.failures) != 0:
#        admin = PyTango.DeviceProxy("dserver/pool/test")
#        admin.command_inout("kill")
        sys.exit(-1)

def GetBasePath():
    return user.home + "/pool"

def GetPoolDevName(pool_ds_name):
    db = PyTango.Database()
    dev_name_list = db.get_device_name(pool_ds_name,"Pool")
    if len(dev_name_list) == 0:
        return None
    else:
        return dev_name_list[0]
        
        
class TestUtil(unittest.TestCase):       
    def check_empty_attribute(self,dev,att_name):
        try:
            c_list = dev.read_attribute(att_name)
            if len(c_list.value) != 0:
                self.assert_(False,"The %s attribute is not empty !! It contains: %s" % (att_name,c_list.value))
        except PyTango.DevFailed,e:
            except_value = sys.exc_info()[1]
            self.assertEqual(except_value[0]["reason"],"API_EmptyDeviceAttribute")
            self.assertEqual(except_value[0]["desc"],"cannot extract, no data in DeviceAttribute object ")
            
    def attribute_error(self,dev,att_name,err,pr = False):
        try:
            c_list = dev.read_attribute(att_name)
            self.assert_(False,"The %s attribute is not in fault!!" % (att_name))
        except PyTango.DevFailed,e:
            except_value = sys.exc_info()[1]
            if pr == True:
                print "\nERROR desc"
                print "origin =",except_value[0]["origin"]
                print "desc =",except_value[0]["desc"]
                print "origin =",except_value[0]['origin']
            self.assertEqual(except_value[0]["reason"],err)
            
    def wr_attribute_error(self,dev,att_val,err,pr = False):
        try:
            dev.write_attribute(att_val)
            self.assert_(False,"The %s attribute is not in fault!!" % (att_val.name))
        except PyTango.DevFailed,e:
            except_value = sys.exc_info()[1]
            if pr == True:
                print "\nERROR desc"
                print "origin =",except_value[0]["origin"]
                print "desc =",except_value[0]["desc"]
                print "origin =",except_value[0]['origin']
            self.assertEqual(except_value[0]["reason"],err)
            
    def _write_attribute(self,dev,att_name,att_val):
        val = PyTango.AttributeValue()
        val.name = att_name
        val.value = att_val
        dev.write_attribute(val)

#---------------------------------------------------------------------------------------------------------  

    def wrong_argument(self,dev,cmd_name,arg_list,err,pr = False):
        try:
            dev.command_inout(cmd_name,arg_list)
            self.assert_(False,"The %s command succeed with stupid arguments!!" % (cmd_name))
        except PyTango.DevFailed,e:
            except_value = sys.exc_info()[1]
            if pr == True:
                print "\nERROR desc"
                print "origin =",except_value[0]["origin"]
                print "desc =",except_value[0]["desc"]
                print "origin =",except_value[0]['origin']
            self.assertEqual(except_value[0]["reason"],err)
            
#---------------------------------------------------------------------------------------------------------  
            
    def pool_configured(self,dev):

#
# Correct controller number and types ?
#

        try:
            ctrl_list = dev.read_attribute("ControllerList")
        except:
            return False
               
        if ctrl_list.dim_x != 4:
            return False
        else :
            if ctrl_list.value[0].find("IcePapController/first") == -1:
                return False
            else:
                if ctrl_list.value[1].find("DummyController/cpp_ctrl") == -1:
                    return False
                else:
                    if ctrl_list.value[2].find("Vct6Controller/Py_Vct6") == -1:
                        return False
                    else:
                        if ctrl_list.value[3].find("DummyZeroDController/Cpp_ZeroD") == -1:
                            return False

#
# Correct number of motors ?
#

        try:
            mot_list = self.pool.read_attribute("MotorList") 
        except:
            return False

        if mot_list.dim_x != 7:
            return False
        else:
            if mot_list.value[0].find("First_Motor") == -1:
                return False
            else:
                if mot_list.value[1].find("Test_Motor") == -1:
                    return False
                else:
                    if mot_list.value[2].find("Test_Motor2") == -1:
                        return False
                    else:
                        if mot_list.value[3].find("Error_Motor") == -1:
                            return False
                        else:
                            if mot_list.value[4].find("Fault_Motor") == -1:
                                return False
                            else:
                                if mot_list.value[5].find("Except_Motor") == -1:
                                    return False
                                else:
                                    if mot_list.value[6].find("ErrorRead_Motor") == -1:
                                        return False
        
#
# Correct number os pseudo motors ?
#

        try:
            mot_list = self.pool.read_attribute("PseudoMotorList") 
        except:
            return False
               
        if mot_list.dim_x != 2:
            return False
        else:
            if mot_list.value[0].find("testgap01") == -1:
                return False
            else:
                if mot_list.value[1].find("testoffset01") == -1:
                    return False

#
# Correct number of CT and Zero D ?
#

        try:
            ct_list = self.pool.read_attribute("ExpChannelList") 
        except:
            return False
               
        if ct_list.dim_x != 3:
            return False
        else:
            if ct_list.value[0].find("First_CT") == -1:
                return False
            else:
                if ct_list.value[1].find("Second_CT") == -1:
                    return False
                else:
                    if ct_list.value[2].find("First_ZeroD") == -1:
                        return False

        return True


#---------------------------------------------------------------------------------------------------------    
            
    def empty_pool(self,dev):
        try:
            pm_list = dev.read_attribute("PseudoMotorList")
            for pm in pm_list.value:
                pm_name = pm.split(" ")
                dev.command_inout("DeletePseudoMotor",pm_name[0])
        except PyTango.DevFailed,e:
            pass
        
        try:
            mg_list = dev.read_attribute("MotorGroupList")
            for mg in mg_list.value:
                mg_id = mg.split(" ")
                dev.command_inout("DeleteMotorGroup",mg_id[0])
        except PyTango.DevFailed,e:
            pass
        
        try:
            mot_list = dev.read_attribute("MotorList")
            for mot in mot_list.value:
                mot_id = mot.split(" ")
                dev.command_inout("DeleteMotor",mot_id[0])
        except PyTango.DevFailed,e:
            pass
        
        try:
            mg_list = dev.read_attribute("MeasurementGroupList")
            for mg in mg_list.value:
                mg_id = mg.split(" ")
                dev.command_inout("DeleteMeasurementGroup",mg_id[0])
        except PyTango.DevFailed,e:
            pass        

        try:
            channel_list = dev.read_attribute("ExpChannelList")
            for channel in channel_list.value:
                channel_id = channel.split(" ")
                dev.command_inout("DeleteExpChannel",channel_id[0])
        except PyTango.DevFailed,e:
            pass

        try:
            ctrl_list = dev.read_attribute("ControllerList")
            for ctrl in ctrl_list.value:
                ctrl_id = ctrl.split(" ")
                dev.command_inout("DeleteController",ctrl_id[0])
        except PyTango.DevFailed,e:
            pass
        
        self.check_empty_attribute(dev,"PseudoMotorList")
        self.check_empty_attribute(dev,"MotorGroupList")
        self.check_empty_attribute(dev,"MeasurementGroupList")
        self.check_empty_attribute(dev,"MotorList")
        self.check_empty_attribute(dev,"ExpChannelList")
        self.check_empty_attribute(dev,"ControllerList")

#---------------------------------------------------------------------------------------------------------          
        
    def create_ctrl_mot(self,dev):
        
#
# Create four controllers (2 motors, 1 ct, 1 zerod)
#

        dev.command_inout("CreateController",["Motor","WaterPapCtrl.py","IcePapController","first"])
        dev.command_inout("CreateController",["Motor","DummyCtrl.so","DummyController","cpp_ctrl"])
        dev.command_inout("CreateController",["CounterTimer","Vct6Ctrl.py","Vct6Controller","Py_Vct6"])
        dev.command_inout("CreateController",["ZeroDExpChannel","DummyZeroDCtrl.so","DummyZeroDController","Cpp_ZeroD"])
        ctrl_list = dev.read_attribute("ControllerList")
        self.assertEqual(ctrl_list.dim_x,4)
        ctrl1_str = "first (WaterPapCtrl.IcePapController/first) - Motor Python ctrl (WaterPapCtrl.py)"
        ctrl2_str = "cpp_ctrl (DummyCtrl.DummyController/cpp_ctrl) - Motor Cpp ctrl (DummyCtrl.so)"
        ctrl3_str = "Py_Vct6 (Vct6Ctrl.Vct6Controller/Py_Vct6) - CounterTimer Python ctrl (Vct6Ctrl.py)"
        ctrl4_str = "Cpp_ZeroD (DummyZeroDCtrl.DummyZeroDController/Cpp_ZeroD) - ZeroDExpChannel Cpp ctrl (DummyZeroDCtrl.so)"
        self.assertEqual(ctrl_list.value[0],ctrl1_str)
        self.assertEqual(ctrl_list.value[1],ctrl2_str)
        self.assertEqual(ctrl_list.value[2],ctrl3_str)
        self.assertEqual(ctrl_list.value[3],ctrl4_str)

#
# Create 6 motors
#
        
        dev.command_inout("CreateMotor",([0],["First_Motor","first"]))
        dev.command_inout("CreateMotor",([1],["Test_Motor","cpp_ctrl"]))
        dev.command_inout("CreateMotor",([2],["Test_Motor2","cpp_ctrl"]))
        dev.command_inout("CreateMotor",([9],["Error_Motor","cpp_ctrl"]))
        dev.command_inout("CreateMotor",([10],["Fault_Motor","cpp_ctrl"]))
        dev.command_inout("CreateMotor",([11],["Except_Motor","cpp_ctrl"]))
        dev.command_inout("CreateMotor",([12],["ErrorRead_Motor","cpp_ctrl"]))

        mot_list = dev.read_attribute("MotorList")
        self.assertEqual(mot_list.dim_x,7)
        mot1_str = "First_Motor (motor/first/0)"
        mot2_str = "Test_Motor (motor/cpp_ctrl/1)"
        mot3_str = "Test_Motor2 (motor/cpp_ctrl/2)"
        mot4_str = "Error_Motor (motor/cpp_ctrl/9)"
        mot5_str = "Fault_Motor (motor/cpp_ctrl/10)"
        mot6_str = "Except_Motor (motor/cpp_ctrl/11)"
        mot7_str = "ErrorRead_Motor (motor/cpp_ctrl/12)"
        self.assertEqual(mot_list.value[0],mot1_str)
        self.assertEqual(mot_list.value[1],mot2_str)
        self.assertEqual(mot_list.value[2],mot3_str)
        self.assertEqual(mot_list.value[3],mot4_str)
        self.assertEqual(mot_list.value[4],mot5_str)
        self.assertEqual(mot_list.value[5],mot6_str)
        self.assertEqual(mot_list.value[6],mot7_str)
        
        test_mot = PyTango.DeviceProxy("Test_Motor")
        attr_info = test_mot.attribute_query("Aaa")
        self.assertEqual(attr_info.name,"Aaa")
        
        attr_info = test_mot.attribute_query("Bbb")
        self.assertEqual(attr_info.name,"Bbb")
        
        attr_info = test_mot.attribute_query("Ccc")
        self.assertEqual(attr_info.name,"Ccc")
        
        received_except = False
        try:
            test_mot.attribute_query("Second_extra")
        except:
            received_except = True
        self.assertEqual(received_except,True)

#
# Create 2 pseudo motors
#

        dev.command_inout("CreatePseudoMotor",["PseudoLib.py","Slit","testgap01","testoffset01","Test_Motor","Test_Motor2"])

        pseudo_list = dev.read_attribute("PseudoMotorList")
        self.assertEqual(pseudo_list.dim_x,2)
        self.assertEqual(pseudo_list.value[0],"testgap01 (pm/pseudolib.slit/testgap01) Motor list: Test_Motor, Test_Motor2")
        self.assertEqual(pseudo_list.value[1],"testoffset01 (pm/pseudolib.slit/testoffset01) Motor list: Test_Motor, Test_Motor2")

#
# Create 2 CT on the Py CoTi controller
#
        
        dev.command_inout("CreateExpChannel",([0],["First_CT","Py_Vct6"]))
        dev.command_inout("CreateExpChannel",([1],["Second_CT","Py_Vct6"]))
        
        ct_list = dev.read_attribute("ExpChannelList")
        self.assertEqual(ct_list.dim_x,2)
        self.assertEqual(ct_list.value[0],"First_CT (expchan/py_vct6/0) Counter/Timer Experiment Channel")
        self.assertEqual(ct_list.value[1],"Second_CT (expchan/py_vct6/1) Counter/Timer Experiment Channel")
        
#
# Create 1 Zero D exp channel
#

        dev.command_inout("CreateExpChannel",([0],["First_ZeroD","Cpp_ZeroD"]))

        exp_list = dev.read_attribute("ExpChannelList")
        self.assertEqual(exp_list.dim_x,3)
        self.assertEqual(exp_list.value[2],"First_ZeroD (expchan/cpp_zerod/0) Zero D Experiment Channel")        

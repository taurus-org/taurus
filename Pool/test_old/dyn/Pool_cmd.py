import PyTango
import sys
import time

if __name__ == '__main__':
    pool_name = "et/pool/test"
    
    pool = PyTango.DeviceProxy(pool_name)
    loop = 0

#
# Test set-up
#

    try:
        pool.command_inout("DeleteMotor","Th_motor")
    except:
        pass
    
    try:
        pool.command_inout("DeleteMotor","Th2_Motor")
    except:
        pass
    
    try:
        pool.command_inout("DeleteMotor","dyn_Motor")
    except:
        pass
    
    try:
        pool.command_inout("DeleteController","dyn_test")
    except:
        pass

#
# The test infinite loop
#
   
    while(True):
        pool.command_inout("CreateMotor",([4],["Th_Motor","cpp_ctrl"]))
        pool.command_inout("CreateMotor",([5],["Th2_Motor","cpp_ctrl"]))
        
        mot_list = pool.read_attribute("MotorList")
        ctrl_list = pool.read_attribute("ControllerList")
        
        mot1_proxy = PyTango.DeviceProxy("Th_Motor")
        mot2_proxy = PyTango.DeviceProxy("Th2_Motor")
        
        mot1_proxy.command_inout("Init")
        mot2_proxy.command_inout("Init")
        
        pool.command_inout("InitController","cpp_ctrl")
#        start = time.time()
        pool.command_inout("DeleteMotor","Th_Motor")
#        stop = time.time()
#        print "Start = %f, Stop = %f" % (start,stop)
        pool.command_inout("DeleteMotor","Th2_Motor")
        
        pool.command_inout("CreateController",["Motor","DummyCtrl.so","DummyController","dyn_test"])
        pool.command_inout("CreateMotor",([1],["dyn_Motor","dyn_test"]))
        
        new_mot_proxy = PyTango.DeviceProxy("dyn_Motor")
        new_mot_proxy.command_inout("Init")
        
        mot_list = pool.read_attribute("MotorList")
        ctrl_list = pool.read_attribute("ControllerList")
        
        pool.command_inout("InitController","dyn_test")
        pool.command_inout("DeleteMotor","dyn_Motor")
        pool.command_inout("DeleteController","dyn_test")
                
#        time.sleep(0.05)
        loop += 1
        print "loop =",loop

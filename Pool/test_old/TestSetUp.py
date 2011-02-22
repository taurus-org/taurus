import PyTango
import sys
import PoolTestUtil

        
def TestSetUp(pool_ds_name,pool_dev_name):
    print "Pool dev name = ",pool_dev_name
    db = PyTango.Database()
    db.delete_device_property(pool_dev_name,["Controller"])
    
    dev_name_list = db.get_device_name(pool_ds_name,"Motor")
    for dev_name in dev_name_list:
        print "dev_name =",dev_name
        db.delete_device(dev_name)
        
    dev_name_list = db.get_device_name(pool_ds_name,"PseudoMotor")
    for dev_name in dev_name_list:
        print "dev_name =",dev_name
        db.delete_device(dev_name)

    dev_name_list = db.get_device_name(pool_ds_name,"MotorGroup")
    for dev_name in dev_name_list:
        print "dev_name =",dev_name
        db.delete_device(dev_name)
        
    dev_name_list = db.get_device_name(pool_ds_name,"CTExpChannel")
    for dev_name in dev_name_list:
        print "dev_name =",dev_name
        db.delete_device(dev_name)
        
    dev_name_list = db.get_device_name(pool_ds_name,"ZeroDExpChannel")
    for dev_name in dev_name_list:
        print "dev_name =",dev_name
        db.delete_device(dev_name)
    
    dev_name_list = db.get_device_name(pool_ds_name,"MeasurementGroup")
    for dev_name in dev_name_list:
        print "dev_name =",dev_name
        db.delete_device(dev_name)    
    
    db.delete_property("FirePapController/third",["MaxDevice"])
    db.delete_property("FirePapController/Max",["MaxDevice"])
    
    base_dir = PoolTestUtil.GetBasePath()
    print base_dir
    poolpath = base_dir + "/test/ctrl/test_ctrl:"
    poolpath = poolpath + base_dir + "/ctrl:" 
    poolpath = poolpath + base_dir + "/test/ctrl/coti_ctrl:"
    poolpath = poolpath + base_dir + "/test/pseudo_motor/test_pm:"
    poolpath = poolpath + base_dir + "/test/ctrl/zerod_ctrl"
    
    props = { 'PoolPath' : [poolpath,] }
    db.put_device_property(pool_dev_name,props)
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print len(sys.argv)
        print "runpooltest usage = runpooltest <pool DS name>"
        sys.exit(-1)

    dev_name = PoolTestUtil.GetPoolDevName(sys.argv[1])
    if (dev_name == None):
        print "Can't get Pool device name for device server",sys.argv[1]
        sys.exit(-1)
        
    TestSetUp(sys.argv[1],dev_name)

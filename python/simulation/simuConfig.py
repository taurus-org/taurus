import sys
import PyTango


class Console:
    
    def __init__(self, simulation):
        self.simulation = simulation
    
    def go(self):
        
        self.ask_motor_simulator()
        self.simulation.create_motor_simulator()
        mot_inst_name = self.simulation.motor_server_name.split("/")[1] 
        print 
        print "Please start the simulator by typing: 'python SimuMotorCtrl.py %s'" % mot_inst_name
        raw_input("Press enter when ready...")            
        
        self.ask_counter_simulator()
        self.simulation.create_counter_simulator()
        co_inst_name = self.simulation.counter_server_name.split("/")[1] 
        print 
        print "Please start the simulator by typing: 'python SimuCoTiCtrl.py %s'" % co_inst_name
        raw_input("Press enter when ready...")

        self.ask_pool()
        self.simulation.create_pool()
        pool_inst_name = self.simulation.pool_server_name.split("/")[1] 
        print 
        print "Please start the device pool by typing: 'Pool %s'" % pool_inst_name
        raw_input("Press enter when ready...")
        self.ask_pool_path()
        self.simulation.fill_pool()
        
        self.ask_macro_server()
        self.simulation.create_ms()
        self.ask_door()
        self.simulation.create_door()
        
    def ask_motor_simulator(self):
        
        dft_motctrl_devname = self.simulation.motor_ctrl_devname
        dft_motctrl_alias = self.simulation.motor_ctrl_alias
        dft_motor_nb = self.simulation.motor_nb
        
        existing_motor_ctrl_devnames = self.simulation.get_existing_motctrl_devices()
        
        # get controller device name from user
        name_in_use = True
        while name_in_use:
            input = raw_input("Motor controller name [%s]:" % dft_motctrl_alias)
            if input is None or len(input) == 0:
                input = dft_motctrl_alias
            curr_motctrl_devname = self.simulation.mot_ctrl_dev_pattern_generic % input
            if not curr_motctrl_devname in existing_motor_ctrl_devnames:
                self.simulation.motor_ctrl_devname = curr_motctrl_devname
                self.simulation.motor_ctrl_alias = input
                name_in_use = False
            else:
                print "%s already in use (%s)" % (input,curr_motctrl_devname)
        
        # get number of motors from user
        motor_nb = -1
        invalid_motor_nb = True
        while motor_nb < 0:
            input = raw_input("How many motors [%d]:" % dft_motor_nb)
            if input is None or len(input) == 0:
                input = dft_motor_nb
            try:
                motor_nb = int(input)
            except:
                pass

        self.simulation.motor_nb = motor_nb
        #self.simulation.motor_server_name = self.simulation.get_next_motorctrl_server()
        
    def ask_counter_simulator(self):
        
        dft_counterctrl_devname = self.simulation.counter_ctrl_devname
        dft_counterctrl_alias = self.simulation.counter_ctrl_alias
        dft_counter_nb = self.simulation.counter_nb
        
        existing_counter_ctrl_devnames = self.simulation.get_existing_counterctrl_devices()
        
        # get controller device name from user
        name_in_use = True
        while name_in_use:
            input = raw_input("Counter controller name [%s]:" % dft_counterctrl_alias)
            if input is None or len(input) == 0:
                input = dft_counterctrl_alias
            curr_counterctrl_devname = self.simulation.counter_ctrl_dev_pattern_generic % input
            if not curr_counterctrl_devname in existing_counter_ctrl_devnames:
                self.simulation.counter_ctrl_devname = curr_counterctrl_devname
                self.simulation.counter_ctrl_alias = input
                name_in_use = False
            else:
                print "%s already in use (%s)" % (input,curr_counterctrl_devname)
        
        # get number of counters from user
        counter_nb = -1
        invalid_counter_nb = True
        while counter_nb < 0:
            input = raw_input("How many counters [%d]:" % dft_counter_nb)
            if input is None or len(input) == 0:
                input = dft_counter_nb
            try:
                counter_nb = int(input)
            except:
                pass

        self.simulation.counter_nb = counter_nb
        #self.simulation.counter_server_name = self.simulation.get_next_counterctrl_server()

    def ask_pool(self):

        dft_pool_devname = self.simulation.pool_devname
        dft_pool_alias = self.simulation.pool_alias
        
        existing_pool_devnames = self.simulation.get_existing_pool_devices()
        
        # get pool device name from user
        name_in_use = True
        while name_in_use:
            input = raw_input("Device pool name [%s]:" % dft_pool_alias)
            if input is None or len(input) == 0:
                input = dft_pool_alias
            curr_pool_devname = self.simulation.pool_dev_pattern_generic % input
            if not curr_pool_devname in existing_pool_devnames:
                self.simulation.pool_devname = curr_pool_devname
                self.simulation.pool_alias = input
                name_in_use = False
            else:
                print "%s already in use (%s)" % (input,curr_pool_devname)
        
        #get the poolPath from the user
        dft_pool_path = self.simulation.pool_path
        input = raw_input("PoolPath ['%s']:" % dft_pool_path)
        if input is None or len(input) == 0:
            input = dft_pool_path
        else:
            input = [input]
            
        self.simulation.pool_path = input
        #self.simulation.pool_server_name = self.simulation.get_next_pool_server()        
    
    def ask_pool_path(self):
        while self.simulation.check_pool_ctrl_classes() == False:
            pool_path = self.pool_proxy.get_property(["PoolPath"])["PoolPath"]
            print "The current PoolPath does not contain the necessary controller classes:"
            print pool_path
            
            input = raw_input("Please give a new PoolPath:")
            self.simulation.change_pool_path([input])

    def ask_macro_server(self):

        dft_ms_devname = self.simulation.ms_devname
        dft_ms_alias = self.simulation.ms_alias
        
        existing_ms_devnames = self.simulation.get_existing_ms_devices()
        
        # get pool device name from user
        name_in_use = True
        while name_in_use:
            input = raw_input("Macro server name [%s]:" % dft_ms_alias)
            if input is None or len(input) == 0:
                input = dft_ms_alias
            curr_ms_devname = self.simulation.ms_dev_pattern_generic % input
            if not curr_ms_devname in existing_ms_devnames:
                self.simulation.ms_devname = curr_ms_devname
                self.simulation.ms_alias = input
                name_in_use = False
            else:
                print "%s already in use (%s)" % (input,curr_ms_devname)
        
        #get the macroPath from the user
        dft_ms_path = self.simulation.ms_path
        input = raw_input("MacroPath ['%s']:" % dft_ms_path)
        if input is None or len(input) == 0:
            input = dft_ms_path
        else:
            input = [input]
            
        self.simulation.ms_path = input
        #self.simulation.ms_server_name = self.simulation.get_next_pool_server()        
    
    def ask_door(self):

        dft_door_devname = self.simulation.door_devname
        dft_door_alias = self.simulation.door_alias
        
        existing_door_devnames = self.simulation.get_existing_door_devices()
        
        # get door device name from user
        name_in_use = True
        while name_in_use:
            input = raw_input("Door name [%s]:" % dft_door_alias)
            if input is None or len(input) == 0:
                input = dft_door_alias
            curr_door_devname = self.simulation.door_dev_pattern_generic % input
            if not curr_door_devname in existing_door_devnames:
                self.simulation.door_devname = curr_door_devname
                self.simulation.door_alias = input
                name_in_use = False
            else:
                print "%s already in use (%s)" % (input,curr_door_devname)

class DB(PyTango.Database):
    
    mot_ctrl_class_name = "SimuMotorCtrl"
    mot_ctrl_dev_pattern_generic = "simulator/motctrl/%s"
    mot_ctrl_dev_pattern = mot_ctrl_dev_pattern_generic % "motctrl*"
    mot_class_name = "SimuMotor"
    mot_dev_pattern_generic = "simulator/%s/mot*"

    counter_ctrl_class_name = "SimuCoTiCtrl"
    counter_ctrl_dev_pattern_generic = "simulator/counterctrl/%s"
    counter_ctrl_dev_pattern = counter_ctrl_dev_pattern_generic % "counterctrl*"
    counter_class_name = 'SimuCounter'
    counter_dev_pattern_generic = "simulator/%s/counter*"
    
    pool_class_name = "Pool"
    pool_dev_pattern_generic = "simulator/pool/%s"
    pool_dev_pattern = pool_dev_pattern_generic % "pool*"
    
    ms_class_name = "MacroServer"
    ms_dev_pattern_generic = "simulator/macroserver/%s"
    ms_dev_pattern = ms_dev_pattern_generic % "ms*"
    door_class_name = "Door"
    door_dev_pattern_generic = "simulator/door/%s"
    door_dev_pattern = door_dev_pattern_generic % "door*"
    
    
    def __init__(self, host=None, port=None):
        if host and port:
            PyTango.Database.__init__(self, host, int(port))
        else:
            PyTango.Database.__init__(self)
        
    def get_existing_door_devices(self):
        return self.db.get_device_member(self.door_dev_pattern)
    
    def get_existing_ms_devices(self):
        return self.db.get_device_member(self.ms_dev_pattern)

    def get_existing_pool_devices(self):
        return self.db.get_device_member(self.pool_dev_pattern)
    
    def get_existing_motctrl_devices(self):
        return self.db.get_device_member(self.mot_ctrl_dev_pattern)

    def get_existing_counterctrl_devices(self):
        return self.db.get_device_member(self.counter_ctrl_dev_pattern)

    def get_existing_server_ids(self, full_systems=False):
        l1 = self.__get_existing_server_ids(self.ms_class_name + "/Simulation*")
        l2 = self.__get_existing_server_ids(self.pool_class_name + "/Simulation*")
        l3 = self.__get_existing_server_ids(self.mot_ctrl_class_name + "/Simulation*")
        l4 = self.__get_existing_server_ids(self.counter_ctrl_class_name + "/Simulation*")

        if full_systems:
            return [ x for x in l1 if x in l2 and x in l3 and x in l4 ]
        else:
            return list(set(l1 + l2 + l3 + l4 ))

    def get_next_server_id(self):
        i = self.__get_next_server_id(self.ms_class_name + "/Simulation*")
        i = max(i, self.__get_next_server_id(self.pool_class_name + "/Simulation*"))
        i = max(i, self.__get_next_server_id(self.mot_ctrl_class_name + "/Simulation*"))
        i = max(i, self.__get_next_server_id(self.counter_ctrl_class_name + "/Simulation*"))
        return i
    
    def get_next_ms_server(self):
        return self.__get_next_server(self.ms_class_name + "/Simulation*")

    def get_next_pool_server(self):
        return self.__get_next_server(self.pool_class_name + "/Simulation*")
    
    def get_next_motorctrl_server(self):
        return self.__get_next_server(self.mot_ctrl_class_name + "/Simulation*")

    def get_next_counterctrl_server(self):
        return self.__get_next_server(self.counter_ctrl_class_name + "/Simulation*")
    
    def get_next_door_device(self):
        return self.__get_next_devices(self.door_dev_pattern,1)[0]
    
    def get_next_ms_device(self):
        return self.__get_next_devices(self.ms_dev_pattern,1)[0]

    def get_next_pool_device(self):
        return self.__get_next_devices(self.pool_dev_pattern,1)[0]
    
    def get_next_motorctrl_device(self):
        return self.__get_next_devices(self.mot_ctrl_dev_pattern,1)[0]

    def get_next_counterctrl_device(self):
        return self.__get_next_devices(self.counter_ctrl_dev_pattern,1)[0]
    
    def __get_next_server_id(self, pattern):
        server_list = self.get_server_list(pattern)
        server_pattern = pattern.rstrip('*') + '%02d'
        i = 1
        while True:
            curr_server = server_pattern % i
            if curr_server in server_list:
                i += 1
                continue
            return i        
    
    def __get_next_server(self,pattern):
        server_pattern = pattern.rstrip('*') + '%02d'
        curr_server = server_pattern % self.__get_next_server_id(pattern)
    
    def __get_next_devices(self,pattern,nb):
        members = self.get_device_member(pattern)
        member_name = pattern.split('/')[2].rstrip('*') + '%02d'
        dev_name = pattern.rstrip('*') + '%02d'
        i = 1
        res = []
        while len(res) < nb:
            curr_member_name = member_name % i
            if curr_member_name in members:
                i += 1
                continue
            curr_dev_name = dev_name % i
            res.append(curr_dev_name)
            # we include the one added to avoid repeating it
            members.append(curr_member_name)
        return res
    
    def __get_existing_server_ids(self, pattern):
        server_list = self.get_server_list(pattern)
        server_pattern = pattern.rstrip('*') + '%02d'
        ret = []
        for server_id in server_list:
            l = len(server_id)
            i = int(server_id[l-2:])
            ret.append(i)
        return ret

    def delete_simulation(self, inst_name):
        inst_name = "/" + inst_name
        
        errors = []
        
        # Delete Motor Simulator
        try:
            self.delete_server(self.mot_ctrl_class_name + inst_name)
        except PyTango.DevFailed, e:
            errors.append(e)
        except:
            pass
        
        # Delete Counter Simulator
        try:
            self.delete_server(self.counter_ctrl_class_name + inst_name)
        except PyTango.DevFailed, e:
            errors.append(e)
        except:
            pass
    
        # Delete pool
        try:
            l = self.get_device_class_list(self.pool_class_name + inst_name)
            pool_devname = l[l.index(self.pool_class_name)-1]
            #  delete all pool properties before
            self.delete_device_property(pool_devname, self.db.get_device_property_list(pool_devname,'*'))
            self.delete_server(self.pool_class_name + inst_name)
        except PyTango.DevFailed, e:
            errors.append(e)
        except:
            pass
    
        # Delete macroserver
        try:
            l = self.get_device_class_list(self.ms_class_name + inst_name)
            ms_devname = l[l.index(self.ms_class_name)-1]
            #  delete all ms properties before
            self.delete_device_property(ms_devname, self.get_device_property_list(ms_devname,'*'))
            #  delete all door properties before
            door_devname = l[l.index(self.door_class_name)-1]
            self.delete_device_property(door_devname, self.get_device_property_list(door_devname,'*'))
            self.delete_server(self.ms_class_name + inst_name)
        except PyTango.DevFailed, e:
            errors.append(e)
        except:
            pass

        return errors        

class Simulation:
    
    def __init__(self, db): 
        self.db = db or DB()
        self.id = self.db.get_next_server_id()

        self.motor_server_name = "%s/Simulation%02d" % (DB.mot_ctrl_class_name, self.id) 
        self.motor_ctrl_devname = self.db.get_next_motorctrl_device()
        self.motor_ctrl_alias = self.motor_ctrl_devname.split('/')[2]
        self.motor_nb = 4
        self.motor_devnames = []
        
        self.counter_server_name = "%s/Simulation%02d" % (DB.counter_ctrl_class_name, self.id)
        self.counter_ctrl_devname = self.db.get_next_counterctrl_device()
        self.counter_ctrl_alias = self.counter_ctrl_devname.split('/')[2]
        self.counter_nb = 4
        self.counter_devnames =[]
        
        self.zerod_nb = 2
        
        self.pool_server_name = "%s/Simulation%02d" % (DB.pool_class_name, self.id)
        self.pool_devname = self.db.get_next_pool_device()
        self.pool_alias = self.pool_devname.split('/')[2]
        self.pool_path = ["/home/tiago/test/pool/lib"]
        self.pool_id = int(self.pool_server_name[len(self.pool_server_name)-2:])
        self.mot_ctrl_inst_name = 'simumotctrl%02d' % self.pool_id
        self.uxtimer_ctrl_inst_name = 'simuuxtimerctrl%02d' % self.pool_id
        self.counter_ctrl_inst_name = 'simucounterctrl%02d' % self.pool_id
        self.zerod_ctrl_inst_name = 'simuzerodctrl%02d' % self.pool_id
        
        self.pool_proxy = None
        
        self.ms_server_name = "%s/Simulation%02d" % (DB.ms_class_name, self.id)
        self.ms_devname = self.db.get_next_ms_device()
        self.ms_alias = self.ms_devname.split('/')[2]
        self.ms_path = ["/home/tiago/test/pool/lib"]
        self.door_devname = self.db.get_next_door_device()
        self.door_alias = self.door_devname.split('/')[2]
    
    def create_door(self):
        #create the server in the database
        door_server_info = PyTango.DbDevInfo()
        door_server_info.name = self.door_devname
        door_server_info._class = self.door_class_name
        door_server_info.server = self.ms_server_name
        self.db.add_device(door_server_info)

        #create the alias
        if self.door_alias:
            self.db.put_device_alias(self.door_devname, self.door_alias)
        
        #put macroserver property
        self.db.put_device_property(self.door_devname, 
                                    {"MacroServerName" : [self.ms_devname]})
        
    def create_ms(self):
        #create the server in the database
        ms_server_info = PyTango.DbDevInfo()
        ms_server_info.name = self.ms_devname
        ms_server_info._class = self.ms_class_name
        ms_server_info.server = self.ms_server_name
        self.db.add_device(ms_server_info)

        #create the alias
        if self.ms_alias:
            self.db.put_device_alias(self.ms_devname, self.ms_alias)
        
        #put macropath property
        self.db.put_device_property(self.ms_devname, 
                                    {"MacroPath" : self.ms_path,
                                     "PoolNames" : [self.pool_devname]})
        
    def create_pool(self):
        #create the server in the database
        pool_server_info = PyTango.DbDevInfo()
        pool_server_info.name = self.pool_devname
        pool_server_info._class = self.pool_class_name
        pool_server_info.server = self.pool_server_name
        self.db.add_device(pool_server_info)

        #create the alias
        if self.pool_alias:
            self.db.put_device_alias(self.pool_devname, self.pool_alias)
        
        #put poolpath property
        self.db.put_device_property(self.pool_devname, {"PoolPath" : self.pool_path})
        
        self.pool_proxy = PyTango.DeviceProxy(self.pool_devname)
        
    def fill_pool(self):
        online = True
        try:
            self.pool_proxy.ping()
        except:
            online = False

        if online:
            self.__fill_pool_online()
        else:
            self.__fill_pool_offline()        
        
    def __fill_pool_motor(self, motor_devname):
        m = PyTango.DeviceProxy(motor_devname)
        pi = m.attribute_query('Position')
        pi.min_value, pi.max_value = '-1000','1000'
        pi.alarms.min_alarm, pi.alarms.max_alarm = '-950', '950'
        pi.alarms.min_warning, pi.alarms.max_warning = '-900', '900'
        pi.label = "Position"
        pi.unit = "mm"
        
        vi = m.attribute_query('Velocity')
        vi.min_value, vi.max_value = '0', '1000'
        vi.alarms.min_alarm, vi.alarms.max_alarm = '10', '990'
        vi.alarms.min_warning, vi.alarms.max_warning = '20', '980'
        vi.label = "Speed"
        vi.unit = "mm/s"

        ai = m.attribute_query('Acceleration')
        ai.min_value, ai.max_value = '0', '10'
        ai.alarms.min_alarm, ai.alarms.max_alarm = '0', '6'
        ai.alarms.min_warning, ai.alarms.max_warning = '0', '5'
        ai.label = "accel"
        ai.unit = "s"

        di = m.attribute_query('Deceleration')
        di.min_value, di.max_value = '0', '10'
        di.alarms.min_alarm, di.alarms.max_alarm = '0', '6'
        di.alarms.min_warning, di.alarms.max_warning = '0', '5'
        di.label = "decel"
        di.unit = "s"
        
        bri = m.attribute_query('Base_rate')
        bri.min_value, bri.max_value = '0', '10'
        bri.alarms.min_alarm, bri.alarms.max_alarm = '0', '6'
        bri.alarms.min_warning, bri.alarms.max_warning = '0', '5'
        bri.label = "base rate"
        bri.unit = "mm/s"

        spui = m.attribute_query('step_per_unit')
        spui.min_value, spui.max_value = '0', '10'
        spui.alarms.min_alarm, spui.alarms.max_alarm = '0', '6'
        spui.alarms.min_warning, spui.alarms.max_warning = '0', '5'
        spui.label = "steps/unit"
        spui.unit = "steps"

        m.set_attribute_config_ex([pi,vi,ai,di,bri,spui])
        
    def __fill_pool_online(self):
        # Create Motor controller
        self.mot_ctrl_inst_name = 'simumotctrl%02d' % self.pool_id 
        self.pool_proxy.command_inout("CreateController", 
                                      ['Motor', 'SimuMotorCtrl.la', 
                                       'SimuMotorController', 
                                       self.mot_ctrl_inst_name,
                                       'DevName', self.motor_ctrl_devname])

        # Create motors 
        for i in range(len(self.motor_devnames)):
            m_name = "mot%02d_%s" % (i+1,self.mot_ctrl_inst_name)
            self.pool_proxy.command_inout("CreateMotor",([i+1],[m_name, self.mot_ctrl_inst_name]))
            self.__fill_pool_motor(m_name)
            
        
        # Create a unix timer controller
        self.uxtimer_ctrl_inst_name = 'simuuxtimerctrl%02d' % self.pool_id
        self.pool_proxy.command_inout("CreateController", 
                                      ['CounterTimer', 'UxTimerCtrl.la', 
                                       'UnixTimer', self.uxtimer_ctrl_inst_name])
        
        co_name = "timer%02d" % self.pool_id
        self.pool_proxy.command_inout("CreateExpChannel",([1],[co_name, self.uxtimer_ctrl_inst_name]))
        
        # Create counter controller
        self.counter_ctrl_inst_name = 'simucounterctrl%02d' % self.pool_id 
        self.pool_proxy.command_inout("CreateController", 
                                      ['CounterTimer', 'SimuCoTiCtrl.py', 
                                       'SimuCoTiController',
                                       self.counter_ctrl_inst_name,
                                       'DevName', self.counter_ctrl_devname])
            
        # Create Counters
        for i in range(len(self.counter_devnames)):
            co_name = "counter%02d_%s" % (i+1,self.counter_ctrl_inst_name)
            self.pool_proxy.command_inout("CreateExpChannel",([i+1],[co_name, self.counter_ctrl_inst_name]))
        
        # Create 0D Controller
        self.zerod_ctrl_inst_name = 'simuzerodctrl%02d' % self.pool_id 
        self.pool_proxy.command_inout("CreateController", 
                                      ['ZeroDExpChannel', 'SimuZeroDCtrl.la', 
                                       'SimuZeroDController',
                                       self.zerod_ctrl_inst_name])
            
        # Create 0D channels
        for i in range(self.zerod_nb):
            zd_name = "zerod%02d_%s" % (i,self.zerod_ctrl_inst_name)
            self.pool_proxy.command_inout("CreateExpChannel",([i+1],[zd_name, self.zerod_ctrl_inst_name]))
        
    def __fill_pool_offline(self):
        # Here we cheat a little: The pool is not running so we have to had
        # the controllers and elements directly as properties
        pass
    
    def change_pool_path(self, new_pool_path):
        self.pool_path = new_pool_path
        self.pool_proxy.put_property({"PoolPath" : self.pool_path})
        self.pool_proxy.init()
        
    def check_pool_ctrl_classes(self): 
        v = self.pool_proxy.read_attribute("ControllerClassList")
        
        motor_ctrl = False
        counter_ctrl = False
        uxtimer_ctrl = False
        zerod_ctrl = False
        
        for ctrl in v.value:
            if ctrl.find("SimuMotorCtrl.la") >= 0:
                if ctrl.find("SimuMotorController") >= 0:
                    motor_ctrl = True
            elif ctrl.find("SimuCoTiCtrl.py") >= 0:
                if ctrl.find("SimuCoTiController") >= 0:
                    counter_ctrl = True
            elif ctrl.find("UxTimerCtrl.la") >= 0:
                if ctrl.find("UnixTimer") >= 0:
                    uxtimer_ctrl = True
            elif ctrl.find("SimuZeroDCtrl.la") >= 0:
                if ctrl.find("ZeroDExpChannel") >= 0:
                    zerod_ctrl = True
            
        return motor_ctrl and counter_ctrl and uxtimer_ctrl and zerod_ctrl
    
    
    def create_motor_simulator(self):
        #create the server in the database
        ctrl_server_info = PyTango.DbDevInfo()
        ctrl_server_info.name = self.motor_ctrl_devname
        ctrl_server_info._class = self.mot_ctrl_class_name
        ctrl_server_info.server = self.motor_server_name
        self.db.add_device(ctrl_server_info)
        
        motor_dev_pattern = self.mot_dev_pattern_generic % self.motor_ctrl_alias
        self.motor_devnames = self.__get_next_devices(motor_dev_pattern, self.motor_nb)
        
        for motor_devname in self.motor_devnames:
            motor_server_info = PyTango.DbDevInfo()
            motor_server_info.name = motor_devname
            motor_server_info._class = self.mot_class_name
            motor_server_info.server = self.motor_server_name
            self.db.add_device(motor_server_info)
        
    def create_counter_simulator(self):
        #create the server in the database
        ctrl_server_info = PyTango.DbDevInfo()
        ctrl_server_info.name = self.counter_ctrl_devname
        ctrl_server_info._class = self.counter_ctrl_class_name
        ctrl_server_info.server = self.counter_server_name
        self.db.add_device(ctrl_server_info)
        
        counter_dev_pattern = self.counter_dev_pattern_generic % self.counter_ctrl_alias
        self.counter_devnames = self.__get_next_devices(counter_dev_pattern, self.counter_nb)
        
        for counter_devname in self.counter_devnames:
            counter_server_info = PyTango.DbDevInfo()
            counter_server_info.name = counter_devname
            counter_server_info._class = self.counter_class_name
            counter_server_info.server = self.counter_server_name
            self.db.add_device(counter_server_info)

        # adding properties
        for i in range(len(self.counter_devnames)):
            counter_devname = self.counter_devnames[i]
            mot_devname = 'not defined'
            if i >= self.motor_nb:
                mot_devname = self.motor_devnames[self.motor_nb - 1]
            else:
                mot_devname = self.motor_devnames[i]
            self.db.put_device_property(counter_devname, 
                                        {"MotorName" : [mot_devname], 
                                        'Average' : ["1"], 
                                        'Sigma' : ["150"]})
    
    def delete_simulation(self, inst_name):
        self.db.delete_simulation(inst_name)
    
def get_args(argv):
    pass

def main():
    
    try:
        args = get_args(sys.argv)
        simulator = Simulation()
        console = Console(simulator)
        console.go()
        
    except KeyboardInterrupt, e:
        print
        print "Canceled..."
        sys.exit(0)

if __name__ == "__main__":
    main()
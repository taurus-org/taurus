""" An extension to the original PyUnit providing specific Device Pool test 
    utilities """
    
from taurus.external import unittest
import PyTango
import sys
import os
import user
import subprocess
import time
import signal
import exceptions
import imp

try:
    import pexpect
except:
    print "The Pool Unit test requires pexpect python module which was not found."
    print "This module can be found at http://www.noah.org/wiki/Pexpect" 
    sys.exit(-1)

class DefaultTangoEventCallBack:
    
    def __init__(self):
        self.evt_list = []
        self.cb_executed = 0
        self.cb_error = 0
        self.verbose = False
        
    def push_event(self,event):
        self.cb_executed += 1
        self.evt_list.append(event)
        if event.err:
            self.cb_error += 1
        elif self.verbose:
            sys.stderr.write("%s\n" % str(event.attr_value.value))
            sys.stderr.flush()
            
    def getEventValues(self):
        ret = []
        for e in self.evt_list:
            if e.err:
                ret.append(None)
            else:
                ret.append(e.attr_value.value)
        return ret
    
class PoolTestCase(unittest.TestCase):       
    """An extension to the original PyUnit TestCase providing specific methods
    for DevicePool tests"""
    
    ReadyMsg        = "Ready to accept request"
    AlreadyRunning  = "This server is already running, exiting!"
    PoolExecNotFound    = "No such file or directory"
    PoolReadyMsg        = ReadyMsg
    PoolAlreadyRunning  = AlreadyRunning
    PoolMaxStartupTime  = 10
    PoolMaxShutdownTime = 10

    MotorSimulatorReadyMsg        = ReadyMsg
    MotorSimulatorAlreadyRunning  = AlreadyRunning
    MotorSimulatorMaxStartupTime  = 10
    MotorSimulatorMaxShutdownTime = 10
    
    CounterTimerSimulatorReadyMsg        = ReadyMsg
    CounterTimerSimulatorAlreadyRunning  = AlreadyRunning
    CounterTimerSimulatorMaxStartupTime  = 10
    CounterTimerSimulatorMaxShutdownTime = 10
    
    def check_empty_attribute(self, dev, att_name):
        """ check_empty_attribute(PyTango.DeviceProxy dev, string att_name) -> None
        
            Reads the given attribute from the given device and checks that the 
            received value is empty.
            
            Paramaters:
                dev: a PyTango.DeviceProxy
                att_name: a string containing the attribute name
        """
        try:
            c_list = dev.read_attribute(att_name)
            if len(c_list.value) != 0:
                self.assert_(False, "The %s attribute is not empty !! It contains: %s" % (att_name,c_list.value))
        except PyTango.DevFailed,e:
            except_value = sys.exc_info()[1]
            self.assertEqual(except_value[0]["reason"],"API_EmptyDeviceAttribute")
            self.assertEqual(except_value[0]["desc"],"cannot extract, no data in DeviceAttribute object ")
            
    def attribute_error(self, dev, att_name, err, pr = False):
        """ attribute_error(PyTango.DeviceProxy dev, string att_name, string err, bool pr = False)
        
            Reads the given attribute from the given device and checks that this
            operation generates a PyTango.DevFailed exception with its 'reason'
            being equal to the given err string. If pr is set to True then the
            exception description is sent to the output. 
        """
        try:
            c_list = dev.read_attribute(att_name)
            self.assert_(False, "The %s attribute is not in fault!!" % (att_name))
        except PyTango.DevFailed,e:
            except_value = sys.exc_info()[1]
            if pr == True:
                self._printException(except_value)
            self.assertEqual(except_value[0]["reason"], err)
            
    def wr_attribute_error(self, dev, att_val, err, pr = False):
        """ wr_attribute_error(PyTango.DeviceProxy dev, PyTango.AttributeValue att_value, string err, bool pr = False)
        
            Writes the given attribute from the given device with the given 
            value and checks that this operation generates a PyTango.DevFailed 
            exception with its 'reason' being equal to the given err string. 
            If pr is set to True then the exception description is sent to the 
            output. 
        """        
        try:
            dev.write_attribute(att_val)
            self.assert_(False,"The %s attribute is not in fault!!" % (att_val.name))
        except PyTango.DevFailed,e:
            except_value = sys.exc_info()[1]
            if pr == True: 
                self._printException(except_value)
            self.assertEqual(except_value[0]["reason"], err)

    def wrong_argument(self, dev, cmd_name, arg_list, err, pr = False):
        """ wrong_argument(PyTango.DeviceProxy dev, string cmd_name, list arg_list, string err, bool pr = False)
           
            Executes the given command with the given arguments on the given 
            device and expects a PyTango.DevFailed exception to be raised with
            its 'reason' being equal to the given err string.
            If pr is set to True then the exception description is sent to the 
            output. 
        """
        try:
            dev.command_inout(cmd_name, arg_list)
            self.assert_(False,"The %s command succeed with wrong arguments!!" % (cmd_name))
        except PyTango.DevFailed,e:
            except_value = sys.exc_info()[1]
            if pr == True:
                self._printException(except_value)
            self.assertEqual(except_value[0]["reason"], err)
                        
    def _write_attribute(self, dev, att_name, att_val):
        """ _write_attribute(PyTango.DeviceProxy dev, string att_name, object attr_val)
        
            Writes the given attribute from the given device with the given 
            value. 
        """          
        val = PyTango.AttributeValue()
        val.name = att_name
        val.value = att_val
        dev.write_attribute(val)  
    
    def _printException(self, except_value):
        print "\nERROR desc"
        print "origin =",except_value[0]["origin"]
        print "desc =",except_value[0]["desc"]
        print "origin =",except_value[0]['origin']

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Default setup. Overwrite this methods in each test scenario when necessary
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    def getPoolPath(self):
        """getPoolPath() -> list<string>
        """
        lib_root = os.path.abspath(os.path.join(self.pool_bin_dir,"..","lib"))
        
        pydir = os.path.join(lib_root, "python")
        if not os.path.exists(pydir):
            pydir += "%d.%d" % (sys.version_info[0],sys.version_info[1]) 
        
        test_ctrl_dir = os.path.abspath(os.path.curdir)
        test_ctrl_dir = os.path.join(test_ctrl_dir,"test_ctrl")
        
        return [os.path.join(lib_root, "pool"),
                test_ctrl_dir, 
                os.path.join(lib_root,"poolcontrollers"),
                os.path.join(pydir,"site-packages")]
    
    def getMotorControllerSimulatorMaxError(self):
        return 0
    
    def getMotorSimulators(self):
        return 10 * ({ "properties" : {"_Velocity"     : ['5.0'],
                                       "_Acceleration" : ['2.0'],
                                       "_Deceleration" : ['2.0'],
                                       "_Base_rate"    : ['0.01'] },
                     },)
    
    def getCounterTimerSimulators(self):
        ret = []
        for i in xrange(10):
            mot_name = "%s/simmot/test%03d" % (self.username, i+1)
            ret.append({ "properties" : {"Average"   : ['1.0'],
                                         "Sigma"     : ['250.0'],
                                         "MotorName" : [mot_name] },
            },)
        return ret
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Generic methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def deleteFromDB(self, server_name, server_instance):
        server_name = server_name.lower()
        server_instance = server_instance.lower()
        server = server_name + '/' + server_instance
        servers = [ s.lower() for s in self.tango_db.get_server_list(server_name + '/*') ]        
        if server in servers:
            devices = self.tango_db.get_device_name(server, '*')
            
            for d in devices:
                if not d.startswith('dserver'):
                    props = self.tango_db.get_device_property_list(d, '*')
                    self.tango_db.delete_device_property(d, props)
                    self.tango_db.delete_device(d)
            
            self.tango_db.delete_server(server)    
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Test requirements. Overwrite as necessary 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def needsPool(self):
        return True
    
    def needsMotorSimulator(self):
        return False
    
    def needsCounterTimerSimulator(self):
        return False

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Pre and Post test methods 
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def setUp(self):
        """Default setUp."""
        self.prepare()
        self.start()
        
    def tearDown(self):
        """Default tearDown."""
        self.stop()
        self.cleanUp()
    
    def start(self):
        """Default startup. Starts Simulators and Device Pool"""
        self.startMotorSimulator()
        self.startCounterTimerSimulator()
        self.startPool()
    
    def stop(self):
        """Default stop. Stops Simulators and Device Pool"""
        self.stopPool()
        self.stopCounterTimerSimulator()
        self.stopMotorSimulator()
            
    def prepare(self):
        """Prepares everything to be run"""
        self.tango_db = PyTango.Database()
        self.username = os.getlogin()
        self.common_ds_instance = self.username + "_test"
        self.prepareMotorSimulator()
        self.prepareCounterTimerSimulator()
        self.prepareDevicePool()
    
    def cleanUp(self):
        """Cleans the Database"""
        self.deletePoolFromDB()
        self.deleteCounterTimerSimulatorFromDB()
        self.deleteMotorSimulatorFromDB()    
    
    def prepareMotorSimulator(self):
        """Prepare the Motor Simulator local variables and registers in the Database"""
        
        if not self.needsMotorSimulator():
            return
        
        self.motsim_ds_instance = self.common_ds_instance
        self.motsim_ctrl_dev_name = self.username + "/simmotctrl/test"
        self.motsim_process = None
        self.motsim_start_time = -1
        self.motsim_stopt_time = -1
        self.motsim_exec = None
        
        # Make sure the python device server code is reachable
        try:
            f, self.motsim_exec, desc = imp.find_module('SimuMotorCtrl')
            f.close()
            f, path, desc = imp.find_module('SimuMotor')
            f.close()
        except exceptions.ImportError, e:
            self.assert_(False, e.message)
        
        # Cleanup the database
        self.deleteMotorSimulatorFromDB()
        
        # Create a new instance in database
        self.createMotorSimulatorInDB()
    
    def createMotorSimulatorInDB(self):
        """Registers the Motor Simulator in the Database"""
        
        if not self.needsMotorSimulator():
            return
        
        # Create the motor controller simulator 
        ctrl_server_info = PyTango.DbDevInfo()
        ctrl_server_info.name   = self.motsim_ctrl_dev_name
        ctrl_server_info._class = 'SimuMotorCtrl'
        ctrl_server_info.server = 'SimuMotorCtrl/' + self.motsim_ds_instance
        self.tango_db.add_device(ctrl_server_info)
        
        # Add the MaxError property
        props = { 'MaxError': [str(self.getMotorControllerSimulatorMaxError())] }
        self.tango_db.put_device_property(ctrl_server_info.name, props)
        
        # Create the motor simulators
        mots = self.getMotorSimulators()
        
        mot_idx = 1
        for mot in mots:
            mot_info = PyTango.DbDevInfo()
            mot_info.name   = "%s/simmot/test%03d" % (self.username, mot_idx)
            mot_info._class = 'SimuMotor'
            mot_info.server = 'SimuMotorCtrl/' + self.motsim_ds_instance
            self.tango_db.add_device(mot_info)
            self.tango_db.put_device_property(mot_info.name, mot['properties'])
            mot_idx += 1

    def deleteMotorSimulatorFromDB(self):
        """Unregisters the Motor Simulator from the Database"""
        
        if not self.needsMotorSimulator():
            return

        self.deleteFromDB('SimuMotorCtrl', self.motsim_ds_instance)
    
    def prepareCounterTimerSimulator(self):
        """Prepare the Counter Timer Simulator local variables and registers in the Database"""
        
        if not self.needsCounterTimerSimulator():
            return
        
        self.ctsim_ds_instance = self.common_ds_instance
        self.ctsim_ctrl_dev_name = self.username + "/simctctrl/test"
        self.ctsim_process = None
        self.ctsim_start_time = -1
        self.ctsim_stopt_time = -1
        self.ctsim_exec = None
        
        # Make sure the python device server code is reachable
        try:
            f, self.ctsim_exec, desc = imp.find_module('SimuCoTiCtrl')
            f.close()
            f, path, desc = imp.find_module('SimuCounter')
            f.close()
        except exceptions.ImportError, e:
            self.assert_(False, e.message)
        
        self.ctsim_exec = self.ctsim_exec
        
        # Cleanup the database
        self.deleteCounterTimerSimulatorFromDB()
        
        # Create a new instance in database
        self.createCounterTimerSimulatorInDB()
    
    def createCounterTimerSimulatorInDB(self):
        """Registers the Counter Timer Simulator in the Database"""
        
        if not self.needsCounterTimerSimulator():
            return
        
        # Create the motor controller simulator 
        ctrl_server_info = PyTango.DbDevInfo()
        ctrl_server_info.name   = self.ctsim_ctrl_dev_name
        ctrl_server_info._class = 'SimuCoTiCtrl'
        ctrl_server_info.server = 'SimuCoTiCtrl/' + self.ctsim_ds_instance
        self.tango_db.add_device(ctrl_server_info)
        
        # Create the counter timer simulators
        cts = self.getCounterTimerSimulators()
        
        ct_idx = 1
        for ct in cts:
            ct_info = PyTango.DbDevInfo()
            ct_info.name   = "%s/simct/test%03d" % (self.username, ct_idx)
            ct_info._class = 'SimuCounter'
            ct_info.server = 'SimuCoTiCtrl/' + self.ctsim_ds_instance
            self.tango_db.add_device(ct_info)
            self.tango_db.put_device_property(ct_info.name, ct['properties'])
            ct_idx += 1

    def deleteCounterTimerSimulatorFromDB(self):
        """Unregisters the Counter Timer Simulator from the Database"""
        
        if not self.needsCounterTimerSimulator():
            return
        
        self.deleteFromDB('SimuCoTiCtrl', self.ctsim_ds_instance)
                
    def prepareDevicePool(self):
        """Prepare the Device Pool local variables and registers in the Database"""
        
        if not self.needsPool():
            return
        
        self.pool_ds_instance = self.common_ds_instance
        self.pool_dev_name = self.username + "/pool/test"
        self.pool_process = None
        self.pool_start_time = -1
        self.pool_stopt_time = -1
        self.pool_exec = None
        
        for path in os.getenv("PATH").split(":"):
            path = os.path.join(path,"Pool")
            if os.path.exists(path):
                self.pool_exec = path
                break
                
        self.failIf(self.pool_exec is None, "Could not find Pool executable. Make sure it is in the PATH")
        
        self.pool_bin_dir = os.path.dirname(self.pool_exec)

        self.deletePoolFromDB()
        
        self.createPoolInDB()
        
        self.pool_dp = PyTango.DeviceProxy(self.pool_dev_name)

    def createPoolInDB(self):
        """Registers the Device Pool in the Database"""
        
        if not self.needsPool():
            return
        
        # Create the device pool in the database 
        pool_server_info = PyTango.DbDevInfo()
        pool_server_info.name   = self.pool_dev_name
        pool_server_info._class = 'Pool'
        pool_server_info.server = 'Pool/' + self.pool_ds_instance
        self.tango_db.add_device(pool_server_info)
        
        # Add the PoolPath property
        props = { 'PoolPath': self.getPoolPath() }
        self.tango_db.put_device_property(pool_server_info.name, props)
        
    def deletePoolFromDB(self):
        """Unregisters the Device Pool from the Database"""
        
        if not self.needsPool():
            return
        
        self.pool_dp = None
        
        self.deleteFromDB('Pool', self.pool_ds_instance)
    
    def waitPoolStop(self):
        """Waits for the Device Pool process (if any) to stop orderly."""
        if self.pool_process is None:
            return 0
        
        idx = self.pool_process.expect(["Exiting", 
                                        pexpect.EOF, 
                                        pexpect.TIMEOUT],
                                        timeout=PoolTestCase.PoolMaxShutdownTime)
        if idx == 0:
            pass 
        elif idx == 1:
            self.assert_(False, "Device Pool terminated unexpectedly (before 'Exiting')")
        elif idx == 2:
            self.assert_(False, "Device Pool shutdown time exceeded")

        idx = self.pool_process.expect(["Exited", 
                                        pexpect.EOF, 
                                        pexpect.TIMEOUT],
                                        timeout=PoolTestCase.PoolMaxShutdownTime)
        if idx == 0:
            pass 
        elif idx == 1:
            self.assert_(False, "Device Pool terminated unexpectedly (before 'Exited')")
        elif idx == 2:
            self.assert_(False, "Device Pool shutdown time exceeded")
        
        try:
            ret = self.pool_process.wait()
            self.pool_process = None
        except:
            #if the process has already terminated before the call to wait()
            ret = self.pool_process.exitstatus
            self.pool_process = None
        
        self.failUnless(ret==0, "Device Pool terminated with exitcode = %d"%ret)
        
        return ret
    
    def startPool(self):
        """Starts the Device pool"""
        
        if not self.needsPool():
            return
        
        self.pool_process = pexpect.spawn(self.pool_exec,
                                          args = [self.pool_ds_instance])
        # make sure the device pool sends events 
        self.pool_process.delayafterterminate = 2
        
        idx = self.pool_process.expect([PoolTestCase.PoolReadyMsg, 
                                        PoolTestCase.PoolAlreadyRunning,
                                        pexpect.EOF, 
                                        pexpect.TIMEOUT],
                                        timeout=PoolTestCase.PoolMaxStartupTime)
        
        if idx == 0:
            return
        elif idx == 1:
            self.assert_(False, PoolTestCase.PoolAlreadyRunning) 
        elif idx == 2:
            self.assert_(False, "Device Pool terminated unexpectedly")
        elif idx == 3:
            self.assert_(False, "Device Pool startup time exceeded")
    
    def stopPool(self):
        """Stops the Device Pool"""
        
        if not self.needsPool():
            return

        if self.pool_process is None:
            return

        if not self.pool_process.isalive():
            return
        
        self.pool_process.terminate()
        if self.pool_process.isalive():
            # flush any existing output
            self.pool_process.close()
            if not self.pool_process.isalive():
                ret = self.pool_process.exitstatus
                self.failUnless(ret==0, "Device Pool terminated with exitcode = %d"%ret)
                return
        else:
            ret = self.pool_process.exitstatus
            self.failUnless(ret==0, "Device Pool terminated with exitcode = %d"%ret)
            return
        
        self.pool_process.terminate(force=True)
        if not self.pool_process.isalive():
            self.assert_(False, "Device Pool hangs: Forced to do a SIGKILL")
        
        self.assert_(False, "Device Pool hangs EVEN with SIGKILL")
            
    def startMotorSimulator(self):
        """Starts the Motor Simulator"""
        
        if not self.needsMotorSimulator():
            return
        
        self.motsim_process = pexpect.spawn("python",
                                            args = [self.motsim_exec,
                                                    self.motsim_ds_instance])
        
        idx = self.motsim_process.expect([PoolTestCase.MotorSimulatorReadyMsg, 
                                          PoolTestCase.MotorSimulatorAlreadyRunning,
                                          pexpect.EOF, 
                                          pexpect.TIMEOUT],
                                         timeout=PoolTestCase.MotorSimulatorMaxStartupTime)
        
        if idx == 0:
            return
        elif idx == 1:
            self.assert_(False, PoolTestCase.MotorSimulatorAlreadyRunning) 
        elif idx == 2:
            self.assert_(False, "Motor Simulator terminated unexpectedly")
        elif idx == 3:
            self.assert_(False, "Motor Simulator startup time exceeded")
        
    def stopMotorSimulator(self):
        """Stops the Motor Simulator"""

        if not self.needsMotorSimulator():
            return

        if self.motsim_process is None:
            return

        if not self.motsim_process.isalive():
            return
        
        self.motsim_process.terminate()
        
        if self.motsim_process.isalive():
            # flush any existing output
            self.motsim_process.close()
            if not self.motsim_process.isalive():
                return
        else:
            return
        
        self.motsim_process.terminate(force=True)
        if not self.motsim_process.isalive():
            self.assert_(False, "Motor Simulator hangs: Forced to do a SIGKILL")
        
        self.assert_(False, "Motor Simulator hangs EVEN with SIGKILL")

    def startCounterTimerSimulator(self):
        """Starts the Counter Timer Simulator"""
        
        if not self.needsCounterTimerSimulator():
            return
        
        self.ctsim_process = pexpect.spawn("python",
                                           args = [self.ctsim_exec,
                                                   self.ctsim_ds_instance])
        
        idx = self.ctsim_process.expect([PoolTestCase.CounterTimerSimulatorReadyMsg, 
                                         PoolTestCase.CounterTimerSimulatorAlreadyRunning,
                                          pexpect.EOF, 
                                          pexpect.TIMEOUT],
                                         timeout=PoolTestCase.CounterTimerSimulatorMaxStartupTime)
        
        if idx == 0:
            return
        elif idx == 1:
            self.assert_(False, PoolTestCase.CounterTimerAlreadyRunning) 
        elif idx == 2:
            self.assert_(False, "Counter Timer Simulator terminated unexpectedly")
        elif idx == 3:
            self.assert_(False, "Counter Timer Simulator startup time exceeded")
        
    def stopCounterTimerSimulator(self):
        """Stops the Counter Timer Simulator"""
        
        if not self.needsCounterTimerSimulator():
            return
        
        if self.ctsim_process is None:
            return

        if not self.ctsim_process.isalive():
            return
        
        self.ctsim_process.terminate()
        
        if self.ctsim_process.isalive():
            # flush any existing output
            self.ctsim_process.close()
            if not self.ctsim_process.isalive():
                return
        else:
            return
        
        self.ctsim_process.terminate(force=True)
        if not self.ctsim_process.isalive():
            self.assert_(False, "Counter Timer Simulator hangs: Forced to do a SIGKILL")
        
        self.assert_(False, "Counter Timer Simulator hangs EVEN with SIGKILL")
           
    def startPool_PopenStyle(self):
        """Starts the Device pool"""
        
        try:
            self.pool_process = subprocess.Popen([self.pool_exec, 
                                                  self.pool_ds_instance], 
                                                 stdout=subprocess.PIPE, 
                                                 stderr=subprocess.STDOUT)
        except exceptions.OSError,e:
            if e.strerror == PoolTestCase.PoolExecNotFound:
                self.assert_(False, "Could not find Pool executable. Make sure it is in the PATH")
            else:
                raise
        
        self.failIf(self.pool_process.stdout is None, 
                    "Was not able to grab Pool output")
        
        self.pool_start_time = time.time()
        while 1:
            delta_time = time.time() - self.pool_start_time
            
            self.failIf(delta_time >= PoolTestCase.PoolMaxStartupTime,
                        "Pool startup time exceeded")
            
            line = self.pool_process.stdout.readline()
            
            if line.count(PoolTestCase.PoolReadyMsg) > 0:
                break
            
            self.failIfEqual(line, PoolTestCase.PoolAlreadyRunning, 
                             PoolTestCase.PoolAlreadyRunning)

    def stopPool_PopenStyle(self):
        """Stops the Device Pool"""
        
        self.pool_stop_time = time.time()
        if self.pool_process is None:
            return
        
        if self.pool_process.poll() is None:
            os.kill(self.pool_process.pid,signal.SIGINT)
            
        while self.pool_process.poll() is None:
            delta_time = time.time() - self.pool_stop_time
            
            if delta_time > PoolTestCase.PoolMaxShutdownTime:
                os.kill(self.pool_process.pid,signal.SIGKILL)    
                self.assert_(False, "Pool hangs: Forced to do a kill -9")
                
            time.sleep(0.2)
        
        self.failUnlessEqual(self.pool_process.returncode, 0, 
                             "Pool exited with code %d" % self.pool_process.returncode)
        self.pool_process = None
                   
    def startMotorSimulator_PopenStyle(self):
        """Starts the Motor Simulator"""
        self.motsim_process = subprocess.Popen(["python",
                                                self.motsim_exec, 
                                                self.motsim_ds_instance],
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.STDOUT,
                                               bufsize=0)

        self.failIf(self.motsim_process.stdout is None, 
                    "Was not able to grab Motor Simulator output")
        
        self.motsim_start_time = time.time()
        while 1:
            delta_time = time.time() - self.motsim_start_time
            
            self.failIf(delta_time >= PoolTestCase.MotorSimulatorMaxStartupTime,
                        "Motor Simulator startup time exceeded")

            line = self.motsim_process.stdout.readline()
            sys.stderr.write(line) 
            sys.stderr.flush()
            
            if line.count(PoolTestCase.MotorSimulatorReadyMsg) > 0:
                break
            
            self.failIfEqual(line, PoolTestCase.MotorSimulatorAlreadyRunning, 
                             PoolTestCase.MotorSimulatorAlreadyRunning)
    
    def stopMotorSimulator_PopenStyle(self):
        """Stops the Motor Simulator"""
        
        self.motsim_stop_time = time.time()
        if self.motsim_process is None:
            return
        
        os.kill(self.motsim_process.pid,signal.SIGINT)
            
        while self.motsim_process.poll() is None:
            delta_time = time.time() - self.motsim_stop_time
            
            if delta_time > PoolTestCase.MotorSimulatorMaxShutdownTime:
                os.kill(self.motsim_process.pid,signal.SIGKILL)    
                self.assert_(False, "MotorSimulator hangs: Forced to do a kill -9")
                
            time.sleep(0.2)
        
        self.failUnlessEqual(self.motsim_process.returncode, 0, 
                             "MotorSimulator exited with code %d" % self.motsim_process.returncode)
        self.motsim_process = None
    
    def startCounterTimerSimulator_PopenStyle(self):
        """Starts the CounterTimer Simulator"""
        
        self.ctsim_process = subprocess.Popen(["python",
                                               self.ctsim_exec, 
                                               self.ctsim_ds_instance], 
                                               stdout=subprocess.PIPE, 
                                               stderr=subprocess.STDOUT)
        
        self.failIf(self.ctsim_process.stdout is None, 
                    "Was not able to grab CounterTimer Simulator output")
        
        self.ctsim_start_time = time.time()
        while 1:
            delta_time = time.time() - self.ctsim_start_time
            
            self.failIf(delta_time >= PoolTestCase.CounterTimerSimulatorMaxStartupTime,
                        "CounterTimer Simulator startup time exceeded")
            
            line = self.ctsim_process.stdout.readline()
            
            if line.count(PoolTestCase.CounterTimerSimulatorReadyMsg) > 0:
                break
            
        self.failIfEqual(line, PoolTestCase.CounterTimerSimulatorAlreadyRunning, 
                         PoolTestCase.CounterTimerSimulatorAlreadyRunning)
        self.motsim_process = None
    
    def stopCounterTimerSimulator_PopenStyle(self):
        """Stops the CounterTimer Simulator"""
        
        self.ctsim_stop_time = time.time()
        if self.ctsim_process is None:
            return
        
        os.kill(self.ctsim_process.pid, signal.SIGINT)
            
        while self.ctsim_process.poll() is None:
            delta_time = time.time() - self.ctsim_stop_time
            
            if delta_time > PoolTestCase.CounterTimerSimulatorMaxShutdownTime:
                os.kill(self.ctsim_process.pid, signal.SIGKILL)    
                self.assert_(False, "CounterTimerSimulator hangs: Forced to do a kill -9")
                
            time.sleep(0.2)
        
        self.failUnlessEqual(self.ctsim_process.returncode, 0, 
                             "MotorSimulator exited with code %d" % self.ctsim_process.returncode)
        self.ctsim_process = None

        
class PoolTestResult(unittest.TestResult):
    """A test result class that can print formatted text results to a stream.
    """
    
    style        = 'test'
    descStyle    = 'testDescription'
    startedStyle = 'testStarted'
    successStyle = 'testSuccess'
    errorStyle   = 'testError'
    failureStyle = 'testFailure'

    def __init__(self, stream, descriptions, verbosity):
        unittest.TestResult.__init__(self)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions
        self.testsSucceeded = 0
        
    def getDescription(self, test):
        if self.descriptions:
            return test.shortDescription() or str(test)
        else:
            return str(test)

    def startTest(self, test):
        unittest.TestResult.startTest(self, test)
        s = self.stream
        desc = self.getDescription(test)
        descId = "desc%d" % self.testsRun
        statusId = "status%d" % self.testsRun
        s.write("<TR class='%s'>" \
                "<TD id='%s' class='%s'>%s</TD>" \
                "<TD id='%s' class='%s'>STARTED</TD>" % 
                (self.style, descId, self.descStyle, desc, 
                 statusId, self.startedStyle))
        s.flush()
        
    def _addFinished(self):
        s = self.stream
        s.seek(-25,1)
        s.write("testFinished'>FINISHED</TD>")
        s.flush()
        
    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)
        self.testsSucceeded += 1 
        s = self.stream
        resultId = "result%d" % self.testsRun
        self._addFinished()
        s.write("<TD id='%s' class='%s'>ok</TD>\n" % (resultId, self.successStyle))
        s.flush()
        
    def addError(self, test, err):
        unittest.TestResult.addError(self, test, err)
        s = self.stream
        resultId = "result%d" % self.testsRun
        self._addFinished()
        s.write("<TD id='%s' class='%s'>ERROR</TD>\n" % (resultId, self.errorStyle))
        s.flush()
        
    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)
        s = self.stream
        resultId = "result%d" % self.testsRun
        self._addFinished()
        s.write("<TD id='%s' class='%s'>FAIL</TD>\n" % (resultId, self.failureStyle))
        s.flush()

    def printErrors(self):
        s = self.stream
        s.write("<p><table class='test'>")
        s.write("<caption class='test'>Errors & Failures details</caption>")
        self.printErrorList("Errors", self.errors)
        self.printErrorList("Failures", self.failures)
        s.write("</table></p>")
        
    def printErrorList(self, flavour, errors):
        s = self.stream
        s.write("<tr><td class='summary%s'>%s</td></tr>" % (flavour, flavour))
        for test, err in errors:
            s.write("<tr><td class='summaryDescription'>%s</td></tr>" % self.getDescription(test))
            err = err.replace('<','&lt;').replace('>','&gt;').replace('\n','<br/>')
            s.write("<tr><td class='summaryDetails'>%s</td></tr>" % err)
            
class PoolTestSuite(unittest.TestSuite):
    """A Pool Test Suite"""
    pass

class PoolTestLoader(unittest.TestLoader):
    """A Pool Test Loader"""
    pass

class PoolTestRunner(unittest.TextTestRunner):
    """A test runner class that displays results HTML.
    """
    css = "test.css"
    
    def _makeResult(self):
        return PoolTestResult(self.stream, self.descriptions, self.verbosity)

    def printHeader(self,t):
        s = self.stream
        time_str = time.ctime(t)
        s.write("<html><head><title>Pool test</title>\n" \
                "<meta http-equiv='refresh' content='2'>\n" \
                "<link rel='stylesheet' href='%s' type='text/css'/>\n" \
                "</head>\n<body>" \
                "<p><table class='info'>" \
                "<caption class='test'>Environment Summary</caption>" \
                "<tr><td>Start time:</td><td>%s</td></tr>" \
                "<tr><td>User name:</td><td>%s</td></tr>" \
                "<tr><td>uname:</td><td>%s</td></tr>" \
                "<tr><td>python:</td><td>%s</td></tr>" \
                "<tr><td>PyTango:</td><td>%s (%s)</td></tr>" \
                "</table></p>" \
                "<p><table class='test'>" \
                "<caption class='test'>Test Summary</caption>\n" \
                "<tr><th>Test</th><th width=100>Status</th><th width=100>Result</th></tr>\n" %  
                (self.css,time_str, os.getlogin(), str(os.uname()),
                 sys.version, PyTango.Release.version, PyTango.Release.version_description ) )

        s.flush()

    def run(self, test):
        "Run the given test case or test suite."
        
        result = self._makeResult()
        
        startTime = time.time()
        self.printHeader(startTime)
        test(result)
        stopTime = time.time()
        
        timeTaken = stopTime - startTime
        
        #result.printErrors()
        #self.stream.writeln(result.separator2)
        run = result.testsRun
        
        self.stream.write("<tr><td/><td class='testSummary' colspan='2'>" \
                          "Ran %d test%s in %.3fs</td></tr>" % 
                          (run, run != 1 and "s" or "", timeTaken))
        
        failed, errored = map(len, (result.failures, result.errors))
        succeeded  = result.testsSucceeded
        
        self.stream.write("<tr><td/><td colspan='2'>" \
                          "<table><tr>" \
                          "<td class='testsFailed'>%03d FAILED</td>"\
                          "<td class='testsError'>%03d ERRORS</td>"\
                          "<td class='testsSucceeded'>%03d SUCCEEDED</td>"\
                          "</tr></table>\n" % (failed, errored, succeeded))
        self.stream.write("</table></p>")
        
        result.printErrors()
        
        self.stream.write("</body></html>")
        self.stream.flush()
        return result
    

if __name__ == "__main__":
    unittest.main()
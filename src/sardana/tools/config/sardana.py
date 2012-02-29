#!/usr/bin/env python

""" The sardana execution tool.
    Syntax:
        python sardana.py [-v] [-l] [--simulation=<mode>] [--cleanup=<True|False>] <file.xml>
        
    This tool creates and executes a sardana system from the given file.
    
    file.xml can be either:
        - a valid XML file coming from an EXCEL spreadsheet.
        - a valid XML file from the sardana schema.
        
    -v  prints an output of the generated XML file and exits
    -l  if given, this parameter activates logging
    
    --simulation=<mode>  supported modes are 'Basic', 'Best' or 'Off'. Default mode is Best.
                         Basic mode will create Dummy* controllers on the Pool
                         Best mode will create Simu* controllers and Simu like device servers
                         Off mode will create the original controllers on the Pool
    WARNING: Any other string will deactivate simulation mode and use REAL mode
    
    --cleanup=<True|False> either or not to perform a cleanup at the end. Default
                           is True.
                           If cleanup is True the database will be cleaned at 
                           shutdown time.
                           Valid True values are: 'yes', 'Yes', 'true', 'True', 'y', 'Y', '1'
                           Any other value will be interpreted as False
"""

import PyTango
import sys
import os
import time, datetime
import exceptions
import imp
import traceback
import logging
import types, operator
import json

from taurus.core.util import CodecFactory

LOG = logging.getLogger()

try:
    from lxml import etree
    LOG.info("Using lxml XML library")
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
        LOG.info("Using python native cElemenTree XML library")
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
            LOG.info("Using python native ElemenTree XML library")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree
                LOG.info("Using python normal cElemenTree XML library")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
                    LOG.info("Using python normal ElemenTree XML library")
                except ImportError:
                    LOG.critical("Could not find any suitable XML library")
                    sys.exit(1)
    
try:
    import pexpect
except:
    try:
        import pexpect23 as pexpect
        print "[WARNING]: pexpect module not found. Using local pexpect 2.3"
    except Exception,e:
        print e
        print "The Sardana requires pexpect python module which was not found."
        print "This module can be found at http://www.noah.org/wiki/Pexpect" 
        sys.exit(2)


SAR_NS = 'http://sardana.cells.es/client/framework/config'

class Process:

    ReadyMsg        = "Ready to accept request"
    AlreadyRunning  = "This server is already running, exiting!"
    MaxStartupTime  = 30
    MaxShutdownTime = 30

    def __init__(self, executable, args, name = "Process", instance = None, logfile = None, env = None):
        self._start_time = -1
        self._stop_time = -1
        self._process = None
        self._exec = executable
        self._args = args
        self._name = name
        self._instance = instance
        self._env = env
        self._logfile = logfile

    def o(self,m):
        sys.stdout.write(m)
        sys.stdout.flush()
    
    def on(self,m=''):
        self.o(m)
        sys.stdout.write('\n')
        sys.stdout.flush()

    def getInstance(self):
        return self._instance

    def start(self):
        raise RuntimeException("Not allowed to 'start' abstract Process")
        
    def stop(self):
        raise RuntimeException("Not allowed to 'stop' abstract Process")

    def getMaxStartupTime(self):
        return Process.MaxStartupTime

    def getMaxShutdownTime(self):
        return Process.MaxShutdownTime
    
class PEProcess(Process):

    def __init__(self, executable, args, name = "PEProcess", instance = None, logfile = None, env = None):
        Process.__init__(self, executable, args, name, instance, logfile, env)
    
    def start(self):
        self._start_time = datetime.datetime.now()
        self.o("Starting '%s %s' (%s, %s)... " % (self._name, self._instance, self._exec, self._args))
        try:
            self._process = pexpect.spawn(self._exec, args=self._args, logfile=self._logfile, env=self._env)
            #self.o("%s, %s, %s" % (self._exec, self._args, self._logfile))
            #self._process.logfile = sys.stderr
            
            idx = self._process.expect([Process.ReadyMsg, Process.AlreadyRunning,
                                        pexpect.EOF, pexpect.TIMEOUT],
                                        timeout=self.getMaxStartupTime())
        except Exception,e:
            self.on("[FAILED]")
            raise e
            
        if idx == 0:
            started = datetime.datetime.now()
            dt = started - self._start_time
            self.on("(took %s) [DONE]" % str(dt))
            return

        self.on("[FAILED]")

        if idx == 1:
            raise Exception("%s %s already running" % (self._name, self._instance))
        elif idx == 2:
            raise Exception("%s %s terminated unexpectedly" % (self._name, self._instance))
        elif idx == 3:
            raise Exception("%s %s startup time exceeded" % (self._name, self._instance))
    
    def terminate(self):
        if self._process is None:
            raise Exception("No process")
        return self._process.terminate()
    
    def kill(self):
        if not self._process is None:
            self._process.close()
            res = self._process.terminate(force=True)
            self._process = None
        self.on("[DONE]")
        return
    
    def stop(self, max_shutdown_time=None):
        """Stops"""
        self._stop_time = datetime.datetime.now()
        self.o("Stopping '%s %s'... " % (self._name, self._instance))
        
        try:
            
            max_shutdown_time = max_shutdown_time or self.getMaxShutdownTime()
            
            if self._process is None:
                self.on(" (no process) [DONE]")
                return

            if not self._process.isalive():
                self.on(" (already dead) [DONE]")
                return
            
            try:
                res = self.terminate()
                idx = self._process.expect(['Exiting','Exited', pexpect.EOF, pexpect.TIMEOUT],
                                           timeout = max_shutdown_time)
            except Exception,e:
                self.on("[FAILED]")
                raise e
                
            if idx == 0:
                self.o(".")
            elif idx == 1:
                self.on(" (terminated before expected: Exited) [DONE]")
                return
            elif idx == 2:
                self.on(" (terminated before expected: EOF) [DONE]")
                return
            elif idx == 3:
                self.o(" (shutdown time exceeded). Forcing... ")
                self.kill()
                return
                
            try:
                idx = self._process.expect(['Exited', pexpect.EOF, pexpect.TIMEOUT],
                                           timeout = 5)
            except Exception,e:
                self.on("[FAILED]")
                raise e
            
            if idx == 0:
                self.o(".")
            elif idx == 1:
                self.on(" (terminated before expected: EOF) [DONE]")
            elif idx == 2:
                self.on(" (shutdown time exceeded) [DONE]")
                self.kill()
                return

            try:
                idx = self._process.expect([pexpect.EOF, pexpect.TIMEOUT],
                                           timeout = 5)
            except Exception,e:
                self.on("[FAILED]")
                raise e
        
            if idx == 0:
                runtime = self._stop_time - self._start_time
                stopped = datetime.datetime.now() - self._stop_time
                self.on(". (ran for %s ;took %s) [DONE]" % (str(runtime), str(stopped)))
            elif idx == 1:
                self.o(" (shutdown time exceeded). Forcing... ")
                self.kill()

        except KeyboardInterrupt, ki:
            self.o("(Ctrl-C during stop). Forcing... ")
            self.kill()

    def run(self, timeout = 0):
        if not self._process:
            return
        try:
            res = self._process.read_nonblocking(size = 10000, timeout = timeout)
            
            #self.on(" \t[READ %s.%s] {%s}" % (self._name, self._instance, res))
            
        except pexpect.TIMEOUT:
            # no data was available. Don't worry: it just means that in the mean
            # time no data was sent to the output/err by the daemon
            pass
        except pexpect.EOF:
            # The process terminated. Maybe to something about it in the future
            self.on("%s %s terminated before expected: (EOF)" % (self._name, self._instance))
            self._process = None


class PEDeviceServerProcess(PEProcess):

    def __init__(self, executable, args, name = "PEDeviceServerProcess", instance = None, db = None, logfile = None):
        db = db or PyTango.Database()
        env = os.environ.copy()
        env["TANGO_HOST"] = "%s:%s" % (db.get_db_host(), db.get_db_port())
        PEProcess.__init__(self, executable, args, name, instance, logfile, env)

    def getServerName(self):
        return os.path.splitext(os.path.basename(self._exec))[0]

    def terminate(self):
        tango_host_port = self._env['TANGO_HOST']
        dserver_device_name = "%s/dserver/%s/%s" % (tango_host_port, self.getServerName(), self._instance)
        dserver_device = PyTango.DeviceProxy(dserver_device_name)
        dserver_device.command_inout("Kill")
        PEProcess.terminate(self)

class PEPythonDeviceServerProcess(PEDeviceServerProcess):

    def getServerName(self):
        return os.path.splitext(os.path.basename(self._args[0]))[0]


class PESimuMotorProcess(PEPythonDeviceServerProcess):

    def __init__(self, instname, db = None, logfile = None):
        name = "Motor Simulator"
        # Make sure the python device server code is reachable
        try:
            f, fname, desc = imp.find_module('SimuMotorCtrl')
            if f: f.close()
            f, path, desc = imp.find_module('SimuMotor')
            if f: f.close()
        except exceptions.ImportError, e:
            msg = "Could not find %s executable.\n" \
                  "Make sure PYTHONPATH points to the directory(ies) where " \
                  "SimuMotorCtrl.py and SimuMotor.py files are installed" % name
            raise Exception(msg)
        
        fname = os.path.join(fname,'SimuMotorCtrl.py')
        
        PEDeviceServerProcess.__init__(self, "/usr/bin/python", [fname, instname], name, instname, db, logfile)
    
  
class PESimuCounterTimerProcess(PEPythonDeviceServerProcess):

    def __init__(self, instname, db = None, logfile = None):
        name = "Counter/Timer Simulator"
        # Make sure the python device server code is reachable
        try:
            f, fname, desc = imp.find_module('SimuCoTiCtrl')
            if f: f.close()
        except exceptions.ImportError, e:
            msg = "Could not find %s executable.\n" \
                  "Make sure PYTHONPATH points to the directory(ies) where " \
                  "SimuCoTiCtrl.py file is installed" % name
            raise Exception(msg)
        
        fname = os.path.join(fname,'SimuCoTiCtrl.py')
        
        PEDeviceServerProcess.__init__(self, "/usr/bin/python", [fname, instname], name, instname, db, logfile)


class PEPySignalSimulatorProcess(PEPythonDeviceServerProcess):

    def __init__(self, instname, db = None, logfile = None):
        name = "PySignal Simulator"
        # Make sure the python device server code is reachable
        try:
            f, fname, desc = imp.find_module('PySignalSimulator')
            if f: f.close()
        except exceptions.ImportError, e:
            msg = "Could not find %s executable.\n" \
                  "Make sure PYTHONPATH points to the directory where " \
                  "PySignalSimulator.py is installed" % name
            raise Exception(msg)
        
        fname = os.path.join(fname,'PySignalSimulator.py')
        
        PEDeviceServerProcess.__init__(self, "/usr/bin/python", [fname, instname], name, instname, db, logfile)


class PEDevicePoolProcess(PEDeviceServerProcess):

    def __init__(self, instname, db = None, logfile = None):
        name = "Device Pool"
        ex = None
        for path in os.getenv("PATH").split(":"):
            path = os.path.join(path,"Pool")
            if os.path.exists(path):
                ex = path
                break
        
        if ex is None:
            raise Exception("Could not find %s executable" % name)
        
        args = [instname, "--log-level=info"]
        PEDeviceServerProcess.__init__(self, ex, args, name, instname, db, logfile)

        
class PEMacroServerProcess(PEDeviceServerProcess):

    def __init__(self, instname, db = None, logfile = None):
        name = "Macro Server"

        ex = None
        for path in os.getenv("PATH").split(":"):
            path = os.path.join(path,"MacroServer")
            if os.path.exists(path):
                ex = path
                break
        
        if ex is None:
            raise Exception("Could not find %s executable" % name)

        args = [instname, "--log-level=info"]
        PEDeviceServerProcess.__init__(self, ex, args, name, instname, db, logfile)


SimuMotorProcess = PESimuMotorProcess
SimuCounterTimerProcess = PESimuCounterTimerProcess
PySignalSimulatorProcess = PEPySignalSimulatorProcess
DevicePoolProcess = PEDevicePoolProcess
MacroServerProcess = PEMacroServerProcess

#____________________________________________________________________TangoServer
class TangoServer:

    klassName = "DeviceServer"

    def __init__(self, servNode, bl, createProc = False, log = False):
        if servNode is None:
            raise Exception("No XML data")
            
        self._bl = bl
        self._node = servNode
                
        self._tghost = servNode.get("tangoHost") or None
        self._db = bl.getTangoDB(self._tghost)
        
        self._complete_name = servNode.get("serverName")
        self.on("Preparing %s" % self._complete_name)
        self._klass_name, self._inst_name = self._complete_name.split("/")


        ##########################################################################
        # To prevent some disaster, just make sure the user knows that the
        # hostname where the server will be deleted and created.
        server_host = self._db.get_db_host()
        server_port = self._db.get_db_port()
        server_tango_host = server_host+':'+server_port
        pytango_tango_host = PyTango.ApiUtil.get_env_var('TANGO_HOST')
        pytango_host, pytango_port = pytango_tango_host.split(':')
        # Using socket to get ip addresses because one of the two hostnames could have domain
        import socket
        server_host_ip = socket.gethostbyname_ex(server_host)[2][0]
        pytango_host_ip = socket.gethostbyname_ex(pytango_host)[2][0]
        if (server_host_ip != pytango_host_ip) or (server_port != pytango_port):
            print '\t!!! WARNING !!! %s TANGO_HOST is not the PyTango default. You may erase the WRONG sardana definition.' % self._complete_name
            print '\tServer: %s  PyTango: %s' % (server_tango_host , pytango_tango_host)
            ans = raw_input('\tDo you _really_ want to continue? [y|N] ')
            if ans.lower() not in ['y','yes']:
                raise Exception('User cancelled the creation of %s server' % self._complete_name)
        ##########################################################################

        ##########################################################################
        # Before erasing the content in the database, we will also  create a backup
        # of all the tango devices's properties and memorized attributes "a-la jive".
        # There's an script called jive-save-config that given the parameters
        # <server_name> and <file_name> it saves the config into the specified file the
        # same way you can right-click an instance within jive and select the
        # option 'Save server data'.
        try:
            config_file_name = self._klass_name+'-'+self._inst_name+'-'+time.strftime('%Y%m%d_%H%M%S')+'.jive'
            cmd = 'TANGO_HOST=%s jive-save-config %s %s &>/dev/null' % (server_tango_host, self._complete_name, config_file_name)
            os.system(cmd)
            print 'There is a backup of the deleted server config in: %s' % config_file_name
        except:
            pass
        ##########################################################################
        

        if self.klassName != self._klass_name:
            raise Exception("Node name differs from expeced '%s' != '%s'" % (self._klass_name, self.klassName))
        
        if log:
            self._logfile = open("Log_%s_%s" % (self.klassName, self._inst_name), "w")
        else:
            self._logfile = None
            
        if createProc == True:
            self._proc = self._createProcess()
        else:
            self._proc = None

    def o(self,m):
        sys.stdout.write(m)
        sys.stdout.flush()
    
    def on(self,m=''):
        self.o(m)
        sys.stdout.write('\n')
        sys.stdout.flush()

    def setUp(self):
        """Default setUp."""
        self.prepare()
        self.start()
        
    def tearDown(self):
        """Default tearDown."""
        self.stop()
        self.cleanUp()

    def prepare(self):
        """Prepares everything to be run"""
        if not self._proc:
            self._proc = self._createProcess()

        # Cleanup the database
        self.deleteServerFromDB()
        
        # Create a new instance in database
        self.createServerInDB()

    def deleteServerFromDB(self):
        db = self._db
        server_name = self._klass_name.lower()
        server_instance = self._inst_name.lower()
        server = self._complete_name.lower()
        servers = [ s.lower() for s in db.get_server_list(server_name + '/*') ]
        if server in servers:
            devices = db.get_device_name(server, '*')
            
            for d in devices:
                if not d.startswith('dserver'):
                    props = db.get_device_property_list(d, '*')
                    db.delete_device_property(d, props)
                    db.delete_device(d)
            
            db.delete_server(server)
        
    def createServerInDB(self):
        for devNodeName in self.getDeviceNodeNames():
            
            nodes = self._node.findall(devNodeName)
            for node in nodes:
                
                dev_name = node.get("deviceName")
                if not dev_name:
                    raise Exception("%s does not have valid deviceName" % self._node)
                            
                # Create the device in the database 
                info = PyTango.DbDevInfo()
                info.name   = dev_name
                info._class = devNodeName
                info.server = self._complete_name
                self._db.add_device(info)
                
                alias = node.get("name")
                if alias:
                    self._db.put_device_alias(dev_name, alias)
                 
                props = node.findall("Property")
                if props:
                    self._putDeviceProps(dev_name, props)

    def getDeviceNodeNames(self):
        return [self._klass_name]
    
    def start(self):
        """Default start"""
        self._proc.start()
    
    def stop(self):
        """Default stop"""
        self._proc.stop()
        
    def cleanUp(self):
        """Clean up"""
        self.deleteServerFromDB()
        
    def run(self, step=True, timeout=0):
        """Run"""
        while 1:
            self._proc.run(timeout=timeout)
            if step: return
    
    def _createProcess(self):
        raise Exception("Must overwrite in subclass")

    def _putDeviceProps(self, dev_name, prop_node_list):
        props = {} 
        for p_node in prop_node_list:
            prop_name = p_node.get("name")
            data = []
            
            i_nodes = p_node.findall("Item")
            if len(i_nodes) > 0:
                for i_node in i_nodes:
                    data.append(i_node.text)
            else:
                data.append(p_node.text)
            props[prop_name] = data
        
        if props:
            self._db.put_device_property(dev_name, props)

    def getInstanceName(self):
        return self._inst_name

    def __str__(self):
        return self._complete_name


class SimuMotorServer(TangoServer):
    
    klassName = "SimuMotorCtrl"
    
    def _createProcess(self):
        return SimuMotorProcess(self._inst_name, self._db, logfile=self._logfile)

    def getDeviceNodeNames(self):
        return TangoServer.getDeviceNodeNames(self) + ["SimuMotor"]

        
class SimuCounterTimerServer(TangoServer):
    
    klassName = "SimuCoTiCtrl"
    
    def _createProcess(self):
        return SimuCounterTimerProcess(self._inst_name, self._db, logfile=self._logfile)

    def getDeviceNodeNames(self):
        return TangoServer.getDeviceNodeNames(self) + ["SimuCounter"]


class PySignalSimulatorServer(TangoServer):
    klassName = "PySignalSimulator"
    
    def _createProcess(self):
        return PySignalSimulatorProcess(self._inst_name, self._db, logfile=self._logfile)


class DevicePoolServer(TangoServer):
    
    klassName = "Pool"
    
    def _createProcess(self):
        self.dev_count = 0
        return DevicePoolProcess(self._inst_name, self._db, logfile=self._logfile)

    def _putDeviceProps(self, dev_name, prop_node_list):
        TangoServer._putDeviceProps(self, dev_name, prop_node_list)
        
    def start(self):
        """Default start"""
        self._proc.start()
        self.loadPool()

    def stop(self):
        """Default stop"""
        max_shutdown_time = self.dev_count * 0.2 + 10
        self._proc.stop(max_shutdown_time)

    def _item_node_to_value(self, attr_info, node):
        v = node.text or [i.text or [ j.text for j in i.findall("Item") ] for i in node.findall("Item")]
        return PyTango.seqStr_2_obj(v, attr_info.data_type, attr_info.data_format)

    def handle_attributes(self, dev_name, node):
        attrs = node.findall('Attribute')
        if not len(attrs):
            return
        # Take into account the possibility to have the device in another Tango Host...
        dev_name = self._tghost+'/'+dev_name
        dev = PyTango.DeviceProxy(dev_name)
        tango_attrs = dev.attribute_list_query_ex()
        tango_attrs_map = {}
        for attr in tango_attrs:
            tango_attrs_map[attr.name.lower()] = attr
        
        for attr in attrs:
            name = attr.get("name").lower()
            tango_attr = tango_attrs_map.get(name)
            if tango_attr:
                attr_info = dev.get_attribute_config_ex(name)[0]
                v_node = attr.find("Value")
                if not v_node is None:
                    v = self._item_node_to_value(tango_attr, v_node)
                    try:
                        dev.write_attribute(name, v)
                    except Exception, ex:
                        print 'SOME PROBLEMS SETTING ATTRIBUTE VALUE FOR DEVICE',dev_name,'ATTRIBUTE',tango_attr.name,'VALUE',str(v)
                        print 'EXCEPTION:',ex
                
                c_node = attr.find("Configuration")
                if not c_node is None:
                    disp_node = c_node.find("Display")
                    if not disp_node is None:
                        attr_info.label = disp_node.get("label") or attr_info.label
                        attr_info.format = disp_node.get("format") or attr_info.format
                    units_node = c_node.find("Units")
                    if not units_node is None:
                        attr_info.unit = units_node.get("unit") or attr_info.unit
                        attr_info.display_unit = units_node.get("display_unit") or attr_info.display_unit
                        attr_info.standard_unit = units_node.get("standard_unit") or attr_info.standard_unit
                    range_node = c_node.find("Range")
                    if not range_node is None:
                        attr_info.min_value = range_node.get("min") or attr_info.min_value
                        attr_info.max_value = range_node.get("max") or attr_info.max_value
                    alarms_node = c_node.find("Alarms")
                    if not alarms_node is None:
                        attr_info.alarms.min_warning = alarms_node.get("min_warning") or attr_info.alarms.min_warning
                        attr_info.alarms.max_warning = alarms_node.get("max_warning") or attr_info.alarms.max_warning
                        attr_info.alarms.min_alarm = alarms_node.get("min_alarm") or attr_info.alarms.min_alarm
                        attr_info.alarms.max_alarm = alarms_node.get("max_alarm") or attr_info.alarms.max_alarm
                
                    e_node = attr.find("Events")
                    if not e_node is None:
                        ch_node = e_node.find("ChangeEvent")
                        if not ch_node is None:
                            attr_info.events.ch_event.abs_change = ch_node.get("absolute") or attr_info.events.ch_event.abs_change
                            rel = ch_node.get("relative")
                            if rel:
                                rel = rel.rstrip('%')
                                attr_info.events.ch_event.rel_change = rel
                    
                    p_node = attr.find("Polling")
                    if not p_node is None:
                        polled = p_node.get("polled") or 'False'
                        polled = not (polled.lower() in ('false','no', 'n', '0'))
                        if polled:
                            try:
                                period = int(p_node.get("period") or 0)
                                dev.poll_attribute(name, period)
                            except:
                                print dev_name,tango_attr.name
    
                    try:
                        dev.set_attribute_config(attr_info)
                    except Exception,e:
                        print 'COULD NOT SET THE FOLLOWING CONFIG FOR DEVICE',dev_name,'ATTR', tango_attr.name
                        print 'ATTRIBUTE INFO:',attr_info
                        print 'EXCEPTION:',e

        intrument_node = node.find("InstrumentRef")        
        if not intrument_node is None:
            try:
                value = intrument_node.text.strip()
                dev.write_attribute('Instrument', value)
            except Exception, ex:
                print 'SOME PROBLEMS SETTING INSTRUMENT VALUE FOR DEVICE',dev_name,'VALUE',value
                print 'EXCEPTION:',ex

                
    def loadPool(self):
        start_load_time = datetime.datetime.now()
        self.on("  Loading 'Device Pool %s'..." % self._inst_name)        

        try:
            tgHost = self._node.get("tangoHost") or \
                     ("%s:%s" % (self._db.get_db_host(), self._db.get_db_port()))
            
            pool = self._node.find(self.klassName)
            
            pool_dev_name = "%s/%s" % (tgHost, pool.get("deviceName"))
            
            pool_dp = PyTango.DeviceProxy(pool_dev_name)
            
            factory = CodecFactory()
            elements = factory.decode(pool_dp.elements, ensure_ascii='True')['new']
            
            ctrl_classes_info = {}
            for elem in elements:
                if elem['type'] != 'ControllerClass':
                    continue
                ctrl_classes_info[elem['name']] = elem

            count = 0           
            # Setup instruments
            instruments = pool.xpath("Instrument")
            self.o("    Creating instruments ")
            for instrument in instruments:
                try:
                    name = instrument.get("name")
                    if name.startswith('#'):
                        self.o("x")
                        continue
                    if name.startswith('REAL'):
                        self.o('R')
                    else:
                        self.o(".")
                    kclass = instrument.get("class")
                    pars = name, kclass
                    pool_dp.command_inout("CreateInstrument", pars)
                    count += 1
                except:
                    self.on("[FAILED]")
                    raise
            self.on(" (%d) [DONE]" % count)

            ctrls = pool.xpath("Controller[@type != 'PseudoMotor' and @type != 'PseudoCounter']")
            self.o("    Creating controllers ")
            count = 0
            self.dev_count = 0            
            for ctrl in ctrls:
                try:
                    name = ctrl.get("name")
                    # skip controllers which name starts with '#'
                    if name.startswith('#'):
                        self.o("x")
                        continue
                    if name.startswith('REAL'):
                        self.o('R')
                    else:
                        self.o(".")
                    type = ctrl.get("type")
                    if type == 'CounterTimer':
                        type = 'CTExpChannel'
                    lib = ctrl.get("lib")
                    kclass = ctrl.get("class")
                    pars = [type, lib, kclass, name]
                    props = ctrl.findall("Property")
                    for p in props:
                        pars.append(p.get("name"))
                        pars.append(p.text or '\n'.join([i.text for i in p.findall("Item")]))
                    pars = map(str.strip, pars)
                    pool_dp.command_inout("CreateController", pars)
                    self.run(step = True) # to flush any output generated by the pool
                    count += 1
                except:
                    self.on("[FAILED]")
                    raise
            self.on(" (%d) [DONE]" % count)
            
            ctrls = pool.xpath("Controller[@type = 'Motor']")
            self.o("    Creating motors ")
            count = 0
            for ctrl in ctrls:
                name = ctrl.get("name")
                elems = ctrl.findall("Motor")
                # skip motor creation for controllers which name starts with '#'
                if name.startswith('#'):
                    elems = []
                for e in elems:
                    try:
                        axis = e.get("axis")
                        aliasName = e.get("name")
                        deviceName = e.get("deviceName") or ""
                        # skip motor creation for alias starting with '#'
                        if aliasName.startswith('#'):
                            self.o('x')
                            continue
                        self.o(".")
                        #pars = [ [axis], [ aliasName, name ] ]
                        pars = "Motor", name, axis, aliasName
                        if deviceName.count('/') == 2:
                            pars.append(deviceName)
                        pars = map(str.strip, pars)
                        pool_dp.command_inout("CreateElement", pars)

                        self.handle_attributes(aliasName, e)
                        
                        self.run(step = True) # to flush any output generated by the pool
                        count += 1
                        self.dev_count += 1
                    except:
                        self.on("[FAILED]")
                        raise
            self.on(" (%d) [DONE]" % count)
            
            ctrls = pool.xpath("Controller[@type = 'CounterTimer']")
            self.o("    Creating Counter/Timers ")
            count = 0
            for ctrl in ctrls:
                name = ctrl.get("name")
                elems = ctrl.findall("CounterTimer")
                # skip counter/timers creation for controllers which name starts with '#'
                if name.startswith('#'):
                    elems = []
                for e in elems:
                    try:
                        axis = e.get("axis")
                        aliasName = e.get("name")
                        deviceName = e.get("deviceName") or ""
                        # skip counter/timers creation for alias starting with '#'
                        if aliasName.startswith('#'):
                            self.o('x')
                            continue
                        self.o(".")
                        pars = "CTExpChannel", name, axis, aliasName
                        if deviceName.count('/') == 2:
                            pars.append(deviceName)
                        pars = map(str.strip, pars)
                        pool_dp.command_inout("CreateElement", pars)

                        self.handle_attributes(aliasName, e)
                        
                        self.run(step = True) # to flush any output generated by the pool
                        count += 1
                        self.dev_count += 1
                    except:
                        self.on("[FAILED]")
                        raise
            self.on(" (%d) [DONE]" % count)
                    
            ctrls = pool.xpath("Controller[@type = 'ZeroDExpChannel']")
            self.o("    Creating 0Ds ")
            count = 0
            for ctrl in ctrls:
                name = ctrl.get("name")
                elems = ctrl.findall("ZeroDExpChannel")
                # skip 0Ds creation for controllers which name starts with '#'
                if name.startswith('#'):
                    elems = []
                for e in elems:
                    try:
                        axis = e.get("axis")
                        aliasName = e.get("name")
                        deviceName = e.get("deviceName") or ""
                        # skip 0Ds creation for alias starting with '#'
                        if aliasName.startswith('#'):
                            self.o('x')
                            continue
                        self.o(".")
                        pars = "ZeroDExpChannel", name, axis, aliasName
                        if deviceName.count('/') == 2:
                            pars.append(deviceName)
                        pars = map(str.strip, pars)
                        try:
                            pool_dp.command_inout("CreateElement", pars)

                            self.handle_attributes(aliasName, e)

                        except PyTango.DevFailed, df:
                            self.on("Exception creating %s: %s" %(aliasName, str(df)))
                        self.run(step = True) # to flush any output generated by the pool
                        count += 1
                        self.dev_count += 1
                    except:
                        self.on("[FAILED]")
                        raise
            self.on(" (%d) [DONE]" % count)

            ctrls = pool.xpath("Controller[@type = 'OneDExpChannel']")
            self.o("    Creating 1Ds ")
            count = 0
            for ctrl in ctrls:
                name = ctrl.get("name")
                elems = ctrl.findall("OneDExpChannel")
                # skip 1Ds creation for controllers which name starts with '#'
                if name.startswith('#'):
                    elems = []
                for e in elems:
                    try:
                        axis = e.get("axis")
                        aliasName = e.get("name")
                        deviceName = e.get("deviceName") or ""
                        # skip 1Ds creation for alias starting with '#'
                        if aliasName.startswith('#'):
                            self.o('x')
                            continue
                        self.o(".")
                        pars = "OneDExpChannel", name, axis, aliasName
                        if deviceName.count('/') == 2:
                            pars.append(deviceName)
                        pars = map(str.strip, pars)
                        pool_dp.command_inout("CreateElement", pars)

                        self.handle_attributes(aliasName, e)

                        self.run(step = True) # to flush any output generated by the pool
                        count += 1
                        self.dev_count += 1
                    except:
                        self.on("[FAILED]")
                        raise
            self.on(" (%d) [DONE]" % count)

            ctrls = pool.xpath("Controller[@type = 'TwoDExpChannel']")
            self.o("    Creating 2Ds ")
            count = 0
            for ctrl in ctrls:
                name = ctrl.get("name")
                elems = ctrl.findall("TwoDExpChannel")
                # skip 2Ds creation for controllers which name starts with '#'
                if name.startswith('#'):
                    elems = []
                for e in elems:
                    try:
                        axis = e.get("axis")
                        aliasName = e.get("name")
                        deviceName = e.get("deviceName") or ""
                        # skip 2Ds creation for alias starting with '#'
                        if aliasName.startswith('#'):
                            self.o('x')
                            continue
                        self.o(".")
                        pars = "TwoDExpChannel", name, axis, aliasName
                        if deviceName.count('/') == 2:
                            pars.append(deviceName)
                        pars = map(str.strip, pars)
                        pool_dp.command_inout("CreateElement", pars)

                        self.handle_attributes(aliasName, e)

                        self.run(step = True) # to flush any output generated by the pool
                        count += 1
                        self.dev_count += 1
                    except:
                        self.on("[FAILED]")
                        raise
            self.on(" (%d) [DONE]" % count)
            
            ctrls = pool.xpath("Controller[@type = 'IORegister']")
            self.o("    Creating IORegisters ")
            count = 0
            for ctrl in ctrls:
                name = ctrl.get("name")
                elems = ctrl.findall("IORegister")
                # skip IORegisters creation for controllers which name starts with '#'
                if name.startswith('#'):
                    elems = []
                for e in elems:
                    try:
                        axis = e.get("axis")
                        aliasName = e.get("name")
                        deviceName = e.get("deviceName") or ""
                        # skip IORegisters creation for alias starting with '#'
                        if aliasName.startswith('#'):
                            self.o('x')
                            continue
                        self.o(".")
                        pars = "IORegister", name, axis, aliasName
                        if deviceName.count('/') == 2:
                            pars.append(deviceName)
                        pars = map(str.strip, pars)
                        pool_dp.command_inout("CreateElement", pars)

                        self.handle_attributes(aliasName, e)
                        
                        self.run(step = True) # to flush any output generated by the pool
                        count += 1
                        self.dev_count += 1
                    except:
                        self.on("[FAILED]")
                        raise
            self.on(" (%d) [DONE]" % count)
            
            #-------------------------------------------------
            # add controllers that depend on physical elements
            #-------------------------------------------------
            ctrls = pool.xpath("Controller[@type = 'PseudoMotor']")
            
            self.o("    Creating Pseudo Motors ")
            pm_ctrl_count = 0
            pm_count = 0
            for ctrl in ctrls:
                try:
                    name = ctrl.get("name")
                    # skip controllers which name starts with '#'
                    if name.startswith('#'):
                        self.o("x")
                        continue
                    self.o(".")
                    type = ctrl.get("type")
                    lib = ctrl.get("lib")
                    kclass = ctrl.get("class")
                    
                    ctrl_class_info = ctrl_classes_info[kclass]                    
                    motor_roles = ctrl_class_info['motor_roles']
                    pseudo_motor_roles = ctrl_class_info['pseudo_motor_roles']
                    pars = [type, lib, kclass, name]
                    
                    for i, e in enumerate(ctrl.findall("Motor")):
                        pars.append("%s=%s" % (motor_roles[i], e.text)) 
                                             
                    for i, e in enumerate(ctrl.findall("PseudoMotor")):
                        pars.append("%s=%s" % (pseudo_motor_roles[i], e.get('name')))

                    pm_count += len(ctrl.findall("PseudoMotor"))
                    self.dev_count += pm_count
                        
                    props = ctrl.findall("Property")
                    
                    for p in props:
                        pars.append(p.get("name"))
                        pars.append(p.text or '\n'.join([i.text for i in p.findall("Item")]))

                    pars = map(str.strip, pars)

                    pool_dp.command_inout("CreateController", pars)
                    pm_ctrl_count += 1

                    for e in ctrl.findall('PseudoMotor'):
                        self.handle_attributes(e.get("name"), e)
                    
                    self.run(step = True) # to flush any output generated by the pool
                except:
                    self.on("[FAILED]")
                    print ctrl_class_info
                    raise
            self.on(" (%d ctrls; %d pmotors) [DONE]" % (pm_ctrl_count, pm_count))
            
            
            
            ctrls = pool.xpath("Controller[@type = 'PseudoCounter']")
            
            self.o("    Creating Pseudo Counters ")
            pc_ctrl_count = 0
            pc_count = 0
            for ctrl in ctrls:
                try:
                    name = ctrl.get("name")
                    # skip controllers which name starts with '#'
                    if name.startswith('#'):
                        self.o("x")
                        continue
                    self.o(".")
                    type = ctrl.get("type")
                    lib = ctrl.get("lib")
                    kclass = ctrl.get("class")

                    ctrl_class_info = ctrl_classes_info[kclass]                    
                    counter_roles = ctrl_class_info['counter_roles']
                    pseudo_counter_roles = ctrl_class_info['pseudo_counter_roles']

                    pars = [type, lib, kclass, name]

                    for i, e in enumerate(ctrl.findall("Channel")):
                        pars.append("%s=%s" % (counter_roles[i], e.text))
                                             
                    for i, e in enumerate(ctrl.findall("PseudoCounter")):
                        pars.append("%s=%s" % (pseudo_counter_roles[i], e.get('name'))) 

                    pc_count += len(ctrl.findall("PseudoCounter"))
                    self.dev_count += pc_count
                        
                    props = ctrl.findall("Property")
                    
                    for p in props:
                        pars.append(p.get("name"))
                        pars.append(p.text or '\n'.join([i.text for i in p.findall("Item")]))

                    pars = map(str.strip, pars)

                    pool_dp.command_inout("CreateController", pars)
                    pc_ctrl_count += 1

                    for e in ctrl.findall('PseudoCounter'):
                        self.handle_attributes(e.get("name"), e)
                    
                    self.run(step = True) # to flush any output generated by the pool
                except:
                    self.on("[FAILED]")
                    raise
            self.on("(%d ctrls; %d pcounters) [DONE]" % (pc_ctrl_count, pc_count))

            measurement_groups = pool.findall("MeasurementGroup")
            self.o("    Creating Measurement Groups ")
            count = 0
            for mg in measurement_groups:
                try:
                    aliasName = mg.get("name")
                    # skip measurementgroups which name starts with '#'
                    if aliasName.startswith('#'):
                        self.o("x")
                        continue
                    self.o(".")

                    channels = mg.findall("ChannelRef")
                    pars = [ aliasName ]
                    for channel in channels:
                        pars.append(channel.get("name"))
                    pars = map(str.strip, pars)
                    pool_dp.command_inout("CreateMeasurementGroup", pars)
                    
                    self.handle_attributes(aliasName, mg)
                    
                    self.run(step = True) # to flush any output generated by the pool
                    count += 1
                    self.dev_count += 1
                except:
                    self.on("[FAILED]")
                    raise
            self.on(" (%d) [DONE]" % count)
     
            end_load_time = datetime.datetime.now()
            dt = end_load_time - start_load_time
            self.on("  Loading 'Device Pool %s'... (took %s) [DONE]" % (self._inst_name, str(dt)))
        except:
            self.on("  Loading 'Device Pool %s'... [FAILED]" % self._inst_name)
            raise


class MacroServerServer(TangoServer):
    
    klassName = "MacroServer"
    
    def _createProcess(self):
        return MacroServerProcess(self._inst_name, self._db, logfile=self._logfile)

    def getDeviceNodeNames(self):
        return TangoServer.getDeviceNodeNames(self) + ["Door"]

    def start(self):
        try:
            TangoServer.start(self)
        except:
            pass
              
                
class Sardana:  
    """Generic Sardana system"""
    
    SimulationModes = { 
        "Basic" : {           "Motor" : ("DummyMotorController.py", "DummyMotorController"),
                       "CounterTimer" : ("DummyCounterTimerController.py", "DummyCounterTimerController"),
                    "ZeroDExpChannel" : ("DummyZeroDController.py", "DummyZeroDController"),
                     "OneDExpChannel" : ("Dummy1DController.py", "'Dummy1DController"),
                     "TwoDExpChannel" : ("Dummy2DController.py", "'Dummy2DController"),
                         "IORegister" : ("DummyIORController.py", "DummyIORController") },
        "Best" :  {           "Motor" : ("SimuMotCtrl.py", "SimuMotorController"),
                       "CounterTimer" : ("SimuCTCtrl.py", "SimuCoTiController"),
                    "ZeroDExpChannel" : ("Simu0DCtrl.py", "Simu0DController"),
                     "OneDExpChannel" : ("Simu1DCtrl.py", "Simu1DController"),
                     "TwoDExpChannel" : ("Simu2DCtrl.py", "Simu2DController"),
                         "IORegister" : ("SimuIOCtrl.py", "SimuIOController"), },
        "Off" :   {           "Motor" : (None,None),
                       "CounterTimer" : (None,None),
                    "ZeroDExpChannel" : (None,None),
                     "OneDExpChannel" : (None,None),
                     "TwoDExpChannel" : (None,None),
                         "IORegister" : (None,None) },
    }
    
    def __init__(self, source, simulation="Best", cleanup=True, log=False):
    
        if type(source) in types.StringTypes:
            self._filename = source
            self._xmldoc = None
        else:
            self._xmldoc = source
            self._filename = self._xmldoc.docinfo.URL
        self._cleanup = cleanup
        self._dft_tg_db = None
        self._tg_dbs = {}
        self._simulation = simulation
        self._log = log

    def o(self,m):
        sys.stdout.write(m)
        sys.stdout.flush()
    
    def on(self,m=''):
        self.o(m)
        sys.stdout.write('\n')
        sys.stdout.flush()

    def getTangoDB(self, id = None):
        if id is None:
            if self._dft_tg_db is None:
                db = PyTango.Database()
                self._dft_tg_db = db
                dft_host = "%s:%s" % (db.get_db_host(), db.get_db_port())
                self._tg_dbs[dft_host] = db
            return self._dft_tg_db
            
        db = self._tg_dbs.get(id)
        if not db is None:
            return db
        try:
            id = str(id)
            host,port = id.split(":")
            port = int(port)
            db = PyTango.Database(host,port)
            self._tg_dbs[id] = db
            return db
        except:
            return None
                    
    def setUp(self):
        """Default setUp."""
        self.prepare()
        self.start()
        
    def tearDown(self):
        """Default tearDown."""
        self.stop()
        if self._cleanup:
            self.cleanUp()
    
    def _preprocess(self):
        start_pp_time = datetime.datetime.now()
        self.o("Preprocessing input... ")
        
        try:
            if not self.SimulationModes.has_key(self._simulation):
                return

            motSimNb   = 0
            ctSimNb    = 0
            zeroDSimNb = 0
            oneDSimNb  = 0
            twoDSimNb  = 0
            ioSimNb    = 0
            pySigSimNb = 0
                        
            sarName = self._sarNode.get("name")
            simType = self.SimulationModes.get(self._simulation)
            poolservers = self._sarNode.findall("PoolServer")
            
            SimuMotorLib, SimuMotorClass = simType["Motor"]
            SimuCoTiLib, SimuCoTiClass = simType["CounterTimer"]
            Simu0DLib, Simu0DClass = simType["ZeroDExpChannel"]
            Simu1DLib, Simu1DClass = simType["OneDExpChannel"]
            Simu2DLib, Simu2DClass = simType["TwoDExpChannel"]
            SimuIOLib, SimuIOClass = simType["IORegister"]
            
            simuMotorLibs = [ mode["Motor"][0] for mode in self.SimulationModes.values()]
            simuCoTiLibs = [ mode["CounterTimer"][0] for mode in self.SimulationModes.values()]
            simu0DLibs = [ mode["ZeroDExpChannel"][0] for mode in self.SimulationModes.values()]
            simu1DLibs = [ mode["OneDExpChannel"][0] for mode in self.SimulationModes.values()]
            simu2DLibs = [ mode["TwoDExpChannel"][0] for mode in self.SimulationModes.values()]
            simuIOLibs = [ mode["IORegister"][0] for mode in self.SimulationModes.values()]
            
            for poolserver in poolservers:
                simuMotorList = []
                pool = poolserver.find("Pool")

                # Process Motor controllers
                motctrls = pool.xpath("Controller[@type = 'Motor']")
                needsServerNumber = len(motctrls) > 1
                for ctrl in motctrls:
                    lib = ctrl.get("lib")
                    klass = ctrl.get("class")
                    
                    if self._simulation == "Off" or lib in simuMotorLibs or ctrl.get('name').startswith('REAL'):
                        continue
            
                    motSimNb += 1
                    
                    if self._simulation == "Best":
                        # add a SimuMotorServer node to the Sardana node
                        simuServer = etree.SubElement(self._sarNode, "SimuMotorServer")
                        tgHost = poolserver.get("tangoHost")
                        if tgHost: 
                            simuServer.set("tangoHost", tgHost)
                        serverName = "SimuMotorCtrl/%s" % sarName
                        if needsServerNumber:
                            serverName += "%03d" % motSimNb
                        simuServer.set("serverName", serverName)
                        
                        simuMotCtrl = etree.SubElement(simuServer, "SimuMotorCtrl")
                        simuMotCtrlName = "%s/simumotctrl/%03d" % (sarName, motSimNb)
                        simuMotCtrl.set("deviceName", simuMotCtrlName)
                        maxError = etree.SubElement(simuMotCtrl, "Property")
                        maxError.set("name","MaxError")
                        maxErrorV = etree.SubElement(maxError, "Item")
                        maxErrorV.text = "0.0"
                        
                        for m in ctrl.findall("Motor"):
                            m_nb = int(m.get('axis'))
                            simuMotor = etree.SubElement(simuServer, "SimuMotor")
                            devName = "%s/simumotctrl%03d/%03d" % (sarName, motSimNb, m_nb)
                            simuMotor.set("deviceName", devName)
                            simuMotor.set("class", "SimuMotor")
                            simuMotorList.append(simuMotor)
                    
                    # change the pool XML nodes to refer to simulator lib
                    # instead of real lib
                    map(ctrl.remove, ctrl.findall("Property"))
                    ctrl.set("lib", SimuMotorLib)
                    ctrl.set("class", SimuMotorClass)
                    
                    if self._simulation == "Best":
                        devName = etree.SubElement(ctrl, "Property")
                        devName.set("name", "DevName")
                        devNameV = etree.SubElement(devName, "Item")
                        devNameV.text = simuMotCtrlName
                
                # Process CounterTimer controllers
                ctctrls = pool.xpath("Controller[@type = 'CounterTimer' and " \
                                                "@lib != '%s' and @class != '%s']" \
                                                 % ("UxTimerCtrl.la", "UnixTimer"))
                needsServerNumber = len(ctctrls) > 1
                for ctrl in ctctrls:
                    lib = ctrl.get("lib")
                    klass = ctrl.get("class")
                    
                    if self._simulation == "Off" or lib in simuCoTiLibs or ctrl.get('name').startswith('REAL'):
                        continue
                    
                    ctSimNb += 1
                    
                    if self._simulation == "Best":
                        # add a SimuCoTiServer node to the Sardana node
                        simuServer = etree.SubElement(self._sarNode, "SimuCoTiServer")
                        tghost = poolserver.get("tangoHost")
                        if tghost: 
                            simuServer.set("tangoHost", tgHost)
                        serverName = "SimuCoTiCtrl/%s" % sarName
                        if needsServerNumber:
                            serverName += "%03d" % ctSimNb
                        simuServer.set("serverName", serverName)
                        
                        simuCoTiCtrl = etree.SubElement(simuServer,"SimuCoTiCtrl")
                        simuCoTiCtrlName = "%s/simuctctrl/%03d" % (sarName, ctSimNb)
                        simuCoTiCtrl.set("deviceName", simuCoTiCtrlName)
                        
                        motRef = 0
                        for ct in ctrl.findall("CounterTimer"):
                            ct_nb = int(ct.get('axis'))
                            simuCounter = etree.SubElement(simuServer, "SimuCounter")
                            devName = "%s/simuctctrl%03d/%03d" % (sarName, ctSimNb, ct_nb)
                            simuCounter.set("deviceName", devName)
                            simuCounter.set("class", "SimuCounter")
                            pAverage = etree.SubElement(simuCounter, "Property")
                            pAverage.set("name", "Average")
                            pAverage.set("type", "DevDouble")
                            pAverage.text = "50.0"
                    
                            pMax = etree.SubElement(simuCounter, "Property")
                            pMax.set("name", "Max")
                            pMax.set("type", "DevDouble")
                            pMax.text = "500.0"

                            pSigma = etree.SubElement(simuCounter, "Property")
                            pSigma.set("name", "Sigma")
                            pSigma.set("type", "DevDouble")
                            pSigma.text = "250.0"
                        
                            if simuMotorList:
                                pMotorName = etree.SubElement(simuCounter, "Property")
                                pMotorName.set("name", "MotorName")
                                pMotorName.set("type", "DevString")
                                pMotorName.text = simuMotorList[motRef].get("deviceName")
                                if motRef == len(simuMotorList) - 1:
                                    motRef = 0
                                else:
                                    motRef += 1
                        
                    # change the pool XML nodes to refer to simulator lib
                    # instead of real lib
                    map(ctrl.remove, ctrl.findall("Property"))
                    ctrl.set("lib", SimuCoTiLib)
                    ctrl.set("class", SimuCoTiClass)
                    if self._simulation == "Best":
                        devName = etree.SubElement(ctrl, "Property")
                        devName.set("name", "DevName")
                        devNameV = etree.SubElement(devName, "Item")
                        devNameV.text = simuCoTiCtrlName
                
                pySigSimNode = None
                
                # Process 0D controllers
                zerodctrls = pool.xpath("Controller[@type = 'ZeroDExpChannel']")
                for ctrl in zerodctrls:
                    lib = ctrl.get("lib")
                    klass = ctrl.get("class")
                    
                    if self._simulation == "Off" or lib in simu0DLibs or ctrl.get('name').startswith('REAL'):
                        continue
                    
                    zeroDSimNb += 1
                    pySigSimNb += 1
                    
                    if self._simulation == "Best":
                        if pySigSimNode is None:
                            # add a PySignalSimulator node to the Sardana node
                            pySigSimNode = etree.SubElement(self._sarNode, "PySignalSimulatorServer")
                            tghost = poolserver.get("tangoHost")
                            if tghost: 
                                pySigSimNode.set("tangoHost", tgHost)
                            serverName = "PySignalSimulator/%s" % sarName
                            pySigSimNode.set("serverName", serverName)
                        
                        simu0DCtrl = etree.SubElement(pySigSimNode, "PySignalSimulator")
                        simu0DCtrlName = "%s/PySignalSimulator/%03d" % (sarName, pySigSimNb)
                        simu0DCtrl.set("deviceName", simu0DCtrlName)
                        
                        zerods = ctrl.findall("ZeroDExpChannel")
                        
                        if len(zerods) > 0:
                            pSimAttributes = etree.SubElement(simu0DCtrl, "Property")
                            pSimAttributes.set("name", "DynamicAttributes")
                            pSimAttributes.set("type", "DevVarStringArray")
                            simAttrTempl = "zerod%03d=float(100.0+10.0*random())"
                            for i in xrange(len(zerods)):
                                pSimAttributeItem = etree.SubElement(pSimAttributes, "Item")
                                pSimAttributeItem.text = simAttrTempl % (i+1)
                        
                    # change the pool XML nodes to refer to simulator lib
                    # instead of real lib
                    map(ctrl.remove, ctrl.findall("Property"))
                    ctrl.set("lib", Simu0DLib)
                    ctrl.set("class", Simu0DClass)
                    if self._simulation == "Best":
                        attributeNames = etree.SubElement(ctrl, "Property")
                        attributeNames.set("name", "AttributeNames")
                        simAttrTempl = "%s/zerod%%03d" % simu0DCtrlName
                        for i in xrange(len(zerods)):
                            attributeNameItem = etree.SubElement(attributeNames, "Item")
                            attributeNameItem.text = simAttrTempl % (i+1)  

                # Process 1D controllers
                onedctrls = pool.xpath("Controller[@type = 'OneDExpChannel']")
                for ctrl in onedctrls:
                    lib = ctrl.get("lib")
                    klass = ctrl.get("class")
                    
                    if self._simulation == "Off" or lib in simu1DLibs or ctrl.get('name').startswith('REAL'):
                        continue
                    
                    oneDSimNb += 1
                    pySigSimNb += 1
                    
                    if self._simulation == "Best":
                        if pySigSimNode is None:
                            # add a PySignalSimulator node to the Sardana node
                            pySigSimNode = etree.SubElement(self._sarNode, "PySignalSimulatorServer")
                            tghost = poolserver.get("tangoHost")
                            if tghost: 
                                pySigSimNode.set("tangoHost", tgHost)
                            serverName = "PySignalSimulator/%s" % sarName
                            pySigSimNode.set("serverName", serverName)
                        
                        simu1DCtrl = etree.SubElement(pySigSimNode, "PySignalSimulator")
                        simu1DCtrlName = "%s/PySignalSimulator/%03d" % (sarName, pySigSimNb)
                        simu1DCtrl.set("deviceName", simu1DCtrlName)
                        
                        onedds = ctrl.findall("OneDExpChannel")
                        
                        if len(onedds) > 0:
                            pSimAttributes = etree.SubElement(simu1DCtrl, "Property")
                            pSimAttributes.set("name", "DynamicAttributes")
                            pSimAttributes.set("type", "DevVarStringArray")
                            
                            simAttrTempl = "oned%03d=DevVarLongArray([10*sin(0.01*x) for x in xrange(100)])"
                            for i in xrange(len(oneds)):
                                pSimAttributeItem = etree.SubElement(pSimAttributes, "Item")
                                pSimAttributeItem.text = simAttrTempl % (i+1)
                        
                    # change the pool XML nodes to refer to simulator lib
                    # instead of real lib
                    map(ctrl.remove, ctrl.findall("Property"))
                    ctrl.set("lib", Simu1DLib)
                    ctrl.set("class", Simu1DClass)
                    if self._simulation == "Best":
                        attributeNames = etree.SubElement(ctrl, "Property")
                        attributeNames.set("name", "AttributeNames")
                        attributeNamesV = etree.SubElement(attributeNames, "Item")
                        simAttrTempl = "%s/oned%%03d" % simu1DCtrlName
                        for i in xrange(len(oneds)):
                            attributeNameItem = etree.SubElement(attributeNames, "Item")
                            attributeNameItem.text = simAttrTempl % (i+1)  
                        
                # Process IORegister controllers
                ioctrls = pool.xpath("Controller[@type = 'IORegister']")
                for ctrl in ioctrls:
                    lib = ctrl.get("lib")
                    klass = ctrl.get("class")
                    
                    if self._simulation == "Off" or lib in simuIOLibs or ctrl.get('name').startswith('REAL'):
                        continue
                    
                    ioSimNb += 1
                    pySigSimNb += 1
                    
                    if self._simulation == "Best":
                        if pySigSimNode is None:
                            # add a PySignalSimulator node to the Sardana node
                            pySigSimNode = etree.SubElement(self._sarNode, "PySignalSimulatorServer")
                            tghost = poolserver.get("tangoHost")
                            if tghost: 
                                pySigSimNode.set("tangoHost", tgHost)
                            serverName = "PySignalSimulator/%s" % sarName
                            pySigSimNode.set("serverName", serverName)
                        
                        simuIOCtrl = etree.SubElement(pySigSimNode, "PySignalSimulator")
                        simuIOCtrlName = "%s/PySignalSimulator/%03d" % (sarName, pySigSimNb)
                        simuIOCtrl.set("deviceName", simuIOCtrlName)
                        
                        iors = ctrl.findall("IORegister")
                        
                        if len(iors) > 0:
                            pSimAttributes = etree.SubElement(simuIOCtrl, "Property")
                            pSimAttributes.set("name", "DynamicAttributes")
                            pSimAttributes.set("type", "DevVarStringArray")
                            
                            simAttrTempl = "ior%03d=int(READ and VAR('ior%03d') or WRITE and VAR('ior%03d',VALUE))"
                            for i in xrange(len(iors)):
                                pSimAttributeItem = etree.SubElement(pSimAttributes, "Item")
                                pSimAttributeItem.text = simAttrTempl % ((i+1),(i+1),(i+1))
                        
                    # change the pool XML nodes to refer to simulator lib
                    # instead of real lib
                    map(ctrl.remove, ctrl.findall("Property"))
                    ctrl.set("lib", SimuIOLib)
                    ctrl.set("class", SimuIOClass)
                    if self._simulation == "Best":
                        attributeNames = etree.SubElement(ctrl, "Property")
                        attributeNames.set("name", "AttributeNames")
                        simAttrTempl = "%s/ior%%03d" % simuIOCtrlName
                        for i in xrange(len(iors)):
                            attributeNameItem = etree.SubElement(attributeNames, "Item")
                            attributeNameItem.text = simAttrTempl % (i+1)  

            end_pp_time = datetime.datetime.now()
            dt = end_pp_time - start_pp_time
            self.on("(took %s) [DONE]" % str(dt))
        except:
            self.on("[FAILED]")
            raise
        
    def prepare(self):
        """Prepares everything to be run"""
        if not self._xmldoc:
            self._xmldoc = etree.parse(self._filename)
            
        self._sarNode = self._xmldoc.getroot()
        
        sarNodeName = "Sardana"
        
        if self._sarNode.tag != sarNodeName:
            raise Exception("<Sardana> root node not found in %s" % self._filename)

        self._preprocess()

        self.prepareMotorSimulators()
        self.prepareCounterTimerSimulators()
        self.prepareSignalSimulators()
        self.prepareDevicePools()
        self.prepareMSs()
        self.prepareServices()
        
    def prepareServices(self):
        sarName = self._sarNode.get("name")
        macro_servers = self._sarNode.findall("MacroServerServer/MacroServer")
        db = self.getTangoDB()
        
        if len(macro_servers) > 0:
            ms_dev_name = macro_servers[0].get("deviceName")
            db.register_service("Sardana", sarName, ms_dev_name)
            self._service = sarName, ms_dev_name
            return
        
        pools = self._sarNode.findall("Pool") 
        if len(pools) > 0:
            pool_dev_name = pools[0].get("deviceName")
            db.register_service("Sardana", sarName, pool_dev_name)
            self._service = sarName, pool_dev_name
            return
       
    def prepareMotorSimulators(self):
        servNodes = self._sarNode.findall("SimuMotorServer")
        
        self._motorSims = {}
        
        for servNode in servNodes:
            serv = SimuMotorServer(servNode, self, log=self._log)
            serv.prepare()
            self._motorSims[serv.getInstanceName()] = serv
            
    def prepareCounterTimerSimulators(self):
        servNodes = self._sarNode.findall("SimuCoTiServer")
        
        self._coTiSims = {}
        
        for servNode in servNodes:
            serv = SimuCounterTimerServer(servNode, self, log=self._log)
            serv.prepare()
            self._coTiSims[serv.getInstanceName()] = serv

    def prepareSignalSimulators(self):
        servNodes = self._sarNode.findall("PySignalSimulatorServer")
        
        self._signalSims = {}
        
        for servNode in servNodes:
            serv = PySignalSimulatorServer(servNode, self, log=self._log)
            serv.prepare()
            self._signalSims[serv.getInstanceName()] = serv

    def prepareDevicePools(self):
        servNodes = self._sarNode.findall("PoolServer")

        self._devicePools = {}
        
        for servNode in servNodes:
            serv = DevicePoolServer(servNode, self, log=self._log)
            serv.prepare()
            self._devicePools[serv.getInstanceName()] = serv

    def prepareMSs(self):
        servNodes = self._sarNode.findall("MacroServer")
        
        self._macServs = {}
        
        for servNode in servNodes:
            serv = MacroServerServer(servNode, self, log=self._log)
            serv.prepare()
            self._macServs[serv.getInstanceName()] = serv

    def _getServsShutdownOrder(self):
        servs  = self._macServs.values()
        servs += self._devicePools.values()
        servs += self._signalSims.values()
        servs += self._coTiSims.values()
        servs += self._motorSims.values()
        return servs

    def _getServsStartupOrder(self):
        servs  = self._motorSims.values()
        servs += self._coTiSims.values()
        servs += self._signalSims.values()
        servs += self._devicePools.values()
        servs += self._macServs.values()
        return servs
    
    def cleanUp(self):
        for s in self._getServsShutdownOrder():
            s.cleanUp()
        
        if hasattr(self, '_service') and not self._service is None:
            db = self.getTangoDB()
            db.unregister_service("Sardana", self._service[0])
    
    def start(self):
        """Default startup. Starts Simulators, Device Pool and MacroServer"""

        for s in self._getServsStartupOrder():
            s.start()

    def stop(self):
        """Default stop."""
                
        for s in self._getServsShutdownOrder():
            s.stop()
    
    def run(self):
        servs = self._getServsStartupOrder()
        self.o("Running ")
        count = 0
        while 1:
            count += 1
            if count % 10 == 0:
                self.o(":")
            for p in servs:
                p.run(step=True, timeout=0.1)
    
    def getDoc(self):
        return self._xmldoc
        
    def getRoot(self):
        return self._sarNode


if __name__ == "__main__":
    import getopt
    
    try:
        opts, pargs = getopt.getopt(sys.argv[1:], 'vl', ['simulation=','cleanup='])
    except Exception, e:
        print "ERROR:",str(e)
        print
        print __doc__
        sys.exit(3)
    
    if not len(pargs):
        print "ERROR: Please provide XML filename"
        print
        sys.exit(3)
 
    filename = pargs[0]
    
    simulation = "Best"
    cleanup = True
    just_output_and_exit = False
    activate_logging = False
    
    for opt,value in opts:
        if opt == '-l':
            activate_logging = True
        elif opt == '--simulation':
            simulation = value
        elif opt == '--cleanup':
            cleanup = value in ('yes', 'Yes', 'true', 'True', 'y', 'Y', '1')
        elif opt == '-v':
            just_output_and_exit = True
        else:
            print __doc__
            sys.exit(3)

    try:
        import to_sar
        sar_doc = to_sar.transform(filename)
    except Exception,e:
        print 'Sorry, but some problems found when trying to convert to SARDANA xml:'
        print str(e)
        
    sardana = Sardana(sar_doc, simulation=simulation, log=activate_logging, cleanup=cleanup)

    if just_output_and_exit:
        sardana.prepare()
        print etree.tostring(sardana.getRoot(), pretty_print=True)
        sys.exit(0)

    try:
        sardana.setUp()
        print "Ready!"
        sardana.run()
    except KeyboardInterrupt, e:
        print "User pressed Ctrl+C..."
    except Exception, e:
        traceback.print_exc()
        
    print "Shutting down!"
    sardana.tearDown()
    

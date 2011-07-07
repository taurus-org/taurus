import sys
import re
import weakref
import threading
import operator
import types

import PyTango

import taurus
import taurus.core.util
from taurus.core import TaurusSWDevState
from taurus.core.util.console import NoColors, TermColors
from taurus.core.util.console import NoTangoColors, TermTangoColors
from taurus.core.util.console import NoTaurusSWDevStateColors, TermTaurusSWDevStateColors

import genutils
import exception

if genutils.get_gui_mode() == 'qt4':
    import taurus.qt.qtcore.tango.macroserver
    BaseDoor = taurus.qt.qtcore.tango.macroserver.QDoor
    BaseMacroServer = taurus.qt.qtcore.tango.macroserver.QMacroServer
else:
    from taurus.core.tango.sardana.macroserver import BaseDoor, BaseMacroServer

class Plotter:
    
    def run(self):
        self.plot()
        
    def plot(self):
        try:
            import sps
        except:
            print 'sps module not available. No plotting'
            return
        
        try:
            import pylab
        except:
            print "pylab not available (try running 'spock -pylab'). No plotting"
            return
        
        door = genutils.get_door()
        
        try:
            env = dict(door.getEnvironmentObj().read().value)
        except Exception,e:
            print 'Unable to read environment. No plotting'
            print str(e)
            return
        
        program = door.getNormalName().replace('/','').replace('_','')
        try:
            array = env['ActiveMntGrp'].replace('/','').replace('_','').upper() + "0D"
            array_ENV = '%s_ENV' % array
        except:
            print 'ActiveMntGrp not defined. No plotting'
            return
        
        if not program in sps.getspeclist():
            print '%s not found. No plotting' % program
            return
        
        if not array in sps.getarraylist(program):
            print '%s not found in %s. No plotting' % (array, program)
            return
        
        if not array_ENV in sps.getarraylist(program):
            print '%s not found in %s. No plotting' % (array_ENV, program)
            return
        
        try:
            mem = sps.attach(program, array)
            mem_ENV = sps.attach(program, array_ENV)
        except Exception, e:
            print 'sps.attach error: %s. No plotting' % str(e)
            return

        # reconstruct the environment
        i, env = 0, {}
        while mem_ENV[i][0] != '':
            line = mem_ENV[i].tostring()
            eq, end = line.index('='), line.index('\x00')
            k,v = line[:eq], line[eq+1:end]
            env[k] = v
            i += 1
        
        
        labels = env['axistitles'].split(' ')
        
        col_nb = len(labels)
        
        if col_nb < 4:
            print 'No data columns available in sps'
            return
        
        rows = int(env['nopts'])
        
        m = mem.transpose()
        
        x = m[1][:rows]
        colors = 'bgrcmyk'
        col_nb = min(col_nb, len(colors)+3)
        # skip point_nb, motor and timer columns
        for i in xrange(3,col_nb):
            y = m[i][:rows]
            line, = pylab.plot(x, y, label = labels[i])
            line.linestyle = '-'
            line.linewidth = 1
            line.color = colors[i-3]
        pylab.legend()

class SpockBaseDoor(BaseDoor):
    """A CLI version of the Door device"""
    
    console_editors = ('vi','vim','nano','joe','pico','emacs')
    
    Critical = 'Critical'
    Error = 'Error'
    Info = 'Info'
    Warning = 'Warning'
    Output = 'Output'
    Debug = 'Debug'
    Result = 'Result'
    RecordData = 'RecordData'
    
    def __init__(self, name, **kw):
        self._consoleReady = kw.get("consoleReady", False)
        if not kw.has_key('silent'): kw['silent'] = False
        self._lines = []
        self._spock_state = None
        self.call__init__(BaseDoor, name, **kw)

    def get_color_mode(self):
        return genutils.get_ipapi().options.colors
    
    def _get_macroserver_for_door(self):
        ret = genutils.get_macro_server()
        return ret

    def _preprocessParameters(self, parameters):
        if type(parameters) in types.StringTypes:
            inside_str = False
            pars = []
            par = ''
            for c in parameters:
                if c == '"':
                    if inside_str:
                        inside_str = False
                        pars.append(par)
                        par = ''
                    else:
                        inside_str = True
                elif c == ' ':
                    if inside_str:
                        par += c
                    else:
                        pars.append(par)
                        par = ''
                else:
                    par += c
            if par: pars.append(par)
            return pars
        elif operator.isSequenceType(parameters):
            return parameters

    def preRunMacro(self, obj, parameters):
        return BaseDoor.preRunMacro(self, obj, self._preprocessParameters(parameters))
    
    def runMacro(self, obj, parameters=[], synch=False):
        # reimplement just to hide exceptions
        try:
            return BaseDoor.runMacro(self, obj, parameters=parameters, synch=synch)
        except:
            pass
    
    def _runMacro(self, xml, **kwargs):
        #kwargs like 'synch' are ignored in this reimplementation
        if self._spock_state != TaurusSWDevState.Running:
            print "Unable to run macro: No connection to door '%s'" % self.getSimpleName()
            raise Exception("Unable to run macro: No connection")
        if xml is None:
            xml = self.getRunningXML()
        kwargs['synch'] = True
        try:
            return BaseDoor._runMacro(self, xml, **kwargs)
        except KeyboardInterrupt:
            print '\nCtrl-C received: Aborting ...'
            self.block_lines = 0
            self.abort()
        except PyTango.DevFailed, e:
            if operator.isSequenceType(e.args) and not type(e.args) in types.StringTypes:
                reason, desc = e.args[0].reason, e.args[0].desc
                macro_obj = self.getRunningMacro()
                if reason == 'MissingParam':
                    print "Missing parameter:",desc
                    print macro_obj.getInfo().doc
                elif reason == 'WrongParam':
                    print "Wrong parameter:",desc
                    print macro_obj.getInfo().doc
                elif reason == 'UnkownParamObj':
                    print "Unknown parameter:",desc
                elif reason == 'MissingEnv':
                    print "Missing environment:",desc
                elif reason in ('API_CantConnectToDevice', 'API_DeviceNotExported'):
                    self._updateState(self._old_sw_door_state, TaurusSWDevState.Shutdown, silent=True)
                    print "Unable to run macro: No connection to door '%s'" % self.getSimpleName()
                else:
                    print "Unable to run macro:", reason, desc
                    
    def _getMacroResult(self, macro):
        ret = None
        if macro.info.hasResult():
            ret = macro.getResult()
            
            if ret is None:
                return None
            
            if macro.info.getResult().type == 'File':
                
                commit_cmd = macro.info.hints['commit_cmd']
                
                if commit_cmd == None:
                    return ret
                
                local_f_name = ret[0]
                remote_f_name = ret[1]
                line_nb = ret[3]
                commit = CommitFile(commit_cmd, local_f_name, remote_f_name)
                self.pending_commits.update( { remote_f_name : commit } )
                ip = genutils.get_ipapi()
                editor = ip.options.editor or 'vi'
                
                cmd = 'edit -x -n %s %s' % (line_nb, local_f_name)
                if not editor in self.console_editors:
                    cmd = 'bg _ip.magic("' + cmd + '")'
                ip.magic(cmd)
                # The return value of the macro was saved in a file and opened
                # with edit so we don't return anything to avoid big outputs
                # to the console
                ret = None
        return ret
    
    def plot(self):
        Plotter().run()
    
    def stateChanged(self, s, t, v):
        old_state, old_sw_state = self._old_door_state, self._old_sw_door_state
        BaseDoor.stateChanged(self, s, t, v)
        new_state, new_sw_state = self._old_door_state, self._old_sw_door_state
        self._updateState(old_sw_state, new_sw_state)
    
    def _updateState(self, old_sw_state, new_sw_state, silent=False):
        ip = genutils.get_ipapi()
        if new_sw_state == TaurusSWDevState.Running:
            ip.user_ns['DOOR_STATE'] = ""
        else:
            ip.user_ns['DOOR_STATE'] = " (OFFLINE)"
        
        if not self.isConsoleReady():
            self._spock_state = new_sw_state
            return
        
        ss = self._spock_state
        if ss is not None and ss != new_sw_state and not silent:
            if ss == TaurusSWDevState.Running:
                self.write_asynch("\nConnection to door '%s' was lost.\n" % self.getSimpleName())
            elif new_sw_state == TaurusSWDevState.Running:
                self.write_asynch("\nConnection to the door (%s) has " \
                    "been restablished\n" % self.getSimpleName())
        self._spock_state = new_sw_state

    def write_asynch(self, msg):
        self._lines.append(msg)

    def pre_prompt_hook(self, ip):
        self._flush_lines()
    
    def _flush_lines(self):
        for l in self._lines:
            self.write(l)
        self._lines = []

    def setConsoleReady(self, state):
        self._consoleReady = state
        
    def isConsoleReady(self):
        return self._consoleReady

    def write(self, msg, stream=None):
        if not self.isConsoleReady():
            return
        return BaseDoor.write(self, msg, stream=stream)

    def processRecordData(self, data):
        if data is None: return
        data = data[1]
        if data['type'] == 'plot':
            func_name = data['type']
            data = data['data']
            args, kwargs = data['args'], data['kwargs']
            # json converts strings to unicode strings but in a function call
            # python demands that the kwargs keys be strings so we need to convert
            # in python 3k this will change since all strings will be unicode
            new_kwargs = {}
            for k,v in kwargs.iteritems():
                if type(k) is unicode: k = str(k)
                new_kwargs[k] = v
            try:
                import pylab
                f = getattr(pylab, func_name)
                f(*args, **new_kwargs)
            except Exception,e:
                self.logReceived(self.Warning, ['Unable to plot:', str(e)])

    _RECORD_DATA_THRESOLD = 4*1024*1024 # 4Mb

    def _processRecordData(self, data):
        if data is None: return
        value = data.value
        format = value[0]
        size = len(value[1])
        if size > self._RECORD_DATA_THRESOLD:
            sizekb = size / 1024
            self.logReceived(self.Info, ['Received long data record (%d Kb)' % sizekb, 
                'It may take some time to process. Please wait...'])
        return BaseDoor._processRecordData(self, data)

    def _processEnvironmentData(self, data):
        obj = BaseDoor._processEnvironmentData(self, data)
        env_type = obj[1].get("__type__")
        if env_type == 'set_env':
            ip = genutils.get_ipapi()
            g_env = ip.user_ns.get(genutils.ENV_NAME)
            g_env.update(obj[1])


class QSpockDoor(SpockBaseDoor):

    def __init__(self, name, **kw):
        self.call__init__(SpockBaseDoor, name, **kw)
        
        import PyQt4.Qt
        PyQt4.Qt.QObject.connect(self, PyQt4.Qt.SIGNAL('recordDataUpdated'), self.processRecordData)


class SpockDoor(SpockBaseDoor):
    
    def _processRecordData(self, data):
        data = SpockBaseDoor._processRecordData(self, data)
        return self.processRecordData(data)


class SpockMacroServer(BaseMacroServer):
    """A CLI version of the MacroServer device"""
    
    def __init__(self, name, **kw):
        self._local_magic = {}
        self.call__init__(BaseMacroServer, name, **kw)
        
    def _addMacro(self, json_macro):
        macro_info = BaseMacroServer._addMacro(self, json_macro)
        macro_name = str(macro_info.name)
        
        def macro_fn(self, parameter_s='', name=macro_name):
            parameters = genutils.arg_split(parameter_s, posix=True)
            door = genutils.get_door()
            ret = door.runMacro(macro_name, parameters, synch=True)
            macro = door.getRunningMacro()
            if macro is not None: # maybe none if macro was aborted
                return door.getRunningMacro().getResult()
        
        macro_fn.func_name = macro_name
        macro_fn.__doc__ = str(macro_info.doc)
        
        # register magic command
        genutils.expose_magic(macro_name, macro_fn)
        self._local_magic[macro_name] = macro_fn
        
        return macro_info
    
    def _removeMacro(self, macro_name):
        BaseMacroServer._removeMacro(self, macro_name)
        #genutils.unexpose_magic(macro_name)
        del self._local_magic[macro_name]

    _SKIP_ELEMENTS = ('controller', 'controllerclass', 'motorgroup', 'instrument')

    def _addElement(self, family, elem_str):
        elem = BaseMacroServer._addElement(self, family, elem_str)
        elem_name = elem.getName()
        family_lower = family.lower()
        if family_lower in self._SKIP_ELEMENTS: return
        genutils.expose_variable(elem_name, PyTango.DeviceProxy(elem_name))
    

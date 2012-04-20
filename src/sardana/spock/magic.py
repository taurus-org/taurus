#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
##
## This file is part of Sardana
## 
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""Initial magic commands and hooks for the spock IPython environment"""

__all__ = ['expconf','showscan', 'spsplot', 'status', 'bench', 'debug_completer',
           'debug', 'www_completer', 'www', 'post_mortem_completer',
           'post_mortem', 'edmac', 'spock_late_startup_hook',
           'spock_pre_prompt_hook']


import IPython

from genutils import page, get_door, get_macro_server, ask_yes_no, arg_split
from genutils import MSG_DONE, MSG_FAILED

def expconf(self, parameter_s=''):
    """Launches a GUI for configuring the environment variables 
    for the experiments (scans)"""
    try:
        from taurus.qt.qtgui.extra_sardana import ExpDescriptionEditor
    except:
        print "Error importing ExpDescriptionEditor (hint: is taurus extra_sardana installed?)"
    doorname = get_door().name()
    w = ExpDescriptionEditor(door=doorname)
    w.show()

def showscan(self, parameter_s=''):
    """Shows a scan in a GUI.
    
    :param scan_id: scan number [default: None, meaning show last scan]"""
    params = parameter_s.split()
    door = get_door()
    online, scan_nb = False, None
    if len(params) > 0:
        if params[0].lower() == 'online':
            online = True
        else:
            scan_nb = int(params[0])
    door.show_scan(scan_nb, online=online)

def spsplot(self, parameter_s=''):
    get_door().plot()

def status(self, parameter_s=''):
    try:
        ms = get_macro_server()
    except:
        print "Not connected. Door is offline"
        return
    door = ms.getDoor()
    if door.working_state == WorkingState.ONLINE:
        door_state = door.state.read()
        print "Connected to Door %s (in %s%s%s state)" % (door.alias,TermTangoColors[door_state],door_state,TermColors.Normal)
        if door_state != PyTango.DevState.ON:
            status = door.get_status().splitlines()
            for line in status:
                print "\t"+line
    elif door.working_state == WorkingState.OFFLINE:
        print "NOT connected to Door %s. Door is offline" % door.alias
    elif door.working_state == WorkingState.SHUTDOWN:
        print "Disconnected from Door %s. Door as been shutdown" % door.alias
    elif door.working_state == WorkingState.CRASHED:
        print "Connection to Door %s was lost (Server crashed or network failed)" % door.alias
    
    if ms.working_state == WorkingState.ONLINE:
        ms_state = ms.state.read()
        print "Connected to Macro Server %s (in %s%s%s state)" % (ms.alias,TermTangoColors[ms_state],ms_state,TermColors.Normal)
        status = ms.status().splitlines()
        for line in status:
            print "\t"+line
    elif ms.working_state == WorkingState.OFFLINE:
        print "NOT connected to Macro Server %s. Door is offline" % ms.alias
    elif ms.working_state == WorkingState.SHUTDOWN:
        print "Disconnected from Macro Server %s. Macro Server as been shutdown" % ms.alias
    elif ms.working_state == WorkingState.CRASHED:
        print "Connection to Macro Server %s was lost (Server crashed or network failed)" % ms.alias
    
def bench(self, parameter_s=''):
    """Measure the execution time of a macro"""
    
    params = parameter_s.split()
    if len(params) == 0:
        print "Usage: bench macro [par ...]"
        return
    
    name = params[0]
    parameter_s = string.join(params[1:])
    
    t0 = time.time()
    door = get_door()
    door.runMacro(name, parameter_s)
    t = time.time()
    print "Execution time: %.3f sec" % (t - t0)

def debug_completer(self, event):
    # calculate parameter index
    param_idx = len(event.line.split()) - 1
    if not event.line.endswith(' '): param_idx -= 1
    if param_idx == 0:
        return ('off', 'on')

def debug(self, parameter_s=''):
    """Activate/Deactivate macro server debug output"""
    params = parameter_s.split()
    door = get_door()
    if len(params) == 0:
        s = door.getDebugMode() and 'on' or 'off'
        print "debug mode is %s" % s
        return
    elif len(params) == 1:
        s = params[0].lower()
        if not s in ('off', 'on'):
            print "Usage: debug [on|off]"
            return
        door.setDebugMode(s == 'on')
        print "debug mode is now %s" % s
    else:
        print "Usage: debug [on|off]"

def www_completer(self, event):
    # calculate parameter index
    param_idx = len(event.line.split()) - 1
    if not event.line.endswith(' '): param_idx -= 1
    if param_idx == 0:
        return get_door().log_streams

def www(self, parameter_s=''):
    """What went wrong. Reads the stream. If no stream is specified, it reads
    'debug' stream. Valid values are output, critical, error, warning, info, 
    debug, result"""
    import PyTango
    params = parameter_s.split() or ('debug',)
    door = get_door()
    logger = door.getLogObj(params[0])
    try:
        # force=True -> make sure we read the latest value from the Door server
        v = logger.getLogBuffer()
        if not v: return
        msg = "\n".join(v)
        page(msg)
    except PyTango.DevFailed, df:
        post_mortem(self, parameter_s, True)
    except Exception,e:
        door.writeln("Unexpected exception occured executing www:", stream=door.Error)
        door.writeln(str(e), stream=door.Error)
        import traceback
        traceback.print_exc()

post_mortem_completer = www_completer

def post_mortem(self, parameter_s='', from_www=False):
    """Post mortem analysis. Prints the local stream buffer. If no stream is 
    specified, it reads 'debug' stream. Valid values are output, critical, 
    error, warning, info, debug, result"""
    params = parameter_s.split() or ['debug']
    door = get_door()
    logger = door.getLogObj(params[0])
    msg = ""
    
    if from_www:
        msg = "------------------------------\n" \
              "Server is offline.\n" \
              "This is a post mortem analysis\n" \
              "------------------------------\n"
    
    for line in logger.getLogBuffer():
        if line:
            msg += "\n".join(line)
    page(msg)

def edmac(self, parameter_s=''):
    """edmac <macro name> [<module>]
    Returns the contents of the macro file which contains the macro code for
    the given macro name. If the module is given and it does not exist a new 
    one is created. If the given module is a simple module name and it does 
    not exist, it will be created on the first directory mentioned in the 
    MacroPath"""
    import os
    import tempfile
    import PyTango
    import taurus.core.util
    
    ms = get_macro_server()
    
    pars = arg_split(parameter_s, posix=True)
    
    if len(pars) == 1:
        macro_name = pars[0]
        macro_info = ms.getMacroInfoObj(macro_name)
        if macro_info is None:
            print "Macro '%s' could not be found" % macro_name
            return
        macro_lib = macro_info.module
    else:
        macro_name, macro_lib = pars

    macro_info = (macro_lib,macro_name)
    print 'Opening %s.%s...' % macro_info
    
    try:
        remote_fname, code, line_nb = ms.GetMacroCode(macro_info)
    except PyTango.DevFailed, e:
        taurus.core.util.print_DevFailed(e)
        return

    fd, local_fname = tempfile.mkstemp(prefix='spock_%s_' % pars[0], suffix='.py', text=True)
    os.write(fd, code)
    os.close(fd)

    cmd = 'edit -x -n %s %s' % (line_nb, local_fname)
    self.magic(cmd)
    
    if ask_yes_no('Do you want to apply the new code on the server?', 'y'):
        print 'Storing...',
        try:
            f = file(local_fname)
            try:
                new_code = f.read()
                ms.SetMacroCode([remote_fname, new_code])
                print MSG_DONE
            except Exception, e:
                print MSG_FAILED
                print 'Reason:', str(e)
            f.close()
        except:
            print 'Could not open file \'%s\' for safe transfer to the server' % local_fname
            print 'Did you forget to save?'
    else:
        print "Discarding changes..."
    
    #if os.path.exists(local_fname):
    #    if ask_yes_no('Delete temporary file \'%s\'?' % local_fname, 'y'):
    #        os.remove(local_fname)
    #        bkp = '%s~' % local_fname
    #        if os.path.exists(bkp):
    #            os.remove(bkp)
    try:
        os.remove(local_fname)
    except:
        pass

def spock_late_startup_hook(self):
    import sardana.spock
    try:
        #ip = IPython.ipapi.get()
        #ip.ready = True
        get_door().setConsoleReady(True)
    except:
        import traceback
        print "Exception in spock_late_startup_hook:"
        traceback.print_exc()
        
def spock_pre_prompt_hook(self):
    import sardana.spock
    try:
        get_door().pre_prompt_hook(self)
    except:
        import traceback
        print "Exception in spock_pre_prompt_hook:"
        traceback.print_exc()
 
#def spock_pre_runcode_hook(self):
#    print "spock_pre_runcode_hook"
#    return None

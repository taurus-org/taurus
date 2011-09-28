"""Initial magic commands and hooks for the spock IPython environment"""

import IPython

def spsplot(self, parameter_s=''):
    _get_door().plot()

def _get_macro_server():
    import sardana.spock.genutils
    return sardana.spock.genutils.get_macro_server()
    
def _get_door():
    import sardana.spock.genutils
    return sardana.spock.genutils.get_door()

def status(self, parameter_s=''):
    try:
        ms = MacroServer()
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
    door = _get_door()
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
    door = _get_door()
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
        return _get_door().log_streams

def www(self, parameter_s=''):
    """What went wrong. Reads the stream. If no stream is specified, it reads
    'debug' stream. Valid values are output, critical, error, warning, info, 
    debug, result"""
    import PyTango
    params = parameter_s.split() or ('debug',)
    door = _get_door()
    logger = door.getLogObj(params[0])
    try:
        # force=True -> make sure we read the latest value from the Door server
        v = logger.getLogBuffer()
        if not v: return
        msg = "\n".join(v)
        IPython.genutils.page(msg)
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
    door = _get_door()
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
    IPython.genutils.page(msg)

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
    import sardana.spock.genutils
    
    ms = _get_macro_server()
    
    import sardana.spock.genutils
    pars = sardana.spock.genutils.arg_split(parameter_s, posix=True)
    
    if len(pars) == 1:
        macro_name = pars[0]
        macro_info = ms.getMacroInfoObj(macro_name)
        if macro_info is None:
            print "Macro '%s' could not be found" % macro_name
            return
        macro_lib = macro_info.module_name
    else:
        macro_name, macro_lib = pars
    
    print 'Editing %s.%s...' % (macro_lib,macro_name)
    
    try:
        remote_fname, code, line_nb = ms.GetMacroCode([macro_lib, macro_name])
    except PyTango.DevFailed, e:
        taurus.core.util.print_DevFailed(e)
        return

    fd, local_fname = tempfile.mkstemp(prefix='spock_%s_' % pars[0], suffix='.py', text=True)
    os.write(fd, code)
    os.close(fd)

    cmd = 'edit -x -n %s %s' % (line_nb, local_fname)
    ip = IPython.ipapi.get()
    ip.magic(cmd)
    
    if sardana.spock.genutils.ask_yes_no('Do you want to apply the new code on the server?', 'y'):
        print 'Storing...',
        try:
            f = file(local_fname)
            try:
                new_code = f.read()
                ms.SetMacroCode([remote_fname, new_code])
                print sardana.spock.genutils.MSG_DONE
            except Exception, e:
                print sardana.spock.genutils.MSG_FAILED
                print 'Reason:', str(e)
            f.close()
        except:
            print 'Could not open file \'%s\' for safe transfer to the server' % local_fname
            print 'Did you forget to save?'
    
    #if os.path.exists(local_fname):
    #    if sardana.spock.genutils.ask_yes_no('Delete temporary file \'%s\'?' % local_fname, 'y'):
    #        os.remove(local_fname)
    #        bkp = '%s~' % local_fname
    #        if os.path.exists(bkp):
    #            os.remove(bkp)
    try:
        os.remove(local_fname)
    except:
        pass

def spock_input_prompt_hook(self, cont):
    try:
        return _get_door().spock_input_prompt(self.api, cont)
    except Exception,e:
        print e
        return
        import sardana.spock
        return sardana.spock.Door.spock_offline_input_prompt(self.api, cont)

def spock_output_prompt_hook(self):
    try:
        return _get_door().spock_output_prompt(self.api)
    except Exception,e:
        print e
        return
        import sardana.spock
        return sardana.spock.Door.spock_offline_output_prompt(self.api)

def spock_late_startup_hook(self):
    import sardana.spock
    try:
        ip = IPython.ipapi.get()
        ip.ready = True
        _get_door().setConsoleReady(True)
    except:
        pass

def spock_pre_prompt_hook(self):
    import sardana.spock
    try:
        _get_door().pre_prompt_hook(self)
    except:
        pass

#def spock_pre_runcode_hook(self):
#    print "spock_pre_runcode_hook"
#    return None

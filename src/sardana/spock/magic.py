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

__all__ = ['expconf', 'showscan', 'spsplot', 'debug_completer',
           'debug', 'www',
           'post_mortem', 'macrodata', 'edmac', 'spock_late_startup_hook',
           'spock_pre_prompt_hook']


from genutils import page, get_door, get_macro_server, ask_yes_no, arg_split
from genutils import MSG_DONE, MSG_FAILED
from genutils import get_ipapi


def expconf(self, parameter_s=''):
    """Launches a GUI for configuring the environment variables
    for the experiments (scans)"""
    try:
        from taurus.qt.qtgui.extra_sardana import ExpDescriptionEditor
    except:
        print "Error importing ExpDescriptionEditor "\
              "(hint: is taurus extra_sardana installed?)"
        return
    doorname = get_door().name()
        
    #===========================================================================
    ## ugly hack to avoid ipython/qt thread problems #e.g. see
    ## https://sourceforge.net/p/sardana/tickets/10/ 
    ## this hack does not allow inter-process communication and leaves the 
    ## widget open after closing spock 
    ## @todo: investigate cause of segfaults when using launching qt widgets from ipython
    # 
    #w = ExpDescriptionEditor(door=doorname)
    #w.show() #launching it like this, produces the problem of https://sourceforge.net/p/sardana/tickets/10/
    import subprocess
    import sys
    fname = sys.modules[ExpDescriptionEditor.__module__].__file__
    args = ['python', fname, doorname]
    subprocess.Popen(args)
    #===========================================================================


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


def debug_completer(self, event):
    # calculate parameter index
    param_idx = len(event.line.split()) - 1
    if not event.line.endswith(' '):
        param_idx -= 1
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


def www(self, parameter_s=''):
    """What went wrong. Prints the error message from the last macro execution"""
    import PyTango
    door = get_door()
    try:
        last_macro = door.getLastRunningMacro()
        if last_macro is None:
            door.writeln("No macro ran from this console yet!")
            return
        if not hasattr(last_macro, 'exc_stack') or last_macro.exc_stack is None:
            door.writeln("Sorry, but no exception occurred running last " \
                         "macro (%s)." % last_macro.name)
            return
        exc = "".join(last_macro.exc_stack)
        door.write(exc)
    except Exception, e:
        door.writeln("Unexpected exception occurred executing www:",
                     stream=door.Error)
        door.writeln(str(e), stream=door.Error)
        import traceback
        traceback.print_exc()


def post_mortem(self, parameter_s='', from_www=False):
    """Post mortem analysis. Prints the local stream buffer. If no stream is
    specified, it reads 'debug' stream. Valid values are output, critical,
    error, warning, info, debug, result"""
    params = parameter_s.split() or ['debug']
    door = get_door()
    logger = door.getLogObj(params[0])
    msg = ""

    if not from_www:
        try:
            msg = "\n".join(logger.read(cache=False).value)
        except:
            from_www = True
            
    if from_www:
        msg = "------------------------------\n" \
              "Server is offline.\n" \
              "This is a post mortem analysis\n" \
              "------------------------------\n"
        msg += "\n".join(logger.getLogBuffer())
    page(msg)

def macrodata(self, parameter_s=''):
    """macrodata
    
    Returns the data produced by the last macro"""
    door = get_door()
    macro_data = door.read_attribute("RecordData")

    from taurus.core.util.codecs import CodecFactory
    factory = CodecFactory()
    data = factory.decode(macro_data.value)    
    return data
    

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

    macro_info = (macro_lib, macro_name)
    print 'Opening %s.%s...' % macro_info

    try:
        remote_fname, code, line_nb = ms.GetMacroCode(macro_info)
    except PyTango.DevFailed, e:
        PyTango.Except.print_exception(e)
        return

    fd, local_fname = tempfile.mkstemp(prefix='spock_%s_' % pars[0],
                                       suffix='.py', text=True)
    os.write(fd, code)
    os.close(fd)

    cmd = 'edit -x -n %s %s' % (line_nb, local_fname)
    ip = get_ipapi()
    ip.magic(cmd)

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
            print 'Could not open file \'%s\' for safe transfer to the ' \
                  'server' % local_fname
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
    try:
        get_door().setConsoleReady(True)
    except:
        import traceback
        print "Exception in spock_late_startup_hook:"
        traceback.print_exc()


def spock_pre_prompt_hook(self):
    try:
        get_door().pre_prompt_hook(self)
    except:
        import traceback
        print "Exception in spock_pre_prompt_hook:"
        traceback.print_exc()

#def spock_pre_runcode_hook(self):
#    print "spock_pre_runcode_hook"
#    return None

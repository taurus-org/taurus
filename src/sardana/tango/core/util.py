#!/usr/bin/env python

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

""" """

__docformat__ = 'restructuredtext'

__all__ = ["GenericScalarAttr", "GenericSpectrumAttr", "GenericImageAttr",
           "tango_protect", "to_tango_state", "to_tango_type_format",
           "to_tango_type", "to_tango_access", "to_tango_attr_info",
           "prepare_tango_logging", "prepare_rconsole", "run_tango_server",
           "run"]

import functools

from PyTango import Util, DevFailed, \
    DevVoid, DevLong, DevLong64, DevBoolean, DevString, DevDouble, \
    DevVarLong64Array, DispLevel, DevState, \
    SCALAR, SPECTRUM, IMAGE, FMT_UNKNOWN, \
    READ_WRITE, READ, Attr, SpectrumAttr, ImageAttr

from sardana import State, SardanaServer, DataType, DataFormat, \
    DataAccess, DTYPE_MAP, DACCESS_MAP, to_dtype_dformat, to_daccess, Release
from sardana.pool.poolmetacontroller import DataInfo

from taurus.core.util import Enumeration

ServerRunMode = Enumeration("ServerRunMode", \
                            ("SynchPure", "SynchThread", "SynchProcess", \
                             "AsynchThread", "AsynchProcess"))

class GenericScalarAttr(Attr):
    pass


class GenericSpectrumAttr(SpectrumAttr):
    
    def __init__(self, name, tg_type, tg_access, dim_x=2048):
        SpectrumAttr.__init__(self, name, tg_type, tg_access, dim_x)


class GenericImageAttr(ImageAttr):

    def __init__(self, name, tg_type, tg_access, dim_x=2048, dim_y=2048):
        ImageAttr.__init__(self, name, tg_type, tg_access, dim_x, dim_y)


def tango_protect(wrapped, *args, **kwargs):
    @functools.wraps(wrapped)
    def wrapper(self, *args, **kwargs):
        with self.tango_lock:
            return wrapped(self, *args, **kwargs)
    return wrapper

def to_tango_state(state):
    return DevState(state)

#: dictionary dict<:class:`sardana.DataType`, :class:`PyTango.CmdArgType`>
TTYPE_MAP = {
    DataType.Integer : DevLong,
    DataType.Double  : DevDouble,
    DataType.String  : DevString,
    DataType.Boolean : DevBoolean,
}

#: dictionary dict<:class:`sardana.DataFormat`, :class:`PyTango.AttrFormat`>
TFORMAT_MAP = {
    DataFormat.Scalar : SCALAR,
    DataFormat.OneD   : SPECTRUM,
    DataFormat.TwoD   : IMAGE,
}

#: dictionary dict<:class:`sardana.DataAccess`, :class:`PyTango.AttrWriteType`>
TACCESS_MAP = {
    DataAccess.ReadOnly  : READ,
    DataAccess.ReadWrite : READ_WRITE,
}

def to_tango_access(access):
    return TACCESS_MAP.get(access, READ_WRITE)

def to_tango_type_format(dtype_or_info, dformat=None):
    dtype = dtype_or_info
    if dformat is None:
        dtype, dformat = to_dtype_dformat(dtype)
    return TTYPE_MAP.get(dtype, DevVoid), TFORMAT_MAP.get(dformat, FMT_UNKNOWN)
    
def to_tango_attr_info(attr_name, attr_info):
    if isinstance(attr_info, DataInfo):
        data_type, data_format = attr_info.dtype, attr_info.dformat
        data_access = attr_info.access
        desc = attr_info.description
    else:
        data_type, data_format = to_dtype_dformat(attr_info.get('type'))
        data_access = to_daccess(attr_info.get('r/w type'))
        desc = attr_info.get('description')
    
    tg_type, tg_format = to_tango_type_format(data_type, data_format)
    tg_access = to_tango_access(data_access)
    tg_attr_info = [ [ tg_type, tg_format, tg_access ] ]

    if desc is not None and len(desc) > 0:
        tg_attr_info.append( { 'description' : desc } )
    return attr_name, tg_attr_info
    
def clean_tango_args(args):
    ret, ret_for_tango = [], []
    
    tango_args = "-?", "-nodb", "-file="
    nb_args = len(args)
    for i in range(nb_args):
        arg = args[i]
        try:
            if arg.startswith("-v") and int(arg[2:]):
                ret_for_tango.append(arg)
                continue
        except:
            pass
        if arg.startswith('-ORB'):
            ret_for_tango.append(arg)
            i += 1
            if i < nb_args:
                ret_for_tango.append(args[i])
                i += 1
            continue
        if arg.startswith(tango_args):
            ret_for_tango.append(arg)
            continue
        if arg == "-dlist":
            ret_for_tango.append(arg)
            i += 1
            while i < nb_args and args[i][0] != "-":
                arg = args[i]
                ret_for_tango.append(arg)
                i += 1
            continue
        ret.append(arg)
    return ret, ret_for_tango
        
def prepare_cmdline(parser=None, args=None):
    """Prepares the command line separating tango options from server specific
    options.
    
    :return: a sequence of options, arguments, tango arguments
    :rtype: seq<opt, list<str>, list<str>>"""
    import optparse
    if args is None:
        args = []
    
    proc_args, tango_args = clean_tango_args(args)
    
    if parser is None:
        version = "%s" % (Release.version)
        parser = optparse.OptionParser(version=version)
    
    parser.usage = "usage: %prog instance_name [options]"
    log_level_choices = "critical", "error", "warning", "info", "debug", "trace", \
                        "0", "1", "2", "3", "4", "5"
    help_olog = "log output level. Possible values are (case sensitive): " \
                "critical (or 0), error (1), warning (2), info (3) " \
                "debug (4), trace (5) [default: %default]"
    help_flog = "log file level. Possible values are (case sensitive): " \
                "critical (or 0), error (1), warning (2), info (3) " \
                "debug (4), trace (5) [default: %default]. " \
                "Ignored if --without-log-file is True"
    help_fnlog = "log file name. When given, MUST be absolute file name. " \
                "[default: /tmp/tango/<DS name>/<DS instance name lower case>/log.txt]. " \
                "Ignored if --without-log-file is True"
    help_tango_v = "tango trace level"
    help_tango_f = "tango db file name"
    help_wflog = "When set to True disables logging into a file [default: %default]"
    help_rfoo = "rconsole port number. [default: %default meaning rconsole NOT active]"
    parser.add_option("--log-level", dest="log_level", metavar="LOG_LEVEL",
                      help=help_olog, type="choice", choices=log_level_choices, default="warning")
    parser.add_option("--log-file-level", dest="log_file_level", metavar="LOG_FILE_LEVEL",
                      help=help_flog, type="choice", choices=log_level_choices, default="debug")
    parser.add_option("--log-file-name", dest="log_file_name",
                      help=help_fnlog, type="str", default=None)
    parser.add_option("--without-log-file", dest="without_log_file",
                      help=help_wflog, default=False)
    
    parser.add_option("--rconsole-port", dest="rconsole_port",
                      metavar="RCONSOLE_PORT", help=help_rfoo, type="int", default=0)

    res = list( parser.parse_args(proc_args) )
    tango_args = res[1][:2] + tango_args
    res.append(tango_args)
    
    return res

def prepare_taurus(options, args, tango_args):
    # make sure the polling is not active
    import taurus
    factory = taurus.Factory()
    factory.disablePolling()
    
def prepare_logging(options, args, tango_args, start_time=None):
    import os.path
    import logging
    import taurus
    import taurus.core.util.log
    Logger = taurus.core.util.log.Logger
    
    taurus.setLogLevel(taurus.Debug)
    root = Logger.getRootLog()
    
    # output logger configuration
    log_output_level = options.log_level
    log_level_map  = { "0" : taurus.Critical, "critical" : taurus.Critical,
                       "1" : taurus.Error, "error" : taurus.Error,
                       "2" : taurus.Warning, "warning" : taurus.Warning,
                       "3" : taurus.Info, "info" : taurus.Info,
                       "4" : taurus.Debug, "debug" : taurus.Debug,
                       "5" : taurus.Trace, "trace" : taurus.Trace,
                     }
    log_output_level = log_level_map[log_output_level]
    root.handlers[0].setLevel(log_output_level)
    
    if not options.without_log_file:
        log_file_level = options.log_file_level
        log_file_level = log_level_map[log_file_level]
        
        # Create a file handler
        if options.log_file_name is None:
            _, ds_name = os.path.split(args[0])
            ds_name, _ = os.path.splitext(ds_name)
            ds_instance = args[-1].lower()
            path = os.path.join(os.sep, "tmp", "tango", ds_name, ds_instance)
            log_file_name = os.path.join(path, 'log.txt')
        else:
            log_file_name = options.log_file_name
        path = os.path.dirname(log_file_name)
        
        # because some versions of python have a bug in logging.shutdown (this
        # function is not protected against deleted handlers) we store the
        # handlers we create to make sure a strong reference exists when the
        # logging.shutdown is called
        taurus._handlers = handlers = []
        try:
            if not os.path.exists(path):
                os.makedirs(path, 0777)
            
            fmt = Logger.getLogFormat()
            f_h = logging.handlers.RotatingFileHandler(log_file_name, maxBytes=1E7, backupCount=5)
            f_h.setFormatter(fmt)
            
            # Create a memory handler and set the target to the file handler
            m_h = logging.handlers.MemoryHandler(10, flushLevel=taurus.Info)
            m_h.setTarget(f_h)
            handlers.append(f_h)
            
            m_h.setLevel(log_file_level)
            root.addHandler(m_h)
            handlers.append(m_h)
            
            if start_time is not None:
                taurus.info("Started at %s", start_time)
            else:
                taurus.info("Starting up...")
            taurus.info("Log is being stored in %s", log_file_name)
        except:
            if start_time is not None:
                taurus.info("Started at %s", start_time)
            else:
                taurus.info("Starting up...")
            taurus.warning("'%s' could not be created. Logs will not be stored",
                           log_file_name)
            taurus.debug("Error description", exc_info=1)

    taurus.debug("Start args=%s", args)
    taurus.debug("Start options=%s", options)

def prepare_rconsole(options, args, tango_args):
    port = options.rconsole_port
    if port is None or port is 0:
        return
    import taurus
    taurus.debug("Setting up rconsole on port %d...", port)
    try:
        import rfoo.utils.rconsole
        rfoo.utils.rconsole.spawn_server(port=port)
        taurus.debug("Finished setting up rconsole")
    except:
        taurus.debug("Failed to setup rconsole", exc_info=1)

def run_tango_server(util, start_time=None):
    import taurus
    try:
        tango_util = Util.instance()
        SardanaServer.server_state = State.Init
        tango_util.server_init()
        SardanaServer.server_state = State.Running
        if start_time is not None:
            import datetime
            dt = datetime.datetime.now() - start_time
            taurus.info("Ready to accept request in %s", dt)
        else:
            taurus.info("Ready to accept request")
        tango_util.server_run()
        SardanaServer.server_state = State.Off
    except DevFailed:
        taurus.critical("Server exited with DevFailed", exc_info=1)
    except KeyboardInterrupt:
        taurus.critical("Interrupted by keyboard")
    except Exception:
        taurus.critical("Server exited with unforeseen exception", exc_info=1)
    taurus.info("Exited")

def run(prepare_func, args=None, tango_util=None, start_time=None, mode=None):
    
    if mode is None:
        mode = ServerRunMode.SynchPure
        
    if args is None:
        if mode != ServerRunMode.SynchPure:
            raise Exception("When running in separate thread/process, " \
                            "'args' must be given")
        import sys
        args = sys.argv
    
    name = args[0]
    
    if mode != ServerRunMode.SynchPure:
        if mode in (ServerRunMode.SynchThread, ServerRunMode.AsynchThread):
            import threading
            class task_klass(threading.Thread):
                def terminate(self):
                    if not self.is_alive():
                        return
                    Util.instance().get_dserver_device().kill()
        else:
            import multiprocessing
            task_klass = multiprocessing.Process
            tango_util = None

        task_args = prepare_func,
        task_kwargs = dict(args=args, tango_util=tango_util,
                           start_time=start_time, mode=ServerRunMode.SynchPure)
        
        task = task_klass(name=name, target=run, args=task_args,
                          kwargs=task_kwargs)
        task.daemon = False
        task.start()
        if mode in (ServerRunMode.SynchThread, ServerRunMode.SynchProcess):
            task.join()
        return task
    
    options, args, tango_args = prepare_cmdline(args=args)
    if tango_util == None:
        tango_util = Util(tango_args)
    
    prepare_taurus(options, args, tango_args)
    prepare_logging(options, args, tango_args, start_time=start_time)
    prepare_rconsole(options, args, tango_args)
    prepare_func(tango_util)
    
    run_tango_server(tango_util, start_time=start_time)

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

__all__ = ["prepare_tango_logging", "prepare_rconsole", "run_tango_server", "run"]

__CMD_LINE = None, None

def prepare_cmdline(parser=None, args=None):
    import optparse
    if args is None:
        args = []
    
    if parser is None:
        parser = optparse.OptionParser()
    
    log_level_choices = "critical", "error", "warning", "info", "debug", "trace", \
                        "0", "1", "2", "3", "4", "5"
    help_olog = "log output level. Possible values are (case sensitive): " \
                "critical (or 0), error (1), warning (2), info (3) " \
                "debug (4), trace (5). Default is warning."
    help_flog = "log file level. Possible values are (case sensitive): " \
                "critical (or 0), error (1), warning (2), info (3) " \
                "debug (4), trace (5). Default is debug."
    help_fnlog = "file log name. When given, MUST be absolute file name. " \
                "Defaults to /tmp/tango/<DS name>/<DS instance name lower case>/log.txt" \
                "(unless --without-log-file is True). "
    help_wflog = "When set to True disables logging into a file. Default is False"
    help_rfoo = "rconsole port number. Default is 0 meaning rconsole NOT active"
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

    res = parser.parse_args(args)
    global __CMD_LINE
    __CMD_LINE = res
    prepare_logging(*res)
    prepare_rconsole(*res)

def prepare_logging(options, args):
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
            
        try:
            if not os.path.exists(path):
                os.makedirs(path, 0777)
            
            fmt = Logger.getLogFormat()
            f_h = logging.handlers.RotatingFileHandler(log_file_name, maxBytes=1E7, backupCount=5)
            f_h.setFormatter(fmt)
            
            # Create a memory handler and set the target to the file handler
            m_h = logging.handlers.MemoryHandler(10, flushLevel=taurus.Info)
            m_h.setTarget(f_h)
            
            m_h.setLevel(log_file_level)
            root.addHandler(m_h)
            taurus.info("Log is being stored in %s", log_file_name)
        except:
            root.warning("'%s' could not be created. Logs will not be stored", log_file_name)
            root.debug("Error description", exc_info=1)

    taurus.info("Starting up")
    taurus.debug("Start args=%s", args)
    taurus.debug("Start options=%s", options)

def prepare_rconsole(options, args):
    port = options.rconsole_port
    if port is None or port is 0:
        return
    taurus.debug("Setting up rconsole on port %d...", port)
    try:
        import rfoo.utils.rconsole
        rfoo.utils.rconsole.spawn_server(port=port)
        taurus.debug("Finished setting up rconsole")
    except:
        taurus.debug("Failed to setup rconsole", exc_info=1)

def run_tango_server():
    import PyTango
    try:
        tango_util = PyTango.Util.instance()
        tango_util.server_init()
        print "Ready to accept request"
        tango_util.server_run()
    except PyTango.DevFailed, e:
        import taurus
        taurus.critical("Server exited with DevFailed",exc_info=1)
    except Exception,e:
        import taurus
        taurus.critical("Server exited with unforeseen exception",exc_info=1)

def run(prepare_func, args=None, tango_util=None):
    if args is None:
        import sys
        args = sys.argv

    prepare_cmdline(args=args)

    if tango_util == None:
        import PyTango
        tango_util = PyTango.Util(args)

    prepare_func(tango_util)
    run_tango_server()

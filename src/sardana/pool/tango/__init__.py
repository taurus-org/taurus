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

from .PoolDevice import *
from .Controller import *
from .Motor import *
from .MotorGroup import *
from .CTExpChannel import *
from .MeasurementGroup import *
from .Pool import *


def main(use_rconsole=True):
    import PyTango
    import sys
    import optparse
    import taurus
    
    parser = optparse.OptionParser()
    
    help_v = "log level"
    parser.add_option("-v", "--log-level", dest="log_level",
                      metavar="LOG_LEVEL", help=help_v, type="int", default=2)
    options, args = parser.parse_args()
    
    log_level_map  = { 0 : taurus.Critical, 1 : taurus.Error,
                       2 : taurus.Warning, 3 : taurus.Info,
                       4 : taurus.Debug, 5 : taurus.Trace }
    
    taurus.setLogLevel(log_level_map[options.log_level])
    
    taurus.info("Starting up %s", sys.argv)
    
    if use_rconsole:
        taurus.debug("Setting up rconsole...")
        try:
            import rfoo.utils.rconsole
            rfoo.utils.rconsole.spawn_server()
            taurus.debug("Finished setting up rconsole")
        except:
            taurus.debug("Failed to setup rconsole", exc_info=1)
        

    try:
        py = PyTango.Util(sys.argv)
        py.add_class(PoolClass, Pool)
        py.add_class(ControllerClass, Controller)
        py.add_class(MotorClass, Motor)
        py.add_class(CTExpChannelClass, CTExpChannel)
        py.add_class(MotorGroupClass, MotorGroup)
        py.add_class(MeasurementGroupClass, MeasurementGroup)
        
        U = PyTango.Util.instance()
        U.server_init()
        print "Ready to accept request"
        U.server_run()

    except PyTango.DevFailed,e:
        print '-------> Received a DevFailed exception:',e
    except Exception,e:
        print '-------> An unforeseen exception occured....',e
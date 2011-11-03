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

from .MacroServer import *
from .Door import *

def prepare_macroserver(util):
    import taurus.core.util.log
    Logger = taurus.core.util.log.Logger

    # Two additional log levels: 
    # output of a macro
    Logger.addLevelName(15, "OUTPUT")

    def output(loggable, msg, *args, **kw):
        loggable.getLogObj().log(Logger.Output, msg, *args, **kw)

    Logger.output = output

    # result of a macro
    Logger.addLevelName(18, "RESULT")

    util.add_class(MacroServerClass, MacroServer)
    util.add_class(DoorClass, Door)
    
def main_macroserver(args=None, start_time=None, mode=None):
    import sardana.tango.core.util
    return sardana.tango.core.util.run(prepare_macroserver, args=args,
                                       start_time=start_time, mode=mode)

run = main_macroserver

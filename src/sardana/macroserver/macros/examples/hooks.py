##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
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

"""This module contains macros that demonstrate the usage of hooks"""

__all__ = ["captain_hook", "captain_hook2", "loop", "hooked_scan",
           "hooked_dummyscan"]

__docformat__ = 'restructuredtext'

from sardana.macroserver.macro import *
        
class loop(Macro, Hookable):
    """A macro that executes a for loop. It accepts hooks.
    This macro is part of the examples package. It was written for 
    demonstration purposes"""
       
    hints = { 'allowsHooks':('pre-move', 'post-move', 'pre-acq', 'post-acq') }
    
    param_def = [['start', Type.Integer, None, 'start point'],
                 ['stop', Type.Integer, None, 'end point'],
                 ['step', Type.Integer, 1, 'step']]

    def hook1(self):
        self.output("En hook 1")
        
    def run(self, start, stop, step):
        self.info("Starting loop")
        self.hooks = [ (self.hook1, ["pre-acq"])]
        for i in xrange(start, stop, step):
            self.output("At step %d" % i)
            self.flushOutput()
            
            for hook,hints in self.hooks:
                self.info("running hook with hints="+repr(hints))
                hook()
        self.info("Finished loop")

class captain_hook(Macro):
    """A macro that executes a loop macro. A hook was attached so that in each 
    step of the loop this hook is executed.
    This macro is part of the examples package. It was written for 
    demonstration purposes"""

    param_def = [['start', Type.Integer, None, 'start point'],
                 ['stop', Type.Integer, None, 'end point'],
                 ['step', Type.Integer, 1, 'step']]
    
    def hook(self):
        self.info("\thook execution")
    
    def run(self, start, stop, step):
        loop_macro = self.createMacro("loop",start,stop,step)
        loop_macro.hooks = [ self.hook ]
        self.runMacro(loop_macro)

class captain_hook2(Macro):
    """A macro that executes a loop macro. A hook was attached so that in each 
    step of the loop this hook is executed.
    This macro is part of the examples package. It was written for 
    demonstration purposes"""

    param_def = [['start', Type.Integer, None, 'start point'],
                 ['stop', Type.Integer, None, 'end point'],
                 ['step', Type.Integer, 1, 'step']]
    
    def hook(self):
        self.execMacroStr(["lsm"])
    
    def run(self, start, stop, step):
        loop_macro = self.createMacro("loop",start,stop,step)
        #h = self.createExecMacroHook(["lsm"])
        loop_macro.hooks = [ self.hook ]  #it gives the "pre-acq" hint to the hook
        self.runMacro(loop_macro)

class hooked_scan(Macro):
    """An example on how to attach hooks to the various hook points of a scan.
    This macro is part of the examples package. It was written for 
    demonstration purposes"""
    
    param_def = [
       ['motor',      Type.Moveable,None, 'Motor to move'],
       ['start_pos',  Type.Float,   None, 'Scan start position'],
       ['final_pos',  Type.Float,   None, 'Scan final position'],
       ['nr_interv',  Type.Integer, None, 'Number of scan intervals'],
       ['integ_time', Type.Float,   None, 'Integration time']
    ]
    def hook1(self):
        self.info("\thook1 execution")
    
    def hook2(self):
        self.info("\thook2 execution")
    
    def hook3(self):
        self.info("\thook3 execution")
    
    def hook4(self):
        self.info("\thook4 execution")
    
    def hook5(self):
        self.info("\thook5 execution")
    
    def hook6(self):
        self.info("\thook6 execution")
    
    def run(self, motor, start_pos, final_pos, nr_interv, integ_time):
        ascan, pars = self.createMacro("ascan",motor, start_pos, final_pos, nr_interv, integ_time)
        ascan.hooks = [ (self.hook1, ["pre-acq"]), 
                       (self.hook2, ["pre-acq","post-acq","pre-move", "post-move","aaaa"]), 
                       self.hook3,
                       (self.hook4, ["pre-scan"]),
                       (self.hook5, ["pre-scan", "post-scan"]),
                       (self.hook6, ["post-step"])]
        self.runMacro(ascan)


class hooked_dummyscan(Macro):
    """An example on how to attach hooks to the various hook points of a scan.
    This macro is part of the examples package. It was written for 
    demonstration purposes"""
    
    param_def = [
       ['start_pos',  Type.Float,   None, 'Scan start position'],
       ['final_pos',  Type.Float,   None, 'Scan final position'],
       ['nr_interv',  Type.Integer, None, 'Number of scan intervals'],
       ['integ_time', Type.Float,   None, 'Integration time']
    ]
    def hook1(self):
        self.info("\thook1 execution")
    
    def hook2(self):
        self.info("\thook2 execution")
    
    def hook3(self):
        self.info("\thook3 execution")
    
    def run(self, start_pos, final_pos, nr_interv, integ_time):
        dummyscan,pars = self.createMacro("dummyscan",start_pos, final_pos, nr_interv, integ_time)
        dummyscan.hooks = [ (self.hook1, ["pre-scan"]), (self.hook2, ["pre-acq","post-acq","pre-move", "post-move","aaaa"]),(self.hook3, ["post-scan"])]
        self.runMacro(dummyscan)


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

"""
A macro package to show examples on how to run a macro from inside another macro
"""

__all__ = ["call_wa", "call_wm", "subsubm", "subm", "mainmacro", "runsubs"]

__docformat__ = 'restructuredtext'

from sardana.macroserver.macro import Macro, Type, ParamRepeat

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# First example:
# A 'mainmacro' that executes a 'subm' that in turn executes a 'subsubm'.
# The 'subsubm' macro itself calls a short ascan macro
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~--~-~-

class call_wa(Macro):
    
    def run(self):
        self.macros.wa()
        
class call_wm(Macro):

    param_def = [
        ['motor_list',
         ParamRepeat(['motor', Type.Motor, None, 'Motor to move']),
         None, 'List of motor to show'],
    ]

    def run(self, *m):
        self.macros.wm(*m)
        
class subsubm(Macro):
    """this macro just calls the 'subm' macro
    This macro is part of the examples package. It was written for demonstration purposes"""
    def run(self):
        self.output("Starting %s" % self.getName())
        m = self.macros
        motors = self.getObjs('.*', type_class=Type.Motor)
        m.ascan(motors[0], 0, 100, 10, 0.2)
        self.output("Finished %s" % self.getName())

class subm(Macro):
    """this macro just calls the 'subsubm' macro
    This macro is part of the examples package. It was written for demonstration purposes"""
    
    def run(self):
        self.output("Starting %s" % self.getName())
        self.macros.subsubm()
        self.output("Finished %s" % self.getName())

class mainmacro(Macro):
    """this macro just calls the 'subm' macro
    This macro is part of the examples package. It was written for demonstration purposes"""
    
    def run(self):
        self.output("Starting %s" % self.getName())
        self.macros.subm()
        self.output("Finished %s" % self.getName())

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# Second example:
# a 'runsubs' macro that shows the different ways to call a macro from inside
# another macro
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~--~-~-

class runsubs(Macro):
    """ A macro that calls a ascan macro using the motor given as first parameter.
    
    This macro is part of the examples package. It was written for demonstration purposes
    
    Call type will allow to choose to format in which the ascan macro is called
    from this macro:
    1 - m.ascan(motor.getName(), '0', '10', '4', '0.2')
    2 - m.ascan(motor, 0, 10, 4, 0.2)
    3 - self.execMacro('ascan', motor.getName(), '0', '10', '4', '0.2')
    4 - self.execMacro(['ascan', motor, 0, 10, 4, 0.2])
    5 - params = 'ascan', motor, 0, 10, 4, 0.2
        self.execMacro(params)
    6 - self.execMacro("ascan %s 0 10 4 0.2" % motor.getName())
    7 - macro, prep = self.createMacro("ascan %s 0 10 4 0.2" % motor.getName())
        macro.hooks = [ self.hook ]
        self.runMacro(macro)
    8 - macro, prep = self.createMacro('ascan', motor, 0, 10, 4, 0.2)
        macro.hooks = [ self.hook ]
        self.runMacro(macro)
    9 - params = 'ascan', motor, 0, 10, 4, 0.2
        macro, prep = self.createMacro(params)
        macro.hooks = [ self.hook ]
        self.runMacro(macro)
        
        Options 7,8 and 9 use the lower level macro API in order to be able to
        attach hooks to the ascan macro."""
    param_def = [
       ['motor',      Type.Motor,   None, 'Motor to move'],
       ['call_type',  Type.Integer, 2, 'type of run to execute internally'],
    ]
    
    def hook(self):
        self.info("executing hook in a step of a scan...")
    
    def run(self, motor, call_type):
        m = self.macros
        self.output("Using type %d" % call_type)
        if call_type == 1:
            m.ascan(motor.getName(), '0', '10', '4', '0.2')
        elif call_type == 2:
            m.ascan(motor, 0, 10, 4, 0.2)
        elif call_type == 3:
            self.execMacro('ascan', motor.getName(), '0', '10', '4', '0.2')
        elif call_type == 4:
            self.execMacro('ascan', motor, 0, 10, 4, 0.2)
        elif call_type == 5:
            params = 'ascan', motor, 0, 10, 4, 0.2
            self.execMacro(params)
        elif call_type == 6:
            self.execMacro("ascan %s 0 10 4 0.2" % motor.getName())
        elif call_type == 7:
            macro, prep = self.createMacro("ascan %s 0 10 4 0.2" % \
                                                     motor.getName())
            macro.hooks = [ self.hook ]
            self.runMacro(macro)
        elif call_type == 8:
            macro, prep = self.createMacro('ascan', motor, 0, 10, 4, 0.2)
            macro.hooks = [ self.hook ]
            self.runMacro(macro)
        elif call_type == 9:
            params = 'ascan', motor, 0, 10, 4, 0.2
            macro, prep = self.createMacro(params)
            macro.hooks = [ self.hook ]
            self.runMacro(macro)
        
            

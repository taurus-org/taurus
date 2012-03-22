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

"""Expert macros"""

from __future__ import print_function

__docformat__ = 'restructuredtext'

__all__ = ["commit_ctrllib", "defctrl", "defelem", "defm", "defmeas", "edctrl",
           "edctrllib", "lsmac", "prdef", "relmac", "relmaclib", "send2ctrl",
           "udefctrl", "udefelem", "udefmeas", "sar_info"]

import time
import array
import os

from taurus.console.list import List
from taurus.console.table import Table
from sardana.macroserver.macro import *

################################################################################
#
# Configuration related macros
#
################################################################################
    

class defm(Macro):
    """Creates a new motor in the active pool"""
    
    param_def = [['controller', Type.String, None, 'Controller name'],
                 ['axis', Type.Integer, None, 'motor axis'],
                 ['motor name', Type.String, None, 'motor name']]
    
    def run(self,controller, axis, name):
        pool = mntgrp.getPoolObj()
        pool.CreateMotor([[int(axis)],[name, controller]])


class defmeas(Macro):
    """Create a new measurement group"""

    param_def = [
       ['name',  Type.String, None, 'Measurement group name'],
       ['channel_list',
            ParamRepeat(['channel', Type.String, None, 'Measurement Channel'],),
            None, 'List of measurement channels'],
    ]

    def prepare(self, name, *channel_list, **opts):

        mntgrp_list = self.findObjs(name, type_class=Type.MeasurementGroup)
        
        if len(mntgrp_list) != 0:
            raise Exception('A measurement group with that name already exists')
        
    def run(self, name, *channel_list):
        pools = self.getPools()
        if len(pools) > 1:
            self.warning('Server connected to more than 1 pool. This macro is '
                         'not supported in this case for now')
        pool = pools[0]
        mg = pool.createMeasurementGroup(name, channel_list)
        self.print("Created %s" % str(mg))

class udefmeas(Macro):
    """Deletes an existing measurement group"""

    param_def = [ ['name', Type.MeasurementGroup, None, 'Measurement group name'],]

    def run(self, mntgrp):
        pool = mntgrp.getPoolObj()
        pool.deleteMeasurementGroup(mntgrp.getName())

class defelem(Macro):
    """Creates an element on a controller with an axis"""
    
    param_def = [ ['name', Type.String, None, 'new element name'],
                  ['ctrl', Type.Controller, None, 'existing controller'],
                  ['axis', Type.Integer, -1, 'axis in the controller (default is -1, meaning add to the end)'],]
    
    def run(self, name, ctrl, axis):
        pool = ctrl.getPoolObj()
        if axis == -1:
            axis = None
        elem = pool.createElement(name, ctrl, axis)
        self.print("Created %s" % str(elem))

class udefelem(Macro):
    """Deletes an existing element"""
    
    param_def = [ ['element', Type.Element, None, 'element name'],]
    
    def run(self, element):
        pool = element.getPoolObj()
        pool.deleteElement(element.getName())


class defctrl(Macro):
    """Creates a new controller"""
    
    param_def = [ ['class',  Type.ControllerClass, None, 'controller class'],
                  ['name',  Type.String, None, 'new controller name'],
                  ['properties',
                   ParamRepeat(['property item', Type.String, None, 'a property item'],min=0),
                   None, 'property item'] ]
    
    def run(self, ctrl_class, name, *props):
        pools = self.getPools()
        if len(pools) > 1:
            self.warning('Server connected to more than 1 pool. This macro is '
                         'not supported in this case for now')
        pool = pools[0]
        elem = pool.createController(ctrl_class.name, name, *props)
        self.print("Created %s" % str(elem))

class udefctrl(Macro):
    """Deletes an existing controller"""
    
    param_def = [ ['controller', Type.Controller, None, 'existing controller'],]
    
    def run(self, controller):
        pool = controller.getPoolObj()
        pool.deleteController(controller.getName())

################################################################################
#
# Controller related macros
#
################################################################################

        
class send2ctrl(Macro):
    """Sends the given data directly to the controller"""
    
    param_def = [['controller', Type.Controller, None, 'Controller name'],
                 ['data',
                  ParamRepeat(['string item', Type.String, None, 'a string item'],),
                  None, 'data to be sent']]
    
    def run(self, controller, *data):
        name = controller.getName()
        pool = controller.getPoolObj()
        str_data = " ".join(data)
        res = pool.SendToController([name,str_data])
        self.output(res)
        
################################################################################
#
# Library handling related macros
#
################################################################################

class edctrl(Macro):
    """Returns the contents of the library file which contains the given 
       controller code."""

    param_def = [
        ['ctrlclass',  Type.ControllerClass, None, 'Controller class name']
    ]
    
    result_def = [
        ['filedata',  Type.File, None, 'The file data object.']
    ]
    
    hints = { 'commit_cmd' : 'commit_ctrllib' }
    
    def run(self,ctrlclass):
        f_name = ctrlclass.file
        pool = ctrlclass.getPool()
        data = pool.GetFile(f_name)
        data = array.array('B',data).tostring()
        line_nb = 1
        for line in data.splitlines():
            line = line.strip(' \t')
            if line.startswith('class') and line.find(ctrlclass.name)>0 and \
                line.endswith(":"):
                break
            line_nb = line_nb + 1
        return [f_name,data,line_nb]

class edctrllib(Macro):
    """Returns the contents of the given library file"""

    param_def = [
        ['filename',  Type.Filename, None, 'Absolute path and file name or '\
         'simple filename. Relative paths are not allowed.']
    ]
    
    result_def = [
        ['filedata',  Type.File, None, 'The file data object']
    ]
    
    hints = { 'commit_cmd' : 'commit_ctrllib' }
    
    def run(self,filename):
        pool = self.getManager().getPool()
        data = pool.GetFile(filename)
        return [filename,array.array('B',data).tostring(),0]
   
class commit_ctrllib(Macro):
    """Puts the contents of the given data in a file inside the pool"""
    
    param_def = [
        ['filename',  Type.Filename, None, 'Absolute path and file name'],
        ['username',  Type.User, None, 'The user name'],
        ['comment',  Type.String, None, 'A description of the changes made to '\
         'the file'],
        ['filedata',  Type.File, None, 'The file data object']
    ]
    
    def run(self,filename,username,comment,filedata):
        pool = self.getManager().getPool()
        meta = filename + '\0' + username + '\0' + comment + '\0'
        data = array.array('B',meta)
        data.extend(array.array('B',filedata))
        pool.PutFile(data.tolist())
    
################################################################################
#
# Macro handling related macros
#
################################################################################

class lsmac(Macro):
    """Lists all macros."""
    
    def run(self):
        macro_libs = self.getMacroLibs()
        
        out = List(['Name','Module'])
        
        for macro_lib in macro_libs:
            for macro in macro_lib.get_macros():
                out.appendRow([macro.name, macro.file_path])
        for line in out.genOutput():
            self.output(line)
        

class prdef(Macro):
     """Returns the the macro code for the given macro name."""

     param_def = [
          ['macro_name', Type.MacroCode, None, 'macro name']
     ]
     
     def run(self,macro_data):
        code_lines, first_line = macro_data.code
        for code_line in code_lines:
            self.output(code_line.strip('\n'))


#class edmac(Macro):
#    """Returns the contents of the macro file which contains the macro code for
#    the given macro name. If the library is given and it does not exist a new 
#    one is created. If the given library is a simple library name and it does 
#    not exist, it will be created on the first directory mentioned in the MacroPath"""
    
#    """Returns the contents of the macro file which contains the macro code for
#    the given macro name."""

#    param_def = [['macro_name', Type.MacroCode, None, 'macro name'],
#                 ['module_name',
#                  ParamRepeat(['module_name', Type.String, None, 'a string item'],min=0,max=1),
#                  None, 'optional module name']]
    
#    result_def = [
#        ['filedata',  Type.File, None, 'The file data object.']
#    ]

#    def run(self, macro_name, *module_name):
#        if len(module_name) > 0:
#            module_name = module_name[0]
#            return self.getManager().getOrCreateMacroLib(module_name, macro_name)
    
#        macro_data = self.getMacroInfo(macro_name)

#        if macro_data == None:
#            self.output("Unknown macro")
#            return
     
#        f_name = macro_data.getFileName()
#        f = open(f_name)

#        try:
#            data = f.read()
#        finally:
#            f.close()
     
#        if data == None:
#            return
     
#        code_lines, first_line = macro_data.getMacroCode()
#        return [f_name , data , first_line]


#class edmaclib(Macro):
#    """Returns the contents of the macro file for the given macro library.
#    If the library does not exist a new one is created. If the given name is
#    a simple library name and it does not exist, it will be created on the 
#    first directory mentioned in the MacroPath"""

#    param_def = [
#        ['library_name',  Type.String, None, 
#         'a module name, a python file name or the absolute path']
#    ]
    
#    result_def = [
#        ['filedata', Type.File, None, 'The file data object']
#    ]
    
#    def run(self, library_name):
#        return self.getManager().getOrCreateMacroLib(library_name)


class relmaclib(Macro):
    """Reloads the given macro library code from the macro server filesystem."""

    param_def = [
        ['module name', Type.MacroLibrary, None,
         'The module name to be reloaded (without extension)']
    ]
    
    def run(self, module):
        self.reloadMacroLib(module.name)
    

class relmac(Macro):
    """Reloads the given macro code from the macro server filesystem.
    Attention: All macros inside the same file will also be reloaded."""
       
    param_def = [
        ['macro_name', Type.MacroCode, None, 'macro name']
    ]
    
    def run(self, macro_data):
        self.reloadMacro(macro_data.name)


class sar_info(Macro):
    """Prints details about the given sardana object"""
    
    param_def = [
        ['obj', Type.Object, None, 'obj']
    ]
    
    def run(self, obj):
        data = obj.serialize()
        
        table = Table([data.values()], row_head_str=data.keys(),
                      row_head_fmt='%*s', col_sep='  =  ')
        for line in table.genOutput():
            self.output(line)
        
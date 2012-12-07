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

import traceback
import array

from sardana.macroserver.macro import Macro, Type, ParamRepeat

################################################################################
#
# Configuration related macros
#
################################################################################


class defm(Macro):
    """Creates a new motor in the active pool"""

    param_def = [['motor name', Type.String, None, 'motor name'],
                 ['controller', Type.Controller, None, 'Controller name'],
                 ['axis', Type.Integer, None, 'motor axis'],]

    def run(self, name, controller, axis):
        pool = controller.getPoolObj()
        if axis == -1:
            axis = None
        elem = pool.createElement(name, controller, axis)
        self.print("Created %s" % str(elem))

class defmeas(Macro):
    """Create a new measurement group. First channel in channel_list MUST
    be an internal sardana channel. At least one channel MUST be a
    Counter/Timer (by default, the first Counter/Timer in the list will
    become the master)."""

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
        channel0 = self.getObj(channel_list[0])
        pool = channel0.getPoolObj()
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
    """Creates a new controller
    'role_prop' is a sequence of roles and/or properties.
    - A role is defined as <role name>=<role value> (only applicable to pseudo controllers)
    - A property is defined as <property name> <property value>
    
    If both roles and properties are supplied, all roles must come before properties.
    All controller properties that don't have default values must be given.
    
    Example of creating a motor controller (with a host and port properties):
    
    [1]: defctrl SuperMotorController myctrl host homer.springfield.com port 5000
    
    Example of creating a Slit pseudo motor (sl2t and sl2b motor roles, Gap and 
    Offset pseudo motor roles):
    
    [1]: defctrl Slit myslit sl2t=mot01 sl2b=mot02 Gap=gap01 Offset=offset01"""

    param_def = [ ['class',  Type.ControllerClass, None, 'controller class'],
                  ['name',  Type.String, None, 'new controller name'],
                  ['roles_props',
                   ParamRepeat(['role_prop', Type.String, None, 
                   'a role or property item'],min=0),
                   None, 'roles and/or properties'] ]

    def run(self, ctrl_class, name, *props):
        pool = ctrl_class.getPoolObj()
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
        ['macro_library', Type.MacroLibrary, None,
         'The module name to be reloaded (without extension)']
    ]

    def run(self, macro_library):
        name = macro_library.name
        new_macro_library = self.reloadMacroLib(name)
        if new_macro_library.has_errors():
            exc_info = new_macro_library.get_error()
            #msg = "".join(traceback.format_exception(*exc_info))
            msg = "".join(traceback.format_exception_only(*exc_info[:2]))
            self.error(msg)
        else:
            macros = new_macro_library.get_macros()
            self.output("%s successfully (re)loaded (found %d macros)", name, len(macros))


class relmac(Macro):
    """Reloads the given macro code from the macro server filesystem.
    Attention: All macros inside the same file will also be reloaded."""

    param_def = [
        ['macro_code', Type.MacroCode, None, 'macro name to be reloaded']
    ]

    def run(self, macro_code):
        name = macro_code.name
        macro_library_name = macro_code.lib.name
        self.reloadMacro(name)
        macro_library = self.getMacroLib(macro_library_name)
        if macro_library.has_errors():
            exc_info = macro_library.get_error()
            #msg = "".join(traceback.format_exception(*exc_info))
            msg = "".join(traceback.format_exception_only(*exc_info[:2]))
            self.error(msg)
        else:
            self.output("%s successfully (re)loaded", name)


class sar_info(Macro):
    """Prints details about the given sardana object"""

    param_def = [
        ['obj', Type.Object, None, 'obj']
    ]

    def run(self, obj):
        self.dump_properties(obj)
        #self.output("")
        #self.dump_attributes(obj)

    def dump_properties(self, obj):
        data = obj.serialize()

        table = Table([data.values()], row_head_str=data.keys(),
                      row_head_fmt='%*s', col_sep='  =  ')
        self.output("Properties:")
        self.output("-----------")
        for line in table.genOutput():
            self.output(line)

    def dump_attributes(self, obj):
        try:
            dev_attrs = obj.dump_attributes()
        except AttributeError:
            return

        row_head, values = [], []
        for dev_attr in dev_attrs:
            row_head.append(dev_attr.name)
            if dev_attr.has_failed:
                err = dev_attr.get_err_stack()
                if len(err):
                    value = err[0].desc
                else:
                    value = "Unknown error!"
            else:
                value = str(dev_attr.value)
            values.append(value)
        table = Table([values], row_head_str=row_head,
                      row_head_fmt='%*s', col_sep='  =  ')
        self.output("Attributes:")
        self.output("-----------")
        for line in table.genOutput():
            self.output(line)


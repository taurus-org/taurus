"""
    Macro library containning macros for handling the ZMX 
    Tango device server as part of the Sardana project.
    
"""

from sardana.macroserver.macro import *

import PyTango

class _zmx:
    """Internal class used as a base class for the zmx macros"""

    env = ('RootZMXName',)
    
    
    def prepare(self):
        self.prepared = False
        
        root_name = self.getEnv('RootZMXName')
        self.db = PyTango.Database()
        name_dev_ask = root_name + "*"
        self.devices = self.db.get_device_exported(name_dev_ask)
        self.zmx_proxy = []
        self.zmx_device_name = []
        self.zmx_axis = []
        self.nb_zmx = len(self.devices)
        j = 0
        for name in self.devices:
            self.zmx_device_name.append(name)
            self.zmx_proxy.append(self.getDevice(name))
            self.zmx_axis.append(j)
            j = j + 1
		
        self.prepared = True

class zmx_nb_devices(Macro, _zmx):
    """The zmx_nb_devices macro is used to printout the number of ZMX devices found for the RootZMXName in enviroment."""
    
    def prepare(self):
        _zmx.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        self.output("Number of found ZMX devices: " + str(self.nb_zmx))

class zmx_general_info(Macro, _zmx):
    """The zmx_general_info macro is used to printout the general info (name/voltage/temperature/error) for all ZMX devices."""
    
    def prepare(self):
        _zmx.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        self.output("Index Name (tango device)         Voltage        Temperature     Error")
        self.flushOutput()
        for j in range(0,int(self.nb_zmx)):
            self.output(str(self.zmx_axis[j]) + " " + self.zmx_proxy[j].AxisName + " (" + self.zmx_device_name[j] + ") " + str(self.zmx_proxy[j].IntermediateVoltage) + " " + str(self.zmx_proxy[j].Temperature) + " " + str(self.zmx_proxy[j].Error))
            self.flushOutput()
        
class zmx_axis_info(Macro, _zmx):
    """The zmx_axis_info macro is used to printout the info of the axis corresponding to the given index."""
    param_def = [
       ['axis_nb', Type.Integer, None, "Index number"]
    ]
                    
    def prepare(self, axis_nb):
        _zmx.prepare(self)
    
    def run(self, axis_nb):
        if not self.prepared:
            return
        if axis_nb < self.nb_zmx:          
            self.output("ZMX axis: " + str(axis_nb))
            self.flushOutput()
            self.output("Axis name: " + str(self.zmx_proxy[axis_nb].AxisName))
            self.flushOutput()
            self.output("Version: " + str(self.zmx_proxy[axis_nb].VersionPS))
            self.flushOutput()
            self.output("Activation: " + str(self.zmx_proxy[axis_nb].DeactivationStr))
            self.flushOutput()
            self.output("Step resolution: " + str(self.zmx_proxy[axis_nb].StepWidthStr))
            self.flushOutput()
            self.output("Run current: " + str(self.zmx_proxy[axis_nb].RunCurrent) + " A")
            self.flushOutput()
            self.output("Stop current: " + str(self.zmx_proxy[axis_nb].StopCurrent) + " A")
            self.flushOutput()
            self.output("Motor direction: " + str(self.zmx_proxy[axis_nb].PreferentialDirectionStr))
            self.flushOutput()
            self.output("Operation mode: " + str(self.zmx_proxy[axis_nb].OperationModeStr))
            self.flushOutput()
            self.output("Delay time: " + str(self.zmx_proxy[axis_nb].DelayTime) + " mS")
            self.flushOutput()
            self.output("Voltage: " + str(self.zmx_proxy[axis_nb].IntermediateVoltage) + " V")
            self.flushOutput()
            self.output("Temperature: " + str(self.zmx_proxy[axis_nb].Temperature) + " C")
            self.flushOutput()
            self.output("Power stage status: " + str(self.zmx_proxy[axis_nb].PowerStageStatus))
            self.flushOutput()
            self.output("Error: " + str(self.zmx_proxy[axis_nb].Error))
            self.flushOutput()
            self.output("Path output files: " + str(self.zmx_proxy[axis_nb].PathOutputFiles))
            self.flushOutput()
            self.output("Save automatically to EPROM: " + str(self.zmx_proxy[axis_nb].FlagSaveAutomatically))
            self.flushOutput()
            self.output("Changes not saved: " + str(self.zmx_proxy[axis_nb].FlagChangeNotSaved))
            self.flushOutput()
            self.output("Error in connection: " + str(self.zmx_proxy[axis_nb].ErrorZMXConnection))
            self.flushOutput()
        else:
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
 
class zmx_set_activation(Macro, _zmx):
    """The zmx_set_activation macro is used to set the activation value of the given axis ( 0 activate, 1 deactivate ) ."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"],
       ['tmp_value', Type.Integer, None, "0 activate, 1 deactivate"]
    ]
    
    def prepare(self, axis_nb, tmp_value):
        _zmx.prepare(self)
    
    def run(self, axis_nb, tmp_value):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return
        if tmp_value != 0 and tmp_value != 1:
            self.output("Not allowed to set this value. 0 -> activate, 1 -> deactivate") 
            self.flushOutput()       
        else:       
            self.zmx_proxy[axis_nb].write_attribute("Deactivation",tmp_value)

 
class zmx_set_stepresolution(Macro, _zmx):
    """The zmx_set_stepresolution macro is used to set the step resolution of the given axis."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"],
       ['tmp_value', Type.Integer, None, "Step resolution"]
    ]
    
    def prepare(self, axis_nb, tmp_value):
        _zmx.prepare(self)
    
    def run(self, axis_nb, tmp_value):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return
        if tmp_value < 0 or tmp_value > 13:
            self.output("Not allowed to set this value. Allowed values from 0 to 13")
            self.flushOutput()       
        else:       
            self.zmx_proxy[axis_nb].write_attribute("StepWidth",tmp_value)

 
class zmx_set_preferentialdirection(Macro, _zmx):
    """The zmx_set_activation macro is used to set the preferential direction of the given axis ( 0 negative, 1 positive ) ."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"],
       ['tmp_value', Type.Integer, None, "0 negative, 1 positive"]
    ]
    
    def prepare(self, axis_nb, tmp_value):
        _zmx.prepare(self)
    
    def run(self, axis_nb, tmp_value):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return
        if tmp_value != 0 and tmp_value != 1:
            self.output("Not allowed to set this value. 0 -> negative, 1 -> positive") 
            self.flushOutput()       
        else:       
            self.zmx_proxy[axis_nb].write_attribute("PreferentialDirection",tmp_value)
 
class zmx_set_delaytime(Macro, _zmx):
    """The zmx_set_delaytime macro is used to set the delay time of the given axis."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"],
       ['tmp_value', Type.Integer, None, "Delay Time"]
    ]
    
    def prepare(self, axis_nb, tmp_value):
        _zmx.prepare(self)
    
    def run(self, axis_nb, tmp_value):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return
        if tmp_value < 0 or tmp_value > 15:
            self.output("Not allowed to set this value. Allowed values from 0 to 15")
            self.flushOutput()       
        else:       
            self.zmx_proxy[axis_nb].write_attribute("DelayTime",tmp_value)
 
class zmx_set_pathoutputfiles(Macro, _zmx):
    """The zmx_set_pathoutputfiles macro is used to set the path for the output files of the given axis."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"],
       ['tmp_value', Type.String, None, "Output path"]
    ]
    
    def prepare(self, axis_nb, tmp_value):
        _zmx.prepare(self)
    
    def run(self, axis_nb, tmp_value):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return   
        self.zmx_proxy[axis_nb].write_attribute("PathOutputFiles",tmp_value)

 
class zmx_set_autosavetoeprom(Macro, _zmx):
    """The zmx_set_autosavetoeprom macro is used to set/unset the automatic write to eprom of the given axis."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"],
       ['tmp_value', Type.Integer, None, "0 -> not auto save, 1 -> auto save"]
    ]
    
    def prepare(self, axis_nb, tmp_value):
        _zmx.prepare(self)
    
    def run(self, axis_nb, tmp_value):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return
        if tmp_value != 0 and tmp_value != 1:
            self.output("Not allowed to set this value. 0 -> not auto save, 1 -> auto save") 
            self.flushOutput()       
        else:       
            self.zmx_proxy[axis_nb].write_attribute("FlagSaveAutomatically",tmp_value)
            
class zmx_loadfromoutputfile(Macro, _zmx):
    """The zmx_loadfromoutputfile macro is used to load parameters from an external file."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"],
       ['tmp_value', Type.String, None, "File name"]
    ]
    
    def prepare(self, axis_nb, tmp_value):
        _zmx.prepare(self)
    
    def run(self, axis_nb, tmp_value):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return    
        self.zmx_proxy[axis_nb].LoadFromOutputFile(tmp_value)
            
class zmx_savetooutputfile(Macro, _zmx):
    """The zmx_savetooutputfile macro is used to save parameters to en external file."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"],
       ['tmp_value', Type.String, None, "File name"]
    ]
    
    def prepare(self, axis_nb, tmp_value):
        _zmx.prepare(self)
    
    def run(self, axis_nb, tmp_value):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return   
        self.zmx_proxy[axis_nb].SaveToOutputFile(tmp_value)
            
class zmx_readfilecontent(Macro, _zmx):
    """The zmx_readfilecontent macro is used to read the parameters stored in an ouput file."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"],
       ['tmp_value', Type.String, None, "File name"]
    ]
    
    def prepare(self, axis_nb, tmp_value):
        _zmx.prepare(self)
    
    def run(self, axis_nb, tmp_value):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return
        contents = self.zmx_proxy[axis_nb].ReadFileContent(tmp_value)
        for element in contents:
            self.output(element)


class zmx_readfilesinoutputpath(Macro, _zmx):
    """The zmx_readfilesinoutputpath macro is used to read the files in the ouput path."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"]
    ]
    
    def prepare(self, axis_nb):
        _zmx.prepare(self)
    
    def run(self, axis_nb):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return      
        files = self.zmx_proxy[axis_nb].ReadFilesInOutputPath()
        for element in files:
            self.output(element)

class zmx_deleteeprom(Macro, _zmx):
    """The zmx_deleteeprom macro is used to delete the EPROM contents."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"]
    ]
    
    def prepare(self, axis_nb):
        _zmx.prepare(self)
    
    def run(self, axis_nb):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return   
        self.zmx_proxy[axis_nb].DeleteEPROM()

class zmx_writeeprom(Macro, _zmx):
    """The zmx_writeeprom macro is used to write current settings to the EPROM."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"]
    ]
    
    def prepare(self, axis_nb):
        _zmx.prepare(self)
    
    def run(self, axis_nb):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return   
        self.zmx_proxy[axis_nb].WriteEPROM()

class zmx_reset(Macro, _zmx):
    """The zmx_reset macro is used to reset the power stage."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"]
    ]
    
    def prepare(self, axis_nb):
        _zmx.prepare(self)
    
    def run(self, axis_nb):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return   
        self.zmx_proxy[axis_nb].Reset()

class zmx_revminus(Macro, _zmx):
    """The zmx_revminus macro is used to  perform a motor test: one motor rotation with preset run current (negative direction)."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"]
    ]
    
    def prepare(self, axis_nb):
        _zmx.prepare(self)
    
    def run(self, axis_nb):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return   
        self.zmx_proxy[axis_nb].RevMinus()

class zmx_revplus(Macro, _zmx):
    """The zmx_revplus macro is used to  perform a motor test: one motor rotation with preset run current (positive direction)."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"]
    ]
    
    def prepare(self, axis_nb):
        _zmx.prepare(self)
    
    def run(self, axis_nb):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return   
        self.zmx_proxy[axis_nb].RevPlus()

class zmx_reseterrorzmxconnection(Macro, _zmx):
    """The zmx_reseterrorzmxconnection macro is used to reset the flag indicating error in ZMX connection."""
    
    param_def = [
       ['axis_nb', Type.Integer, None, "Index"]
    ]
    
    def prepare(self, axis_nb):
        _zmx.prepare(self)
    
    def run(self, axis_nb):
        if not self.prepared:
            return
        if axis_nb > (self.nb_zmx - 1):
            self.output("Not axis existing for that index. Maximum index value: " + str(self.nb_zmx - 1))
            return   
        self.zmx_proxy[axis_nb].ResetErrorZMXConnection()

"""
    Macro library containning shuttere related macros for the 
    Tango device server as part of the Sardana project.
    
"""
import time
from sardana.macroserver.macro import *

class _shutter:
    """Internal class used as a base class for the shutter macros"""

    env = ('ShutterDevice',)
    
    def prepare(self):

        self.prepared = False
        
        dev_name = self.getEnv('ShutterDevice')        
        self.shutter = self.getDevice(dev_name)
        
        self.nb_bs = self.shutter.get_property(['Nb_bs'])

        
        self.prepared = True

class shutter_status(Macro, _shutter):
    """Returns information about the current status of the shutter.""" 

    def prepare(self):
        _shutter.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        
        for i in range(0,self.nb_bs):
            angle_device = self.getDevice(self.angle_device_name[angle])
            if i == 0:
                shutter_name = Abs0
                str_status = self.shutter.StringStateAbs0
            elif i == 1:
                shutter_name = BS0
                str_status = self.shutter.StringStateBS0
            elif i == 2:
                shutter_name = BS1
                str_status = self.shutter.StringStateBS1
            elif i == 3:
                shutter_name = BS2
                str_status = self.shutter.StringStateBS2
            elif i == 4:
                shutter_name = BS3
                str_status = self.shutter.StringStateBS3
            elif i == 5:
                shutter_name = BS4
                str_status = self.shutter.StringStateBS4
            elif i == 6:
                shutter_name = BS5
                str_status = self.shutter.StringStateBS5
                
            self.output("%s:  %s " % (shutter_name,str_status))
            
        self.output("General State:  %s" % (self.shutter.StringGeneralStateBL))

class shutter_open(Macro, _shutter):
    """Open shutter. Without arguments open all shutters in the beamline.
       Argument indicates which shutter should be opened""" 
    
    param_def = [
       ['shutter_index', Type.Integer, -9999, "shutter index"]
    ]
    
    def prepare(self, shutter_index):
        _shutter.prepare(self)
    
    def run(self, shutter_index):
        if not self.prepared:
            return
        
        value = 1
        for i in range(0,self.nb_bs):
            if i == 0 and (shutter_index == 0 or shutter_index == -9999):
                self.shutter.CloseOpenABS_BS_0(value)
            if i == 1 and (shutter_index == 1 or shutter_index == -9999):
                self.shutter.CloseOpen_BS_0(value)
            if i == 2 and (shutter_index == 2 or shutter_index == -9999):
                self.shutter.CloseOpen_BS_1(value)
            if i == 3 and (shutter_index == 3 or shutter_index == -9999):
                self.shutter.CloseOpen_BS_2(value)
            if i == 4 and (shutter_index == 4 or shutter_index == -9999):
                self.shutter.CloseOpen_BS_3(value)
            if i == 5 and (shutter_index == 5 or shutter_index == -9999):
                self.shutter.CloseOpen_BS_4(value)
            if i == 6 and (shutter_index == 6 or shutter_index == -9999):
                self.shutter.CloseOpen_BS_5(value)

class shutter_close(Macro, _shutter):
    """Close shutter. Without arguments close all shutters in the beamline.
       Argument indicates which shutter should be closed""" 
    
    param_def = [
       ['shutter_index', Type.Integer, -9999, "shutter index"]
    ]
    
    def prepare(self, shutter_index):
        _shutter.prepare(self)
    
    def run(self, shutter_index):
        if not self.prepared:
            return
        
        value = 0
        for i in range(0,self.nb_bs):
            if i == 0 and (shutter_index == 0 or shutter_index == -9999):
                self.shutter.CloseOpenABS_BS_0(value)
            if i == 1 and (shutter_index == 1 or shutter_index == -9999):
                self.shutter.CloseOpen_BS_0(value)
            if i == 2 and (shutter_index == 2 or shutter_index == -9999):
                self.shutter.CloseOpen_BS_1(value)
            if i == 3 and (shutter_index == 3 or shutter_index == -9999):
                self.shutter.CloseOpen_BS_2(value)
            if i == 4 and (shutter_index == 4 or shutter_index == -9999):
                self.shutter.CloseOpen_BS_3(value)
            if i == 5 and (shutter_index == 5 or shutter_index == -9999):
                self.shutter.CloseOpen_BS_4(value)
            if i == 6 and (shutter_index == 6 or shutter_index == -9999):
                self.shutter.CloseOpen_BS_5(value)  

"""
    Macro library containning shuttere related macros for the 
    Tango device server as part of the Sardana project.
    
"""
import time
from macro import *

intern_nb_cs = [0,6,4,4,4,4,4,8,3,5,4,3,3,3,4]


shutter_names = [[""],["ABS0", "BS0", "BS1", "BS2", "BS3", "BS4"],["ABS0",  "BS0", "BSA1", "BSB1"],["ABS0", "BS0", "BS1", "BS2"],["ABS0",  "BS0", "BSA1", "BSB1"],["ABS0", "BS0", "BS1", "BS2"],["ABS0", "BS0", "BS1", "BS2"],["ABS0", "BS0", "BSA1", "BSA2", "BSA3", "BSA4", "BSA5", "BSB1"],["ABS0", "BS0", "BS1"],["ABS0", "BS0", "BS1", "BS2", "BS3"],["ABS0", "BS0", "BS1", "BS2"],["ABS0", "BS0", "BS1"],["ABS0", "BS0", "BS1"],["ABS0", "BS0", "BS1"],["ABS0", "BS0", "BS1", "BS2"]]

class _shutter:
    """Internal class used as a base class for the shutter macros"""

    env = ('ShutterDevice',)
    
    def prepare(self):

        self.prepared = False
        
        dev_name = self.getEnv('ShutterDevice')        
        self.shutter = self.getDevice(dev_name)
        
        self.nb_bs = self.shutter.get_property(['Nb_bs'])

        self.beamline = self.shutter.get_property(['Beamline'])

        self.prepared = True

class shutter_status(Macro, _shutter):
    """Returns information about the current status of the shutter. 0 open, 3 closed""" 

    def prepare(self):
        _shutter.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        
        for i in range(0,self.intern_nb_cs[self.beamline]):
            shutter_name = shutter_names[self.beamline][i]
            attr_to_read = shutter_names[self.beamline][i] + "OffenDisplayState"
            status = self.shutter.read_attribute(attr_to_read).value
            self.output("%s:  %d " % (shutter_name,status))
 

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

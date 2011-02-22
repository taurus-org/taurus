"""
    Macro library containning macros for handling the LensesBox
    Tango device server as part of the Sardana project.
    
"""

from macro    import *

import PyTango

class _lensesbox:
    """Internal class used as a base class for the lensesbox macros"""

    env = ('ActiveLensesBox',)
    
    
    def prepare(self):
        self.prepared = False
        
        dev_name = self.getEnv('ActiveLensesBox')        
        self.lensesbox = self.getDevice(dev_name)
		
        self.prepared = True

class lensesbox_set_nbmotors(Macro, _lensesbox):
    """The lensesbox_set_nbmotors macro is used to initialize the given number of motors."""
    
    param_def = [
       ['nb_motors', Type.Integer, None, "Number of motors to be initialized"]]
	
    def prepare(self, nb_motors):
        _lensesbox.prepare(self)
    
    def run(self, nb_motors):
        if not self.prepared:
            return
        self.lensesbox.write_attribute("NbMotors",nb_motors)
        
class lensesbox_get_nbmotors(Macro, _lensesbox):
    """The lensesbox_get_nbmotors macro is used to read the number of initialized motors."""
	
    def prepare(self):
        _lensesbox.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        self.output("Number of initialized motors ")
        self.output(self.lensesbox.read_attribute("NbMotors").value)


class lensesbox_set_lensesToMoveIn(Macro, _lensesbox):
    """The lensesbox_set_lensesToMoveIn macro is used to select the lenses that will go to the IN by performing the next movement."""
    
    param_def = [
       ['lens1', Type.Integer, 0, "1-IN, 0-OUT"],
       ['lens2', Type.Integer, 0, "1-IN, 0-OUT"],
       ['lens3', Type.Integer, 0, "1-IN, 0-OUT"],
       ['lens4', Type.Integer, 0, "1-IN, 0-OUT"],
       ['lens5', Type.Integer, 0, "1-IN, 0-OUT"],
       ['lens6', Type.Integer, 0, "1-IN, 0-OUT"],
       ['lens7', Type.Integer, 0, "1-IN, 0-OUT"],
       ['lens8', Type.Integer, 0, "1-IN, 0-OUT"],
       ['lens9', Type.Integer, 0, "1-IN, 0-OUT"],
       ['lens10', Type.Integer, 0, "1-IN, 0-OUT"],
       ['lens11', Type.Integer, 0, "1-IN, 0-OUT"],
       ['lens12', Type.Integer, 0, "1-IN, 0-OUT"]
    ]
    
    def prepare(self, *pars):
        _lensesbox.prepare(self)
    
    def run(self, *pars):
        if not self.prepared:
            return          
        values = []
        for p in pars:
            values.append(p)
        self.lensesbox.write_attribute("SetIN",values)


class lensesbox_get_lensesToMoveIn(Macro, _lensesbox):
    """The lensesbox_get_lensesToMoveIn macro is used to read the lenses that will go to the IN by performing the next movement."""
    
    def prepare(self):
        _lensesbox.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        dim_x = self.lensesbox.read_attribute("SetIN").dim_x
        if dim_x > 0:
            lenses_inout = self.lensesbox.SetIn
            for lens in lenses_inout:
                self.output(lens)

class lensesbox_get_statusIN(Macro, _lensesbox):
    """The lensesbox_get_statusIN macro is used to read the status of the lenses (1 IN, 0 OUT)."""
    
    def prepare(self):
        _lensesbox.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        dim_x = self.lensesbox.read_attribute("StatusIN").dim_x
        if dim_x > 0:
            lenses_inout = self.lensesbox.StatusIn
            for lens in lenses_inout:
                self.output(lens)

class lensesbox_get_statusOK(Macro, _lensesbox):
    """The lensesbox_get_statusOK macro is used to read the status of the lenses (1 OK)."""
    
    def prepare(self):
        _lensesbox.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        dim_x = self.lensesbox.read_attribute("StatusOK").dim_x
        if dim_x > 0:
            lenses_inout = self.lensesbox.StatusOK
            for lens in lenses_inout:
                self.output(lens)

class lensesbox_get_statusGeneral(Macro, _lensesbox):
    """The lensesbox_get_statusGeneral macro is used to read the status of the lenses system"""
    
    def prepare(self):
        _lensesbox.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        dim_x = self.lensesbox.read_attribute("StatusGeneral").dim_x
        if dim_x > 0:
            lenses_inout = self.lensesbox.StatusGeneral
            dict_general_status = []
            dict_general_status.append("Done:")
            dict_general_status.append(" Enabled:")
            dict_general_status.append(" Power:")
            dict_general_status.append(" Busy:")
            dict_general_status.append(" Reset:")
            i = 0
            for lens in lenses_inout:
                self.output(dict_general_status[i])
                self.output("          " + str(lens))
                i = i + 1

class lensesbox_get_position(Macro, _lensesbox):
    """The lensesbox_get_position macro is used to read the position of the system (12 bits in decimal)"""
    
    def prepare(self):
        _lensesbox.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        self.output("Current position ")
        self.output(self.lensesbox.read_attribute("Position").value)

class lensesbox_set_position(Macro, _lensesbox):
    """The lensesbox_set_position macro is used to move the lenses according to the given position (12 bits in decimal)."""
    
    param_def = [
       ['position', Type.Float, None, "Position"]]
	
    def prepare(self, nb_motors):
        _lensesbox.prepare(self)
    
    def run(self, position):
        if not self.prepared:
            return
        self.lensesbox.write_attribute("Position",position)
                
class lensesbox_move(Macro, _lensesbox):
    """The lensesbox_move macro is used to perform the movement of the lenses"""
    
    def prepare(self):
        _lensesbox.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        self.lensesbox.Move()
                
class lensesbox_reboot(Macro, _lensesbox):
    """The lensesbox_reboot macro is used to make a hardware reboot of the system"""
    
    def prepare(self):
        _lensesbox.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        self.lensesbox.Reboot()
                
class lensesbox_stop(Macro, _lensesbox):
    """The lensesbox_stop macro is used to set the flag of movement done after 4 sec"""
    
    def prepare(self):
        _lensesbox.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        self.lensesbox.Stop()

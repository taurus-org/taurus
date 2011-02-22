"""
    Macro library containning macros for handling the Absorbercontroller
    Tango device server as part of the Sardana project.
    
"""

from macro    import *

#import PyTango

class _absorbercontroller:
    """Internal class used as a base class for the absorbercontroller macros"""

    env = ('ActiveAbsorberController',)
    
    
    def prepare(self):
        self.prepared = False
        
        dev_name = self.getEnv('ActiveAbsorberController')        
        self.absorbercontroller = self.getDevice(dev_name)
		
        self.prepared = True

        
class absorbercontroller_get_nbsliders(Macro, _absorbercontroller):
    """The absorbercontroller_get_nbsliders macro is used to read the number of sliders."""
	
    def prepare(self):
        _absorbercontroller.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        
        prop = self.absorbercontroller.get_property(['NbSliders'])        
        for v in prop['NbSliders']:        
            nb_sliders = v
            
        self.output(nb_sliders)


class absorbercontroller_set_slidersToMoveIn(Macro, _absorbercontroller):
    """The absorbercontroller_set_slidersToMoveIn macro is used to select the sliders that will go to the IN by performing the next movement."""
    
    param_def = [
       ['slider1', Type.Integer, 0, "1-IN, 0-OUT"],
       ['slider2', Type.Integer, 0, "1-IN, 0-OUT"],
       ['slider3', Type.Integer, 0, "1-IN, 0-OUT"],
       ['slider4', Type.Integer, 0, "1-IN, 0-OUT"],
       ['slider5', Type.Integer, 0, "1-IN, 0-OUT"],
       ['slider6', Type.Integer, 0, "1-IN, 0-OUT"],
       ['slider7', Type.Integer, 0, "1-IN, 0-OUT"],
       ['slider8', Type.Integer, 0, "1-IN, 0-OUT"],
       ['slider9', Type.Integer, 0, "1-IN, 0-OUT"],
       ['slider10', Type.Integer, 0, "1-IN, 0-OUT"],
       ['slider11', Type.Integer, 0, "1-IN, 0-OUT"],
       ['slider12', Type.Integer, 0, "1-IN, 0-OUT"]
    ]
    
    def prepare(self, *pars):
        _absorbercontroller.prepare(self)
    
    def run(self, *pars):
        if not self.prepared:
            return          
        values = []
        for p in pars:
            values.append(p)
        self.absorbercontroller.write_attribute("SetIn",values)


class absorbercontroller_get_slidersToMoveIn(Macro, _absorbercontroller):
    """The absorbercontroller_get_slidersToMoveIn macro is used to read the sliders that will go to the IN by performing the next movement."""
    
    def prepare(self):
        _absorbercontroller.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        dim_x = self.absorbercontroller.read_attribute("SetIn").dim_x
        if dim_x > 0:
            sliders_inout = self.absorbercontroller.SetIn
            for slider in sliders_inout:
                self.output(slider)

class absorbercontroller_get_slidersIn(Macro, _absorbercontroller):
    """The absorbercontroller_get_statusIn macro is used to read the status of the sliders (1 IN, 0 OUT)."""
    
    def prepare(self):
        _absorbercontroller.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        dim_x = self.absorbercontroller.read_attribute("SlidersIn").dim_x
        if dim_x > 0:
            sliders_inout = self.absorbercontroller.SlidersIn
            for slider in sliders_inout:
                self.output(slider)

class absorbercontroller_get_slidersOut(Macro, _absorbercontroller):
    """The absorbercontroller_get_statusOut macro is used to read the status of the sliders (0 IN, 1 OUT)."""
    
    def prepare(self):
        _absorbercontroller.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        dim_x = self.absorbercontroller.read_attribute("SlidersOut").dim_x
        if dim_x > 0:
            sliders_inout = self.absorbercontroller.SlidersOut
            for slider in sliders_inout:
                self.output(slider)
                
class absorbercontroller_get_statusSliders(Macro, _absorbercontroller):
    """The absorbercontroller_get_statusSliders macro is used to read the status of the sliders (1 Error)."""
    
    def prepare(self):
        _absorbercontroller.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        dim_x = self.absorbercontroller.read_attribute("StatusSliders").dim_x
        if dim_x > 0:
            sliders_status = self.absorbercontroller.StatusSliders
            for slider in sliders_status:
                self.output(slider)

class absorbercontroller_get_FlagError(Macro, _absorbercontroller):
    """The absorbercontroller_get_FlagError  macro returns 1 if there is any slider in error"""
    
    def prepare(self):
        _absorbercontroller.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        
        self.output(self.absorbercontroller.FlagError)

class absorbercontroller_get_FlagMovementOK(Macro, _absorbercontroller):
    """The absorbercontroller_get_FlagMovementOK  macro returns 1 if the last movement was smoothly done"""
    
    def prepare(self):
        _absorbercontroller.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        
        self.output(self.absorbercontroller.FlagMovementOK)


class absorbercontroller_get_position(Macro, _absorbercontroller):
    """The absorbercontroller_get_position macro is used to read the position of the system (12 bits in decimal)"""
    
    def prepare(self):
        _absorbercontroller.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        self.output("Current position ")
        self.output(self.absorbercontroller.read_attribute("Position").value)

class absorbercontroller_set_position(Macro, _absorbercontroller):
    """The absorbercontroller_set_position macro is used to move the sliders according to the given position (12 bits in decimal)."""
    
    param_def = [
       ['position', Type.Float, None, "Position"]]
	
    def prepare(self, nb_motors):
        _absorbercontroller.prepare(self)
    
    def run(self, position):
        if not self.prepared:
            return
        self.absorbercontroller.write_attribute("Position",position)
                
                
class absorbercontroller_move(Macro, _absorbercontroller):
    """The absorbercontroller_move macro is used to perform the movement of the sliders"""
    
    def prepare(self):
        _absorbercontroller.prepare(self)
    
    def run(self):
        if not self.prepared:
            return
        self.absorbercontroller.Move()

from sardana.macroserver import parameter

# Basic types

class Integer(parameter.ParamType):
    type_class = int

class Float(parameter.ParamType):
    type_class = float

class Boolean(parameter.ParamType):
    type_class = bool

    def getObj(self, str_repr):
        return str_repr.lower() == "true"
    
class String(parameter.ParamType):
    type_class = str

class User(parameter.ParamType):
    type_class = str

class Filename(parameter.ParamType):
    type_class = str

class File(parameter.ParamType):
    type_class = str
    
    def __init__(self, name):
        parameter.ParamType.__init__(self, name)
        self.filename = None
        #self.data is supposed to be a array.array object
        self.data = None
    
    def set(self, filename, data):
        self.filename = filename
        self.data = data
        

class Macro(parameter.ParamType):
    type_class = str


class MacroLib(parameter.ParamType):
    type_class = str

class Env(parameter.ParamType):
    type_class = str

# Hardware types

class MotorParam(parameter.AttrParamType):
    """ Class designed to represent a motor parameter name. Usual values
    are acceleration,deceleration,velocity,backlash,steps_per_unit,etc"""
    
    def __init__(self, name):
        parameter.AttrParamType.__init__(self, name)
        self.attr_item_list = ["Acceleration","Backlash","Base_rate","Step_per_unit",
                "Deceleration","Velocity","Offset"]
        self.non_attr_item_list = ["Controller"]
    
    def getItemList(self):
        return self.non_attr_item_list + self.attr_item_list
    
    def getAttrItemList(self):
        return self.attr_item_list
    
    def getNonAttrItemList(self):
        return self.non_attr_item_list

class Motor(parameter.PoolObjParamType):
    """ Class designed to represend a generic movement parameter. Could in fact
    be a Motor, PseudoMotor or even a MotorGroup object 
    """
    pass

class MotorGroup(parameter.PoolObjParamType):
    pass

class ExpChannel(parameter.PoolObjParamType):
    """ Class designed to represend a generic experiment channel parameter. 
    Could in fact be a Counter/Timer, 0D, 1D or 2D channel or a PseudoCounter 
    """
    pass

class MeasurementGroup(parameter.PoolObjParamType):
    """ Class designed to represend a generic experiment."""    
    pass

class ComChannel(parameter.PoolObjParamType):
    """ Class designed to represend a generic communication channel."""
    pass

class IORegister(parameter.PoolObjParamType):
    """ Class designed to represend a generic input/output register. """
    pass

class Controller(parameter.PoolObjParamType):
    """ Class designed to represent a generic controller."""
    pass

class Instrument(parameter.PoolObjParamType):
    """ Class designed to represent a generic instrument."""
    pass

class ControllerClass(parameter.PoolObjParamType):
    
    def __init__(self, name):
        parameter.PoolObjParamType.__init__(self, name)

#    def getPoolObjList(self, pool):
#        obj_list = pool.getCtrlClassListObj()
#        return obj_list.read()
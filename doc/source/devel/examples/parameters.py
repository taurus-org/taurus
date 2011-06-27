"""This module contains macros that demonstrate the usage of macro parameters"""

from macro import *

class pt0(Macro):
    """Macro without parameters. Pretty dull"""

    param_def = []
    
    def run(self):
        pass
    
class pt1(Macro):
    """Macro with one float parameter: Each parameter is described in the 
    param_def sequence as being a sequence of for elements: name, type, 
    default value and description"""
    
    param_def = [ [ 'value', Type.Float, None, 'some bloody float'] ]
    
    def run(self, f):
        pass

class pt2(Macro):
    """Macro with one Motor parameter: Each parameter is described in the 
    param_def sequence as being a sequence of for elements: name, type, 
    default value and description"""

    param_def = [ [ 'motor', Type.Motor, None, 'some bloody motor'] ]
    
    def run(self, m):
        pass

class pt3(Macro):
    """Macro with a list of numbers as parameter: the type is a sequence of
    parameter types which is repeated. In this case it is a repetition of a 
    float so only one parameter is defined.
    By default the repetition as a semantics of 'at least one'"""

    param_def = [
       [ 'numb_list', [ [ 'pos', Type.Float, None, 'value'] ], None, 'List of values'],
    ]
    
    def run(self, *args, **kwargs):
        pass

class pt4(Macro):
    """Macro with a list of motors as parameter: the type is a sequence of
    parameter types which is repeated. In this case it is a repetition of a 
    motor so only one parameter is defined.
    By default the repetition as a semantics of 'at least one'"""

    param_def = [
       [ 'motor_list', [ [ 'motor', Type.Motor, None, 'motor name'] ], None, 'List of motors'],
    ]
    
    def run(self, *args, **kwargs):
        pass

class pt5(Macro):
    """Macro with a motor parameter followed by a list of numbers"""

    param_def = [
       [ 'motor', Type.Motor, None, 'Motor to move'],
       [ 'numb_list', [ [ 'pos', Type.Float, None, 'value'] ], None, 'List of values'],
    ]
    
    def run(self, *args, **kwargs):
        pass

class pt6(Macro):
    """Macro with a motor parameter followed by a list of numbers. The list as
    explicitly stated an optional last element which is a dictionary that defines the
    min and max values for repetitions"""

    param_def = [
       [ 'motor', Type.Motor, None, 'Motor to move'],
       [ 'numb_list', [ [ 'pos', Type.Float, None, 'value'], { 'min' : 1, 'max' : None } ],
         None, 'List of values'],
    ]
    
    def run(self, *args, **kwargs):
        pass
    
class pt7(Macro):
    """Macro with a list of pair Motor,Float"""

    param_def = [
       [ 'm_p_pair', [ [ 'motor', Type.Motor, None, 'Motor to move'],
                       [ 'pos',   Type.Float, None, 'Position to move to'] ],
         None, 'List of motor/position pairs']
    ]
    
    def run(self, *args, **kwargs):
        pass

class pt8(Macro):
    """Macro with a list of pair Motor,Float. The min and max elements have been
    explicitly stated"""
    
    param_def = [
       [ 'm_p_pair', [ [ 'motor', Type.Motor, None, 'Motor to move'],
                       [ 'pos',   Type.Float, None, 'Position to move to'],
                       { 'min' : 1, 'max' : 2 } ],
         None, 'List of motor/position pairs']
    ]
    
    def run(self, *args, **kwargs):
        pass

class pt9(Macro):
    """Same as macro pt7 but witb old style ParamRepeat. If you are writing
    a macro with variable number of parameters for the first time don't even
    bother to look at this example since it is DEPRECATED."""

    param_def = [
       ['m_p_pair',
        ParamRepeat(['motor', Type.Motor, None, 'Motor to move'],
                    ['pos',  Type.Float, None, 'Position to move to'], min=1, max= 2),
        None, 'List of motor/position pairs'],
    ]
    
    def run(self, *args, **kwargs):
        pass
""" The standard pseudo counter controller library for the device pool """ 

import PyTango
from pool import PseudoCounterController, PoolUtil

from math import *

try:
    import scipy
    __SCIPY_AVAILABLE__ = True
except:
    __SCIPY_AVAILABLE__ = False
    
# Will disapear when we have pseudo counters that can have other pseudo counters
# in their counter roles.
class Current(PseudoCounterController):
    """ A simple pseudo counter which receives two counter values (I and I0) 
        and returns I/I0"""

    counter_roles = ("I","I0")

    def calc(self,counter_values):
        if counter_values[1] < 0.00001:
            return counter_values[0]
        return float(counter_values[0]/counter_values[1])
    

class PseudoCoMotorWrapper(PseudoCounterController):
    """ A pseudo counter controller whose pseudo counter value is the motor 
        position to which it is connected to"""
    
    class_prop = { 'Motor' : { 'Description' : 'the motor tango device name (or alias)','Type' : 'PyTango.DevString'} }
    
    def calc(self,counter_values):
        mot = PoolUtil().get_motor(self.inst_name,self.Motor)
        return mot.read_attribute("position").value
    

class PseudoFunctionCounterController(PseudoCounterController):
    """ A simple pseudo counter that returns a function of the last values of a counter using
     a dummy motor. It resets the data list when the dummy motor is at position zero.
     Typical for being used within a mesh."""

     # IF YOU NEED TO CREATE THE CONTROLLER WITH JIVE:
     # TEST THE POOL DEVICE AND ISSUE THE CreateController command with:
     # PseudoCounter,file_name,class_name,ctrl_name,counter_to_read,pseudo_counter_name,dummy_motor,motor_value,function,function_value

    MEAN = "MEAN"
    STD = "STD"
    
    class_prop = {'dummy_motor':{'Description':'The dummy motor device the reset counter values.'
                              ,'Type' : 'PyTango.DevString'},
                  'function':{'Description':'The function to use (MEAN|STD).'
                              ,'Type' : 'PyTango.DevString'}
                  }
    counter_roles = ("Counter",)

    def __init__(self,inst,props):
        PseudoCounterController.__init__(self,inst,props)
        
        if not __SCIPY_AVAILABLE__:
            raise RuntimeException("scipy python package not availabe.")
        
        util = PoolUtil()
        self.dummy_motor_dev = util.get_device(self.inst_name,self.dummy_motor)
        self.dict_values = {}


    def calc(self,counter_values):
        position =  self.dummy_motor_dev.read_attribute("Position").value
        if position == 0:
            self.dict_values = {}

        self.dict_values[position] = counter_values[0]

        if self.function.upper() == self.MEAN:
            return scipy.mean(self.dict_values.values())
        elif self.function.upper() == self.STD:
            return scipy.std(self.dict_values.values())
        else:
            return 0


class PseudoCoTangoWrapper(PseudoCounterController):
    """ A pseudo counter which value is the attribute of a tango
    device.  There is also the 'Formula' that allows the user to
    define an expression that will be evaluated e.g. 'VALUE * 2'."""

    # NO COUNTERS NEEDED
    counter_roles = ()
    
    # THE EXTRA ATTRIBUTES EXTERNALATTRIBUTE AND FORMULA FOR THE PSEUDO COUNTER
    ctrl_extra_attributes ={'ExternalAttribute':
                            {'Type':'PyTango.DevString'
                             ,'Description':'The Tango Attribute to read (e.g. my/tango/dev/attr)'
                             ,'R/W Type':'PyTango.READ_WRITE'}
                            ,'Formula':
                            {'Type':'PyTango.DevString'
                             ,'Description':'The Formula to get the REAL VALUE.\ne.g. "(-1 * VALUE) + 10"'
                             ,'R/W Type':'PyTango.READ_WRITE'}
                            }

    FORMULA = 'Formula'
    EXTERNALATTRIBUTE = 'ExternalAttribute'
    ATTRIBUTE = 'Attribute'
    
    
    def __init__(self,inst,props):
        
        PseudoCounterController.__init__(self,inst,props)
        self.counterExtraAttributes = {}
        self.counterExtraAttributes[1] = {self.FORMULA:"VALUE",self.EXTERNALATTRIBUTE:""
                                          ,self.ATTRIBUTE:""}
        self.device_proxy = None

    def calc(self, index, counter_values):
        """ Ignore the counter values and return the evaluation of the formula"""
        try:
            attribute = self.counterExtraAttributes[index][self.ATTRIBUTE]
            VALUE = self.device_proxy.read_attribute(attribute).value
            return eval(self.counterExtraAttributes[index][self.FORMULA])
        except PyTango.DevFailed, df:
            print "error in  %s.calc: %s" % (self.inst_name, str(df[-1]))
        except Exception, e:
            print "error in  %s.calc: %s" % (self.inst_name, str(e))
        return -1

    def GetExtraAttributePar(self,index,name):
        # IMPLEMENTED THE EXTRA ATTRIBUTE 'Formula','ExternalAttribute'
        return self.counterExtraAttributes[index][name]


    def SetExtraAttributePar(self,index,name,value):
        # IMPLEMENTED THE EXTRA ATTRIBUTE 'Formula','ExternalAttribute'
        self.counterExtraAttributes[index][name] = value
        try:
            if name == self.EXTERNALATTRIBUTE:
                idx = value.rfind("/")
                device =  value[:idx]
                attribute = value[idx+1:]
                self.counterExtraAttributes[index][self.ATTRIBUTE] = attribute
                self.device_proxy = PoolUtil().get_device(self.inst_name,device)
        except PyTango.DevFailed, df:
            print "error in  %s.SetExtraAttributePar: %s" % (self.inst_name, str(df[-1]))
        except Exception, e:
            print "error in  %s.SetExtraAttributePar: %s" % (self.inst_name, str(e))

class PseudoCoTwoTangoAtt(PseudoCounterController):
    """ A pseudo counter which value is a formula from two tango
    device attributes.  The 'Formula' that allows the user to define
    an expression that will be evaluated e.g. 'VALUE1 / VALUE2'."""

    # NO COUNTERS NEEDED
    counter_roles = ()

    # THE EXTRA ATTRIBUTES EXTERNALATTRIBUTE AND FORMULA FOR THE PSEUDO COUNTER
    ctrl_extra_attributes ={'ExternalAttribute1':
                            {'Type':'PyTango.DevString'
                             ,'Description':'The first Tango Attribute to read (e.g. my/tango/dev/attr)'
                             ,'R/W Type':'PyTango.READ_WRITE'}
                            ,'ExternalAttribute2':
                            {'Type':'PyTango.DevString'
                             ,'Description':'The second Tango Attribute to read (e.g. my/tango/dev/attr)'
                             ,'R/W Type':'PyTango.READ_WRITE'}
                            ,'Formula':
                            {'Type':'PyTango.DevString'
                             ,'Description':'The Formula to get the REAL VALUE.\ne.g. "VALUE1/VALUE2"'
                             ,'R/W Type':'PyTango.READ_WRITE'}
                            }

    FORMULA = 'Formula'
    EXTERNALATTRIBUTE1 = 'ExternalAttribute1'
    EXTERNALATTRIBUTE2 = 'ExternalAttribute2'
    ATTRIBUTE1 = 'Attribute1'
    ATTRIBUTE2 = 'Attribute2'
    
    
    def __init__(self,inst,props):
        
        PseudoCounterController.__init__(self,inst,props)
        self.counterExtraAttributes = {}
        self.counterExtraAttributes[0] = {self.FORMULA:"VALUE1/VALUE2"
                                          ,self.EXTERNALATTRIBUTE1:"",self.ATTRIBUTE1:""
                                          ,self.EXTERNALATTRIBUTE2:"",self.ATTRIBUTE2:""}
        self.device_proxy1 = None
        self.device_proxy2 = None

    def calc(self,counter_values):
        """ Ignore the counter values and return the evaluation of the formula"""
        try:
            attribute1 = self.counterExtraAttributes[0][self.ATTRIBUTE1]
            attribute2 = self.counterExtraAttributes[0][self.ATTRIBUTE2]
            VALUE1 = self.device_proxy1.read_attribute(attribute1).value
            VALUE2 = self.device_proxy2.read_attribute(attribute2).value
            return eval(self.counterExtraAttributes[0][self.FORMULA])
        except PyTango.DevFailed, df:
            print "error in  %s.calc: %s" % (self.inst_name, str(df[-1]))
        except Exception, e:
            print "error in  %s.calc: %s" % (self.inst_name, str(e))
        return -1

    def GetExtraAttributePar(self,counter,name):
        # IMPLEMENTED THE EXTRA ATTRIBUTE 'Formula','ExternalAttribute1','ExternalAttribute2'
        return self.counterExtraAttributes[counter][name]


    def SetExtraAttributePar(self,counter,name,value):
        # IMPLEMENTED THE EXTRA ATTRIBUTE 'Formula','ExternalAttribute1','ExternalAttribute2'
        self.counterExtraAttributes[counter][name] = value
        try:
            if name == self.EXTERNALATTRIBUTE1 or name == self.EXTERNALATTRIBUTE2:
                idx = value.rfind("/")
                device =  value[:idx]
                attribute = value[idx+1:]
                if name == self.EXTERNALATTRIBUTE1:
                    self.counterExtraAttributes[counter][self.ATTRIBUTE1] = attribute
                    self.device_proxy1 = PoolUtil().get_device(self.inst_name,device)
                else:
                    self.counterExtraAttributes[counter][self.ATTRIBUTE2] = attribute
                    self.device_proxy2 = PoolUtil().get_device(self.inst_name,device)
        except PyTango.DevFailed, df:
            print "error in  %s.SetExtraAttributePar: %s" % (self.inst_name, str(df[-1]))
        except Exception, e:
            print "error in  %s.SetExtraAttributePar: %s" % (self.inst_name, str(e))
            

class PseudoCounterWrapper(PseudoCounterController):
    """ A pseudo counter which value is the evaluation of a formula from a counter
    value.  The 'Formula' could be 'sqrt(VALUE)' or 'cos(VALUE)'."""
    
    counter_roles = ("Counter",)
    pseudo_counter_roles = ("Pseudo counter",)
    
    FORMULA = 'Formula'
    INT_FORMULA = 'InternalFormula'
    
    # THE EXTRA ATTRIBUTES EXTERNALATTRIBUTE AND FORMULA FOR THE PSEUDO COUNTER
    ctrl_extra_attributes ={'Formula':
                            {'Type':'PyTango.DevString'
                             ,'Description':'The Formula to get the REAL VALUE.\ne.g. "VALUE1/VALUE2"'
                             ,'R/W Type':'PyTango.READ_WRITE'}
                            }

    def __init__(self,inst,props):
        PseudoCounterController.__init__(self,inst,props)
        self.counterExtraAttributes = {}
        self.counterExtraAttributes[1] = { self.FORMULA: "VALUE",
                                           self.INT_FORMULA : self._fromUserFormulaToInternalFormula("VALUE") }
    
    def _fromUserFormulaToInternalFormula(self, formula):
        
        c_nb = len(self.counter_roles)
        if c_nb == 1:
            return formula.replace("VALUE","counter_values[0]")
        else:
            for i in xrange(c_nb):
                formula = formula.replace("VALUE%d" % (i+1), "counter_values[%d]" % i)
            return formula
    
    def calc(self, index, counter_values):
        """ Return the evaluation of the formula"""
        try:
            return eval(self.counterExtraAttributes[index][self.INT_FORMULA])
        except PyTango.DevFailed, df:
            print "error in  %s.calc: %s" % (self.inst_name, str(df[-1]))
        except Exception, e:
            print "error in  %s.calc: %s" % (self.inst_name, str(e))
        return -1
        
    def GetExtraAttributePar(self,counter,name):
        # IMPLEMENTED THE EXTRA ATTRIBUTE 'Formula'
        return self.counterExtraAttributes[counter][name]

    def SetExtraAttributePar(self,counter,name,value):
        # IMPLEMENTED THE EXTRA ATTRIBUTE 'Formula'
        self.counterExtraAttributes[counter][name] = value
        if name == self.FORMULA:
            self.counterExtraAttributes[counter][self.INT_FORMULA] = self._fromUserFormulaToInternalFormula(value)

class PseudoCo2To1(PseudoCounterWrapper):
    """ A pseudo counter which value is the evaluation of a formula from two counter
    values.  The 'Formula' could be 'VALUE1 / VALUE2'."""

    counter_roles = ("Counter 1", "Counter 2")
    
    def __init__(self,inst,props):
        
        PseudoCounterWrapper.__init__(self,inst,props)
        dft_formula = "VALUE1/VALUE2"
        self.counterExtraAttributes[1] = { self.FORMULA: dft_formula,
                                           self.INT_FORMULA : self._fromUserFormulaToInternalFormula(dft_formula) }

class PseudoCo2To2(PseudoCo2To1):
    """ A pseudo counter which value is a formula from two tango
    device attributes.  The 'Formula' that allows the user to define
    an expression that will be evaluated e.g. 'VALUE1 / VALUE2'."""

    pseudo_counter_roles = ("Pseudo 1", "Pseudo 2")
    
    def __init__(self,inst,props):
        PseudoCo2To1.__init__(self,inst,props)
        dft_formula = "VALUE2/VALUE1"
        self.counterExtraAttributes[2] = { self.FORMULA: dft_formula,
                                           self.INT_FORMULA : self._fromUserFormulaToInternalFormula(dft_formula) }

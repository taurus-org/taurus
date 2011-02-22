""" Pseudo motor system file"""

class PseudoMotor:
    """The abstract class for the Python Pseudo Motor.
       Every Pseudo Motor implementation must be a subclass of this class.
       Current procedure for a correct implementation of a Pseudo Motor class:
        - mandatory: define the class level attributes pseudo_motor_roles, 
                     motor_roles and class_prop (if any).
        - mandatory: write calc_pseudo(self,physical_pos) method
        - mandatory: write calc_physical(self,pseudo_pos) method.
        - optional: write calc_all_pseudo and calc_all_physical if great 
                    performance gain can be achived"""

    pseudo_motor_roles = ()
    motor_roles = ()
    class_prop = {}
    
    def __init__(self, inst, inst_prop):
        self.inst_name = inst;
        
        for class_prop_key in self.class_prop:
            #get the value from the instance 
            value = inst_prop.get(class_prop_key)
            
            #if the value does't exist get it from the instance dict
            if value == None:
                value = self.class_prop.get(class_prop_key).get('DefaultValue')
                
                #if the value does't exist in the instance dict -> serious error
                if value == None:
                    raise Exception("property %s must be defined at instance "
                                    "level." % class_prop_key)
            
            #add the attribute
            setattr(self, class_prop_key, value)
            
    @classmethod
    def get_physical_motor_nb(cls):
        """Returns the number of physical motors that an instance of a Pseudo 
           Motor Class must have."""
        return len(cls.motor_roles)
    
    @classmethod
    def get_pseudo_motor_nb(cls):
        """Returns the number of pseudo motors that an instance of a Pseudo
           Motor Class must have."""
        return len(cls.get_pseudo_motor_roles())
    
    @classmethod
    def get_motor_role(cls, idx):
        """Given a physical motor number, it will return it's description."""
        return cls.motor_roles[idx]

    @classmethod
    def get_pseudo_motor_role(cls, idx):
        """Given a pseudo motor number, it will return it's description."""
        return cls.get_pseudo_motor_roles()[idx]
    
    @classmethod
    def get_properties(cls):
        """Returns all properties defined for this class"""
        return cls.class_prop
    
    @classmethod
    def get_property_descr(cls, name):
        """Returns the description of the given property"""
        return cls.class_prop[name]
    
    @classmethod
    def get_class_info(cls):
        """Returns a list with the complete information about the pseudo motor 
           class in the following format:
             ret[0] - class description
             ret[1] - number of physical motors = M
             ret[2...M+1] - physical motor roles
             ret[M+2] - number of pseudo motors = N
             ret[M+3...M+N+2] - pseudo motor roles
             ret[M+N+3] - number of properties = P
             ret[M+N+4...M+N+(P*4)+3] - properties description
           
           Each property description consists of four strings:
             ret[i] - name
             ret[i+1] - type
             ret[i+2] - description
             ret[i+3] - default value
           
           The default value is None if not defined. When existing, the data type of the default conforms to the corresponding type:
           /------------------------------|--------------------------------------------------------------------------------\
           |        Tango type            |                                 Python type                                    |
           |------------------------------|--------------------------------------------------------------------------------|
           | PyTango.DevBoolean           | bool  (types.BooleanType)                                                      |
           | PyTango.DevLong              | long  (types.LongType)                                                         |
           | PyTango.DevDouble            | float (types.FloatType)                                                        |
           | PyTango.DevString            | str   (types.StringType)                                                       |
           | PyTango.DevVarBooleanArray   | tuple or list (types.TupleType or types.ListType) of bool (types.BooleanType)  |
           | PyTango.DevVarLongArray      | tuple or list (types.TupleType or types.ListType) of long (types.LongType)     |
           | PyTango.DevVarDoubleArray    | tuple or list (types.TupleType or types.ListType) of float (types.FloatType)   |
           | PyTango.DevVarStringArray    | tuple or list (types.TupleType or types.ListType) of string (types.StringType) |
           \------------------------------|--------------------------------------------------------------------------------/
        """
        lst = cls.get_pseudo_class_info()
        
        lst.append(len(cls.class_prop))
        
        for key in cls.class_prop:
            value_dict = cls.class_prop.get(key)
            lst.append(key)
            lst.append(value_dict.get('Type'))
            lst.append(value_dict.get('Description'))
            lst.append(value_dict.get('DefaultValue'))
        
        return lst
    
    @classmethod
    def get_pseudo_class_info(cls):
        """Returns a list with the information (except properties information) 
           about the pseudo motor class in the following format:
             ret[0] - class description
             ret[1] - number of physical motors = M
             ret[2...M+2] - physical motor roles
             ret[M+3] - number of pseudo motors = N
             ret[M+4...M+N+4] - pseudo motor roles
         """        
        lst = [cls.__doc__, len(cls.motor_roles)]
        
        for motor_role in cls.motor_roles:
            lst.append(motor_role)
        
        lst.append(cls.get_pseudo_motor_nb())
        
        for pseudo_motor_role in cls.get_pseudo_motor_roles():
            lst.append(pseudo_motor_role)
        
        return lst
    
    @classmethod
    def get_pseudo_motor_roles(cls):
        """Returns the pseudo motor roles for this class"""
        if len(cls.pseudo_motor_roles) == 0:
            cls.pseudo_motor_roles = (cls.__name__,)
        return cls.pseudo_motor_roles
    
    def get_info(self):
        """Returns a list with the complete information about the pseudo motor 
           class in the following format:
             ret[0] - class description
             ret[1] - number of physical motors = M
             ret[2...M+2] - physical motor roles
             ret[M+3] - number of pseudo motors = N
             ret[M+4...M+N+4] - pseudo motor roles
             ret[M+N+5] - number of properties = P
             ret[M+N+6...M+N+(P*4)+6] - properties description
             
             @see get_class_info() for more information on the format of the 
                  properties
         """
        lst = self.get_pseudo_class_info()
        
        lst.append(len(self.class_prop))
        
        for key in self.class_prop:
            value_dict = self.class_prop.get(key)
            lst.append(key)
            lst.append(value_dict.get('Type'))
            lst.append(value_dict.get('Description'))
            lst.append(getattr(self, key))
        
        return lst
    
    def calc_all_pseudo(self, physical_pos):
        """Calculates the positions of all pseudo motors that belong to the 
           pseudo motor system from the positions of the physical motors."""
        ret = []
        for i in range(self.get_pseudo_motor_nb()):
            ret.append(self.calc_pseudo(i, physical_pos))
        return ret
    
    def calc_all_physical(self, pseudo_pos):
        """Calculates the positions of all motors that belong to the pseudo 
           motor system from the positions of the pseudo motors."""
        ret = []
        for i in range(len(self.motor_roles)):
            pos = self.calc_physical(i, pseudo_pos)
            ret.append(pos)
        return ret
    
    def calc_physical(self, pseudo_pos):
        """Calculate physical motor position given the pseudo motor positions"""
        raise Exception("calc_physical must be redefined")
    
    def calc_pseudo(self, physical_pos):
        """Calculate pseudo motor position given the physical motor positions"""
        raise Exception("calc_pseudo must be redefined")
        
if __name__ == '__main__':
    print PseudoMotor.__doc__

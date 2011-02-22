""" Pseudo motor system file"""

import PseudoController

class PseudoMotorController(PseudoController.PseudoController):
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

    trace = ["calc_pseudo", "calc_physical", "calc_all_pseudo", "calc_all_physical"]

    @classmethod
    def get_MaxDevice(cls):
        return cls.get_pseudo_motor_nb()
            
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
    def get_pseudo_motor_roles(cls):
        """Returns the pseudo motor roles for this class"""
        if len(cls.pseudo_motor_roles) == 0:
            cls.pseudo_motor_roles = (cls.__name__,)
        return cls.pseudo_motor_roles
    
    @classmethod
    def get_pseudo_info(cls):
        """Returns information specific to pseudo motors:
             ret[0] - number of physical motors = M
             ret[1...M+1] - physical motor roles
             ret[M+2] - number of pseudo motors = N
             ret[M+3..M+N+4] - pseudo motor roles
        """
        lst = len(cls.motor_roles)
        lst.extend(cls.motor_roles)
        lst.append(cls.get_pseudo_motor_nb())
        lst.extend(cls.get_pseudo_motor_roles())

        return lst
    
    def calc_all_pseudo(self, physical_pos):
        """Calculates the positions of all pseudo motors that belong to the 
           pseudo motor system from the positions of the physical motors."""
        ret = []
        for i in xrange(self.get_pseudo_motor_nb()):
            ret.append(self.calc_pseudo(i+1, physical_pos))
        return ret
    
    def calc_all_physical(self, pseudo_pos):
        """Calculates the positions of all motors that belong to the pseudo 
           motor system from the positions of the pseudo motors."""
        ret = []
        for i in xrange(len(self.motor_roles)):
            pos = self.calc_physical(i+1, pseudo_pos)
            ret.append(pos)
        return ret
    
    def calc_physical(self, pseudo_pos):
        """Calculate physical motor position given the pseudo motor positions"""
        raise Exception("calc_physical must be redefined")
    
    def calc_pseudo(self, physical_pos):
        """Calculate pseudo motor position given the physical motor positions"""
        raise Exception("calc_pseudo must be redefined")
        
if __name__ == '__main__':
    print PseudoMotorController.__doc__

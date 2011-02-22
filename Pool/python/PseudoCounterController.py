""" Pseudo counter system file"""

import PseudoController

class PseudoCounterController(PseudoController.PseudoController):
    """The abstract class for the Python Pseudo Counter.
       Every Pseudo Counter implementation must be a subclass of this class.
       Current procedure for a correct implementation of a Pseudo Counter class:
        - mandatory: define the class level attributes counter_roles, 
                     and class_prop (if any).
        - mandatory: write calc(self, idx, counter_values) method"""

    pseudo_counter_roles = ()
    counter_roles = ()

    @classmethod
    def get_MaxDevice(cls):
        return cls.get_counter_nb()
                
    @classmethod
    def get_counter_nb(cls):
        """Returns the number of physical counters that an instance of a Pseudo
           Counter controller class must have."""
        return len(cls.counter_roles)

    @classmethod
    def get_pseudo_counter_nb(cls):
        """Returns the number of pseudo counters that an instance of a Pseudo
           Counter controller class must have."""
        return len(cls.pseudo_counter_roles)
    
    @classmethod
    def get_counter_role(cls, idx):
        """Given a physical counter number, it will return it's description."""
        return cls.counter_roles[idx]
    
    @classmethod
    def get_pseudo_counter_role(cls, idx):
        """Given a pseudo counter number, it will return it's description."""
        return cls.pseudo_counter_roles[idx]

    @classmethod
    def get_properties(cls):
        """Returns all properties defined for this class"""
        return cls.class_prop
    
    @classmethod
    def get_property_descr(cls, name):
        """Returns the description of the given property"""
        return cls.class_prop[name]
    
    @classmethod
    def get_pseudo_counter_roles(cls):
        """Returns the pseudo counter roles for this class"""
        if len(cls.pseudo_counter_roles) == 0:
            cls.pseudo_counter_roles = (cls.__name__,)
        return cls.pseudo_counter_roles
    
    @classmethod
    def get_pseudo_info(cls):
        """Returns information specific to pseudo counters:
             ret[0] - number of physical motors = M
             ret[1...M+1] - physical motor roles
             ret[M+2] - number of pseudo motors = N
             ret[M+3..M+N+4] - pseudo motor roles
        """
        lst = len(cls.counter_roles)
        lst.extend(cls.counter_roles)
        lst.append(cls.get_pseudo_counter_nb())
        lst.extend(cls.get_pseudo_counter_roles())

        return lst
    
    def calc(self, idx, counter_values):
        """Calculate pseuco counter value given the counter values"""
        raise Exception("cal must be redefined")
            
if __name__ == '__main__':
    print PseudoCounterController.__doc__

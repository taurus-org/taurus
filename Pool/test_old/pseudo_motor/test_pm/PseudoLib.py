from PseudoMotor import PseudoMotor
#import PseudoMotor

class Dummy:
	"""I don implement the proper methods and i don't inherit from PseudoMotor so I am not valid"""
	def __init__(self):
		print "I am just a dummy class"

class DontInheritFromPseudoMotor:
	"""I implement the proper methods but i don't inherit from PseudoMotor so I am not valid"""
	
	def calc_physical(self,index,pseudo_pos):
		half_gap = pseudo_pos[0]/2.0
		if index == 0:
			return pseudo_pos[1] - half_gap
		else:			
			return pseudo_pos[1] + half_gap
	
	def calc_pseudo(self,index,physical_pos):
		if index == 0:
			return physical_pos[1] - physical_pos[0]
		else:
			return (physical_pos[0] + physical_pos[1])/2.0

class DontImplementMethods(PseudoMotor):
	"""I inherit from PseudoMotor but i don't implement the proper methods so I am not valid"""	

class TableHeight(PseudoMotor):
	"""Controllertable-height pseudomotor with mnemonic t1z that is the average height 
	    of the three real motors t1f, t1b1 and t1b2 that correspond to the table legs. When the height is moved, 
	    each leg is moved by an amount equal to the difference of the current height and the target height. The 
	    current average height needs to be calculated from the current real-motor positions before the new 
	    positions are assigned."""
	
	pseudo_motor_roles = ("t1z",)
	motor_roles = ("t1f", "t1b1", "t1b2")
	class_prop = { 'weight' : {
				       'Description' : 'The table weight',
				       'Type' : 'PyTango.DevDouble',
				       'DefaultValue' : 0.0
				       },
				   'table color' : {
				       'Description' : 'Color value',
				       'Type' : 'PyTango.DevLong',
				       'DefaultValue' : 0
				       },
				   'leg color' : {
				       'Description' : 'Color value',
				       'Type' : 'PyTango.DevLong',
				       'DefaultValue' : 0
				       }
				 }

	def calc_physical(self,pseudo_pos):
		# get last known real positions
		# calculate the pseudo position by calling calc_pseudo
		# calculate 
		pass
	
	def calc_pseudo(self,physical_pos):
		return (physical_pos[0] + physical_pos[1] + physical_pos[2]) / 3.0

class Slit(PseudoMotor):
	"""A Slit pseudo motor system for controlling gap and offset pseudo motors."""
	
	pseudo_motor_roles = ("Gap", "Offset")
	motor_roles = ("sl2t", "sl2b")
	class_prop = { 'print_string' : {
				       'Description' : 'A property for demonstrating a string property',
				       'Type' : 'PyTango.DevString',
				       'DefaultValue' : 'Somebody told me to print a default value'
			       		},
				 }
				       	
	def calc_physical(self,index,pseudo_pos):
		half_gap = pseudo_pos[0]/2.0
		if index == 0:
			return pseudo_pos[1] - half_gap
		else:
			return pseudo_pos[1] + half_gap
	
	def calc_pseudo(self,index,physical_pos):
		if index == 0:
			return physical_pos[1] - physical_pos[0]
		else:
			return (physical_pos[0] + physical_pos[1])/2.0

from PseudoMotor import PseudoMotor
#import PseudoMotor

class DummyGarbage:
	def __init__(self):
		print "Nothing here on DummyGarbage :-("



class DummyMotor01(PseudoMotor):
	"""Just a silly pseudo motor. It doesn't actually do anything."""
	
	motor_roles = ("Motor on upper Blade","Motor on lower Blade")
		
	def calc_physical(self,index,pseudo_pos):
		return 5.0
	
	def calc_pseudo(self,index,physical_pos):
		return 1.0



class Silly01(PseudoMotor):
	"""Just a silly pseudo motor. It doesn't actually do anything."""
	
	pseudo_motor_roles = ("psd 01", "psd 02", "psd 03", "psd 04")
	motor_roles = ("real 01", "real 02", "real 03", "real 04")
		
	def calc_physical(self,index,pseudo_pos):
		return 0.0
	
	def calc_pseudo(self,index,physical_pos):
		return 0.0



class Silly02(PseudoMotor):
	"""Just a silly pseudo motor. It doesn't actually do anything."""
	
	pseudo_motor_roles = ("psd 01", "psd 02", "psd 03", "psd 04")
	motor_roles = ("real 01", "real 02", "real 03", "real 04")
		
	def calc_physical(self,index,pseudo_pos):
		return 10.0
	
	def calc_pseudo(self,index,physical_pos):
		return 10.0


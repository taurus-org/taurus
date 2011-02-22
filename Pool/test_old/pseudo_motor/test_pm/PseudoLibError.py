from PseudoMotor import PseudoMotor
#import PseudoMotor

class ErrorPseudoMotor(PseudoMotor):
	some syntax error
	"""Just a silly pseudo motor. It doesn't actually do anything."""
	
	motor_roles = ("Motor on upper Blade","Motor on lower Blade")
		
	def calc_physical(self,index,pseudo_pos):
		return 5.0
	
	def calc_pseudo(self,index,physical_pos):
		return 2.0


from PseudoMotor import PseudoMotor
#import PseudoMotor

class P1(PseudoMotor):
	"""A pseudo motor system for testing properties feature."""
	
	motor_roles = ("m1",)
	class_prop = { 'p_long' : {
				       'Description' : 'A property for demonstrating a long property',
				       'Type' : 'PyTango.DevLong',
				       'DefaultValue' : 987654321
				       },
				 }
				       				       	
	def calc_physical(self,index,pseudo_pos):
		return self.p_long
	
	def calc_pseudo(self,index,physical_pos):
		return self.p_long
	
class P2(PseudoMotor):
	"""A pseudo motor system for testing properties feature: without default value."""
	
	motor_roles = ("m1",)
	class_prop = { 'p_no_dft' : {
				       'Description' : 'A property for demonstrating a long property without default value',
				       'Type' : 'PyTango.DevLong',
				       },
				 }
				       				       	
	def calc_physical(self,index,pseudo_pos):
		return self.p_no_dft
	
	def calc_pseudo(self,index,physical_pos):
		return self.p_no_dft
	
class P3(PseudoMotor):
	"""A pseudo motor system for testing properties feature: All types of data"""
	
	motor_roles = ("m1",)
	class_prop = { 'p_long' : {
				       'Description' : 'A property for demonstrating a long property',
				       'Type' : 'PyTango.DevLong',
				       'DefaultValue' : 987654321
				       },
				   'p_double' : {
				       'Description' : 'A property for demonstrating a double property',
				       'Type' : 'PyTango.DevDouble',
				       'DefaultValue' : 123456.654321
				       },
				   'p_bool' : {
				       'Description' : 'A property for demonstrating a boolean property',
				       'Type' : 'PyTango.DevBoolean',
				       'DefaultValue' : True
				       },
				   'p_string' : {
				       'Description' : 'A property for demonstrating a string property',
				       'Type' : 'PyTango.DevString',
				       'DefaultValue' : 'Some silly default content for a string property'
				       },
				   'p_longArray_tuple' : {
				       'Description' : 'A property for demonstrating a long array property as a tuple',
				       'Type' : 'PyTango.DevVarLongArray',
				       'DefaultValue' : (9876,12345)
				       },
				   'p_longArray_list' : {
				       'Description' : 'A property for demonstrating a long array property as a list',
				       'Type' : 'PyTango.DevVarLongArray',
				       'DefaultValue' : [9876,54321]
				       },
				   'p_doubleArray_tuple' : {
				       'Description' : 'A property for demonstrating a double array property as a tuple',
				       'Type' : 'PyTango.DevVarDoubleArray',
				       'DefaultValue' : (5.1,0.44,333)
				       },
				   'p_doubleArray_list' : {
				       'Description' : 'A property for demonstrating a double array property as a list',
				       'Type' : 'PyTango.DevVarDoubleArray',
				       'DefaultValue' : [5.1,0.44,333]
				       },
				   'p_boolArray_tuple' : {
				       'Description' : 'A property for demonstrating a boolean array property as a tuple',
				       'Type' : 'PyTango.DevVarBooleanArray',
				       'DefaultValue' : (True,False,True)
				       },
				   'p_boolArray_list' : {
				       'Description' : 'A property for demonstrating a boolean array property as a list',
				       'Type' : 'PyTango.DevVarBooleanArray',
				       'DefaultValue' : [True,False,True]
				       },
				   'p_stringArray_tuple' : {
				       'Description' : 'A property for demonstrating a string array property',
				       'Type' : 'PyTango.DevVarStringArray',
				       'DefaultValue' : ('Some silly default content for a string array property','as a tuple!')
				       },
				   'p_stringArray_list' : {
				       'Description' : 'A property for demonstrating a string array property',
				       'Type' : 'PyTango.DevVarStringArray',
				       'DefaultValue' : ['Some silly default content for a string array property','as a list!']
				       },
				 }
				       				       	
	def calc_physical(self,index,pseudo_pos):
		return self.p_double
	
	def calc_pseudo(self,index,physical_pos):
		return self.p_longArray_tuple[0]
		
			
class P4(PseudoMotor):
	"""A pseudo motor system for testing properties feature: wrong default value type."""
	
	motor_roles = ("m1",)
	class_prop = { 'p_no_dft' : {
				       'Description' : 'A property for demonstrating a long property without default value',
				       'Type' : 'PyTango.DevLong',
				       'DefaultValue' : 5.1
				       },
				 }
				       				       	
	def calc_physical(self,index,pseudo_pos):
		return self.p_long
	
	def calc_pseudo(self,index,physical_pos):
		return self.p_long

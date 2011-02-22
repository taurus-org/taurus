from macro import *

################################################################################
#
# Encoder related macros
#
################################################################################

## OmsVme58 Motors:

class get_enconder_position(Macro):
    """Get the encoder position for the specified motor"""
    
    param_def = [
        ['motor', Type.Motor, None, 'Motor name']
    ]
    
    def run(self, motor):
        enc_pos = motor._getAttrValue('positionencoder')
        self.output("Encoder position %.4f" % (enc_pos))


class get_home_position(Macro):
    """Get the home position for the specified motor"""
    
    param_def = [
        ['motor', Type.Motor, None, 'Motor name']
    ]
    
    def run(self, motor):
        home_pos = motor._getAttrValue('homeposition')
        self.output("Home position %.4f" % (home_pos))

class set_home_position(Macro):
    """Set a new home position for the specified motor"""
    
    param_def = [
        ['motor', Type.Motor, None, 'Motor name'],
        ['home_pos',   Type.Float, None, 'New home position']
    ]
    
    def run(self, motor, home_pos):
        old_home_pos = motor._getAttrValue('homeposition')
        local_obj = motor._getAttrEx('homeposition')
        local_obj.write(home_pos)
        self.output("Home position changed from %.4f  to %.4f" % (old_home_pos, home_pos))
        
class get_use_encoder_flag(Macro):
    """Get the value for the flag forcing the use of the encoder position"""
    
    param_def = [
        ['motor', Type.Motor, None, 'Motor name']
    ]
    
    def run(self, motor):
        flag_enc = motor._getAttrValue('flaguseencoderposition')
        if flag_enc == 1:
            self.output("Flag value %d (encoder position used)" % (flag_enc))
        else:
            self.output("Flag value %d (encoder position not used)" % (flag_enc)) 

class set_use_encoder_flag(Macro):
    """Set a new value for the use_encoder flag (1 -> encoder position used)"""
    
    param_def = [
        ['motor', Type.Motor, None, 'Motor name'],
        ['new_value',   Type.Integer, None, 'New flag value']
    ]
    
    def run(self, motor, new_value):
        old_value = motor._getAttrValue('flaguseencoderposition')
        local_obj = motor._getAttrEx('flaguseencoderposition')
        local_obj.write(new_value)
        self.output("FlagUseEncoderPosition change from %d  to %d" % (old_value, new_value)) 

class move_home(Macro):
    """Move specified motor to HomePosition"""
    
    param_def = [
        ['motor', Type.Motor, None, 'Motor name']
    ]
    
    def run(self, motor):
        home_pos = motor._getAttrValue('homeposition')
        local_obj = motor._getAttrEx('movehome')
        dummy_value = 1
        local_obj.write(dummy_value)
        self.output("Motor moved to home position %.4f" % (home_pos)) 
    


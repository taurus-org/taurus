import sys

from macro import *

################################################################################
#
# Motion related macros
#
################################################################################

class _wm(Macro):
    """Show motor positions"""

    param_def = [
        ['motor_list',
         ParamRepeat(['motor', Type.Motor, None, 'Motor to move']),
         None, 'List of motor to show'],
    ]

    def prepare(self, *motor_list, **opts):
        self.table_opts = {}
    
    def run(self, *motor_list):
        motor_width = 9
        motor_names = []
        motor_pos   = []
        motor_list = list(motor_list)
        motor_list.sort()
        for motor in motor_list:
            name = motor.getName()
            motor_names.append([name])
            pos, dial_pos = motor.getPosition(force=True), motor.getDialPosition()
            if pos is None: pos = float('NAN')
            if dial_pos is None: dial_pos = float('NAN')
            motor_pos.append((pos,dial_pos))
            motor_width = max(motor_width,len(name))

        fmt = '%c*.%df' % ('%',motor_width - 5)

        table = Table(motor_pos, elem_fmt=[fmt],
                      col_head_str=motor_names, col_head_width=motor_width,
                      **self.table_opts)
        for line in table.genOutput():
            self.output(line)
            
            
class wa(Macro):
    """Show all motor position"""

    def prepare(self, **opts):
        self.all_motors = self.findObjs('.*', type_class=Type.Motor)
        self.table_opts = {}
    
    def run(self):
        nr_motors = len(self.all_motors)
        if nr_motors == 0:
            self.output('No motor defined')
            return

        self.output('Current Positions  (user, dial)')
        self.output('')
        
        self.execMacro('_wm',*self.all_motors, **self.table_opts)
        
class pwa(Macro):
    """Show all motor positions in a pretty table"""

    def run(self):
        self.execMacro('wa', **Table.PrettyOpts)

class set_lim(Macro):
    """Sets the software limits on the specified motor hello"""
    param_def = [
        ['motor', Type.Motor, None, 'Motor name'],
        ['low',   Type.Float, None, 'lower limit'],
        ['high',   Type.Float, None, 'upper limit']
    ]
    
    def run(self, motor, low, high):
        name = motor.getName()
        self.debug("Setting user limits for %s" % name)
        motor.getPositionObj().setLimits(low,high)
        self.output("%s limits set to %.4f %.4f (user units)" % (name, low, high))

class set_lm(Macro):
    """Sets the dial limits on the specified motor"""
    param_def = [
        ['motor', Type.Motor, None, 'Motor name'],
        ['low',   Type.Float, None, 'lower limit'],
        ['high',   Type.Float, None, 'upper limit']
    ]
    
    def run(self, motor, low, high):
        name = motor.getName()
        self.debug("Setting dial limits for %s" % name)
        motor.getDialPositionObj().setLimits(low,high)
        self.output("%s limits set to %.4f %.4f (dial units)" % (name, low, high))
        
class set_pos(Macro):
    """Sets the USER position of the motor to the specified value (by changing DIAL and keeping OFFSET)"""
    
    param_def = [
        ['motor', Type.Motor, None, 'Motor name'],
        ['pos',   Type.Float, None, 'Position to move to']
    ]
    
    def run(self, motor, pos):
        name = motor.getName()
        old_pos = motor.getPosition(force=True)
        motor.definePosition(pos)
        self.output("%s reset from %.4f to %.4f" % (name, old_pos, pos))

class set_user_pos(Macro):
    """Sets the USER position of the motor to the specified value (by changing OFFSET and keeping DIAL)"""
    
    param_def = [
        ['motor', Type.Motor, None, 'Motor name'],
        ['pos',   Type.Float, None, 'Position to move to']
    ]
    
    def run(self, motor, pos):
        name = motor.getName()
        old_pos = motor.getPosition(force=True)
        offset_attr = motor.getAttribute('Offset')
        old_offset = offset_attr.read().value
        new_offset = pos - (old_pos - old_offset)
        offset_attr.write(new_offset)
        self.output("%s reset from %.4f (offset %.4f) to %.4f (offset %.4f)" % (name, old_pos, old_offset, pos, new_offset))

class wm(Macro):
    """Show the position of the specified motors."""

    param_def = [
        ['motor_list',
         ParamRepeat(['motor', Type.Motor, None, 'Motor to move']),
         None, 'List of motor to show'],
    ]

    def prepare(self, *motor_list, **opts):
        self.table_opts = {}
        
    def run(self, *motor_list):
        motor_width = 10
        motor_names = []
        motor_pos   = []
        
        for motor in motor_list:
            name = motor.getName()
            motor_names.append([name] * 2)
            posObj = motor.getPositionObj()
            upos = map(str, [posObj.getMaxValue(), motor.getPosition(force=True), posObj.getMinValue()])
            dPosObj = motor.getDialPositionObj()
            dpos = map(str, [dPosObj.getMaxValue(), motor.getDialPosition(), dPosObj.getMinValue()])
            pos_data = [''] + upos + [''] + dpos
            
            motor_pos.append(pos_data)

        elem_fmt = (['%*s'] + ['%*s'] * 3) * 2
        row_head_str = ['User', ' High', ' Current', ' Low',
                        'Dial', ' High', ' Current', ' Low']
        table = Table(motor_pos, elem_fmt=elem_fmt, row_head_str=row_head_str,
                      col_head_str=motor_names, col_head_width=motor_width,
                      **self.table_opts)
        for line in table.genOutput():
            self.output(line)

class pwm(Macro):
    """Show the position of the specified motors in a pretty table"""

    param_def = [
        ['motor_list',
         ParamRepeat(['motor', Type.Motor, None, 'Motor to move']),
         None, 'List of motor to show'],
    ]

    def run(self, *motor_list):
        self.execMacro('wm', *motor_list, **Table.PrettyOpts)

class mv(Macro):
    """Move motor(s) to the specified position(s) and hello"""

    param_def = [
       [ 'motor_pos_list',
         ( [ 'motor', Type.Motor, None, 'Motor to move'],
           [ 'pos',   Type.Float, None, 'Position to move to'],
           { 'min' : 1, 'max' : None } ),
        None, 'List of motor/position pairs'],
    ]

    param_def = [
       ['motor_pos_list',
        ParamRepeat(['motor', Type.Motor, None, 'Motor to move'],
                    ['pos',   Type.Float, None, 'Position to move to']),
        None, 'List of motor/position pairs'],
    ]

    def run(self, *motor_pos_list):
        motors, positions = [], []
        for motor, pos in motor_pos_list:
            motors.append(motor)
            positions.append(pos)
            self.debug("Starting %s movement to %s", motor.getName(), pos)
        motion = self.getMotion(motors)
        motion.move(positions)


class mv2(Macro):
    """Move motor(s) to the specified position(s)"""

    param_def = [
       [ 'motor_pos_list',
         ( [ 'motor', Type.Motor, None, 'Motor to move'],
           [ 'pos',   Type.Float, None, 'Position to move to'],
           { 'min' : 1, 'max' : None } ),
        None, 'List of motor/position pairs'],
    ]

    param_def = [
       ['motor_pos_list',
        ParamRepeat(['motor', Type.Motor, None, 'Motor to move'],
                    ['pos',   Type.Float, None, 'Position to move to']),
        None, 'List of motor/position pairs'],
    ]

    def run(self, *motor_pos_list):
        motors, positions = [], []
        for motor, pos in motor_pos_list:
            motors.append(motor)
            positions.append(pos)
            self.debug("Starting %s movement to %s", motor.getName(), pos)
        orig_p = motor_pos_list[0][0].getPosition(force=True)
        final_p = motor_pos_list[0][1]
        dp = abs(final_p - orig_p)
        
        motion = self.getMotion(motors)
        self.info("Start move")
        for p in motion.iterMove(positions):
            curr_dp = abs(p - orig_p)
            yield curr_dp/dp*100.0
        yield 100.0
        self.info("end")


class mstate(Macro):

        param_def = [['motor', Type.Motor, None, 'Motor to move']]

        def run(self, motor):
            self.info("Motor %s" % str(motor.getState()))

class umv(Macro):
    """Move motor(s) to the specified position(s) and update"""

    param_def = mv.param_def

    def prepare(self, *motor_pos_list, **opts):
        self.all_names = []
        self.all_pos = []
        idx = 0
        self.print_pos = False
        for motor, pos in motor_pos_list:
            self.all_names.append([motor.getName()])
            pos, posObj = motor.getPosition(force=True), motor.getPositionObj()
            self.all_pos.append([pos])
            posObj.subscribeEvent(self.positionChanged, motor)
        
    def run(self, *motor_pos_list):
        self.print_pos = True
        pars = []
        for motor, pos in motor_pos_list:
            pars.append(motor)
            pars.append(pos)

        self.execMacro('mv', *pars)
        self.finish()
 
    def finish(self):
        self._clean()
        self.printAllPos()
 
    def on_abort(self):
        self.finish()
        
    def _clean(self):
        for motor, pos in self.getParameters():
            posObj = motor.getPositionObj()
            try:
                posObj.unsubscribeEvent(self.positionChanged, motor)
            except Exception, e:
                print str(e)
                raise e
    
    def positionChanged(self, motor, position):
        try:
            idx = self.all_names.index([motor.getName()])
            self.all_pos[idx] = [position]
            if self.print_pos:
                self.printAllPos()
        except Exception,e:
            print str(e)
            
    def printAllPos(self):
        motor_width = 10
        table = Table(self.all_pos, elem_fmt=['%*.4f'],
                      col_head_str=self.all_names, col_head_width=motor_width)
        self.outputBlock(table.genOutput())
        self.flushOutput()

class mvr(Macro):
    """Move motor(s) relative to the current position(s)"""

    param_def = [
       ['motor_disp_list',
        ParamRepeat(['motor', Type.Motor, None, 'Motor to move'],
                    ['disp',  Type.Float, None, 'Relative displacement']),
        None, 'List of motor/displacement pairs'],
    ]
    
    def run(self, *motor_disp_list):
        motor_pos_list = []
        for motor, disp in motor_disp_list:
            pos = motor.getPosition(force=True) 
            if pos is None:
                self.error("Cannot get %s position" % motor.getName())
                return
            else:
                pos += disp
            motor_pos_list.extend([motor, pos])
        self.execMacro('mv', *motor_pos_list)

class umvr(Macro):
    """Move motor(s) relative to the current position(s) and update"""

    param_def = mvr.param_def

    def run(self, *motor_disp_list):
        motor_pos_list = []
        for motor, disp in motor_disp_list:
            pos = motor.getPosition(force=True) 
            if pos is None:
                self.error("Cannot get %s position" % motor.getName())
                return
            else:
                pos += disp
            motor_pos_list.extend([motor, pos])
        self.execMacro('umv', *motor_pos_list)


################################################################################
#
# Data acquisition related macros
#
################################################################################


class ct(Macro):
    """Count for the specified time on the active measurement group"""

    env = ('ActiveMntGrp',)

    param_def = [
       ['integ_time', Type.Float, 1.0, 'Integration time']
    ]

    def prepare(self, integ_time, **opts):
        mnt_grp_name = self.getEnv('ActiveMntGrp')
        self.mnt_grp = self.getObj(mnt_grp_name, type_class=Type.MeasurementGroup)

    def run(self, integ_time):
        if self.mnt_grp is None:
            self.error('ActiveMntGrp is not defined or has invalid value')
            return

        self.debug("Counting for %s sec", integ_time)
        self.outputDate()
        self.output('')
        self.flushOutput()

        state, data = self.mnt_grp.count(integ_time)

        names, counts = [], []
        for ch_name in self.mnt_grp.getChannelNames():
            names.append('  %s' % ch_name)
            counts.append(data.get(ch_name))
    
        table = Table([counts], row_head_str=names, row_head_fmt='%*s',
                      col_sep='  =  ')
        for line in table.genOutput():
            self.output(line)


class uct(Macro):
    """Count on the active measurement group and update"""

    env = ('ActiveMntGrp',)

    param_def = [
       ['integ_time', Type.Float, 1.0, 'Integration time']
    ]

    def prepare(self, integ_time, **opts):
        
        self.print_value = False
        
        mnt_grp_name = self.getEnv('ActiveMntGrp')
        self.mnt_grp = self.getObj(mnt_grp_name, type_class=Type.MeasurementGroup)

        if self.mnt_grp is None:
            return

        names, nan = self.mnt_grp.getChannelNames(), float('nan')
        self.names    = [ [n] for n in names ]
        
        self.values   = len(names)*[ [nan] ]
        self.channels = self.mnt_grp.getChannelAttrExs()

        for ch_attr_ex in self.channels:
            ch_attr_ex.subscribeEvent(self.counterChanged, ch_attr_ex)

    def printAllValues(self):
        ch_width = 10
        table = Table(self.values, elem_fmt=['%*.4f'], col_head_str=self.names, 
                      col_head_width=ch_width)
        self.outputBlock(table.genOutput())
        self.flushOutput()
    
    def counterChanged(self, ch_attr, value):
        idx = self.channels.index(ch_attr)
        self.values[idx] = [value]
        if self.print_value:
            self.printAllValues()
        
    def run(self, integ_time):
        if self.mnt_grp is None:
            self.error('ActiveMntGrp is not defined or has invalid value')
            return
        
        self.print_value = True
        
        state, data = self.mnt_grp.count(integ_time)

        for ch_attr_ex in self.mnt_grp.getChannelAttrExs():
            ch_attr_ex.unsubscribeEvent(self.counterChanged, ch_attr_ex)
        self.printAllValues()


class settimer(Macro):
    """Defines the timer channel for the active measurement group"""
    
    env = ('ActiveMntGrp',)
    
    param_def = [
       ['timer', Type.ExpChannel,   None, 'Timer'],
    ]
    
    def run(self,timer):
        mnt_grp_name = self.getEnv('ActiveMntGrp')
        mnt_grp = self.getObj(mnt_grp_name, type_class=Type.MeasurementGroup)

        if mnt_grp is None:
            self.error('ActiveMntGrp is not defined or has invalid value.\n' \
                       'please define a valid active measurement group ' \
                       'before setting a timer')
            return
        
        try:
            mnt_grp.setTimer(timer.getName())
        except Exception,e:
            self.output(str(e))
            self.output("%s is not a valid channel in the active measurement group" % timer)


class twice(Macro):
    """twice description."""

    # uncomment the following lines as necessary. Otherwise you may delete them
    param_def = [ [ "value", Type.Float, 23, "value to be doubled" ] ]
    result_def = [ [ "result", Type.Float, 23, "the double of the given value" ] ]
    #hints = {}
    #env = (,)
    
    # uncomment the following lines if need prepare. Otherwise you may delete them
    #def prepare(self):
    #    pass
        
    def run(self, n):
        return 2*n

class th_exc(Macro):
    
    def run(self):
        raise Exception("An exception in a macro!")


################################################################################
#
# Tango getters and setters for different pool elements
#
################################################################################

class get_attr(Macro):
    """get_attr.
    For a given pool element, get values for it's corresponding attributes.
    EXAMPLE: get_attr my_motor Sign Offset
    NOTE: At some point the 'elem' param type should be changed to the not
    available yet: Type.PoolElem(ent)
    """
    param_def = [
        ['element', Type.String, None, 'Pool element to read.'],
        ['attributes',
         ParamRepeat(['attribute', Type.String, None, 'Attribute to be read']),
         None, 'List of attributes']
    ]

    def run(self, element, *attributes):
        for attribute in attributes:
            # Get the element
            # Get the attribute
            # Get the display value
            element_obj = self.getObj(element)
            element_obj_attr = element_obj.getAttribute(attribute)
            display_value = element_obj_attr.getDisplayValue(cache=False)
            
            get_info = element+'.'+attribute+' -> '+display_value
            print(get_info)
            
class set_attr(Macro):
    """set_attr.
    For a given pool element, set values to it's corresponding attributes.
    EXAMPLE: set_attr my_motor Sign -1 Offset 10.4
    NOTE: At some point the 'elem' param type should be changed to the not
    available yet: Type.PoolElem(ent)
    NOTE2: Right now, Boolean attributes can only be set to False by ''.
    """
    param_def = [
        ['element', Type.String, None, 'Pool element to operate.'],
        ['attributes_and_values',
         ParamRepeat(['attribute', Type.String, None, 'Attribute to be written'],
                     ['value', Type.String, None, 'Value to set']),
         None, 'List of pairs: attribute, value']
    ]

    def run(self, element, *attributes_and_values):
        for attribute, value in attributes_and_values:
            # If attribute is Position (dangerous) -> bypass
            # Get the element
            # Get the attribute
            # Write the value
            if attribute.lower() == 'position':
                self.warning(set_info+': This is a dangerous operation, use a macro to move')
                continue
            element_obj = self.getObj(element)
            element_obj_attr = element_obj.getAttribute(attribute)
            element_obj_attr.write(value)
            
            set_info = element+'.'+attribute+' <- '+value
            print(set_info)
            
class get_attr_cfg(Macro):
    """get_attr_cfg.
    For a given pool element, get values for it's corresponding attribute configurations.
    EXAMPLE: get_attr my_motor Position unit Position min_value Position max_value
    NOTE: At some point the 'elem' param type should be changed to the not
    available yet: Type.PoolElem(ent)
    """
    param_def = [
        ['element', Type.String, None, 'Pool element to read.'],
        ['attributes_and_configs',
         ParamRepeat(['attribute', Type.String, None, 'Attribute to be read'],
                     ['config', Type.String, None, 'Configuration parameter to be read']),
         None, 'List of attributes and configs']
    ]

    def run(self, element, *attributes_and_configs):
        for attribute, config in attributes_and_configs:
            # Get the element
            # Get the attribute
            # Get the attribute config value
            element_obj = self.getObj(element)
            element_obj_attr = element_obj.getAttribute(attribute)
            attr_cfg_value = element_obj_attr.getParam(config)

            get_cfg_info = element+'.'+attribute+'.'+config+' -> '+attr_cfg_value
            print(get_cfg_info)
            
class set_attr_cfg(Macro):
    """set_attr.
    For a given pool element, set values to it's corresponding attribute configurations.
    EXAMPLE: get_attr my_motor Position unit Position min_value Position max_value
    NOTE: At some point the 'elem' param type should be changed to the not
    available yet: Type.PoolElem(ent)
    """
    param_def = [
        ['element', Type.String, None, 'Pool element to operate.'],
        ['attributes_and_configs_values',
         ParamRepeat(['attribute', Type.String, None, 'Attribute to be written'],
                     ['config', Type.String, None, 'Configuration parameter to be written'],
                     ['value', Type.String, None, 'Value to set']),
         None, 'List of pairs: attribute, value']
    ]

    def run(self, element, *attributes_and_configs_and_values):
        for attribute, config, value in attributes_and_configs_and_values:
            # Get the element
            # Get the attribute
            # Write the attribute's config value
            element_obj = self.getObj(element)
            element_obj_attr = element_obj.getAttribute(attribute)
            element_obj_attr.setParam(config, value)

            set_info = element+'.'+attribute+'.'+config+' <- '+value
            print(set_info)

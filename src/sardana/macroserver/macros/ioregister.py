from macro import *

import array

class lsioreg(Macro):
    """Lists all existing input/output registers"""
    
    def run(self):

        all_ioreg = self.findObjs('.*', type_class=Type.IORegister)

        nr_ioreg = len(all_ioreg)
        if nr_ioreg == 0:
            self.output('No input/output registers defined')
            return

        out = List(['Name', 'Family'])
       
        for ioreg in all_ioreg:
            pool = ioreg.getPool()            
            ctrl = self.findObjs(ioreg.info.ctrl_name, type_class=Type.Controller)
            family = "Not specified"
            if len(ctrl) > 0:
                class_name = ctrl[0].info.klass
                ctrl_class = pool.getCtrlClassByName(class_name)
                if ctrl_class:
                    family = ctrl_class.getGender()
            out.appendRow([ioreg.getName(), family])
        
        for line in out.genOutput():
            self.output(line)



class write_ioreg(Macro):
    """Writes a value to an input register"""
    
    param_def = [
       ['input/output register', Type.IORegister, None, 'input/output register'],
       ['data', Type.Integer, None, 'value to be send']
    ]
    
    def run(self, ioreg, data):
        name = ioreg.getName()
        o = "Writing " + str(data) + " to " + name + " register "
        self.output(o)
        data = ioreg.writeIORegister(data)



class read_ioreg(Macro):
    """Reads an output register"""
    
    param_def = [
       ['input/output register', Type.IORegister, None, 'input/output register']
    ]
    
    def run(self, ioreg):
        name = ioreg.getName()
        data = ioreg.readIORegister()
        o = "Reading " +  name + " register "
        self.output(o)
        self.output(data)

from macro import *

import array

class lscom(Macro):
    """Lists all existing communication channels"""
    
    def run(self):

        all_comch = self.findObjs('.*', type_class=Type.ComChannel)

        nr_comch = len(all_comch)
        if nr_comch == 0:
            self.output('No communication channels defined')
            return

        out = List(['Name', 'Family'])
       
        for comch in all_comch:
            pool = comch.getPool()            
            ctrl = self.findObjs(comch.info.ctrl_name, type_class=Type.Controller)
            family = "Not specified"
            if len(ctrl) > 0:
                class_name = ctrl[0].info.klass
                ctrl_class = pool.getCtrlClassByName(class_name)
                if ctrl_class:
                    family = ctrl_class.getGender()
            out.appendRow([comch.getName(), family])
        
        for line in out.genOutput():
            self.output(line)

    
class put(Macro):
    """Sends a string to the communication channel"""
    param_def = [
       ['communication channel', Type.ComChannel, None, 'the communication channel'],
       ['data', Type.String, None, 'data to be sent']
    ]
    
    def run(self, comch, data):
        name = comch.getName()
        nb = comch.write(data)
        o = str(nb) + " bytes sent to " + name
        self.output(o)


class get(Macro):
    """Reads and outputs the data from the communication channel"""
    
    param_def = [
       ['communication channel', Type.ComChannel, None, 'the communication channel'],
       ['maximum length', Type.String, -1, 'maximum number of bytes to read']
    ]
    
    def run(self, comch, maxlen):
        name = comch.getName()
        data = comch.command_inout("read",maxlen)
        
        datastr = array.array('B',data).tostring()
        self.output("'" + datastr + "'")
        self.output(data)
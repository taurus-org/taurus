#!/usr/bin/env python
import sys

"""
ControllerTemplate.py: Create a basic controller's template. 
Its parameters are  the file name plus .py, 
    the class inherited if it had (optional)
    and "yes" if you want to use the obsolete convention.
The necessary "defs" are marked as #TODO

python ControllerTemplate.py ExampleClass.py InheritedClass NoCT
"""
__author__ = "Carlos Falcon - cfalcon@cells.es"

class ControllerTemplate():
    def __init__(self,f, e=""):
        self.filename = f
        self.end = e
        self.ind = 'ind' 
    #    pass
    def addHead(self):
        f=open(self.filename,"w")
        f.write('##############################################################################\n'+\
                '##\n'+\
                '## This file is part of Sardana\n'+\
                '##\n'+\
                '## http://www.sardana-controls.org/\n'+\
                '##\n'+\
                '## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain\n'+\
                '##\n'+\
                '## Sardana is free software: you can redistribute it and/or modify\n'+\
                '## it under the terms of the GNU Lesser General Public License as published by\n'+\
                '## the Free Software Foundation, either version 3 of the License, or\n'+\
                '## (at your option) any later version.\n'+\
                '##\n'+\
                '## Sardana is distributed in the hope that it will be useful,\n'+\
                '## but WITHOUT ANY WARRANTY; without even the implied warranty of\n'+\
                '## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n'+\
                '## GNU Lesser General Public License for more details.\n'+\
                '##\n'+\
                '## You should have received a copy of the GNU Lesser General Public License\n'+\
                '## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.\n'+\
                '##\\n'+\
                '##############################################################################\n\n')\

    def addIncludes(self,inherit,others=None):
        f = open(self.filename,"a")
        text = "from sardana import State\n"
        if inherit!="":
            text = text+"from sardana.pool.controller import "+inherit+"\n"
            if inherit.find("Motor")>=0:
                self.ind = 'axis'
        if others is not None:
            text = text+others
        text = text+"#ADD others includes\n\n"
        f.write(text)
        #f.close()

    def createBasicClass(self):
        f = open(self.filename,"a")
        text = "#TODO - Delete it if you don't need\n"
        text = text +'class BasicClass():\n'+\
               '\tpass\n\n'
        f.write(text)

    def createMainClass(self,inherit):
        f = open(self.filename,"a")
        text = "class "+self.filename[0:len(self.filename)-3]+"("+inherit+"):\n"+\
        '\t"""Description""" #TODO\n'+\
        '\tgender = "Simulation"\n'+\
        '\tmodel  = "Basic"\n'+\
        '\torganization = "CELLS - ALBA"\n'+\
        '\timage = "IMAGE.png"\n'+\
        '\tlogo = "ALBA_logo.png"\n\n'+\
        '\t#TODO - Delete it if you don\'t need\n'+\
        '\tctrl_properties= { \'AAA\' : { \'Type\' : \'DevString\', \'Description\' : \'AAA\' } }\n'+\
        '\taxis_attributes = { \'AAA\' : { \'type\' : str, \'Description\' : \'AAA\' }}\n\n'+\
        '\tMaxDevice = 1024 #TODO Standar value\n\n'

        fun = '# --------------------------------------------------------------------------\n'+\
            '# Init()\n'+\
            '# --------------------------------------------------------------------------\n'+\
            '\tdef __init__(self, inst, props, *args, **kwargs):\n' 
        if inherit!="":
            fun = fun + '\t\t' + inherit + '.__init__(self, inst, props, *args, **kwargs)\n'
        fun = fun + '\t\t#TODO\n'
        text = text + fun
        
        fun = '# --------------------------------------------------------------------------\n'+\
            '# AddDevice/DelDevice()\n'+\
            '# --------------------------------------------------------------------------\n'+\
            '\tdef AddDevice(self,'+self.ind+'):\n'
        fun = fun + '\t\t#TODO\n' 
        fun = fun + '\tdef DeleteDevice(self, '+self.ind+'):\n'
        fun = fun + '\t\t#TODO\n' 
        text = text + fun

        fun = '# --------------------------------------------------------------------------\n'+\
            '# State()\n'+\
            '# --------------------------------------------------------------------------\n'+\
            '\tdef PreStateOne'+self.end+'(self, '+self.ind+'):\n'+'\t\tpass\n' 
        fun = fun + '\tdef StateOne(self, '+self.ind+'):\n'
        fun = fun + '\t\tstate = State.On\n'
        fun = fun + '\t\tstatus = "Undefined"\n'
        if inherit.find("Motor")>=0:
            fun = fun + '\t\tswitchstate = 0"\n'
            fun = fun + '\t\t#TODO\n' 
            fun = fun + '\t\treturn state, status, switchstate"\n'
        else:        
            fun = fun + '\t\t#TODO\n' 
            fun = fun + '\t\treturn state, status\n'

        fun = fun + '\tdef PreStateAll'+self.end+'(self):\n'
        fun = fun + '\t\tpass\n' 

        fun = fun + '\tdef StateAll'+self.end+'(self):\n'
        fun = fun + '\t\tpass\n' 
        text = text + fun

        fun = '# --------------------------------------------------------------------------\n'+\
            '# Read()\n'+\
            '# --------------------------------------------------------------------------\n'+\
            '\tdef PreReadOne'+self.end+'(self, '+self.ind+'):\n'+'\t\tpass\n'
        fun = fun + '\tdef ReadOne(self, '+self.ind+'):\n'
        fun = fun + '\t\t#TODO\n'
        fun = fun + '\tdef PreReadAll'+self.end+'(self):\n'
        fun = fun + '\t\tpass\n' 
        fun = fun + '\tdef ReadAll'+self.end+'(self):\n'
        fun = fun + '\t\tpass\n' 
 
        text = text + fun

        fun = '# --------------------------------------------------------------------------\n'+\
            '# Start/Stop()\n'+\
            '# --------------------------------------------------------------------------\n'+\
            '\tdef PreStartOne'+self.end
        if inherit.find("Motor")>=0:
             fun = fun + '(self, '+self.ind+', pos):\n'
        else:
             fun = fun + '(self, '+self.ind+'):\n'
        fun = fun + '\t\tpass\n' 
        fun = fun + '\tdef StartOne'+self.end+'(self, '+self.ind+', pos):\n'
        fun = fun + '\t\t#TODO\n' 

        fun = fun + '\tdef AbortOne(self, '+self.ind+'):\n'
        fun = fun + '\t\t#TODO\n' 

        fun = fun + '\tdef StopOne(self, '+self.ind+'):\n'
        fun = fun + '\t\tself.AbortOne('+self.ind+')\n' 

        fun = fun + '\tdef PreStartAll'+self.end+'(self):\n'
        fun = fun + '\t\tpass\n' 

        fun = fun + '\tdef StartAll'+self.end+'(self):\n'
        fun = fun + '\t\tpass\n' 

        fun = fun + '\tdef AbortAll(self):\n'
        fun = fun + '\t\tpass\n' 
        text = text + fun

        fun = '# --------------------------------------------------------------------------\n'+\
            '# SetAxisPar/GetAxisPar()\n'+\
            '# --------------------------------------------------------------------------\n'+\
            '\tdef SetAxisPar(self, '+self.ind+', name, value):\n'
        fun = fun + '\t\t#TODO - Delete it if you don\'t need\n' 

        fun = fun + '\tdef GetAxisPar(self, '+self.ind+', name):\n'
        fun = fun + '\t\t#TODO - Delete it if you don\'t need\n' 
        text = text + fun

        fun = '# --------------------------------------------------------------------------\n'+\
            '# SetAxisExtraPar/GetAxisExtraPar()\n'+\
            '# --------------------------------------------------------------------------\n'+\
            '\tdef SetAxisExtraPar(self, '+self.ind+', name, value):\n'
        fun = fun + '\t\t#TODO - Delete it if you don\'t need\n' 

        fun = fun + '\tdef GetAxisExtraPar(self, '+self.ind+', name):\n'
        fun = fun + '\t\t#TODO - Delete it if you don\'t need - \n' 
        text = text + fun
        f.write(text)


def main():
    #Add MACRO_PATH
    filename = ""
    end = ""
    inherit = ""
    if(len(sys.argv) > 1):
        print "Creating " + sys.argv[1]
        filename = sys.argv[1]
        if(len(sys.argv) > 2):
            inherit = sys.argv[2]
        if(len(sys.argv) > 3):
            end = "CT"
        s= ControllerTemplate(filename,end)
        s.addHead()
        s.addIncludes(inherit)
        s.createBasicClass()
        s.createMainClass(inherit)
    else:
        print "Please introduce filename"

if __name__ == "__main__":
    main()

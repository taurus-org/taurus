from sardana.macroserver.macro import *

import array

class mca_start(Macro):
    """Starts an mca"""
    
    param_def = [
       ['mca', Type.ExpChannel, None, 'mca']
    ]
    
    def run(self, mca):
        name = mca.getName()
        mca.Start()
        o = "Starting " +  name
        self.output(o)

class mca_stop(Macro):
    """Stops an mca"""
    
    param_def = [
       ['mca', Type.ExpChannel, None, 'mca']
    ]
    
    def run(self, mca):
        name = mca.getName()
        mca.Abort()
        o = "Stopping " +  name
        self.output(o)

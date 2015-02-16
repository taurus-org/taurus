##############################################################################
##
## This file is part of Sardana
##
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""Library of specific macros for performing specific experimental techniques
     
"""

__all__ = ["xas_acq"]

__docformat__ = 'restructuredtext'

import numpy
    
from sardana.macroserver.macro import *
from sardana.macroserver.scan import *

class xas_acq(Macro, Hookable):
    """
    .. warning:: This macro is still under development. It may change.
    
    Perform an X-ray absorption scan experiment. Data is stored in a NXxas-compliant file.
    """
    hints = { 'FileRecorder':'NXxas_FileRecorder', 'scan' : 'xas_acq', 'allowsHooks':('pre-move', 'post-move', 'pre-acq', 'post-acq', 'post-step') }
    #env = ('MonochromatorEnergy', )#'AbsorbedBeam', 'IncomingBeam', 'Monitor') #this hints that the macro requires the ActiveMntGrp environment variable to be set

    param_def = [
       ['start',  Type.Float,    None, 'start energy in keV'],
       ['final',  Type.Float,    None, 'final energy in keV'],
       ['nr_interv',  Type.Integer,  None, 'Number of energy intervals'],
       ['integ_time', Type.Float,    None, 'Integration time in s']
    ]

    def prepare(self, start, final, nr_interv, integ_time, **opts):
        #parse the user parameters
        self.starts = numpy.array([start], dtype='d')
        self.finals = numpy.array([final], dtype='d')
        self.integ_time = integ_time

        self.nr_points = nr_interv+1
        self.interv_sizes = ( self.finals - self.starts) / nr_interv
        self.name='xas_acq'
        env = opts.get('env',{}) #the "env" dictionary may be passed as an option
        env['integ_time'] = integ_time
        
        #print "!!!!!", type(self.getInstrument('/instrument/monochromator')), self.getEnv('MonochromatorEnergy', macro_name=self.name)
        #ElementWithInterface('Instrument','monochromator')
        for n,e in self.getElementsWithInterface('Instrument').iteritems():
            inst=e.getObj()
            print n, e.name, inst.getFullName(), type(e), type(inst), type(inst.getPoolObj())#,inst.getElements()
            
        #maybe I should use the instrument interface to obtain the right counters
        
        env['monochromator'] = monochromator = self.getEnv('MonochromatorEnergy', macro_name=self.name)
        energymotor = self.getMoveable(monochromator)
        xasMntGrp = self.getMeasurementGroup(self.getEnv('xasMntGrp', macro_name=self.name))
        
        xasMntGrp=xasMntGrp.getObj()
        monitor,incbeam,absbeam = xasMntGrp.getChannelNames()[:3]
        env['monitor'] = monitor
        env['absbeam'] = absbeam
        env['incbeam'] = incbeam
        
#        print "!!!!!!!!",xasMntGrp.getObj().getElements()
        
        
#        absbeam =  self.getExpChannel(self.getEnv('AbsorbedBeam')) #this should be get measurement group (e.g., second channel?)
#        incbeam =  self.getExpChannel(self.getEnv('IncomingBeam')) #this should be get measurement group (e.g., first channel?)
#        monitor =  self.getExpChannel(self.getEnv('Monitor')) #this should be get from the monitor of the measurement group
        
        
        #create an instance of GScan (in this case, of its child, SScan
        self._gScan=SScan(self, generator=self._generator, moveables=[energymotor], env=env) 
  
    def _generator(self):
        step = {}
        step["integ_time"] =  self.integ_time
        step["post-acq-hooks"] = self.getHooks('post-acq') +  self.getHooks('_NOHINT_')
        step["post-step-hooks"] = self.getHooks('post-step')
        step["check_func"] = []
        for point_no in xrange(self.nr_points):
            step["positions"] = self.starts + point_no * self.interv_sizes
            step["point_id"] = point_no
            yield step
    
    def run(self,*args):
        for step in self._gScan.step_scan(): #just go through the steps
            yield step
        
    @property
    def data(self):
        return self._gScan.data #the GScan provides scan data

    
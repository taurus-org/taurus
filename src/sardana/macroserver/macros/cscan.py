##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
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

"""
    Macro library containning scan macros for the macros server Tango device 
    server as part of the Sardana project.
   
   Available Macros are:
     ascanc
"""

__all__ = ["ascanc"]

__docformat__ = 'restructuredtext'

from sardana.macroserver.macro import *
from sardana.macroserver.scan import *

class ascanc(Macro, Hookable):
    """Simplest example of continuous scan: a continuous ascan giving a compact table"""

    hints = { 'scan' : 'ascanc', 'allowsHooks':('pre-move', 'post-move', 'pre-acq', 'post-acq', 'post-step') }
    env = ('ActiveMntGrp',)

    param_def = [
       ['motor',      Type.Moveable, None, 'Motor to move'],
       ['start_pos',  Type.Float,    None, 'Scan start position'],
       ['final_pos',  Type.Float,    None, 'Scan final position'],
       ['acq_period', Type.Float,    None, 'Period between acquisitions']
    ]

    def prepare(self, motor, start_pos, final_pos, acq_period, 
                **opts):
        
        self.starts = numpy.array([start_pos], dtype='d')
        self.finals = numpy.array([final_pos], dtype='d')
        self.acq_period = acq_period
        self.opts = opts

        self.nr_waypoints = 2
        self.way_lengths = ( self.finals - self.starts) / (self.nr_waypoints -1)
        self.name='ascanc'
        
        moveables=[motor]
        env=opts.get('env',{})
        constrains = []
        extrainfodesc = []
                
        self._cScan = CScan(self, self._waypoint_generator, self._period_generator, moveables, env, constrains, extrainfodesc) #!!!
  

    def _waypoint_generator(self):
        step = {}
        step["post-acq-hooks"] = []
        step["post-step-hooks"] = []
        step["check_func"] = []
        for point_no in xrange(self.nr_waypoints):
            step["positions"] = self.starts + point_no * self.way_lengths
            step["waypoint_id"] = point_no
            yield step
                
    
    def _period_generator(self):
        step = {}
        step["acq_period"] =  self.acq_period
        step["post-acq-hooks"] = []
        step["post-step-hooks"] = []
        step["check_func"] = []
        step['extrainfo'] = {}
        point_no = 0
        while(True):
            point_no += 1
            step["point_id"] = point_no
            yield step
    
    def run(self,*args):
        self._cScan.scan()
        
    @property
    def data(self):
        return self._cScan.data

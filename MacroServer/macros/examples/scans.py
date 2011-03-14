"""
    Macro library containning examples demonstrating specific features or tricks
    for programming macros for Sardana.
   
   Available Macros are:
     ascanr
     ToothedTriangle
     ascanc
     
"""

import os
import numpy

from macro import *
from scan import *

class ascanr(Macro, Hookable):
    hints = { 'scan' : 'ascanr', 'allowsHooks':('pre-move', 'post-move', 'pre-acq', 'post-acq', 'post-step') }
    env = ('ActiveMntGrp',)
    
    """This is an example of how to handle adding extra info columns in a scan.
    Does the same than ascan but repeats the acquisitions "repeat" times for each step. 
    It could be implemented deriving from aNscan, but I do it like this for clarity.
    Look for the comments with "!!!" for tips specific to the extra info columns
    I do not support constrains in this one for simplicity (see ascan for that)
    
    Do an absolute scan of the specified motor, repeating measurements in each step.
    ascanr scans one motor, as specified by motor. The motor starts at the
    position given by start_pos and ends at the position given by final_pos.
    At each step, the acquisition will be repeated "repeat" times
    The step size is (start_pos-final_pos)/nr_interv. The number of data points collected
    will be (nr_interv+1)*repeat. Count time for each acquisition is given by time which if positive,
    specifies seconds and if negative, specifies monitor counts. """

    param_def = [
       ['motor',      Type.Motor,   None, 'Motor to move'],
       ['start_pos',  Type.Float,   None, 'Scan start position'],
       ['final_pos',  Type.Float,   None, 'Scan final position'],
       ['nr_interv',  Type.Integer, None, 'Number of scan intervals'],
       ['integ_time', Type.Float,   None, 'Integration time'],
       ['repeat',     Type.Integer, None, 'Number of Repetitions']
    ]


    def prepare(self, motor, start_pos, final_pos, nr_interv, integ_time, repeat,
                **opts):
        
        self.starts = numpy.array([start_pos], dtype='d')
        self.finals = numpy.array([final_pos], dtype='d')
        self.nr_interv = nr_interv
        self.integ_time = integ_time
        self.repeat=repeat
        self.opts = opts

        self.nr_points = nr_interv+1
        self.interv_sizes = ( self.finals - self.starts) / nr_interv
        self.name='ascanr'
        
        generator=self._generator
        moveables=[motor]
        env=opts.get('env',{})
        constrains=[]
        extrainfodesc=[ColumnDesc(label='repetition', dtype='int64', shape=(1,))] #!!!
                
        self._gScan=SScan(self, generator, moveables, env, constrains, extrainfodesc) #!!!
  

    def _generator(self):
        step = {}
        step["integ_time"] =  self.integ_time
        step["post-acq-hooks"] = self.getHooks('post-acq') +  self.getHooks('_NOHINT_')
        step["post-step-hooks"] = self.getHooks('post-step')
        step["check_func"] = []
        extrainfo = {"repetition":0} #!!! 
        step['extrainfo'] = extrainfo  #!!! 
        for point_no in xrange(self.nr_points):
            step["positions"] = self.starts + point_no * self.interv_sizes
            step["point_id"] = point_no
            for i in xrange(self.repeat):
                extrainfo["repetition"] = i #!!! 
                yield step
    
    def run(self,*args):
        for step in self._gScan.step_scan():
            yield step
        
    @property
    def data(self):
        return self._gScan.data
        

class ToothedTriangle(Macro):
    """ToothedTriangle macro implemented with the gscan framework.
    It performs nr_cycles cycles, each consisting of two stages: the first half
    of the cycle it behaves like the ascan macro (from start_pos to stop_pos in
    nr_interv+1 steps).For the second half of the cycle it steps back until
    it undoes the first half and is ready for the next cycle.
    At each step, nr_samples acquisitions are performed.
    The total number of points in the scan is nr_interv*2*nr_cycles*nr_samples+1"""

    hints = { 'scan' : 'ToothedTriangle', 'allowsHooks':('pre-move', 'post-move', 'pre-acq', 'post-acq') }
    env = ('ActiveMntGrp',)

    param_def = [
       ['motor',      Type.Motor,   None, 'Motor to move'],
       ['start_pos',  Type.Float,   None, 'start position'],
       ['final_pos',  Type.Float,   None, 'position after half cycle'],
       ['nr_interv',  Type.Integer, None, 'Number of intervals in half cycle'],
       ['integ_time', Type.Float,   None, 'Integration time'],
       ['nr_cycles',  Type.Integer, None, 'Number of cycles'],
       ['nr_samples', Type.Integer, 1 , 'Number of samples at each point']
    ]

    def prepare(self, motor, start_pos, final_pos, nr_interv, integ_time,
                nr_cycles, nr_samples, **opts):
        
        self.start_pos = start_pos
        self.final_pos = final_pos
        self.nr_interv = nr_interv
        self.integ_time = integ_time
        self.nr_cycles = nr_cycles
        self.nr_samples = nr_samples
        self.opts = opts
        cycle_nr_points = self.nr_interv+1 + (self.nr_interv+1)-2
        self.nr_points = cycle_nr_points*nr_samples*nr_cycles+nr_samples
        
        self.interv_size = ( self.final_pos - self.start_pos) / nr_interv
        self.name='ToothedTriangle'
        
        generator=self._generator
        moveables=[motor]
        env=opts.get('env',{})
        constrains=[]
        extrainfodesc=[ColumnDesc(label='cycle', dtype='int64', shape=(1,)),
                       ColumnDesc(label='interval', dtype='int64', shape=(1,)),
                       ColumnDesc(label='sample', dtype='int64', shape=(1,))] #!!!
                
        self._gScan=SScan(self, generator, moveables, env, constrains, extrainfodesc) #!!!
  

    def _generator(self):
        step = {}
        step["integ_time"] =  self.integ_time
        step["post-acq-hooks"] = []
        step["post-step-hooks"] = []
        step["check_func"] = []
        extrainfo = {"cycle":None, "interval":None, "sample":None, } 
        step['extrainfo'] = extrainfo
        halfcycle1=range(self.nr_interv+1)
        halfcycle2=halfcycle1[1:-1]
        halfcycle2.reverse()
        intervallist=halfcycle1+halfcycle2
        point_no=0
        for cycle in xrange(self.nr_cycles):
            extrainfo["cycle"] = cycle
            for interval in intervallist:
                extrainfo["interval"] = interval
                step["positions"] = numpy.array([self.start_pos + (interval) * self.interv_size] ,dtype='d')
                for sample in xrange(self.nr_samples):
                    extrainfo["sample"] = sample
                    step["point_id"] = point_no 
                    yield step
                    point_no+=1
                    
        #last step for closing the loop
        extrainfo["interval"] = 0
        step["positions"] = numpy.array([self.start_pos] ,dtype='d')
        for sample in xrange(self.nr_samples):
            extrainfo["sample"] = sample
            step["point_id"] = point_no 
            yield step
            point_no+=1
    
    def run(self,*args):
        for step in self._gScan.step_scan():
            yield step
    
    @property
    def data(self):
        return self._gScan.data

class ascanc(Macro, Hookable):
    
    hints = { 'scan' : 'ascanc', 'allowsHooks':('pre-move', 'post-move', 'pre-acq', 'post-acq', 'post-step') }
    env = ('ActiveMntGrp',)
    
    """Simplest example of continuous scan: a continuous ascan giving a compact table"""

    param_def = [
       ['motor',      Type.Motor,   None, 'Motor to move'],
       ['start_pos',  Type.Float,   None, 'Scan start position'],
       ['final_pos',  Type.Float,   None, 'Scan final position'],
       ['acq_period', Type.Float,   None, 'Period between acquisitions']
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
        

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
    Macro library containning examples demonstrating specific features or tricks
    for programming macros for Sardana.
   
   Available Macros are:
     ascanr
     toothedtriangle
     
"""

__all__ = ["ascan_demo", "ascanr", "toothedtriangle", "regscan", "reg2scan", "reg3scan", "a2scan_mod"]

__docformat__ = 'restructuredtext'

import os
import numpy

from sardana.macroserver.macro import *
from sardana.macroserver.scan import *

class ascan_demo(Macro):
    """
    This is a basic reimplementation of the ascan` macro for demonstration
    purposes of the Generic Scan framework. The "real" implementation of
    :class:`sardana.macroserver.macros.ascan` derives from
    :class:`sardana.macroserver.macros.aNscan` and provides some extra features.
    """

    hints = { 'scan' : 'ascan_demo'} #this is used to indicate other codes that the macro is a scan
    env = ('ActiveMntGrp',) #this hints that the macro requires the ActiveMntGrp environment variable to be set

    param_def = [
       ['motor',      Type.Moveable, None, 'Motor to move'],
       ['start_pos',  Type.Float,    None, 'Scan start position'],
       ['final_pos',  Type.Float,    None, 'Scan final position'],
       ['nr_interv',  Type.Integer,  None, 'Number of scan intervals'],
       ['integ_time', Type.Float,    None, 'Integration time']
    ]

    def prepare(self, motor, start_pos, final_pos, nr_interv, integ_time, **opts):
        #parse the user parameters
        self.start = numpy.array([start_pos], dtype='d')
        self.final = numpy.array([final_pos], dtype='d')
        self.integ_time = integ_time

        self.nr_points = nr_interv+1
        self.interv_size = ( self.final - self.start) / nr_interv
        self.name='ascan_demo'
        env = opts.get('env',{}) #the "env" dictionary may be passed as an option
        
        #create an instance of GScan (in this case, of its child, SScan
        self._gScan=SScan(self, generator=self._generator, moveables=[motor], env=env) 
  

    def _generator(self):
        step = {}
        step["integ_time"] =  self.integ_time #integ_time is the same for all steps
        for point_no in xrange(self.nr_points):
            step["positions"] = self.start + point_no * self.interv_size #note that this is a numpy array
            step["point_id"] = point_no
            yield step
    
    def run(self,*args):
        for step in self._gScan.step_scan(): #just go through the steps
            yield step
        
    @property
    def data(self):
        return self._gScan.data #the GScan provides scan data


class ascanr(Macro, Hookable):
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

    hints = { 'scan' : 'ascanr', 'allowsHooks':('pre-move', 'post-move', 'pre-acq', 'post-acq', 'post-step') }
    env = ('ActiveMntGrp',)

    param_def = [
       ['motor',      Type.Moveable, None, 'Motor to move'],
       ['start_pos',  Type.Float,    None, 'Scan start position'],
       ['final_pos',  Type.Float,    None, 'Scan final position'],
       ['nr_interv',  Type.Integer,  None, 'Number of scan intervals'],
       ['integ_time', Type.Float,    None, 'Integration time'],
       ['repeat',     Type.Integer,  None, 'Number of Repetitions']
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
        extrainfodesc=[ColumnDesc(name='repetition',
                                  dtype='int64', shape=(1,))] #!!!
                
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
        

class toothedtriangle(Macro, Hookable):
    """toothedtriangle macro implemented with the gscan framework.
    It performs nr_cycles cycles, each consisting of two stages: the first half
    of the cycle it behaves like the ascan macro (from start_pos to stop_pos in
    nr_interv+1 steps).For the second half of the cycle it steps back until
    it undoes the first half and is ready for the next cycle.
    At each step, nr_samples acquisitions are performed.
    The total number of points in the scan is nr_interv*2*nr_cycles*nr_samples+1"""

    hints = { 'scan' : 'toothedtriangle',
             'allowsHooks':('pre-scan', 'pre-move', 'post-move', 'pre-acq',
                            'post-acq', 'post-step', 'post-scan')
             }
    env = ('ActiveMntGrp',)

    param_def = [
       ['motor',      Type.Moveable, None, 'Motor to move'],
       ['start_pos',  Type.Float,    None, 'start position'],
       ['final_pos',  Type.Float,    None, 'position after half cycle'],
       ['nr_interv',  Type.Integer,  None, 'Number of intervals in half cycle'],
       ['integ_time', Type.Float,    None, 'Integration time'],
       ['nr_cycles',  Type.Integer,  None, 'Number of cycles'],
       ['nr_samples', Type.Integer,  1 , 'Number of samples at each point']
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
        self.name='toothedtriangle'
        
        generator=self._generator
        moveables = []
        moveable = MoveableDesc(moveable=motor, is_reference=True,
                                min_value=min(start_pos,final_pos),
                                max_value=max(start_pos,final_pos))
        moveables=[moveable]
        env=opts.get('env',{})
        constrains=[]
        extrainfodesc=[ColumnDesc(name='cycle', dtype='int64', shape=(1,)),
                       ColumnDesc(name='interval', dtype='int64', shape=(1,)),
                       ColumnDesc(name='sample', dtype='int64', shape=(1,))] #!!!
                
        self._gScan=SScan(self, generator, moveables, env, constrains, extrainfodesc) #!!!
  

    def _generator(self):
        step = {}
        step["integ_time"] =  self.integ_time
        step["pre-move-hooks"] = self.getHooks('pre-move')
        step["post-move-hooks"] = self.getHooks('post-move')
        step["pre-acq-hooks"] = self.getHooks('pre-acq')
        step["post-acq-hooks"] = self.getHooks('post-acq') + self.getHooks('_NOHINT_')
        step["post-step-hooks"] = self.getHooks('post-step')
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


class regscan(Macro):
    """regscan.
    Do an absolute scan of the specified motor with different number of intervals for each region.
    It uses the gscan framework.

    NOTE: Due to a ParamRepeat limitation, integration time has to be
    specified before the regions.
    """

    hints = {'scan' : 'regscan'}
    env = ('ActiveMntGrp',)

    param_def = [
        ['motor',      Type.Moveable, None, 'Motor to move'],
        ['integ_time', Type.Float,    None, 'Integration time'],
        ['start_pos',  Type.Float,    None, 'Start position'],
        ['step_region',
         ParamRepeat(['next_pos',  Type.Float,   None, 'next position'],
                     ['region_nr_intervals',  Type.Float,   None, 'Region number of intervals']),
         None, 'List of tuples: (next_pos, region_nr_intervals']
    ]

    def prepare(self, motor, integ_time, start_pos, *regions, **opts):
        self.name='regscan'
        self.integ_time = integ_time
        self.start_pos = start_pos
        self.regions = regions
        self.regions_count = len(self.regions)/2
        
        generator=self._generator
        moveables=[motor]
        env=opts.get('env',{})
        constrains=[]
        self._gScan=SScan(self, generator, moveables, env, constrains)

    def _generator(self):
        step = {}
        step["integ_time"] =  self.integ_time
        
        point_id = 0
        region_start = self.start_pos
        for r in range(len(self.regions)):
            region_stop, region_nr_intervals = self.regions[r][0], self.regions[r][1]
            positions = numpy.linspace(region_start, region_stop, region_nr_intervals+1)
            if region_start != self.start_pos:
                # positions must be calculated from the start to the end of the region
                # but after the first region, the 'start' point must not be repeated
                positions = positions[1:]
            for p in positions:
                step['positions'] = [p]
                step['point_id'] = point_id
                point_id += 1
                yield step
            region_start = region_stop

    def run(self,*args):
        for step in self._gScan.step_scan():
            yield step


class reg2scan(Macro):
    """reg2scan.
    Do an absolute scan of the specified motors with different number of intervals for each region.
    It uses the gscan framework. All the motors will be drived to the same position in each step

    NOTE: Due to a ParamRepeat limitation, integration time has to be
    specified before the regions.
    """

    hints = {'scan' : 'reg2scan'}
    env = ('ActiveMntGrp',)

    param_def = [
        ['motor1',     Type.Moveable, None, 'Motor to move'],
        ['motor2',     Type.Moveable, None, 'Motor to move'],
        ['integ_time', Type.Float,    None, 'Integration time'],
        ['start_pos',  Type.Float,    None, 'Start position'],
        ['step_region',
         ParamRepeat(['next_pos',  Type.Float,   None, 'next position'],
                     ['region_nr_intervals',  Type.Float,   None, 'Region number of intervals']),
         None, 'List of tuples: (next_pos, region_nr_intervals']
    ]

    def prepare(self, motor1, motor2, integ_time, start_pos, *regions, **opts):
        self.name='reg2scan'
        self.integ_time = integ_time
        self.start_pos = start_pos
        self.regions = regions
        self.regions_count = len(self.regions)/2

        generator=self._generator
        moveables=[motor1, motor2]
        env=opts.get('env',{})
        constrains=[]
        self._gScan=SScan(self, generator, moveables, env, constrains)

    def _generator(self):
        step = {}
        step["integ_time"] =  self.integ_time

        point_id = 0
        region_start = self.start_pos
        for r in range(len(self.regions)):
            region_stop, region_nr_intervals = self.regions[r][0], self.regions[r][1]
            positions = numpy.linspace(region_start, region_stop, region_nr_intervals+1)
            if region_start != self.start_pos:
                # positions must be calculated from the start to the end of the region
                # but after the first region, the 'start' point must not be repeated
                positions = positions[1:]
            for p in positions:
                step['positions'] = [p, p]
                step['point_id'] = point_id
                point_id += 1
                yield step
            region_start = region_stop

    def run(self,*args):
        for step in self._gScan.step_scan():
            yield step


class reg3scan(Macro):
    """reg3scan.
    Do an absolute scan of the specified motors with different number of intervals for each region.
    It uses the gscan framework. All the motors will be drived to the same position in each step

    NOTE: Due to a ParamRepeat limitation, integration time has to be
    specified before the regions.
    """

    hints = {'scan' : 'reg3scan'}
    env = ('ActiveMntGrp',)

    param_def = [
        ['motor1',     Type.Moveable, None, 'Motor to move'],
        ['motor2',     Type.Moveable, None, 'Motor to move'],
        ['motor3',     Type.Moveable, None, 'Motor to move'],
        ['integ_time', Type.Float,    None, 'Integration time'],
        ['start_pos',  Type.Float,    None, 'Start position'],
        ['step_region',
         ParamRepeat(['next_pos',  Type.Float,   None, 'next position'],
                     ['region_nr_intervals',  Type.Float,   None, 'Region number of intervals']),
         None, 'List of tuples: (next_pos, region_nr_intervals']
    ]

    def prepare(self, motor1, motor2, motor3, integ_time, start_pos, *regions, **opts):
        self.name='reg3scan'
        self.integ_time = integ_time
        self.start_pos = start_pos
        self.regions = regions
        self.regions_count = len(self.regions)/2

        generator=self._generator
        moveables=[motor1, motor2, motor3]
        env=opts.get('env',{})
        constrains=[]
        self._gScan=SScan(self, generator, moveables, env, constrains)

    def _generator(self):
        step = {}
        step["integ_time"] =  self.integ_time

        point_id = 0
        region_start = self.start_pos
        for r in range(len(self.regions)):
            region_stop, region_nr_intervals = self.regions[r][0], self.regions[r][1]
            positions = numpy.linspace(region_start, region_stop, region_nr_intervals+1)
            if region_start != self.start_pos:
                # positions must be calculated from the start to the end of the region
                # but after the first region, the 'start' point must not be repeated
                positions = positions[1:]
            for p in positions:
                step['positions'] = [p, p, p]
                step['point_id'] = point_id
                point_id += 1
                yield step
            region_start = region_stop

    def run(self,*args):
        for step in self._gScan.step_scan():
            yield step


class a2scan_mod(Macro):
    """a2scan_mod.
    Do an a2scan with the particularity of different intervals per motor: int_mot1, int_mot2.
    If int_mot2 < int_mot1, mot2 will change position every int(int_mot1/int_mot2) steps of mot1.
    It uses the gscan framework.
    """

    hints = {'scan' : 'a2scan_mod'}
    env = ('ActiveMntGrp',)

    param_def = [
       ['motor1',      Type.Moveable, None, 'Motor 1 to move'],
       ['start_pos1',  Type.Float,    None, 'Scan start position 1'],
       ['final_pos1',  Type.Float,    None, 'Scan final position 1'],
       ['nr_interv1',  Type.Integer,  None, 'Number of scan intervals of Motor 1'],
       ['motor2',      Type.Moveable, None, 'Motor 2 to move'],
       ['start_pos2',  Type.Float,    None, 'Scan start position 2'],
       ['final_pos2',  Type.Float,    None, 'Scan final position 2'],
       ['nr_interv2',  Type.Integer,  None, 'Number of scan intervals of Motor 2'],
       ['integ_time',  Type.Float,    None, 'Integration time']
    ]
    
    def prepare(self, motor1, start_pos1, final_pos1, nr_interv1, motor2, start_pos2, final_pos2, nr_interv2, integ_time,
                **opts):
        self.name='a2scan_mod'
        self.integ_time = integ_time
        self.start_pos1 = start_pos1
        self.final_pos1 = final_pos1
        self.nr_interv1 = nr_interv1
        self.start_pos2 = start_pos2
        self.final_pos2 = final_pos2
        self.nr_interv2 = nr_interv2
        
        generator = self._generator
        moveables = [motor1, motor2]
        env = opts.get('env',{})
        constraints = []
        self._gScan=SScan(self, generator, moveables, env, constraints)

    def _generator(self):
        step = {}
        step["integ_time"] =  self.integ_time

        start1, end1, interv1 = self.start_pos1, self.final_pos1, self.nr_interv1
        start2, end2, interv2 = self.start_pos2, self.final_pos2, self.nr_interv2
        
        # Prepare the positions
        positions_m1 = numpy.linspace(start1, end1, interv1+1)
        positions_m2 = numpy.linspace(start2, end2, interv2+1)

        if interv1 > interv2:
            positions_m2 = start2+(float(end2-start2)/interv2)*(numpy.arange(interv1+1)//(float(interv1)/float(interv2)))
        elif interv2 > interv1:
            positions_m1 = start1+(float(end1-start1)/interv1)*(numpy.arange(interv2+1)//(float(interv2)/float(interv1)))

        point_id = 0
        for pos1,pos2 in zip(positions_m1,positions_m2):
            step['point_id'] = point_id
            step['positions'] = [pos1, pos2]
            yield step
            point_id += 1
 
    def run(self,*args):
        for step in self._gScan.step_scan():
            yield step


class ascanc_demo(Macro):
    """
    This is a basic reimplementation of the ascanc` macro for demonstration
    purposes of the Generic Scan framework. The "real" implementation of
    :class:`sardana.macroserver.macros.ascanc` derives from
    :class:`sardana.macroserver.macros.aNscan` and provides some extra features.
    """

    hints = { 'scan' : 'ascanc_demo'} #this is used to indicate other codes that the macro is a scan
    env = ('ActiveMntGrp',) #this hints that the macro requires the ActiveMntGrp environment variable to be set

    param_def = [
       ['motor',      Type.Moveable, None, 'Motor to move'],
       ['start_pos',  Type.Float,    None, 'Scan start position'],
       ['final_pos',  Type.Float,    None, 'Scan final position'],
       ['integ_time', Type.Float,    None, 'Integration time']
    ]

    def prepare(self, motor, start_pos, final_pos, integ_time, **opts):
        self.name='ascanc_demo'
        #parse the user parameters
        self.start = numpy.array([start_pos], dtype='d')
        self.final = numpy.array([final_pos], dtype='d')
        self.integ_time = integ_time
        env = opts.get('env',{}) #the "env" dictionary may be passed as an option
        
        #create an instance of GScan (in this case, of its child, CScan
        self._gScan = CScan(self, 
                            waypointGenerator=self._waypoint_generator, 
                            periodGenerator=self._period_generator, 
                            moveables=[motor], 
                            env=env)
        
    def _waypoint_generator(self):
        #a very simple waypoint generator! only start and stop points!
        yield {"positions":self.start, "waypoint_id": 0}
        yield {"positions":self.final, "waypoint_id": 1}
        

    def _period_generator(self):
        step = {}
        step["integ_time"] =  self.integ_time
        point_no = 0
        while(True): #infinite generator. The acquisition loop is started/stopped at begin and end of each waypoint 
            point_no += 1
            step["point_id"] = point_no
            yield step
    
    def run(self,*args):
        for step in self._gScan.step_scan():
            yield step



class ascan_with_addcustomdata(ascan_demo):
    '''
    example of an ascan-like macro where we demonstrate how to pass custom data to the data handler.
    This is an extension of the ascan_demo macro. Wemake several calls to `:meth:DataHandler.addCustomData`
    exemplifying different features.
    At least the following recorders will act on custom data: 
      - OutputRecorder (this will ignore array data)
      - NXscan_FileRecorder
      - SPEC_FileRecorder (this will ignore array data)
    '''
    def run(self, motor, start_pos, final_pos, nr_interv, integ_time, **opts):
        #we get the datahandler
        dh = self._gScan._data_handler
        #at this point the entry name is not yet set, so we give it explicitly (otherwise it would default to "entry")
        dh.addCustomData('Hello world1', 'dummyChar1', nxpath='/custom_entry:NXentry/customdata:NXcollection')
        #this is the normal scan loop
        for step in self._gScan.step_scan():
            yield step
        #the entry number is known and the default nxpath is used "/<currententry>/custom_data") if none given
        dh.addCustomData('Hello world1', 'dummyChar1')
        #you can pass arrays (but not all recorders will handle them) 
        dh.addCustomData(range(10), 'dummyArray1') 
        #you can pass a custom nxpath *relative* to the current entry
        dh.addCustomData('Hello world2', 'dummyChar2', nxpath='sample:NXsample') 
        
        #calculate a linear fit to the timestamps VS motor positions and store it 
        x = [r.data [motor.getName()] for r in self.data.records]
        y = [r.data['timestamp'] for r in self.data.records]
        fitted_y = numpy.polyval(numpy.polyfit(x,y,1), x)
        dh.addCustomData(fitted_y, 'fittedtime', nxpath='measurement:NXcollection')
        
        #as a bonus, plot the fit
        self.pyplot.plot(x, y, 'ro')
        self.pyplot.plot(x, fitted_y, 'b-')

    
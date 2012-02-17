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
     ascan family: ascan, a2scan, a3scan, a4scan and amultiscan
     dscan family: dscan, d2scan, d3scan, d4scan and dmultiscan
     mesh
     fscan
     scanhist
"""

__docformat__ = 'restructuredtext'

__all__ = ["a2scan", "a3scan", "a4scan", "amultiscan", "aNscan", "ascan",
           "d2scan", "d3scan", "d4scan", "dmultiscan", "dNScan", "dscan",
           "fscan", "mesh", "scanhist", "getCallable", "UNCONSTRAINED"]

import os
import copy
import datetime

import numpy

from taurus.console import Alignment
from taurus.console.list import List
from taurus.console.table import Table

from sardana.macroserver.msexception import UnknownEnv
from sardana.macroserver.macro import *
from sardana.macroserver.scan import *

UNCONSTRAINED="unconstrained"

def getCallable(repr):
    '''returns a function .
    Ideas: repr could be an URL for a file where the function is contained,
    or be evaluable code, or a pickled function object,...
    
    In any case, the return from it should be a callable of the form:
    f(x1,x2) where x1, x2 are points in the moveable space and the return value
    of f is True if the movement from x1 to x2 is allowed. False otherwise'''
    if repr==UNCONSTRAINED:
        return lambda x1,x2:True
    else:
        return lambda: None

class aNscan(Hookable):
    
    hints = { 'scan' : 'aNscan', 'allowsHooks': ('pre-scan', 'pre-move', 'post-move', 'pre-acq', 'post-acq', 'post-step', 'post-scan') }
    #env = ('ActiveMntGrp',)
    
    """N-dimensional scan. This is **not** meant to be called by the user,
    but as a generic base to construct ascan, a2scan, a3scan,..."""
    def _prepare(self, motorlist, startlist, endlist, nr_interv, integ_time, **opts):
        if nr_interv > 0:
            prepare = self._prepare_stepMode
        elif nr_interv == -1:
            prepare = self._prepare_continuousMode
        elif nr_interv == -2:
            raise NotImplementedError('The sparse-output mode for continuous scans is not yet implemented') #@TODO
        else:
            raise ValueError('invalid value for nr_interv = %i'%nr_interv)
        
        prepare(motorlist, startlist, endlist, nr_interv, integ_time, **opts)
        
    def _prepare_stepMode(self, motorlist, startlist, endlist, nr_interv, integ_time, **opts):
        self.motors = motorlist
        self.starts = numpy.array(startlist,dtype='d')
        self.finals = numpy.array(endlist,dtype='d')
        self.nr_interv = nr_interv
        self.integ_time = integ_time
        self.opts = opts
        if len(self.motors) == self.starts.size == self.finals.size:
            self.N = self.finals.size
        else:
            raise ValueError('Moveablelist, startlist and endlist must all be same length')
        
        self.nr_points = nr_interv+1
        self.interv_sizes = ( self.finals - self.starts) / nr_interv
        
        self.name = opts.get('name','a%iscan'%self.N)
        
        moveables = []
        for m, start, final in zip(self.motors, self.starts, self.finals):
            moveables.append(MoveableDesc(moveable=m, min_value=min(start,final), max_value=max(start,final)))
        moveables[0].is_reference = True
        
        env = opts.get('env',{})
        constrains = [getCallable(cns) for cns in opts.get('constrains',[UNCONSTRAINED])]
        extrainfodesc = opts.get('extrainfodesc',[])

        self.pre_scan_hooks = self.getHooks('pre-scan')
        self.post_scan_hooks = self.getHooks('post-scan')
        
        self._gScan = SScan(self, self._stepGenerator, moveables, env, constrains, extrainfodesc)
    
    def _prepare_continuousMode(self, motorlist, startlist, endlist, mode, acq_period, **opts):
        self.motors = motorlist
        self.starts = numpy.array(startlist,dtype='d')
        self.finals = numpy.array(endlist,dtype='d')
        self.mode = mode
        self.acq_period = acq_period
        self.opts = opts
        if len(self.motors) == self.starts.size == self.finals.size:
            self.N = self.finals.size
        else:
            raise ValueError('Moveablelist, startlist and endlist must all be same length')
        
        self.nr_waypoints = 2 #aNscans will only have two waypoints (the start and the final positions)
        self.way_lengths = ( self.finals - self.starts) / (self.nr_waypoints -1)
                
        self.name = opts.get('name','a%iscan'%self.N)
        
        moveables = []
        for m, start, final in zip(self.motors, self.starts, self.finals):
            moveables.append(MoveableDesc(moveable=m, min_value=start, max_value=final))
        env = opts.get('env',{})
        constrains = [getCallable(cns) for cns in opts.get('constrains',[UNCONSTRAINED])]
        extrainfodesc = opts.get('extrainfodesc',[])
        
        self.pre_scan_hooks = self.getHooks('pre-scan')
        self.post_scan_hooks = self.getHooks('post-scan')

        self._gScan = CScan(self, self._waypoint_generator, self._period_generator, moveables, env, constrains, extrainfodesc)
        
    def _stepGenerator(self):
        step = {}
        step["integ_time"] =  self.integ_time
        step["pre-move-hooks"] = self.getHooks('pre-move')
        step["post-move-hooks"] = self.getHooks('post-move')
        step["pre-acq-hooks"] = self.getHooks('pre-acq')
        step["post-acq-hooks"] = self.getHooks('post-acq') + self.getHooks('_NOHINTS_')
        step["post-step-hooks"] = self.getHooks('post-step')
        
        step["check_func"] = []
        for point_no in xrange(self.nr_points):
            step["positions"] = self.starts + point_no * self.interv_sizes
            step["point_id"] = point_no
            yield step
    
    def _waypoint_generator(self):
        step = {}
        step["pre-move-hooks"] = self.getHooks('pre-move')
        step["post-move-hooks"] = self.getHooks('post-move')
        step["check_func"] = []
        for point_no in xrange(self.nr_waypoints):
            step["positions"] = self.starts + point_no * self.way_lengths
            step["waypoint_id"] = point_no
            yield step
    
    def _period_generator(self):
        step = {}
        step["acq_period"] =  self.acq_period
        step["pre-acq-hooks"] = self.getHooks('pre-acq')
        step["post-acq-hooks"] = self.getHooks('post-acq')+self.getHooks('_NOHINTS_')
        step["post-step-hooks"] = self.getHooks('post-step')
        step["check_func"] = []
        step['extrainfo'] = {}
        point_no = 0
        while(True):
            point_no += 1
            step["point_id"] = point_no
            yield step
    
    def run(self,*args):
        for step in self._gScan.step_scan():
            yield step
    
    @property
    def data(self):
        return self._gScan.data

class dNscan(aNscan):
    '''same as aNscan but it interprets the positions as being relative to the
    current positions and upon completion, it returns the motors to their
    original positions'''

    hints = copy.deepcopy(aNscan.hints)
    hints['scan'] = 'dNscan'

    def _prepare(self, motorlist, startlist, endlist, nr_interv, integ_time, **opts):
        self._motion=self.getMotion( [ m.getName() for m in motorlist] )
        self.originalPositions = numpy.array(self._motion.readPosition())
        starts = numpy.array(startlist, dtype='d') + self.originalPositions
        finals = numpy.array(endlist, dtype='d') + self.originalPositions
        aNscan._prepare(self, motorlist, starts, finals, nr_interv, integ_time, **opts)
        
    def run(self, *args):
        for step in self._gScan.step_scan():
            yield step
        self._motion.move(self.originalPositions)
        
class ascan(aNscan, Macro): 
    """Do an absolute scan of the specified motor.
    ascan scans one motor, as specified by motor. The motor starts at the
    position given by start_pos and ends at the position given by final_pos.
    The step size is (start_pos-final_pos)/nr_interv. The number of data points collected
    will be nr_interv+1. Count time is given by time which if positive,
    specifies seconds and if negative, specifies monitor counts. """

    param_def = [
       ['motor',      Type.Moveable,   None, 'Moveable to move'],
       ['start_pos',  Type.Float,   None, 'Scan start position'],
       ['final_pos',  Type.Float,   None, 'Scan final position'],
       ['nr_interv',  Type.Integer, None, 'Number of scan intervals'],
       ['integ_time', Type.Float,   None, 'Integration time']
    ]

    def prepare(self, motor, start_pos, final_pos, nr_interv, integ_time,
                **opts):
        self._prepare([motor], [start_pos], [final_pos], nr_interv, integ_time, **opts)
       

class a2scan(aNscan, Macro): 
    """two-motor scan.
    a2scan scans two motors, as specified by motor1 and motor2.
    Each motor moves the same number of intervals with starting and ending
    positions given by start_pos1 and final_pos1, start_pos2 and final_pos2,
    respectively. The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts."""
    param_def = [
       ['motor1',      Type.Moveable,   None, 'Moveable 1 to move'],
       ['start_pos1',  Type.Float,   None, 'Scan start position 1'],
       ['final_pos1',  Type.Float,   None, 'Scan final position 1'],
       ['motor2',      Type.Moveable,   None, 'Moveable 2 to move'],
       ['start_pos2',  Type.Float,   None, 'Scan start position 2'],
       ['final_pos2',  Type.Float,   None, 'Scan final position 2'],
       ['nr_interv',  Type.Integer, None, 'Number of scan intervals'],
       ['integ_time', Type.Float,   None, 'Integration time']
    ]

    def prepare(self, motor1, start_pos1, final_pos1, motor2, start_pos2, final_pos2, nr_interv, integ_time,
                **opts):
        self._prepare([motor1,motor2], [start_pos1,start_pos2], [final_pos1,final_pos2], nr_interv, integ_time, **opts)


class a3scan(aNscan, Macro): 
    """three-motor scan .
    a3scan scans three motors, as specified by motor1, motor2 and motor3.
    Each motor moves the same number of intervals with starting and ending
    positions given by start_pos1 and final_pos1, start_pos2 and final_pos2,
    start_pos3 and final_pos3, respectively.
    The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts."""
    param_def = [
       ['motor1',      Type.Moveable,   None, 'Moveable 1 to move'],
       ['start_pos1',  Type.Float,   None, 'Scan start position 1'],
       ['final_pos1',  Type.Float,   None, 'Scan final position 1'],
       ['motor2',      Type.Moveable,   None, 'Moveable 2 to move'],
       ['start_pos2',  Type.Float,   None, 'Scan start position 2'],
       ['final_pos2',  Type.Float,   None, 'Scan final position 2'],
       ['motor3',      Type.Moveable,   None, 'Moveable 3 to move'],
       ['start_pos3',  Type.Float,   None, 'Scan start position 3'],
       ['final_pos3',  Type.Float,   None, 'Scan final position 3'],
       ['nr_interv',  Type.Integer, None, 'Number of scan intervals'],
       ['integ_time', Type.Float,   None, 'Integration time']
    ]

    def prepare(self, m1, s1, f1,  m2, s2, f2, m3, s3, f3, nr_interv, integ_time,
                **opts):
        self._prepare([m1,m2,m3], [s1,s2,s3], [f1,f2,f3], nr_interv, integ_time, **opts)

class a4scan(aNscan, Macro): 
    """four-motor scan .
    a4scan scans four motors, as specified by motor1, motor2, motor3 and motor4.
    Each motor moves the same number of intervals with starting and ending
    positions given by start_posN and final_posN (for N=1,2,3,4).
    The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts."""
    param_def = [
       ['motor1',      Type.Moveable,   None, 'Moveable 1 to move'],
       ['start_pos1',  Type.Float,   None, 'Scan start position 1'],
       ['final_pos1',  Type.Float,   None, 'Scan final position 1'],
       ['motor2',      Type.Moveable,   None, 'Moveable 2 to move'],
       ['start_pos2',  Type.Float,   None, 'Scan start position 2'],
       ['final_pos2',  Type.Float,   None, 'Scan final position 2'],
       ['motor3',      Type.Moveable,   None, 'Moveable 3 to move'],
       ['start_pos3',  Type.Float,   None, 'Scan start position 3'],
       ['final_pos3',  Type.Float,   None, 'Scan final position 3'],
       ['motor4',      Type.Moveable,   None, 'Moveable 3 to move'],
       ['start_pos4',  Type.Float,   None, 'Scan start position 3'],
       ['final_pos4',  Type.Float,   None, 'Scan final position 3'],
       ['nr_interv',  Type.Integer, None, 'Number of scan intervals'],
       ['integ_time', Type.Float,   None, 'Integration time']
    ]

    def prepare(self, m1, s1, f1, m2, s2, f2, m3, s3, f3, m4, s4, f4, nr_interv,
                integ_time, **opts):
        self._prepare([m1,m2,m3,m4], [s1,s2,s3,m4], [f1,f2,f3,f4], nr_interv, integ_time, **opts)

class amultiscan(aNscan, Macro): 
    '''Multiple motor scan.
    amultiscan scans N motors, as specified by motor1, motor2,...,motorN.
    Each motor moves the same number of intervals with starting and ending
    positions given by start_posN and final_posN (for N=1,2,...).
    The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts."""
    '''

    param_def = [
       ['motor_start_end_list',
        ParamRepeat(['motor', Type.Moveable, None, 'Moveable to move'],
                    ['start',   Type.Float, None, 'Starting position'],
                    ['end',   Type.Float, None, 'Final position']),
        None, 'List of motor, start and end positions'],
       ['nr_interv',  Type.Integer, None, 'Number of scan intervals'],
       ['integ_time', Type.Float,   None, 'Integration time']
    ]
    
    def prepare(self, *args, **opts):
        motors = args[0:-2:3]
        starts = args[1:-2:3]
        ends   = args[2:-2:3]
        nr_interv = args[-2]
        integ_time = args[-1]
        
        self._prepare(motors, starts, ends, nr_interv, integ_time, **opts)

class dmultiscan(dNscan, Macro): 
    '''Multiple motor scan relative to the starting positions.
    dmultiscan scans N motors, as specified by motor1, motor2,...,motorN.
    Each motor moves the same number of intervals If each motor is at a
    position X before the scan begins, it will be scanned from X+start_posN
    to X+final_posN (where N is one of 1,2,...)
    The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts."""
    '''
    param_def = [
       ['motor_start_end_list',
        ParamRepeat(['motor', Type.Moveable, None, 'Moveable to move'],
                    ['start',   Type.Float, None, 'Starting position'],
                    ['end',   Type.Float, None, 'Final position']),
        None, 'List of motor, start and end positions'],
       ['nr_interv',  Type.Integer, None, 'Number of scan intervals'],
       ['integ_time', Type.Float,   None, 'Integration time']
    ]
    
    def prepare(self, *args, **opts):
        motors = args[0:-2:3]
        starts = args[1:-2:3]
        ends   = args[2:-2:3]
        nr_interv = args[-2]
        integ_time = args[-1]
        
        self._prepare(motors, starts, ends, nr_interv, integ_time, **opts)


class dscan(dNscan, Macro): 
    """motor scan relative to the starting position.
    dscan scans one motor, as specified by motor. If motor motor is at a
    position X before the scan begins, it will be scanned from X+start_pos
    to X+final_pos. The step size is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1. Count time is
    given by time which if positive, specifies seconds and if negative,
    specifies monitor counts. """

    param_def = [
       ['motor',      Type.Moveable,   None, 'Moveable to move'],
       ['start_pos',  Type.Float,   None, 'Scan start position'],
       ['final_pos',  Type.Float,   None, 'Scan final position'],
       ['nr_interv',  Type.Integer, None, 'Number of scan intervals'],
       ['integ_time', Type.Float,   None, 'Integration time']
    ]

    def prepare(self, motor, start_pos, final_pos, nr_interv, integ_time,
                **opts):
        self._prepare([motor], [start_pos], [final_pos], nr_interv, integ_time, **opts)


class d2scan(dNscan,Macro): 
    """two-motor scan relative to the starting position.
    d2scan scans two motors, as specified by motor1 and motor2.
    Each motor moves the same number of intervals. If each motor is at a
    position X before the scan begins, it will be scanned from X+start_posN
    to X+final_posN (where N is one of 1,2).
    The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts."""
    param_def = [
       ['motor1',      Type.Moveable,   None, 'Moveable 1 to move'],
       ['start_pos1',  Type.Float,   None, 'Scan start position 1'],
       ['final_pos1',  Type.Float,   None, 'Scan final position 1'],
       ['motor2',      Type.Moveable,   None, 'Moveable 2 to move'],
       ['start_pos2',  Type.Float,   None, 'Scan start position 2'],
       ['final_pos2',  Type.Float,   None, 'Scan final position 2'],
       ['nr_interv',  Type.Integer, None, 'Number of scan intervals'],
       ['integ_time', Type.Float,   None, 'Integration time']
    ]

    def prepare(self, motor1, start_pos1, final_pos1, motor2, start_pos2, final_pos2, nr_interv, integ_time,
                **opts):
        self._prepare([motor1,motor2], [start_pos1,start_pos2], [final_pos1,final_pos2], nr_interv, integ_time, **opts)


class d3scan(dNscan, Macro): 
    """three-motor scan .
    d3scan scans three motors, as specified by motor1, motor2 and motor3.
    Each motor moves the same number of intervals. If each motor is at a
    position X before the scan begins, it will be scanned from X+start_posN
    to X+final_posN (where N is one of 1,2,3)
    The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts."""
    param_def = [
       ['motor1',      Type.Moveable,   None, 'Moveable 1 to move'],
       ['start_pos1',  Type.Float,   None, 'Scan start position 1'],
       ['final_pos1',  Type.Float,   None, 'Scan final position 1'],
       ['motor2',      Type.Moveable,   None, 'Moveable 2 to move'],
       ['start_pos2',  Type.Float,   None, 'Scan start position 2'],
       ['final_pos2',  Type.Float,   None, 'Scan final position 2'],
       ['motor3',      Type.Moveable,   None, 'Moveable 3 to move'],
       ['start_pos3',  Type.Float,   None, 'Scan start position 3'],
       ['final_pos3',  Type.Float,   None, 'Scan final position 3'],
       ['nr_interv',  Type.Integer, None, 'Number of scan intervals'],
       ['integ_time', Type.Float,   None, 'Integration time']
    ]

    def prepare(self, m1, s1, f1,  m2, s2, f2, m3, s3, f3, nr_interv, integ_time,
                **opts):
        self._prepare([m1,m2,m3], [s1,s2,s3], [f1,f2,f3], nr_interv, integ_time, **opts)
        

class d4scan(dNscan, Macro): 
    """four-motor scan relative to the starting positions
    a4scan scans four motors, as specified by motor1, motor2, motor3 and motor4.
    Each motor moves the same number of intervals. If each motor is at a
    position X before the scan begins, it will be scanned from X+start_posN
    to X+final_posN (where N is one of 1,2,3,4).
    The step size for each motor is (start_pos-final_pos)/nr_interv.
    The number of data points collected will be nr_interv+1.
    Count time is given by time which if positive, specifies seconds and
    if negative, specifies monitor counts.
    Upon termination, the motors are returned to their starting positions.
    """
    param_def = [
       ['motor1',      Type.Moveable,   None, 'Moveable 1 to move'],
       ['start_pos1',  Type.Float,   None, 'Scan start position 1'],
       ['final_pos1',  Type.Float,   None, 'Scan final position 1'],
       ['motor2',      Type.Moveable,   None, 'Moveable 2 to move'],
       ['start_pos2',  Type.Float,   None, 'Scan start position 2'],
       ['final_pos2',  Type.Float,   None, 'Scan final position 2'],
       ['motor3',      Type.Moveable,   None, 'Moveable 3 to move'],
       ['start_pos3',  Type.Float,   None, 'Scan start position 3'],
       ['final_pos3',  Type.Float,   None, 'Scan final position 3'],
       ['motor4',      Type.Moveable,   None, 'Moveable 3 to move'],
       ['start_pos4',  Type.Float,   None, 'Scan start position 3'],
       ['final_pos4',  Type.Float,   None, 'Scan final position 3'],
       ['nr_interv',  Type.Integer, None, 'Number of scan intervals'],
       ['integ_time', Type.Float,   None, 'Integration time']
    ]

    def prepare(self, m1, s1, f1, m2, s2, f2, m3, s3, f3, m4, s4, f4, nr_interv,
                integ_time, **opts):
        self._prepare([m1,m2,m3,m4], [s1,s2,s3,m4], [f1,f2,f3,f4], nr_interv, integ_time, **opts)
        

class mesh(Macro,Hookable): 
    """2d grid scan  .
    The mesh scan traces out a grid using motor1 and motor2.
    The first motor scans from m1_start_pos to m1_final_pos using the specified
    number of intervals. The second motor similarly scans from m2_start_pos
    to m2_final_pos. Each point is counted for for integ_time seconds
    (or monitor counts, if integ_time is negative).
    The scan of motor1 is done at each point scanned by motor2. That is, the
    first motor scan is nested within the second motor scan.
    """
    
    hints = { 'scan' : 'mesh', 'allowsHooks': ('pre-scan', 'pre-move', 'post-move', 'pre-acq', 'post-acq', 'post-step', 'post-scan') }
    env = ('ActiveMntGrp',)
    
    param_def = [
       ['motor1',      Type.Moveable,   None, 'First motor to move'],
       ['m1_start_pos',Type.Float,   None, 'Scan start position for first motor'],
       ['m1_final_pos',Type.Float,   None, 'Scan final position for first motor'],
       ['m1_nr_interv',Type.Integer, None, 'Number of scan intervals'],
       ['motor2',      Type.Moveable,   None, 'Second motor to move'],
       ['m2_start_pos',Type.Float,   None, 'Scan start position for second motor'],
       ['m2_final_pos',Type.Float,   None, 'Scan final position for second motor'],
       ['m2_nr_interv',Type.Integer, None, 'Number of scan intervals'],
       ['integ_time',  Type.Float,   None, 'Integration time']
    ]

    def prepare(self, m1, m1_start_pos, m1_final_pos, m1_nr_interv,
                m2, m2_start_pos, m2_final_pos, m2_nr_interv, integ_time,
                **opts):
        self.motors=[m1,m2]
        self.starts = numpy.array([m1_start_pos,m2_start_pos],dtype='d')
        self.finals = numpy.array([m1_final_pos,m2_final_pos],dtype='d')
        self.nr_intervs= numpy.array([m1_nr_interv, m2_nr_interv],dtype='i')
        self.integ_time = integ_time
        
        self.name=opts.get('name','mesh')
        
        generator=self._generator
        moveables=self.motors
        env=opts.get('env',{})
        constrains=[getCallable(cns) for cns in opts.get('constrains',[UNCONSTRAINED])]
    
        self.pre_scan_hooks = self.getHooks('pre-scan')
        self.post_scan_hooks = self.getHooks('post-scan')

        self._gScan=SScan(self, generator, moveables, env, constrains)

    def _generator(self):
        step = {}
        step["integ_time"] =  self.integ_time
        step["pre-move-hooks"] = self.getHooks('pre-move')
        step["post-move-hooks"] = self.getHooks('post-move')
        step["pre-acq-hooks"] = self.getHooks('pre-acq')
        step["post-acq-hooks"] = self.getHooks('post-acq') +  self.getHooks('_NOHINTS_')
        step["post-step-hooks"] = self.getHooks('post-step')
        step["check_func"] = []
        m1start,m2start=self.starts
        m1end,m2end=self.finals
        points1,points2=self.nr_intervs+1
        point_no=1
        for m2pos in numpy.linspace(m2start,m2end,points2):
            for m1pos in numpy.linspace(m1start,m1end,points1):
                step["positions"] = numpy.array([m1pos,m2pos])
                step["point_id"]= point_no  #@TODO: maybe another ID would be better? (e.g. "(A,B)")
                point_no+=1
                yield step
    
    def run(self,*args):
        for step in self._gScan.step_scan():
            yield step

    @property
    def data(self):
        return self._gScan.data

class fscan(Macro,Hookable):
    '''N-dimensional scan along user defined paths.
    The motion path for each motor is defined through the evaluation of a
    user-supplied function that is evaluated as a function of the independent
    variables.
    -independent variables are supplied through the indepvar string.
    The syntax for indepvar is "x=expresion1,y=expresion2,..."
    -If no indep vars need to be defined, write "!" or "*" or "None"
    -motion path for motor is generated by evaluating the corresponding
    function 'func'
    -Count time is given by integ_time. If integ_time is a scalar, then
    the same integ_time is used for all points. If it evaluates as an array
    (with same length as the paths), fscan will assign a different integration
    time to each acquisition point.
    -If integ_time is positive, it specifies seconds and if negative, specifies
    monitor counts.   

    IMPORTANT Notes:
    -no spaces are allowed in the indepvar string.
    -all funcs must evaluate to the same number of points
    
    EXAMPLE: fscan x=[1,3,5,7,9],y=arange(5) motor1 x**2 motor2 sqrt(y*x-3) 0.1
    '''
    
    hints = { 'scan' : 'fscan', 'allowsHooks': ('pre-scan', 'pre-move', 'post-move', 'pre-acq', 'post-acq', 'post-step', 'post-scan') }
    env = ('ActiveMntGrp',)
    
    param_def = [
       ['indepvars',  Type.String, None, 'Independent Variables'],
       ['motor_funcs',
        ParamRepeat(['motor', Type.Moveable, None, 'motor'],
                    ['func', Type.String, None, 'curve defining path']),
        None, 'List of motor and path curves'],
       ['integ_time', Type.String,   None, 'Integration time']
    ]
    
    def prepare(self, *args, **opts):
        if args[0].lower() in ["!", "*", "none", None]: indepvars={}
        else: indepvars=SafeEvaluator({'dict':dict}).eval('dict(%s)'%args[0]) #create a dict containing the indepvars
        self.motors=args[1:-1:2] #get motors
        sev=SafeEvaluator(indepvars) #create a safe evaluator whitelisting the indepvars
        self.funcstrings=args[2:-1:2]
        self.paths = map(sev.eval,self.funcstrings) #evaluate the functions
        self.integ_time=numpy.array(sev.eval(args[-1]), dtype='d')
        self.opts = opts
        if len(self.motors)==len(self.paths)>0:
            self.N=len(self.motors)
        else:
            raise ValueError('Moveable and func lists must be non-empty and same length')
        npoints=len(self.paths[0])
        try:
            #if everything is OK, the following lines should return a 2D array
            # n which each motor path is a row.
            #Typical failure is due to shape mismatch due to inconsistent input
            self.paths=numpy.array(self.paths,dtype='d')
            self.paths.reshape((self.N, npoints))
        except: #shape mismatch?
            #try to give a meaningful description of the error
            for p,fs in zip(self.paths,self.funcstrings):
                if len(p)!=npoints:
                    raise ValueError(
                        '"%s" and "%s" yield different number of points (%i vs %i)'
                        %(self.funcstrings[0],fs,npoints,len(p)))
            raise #the problem wasn't a shape mismatch
        self.nr_points=npoints
        
        if self.integ_time.size==1:
            self.integ_time=self.integ_time*numpy.ones(self.nr_points) #extend integ_time
        elif self.integ_time.size!=self.nr_points:
            raise ValueError('time_integ must either be a scalar or length=npoints (%i)'%self.nr_points)
                
        self.name=opts.get('name','fscan')
                
        generator=self._generator
        moveables=self.motors
        env=opts.get('env',{})
        constrains=[getCallable(cns) for cns in opts.get('constrains',[UNCONSTRAINED])]
        
        self.pre_scan_hooks = self.getHooks('pre-scan')
        self.post_scan_hooks = self.getHooks('post-scan')
        self._gScan=SScan(self, generator, moveables, env, constrains)
        
    def _generator(self):
        step = {}
        step["pre-move-hooks"] = self.getHooks('pre-move')
        step["post-move-hooks"] = self.getHooks('post-move')
        step["pre-acq-hooks"] = self.getHooks('pre-acq')
        step["post-acq-hooks"] = self.getHooks('post-acq') + self.getHooks('_NOHINTS_')
        step["post-step-hooks"] = self.getHooks('post-step')
        
        step["check_func"] = []
        for i in xrange(self.nr_points):
            step["positions"] = self.paths[:,i]
            step["integ_time"] = self.integ_time[i]
            step["point_id"]= i
            yield step
    
    def run(self,*args):
        for step in self._gScan.step_scan():
            yield step

    @property
    def data(self):
        return self._gScan.data


class scanhist(Macro):
    """Shows scan history information. Give optional parameter scan number to
    display details about a specific scan"""
    
    param_def = [
       ['scan number',  Type.Integer, -1,
        'scan number. [default=-1 meaning show all scans]'],
    ]
    
    def run(self, scan_number):
        try:
            hist = self.getEnv("ScanHistory")
        except UnknownEnv:
            print "No scan recorded in history"
            return
        if scan_number < 0:
            self.show_all(hist)
        else:
            self.show_one(hist, scan_number)
    
    def show_one(self, hist, scan_number):
        item = None
        for h in hist:
            if h['serialno'] == scan_number:
                item = h
                break
        if item is None:
            self.warning("Could not find scan number %s", scan_number)
            return
        
        serialno, title = h['serialno'], h['title']
        start = datetime.datetime.fromtimestamp(h['startts'])
        end = datetime.datetime.fromtimestamp(h['endts'])
        total_time = end - start
        start, end, total_time = start.ctime(), end.ctime(), str(total_time)
        scan_dir, scan_file = h['ScanDir'], h['ScanFile']
        deadtime = '%.1f%%' % h['deadtime']
        
        user = h['user']
        store = "Not stored!"
        if scan_dir is not None and scan_file is not None:
            if type(scan_file) is str:
                store = os.path.join(scan_dir, scan_file)
            else:
                store = scan_dir + os.path.sep + str(scan_file)
        
        channels = ", ".join(h['channels'])
        cols = ["#", "Title", "Start time", "End time", "Took", "Dead time",
                "User", "Stored", "Channels" ]
        data = [serialno, title, start, end, total_time, deadtime, user, store,
                channels]
        
        table = Table([data], row_head_str=cols, row_head_fmt='%*s',
                      elem_fmt=['%-*s'],
                      col_sep='  :  ')
        for line in table.genOutput():
            self.output(line)
    
    def show_all(self, hist):
        
        cols  = "#", "Title", "Start time", "End time", "Stored"
        width =  -1,      -1,           -1,         -1,       -1
        out = List(cols, max_col_width=width)
        today = datetime.datetime.today().date()
        for h in hist:
            start = datetime.datetime.fromtimestamp(h['startts'])
            if start.date() == today:
                start = start.time().strftime("%H:%M:%S")
            else:
                start = start.strftime("%Y-%m-%d %H:%M:%S")
            end = datetime.datetime.fromtimestamp(h['endts'])
            if end.date() == today:
                end = end.time().strftime("%H:%M:%S")
            else:
                end = end.strftime("%Y-%m-%d %H:%M:%S")
            scan_file = h['ScanFile']
            store = "Not stored!"
            if scan_file is not None:
                store = ", ".join(scan_file)
            row = h['serialno'], h['title'], start, end, store
            out.appendRow(row)
        for line in out.genOutput():
            self.output(line)
        
        

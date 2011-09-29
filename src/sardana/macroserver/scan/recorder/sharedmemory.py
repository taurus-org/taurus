#!/usr/bin/env python

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

"""This is the macro server scan data output recorder module"""

__all__ = ["SharedMemoryRecorder"]

__docformat__ = 'restructuredtext'

import os
import time
import operator
import numpy

from datarecorder import DataRecorder

SPS_AVAILABLE = False
try:
    import sps
    SPS_AVAILABLE = True
except:
    pass

class _SharedMemoryRecorder(DataRecorder):
    
    def __init__(self, **pars):
        DataRecorder.__init__(self, **pars)


class SPSRecorder(_SharedMemoryRecorder):
    
    maxenv = 50
    envlen = 1024
    
    def __init__(self, program=None, array=None, shape=None, **kwpars):
        """ @param[in] program SPS program name
            @param[in] array SPS array name
            @param[in] shape tuple (cols, rows)
            @param[in] pars keyword extra parameters
        """
        _SharedMemoryRecorder.__init__(self, **kwpars)
        self.shape = shape
        self.owner = False
        self.owner_ENV = False
        self.setID(program, array)
        
    def setID(self, program, array):
        self.program = program.replace('/','')
        self.array = array.replace('_','')
        if not array is None:
            self.array_ENV = "%s_ENV" % self.array
        else:
            self.array_ENV = None
        if program and array:
            self.init()

    def init(self):
        pass
        
    def setSize(self, rows, cols):
        self.shape = (cols, rows)
        self.rows = rows
        self.cols = cols

    def isInitialized(self):
        ret = not (self.program is None or self.array_ENV is None or self.array is None)
        return ret and not self.shape is None

    def putEnv(self, name, value):
        if not self.isInitialized(): return
        sps.putenv(self.program, self.array_ENV, name, str(value))

    def putAllEnv(self, d):
        if not self.isInitialized(): return
        p, a = self.program, self.array_ENV
        for k, v in d.iteritems():
            sps.putenv(p, a, k, str(v))

    def _startRecordList(self, recordlist):
        if not self.isInitialized(): return
        
        arraylist = sps.getarraylist(self.program)

        if self.array in arraylist:
            shm = sps.attach(self.program, self.array)
        else:
            cols, rows = self.shape
            sps.create(self.program, self.array, rows, cols, sps.DOUBLE)
            self.owner = True

        if self.array_ENV in arraylist:
            shm_env = sps.attach(self.program, self.array_ENV )
        else:
            sps.create(self.program, self.array_ENV, self.maxenv, self.envlen,
                       sps.STRING)
            self.owner_ENV = True
                       
        self.nopts = 0
        
        env = recordlist.getEnviron()
        
        self.labels = [ col.label for col in env['datadesc'] ]
        
        env = {     'title' : env['title'], 
                  'started' : env['starttime'].ctime(),
                    'ended' : '',
               'axistitles' : ' '.join(self.labels),
                   'ylabel' : 'Counts',
                    'nopts' : self.nopts,
                     'xbeg' : 0,
                     'xend' : 200,
                  'aborted' : 0,
                  'command' : 'done',
                'fitresult' : '0' }
        
        self.putAllEnv(env)
        
    def _writeRecord(self, record):
        if not self.isInitialized(): return
        
        vals = []
        
        for colname in self.labels:
            val = record.data.get(colname)
            if (not val is None) and (operator.isNumberType(val) and (type(val) in [int,float,long])):
                vals.append(val)
            elif (not val is None) and (operator.isNumberType(val)):
                valsmca = []
                for i in range(0, len(val)):
                    valsmca.append(val[i])
                sufix = "1D"
                if self.array.endswith(sufix):
                    valsmca = numpy.array( valsmca )
                    sps.putdatarow( self.program, self.array, record.recordno, valsmca )

        sufix = "0D"
        if self.array.endswith(sufix):                   
            vals = numpy.array( vals )
            sps.putdatarow( self.program, self.array, record.recordno, vals )

        self.nopts +=1

        env = {   'nopts' : self.nopts,
                   'peak' : 111,
                'peakpos' : 34,
                   'fwhm' : 12.3,
                'fwhmpos' : 45,
                    'com' : 23 }
                    
        self.putAllEnv(env)

    def _endRecordList(self, recordlist):
        if not self.isInitialized(): return
        env = recordlist.getEnviron()
        self.putEnv('ended', env.get('endtime').ctime())


class ShmRecorder(DataRecorder):

    """ Sets data in shared memory to be used by sps """

    maxenv = 50
    envlen = 1024

    def setShmID(self, shmid):
        self.shm_id = shmid
        self.shm_id_ENV = shmid + "_ENV"

    def setShmMntGrp(self, mnt_grp):
        self.mnt_grp = mnt_grp

    def setProgram(self, progname):
        self.progname = progname

    def isInitialized(self):
        try:
            getattr(self, "shm_id")
            getattr(self, "shm_id_env")
            getattr(self, "progname")
            return True
        except:
            return False

    def setSize(self, rows, cols):
        self.rows = rows
        self.cols = cols

    def putenv(self, name, value):
        sps.putenv(self.progname, self.shm_id_env, name, str(value))

    def setChanDimList(self, chandimlist):
        self.chandimlist = chandimlist

    def _startRecordList(self, recordlist):

        if not self.isInitialized(): return

        arraylist = sps.getarraylist(self.progname)

        if self.shm_id in arraylist:
            shm = sps.attach(self.progname, self.shm_id)
        else:
            sps.create(self.progname, self.shm_id, self.rows, self.cols, 
                       sps.DOUBLE)

        if self.shm_id_env in arraylist:
            shm_env = sps.attach(self.progname, self.shm_id_env )
        else:
            sps.create(self.progname, self.shm_id_env, self.maxenv, self.envlen,
                       sps.STRING)

        print "Starting new SHM recording"

        self.putenv( 'title', recordlist.getEnvironValue('title') )

        for env,val in recordlist.getEnviron().items():
           if env != 'title' and env != 'labels':
               self.putenv( env , val)

        self.nopts = 0

        self.putenv('started', time.ctime(recordlist.getEnvironValue('starttime')))
        self.putenv('ended', '')
        self.putenv('axistitles', ' '.join(recordlist.getEnvironValue('labels')))
        self.putenv('ylabel', 'Counts')
        self.putenv('nopts', self.nopts)
        self.putenv('xbeg',100)
        self.putenv('xend',200)
        self.putenv('aborted',0)
        self.putenv('command','done')
        self.putenv('fitresult','0')
        
        self.labels = recordlist.getEnvironValue('labels')

    def _writeRecord(self, record):
        # uhmm. only numeric values can be written
        
        if not self.isInitialized(): return
        
        vals = []
        
        dim_list = []
        for colname in self.labels:
            dim_list.append(0)
            val = record.data.get(colname)
            if (not val is None) and (type(val) in [int,float,long]):
                vals.append(val) 
                
        myj = 0
                
        for val2 in record.data:
           tmp = val2+'_value'
           #esto me da el nombre del canal
           for dim in self.chandimlist:
              if tmp == dim:
                 dim_list[myj] = self.chandimlist[dim]
                 myj = myj+1 
                
        myj = 0
                 
        for val2 in record.data.values():
           valsmca = []
           if type(val2) in [list]:
              if dim_list[myj] == 1:
                 for i in range(0,len(val2)):
                    valsmca.append(val2[i])
                 tmp_name =  self.mnt_grp + "_1D"
                 if self.shm_id == tmp_name:
                    valsmca = numpy.array( valsmca )
                    sps.putdatarow( self.progname, self.shm_id, record.recordno, valsmca )
           myj = myj+1
           
        vals = numpy.array( vals )
        tmp_name =  self.mnt_grp+"_0D"
        if self.shm_id == tmp_name:
           sps.putdatarow( self.progname, self.shm_id, record.recordno, vals )
           
        self.nopts +=1
        self.putenv('nopts', self.nopts)
        self.putenv('peak', 111)
        self.putenv('peakpos', 34)
        self.putenv('fwhm', 12.3)
        self.putenv('fwhmpos', 45)
        self.putenv('com', 23)


    def _endRecordList(self, recordlist):
        if not self.isInitialized(): return
        self.putenv('ended', time.ctime( recordlist.getEnvironValue('endtime')))


def SharedMemoryRecorder(type, **pars):
    global SPS_AVAILABLE
    if type == 'sps' and SPS_AVAILABLE:
        klass = SPSRecorder
    else:
        return
    
    return klass(**pars)

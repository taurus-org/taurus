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

__all__ = ["JsonRecorder", "OutputRecorder"]

__docformat__ = 'restructuredtext'

import numpy
import datetime
import operator
import string

from taurus.core.util import json, CodecFactory

from datarecorder import DataRecorder
from storage import BaseFileRecorder


class JsonRecorder(DataRecorder):
    def __init__(self, stream, cols=None, **pars):
        DataRecorder.__init__(self, **pars)
        self._stream = stream
        self._codec = CodecFactory().getCodec('json')

    def _startRecordList(self, recordlist):
        macro_id = recordlist.getEnvironValue('macro_id')
        title = recordlist.getEnvironValue('title')
        counters = recordlist.getEnvironValue('counters')
        scanfile = recordlist.getEnvironValue('ScanFile')
        scandir = recordlist.getEnvironValue('ScanDir')
        serialno = recordlist.getEnvironValue('serialno')
        column_desc = recordlist.getEnvironValue('datadesc')
        ref_moveables = recordlist.getEnvironValue('ref_moveables')
        estimatedtime = recordlist.getEnvironValue('estimatedtime')
        total_scan_intervals = recordlist.getEnvironValue('total_scan_intervals')
        start_time = recordlist.getEnvironValue('starttime').ctime()
        self.column_desc = [ e for e in column_desc if e.shape == () ] #only scalar data is transmitted with json
        column_desc = [ d.toDict() for d in self.column_desc ]
        data = { 'column_desc' : column_desc,
                 'ref_moveables' : ref_moveables,
                 'estimatedtime' : estimatedtime,
                 'total_scan_intervals' : total_scan_intervals,
                 'starttime': start_time,
                 'title': title,
                 'counters': counters,
                 'scanfile': scanfile,
                 'scandir' : scandir,
                 'serialno': serialno}
        self._sendPacket(type="data_desc", data=data, macro_id=macro_id)
    
    def _endRecordList(self, recordlist):
        macro_id = recordlist.getEnvironValue('macro_id')
        data = { 'endtime'  : recordlist.getEnvironValue('endtime').ctime(),
                 'deadtime' : recordlist.getEnvironValue('deadtime') }
        self._sendPacket(type="record_end", data=data, macro_id=macro_id)
    
    def _writeRecord(self, record):
        macro_id = self.recordlist.getEnvironValue('macro_id')
        data = {} # dict(record.data)
        for k in self.column_desc:
            name = k.name
            data[name] = record.data[name]
        self._sendPacket(type="record_data", data=data, macro_id=macro_id)
        
    def _sendPacket(self, **kwargs):
        '''creates a JSON packet using the keyword arguments passed and then sends it'''
        #data = self._codec.encode(('', kwargs))
        #self._stream.sendRecordData(*data)
        self._stream.sendRecordData(kwargs)
    
class OutputRecorder(DataRecorder):
    
    def __init__(self, stream, cols=None, number_fmt='%8.4f', col_sep=' ', **pars):
        DataRecorder.__init__(self, **pars)
        self._stream = stream
        if not number_fmt.startswith('%'): number_fmt = '%%s' % number_fmt
        self._number_fmt = number_fmt
        self._col_sep = col_sep
        if operator.isSequenceType(cols) and not type(cols) in types.StringTypes:
            cols = CaselessList(cols)
        elif operator.isNumberType(cols):
            cols = cols
        else:
            cols = None
        self._columns = cols
        
    def _startRecordList(self, recordlist):
        starttime = recordlist.getEnvironValue('starttime').ctime()
        estimatedtime = recordlist.getEnvironValue('estimatedtime')
        data_desc = recordlist.getEnvironValue('datadesc')
        serialno = recordlist.getEnvironValue('serialno')
        
        dh = recordlist.getDataHandler()
        
        for fr in [ r for r in dh.recorders if isinstance(r, BaseFileRecorder) ]:
            self._stream.info('Operation will be saved in %s (%s)', 
                              fr.getFileName(), fr.getFormat())

        msg = "Scan #%d started at %s." % (serialno, starttime)
        if not estimatedtime is None:
            estimatedtime = datetime.timedelta(0, abs(estimatedtime))
            msg += " It will take at least %s" % estimatedtime
        self._stream.info(msg)

        #labels = [ col.label for col in data_desc if numpy.prod(col.shape) == 1 ]
        labels = [ col.label for col in data_desc if getattr(col,'output',True) ]
        col_names = [ col.name for col in data_desc if getattr(col,'output',True) ]
        
        cols = self._columns
        if operator.isSequenceType(cols):
            labels = [labels[0]] + [ l for l in labels[1:] if l in cols ]
            col_names = [col_names[0]] + [ l for l in col_names[1:] if l in cols ]
        elif operator.isNumberType(cols):
            labels = labels[:cols]
            col_names = col_names[:cols]
        
        self._labels = labels
        self._col_names = col_names
        
        col_size = max(map(len, self._col_names))
        number_size = len(self._number_fmt % float())
        self._col_size = max(col_size, number_size)
        
        cell_t_number = '%%%%(%%s)%s' % self._number_fmt[1:]
        cell_t_str = '%%%%(%s)%s'
        
        self._scan_line_t  = [(col_names[0], '%%(%s)4d' % col_names[0])]
        self._scan_line_t += [ (name, cell_t_number % name) for name in col_names[1:] ]
        header = ''
        for l in self._labels:
            header += '%s%s%s' % (self._col_sep,
                                  string.center(l, self._col_size),
                                  self._col_sep)
            
        self._stream.output(header)
        self._stream.flushOutput()
    
    def _endRecordList(self, recordlist):
        self._stream.flushOutput()
        starttime = recordlist.getEnvironValue('starttime')
        endtime   = recordlist.getEnvironValue('endtime')
        deadtime = recordlist.getEnvironValue('deadtime')
        deltatime = endtime - starttime
        endtime = endtime.ctime()
        serialno = recordlist.getEnvironValue('serialno')

        dh = recordlist.getDataHandler()
        
        for fr in [ r for r in dh.recorders if isinstance(r, BaseFileRecorder) ]:
            self._stream.info('Operation saved in %s (%s)', fr.getFileName(),
                              fr.getFormat())

        self._stream.info('Scan #%s ended at %s, taking %s (dead time was %.1f%%)'
                          % (serialno, endtime, deltatime, deadtime))
    
    def _writeRecord(self, record):
        scan_line, sep, c_nb = '', self._col_sep, self._col_size
        for name, cell in self._scan_line_t:
            cell_data = record.data[name]
            if isinstance(cell_data, numpy.ndarray):
                cell = str(cell_data.shape)
            elif cell_data is None:
                cell = "<no data>"
            else:
                cell %= record.data
            scan_line += '%s%s%s' % (sep, string.center(cell, c_nb), sep)
            
        self._stream.output(scan_line)
        self._stream.flushOutput()

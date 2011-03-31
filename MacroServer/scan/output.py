import numpy
import datetime

from taurus.core.util import json, CodecFactory

from datarecorder import *
from storage import BaseFileRecorder

class JsonRecorder(DataRecorder):
    def __init__(self, stream, cols=None, **pars):
        DataRecorder.__init__(self, **pars)
        self._stream = stream
        self._codec = CodecFactory().getCodec('json')

    def _startRecordList(self, recordlist):
        macro_id = recordlist.getEnvironValue('macro_id')
#+++
        title = recordlist.getEnvironValue('title')
        counters = recordlist.getEnvironValue('counters')
        scanfile = recordlist.getEnvironValue('ScanFile')
        serialno = recordlist.getEnvironValue('serialno')
#+++
        column_desc = recordlist.getEnvironValue('datadesc')
        ref_moveables = recordlist.getEnvironValue('ref_moveables')
        estimatedtime = recordlist.getEnvironValue('estimatedtime')
        total_scan_intervals = recordlist.getEnvironValue('total_scan_intervals')
        start_time = recordlist.getEnvironValue('starttime').ctime()
        self.column_desc = [ e for e in column_desc if e.shape == (1,) ]
        column_desc = [ d.toDict() for d in self.column_desc ]
        data = { 'column_desc' : column_desc, 
                 'ref_moveables' : ref_moveables,
                 'estimatedtime' : estimatedtime,
                 'total_scan_intervals' : total_scan_intervals,
                 'starttime': start_time,
                 'title': title,
                 'counters': counters,
                 'scanfile': scanfile,
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
            name = k.label
            data[name] = record.data[name]
        self._sendPacket(type="record_data", data=data, macro_id=macro_id)
        
    def _sendPacket(self, **kwargs):
        '''creates a JSON packet using the keyword arguments passed and then sends it'''
        data = self._codec.encode(('', kwargs))
        self._stream.sendRecordData(*data)
    
    
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
        
        msg = "Scan started at %s." % starttime
        if not estimatedtime is None:
            estimatedtime = datetime.timedelta(0, abs(estimatedtime))
            msg += " It will take at least %s" % estimatedtime
        self._stream.info(msg)

        dh = recordlist.getDataHandler()
        
        for fr in [ r for r in dh.recorders if isinstance(r, BaseFileRecorder) ]:
            self._stream.info('Scan data will be saved in %s (%s)' % (fr.getFileName(), fr.getFormat()))

        #labels = [ col.label for col in data_desc if numpy.prod(col.shape) == 1 ]
        labels = [ col.label for col in data_desc ]
        cols = self._columns
        if operator.isSequenceType(cols):
            labels = [labels[0]] + [ l for l in labels[1:] if l in cols ]
        elif operator.isNumberType(cols):
            labels = labels[:cols]
        
        self._labels = ['#Pt No'] + labels[1:]
        
        col_size = max(map(len, self._labels))
        number_size = len(self._number_fmt % float())
        self._col_size = max(col_size, number_size)
        
        cell_t_number = '%%%%(%%s)%s' % self._number_fmt[1:]
        cell_t_str = '%%%%(%s)%s'
        
        self._scan_line_t  = [(labels[0], '%%(%s)4d' % labels[0])]
        self._scan_line_t += [ (l, cell_t_number % l) for l in self._labels[1:] ]
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
        self._stream.info('Scan ended at %s, taking %s (dead time was %.1f%%)' % (endtime, deltatime, deadtime))
    
    def _writeRecord(self, record):
        scan_line, sep, c_nb = '', self._col_sep, self._col_size
        for label, cell in self._scan_line_t:
            cell_data = record.data[label]
            if isinstance(cell_data, numpy.ndarray):
                cell = str(cell_data.shape)
            elif cell_data is None:
                cell = "<no data>"
            else:
                cell %= record.data
            scan_line += '%s%s%s' % (sep, string.center(cell, c_nb), sep)
            
        self._stream.output(scan_line)
        self._stream.flushOutput()

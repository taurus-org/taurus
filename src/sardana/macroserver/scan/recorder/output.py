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

from taurus.core.util.codecs import CodecFactory
from taurus.core.util.containers import CaselessList

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
        self.column_desc = []
        discarded = []
        for e in column_desc:
            if len(e.shape) == 0:
                self.column_desc.append(e)
            else:
                discarded.append(e.label)
        if discarded:
            self.info('The following data will not be json-serialized: %s',
                      " ".join(discarded))
        column_desc = [d.toDict() for d in self.column_desc]
        data = {'column_desc': column_desc,
                'ref_moveables': ref_moveables,
                'estimatedtime': estimatedtime,
                'total_scan_intervals': total_scan_intervals,
                'starttime': start_time,
                'title': title,
                'counters': counters,
                'scanfile': scanfile,
                'scandir': scandir,
                'serialno': serialno}
        self._sendPacket(type="data_desc", data=data, macro_id=macro_id)

    def _endRecordList(self, recordlist):
        macro_id = recordlist.getEnvironValue('macro_id')
        data = {'endtime': recordlist.getEnvironValue('endtime').ctime(),
                'deadtime': recordlist.getEnvironValue('deadtime')}
        self._sendPacket(type="record_end", data=data, macro_id=macro_id)

    def _writeRecord(self, record):
        macro_id = self.recordlist.getEnvironValue('macro_id')
        data = {}  # dict(record.data)
        for k in self.column_desc:
            name = k.name
            data[name] = record.data[name]
        self._sendPacket(type="record_data", data=data, macro_id=macro_id)

    def _sendPacket(self, **kwargs):
        '''creates a JSON packet using the keyword arguments passed
        and then sends it'''
        #data = self._codec.encode(('', kwargs))
        #self._stream.sendRecordData(*data)
        self._stream.sendRecordData(kwargs, codec='json')

    def _addCustomData(self, value, name, **kwargs):
        '''
        The custom data will be sent as a packet with type='custom_data'
        and its data will be the dictionary of keyword arguments passed to this
        method plus 'name' and 'value'
        '''
        #try to convert to list to avoid serialization problems
        try:
            value = value.tolist()
        except:
            pass
        macro_id = self._stream.getID()
        data = dict(kwargs)  # shallow copy
        data['name'] = name
        data['value'] = value
        self._sendPacket(type="custom_data", data=data, macro_id=macro_id)


class OutputRecorder(DataRecorder):

    def __init__(self, stream, cols=None, number_fmt='%8.4f', col_width=8,
                 col_sep='  ', **pars):
        DataRecorder.__init__(self, **pars)
        self._stream = stream
        if not number_fmt.startswith('%'):
            number_fmt = '%%s' % number_fmt
        self._number_fmt = number_fmt
        self._col_sep = col_sep
        self._col_width = col_width
        if operator.isSequenceType(cols) and \
                not isinstance(cols, (str, unicode)):
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
        col_sep = self._col_sep
        cols = self._columns
        number_fmt = self._number_fmt
        col_width = self._col_width
        dh = recordlist.getDataHandler()

        for fr in [r for r in dh.recorders if isinstance(r, BaseFileRecorder)]:
            self._stream.info('Operation will be saved in %s (%s)',
                              fr.getFileName(), fr.getFormat())

        msg = "Scan #%d started at %s." % (serialno, starttime)
        if not estimatedtime is None:
            estimatedtime = datetime.timedelta(0, abs(estimatedtime))
            msg += " It will take at least %s\n" % estimatedtime
            msg += "Moving to start positions..."
        self._stream.info(msg)

        labels, col_names, col_sizes = [], [], []
        header_rows, header_len = 1, 0
        for col, column in enumerate(data_desc):
            if not getattr(column, 'output', True):
                continue
            name = column.name
            if operator.isSequenceType(cols) and name not in cols:
                continue
            if operator.isNumberType(cols) and col >= cols:
                break
            col_names.append(name)
            label = column.label.strip()
            if len(label) > col_width:
                label = label.split("/")
            else:
                label = [label]
            header_rows = max(header_rows, len(label))
            labels.append(label)
            col_size = max(col_width, max(map(len, label)))
            header_len += col_size
            col_sizes.append(col_size)

        nb_cols = len(col_names)
        header_len += (nb_cols - 1) * len(col_sep)
        self._labels = labels
        self._col_names = col_names
        self._col_sizes = col_sizes

        header = [[] for i in range(header_rows)]
        for col, (label, col_size) in enumerate(zip(labels, col_sizes)):
            empty_row_nb = header_rows - len(label)
            for row in range(empty_row_nb):
                header[row].append(col_size*" ")
            for i, l in enumerate(label):
                header[i+empty_row_nb].append(string.center(l, col_size))
        head = []
        for header_row in header:
            head.append(col_sep.join(header_row))

        header = "\n".join(head)

        cell_t_number = '%%%%(%%s)%s' % number_fmt[1:]

        self._scan_line_t = [(col_names[0], '%%(%s)8d' % col_names[0])]
        self._scan_line_t += [(name, cell_t_number % name) for name in col_names[1:]]

        self._stream.output(header)
        self._stream.flushOutput()

    def _endRecordList(self, recordlist):
        self._stream.flushOutput()
        starttime = recordlist.getEnvironValue('starttime')
        endtime = recordlist.getEnvironValue('endtime')
        deadtime = recordlist.getEnvironValue('deadtime')
        motiontime = recordlist.getEnvironValue('motiontime')
        totaltime = endtime - starttime
        endtime = endtime.ctime()
        serialno = recordlist.getEnvironValue('serialno')

        dh = recordlist.getDataHandler()

        for fr in [r for r in dh.recorders if isinstance(r, BaseFileRecorder)]:
            self._stream.info('Operation saved in %s (%s)', fr.getFileName(),
                              fr.getFormat())

        endts = recordlist.getEnvironValue('endts')
        startts = recordlist.getEnvironValue('startts')
        totaltimets = endts - startts
        deadtime_perc = deadtime * 100.0 / totaltimets
        motiontime_perc = motiontime * 100.0 / totaltimets
        info_string = 'Scan #%s ended at %s, taking %s.' + \
                      'Dead time %.1f%% (motion dead time %.1f%%)'
        self._stream.info(info_string % (serialno, endtime, totaltime,
                                         deadtime_perc, motiontime_perc))

    def _writeRecord(self, record):
        cells = []
        for i, (name, cell) in enumerate(self._scan_line_t):
            cell_data = record.data[name]
            if isinstance(cell_data, numpy.ndarray):
                cell = str(cell_data.shape)
            elif cell_data is None:
                cell = "<nodata>"
            elif isinstance(cell_data, (str, unicode)):
                cell = "<string>"
            else:
                cell %= record.data
            cell = string.center(cell.strip(), self._col_sizes[i])
            cells.append(cell)
        scan_line = self._col_sep.join(cells)

        self._stream.output(scan_line)
        self._stream.flushOutput()

    def _addCustomData(self, value, name, **kwargs):
        '''
        The custom data will be added as an info line in the form:
        Custom data: name : value
        '''
        if numpy.rank(value) > 0:
            v = 'Array(%s)' % str(numpy.shape(value))
        else:
            v = str(value)
        self._stream.output('Custom data: %s : %s' % (name, v))
        self._stream.flushOutput()

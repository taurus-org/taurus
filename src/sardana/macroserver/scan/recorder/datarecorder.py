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

"""This is the macro server scan data recorder module"""

__all__ = ["DataFormats", "SaveModes", "RecorderStatus", "DataHandler",
           "DataRecorder", "DumbRecorder"]

__docformat__ = 'restructuredtext'

import time

from taurus.core.util import Enumeration, Logger

DataFormats = Enumeration('DataFormats', ('Spec', 'CSV', 'XLS', 'w5', 'w4',
                                          'wx', 'fio'))
SaveModes = Enumeration('SaveModes', ('Record', 'Block'))
RecorderStatus = Enumeration('RecorderStatus', ('Idle', 'Active', 'Disable'))


class DataHandler:
    """ The data handler is the data recording center of a system. It contains
    one or several recorders.  All data transit through the handler, then
    given to recorders for final saving """

    def __init__(self):
        self.recorders = []

    def addRecorder(self, recorder):
        if recorder is not None:
            self.recorders.append(recorder)

    def startRecordList(self, recordlist):
        for recorder in self.recorders:
            if recorder.savemode is SaveModes.Record:
                recorder.startRecordList(recordlist)

    def endRecordList(self, recordlist):
        for recorder in self.recorders:
            if recorder.savemode is SaveModes.Record:
                recorder.endRecordList(recordlist)
            else:
                recorder.writeRecordList(recordlist)

    def addRecord(self, recordlist, record):
        for recorder in self.recorders:
            if recorder.savemode is SaveModes.Record:
                recorder.writeRecord(record)
            else:  # blockSave
                pass

    def addCustomData(self, value, name, **kwargs):
        '''Write data other than a record.

        :param value: The value to be written
        :param name: An identification for this value

        Optional keyword arguments can be passed with information that some
        recorders may need in order to record this value.
        For example: the NeXus recorder will make use of "nxpath" info if
        available to place the value where it belongs in the nexus hierarchy.
        Check the `addCustomData` method of each recorder to see
        what they use/require.
        '''
        for recorder in self.recorders:
            recorder.addCustomData(value, name, **kwargs)

# Recorders


class DataRecorder(Logger):
    """ Generic class for data recorder. Does nothing"""
    def __init__(self, **pars):
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        self.recordlist = None
        self.status = RecorderStatus.Idle
        self.savemode = SaveModes.Record

    def getStatus(self):
        return self.status

    def disable(self):
        self.status = RecorderStatus.Disable

    def enable(self):
        self.status = RecorderStatus.Idle

    def startRecordList(self, recordlist):
        is_idle = self.status is RecorderStatus.Idle
        if is_idle:
            self.recordlist = recordlist

        self._startRecordList(recordlist)

        if is_idle:
            return 0
        else:
            return -1

    def _startRecordList(self, recordlist):
        pass

    def endRecordList(self, recordlist):
        self._endRecordList(recordlist)

        self.status = RecorderStatus.Idle
        self.recordlist = None

    def _endRecordList(self, recordlist):
        pass

    def writeRecordList(self, recordlist):
        """ Only in BLOCK_MODE. Will write whole RecordList """
        self._startRecordList(recordlist)
        for record in recordlist.records:
            self.writeRecord(record)
        self._endRecordList(recordlist)

    def writeRecord(self, record):
        self._writeRecord(record)

    def _writeRecord(self, record):
        pass

    def setSaveMode(self, mode):
        self.savemode = mode

    def addCustomData(self, value, name, **kwargs):
        try:
            self._addCustomData(value, name, **kwargs)
        except Exception, e:
            raise RuntimeError('%s can not process custom data: %s' %
                               (self.__class__.__name__, e))

    def _addCustomData(self, value, name, **kwargs):
        pass


class DumbRecorder(DataRecorder):
    def _startRecordList(self, recordlist):
        print "Starting new recording"
        print "# Title :     ", recordlist.getEnvironValue('title')
        env = recordlist.getEnviron()
        for envky in env.keys():
            if envky != 'title' and envky != 'labels':
                print "# %8s :    %s " % (envky, str(env[envky]))
        print "# Started:    ", time.ctime(env['starttime'])
        print "# L:  ",
        print "  ".join(env['labels'])

    def _writeRecord(self, record):
        print record.data

    def _endRecordList(self, recordlist):
        print "Ending recording"
        env = recordlist.getEnviron()
        print "Recording ended at: ", time.ctime(env['endtime'])

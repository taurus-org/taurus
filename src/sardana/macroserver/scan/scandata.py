#!/usr/bin/env python

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

"""This is the macro server scan data module"""

__all__ = ["ColumnDesc", "MoveableDesc", "Record", "RecordEnvironment",
           "ScanDataEnvironment", "RecordList", "ScanData", "ScanFactory"]

import copy

from taurus.core.util.singleton import Singleton

from sardana.macroserver.scan.recorder import DataHandler


class ColumnDesc:
    """The description of a column for a Record"""

    _TYPE_MAP = {"short": "int16",
                 "ushort": "uint16"}
    _shape = []
    _dtype = 'float64'

    def __init__(self, **kwargs):
        """Expected keywords are:

               - name (str, mandatory): unique column name
               - label (str, optional): column label (defaults to name)
               - dtype (str, optional): data type. Defaults to 'float64'
               - shape (seq, optional): data shape. Defaults to []

        Any keyword not in the previous list will be converted to a member of
        the :class:`ColumnDesc`"""
        #enforce that the mandatory arguments are present
        try:
            self.name = kwargs.pop('name')
        except:
            raise TypeError('"name" parameter is mandatory')

        #make sure that at least the required members exist
        self.label = kwargs.pop('label', self.name)
        self.setDtype(kwargs.pop('dtype', self.__class__._dtype))
        self.setShape(kwargs.pop('shape', self.__class__._shape))

        # create members of the ColumnDesc class using the remaining keyword
        # args
        self._extra_kwargs = kwargs
        self.__dict__.update(kwargs)

    def getShape(self):
        return self._shape

    def setShape(self, shape):
        self._shape = self._simplifyShape(shape)

    def getDtype(self):
        return self._dtype

    def setDtype(self, dtype):
        self._dtype = self.tr(dtype)

    shape = property(getShape, setShape)
    dtype = property(getDtype, setDtype)

    @staticmethod
    def _simplifyShape(s):
        '''the idea is to strip the shape of useless "ones" at the beginning.
        For example:

            - () -> ()
            - (1,) -> ()
            - (1,1,1,1) -> ()
            - (2,) -> (2)
            - (1,2) -> (2)
            - (1,2,3) -> (2,3)
            - (2,3) -> (2,3)
            - (1,1,1,2,3) -> (2,3)
            - (3,1,1) -> (3,1,1)
        '''
        s = list(s)
        for i, e in enumerate(s):
            if e > 1:
                return s[i:]
        return []

    def tr(self, dtype):
        return self._TYPE_MAP.get(dtype, dtype)

    def toDict(self):
        '''creates a dictionary representation of the record'''
        d = copy.deepcopy(self._extra_kwargs)
        for k in ['name', 'label', 'dtype', 'shape']:
            d[k] = getattr(self, k)
        return d

    def clone(self):
        return copy.deepcopy(self)
        #return self.__class__(**self.toDict())


class MoveableDesc(ColumnDesc):

    def __init__(self, **kwargs):
        """Expected keywords are:

               - moveable (Moveable, mandatory): moveable object
               - name (str, optional): column name (defaults to moveable name)
               - label (str, optional): column label (defaults to moveable
                 name)
               - dtype (str, optional): data type. Defaults to 'float64'
               - shape (seq, optional): data shape. Defaults to (1,)
               - instrument (Instrument, optional): instrument object.
                 Defaults to moveable instrument"""

        try:
            self.moveable = moveable = kwargs.pop('moveable')
        except KeyError:
            raise TypeError("moveable parameter is mandatory")
        name = moveable.getName()
        kwargs['name'] = kwargs.get('name', name)
        kwargs['label'] = kwargs.get('label', name)
        kwargs['instrument'] = kwargs.get('instrument', moveable.instrument)

        self.min_value = kwargs.get('min_value')
        self.max_value = kwargs.get('max_value')
        self.is_reference = kwargs.get('is_reference')
        ColumnDesc.__init__(self, **kwargs)

    def toDict(self):
        d = ColumnDesc.toDict(self)
        d['min_value'] = self.min_value
        d['max_value'] = self.max_value
        d['is_reference'] = self.is_reference
        return d

    def clone(self):
        return self.__class__(moveable=self.moveable, **self.toDict())


class Record:
    """ One record is a set of values measured at the same time.

    The Record.data member will be
    a dictionary containing:
      - 'point_nb' : (int) the point number of the scan
      - for each column of the scan (motor or counter), a key with the
      corresponding column name (str) and the corresponding value
    """

    def __init__(self, data):
        self.recordno = 0
        self.data = data
        self.complete = 0
        self.written = 0

    def setRecordNo(self, recordno):
        self.recordno = recordno

    def setComplete(self):
        self.complete = 1

    def setWritten(self):
        self.written = 1


class RecordEnvironment(dict):
    """  A RecordEnvironment is a set of arbitrary pairs of type
    label/value in the form of a dictionary.
    """
    __needed = ['title', 'labels']

    def isValid(self):
        """ Check valid environment = all needed keys present """

        if not self.needed:
            return 1

        for ky in self.needed + self.__needed:
            if ky not in self.keys():
                return 0
        else:
            return 1


class ScanDataEnvironment(RecordEnvironment):
    """It describes a recordlist and its environment

    A recordlist environment contains a number of predefined label/value pairs
    Values can be either a string, a numeric value or a list of strings,
    numbers

    title:     mandatory
    labels:    mandatory. label for each of the fields in a record of the
               recordlist
    fielddesc: description of the content of each of the fields in a record.
               Can be used to affect the way the field is saved by the
               recorder. If not present all fields are by default of type
               FLOAT and FORMAT ".8g"
    """
    needed = ['title', 'labels', 'user']


class RecordList(dict):
    """  A RecordList is a set of records: for example a scan.
    It is composed of a environment and a list of records"""

    def __init__(self, datahandler, environ=None):

        self.datahandler = datahandler
        if environ == None:
            self.environ = RecordEnvironment()
        else:
            self.environ = environ
        self.records = []

    # make it pickable
    def __getstate__(self):
        return dict(datahandler=None, environ=None, records=self.records)

    def setEnviron(self, environ):
        self.environ = environ

    def updateEnviron(self, environ):
        self.environ.update(environ)

    def setEnvironValue(self, name, value):
        self.environ[name] = value

    def getEnvironValue(self, name):
        return self.environ[name]

    def getEnviron(self):
        return self.environ

    def start(self):
        self.recordno = 0
        self.datahandler.startRecordList(self)

    def addRecord(self, record):
        rc = Record(record)
        rc.setRecordNo(self.recordno)
        self.records.append(rc)
        self[self.recordno] = rc
        self.recordno += 1

        self.datahandler.addRecord(self, rc)

    def addRecords(self, records):
        map(self.addRecord, records)

    def end(self):
        self.datahandler.endRecordList(self)

    def getDataHandler(self):
        return self.datahandler


class ScanData(RecordList):

    def __init__(self, environment=None, data_handler=None):
        dh = data_handler or DataHandler()
        RecordList.__init__(self, dh, environment)


class ScanFactory(Singleton):

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args):
        """Singleton instance initialization."""
        pass

    def getDataHandler(self):
        return DataHandler()

    def getScanData(self, dh):
        return ScanData(data_handler=dh)

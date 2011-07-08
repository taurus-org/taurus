from datarecorder import *

from taurus.core.util import Singleton, Logger

class ColumnDesc:
    """The description of a column for a Record"""
    
    _TYPE_MAP = { "short" : "int16",
                  "ushort" : "uint16", }
    
    def __init__(self, **kwargs):
        """Expected keywords are:
            - label (str, mandatory): column label
            - dtype (str, optional): data type. Defaults to 'float64'
            - shape (seq, optional): data shape. Defaults to (1,)
            - instrument (Instrument, optional): instrument object. Defaults to None"""
        
        # string to be used as label (e.g. will be used as column header in an ascii output)
        self.label = kwargs.get('label')
        if self.label is None:
            raise TypeError("label parameter is mandatory")
    
        # numpy-compatible description of data type
        self.dtype = self.tr(kwargs.get('dtype', 'float64'))
        
        # tuple describing the shape of the data:e.g. scalars-->() ;
        # a 5 element vector-->(5,) ; a 3x4 Matrix-->(3,4)
        s = kwargs.get('shape', ()) 
        self.shape = self._simplifyShape(s)
        self.instrument = kwargs.get('instrument', None)

    def _simplifyShape(self, s):
        for i in s:
            if i > 1:
                return s
        return (1,)

    def tr(self, dtype):
        return self._TYPE_MAP.get(dtype, dtype)
        
    def toDict(self):
        '''creates a dictionary representation of the record'''
        d={}
        for k in ['label', 'dtype', 'shape']:
            d[k] = getattr(self, k)
        if self.instrument is not None:
            d['instrument'] = self.instrument.getFullName()
            d['instrument_type'] = self.instrument.getType()
        return d


class MoveableDesc(ColumnDesc):
    
    def __init__(self, **kwargs):
        """Expected keywords are:
            - label (str, optional): column label (defaults to moveable name)
            - dtype (str, optional): data type. Defaults to 'float64'
            - shape (seq, optional): data shape. Defaults to (1,)
            - instrument (Instrument, optional): instrument object. Defaults to moveable instrument"""
            
        try:
            self.moveable = kwargs.pop('moveable')
        except KeyError:
            raise TypeError("moveable parameter is mandatory")
        
        kwargs['label'] = kwargs.get('label', self.moveable.getName())
        kwargs['instrument'] = kwargs.get('instrument', self.moveable.getInstrument())
        
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
        self.data     = data
        self.complete = 0
        self.written  = 0

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

        if not needed:  return 1

        for ky in self.needed + self.__needed:
           if ky not in self.keys():
              return 0 
        else:
           return 1


class ScanDataEnvironment(RecordEnvironment):
    """
    It describes a recordlist and its environment

    A recordlist environment contains a number of predefined label/value pairs
    Values can be either a string, a numeric value or a list of strings, numbers
      title:     mandatory
      labels:    mandatory. label for each of the fields in a record of the recordlist
      fielddesc: description of the content of each of the fields in a record. Can be used
          to affect the way the field is saved by the recorder. If not present all fields 
          are by default of type FLOAT and FORMAT ".8g"
    """
    needed = ['title', 'labels', 'user']


class RecordList(dict):
    """  A RecordList is a set of records: for example a scan.
    It is composed of a environment and a list of records
 """
    def __init__(self, datahandler, environ=None):

        self.datahandler = datahandler
        if environ == None:
           self.environ = RecordEnvironment()
        else:
           self.environ = environ
        self.records = []

    def setEnviron( self, environ):
        self.environ = environ

    def updateEnviron( self, environ):
        self.environ.update( environ )

    def setEnvironValue(self, name, value):
        self.environ[name] = value

    def getEnvironValue(self, name):
        return self.environ[name]

    def getEnviron(self):
        return self.environ

    def start(self):
        self.recordno = 0
        self.datahandler.startRecordList( self )
 
    def addRecord(self, record):
        rc = Record( record )
        rc.setRecordNo( self.recordno )
        self.records.append( rc )
        self[self.recordno] = rc
        self.recordno  += 1
        
        self.datahandler.addRecord( self, rc )

    def addRecords(self, records):
        map( self.addRecord, records )

    def end(self):
        self.datahandler.endRecordList( self )

    def getDataHandler(self):
        return self.datahandler

    #def __str__(self):
    #    return "RecordList(env=%s, records=%s" % (str(self.getEnviron()), str(self.records))

class ScanData(RecordList):
    def __init__(self, environment=None,data_handler=None):
        dh = data_handler or DataHandler()
        RecordList.__init__(self, dh, environment)


class ScanFactory(Singleton, Logger):
    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        self.serialno = 0


# +++
    def incrSerialNo(self):
        self.serialno += 1
        return self.serialno
# +++
    def getSerialNo(self):
        return self.serialno
# +++

    def getDataHandler(self):
        return DataHandler()

    def getScanData(self, dh):
        return ScanData(data_handler=dh)

    
def main():
    pass
   
if __name__ == '__main__':
   import time

   main()
   time.sleep(20) 

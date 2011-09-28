
from datarecorder import *
import numpy

try:
    import nxs  #check if Nexus data format is supported by this system
    NEXUS_AVAILABLE=True
except: 
    from taurus.core.util import Logger
    log = Logger("ScanStorage")
    log.info("NEXUS is not available. NEXUS_FileRecorder won't work")
    NEXUS_AVAILABLE=False


class BaseFileRecorder(DataRecorder):
    
    def __init__(self, **pars):
        DataRecorder.__init__(self, **pars)
        self.filename = None
        self.fd       = None 
        
    def getFileName(self):
        return self.filename

    def getFileObj(self):
        return self.fd

    def getFormat(self):
        return '<unknown>'

class FIO_FileRecorder(BaseFileRecorder):
    """ Saves data to a file """

    formats = { DataFormats.fio : '.fio' }

    def __init__(self, filename=None, macro=None, **pars):
        BaseFileRecorder.__init__(self)
        if filename:
            self.setFileName(filename)
        if macro:
            self.macro = macro
    
    def setFileName(self, filename):
        if self.fd != None:
            self.fd.close()
   
        dirname = os.path.dirname(filename)
        
        if not os.path.isdir(dirname):
            try:
                os.makedirs(dirname)
            except:
                self.filename = None
                return
        self.currentlist = None
        #
        # construct the filename, e.g. : /dir/subdir/etcdir/prefix_00123.fio
        #
        tpl = filename.rpartition('.')
        serial = ScanFactory().getSerialNo(); 
        self.filename = "%s_%05d.%s" % (tpl[0], serial, tpl[2])

    def getFormat(self):
        return DataFormats.whatis(DataFormats.fio)
    
    def _startRecordList(self, recordlist):
        
        if self.filename is None:
              return
 
        envRec = recordlist.getEnviron()

        #datetime object
        start_time = envRec['starttime']
        epoch = time.mktime(start_time.timetuple())
        serialno = envRec['serialno']
        
        #store labels for performace reason
        self.labels = [ e.label for e in envRec['datadesc'] ]
        self.fd = open( self.filename,'w')
        #
        # write the comment section of the header
        #
        self.fd.write("!\n! Comments\n!\n%%c\n %s\nuser %s Acquisition started at %s\n" % 
                      (envRec['title'], envRec['user'], start_time.ctime()))
        self.fd.flush()
        #
        # write the parameter section, including the motor positions, if needed
        #
        self.fd.write("!\n! Parameter\n!\n%p\n")
        self.fd.flush()
        env = self.macro.getAllEnv()
        if env.has_key( 'FlagWriteMotorPositions') and env['FlagWriteMotorPositions'] == True:
            all_motors = self.macro.findObjs('.*', type_class=Type.Motor)
            for mot in all_motors:
                record = "%s = %g\n" % (mot, mot.getPosition())
                self.fd.write( record)
            self.fd.flush()
        #
        # write the data section starting with the description of the columns
        #
        self.fd.write("!\n! Data\n!\n%d\n")
        self.fd.flush()
        i = 1
        for col in envRec[ 'datadesc']:
            if col.label == 'point_nb':
                continue
            dType = 'FLOAT'
            if col.dtype == 'float64':
                dType = 'DOUBLE'
            outLine = " Col %d %s %s\n" % ( i, col.label, dType)
            self.fd.write( outLine)
            i += 1
        self.fd.flush()

    def _writeRecord(self, record):
        if self.filename is None:
              return
        nan, labels, fd = float('nan'), self.labels, self.fd
        outstr = ''
        for c in labels:
            if c == 'point_nb':
                continue
            outstr += ' ' + str(record.data.get(c, nan))
        outstr += '\n'
        
        fd.write( outstr )
        fd.flush()

    def _endRecordList(self, recordlist):
        if self.filename is None:
              return

        envRec = recordlist.getEnviron()
        end_time = envRec['endtime'].ctime()
        self.fd.write("! Acquisition ended at %s\n" % end_time)
        self.fd.flush()
        self.fd.close()


class NEXUS_FileRecorder(BaseFileRecorder):
    """saves data to a nexus file
    This is a proof of concept, with the following limitations:
        Nexus file structure may not be standard
        assumes hdf5
        """

    formats = { DataFormats.w5 : '.h5', 
                DataFormats.w4 : '.h4', 
                DataFormats.wx : '.xml' }
        
    def __init__(self, filename=None, macro=None, overwrite=False, **pars):
        BaseFileRecorder.__init__(self, **pars)
        self.overwrite = overwrite
        if filename:
            self.setFileName(filename)
    
    def setFileName(self, filename):
        if self.fd  is not None:
            self.fd.close()
   
        self.filename    = filename
        #obtain preferred nexus file mode for writing  fromthe filename extension (defaults to hdf5) 
        extension=os.path.splitext(filename)[1]
        inv_formats = dict(itertools.izip(self.formats.itervalues(), self.formats.iterkeys()))
        self.nxfilemode  = inv_formats.get(extension.lower(), DataFormats.w5)
        self.currentlist = None
    
    def getFormat(self):
        return DataFormats.whatis(self.nxfilemode)
        
    def _startRecordList(self, recordlist):
        nxfilemode = self.getFormat()
        
        if self.filename is None:
            return
        if not self.overwrite and os.path.exists(self.filename): nxfilemode='rw'
        self.fd = nxs.open(self.filename, nxfilemode) 
        self.entryname=self._newentryname('entry')
        self.fd.makegroup(self.entryname,"NXentry") 
        self.fd.opengroup(self.entryname,"NXentry") 
        
        self.currentlist = recordlist
        env = self.currentlist.getEnviron()
        self.datadesc = env['datadesc']
        
        #make a dictionary out of env['instrumentlist'] (use paths as keys)
        self.instrDict={}
        for inst in env.get('instrumentlist',[]):
            self.instrDict[inst.getFullName()]=inst
        if self.instrDict is {}:
            self.warning("missing information on NEXUS structure. Nexus Tree won't be created")
        
        self.debug("starting new recording %d on file %s", env['serialno'], self.filename)

        #populate the entry with some data
        self._writeData("start_time",env['starttime'].isoformat(),'char') #note: the type should be NX_DATE_TIME, but the nxs python api does not recognice it
        self.fd.putattr("epoch",time.mktime(env['starttime'].timetuple()))
        self._writeData("title",env['title'],'char')
        self._writeData("entry_identifier",str(env['serialno']),'char')
        self.fd.makegroup("user","NXuser") #user data goes in a separate group following NX convention...
        self.fd.opengroup("user","NXuser")
        self._writeData("name",env['user'],'char')
        self.fd.closegroup()
        #prepare the measurement group
        self.fd.makegroup("measurement","measurement")
        self.fd.opengroup("measurement","measurement")
        if self.savemode==SaveModes.Record:
            #create extensible data elements
            for dd in self.datadesc:
                self.fd.makedata(dd.label,dd.dtype, [nxs.UNLIMITED]+list(dd.shape)) #the first dimension is extensible
        else:
            #leave the creation of the data elements to _writeRecordList (when we actually know the length of the data to write)
            pass 
        self.fd.flush()
        
    def _writeData(self, name, data, dtype, shape=None):
        if shape is None:
            if dtype=='char': shape=[len(data)]
        self.fd.makedata(name, dtype, shape)
        self.fd.opendata(name)
        self.fd.putdata(data)
        self.fd.closedata()

    def _writeRecord(self, record):
        if self.filename is None:
            return
        for dd in self.datadesc:
            if record.data.has_key( dd.label ):
                data = record.data[dd.label]
                self.trace("writing recordno %i: '%s' (type=%s, shape=%s)",
                           record.recordno, dd.label, type(data), dd.shape)
                self.fd.opendata(dd.label)
                
                if not hasattr(data, 'shape'):
                    data = numpy.array([data], dtype=dd.dtype)
                slab_offset = [record.recordno]+[0]*len(dd.shape)
                shape = [1]+list(numpy.shape(data))
                self.fd.putslab(data,slab_offset,shape)
                    
                ###Note: the following 3 lines of code were substituted by the one above.
                ###      (now we trust the datadesc info instead of asking the nxs file each time)
                #shape,dtype=self.fd.getinfo()
                #shape[0]=1 #the shape of the record is of just 1 slab in the extensible dimension (first dim)
                #self.fd.putslab(record.data[lbl],[record.recordno]+[0]*(len(shape)-1),shape)
                self.fd.closedata()
                self.trace("done writing %i", record.recordno)
            else:
                self.debug("missing data for label '%s'", dd.label)
        self.fd.flush()

    def _endRecordList(self, recordlist):

        if self.filename is None:
            return
        
        env=self.currentlist.getEnviron()
        self._populateInstrumentInfo()
        self.fd.openpath("/"+self.entryname)
        self._writeData("end_time",env['endtime'].isoformat(),'char')
        self.fd.flush()
        self.debug("Finishing recording %d on file %s:", env['serialno'], self.filename)
        #self.fd.show('.') #prints nexus file summary on stdout (only the current entry)
        self.fd.close()
        self.currentlist = None

    def writeRecordList(self, recordlist):
        """Called when in BLOCK writing mode"""
        self._startRecordList( recordlist )
        labels = self.currentlist.getEnvironValue('labels')
        for dd in self.datadesc:
            self.fd.makedata(dd.label, dd.dtype, [len(recordlist.records)]+list(dd.shape))
            self.fd.opendata(dd.label)
            try:
                #try creating a single block to write it at once
                block=numpy.array([r.data[dd.label] for r in recordlist.records],dtype=dd.dtype)
                #if dd.dtype !='char': block=numpy.array(block,dtype=dtype) #char not supported anyway
                self.fd.putdata(block)
            except KeyError:
                #if not all the records contain this field, we cannot write it as a block.. so do it record by record (but only this field!)
                for record in recordlist.records:
                    if record.data.has_key( dd.label ):
                        self.fd.putslab(record.data[dd.label],[record.recordno]+[0]*len(dd.shape),[1]+list(dd.shape)) 
                    else:
                        self.debug("missing data for label '%s' in record %i", dd.label, record.recordno)
            self.fd.closedata()
        self._endRecordList( recordlist )

    def _newentryname(self,preffix='entry',offset=1):
        '''Returns a str representing the name for a new entry.
        The name is formed by the preffix and an incremental numeric suffix.
        The offset indicates the start of the numeric suffix search'''
        i=offset
        while True:
            entry="%s%i"%(preffix,i)            
            try:
                self.fd.opengroup(entry,'NXentry')
                self.fd.closegroup()
                i+=1
            except ValueError: #no such group name exists
                return entry
    
    def _populateInstrumentInfo(self):
        #create the link for each set in <entry>/data that has a datadesc.nxpath
        for dd in self.datadesc:
            if dd.instrument is not None:
                #grab the ID of the data group
                datapath="/%s/%s/%s"%(self.entryname,"measurement",dd.label)
                self.fd.openpath(datapath)
                id=self.fd.getdataID()
                self._createBranch(dd.instrument.getFullName())
                self.fd.makelink(id)
            
    def _createBranch(self, path):
        """navigates the nexus tree starting in the current <entry> and finishing in <entry>/path.
        It creates the groups if they do not exist, using the class info in self.instrDict
        If successful, path is left open"""
        groups=path.split('/')
        self.fd.openpath("/"+self.entryname)
        relpath="" #the current path relative to <entry>, to use as a key for instrDict
        for g in groups:
            if len(g) == 0:
                continue
            relpath = relpath + "/"+ g
            try:
                self.fd.opengroup(g)
            except:
                self.fd.makegroup(g,self.instrDict[relpath].getType())
                self.fd.opengroup(g)


class SPEC_FileRecorder(BaseFileRecorder):
    """ Saves data to a file """

    formats = { DataFormats.Spec : '.spec' }

    def __init__(self, filename=None, macro=None, **pars):
        BaseFileRecorder.__init__(self)
        if filename:
            self.setFileName(filename)
    
    def setFileName(self, filename):
        if self.fd != None:
            self.fd.close()
   
        dirname = os.path.dirname(filename)
        
        if not os.path.isdir(dirname):
            try:
                os.makedirs(dirname)
            except:
                self.filename = None
                return
        self.filename    = filename
        self.currentlist = None

    def getFormat(self):
        return DataFormats.whatis(DataFormats.Spec)
    
    def _startRecordList(self, recordlist):

        if self.filename is None:
            return

        env = recordlist.getEnviron()
        
        #datetime object
        start_time = env['starttime']
        epoch = time.mktime(start_time.timetuple())
        serialno = env['serialno']
        
        #store labels for performance reason
        labels = []
        for e in env['datadesc']:
            if e.shape == (1,):
                labels.append(e.label)
        self.labels = labels

        data = {
                'serialno':  serialno,
                'title':     env['title'],
                'user':      env['user'],
                'epoch':     epoch,
                'starttime': start_time.ctime(),
                'nocols':    len(labels),
                'labels':    '  '.join(labels)
               }
               
        self.fd = open(self.filename,'a')
        self.fd.write("""
#S %(serialno)s %(title)s
#U %(user)s
#D %(epoch)s
#C Acquisition started at %(starttime)s
#N %(nocols)s
#L %(labels)s
""" % data )
        self.fd.flush()

    def _writeRecord(self, record):
        if self.filename is None:
            return
        nan, labels, fd = float('nan'), self.labels, self.fd
        
        d = []
        for c in labels:
            data = record.data.get(c)
            if data is None: data = nan
            d.append(str(data))
        outstr  = ' '.join(d)
        outstr += '\n'
        
        fd.write( outstr )
        fd.flush()

    def _endRecordList(self, recordlist):
        if self.filename is None:
            return

        env = recordlist.getEnviron()
        end_time = env['endtime'].ctime()
        self.fd.write("#C Acquisition ended at %s\n" % end_time)
        self.fd.flush()
        self.fd.close()


def FileRecorder(filename, macro, **pars):
    ext = os.path.splitext(filename)[1].lower() or '.spec'

    if ext in NEXUS_FileRecorder.formats.values():
        klass = NEXUS_FileRecorder
    elif ext in FIO_FileRecorder.formats.values():
        klass = FIO_FileRecorder
    else:
        klass = SPEC_FileRecorder
    return klass(filename=filename, macro=macro, **pars)

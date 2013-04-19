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

__all__ = ["BaseFileRecorder", "FileRecorder"]

__docformat__ = 'restructuredtext'

import os
import time
import itertools
import re

import numpy

from datarecorder import DataRecorder, DataFormats, SaveModes
from taurus.core.tango.sardana import PlotType
from sardana.macroserver.macro import Type
import PyTango

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
        self.base_filename = filename
        if macro:
            self.macro = macro
        self.db = PyTango.Database()

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
        serial = self.recordlist.getEnvironValue('serialno')
        self.filename = "%s_%05d.%s" % (tpl[0], serial, tpl[2])
        #
        # in case we have MCAs, prepare the dir name
        #
        self.mcaDirName = "%s_%05d" % (tpl[0], serial)

    def getFormat(self):
        return DataFormats.whatis(DataFormats.fio)
    
    def _startRecordList(self, recordlist):

        if self.base_filename is None:
            return

        self.setFileName(self.base_filename)
        
        envRec = recordlist.getEnviron()

        self.sampleTime = envRec['estimatedtime']/(envRec['total_scan_intervals'] + 1)
        #datetime object
        start_time = envRec['starttime']
        
        self.motorNames = envRec[ 'ref_moveables']
        self.mcaNames = []
        self.ctNames = []
        for e in envRec['datadesc']:
            if len( e.shape) == 1:
                self.mcaNames.append( e.name)
            else:
                self.ctNames.append( e.name)
        #
        # we need the aliases for the column description
        #
        self.mcaAliases = []
        for mca in self.mcaNames:
            lst = mca.split("/")
            self.mcaAliases.append( self.db.get_alias( "/".join( lst[1:])))

        # self.names = [ e.name for e in envRec['datadesc'] ]
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
        if env.has_key( 'FlagFioWriteMotorPositions') and env['FlagFioWriteMotorPositions'] == True:
            all_motors = self.macro.findObjs('.*', type_class=Type.Motor)
            all_motors.sort()
            for mot in all_motors:
                pos = mot.getPosition()
                if pos is None:
                    record = "%s = nan\n" % (mot)
                else:
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
            if col.name == 'point_nb':
                continue
            if col.name == 'timestamp':
                continue
            dType = 'FLOAT'
            if col.dtype == 'float64':
                dType = 'DOUBLE'
            outLine = " Col %d %s %s\n" % ( i, col.label, dType)
            self.fd.write( outLine)
            i += 1
        # +++
        # 11.9.2012 timestamp to the end
        #
        outLine = " Col %d %s %s\n" % ( i, 'timestamp', 'DOUBLE')
        self.fd.write( outLine)
        # +++
        self.fd.flush()

    def _writeRecord(self, record):
        if self.filename is None:
            return
        nan, ctNames, fd = float('nan'), self.ctNames, self.fd
        outstr = ''
        for c in ctNames:
            outstr += ' ' + str(record.data.get(c, nan))
        # +++
        # 11.9.2012 timestamp to the end
        #
        outstr += ' ' + str(record.data.get('timestamp', nan))
        # +++
        outstr += '\n'
        
        fd.write( outstr )
        fd.flush()

        if len( self.mcaNames) > 0:
            self._writeMcaFile( record)

    def _endRecordList(self, recordlist):
        if self.filename is None:
            return

        envRec = recordlist.getEnviron()
        end_time = envRec['endtime'].ctime()
        self.fd.write("! Acquisition ended at %s\n" % end_time)
        self.fd.flush()
        self.fd.close()

    def _writeMcaFile( self, record):
        if self.mcaDirName is None:
            return

        if not os.path.isdir( self.mcaDirName):
            try:
                os.makedirs( self.mcaDirName)
            except:
                self.mcaDirName = None
                return
        currDir = os.getenv( 'PWD')
        os.chdir( self.mcaDirName)

        serial = self.recordlist.getEnvironValue('serialno')
        if type(self.recordlist.getEnvironValue('ScanFile')).__name__ == 'list':
            scanFile = self.recordlist.getEnvironValue('ScanFile')[0]
        else:
            scanFile = self.recordlist.getEnvironValue('ScanFile')

        mcaFileName = "%s_%05d_mca_s%d.fio" % (scanFile.split('.')[0], serial, record.data['point_nb'] + 1)
        fd = open( mcaFileName,'w')
        fd.write("!\n! Comments\n!\n%%c\n Position %g, Index %d \n" % 
                      ( record.data[ self.motorNames[0]], record.data[ 'point_nb']))
        fd.write("!\n! Parameter \n%%p\n Sample_time = %g \n" % ( self.sampleTime))
        self.fd.flush()

        col = 1
        fd.write("!\n! Data \n%d \n")
        for mca in self.mcaAliases:
            fd.write(" Col %d %s FLOAT \n" % (col, mca))
            col = col + 1

        if not record.data[ self.mcaNames[0]] is None:
            #print "+++storage.py, recordno", record.recordno
            #print "+++storage.py, record.data", record.data
            #print "+++storage.py, len %d,  %s" % (len( record.data[ self.mcaNames[0]]), self.mcaNames[0])
            #
            # the MCA arrays me be of different size. the short ones are extended by zeros.
            #
            lMax = len( record.data[ self.mcaNames[0]])
            for mca in self.mcaNames:
                if len(record.data[ mca]) > lMax:
                    lMax = len(record.data[ mca])
                    
            for i in range( 0, lMax):
                line = ""
                for mca in self.mcaNames:
                    if i > (len(record.data[mca]) - 1):
                        line = line + " 0"
                    else:
                        line = line + " " + str( record.data[ mca][i])
                line = line + "\n"
                fd.write(line)
            
            fd.close()
        else:
            #print "+++storage.py, recordno", record.recordno, "data None"
            pass
            
        os.chdir( currDir)

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
        
        #store names for performance reason
        labels = []
        names = []
        for e in env['datadesc']:
            dims = len(e.shape)
            if not dims or (dims==1 and e.shape[0] == 1):
                sanitizedlabel = "".join(x for x in e.label.replace(' ','_') if x.isalnum() or x=='_') #substitute whitespaces by underscores and remove other non-alphanumeric characters
                labels.append(sanitizedlabel)
                names.append(e.name)
        self.names = names
        data = {
                'serialno':  serialno,
                'title':     env['title'],
                'user':      env['user'],
                'epoch':     epoch,
                'starttime': start_time.ctime(),
                'nocols':    len(names),
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
        nan, names, fd = float('nan'), self.names, self.fd
        
        d = []
        for c in names:
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

                    
    def _addCustomData(self, value, name, **kwargs):
        '''
        The custom data will be added as a comment line in the form:: 
        
        #C name : value
        
        ..note:: non-scalar values (or name/values containing end-of-line) will not be written
        '''
        if self.filename is None:
            self.info('Custom data "%s" will not be stored in SPEC file. Reason: uninitialized file',name)
            return
        if numpy.rank(value)>0: #ignore non-scalars
            self.info('Custom data "%s" will not be stored in SPEC file. Reason: value is non-scalar',name)
            return
        v = str(value)
        if '\n' in v or '\n' in name: #ignore if name or the string representation of the value contains end-of-line
            self.info('Custom data "%s" will not be stored in SPEC file. Reason: unsupported format',name)
            return
        
        fileWasClosed = self.fd is None or self.fd.closed
        if fileWasClosed:
            try:
                self.fd = open(self.filename,'a')
            except:
                self.info('Custom data "%s" will not be stored in SPEC file. Reason: cannot open file',name)
                return
        self.fd.write( '#C %s : %s\n'%(name,v) )
        self.fd.flush()
        if fileWasClosed:
            self.fd.close() #leave the file descriptor as found
        
        

class BaseNEXUS_FileRecorder(BaseFileRecorder):
    """Base class for NeXus file recorders"""   
    
    formats = { DataFormats.w5 : '.h5', 
                DataFormats.w4 : '.h4', 
                DataFormats.wx : '.xml' }
    supported_dtypes = ('float32','float64','int8',
                        'int16','int32','int64','uint8',
                        'uint16','uint32','uint64') #note that 'char' is not supported yet!
    _dataCompressionRank = -1
        
    def __init__(self, filename=None, macro=None, overwrite=False, **pars):
        BaseFileRecorder.__init__(self, **pars)

        try:
            import nxs  #check if Nexus data format is supported by this system
            self.nxs = nxs
        except ImportError:
            raise Exception("NeXus is not available")
        
        self.macro = macro
        self.overwrite = overwrite
        if filename:
            self.setFileName(filename)
            
        self.instrDict = {}
        self.entryname = 'entry'
    
    def setFileName(self, filename):
        if self.fd  is not None:
            self.fd.close()
   
        self.filename = filename
        #obtain preferred nexus file mode for writing from the filename extension (defaults to hdf5) 
        extension=os.path.splitext(filename)[1]
        inv_formats = dict(itertools.izip(self.formats.itervalues(), self.formats.iterkeys()))
        self.nxfilemode  = inv_formats.get(extension.lower(), DataFormats.w5)
        self.currentlist = None
    
    def getFormat(self):
        return DataFormats.whatis(self.nxfilemode)
    
    def sanitizeName(self, name):
        '''It returns a version of the given name that can be used as a python
        variable (and conforms to NeXus best-practices for dataset names)'''
        #make sure the name does not start with a digit 
        if name[0].isdigit(): name="_%s"%name 
        #substitute whitespaces by underscores and remove other non-alphanumeric characters
        return "".join(x for x in name.replace(' ','_') if x.isalnum() or x=='_')
    
    
    def _nxln(self, src, dst, name=None):
        '''convenience function to create NX links with just one call. On successful return, dst will be open.
        
        :param src: (str or NXgroup or NXfield) source group or dataset (or its path)
        :param dst: (str or NXgroup) the group that will hold the link (or its path)
        :param name: (str) name for the link. If not given, the name of the source is used
        
        .. note:: `groupname:nxclass` notation can be used for both paths for better performance
        '''
        
        fd = getattr(self, 'fd')
        if fd is None:
            fd = getattr(src,'nxfile', getattr(dst,'nxfile'))
        if fd is None:
            raise NeXusError('Cannot get a file handle')
        
        if isinstance(src, self.nxs.NXobject):
            src = src.nxpath
        if isinstance(dst, self.nxs.NXobject):
            dst = dst.nxpath
            
        fd.openpath(src)
        try:
            nid=fd.getdataID()
        except self.nxs.NeXusError:
            nid=fd.getgroupID()
        fd.openpath(dst)
        if name is None:
            fd.makelink(nid)
        else:
            fd.makenamedlink(name,nid)

    #===========================================================================
    # Unimplemented methods that must be implemented in derived classes    
    #===========================================================================
    
    def _startRecordList(self, recordlist):
        raise NotImplementedError('_startRecordList must be implemented in BaseNEXUS_FileRecorder derived classes')    
    
    def _writeRecord(self, record):
        raise NotImplementedError('_writeRecord must be implemented in BaseNEXUS_FileRecorder derived classes')  
    
    def _endRecordList(self, recordlist):
        raise NotImplementedError('_endRecordList must be implemented in BaseNEXUS_FileRecorder derived classes')  


class BaseNAPI_FileRecorder(BaseNEXUS_FileRecorder):
    """Base class for NeXus file recorders (NAPI-based)"""
    
    #===========================================================================
    # Convenience methods to make NAPI less tedious
    #===========================================================================
    
    _nxentryInPath = re.compile(r'/[^/:]+:NXentry')
    
    def _makedata(self, name, dtype=None, shape=None, mode='lzw', chunks=None, comprank=None):
        '''
        combines :meth:`nxs.NeXus.makedata` and :meth:`nxs.NeXus.compmakedata` by selecting between 
        using compression or not based on the comprank parameter and the rank of the data.
        Compression will be used only if the shape of the data is given and its length is larger 
        than comprank. If comprank is not passed (or None is passed) the default dataCompressionRank 
        will be used
        '''
        if comprank is None: 
            comprank = self._dataCompressionRank
        
        if shape is None or comprank<0 or (len(shape) < comprank):
            return self.fd.makedata(name, dtype=dtype, shape=shape)
        else:
            try:
                self.fd.compmakedata(name, dtype=dtype, shape=shape, mode=mode, chunks=chunks)
            except ValueError: #workaround for bug in nxs<4.3 (compmakedatafails if chunks is not explicitly passed)
                chunks = [1]*len(shape)
                chunks[-1] = shape[-1]
                self.fd.compmakedata(name, dtype=dtype, shape=shape, mode=mode, chunks=chunks)
              
    def _writeData(self, name, data, dtype, shape=None, chunks=None, attrs=None):
        '''
        convenience method that creates datasets (calling self._makedata), opens
        it (napi.opendata) and writes the data (napi.putdata).
        It also writes attributes (napi.putattr) if passed in a dictionary and 
        it returns the data Id (useful for linking). The dataset is left closed. 
        '''
        if shape is None:
            if dtype=='char': 
                shape = [len(data)]
                chunks = chunks or list(shape) #for 'char', write the whole block in one chunk
            else:
                shape = getattr(data,'shape',[1])
        self._makedata(name, dtype=dtype, shape=shape, chunks=chunks)
        self.fd.opendata(name)
        self.fd.putdata(data)
        if attrs is not None:
            for k,v in attrs.items():
                self.fd.putattr(k,v)
        nid = self.fd.getdataID()
        self.fd.closedata()
        return nid

    def _newentryname(self, prefix='entry', suffix='', offset=1):
        '''Returns a str representing the name for a new entry.
        The name is formed by the prefix and an incremental numeric suffix.
        The offset indicates the start of the numeric suffix search'''
        i=offset
        while True:
            entry="%s%i"%(prefix,i)
            if suffix:
                entry += " - " + suffix
            try:
                self.fd.opengroup(entry,'NXentry')
                self.fd.closegroup()
                i+=1
            except ValueError: #no such group name exists
                return entry
        
    def _nxln(self, src, dst):
        '''convenience function to create NX links with just one call. On successful return, dst will be open.
        
        :param src: (str) the nxpath to the source group or dataset
        :param dst: (str) the nxpath to the group that will hold the link
        
        .. note:: `groupname:nxclass` notation can be used for both paths for better performance
        '''
        self.fd.openpath(src)
        try:
            nid=self.fd.getdataID()
        except self.nxs.NeXusError:
            nid=self.fd.getgroupID()
        self.fd.openpath(dst)
        self.fd.makelink(nid)
            
    def _createBranch(self, path):
        """
        Navigates the nexus tree starting in / and finishing in path. 
        
        If path does not start with `/<something>:NXentry`, the current entry is
        prepended to it.
        
        This method creates the groups if they do not exist. If the
        path is given using `name:nxclass` notation, the given nxclass is used.
        Otherwise, the class name is obtained from self.instrDict values (and if
        not found, it defaults to NXcollection). If successful, path is left
        open
        """
        m = self._nxentryInPath.match(path)
        if m is None:
            self._createBranch("/%s:NXentry"%self.entryname) #if at all, it will recurse just once 
#            self.fd.openpath("/%s:NXentry" % self.entryname)
        else:
            self.fd.openpath("/")
        
        relpath="" 
        for g in path.split('/'):
            if len(g) == 0:
                continue
            relpath = relpath + "/"+ g
            if ':' in g:
                g,group_type = g.split(':')
            else:
                try:
                    group_type = self.instrDict[relpath].klass
                except:
                    group_type = 'NXcollection'
            try:
                self.fd.opengroup(g, group_type)
            except:
                self.fd.makegroup(g, group_type)
                self.fd.opengroup(g, group_type)
                

class NXscan_FileRecorder(BaseNAPI_FileRecorder):
    """saves data to a nexus file that follows the NXscan application definition
    
        """

    def __init__(self, filename=None, macro=None, overwrite=False, **pars):
        BaseNAPI_FileRecorder.__init__(self, filename=filename, macro=macro, overwrite=overwrite, **pars)
            
    def _startRecordList(self, recordlist):
        nxs = self.nxs
        nxfilemode = self.getFormat()
        
        if self.filename is None:
            return
        
        self.currentlist = recordlist
        env = self.currentlist.getEnviron()
        serialno = env["serialno"]
        self._dataCompressionRank = env.get("DataCompressionRank", self._dataCompressionRank)
        
        if not self.overwrite and os.path.exists(self.filename): nxfilemode='rw'
        self.fd = nxs.open(self.filename, nxfilemode)
        self.entryname = "entry%d" % serialno
        try:
            self.fd.makegroup(self.entryname,"NXentry")
        except NeXusError:
            entrynames = self.fd.getentries().keys()
            
            #===================================================================
            ##Warn and abort
            if self.entryname in entrynames:
                raise RuntimeError(('"%s" already exists in %s. To prevent data corruption the macro will be aborted.\n'%(self.entryname, self.filename)+
                                    'This is likely caused by a wrong ScanID\n'+
                                    'Possible workarounds:\n'+
                                    '  * first, try re-running this macro (the ScanID may be automatically corrected)\n'
                                    '  * if not, try changing ScanID with senv, or...\n'+
                                    '  * change the file name (%s will be in both files containing different data)\n'%self.entryname+
                                    '\nPlease report this problem.'))
            else:
                raise              
            #===================================================================
            
            #===================================================================
            ## Warn and continue writing to another entry
            #if self.entryname in entrynames:
            #    i = 2
            #    newname = "%s_%i"%(self.entryname,i)
            #    while(newname in entrynames):
            #        i +=1
            #        newname = "%s_%i"%(self.entryname,i)
            #    self.warning('"%s" already exists. Using "%s" instead. This may indicate a bug in %s',self.entryname, newname, self.macro.name)
            #    self.macro.warning('"%s" already exists. Using "%s" instead. \nThis may indicate a bug in %s. Please report it.',self.entryname, newname, self.macro.name)
            #    self.entryname = newname
            #    self.fd.makegroup(self.entryname,"NXentry")
            #===================================================================
            
        self.fd.opengroup(self.entryname,"NXentry") 
        
        
        #adapt the datadesc to the NeXus requirements
        self.datadesc = []
        for dd in env['datadesc']:
            dd = dd.clone()
            dd.label = self.sanitizeName(dd.label)
            if dd.dtype == 'bool':
                dd.dtype = 'int8'
                self.debug('%s will be stored with type=%s',dd.name,dd.dtype)
            if dd.dtype in self.supported_dtypes:
                self.datadesc.append(dd)
            else:
                self.warning('%s will not be stored. Reason: type %s not supported',dd.name,dd.dtype)
                        
        #make a dictionary out of env['instrumentlist'] (use fullnames -paths- as keys)
        self.instrDict={}
        for inst in env.get('instrumentlist',[]):
            self.instrDict[inst.getFullName()]=inst
        if self.instrDict is {}:
            self.warning("missing information on NEXUS structure. Nexus Tree won't be created")
        
        self.debug("starting new recording %d on file %s", env['serialno'], self.filename)

        #populate the entry with some data
        self._writeData('definition', 'NXscan', 'char') #this is the Application Definition for NeXus Generic Scans
        import sardana.release
        program_name = "%s (%s)"%(sardana.release.name, self.__class__.__name__)
        self._writeData('program_name', program_name, 'char', attrs={'version':sardana.release.version})
        self._writeData("start_time",env['starttime'].isoformat(),'char') #note: the type should be NX_DATE_TIME, but the nxs python api does not recognize it
        self.fd.putattr("epoch",time.mktime(env['starttime'].timetuple()))
        self._writeData("title",env['title'],'char')
        self._writeData("entry_identifier",str(env['serialno']),'char')
        self.fd.makegroup("user","NXuser") #user data goes in a separate group following NX convention...
        self.fd.opengroup("user","NXuser")
        self._writeData("name",env['user'],'char')
        self.fd.closegroup()
        
        #prepare the "measurement" group
        self._createBranch("measurement:NXcollection")
        if self.savemode==SaveModes.Record:
            #create extensible datasets
            for dd in self.datadesc:
                self._makedata(dd.label,dd.dtype, [nxs.UNLIMITED]+list(dd.shape), chunks=[1]+list(dd.shape)) #the first dimension is extensible
                if hasattr(dd,'data_units'):
                    self.fd.opendata(dd.label)
                    self.fd.putattr('units', dd.data_units)
                    self.fd.closedata()
                    
        else:
            #leave the creation of the datasets to _writeRecordList (when we actually know the length of the data to write)
            pass
        
        self._createPreScanSnapshot(env)
            
        self.fd.flush()
    
    def _createPreScanSnapshot(self, env):
        #write the pre-scan snapshot in the "measurement:NXcollection/pre_scan_snapshot:NXcollection" group
        self.preScanSnapShot = env.get('preScanSnapShot',[])
        self._createBranch('measurement:NXcollection/pre_scan_snapshot:NXcollection')
        links = {}
        for dd in self.preScanSnapShot: #desc is a ColumnDesc object
            label = self.sanitizeName(dd.label)
            dtype = dd.dtype
            pre_scan_value = dd.pre_scan_value
            if dd.dtype == 'bool':
                dtype = 'int8'
                pre_scan_value = numpy.int8(dd.pre_scan_value)
                self.debug('Pre-scan snapshot of %s will be stored with type=%s',dd.name, dtype)
            if dtype in self.supported_dtypes:
                nid = self._writeData(label, pre_scan_value, dtype, shape=dd.shape or (1,)) #@todo: fallback shape is hardcoded!
                links[label] = nid
            else:
                self.warning('Pre-scan snapshot of %s will not be stored. Reason: type %s not supported',dd.name, dtype)
                
        self.fd.closegroup() #we are back at the measurement group
        
        measurement_entries = self.fd.getentries()
        for label,nid in links.items():
            if label not in measurement_entries:
                self.fd.makelink(nid)
         
    def _writeRecord(self, record):
        if self.filename is None:
            return
        # most used variables in the loop
        fd, debug, warning = self.fd, self.debug, self.warning
        nparray, npshape = numpy.array, numpy.shape
        rec_data, rec_nb = record.data, record.recordno
        
        for dd in self.datadesc:
            if record.data.has_key( dd.name ):
                data = rec_data[dd.name]
                fd.opendata(dd.label)
                
                if data is None:
                    data = numpy.zeros(dd.shape, dtype=dd.dtype)
                if not hasattr(data, 'shape'):
                    data = nparray([data], dtype=dd.dtype)
                elif dd.dtype != data.dtype.name:
                    debug('%s casted to %s (was %s)', dd.label, dd.dtype,
                                                      data.dtype.name)
                    data = data.astype(dd.dtype)
                    
                slab_offset = [rec_nb]+[0]*len(dd.shape)
                shape = [1]+list(npshape(data))
                try:
                    fd.putslab(data, slab_offset, shape)
                except:
                    warning("Could not write <%s> with shape %s", data, shape)
                    raise
                    
                ###Note: the following 3 lines of code were substituted by the one above.
                ###      (now we trust the datadesc info instead of asking the nxs file each time)
                #shape,dtype=self.fd.getinfo()
                #shape[0]=1 #the shape of the record is of just 1 slab in the extensible dimension (first dim)
                #self.fd.putslab(record.data[lbl],[record.recordno]+[0]*(len(shape)-1),shape)
                fd.closedata()
            else:
                debug("missing data for label '%s'", dd.label)
        fd.flush()

    def _endRecordList(self, recordlist):

        if self.filename is None:
            return
        
        self._populateInstrumentInfo()
        self._createNXData()
        
        env=self.currentlist.getEnviron()
        self.fd.openpath("/%s:NXentry" % self.entryname)
        self._writeData("end_time",env['endtime'].isoformat(),'char')
        self.fd.flush()
        self.debug("Finishing recording %d on file %s:", env['serialno'], self.filename)
        #self.fd.show('.') #prints nexus file summary on stdout (only the current entry)
        self.fd.close()
        self.currentlist = None

    def writeRecordList(self, recordlist):
        """Called when in BLOCK writing mode"""
        self._startRecordList( recordlist )
        for dd in self.datadesc:
            self._makedata(dd.label, dd.dtype, [len(recordlist.records)]+list(dd.shape), chunks=[1]+list(dd.shape))
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

    def _populateInstrumentInfo(self):
        measurementpath = "/%s:NXentry/measurement:NXcollection"%self.entryname
        #create a link for each
        for dd in self.datadesc:
            if getattr(dd,'instrument', None): #we don't link if it is None or it is empty
                try:
                    datapath="%s/%s"%(measurementpath,dd.label) 
                    self.fd.openpath(datapath)
                    nid=self.fd.getdataID()
                    self._createBranch(dd.instrument)
                    self.fd.makelink(nid)
                except Exception,e:
                    self.warning("Could not create link to '%s' in '%s'. Reason: %s",datapath, dd.instrument, repr(e))
                    
        for dd in self.preScanSnapShot:
            if getattr(dd,'instrument', None):
                try:
                    label = self.sanitizeName(dd.label)
                    datapath="%s/pre_scan_snapshot:NXcollection/%s"%(measurementpath,label)
                    self.fd.openpath(datapath)
                    nid=self.fd.getdataID()
                    self._createBranch(dd.instrument)
                    self.fd.makelink(nid)
                except Exception,e:
                    self.warning("Could not create link to '%s' in '%s'. Reason: %s",datapath, dd.instrument, repr(e))
                
    def _createNXData(self):
        '''Creates groups of type NXdata by making links to the corresponding datasets 
        '''        
        #classify by type of plot:
        plots1d = {}
        plots1d_names = {}
        i = 1
        for dd in self.datadesc:
            ptype = getattr(dd, 'plot_type', PlotType.No)
            if ptype == PlotType.No:
                continue
            elif ptype == PlotType.Spectrum:
                axes = ":".join(dd.plot_axes) #converting the list into a colon-separated string
                if axes in plots1d:
                    plots1d[axes].append(dd)
                else:
                    plots1d[axes] = [dd]
                    plots1d_names[axes] = 'plot_%i'%i #Note that datatesc ordering determines group name indexing
                    i+=1
            else:
                continue  #@todo: implement support for images and other
        
        #write the 1D NXdata group
        for axes,v in plots1d.items():
            self.fd.openpath("/%s:NXentry"%(self.entryname))
            groupname = plots1d_names[axes]
            self.fd.makegroup(groupname,'NXdata')
            #write the signals
            for i,dd in enumerate(v):
                src = "/%s:NXentry/measurement:NXcollection/%s"%(self.entryname,dd.label)
                dst = "/%s:NXentry/%s:NXdata"%(self.entryname,groupname)
                self._nxln(src, dst)
                self.fd.opendata(dd.label)
                self.fd.putattr('signal',min(i+1,2))
                self.fd.putattr('axes',axes)
                self.fd.putattr('interpretation','spectrum')
            #write the axes
            for axis in axes.split(':'):
                src = "/%s:NXentry/measurement:NXcollection/%s"%(self.entryname,axis)
                dst = "/%s:NXentry/%s:NXdata"%(self.entryname,groupname)
                try:
                    self._nxln(src, dst)
                except:
                    self.warning("cannot create link for '%s'. Skipping",axis)
                    
    def _addCustomData(self, value, name, nxpath=None, dtype=None, **kwargs):
        '''
        apart from value and name, this recorder can use the following optional parameters:
        
        :param nxpath: (str) a nexus path (optionally using name:nxclass notation for
                       the group names). See the rules for automatic nxclass
                       resolution used by
                       :meth:`NXscan_FileRecorder._createBranch`.
                       If None given, it defaults to 
                       nxpath='custom_data:NXcollection'
                       
        :param dtype: name of data type (it is inferred from value if not given)
                       
        '''           
        if nxpath is None:
            nxpath='custom_data:NXcollection'
        if dtype is None:
            if numpy.isscalar(value):
                dtype = numpy.dtype(type(value)).name
                if numpy.issubdtype(dtype,str):
                    dtype='char'
                if dtype == 'bool':
                    value, dtype = int(value), 'int8' 
            else:
                value = numpy.array(value)
                dtype = value.dtype.name
            
        if dtype not in self.supported_dtypes and dtype != 'char':
            self.warning("cannot write '%s'. Reason: unsupported data type",name)
            return
        #open the file if necessary 
        fileWasClosed = self.fd is None or not self.fd.isopen
        if fileWasClosed:
            if not self.overwrite and os.path.exists(self.filename): nxfilemode='rw'
            import nxs
            self.fd = nxs.open(self.filename, nxfilemode)
        #write the data
        self._createBranch(nxpath)
        try:
            self._writeData(name, value, dtype)
        except ValueError, e:
            msg = "Error writing %s. Reason: %s"%(name, str(e))
            self.warning(msg)
            self.macro.warning(msg)
        #leave the file as it was
        if fileWasClosed:
            self.fd.close()
        
            
class NXxas_FileRecorder(BaseNEXUS_FileRecorder):
    """saves data to a nexus file that follows the NXsas application definition
    
        """
        
    def __init__(self, filename=None, macro=None, overwrite=False, **pars):
        BaseNEXUS_FileRecorder.__init__(self, filename=filename, macro=macro, overwrite=overwrite, **pars)
        
        
    def _startRecordList(self, recordlist):
        nxs = self.nxs
        if self.filename is None:
            return
        
        #get the recordlist environment
        self.currentlist = recordlist
        env = self.currentlist.getEnviron()
        
        #adapt the datadesc to the NeXus requirements
        self.datadesc = []
        for dd in env['datadesc']:
            dd = dd.clone()
            dd.label = self.sanitizeName(dd.label)
            if dd.dtype == 'bool':
                dd.dtype = 'int8'
                self.debug('%s will be stored with type=%s',dd.name,dd.dtype)
            if dd.dtype in self.supported_dtypes:
                self.datadesc.append(dd)
            else:
                self.warning('%s will not be stored. Reason: type %s not supported',dd.name,dd.dtype)
        
        
        serialno = env["serialno"]
        nxfilemode = self.getFormat()
        if not self.overwrite and os.path.exists(self.filename): nxfilemode='rw'               
        
        self.debug("starting new recording %d on file %s", serialno, self.filename)
        
        #create an nxentry and write it to file
        self.nxentry = nxs.NXentry(name= "entry%d" % serialno)
        self.nxentry.save(self.filename, format=nxfilemode)

        #add fields to nxentry
        import sardana.release
        program_name = "%s (%s)"%(sardana.release.name, self.__class__.__name__)
        self.nxentry.insert(nxs.NXfield(name='start_time', value=env['starttime'].isoformat()))
        self.nxentry.insert(nxs.NXfield(name='title', value=env['title']))
        self.nxentry.insert(nxs.NXfield(name='definition', value='NXxas'))
        self.nxentry.insert(nxs.NXfield(name='epoch', value=time.mktime(env['starttime'].timetuple())))
        self.nxentry.insert(nxs.NXfield(name='program_name', value=program_name, attrs={'version':sardana.release.version}))
        self.nxentry.insert(nxs.NXfield(name='entry_identifier', value=env['serialno']))
                
        #add the "measurement" group (a NXcollection containing all counters from the mntgrp for convenience) 
        measurement = nxs.NXcollection(name='measurement')
        self.ddfieldsDict = {}
        for dd in self.datadesc:
            field = NXfield_comp(name=dd.label, 
                                 dtype=dd.dtype, 
                                 shape=[nxs.UNLIMITED]+list(dd.shape), 
                                 nxslab_dims=[1]+list(dd.shape)
                                 )
            if hasattr(dd,'data_units'):
                field.attrs['units'] = dd.data_units
            measurement.insert(field)
            #create a dict of fields in the datadesc for easier access later on
            self.ddfieldsDict[dd.label] = field
        
        self.nxentry.insert(measurement)
        
        #user group
        nxuser = nxs.NXuser()
        self.nxentry.insert(nxuser)
        nxuser['name'] = env['user']

        #sample group
        nxsample = nxs.NXsample()
        self.nxentry.insert(nxsample)
        nxsample['name'] = env['SampleInfo'].get('name','Unknown')
        
        #monitor group
        scan_acq_time = env.get('integ_time')
        scan_monitor_mode = scan_acq_time>1 and 'timer' or 'monitor'
        nxmonitor = nxs.NXmonitor(mode=scan_monitor_mode,
                        preset=scan_acq_time)
        self.nxentry.insert(nxmonitor)
        monitor_data = self.ddfieldsDict[self.sanitizeName(env['monitor'])] #to be linked later on
        
        #instrument group
        nxinstrument = nxs.NXinstrument()
        self.nxentry.insert(nxinstrument)
        
        #monochromator  group
        nxmonochromator = nxs.NXmonochromator()
        nxinstrument.insert(nxmonochromator)
        energy_data = self.ddfieldsDict[self.sanitizeName(env['monochromator'])] #to be linked later on
        
        #incoming_beam  group
        nxincoming_beam = nxs.NXdetector(name='incoming_beam')
        nxinstrument.insert(nxincoming_beam)
        incbeam_data = self.ddfieldsDict[self.sanitizeName(env['incbeam'])] #to be linked later on
        
        #absorbed_beam  group
        nxabsorbed_beam = nxs.NXdetector(name='absorbed_beam')
        nxinstrument.insert(nxabsorbed_beam)
        absbeam_data = self.ddfieldsDict[self.sanitizeName(env['absbeam'])] #to be linked later on
        absbeam_data.attrs['signal'] = '1'
        absbeam_data.attrs['axes'] = 'energy'
        
        #source group
        nxsource = nxs.NXsource()
        nxinstrument.insert(nxsource) 
        nxinstrument['source']['name'] = env.get('SourceInfo',{}).get('name','Unknown')
        nxinstrument['source']['type'] = env.get('SourceInfo',{}).get('type','Unknown')
        nxinstrument['source']['probe'] = env.get('SourceInfo',{}).get('x-ray','Unknown')
        
        #data group
        nxdata = nxs.NXdata()
        self.nxentry.insert(nxdata)
        
        
        #@todo create the PreScanSnapshot
        #self._createPreScanSnapshot(env)   
        
        #write everything to file
        self.nxentry.write() 
        
        #@todo: do this with the PyTree api instead(how to do named links with the PyTree API????)
        self._nxln(monitor_data, nxmonitor, name='data')
        self._nxln(incbeam_data, nxincoming_beam, name='data')
        self._nxln(absbeam_data, nxabsorbed_beam, name='data')
        self._nxln(energy_data, nxmonochromator, name='energy')
        self._nxln(energy_data, nxdata, name='energy')
        self._nxln(absbeam_data, nxdata, name='absorbed_beam')
                
        self.nxentry.nxfile.flush()
        
    
    def _writeRecord(self, record):
        # most used variables in the loop
        fd, debug, warning = self.nxentry.nxfile, self.debug, self.warning
        nparray, npshape = numpy.array, numpy.shape
        rec_data, rec_nb = record.data, record.recordno
                
        for dd in self.datadesc:
            if record.data.has_key( dd.name ):
                data = rec_data[dd.name]
                field = self.ddfieldsDict[dd.label]
                
                if data is None:
                    data = numpy.zeros(dd.shape, dtype=dd.dtype)
                if not hasattr(data, 'shape'):
                    data = nparray([data], dtype=dd.dtype)
                elif dd.dtype != data.dtype.name:
                    debug('%s casted to %s (was %s)', dd.label, dd.dtype,
                                                      data.dtype.name)
                    data = data.astype(dd.dtype)
                    
                slab_offset = [rec_nb]+[0]*len(dd.shape)
                shape = [1]+list(npshape(data))
                try:
                    field.put(data, slab_offset, shape)
                    field.write()
                except:
                    warning("Could not write <%s> with shape %s", data, shape)
                    raise
            else:
                debug("missing data for label '%s'", dd.label)
        self.nxentry.nxfile.flush()


    def _endRecordList(self, recordlist):
        env=self.currentlist.getEnviron()
        self.nxentry.insert(nxs.NXfield(name='end_time', value=env['endtime'].isoformat()))
        #self._populateInstrumentInfo()
        #self._createNXData()
        self.nxentry.write()
        self.nxentry.nxfile.flush()
        self.debug("Finishing recording %d on file %s:", env['serialno'], self.filename)
        return
        


#===============================================================================
# BEGIN: THIS BLOCK SHOULD BE REMOVED IF NEXUS ACCEPTS THE PATCH TO NXfield
#===============================================================================
try:
    from nxs import NXfield #needs Nexus v>=4.3
    from nxs import napi, NeXusError
    
    class NXfield_comp(NXfield):
        
        #NOTE: THE CONSTRUCTOR IS OPTIONAL. IF NOT IMPLEMENTED, WE CAN STILL USE THE nxslab_dims PROPERTY
        def __init__(self, value=None, name='field', dtype=None, shape=(), group=None,
                     attrs={}, nxslab_dims=None, **attr):
            NXfield.__init__(self, value=value, name=name, dtype=dtype, shape=shape, group=group,
                     attrs=attrs, **attr)
            self._slab_dims = nxslab_dims
            
        def write(self):
            """
            Write the NXfield, including attributes, to the NeXus file.
            """
            if self.nxfile:
                if self.nxfile.mode == napi.ACC_READ:
                    raise NeXusError("NeXus file is readonly")
                if not self.infile:
                    shape = self.shape
                    if shape == (): shape = (1,)
                    with self.nxgroup as path:
                        if self.nxslab_dims is not None:
                        #compress
                            path.compmakedata(self.nxname, self.dtype, shape, 'lzw', 
                                              self.nxslab_dims)
                        else:
                        # Don't use compression
                            path.makedata(self.nxname, self.dtype, shape)
                    self._infile = True
                if not self.saved:            
                    with self as path:
                        path._writeattrs(self.attrs)
                        value = self.nxdata
                        if value is not None:
                            path.putdata(value)
                    self._saved = True
            else:
                raise IOError("Data is not attached to a file")
        
        def _getnxslabdims(self):
            try:
                return self._nxslab_dims
            except:
                slab_dims = None
            #even if slab_dims have not been set, check if the dataset is large 
            shape = self.shape or (1,)
            if numpy.prod(shape) > 10000:
                slab_dims = numpy.ones(len(shape),'i')
                slab_dims[-1] = min(shape[-1], 100000)
            return slab_dims
        
        def _setnxslabdims(self, slab_dims):
            self._nxslab_dims = slab_dims
        
        nxslab_dims = property(_getnxslabdims,_setnxslabdims,doc="Slab (a.k.a. chunk) dimensions for compression")
except:
    pass #NXxas_FileRecorder won't be usable


#===============================================================================
# END: THE ABOVE BLOCK SHOULD BE REMOVED IF NEXUS ACCEPTS THE PATCH TO NXfield
#===============================================================================


def FileRecorder(filename, macro, **pars):
    ext = os.path.splitext(filename)[1].lower() or '.spec'
    
    hintedklass = globals().get(getattr(macro,'hints',{}).get('FileRecorder',None))
    
    if hintedklass is not None and issubclass(hintedklass, BaseFileRecorder): 
        klass = hintedklass
    elif ext in NXscan_FileRecorder.formats.values():
        klass = NXscan_FileRecorder
    elif ext in FIO_FileRecorder.formats.values():
        klass = FIO_FileRecorder
    else:
        klass = SPEC_FileRecorder
    return klass(filename=filename, macro=macro, **pars)

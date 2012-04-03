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

import numpy

from datarecorder import DataRecorder, DataFormats, SaveModes
from taurus.core.tango.sardana import PlotType

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

    def getFormat(self):
        return DataFormats.whatis(DataFormats.fio)
    
    def _startRecordList(self, recordlist):
        
        if self.base_filename is None:
              return
        
        self.setFileName(self.base_filename)
        
        envRec = recordlist.getEnviron()

        #datetime object
        start_time = envRec['starttime']
        epoch = time.mktime(start_time.timetuple())
        serialno = envRec['serialno']
        
        #store labels for performace reason
        self.names = [ e.name for e in envRec['datadesc'] ]
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
            if col.name == 'point_nb':
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
        nan, names, fd = float('nan'), self.names, self.fd
        outstr = ''
        for c in names:
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

        try:
            import nxs  #check if Nexus data format is supported by this system
            self.nxs = nxs
        except ImportError:
            raise Exception("NeXus is not available")

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
        nxs = self.nxs
        nxfilemode = self.getFormat()
        
        if self.filename is None:
            return
        
        self.currentlist = recordlist
        env = self.currentlist.getEnviron()
        serialno = env["serialno"]
        
        if not self.overwrite and os.path.exists(self.filename): nxfilemode='rw'
        self.fd = nxs.open(self.filename, nxfilemode)
        #self.entryname=self._newentryname(prefix='entry')
        self.entryname = "entry%d" % serialno
        self.fd.makegroup(self.entryname,"NXentry") 
        self.fd.opengroup(self.entryname,"NXentry") 
        
        self.datadesc = env['datadesc']
        
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
        self.fd.makegroup("measurement","NXcollection")
        self.fd.opengroup("measurement","NXcollection")
        if self.savemode==SaveModes.Record:
            #create extensible datasets
            for dd in self.datadesc:
                self.fd.makedata(dd.label,dd.dtype, [nxs.UNLIMITED]+list(dd.shape)) #the first dimension is extensible
                if hasattr(dd,'data_units'):
                    self.fd.opendata(dd.label)
                    self.fd.putattr('units', dd.data_units)
                    self.fd.closedata()
                    
        else:
            #leave the creation of the datasets to _writeRecordList (when we actually know the length of the data to write)
            pass
        
        #write the pre-scan snapshot in the "measurement:NXcollection/preScanSnapShot:NXcollection" group
        self.preScanSnapShot = env.get('preScanSnapShot',[])
        self.fd.makegroup("pre_scan_snapshot","NXcollection")
        self.fd.opengroup("pre_scan_snapshot","NXcollection")
        for desc in self.preScanSnapShot: #desc is a ColumnDesc object
            self._writeData(desc.label, desc.pre_scan_value, desc.dtype, desc.shape or (1,)) #@todo: fallback shape is hardcoded! 
        self.fd.closegroup()
        
        self.fd.flush()
        
    def _writeData(self, name, data, dtype, shape=None, attrs=None):
        if shape is None:
            if dtype=='char': 
                shape=[len(data)]
            else:
                shape = getattr(data,'shape',[1])
        self.fd.makedata(name, dtype, shape)
        self.fd.opendata(name)
        self.fd.putdata(data)
        if attrs is not None:
            for k,v in attrs.items():
                self.fd.putattr(k,v)
        self.fd.closedata()

    def _writeRecord(self, record):
        if self.filename is None:
            return
        for dd in self.datadesc:
            if record.data.has_key( dd.name ):
                data = record.data[dd.name]
                self.fd.opendata(dd.label)
                
                if not hasattr(data, 'shape'):
                    data = numpy.array([data], dtype=dd.dtype)
                slab_offset = [record.recordno]+[0]*len(dd.shape)
                shape = [1]+list(numpy.shape(data))
                try:
                    self.fd.putslab(data,slab_offset,shape)
                except:
                    self.warning("Could not write <%s> with shape %s", data, shape)
                    raise
                    
                ###Note: the following 3 lines of code were substituted by the one above.
                ###      (now we trust the datadesc info instead of asking the nxs file each time)
                #shape,dtype=self.fd.getinfo()
                #shape[0]=1 #the shape of the record is of just 1 slab in the extensible dimension (first dim)
                #self.fd.putslab(record.data[lbl],[record.recordno]+[0]*(len(shape)-1),shape)
                self.fd.closedata()
            else:
                self.debug("missing data for label '%s'", dd.label)
        self.fd.flush()

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
    
    def _populateInstrumentInfo(self):
        #create the link for each set in <entry>/data that has a datadesc.nxpath
        for dd in self.datadesc:
            if getattr(dd,'instrument', None): #we don't link if it is None or it is empty
                #grab the ID of the data group
                datapath="/%s:NXentry/measurement:NXcollection/%s"%(self.entryname,dd.label) 
                self.fd.openpath(datapath)
                id=self.fd.getdataID()
                self._createBranch(dd.instrument)
                self.fd.makelink(id)
                
        for dd in self.preScanSnapShot:
            if getattr(dd,'instrument', None):
                datapath="/%s:NXentry/measurement:NXcollection/pre_scan_snapshot:NXcollection/%s"%(self.entryname,dd.label)
                self.fd.openpath(datapath)
                id=self.fd.getdataID()
                self._createBranch(dd.instrument)
                self.fd.makelink(id)
                
    def _createNXData(self):
        '''Creates groups of type NXdata by making links to the corresponding datasets 
        '''        
        #classify by type of plot:
        plots1d = {}
        plots1d_names = {}
        i = 1
        for dd in self.datadesc:
            print dd.label, getattr(dd, 'plot_type','---')
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
                
    def _nxln(self, src, dst):
        '''convenience function to create NX links with just one call. On successful return, dst will be open.
        
        :param src: (str) the nxpath to the source group or dataset
        :param dst: (str) the nxpath to the group that will hold the link
        
        .. note:: `groupname:nxclass` notation can be used for both paths for better performance
        '''
        self.fd.openpath(src)
        try:
            id=self.fd.getdataID()
        except NeXusError:
            id=self.fd.getgroupID()
        self.fd.openpath(dst)
        self.fd.makelink(id)
            
    def _createBranch(self, path):
        """navigates the nexus tree starting in the current <entry> and finishing in <entry>/path.
        It creates the groups if they do not exist, using the class info in self.instrDict
        If successful, path is left open"""
        groups=path.split('/')
        self.fd.openpath("/%s:NXentry" % self.entryname)
        relpath="" #the current path relative to <entry>, to use as a key for instrDict
        for g in groups:
            if len(g) == 0:
                continue
            relpath = relpath + "/"+ g
            try:
                group_type = self.instrDict[relpath].klass
            except:
                group_type = 'NXcollection'
            try:
                self.fd.opengroup(g, group_type)
            except:
                self.fd.makegroup(g, group_type)
                self.fd.opengroup(g, group_type)


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
            if e.shape == ():
                labels.append(e.label)
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


def FileRecorder(filename, macro, **pars):
    ext = os.path.splitext(filename)[1].lower() or '.spec'

    if ext in NEXUS_FileRecorder.formats.values():
        klass = NEXUS_FileRecorder
    elif ext in FIO_FileRecorder.formats.values():
        klass = FIO_FileRecorder
    else:
        klass = SPEC_FileRecorder
    return klass(filename=filename, macro=macro, **pars)

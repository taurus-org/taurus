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

"""This module contains the class definition for the MacroServer generic
scan"""

__all__ = ["ScanSetupError", "ScanException", "ExtraData", "TangoExtraData",
           "GScan", "SScan", "CScan", "CSScan", "CTScan", "HScan"]

__docformat__ = 'restructuredtext'

import os
import datetime
import operator
import time
import threading
import numpy as np

import PyTango
import taurus
from taurus.core.util.user import USER_NAME
from taurus.core.util.log import Logger
from taurus.core.tango import FROM_TANGO_TO_STR_TYPE
from taurus.core.tango.sardana.pool import Ready

from sardana.util.tree import BranchNode, LeafNode, Tree
from sardana.util.motion import Motor as VMotor
from sardana.util.motion import MotionPath
from sardana.macroserver.msexception import MacroServerException, UnknownEnv, \
    InterruptException
from sardana.macroserver.msparameter import Type
from scandata import ColumnDesc, MoveableDesc, ScanFactory, ScanDataEnvironment
from recorder import OutputRecorder, JsonRecorder, SharedMemoryRecorder, \
    FileRecorder

class ScanSetupError(Exception): pass

class ScanException(MacroServerException): pass

class ExtraData(object):
    
    def __init__(self, **kwargs):
        """Expected keywords are:
            - model (str, mandatory): represents data source (ex.: a/b/c/d)
            - label (str, mandatory): column label
            - name (str, optional): unique name (defaults to model)
            - shape (seq, optional): data shape 
            - dtype (numpy.dtype, optional): data type
            - instrument (str, optional): full instrument name"""
        self._label = kwargs['label']
        self._model = kwargs['model']
        if not kwargs.has_key('dtype'):
            kwargs['dtype'] = self.getType()
        if not kwargs.has_key('shape'):
            kwargs['shape'] = self.getShape()
        if not kwargs.has_key('name'):
            kwargs['name'] = self._model
        self._column = ColumnDesc(**kwargs)
    
    def getLabel(self):
        return self._label

    def getName(self):
        return self._label
    
    def getColumnDesc(self):
        return self._column
    
    def getType(self):
        raise Exception("Must be implemented in subclass")
    
    def getShape(self):
        raise Exception("Must be implemented in subclass")

    def read(self):
        raise Exception("Must be implemented in subclass")


class TangoExtraData(ExtraData):
    
    def __init__(self, **kwargs):
        self._attribute = None
        ExtraData.__init__(self, **kwargs)
    
    @property
    def attribute(self):
        if self._attribute is None:
            self._attribute = taurus.Attribute(self._model)
        return self._attribute
        
    def getType(self):
        t = self.attribute.getType()
        if t is None:
            raise Exception("Could not determine type for unknown attribute '%s'" % self._model)
        return FROM_TANGO_TO_STR_TYPE[t]
    
    def getShape(self):
        s = self.attribute.getShape()
        if s is None:
            raise Exception("Could not determine type for unknown attribute '%s'" % self._model)
        return s

    def read(self):
        try:
            return self.attribute.read(cache=False).value
        except InterruptException:
            raise
        except Exception:
            return None


class GScan(Logger):
    """Generic Scan object. 
    The idea is that the scan macros create an instance of this Generic Scan, 
    supplying in the constructor a reference to the macro that created the scan,
    a generator function pointer, a list of moveable items, an extra 
    environment and a sequence of constrains.
    
    If the referenced macro is hookable, 'pre-scan' and 'post-scan' hook hints
    will be used to execute callables before the start and after the end of the
    scan, respectively
    
    The generator must be a function yielding a dictionary with the following
    content (minimum) at each step of the scan:
      - 'positions'  : In a step scan, the position where the moveables should go
      - 'integ_time' : In a step scan, a number representing the integration time for the step 
                     (in seconds)
      - 'integ_time' : In a continuous scan, the time between acquisitions
      - 'pre-move-hooks' : (optional) a sequence of callables to be called in strict order before starting to move.
      - 'post-move-hooks': (optional) a sequence of callables to be called in strict order after finishing the move.
      - 'pre-acq-hooks'  : (optional) a sequence of callables to be called in strict order before starting to acquire.
      - 'post-acq-hooks' : (optional) a sequence of callables to be called in strict order after finishing acquisition but before recording the step.
      - 'post-step-hooks' : (optional) a sequence of callables to be called in strict order after finishing recording the step.
      - 'hooks' : (deprecated, use post-acq-hooks instead)
      - 'point_id' : a hashable identifing the scan point.
      - 'check_func' : (optional) a list of callable objects. callable(moveables, counters)
      - 'extravalues': (optional) a dictionary containing the values for each extra info
                       field. The extra information fields must be described in
                       extradesc (passed in the constructor of the Gscan) 
    
    
    The moveables must be a sequence Motion or MoveableDesc objects.
    
    The environment is a dictionary of extra environment to be added specific
    to the macro in question.
    
    Each constrain must be a callable which must receive a two parameters: the 
    current point and the next point. It should return True or False
    
    The extradesc optional argument consists of a list of ColumnDesc objects
    which describe the data fields that will be filled using step['extravalues'],
    where step is what the generator yields.
    
    The Generic Scan will create:
      - a ScanData
      - DataHandler with the following recorders:
        - OutputRecorder (depends on 'OutputCols' environment variable)
        - SharedMemoryRecorder (depends on 'SharedMemory' environment variable)
        - FileRecorder (depends on 'ScanDir' and 'ScanData' environment variables)
      - ScanDataEnvironment with the following contents:
        - 'serialno' : a integer identifier for the scan operation
        - 'user' : the user which started the scan
        - 'title' : the scan title (build from macro.getCommand)
        - 'datadesc' : a seq<ColumnDesc> describing each column of data 
                     (labels, data format, data shape, etc)
        - 'estimatedtime' : a float representing an estimation for 
                          the duration of the scan (in seconds). Negative means
                          the time estimation is known not to be accurate. Anyway,
                          time estimation has 'at least' semantics.
        - 'total_scan_intervals' : total number of scan intervals. Negative means
                                   the estimation is known not to be accurate. In
                                   this case, estimation has 'at least' semantics.
        - '' : a datetime.datetime representing the start of the scan
        - 'instrumentlist' : a list of Instrument objects containing info
                            about the physical setup of the motors, counters,...
        - <extra environment> given in the constructor
        (at the end of the scan, extra keys 'endtime' and 'deadtime' will be added
        representing the time at the end of the scan and the dead time)

        This object is passed to all recorders at the beginning and at the end 
        of the scan (when startRecordList and endRecordList is called)
    
    At each step of the scan, for each Recorder, the writeRecord method will
    be called with a Record object as parameter. The Record.data member will be
    a dictionary containing:
      - 'point_nb' : the point number of the scan
      - for each column of the scan (motor or counter), a key with the 
      corresponding column name will contain the value"""
    
    MAX_SCAN_HISTORY = 20
    
    env = ('ActiveMntGrp', 'ExtraColumns' 'ScanDir', 'ScanFile', 'SharedMemory', 'OutputCols')
    
    def __init__(self, macro, generator=None, moveables=[], env={}, constraints=[], extrainfodesc=[]):
        self._macro = macro
        self._generator = generator
        self._extrainfodesc = extrainfodesc
        
        #nasty hack to make sure macro has access to gScan as soon as possible 
        self._macro._gScan = self #TODO: CAUTION! this may be causing a circular reference! 
        
        self._moveables, moveable_names = [], []
        for moveable in moveables:
            if not isinstance(moveable, MoveableDesc):
                moveable = MoveableDesc(moveable=moveable)
            moveable_names.append(moveable.moveable.getName())
            self._moveables.append(moveable)
        
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        
        # ----------------------------------------------------------------------
        # Setup motion objects
        # ----------------------------------------------------------------------
        self._motion = macro.getMotion(moveable_names)

        # ----------------------------------------------------------------------
        # Find the measurement group
        # ----------------------------------------------------------------------
        try:
            mnt_grp_name = macro.getEnv('ActiveMntGrp')
        except UnknownEnv:
            mnt_grps = macro.getObjs(".*", type_class=Type.MeasurementGroup)
            if len(mnt_grps) == 0:
                ScanSetupError('No Measurement Group defined')
            mnt_grp = mnt_grps[0]
            macro.info("ActiveMntGrp not defined. Using %s", mnt_grp)
            macro.setEnv('ActiveMntGrp', mnt_grp.getName())
        else:
            if not isinstance(mnt_grp_name, (str, unicode)):
                t = type(mnt_grp_name).__name__
                raise TypeError("ActiveMntGrp MUST be string. It is '%s'" % t)

            mnt_grp = macro.getObj(mnt_grp_name,
                                   type_class=Type.MeasurementGroup)

        if mnt_grp is None:
            raise ScanSetupError("ActiveMntGrp has invalid value: '%s'"
                                 % mnt_grp_name)

        self._master = mnt_grp.getTimer()

        if self._master is None:
            raise ScanSetupError('%s has no timer defined' % mnt_grp.getName())
        
        self._measurement_group = mnt_grp
        
        # ----------------------------------------------------------------------
        # Setup extra columns
        # ----------------------------------------------------------------------
        self._extra_columns = self._getExtraColumns()
        
        # ----------------------------------------------------------------------
        # Setup data management
        # ----------------------------------------------------------------------
        
        # Generate data handler
        data_handler = ScanFactory().getDataHandler()
        
        # The Scan data object
        data = ScanFactory().getScanData(data_handler)

        # The Output recorder (if any)
        output_recorder = self._getOutputRecorder()

        # The Output recorder (if any)
        json_recorder = self._getJsonRecorder()
        
        # The File recorders (if any)
        file_recorders = self._getFileRecorders()
        
        # The Shared memory recorder (if any)
        shm_recorder = self._getSharedMemoryRecorder(0)
        shm_recorder_1d = None
        if shm_recorder is not None:
            shm_recorder_1d = self._getSharedMemoryRecorder(1)
        
        data_handler.addRecorder(output_recorder)
        data_handler.addRecorder(json_recorder)
        for file_recorder in file_recorders:
            data_handler.addRecorder(file_recorder)
        data_handler.addRecorder(shm_recorder)
        data_handler.addRecorder(shm_recorder_1d)
        
        self._data = data
        self._data_handler = data_handler
                
        # ----------------------------------------------------------------------
        # Setup environment
        # ----------------------------------------------------------------------
        self._setupEnvironment(env)

    def _getExtraColumns(self):
        ret = []
        try:
            cols = self.macro.getEnv('ExtraColumns')
        except InterruptException:
            raise
        except:
            self.info('ExtraColumns is not defined')
            return ret
        
        try:
            for i, kwargs in enumerate(cols):
                kw = dict(kwargs)
                try:
                    if kw.has_key('instrument'):
                        instrument = self._macro.getObj(kw['instrument'],
                            type_class=Type.Instrument)
                        if instrument:
                            kw['instrument'] = instrument
                    ret.append(TangoExtraData(**kw))
                except InterruptException:
                    raise
                except Exception, colexcept:
                    colname = kw.get('label', str(i))
                    self.macro.warning("Extra column %s is invalid: %s",
                                       colname, str(colexcept))
        except InterruptException:
            raise
        except Exception:
            self.macro.warning('ExtraColumns has invalid value. Must be a '
                               'sequence of maps')
        return ret

    def _getJsonRecorder(self):
        try:
            json_enabled = self.macro.getEnv('JsonRecorder')
            if json_enabled:
                return JsonRecorder(self.macro)
        except InterruptException:
            raise
        except Exception:
            pass
        self.info('JsonRecorder is not defined. Use "senv JsonRecorder '
                  'True" to enable it')

    def _getOutputRecorder(self):
        cols = None
        try:
            cols = self.macro.getEnv('OutputCols')
        except InterruptException:
            raise
        except:
            pass
        return OutputRecorder(self.macro, cols=cols, number_fmt='%g')
    
    def _getFileRecorders(self):
        macro = self.macro
        try:
            scan_dir = macro.getEnv('ScanDir')
        except InterruptException:
            raise
        except Exception:
            macro.warning('ScanDir is not defined. This operation will not be '
                          'stored persistently. Use Use "expconf" (or "senv ScanDir '
                          '<abs directory>") to enable it')
            return ()
        
        if not isinstance(scan_dir, (str, unicode)):
            scan_dir_t = type(scan_dir).__name__
            raise TypeError("ScanDir MUST be string. It is '%s'" % scan_dir_t)
        
        try:
            file_names = macro.getEnv('ScanFile')
        except InterruptException:
            raise
        except Exception:
            macro.warning('ScanFile is not defined. This operation will not '
                          'be stored persistently. Use "expconf" (or "senv ScanDir <scan '
                          'file(s)>") to enable it')
            return ()

        if isinstance(file_names, (str, unicode)):
            file_names = (file_names,)
        elif not operator.isSequenceType(file_names):
            scan_file_t = type(file_names).__name__
            raise TypeError("ScanFile MUST be string or sequence of strings."\
                            " It is '%s'" % scan_file_t)
            
        file_recorders = []
        for file_name in file_names:
            abs_file_name = os.path.join(scan_dir, file_name)
            try:
                file_recorder = FileRecorder(abs_file_name, macro=macro)
                file_recorders.append(file_recorder)
            except InterruptException:
                raise
            except Exception:
                macro.warning("Error creating recorder for %s", abs_file_name)
                macro.debug("Details:", exc_info=1)
        
        if len(file_recorders) == 0:
            macro.warning("No valid recorder found. This operation will not be "
                          " stored persistently")
        return file_recorders
    
    def _getSharedMemoryRecorder(self, eid):
        macro, mg, shm = self.macro, self.measurement_group, False
        try:
            shm = macro.getEnv('SharedMemory')
        except InterruptException:
            raise
        except Exception:
            self.info('SharedMemory is not defined. Use "senv '
                      'SharedMemory sps" to enable it')
            return
        
        if not shm: 
            return
        
        kwargs = {}
        # For now we only support SPS shared memory format
        if shm.lower() == 'sps':
            cols  = 1                            # Point nb column
            cols += len(self.moveables)          # motor columns
            ch_nb = len(mg.getChannels())
            oned_nb = 0
            array_prefix = mg.getName().upper()
            
            try:
                oned_nb = len(mg.OneDExpChannels)
            except InterruptException:
                raise
            except:
                oned_nb = 0
            
            twod_nb = 0
            try:
                twod_nb = len(mg.TwoDExpChannels)
            except InterruptException:
                raise
            except:
                twod_nb = 0
            
            if eid == 0:
                cols += (ch_nb - oned_nb - twod_nb)    # counter/timer & 0D channel columns
            elif eid == 1:
                cols = 1024
                
            if eid == 0:
                kwargs.update({ 'program' : macro.getDoorName(),
                                  'array' : "%s_0D" % array_prefix,
                                  'shape' : (cols, 4096) } )
            elif eid == 1:
                if oned_nb == 0:
                    return
                else:
                    kwargs.update({ 'program' : macro.getDoorName(),
                                  'array' : "%s_1D" % array_prefix,
                                  'shape' : (cols, 99) } )
            
        shmRecorder = SharedMemoryRecorder(shm, **kwargs)
        if shmRecorder is None:
            self.info('SharedMemory %s is not available'%shm)
        return shmRecorder
    
    def _secsToTimedelta(self, secs):
        days, secs = divmod(secs, 86400)
        # we don't have to care about microseconds because if secs is a float
        # timedelta will do it for us
        return datetime.timedelta(days, secs)
    
    def _timedeltaToSecs(self, td):
        return 86400*td.days + td.seconds + 1E-6*td.microseconds
    
    def _setupEnvironment(self, additional_env):
        try:
            serialno = self.macro.getEnv("ScanID") + 1
        except UnknownEnv:
            serialno = 1
        self.macro.setEnv("ScanID", serialno)
            
        env = ScanDataEnvironment(
                { 'serialno' : serialno,
                      'user' : USER_NAME, #TODO: this should be got from self.measurement_group.getChannelsInfo()
                     'title' : self.macro.getCommand() } )
        
        # Initialize the data_desc list (and add the point number column)
        data_desc = [
            ColumnDesc(name='point_nb', label='#Pt No', dtype='int64')
        ]
        
        # add motor columns
        ref_moveables = []
        for moveable in self.moveables:
            data_desc.append(moveable)
            if moveable.is_reference:
                ref_moveables.insert(0, moveable.name)
        
        if not ref_moveables and len(self.moveables):
            ref_moveables.append(data_desc[-1].name)
        env['ref_moveables'] = ref_moveables
        
        # add master column
        master = self._master
        instrument = master['instrument']
        
        #add channels from measurement group
        channels_info = self.measurement_group.getChannelsInfo()
        counters = []
        for ci in channels_info:
            instrument = ci.instrument or ''
            try:
                instrumentFullName = self.macro.findObjs(instrument, type_class=Type.Instrument)[0].getFullName()
            except InterruptException:
                raise
            except:
                instrumentFullName = ''
            #substitute the axis placeholder by the corresponding moveable.
            plotAxes = []
            i = 0
            for a in ci.plot_axes:
                if a=='<mov>':
                    plotAxes.append(ref_moveables[i])
                    i+=1
                else: plotAxes.append(a)
                
            #create the ColumnDesc object
            column = ColumnDesc(name=ci.full_name,
                                label = ci.label,
                                dtype = ci.data_type,
                                shape = ci.shape,
                                instrument = instrumentFullName,
                                source = ci.source,
                                output = ci.output,
                                conditioning = ci.conditioning,
                                normalization = ci.normalization,
                                plot_type = ci.plot_type,
                                plot_axes = plotAxes,
                                data_units = ci.unit)
            data_desc.append(column)
            counters.append(column.name)
        counters.remove(master['full_name'])
        env['counters'] = counters
        
        for extra_column in self._extra_columns:
            data_desc.append(extra_column.getColumnDesc())
        # add extra columns 
        data_desc += self._extrainfodesc
        data_desc.append(ColumnDesc(name='timestamp', label='dt', dtype='float64'))
        
        env['datadesc'] = data_desc
        
        #set the data compression default
        try:
            env['DataCompressionRank'] = self.macro.getEnv('DataCompressionRank')
        except UnknownEnv:
            env['DataCompressionRank'] = -1
        
        #set the sample information
        #@todo: use the instrument API to get this info
        try: 
            env['SampleInfo'] = self.macro.getEnv('SampleInfo')
        except UnknownEnv:
            env['SampleInfo'] = {}
            
        #set the source information
        #@todo: use the instrument API to get this info
        try:
            env['SourceInfo'] = self.macro.getEnv('SourceInfo')
        except UnknownEnv:
            env['SourceInfo'] = {}
        
        #take the pre-scan snapshot
        try:
            preScanSnapShot = self.macro.getEnv('PreScanSnapshot')
        except UnknownEnv:
            preScanSnapShot = []
        env['preScanSnapShot'] = self.takeSnapshot(elements=preScanSnapShot)
        
        env['macro_id'] = self.macro.getID()
        try:
            env['ScanFile'] = self.macro.getEnv('ScanFile')
        except InterruptException:
            raise
        except:
            env['ScanFile'] = None
        try:
            env['ScanDir'] = self.macro.getEnv('ScanDir')
        except InterruptException:
            raise
        except:
            env['ScanDir'] = None
        env['estimatedtime'], env['total_scan_intervals'] = self._estimate()
        env['instrumentlist'] = self._macro.findObjs('.*', type_class=Type.Instrument) 

        #env.update(self._getExperimentConfiguration) #add all the info from the experiment configuration to the environment
        env.update(additional_env)
        self._env = env
        
        # Give the environment to the ScanData
        self.data.setEnviron(env)

    def takeSnapshot(self, elements=[]):
        '''reads the current values of the given elements
        
        :param elements: (list<str,str>) list of tuples of label,src for the elements to read
                         (can be pool elements or Taurus attribute names).
        
        :return: (list<ColumnDesc>) a list of :class:`ColumnDesc`, each including a 
                 "pre_scan_value" attribute with the read value for that attr
        '''
        manager = self.macro.getManager()
        all_elements_info = manager.get_elements_with_interface('Element')
        ret = []
        for src,label in elements:
            try:
                if src in all_elements_info:
                    ei = all_elements_info[src]
                    column = ColumnDesc(name=ei.full_name,
                                        label=label,
                                        instrument = ei.instrument,
                                        source = ei.source)
                else:
                    column = ColumnDesc(name=src,
                                        label=label,
                                        source=src)
                
                v = PyTango.AttributeProxy(column.source).read().value #@Fixme: Tango-centric. It should work for any Taurus Attribute
                column.pre_scan_value = v
                column.shape = np.shape(v)
                column.dtype = getattr(v, 'dtype', np.dtype(type(v))).name
                ret.append(column)
            except:
                self.macro.warning('Error taking pre-scan snapshot of %s (%s)',label,src)
                self.debug('Details:', exc_info=1)
        return ret

    def get_virtual_motors(self):
        ret = []
        for moveable in self.moveables:
            try:
                v_motor = VMotor.fromMotor(moveable.moveable)
            except:
                #self.debug("Details:", exc_info=1)
                v_motor = VMotor(min_vel=0, max_vel=float('+inf'),
                                 accel_time=0, decel_time=0)
            ret.append(v_motor)
        return ret

    MAX_ITER = 100000

    def _estimate(self, max_iter=None):
        with_time = hasattr(self.macro, "getTimeEstimation")
        with_interval = hasattr(self.macro, "getIntervalEstimation")
        if with_time and with_interval:
            t, i = self.macro.getTimeEstimation(), self.macro.getIntervalEstimation()
            return t, i
        
        max_iter = max_iter or self.MAX_ITER
        iterator = self.generator()
        total_time = 0.0
        interval_nb = 0
        try:
            if not with_time:
                start_pos = self.motion.readPosition(force=True)
                v_motors = self.get_virtual_motors()
                motion_time, acq_time = 0.0, 0.0
                while interval_nb < max_iter:
                    step = iterator.next()
                    end_pos = step['positions']
                    max_path_duration = 0.0
                    for v_motor, start, stop in zip(v_motors, start_pos, end_pos):
                        path = MotionPath(v_motor, start, stop)
                        max_path_duration = max(max_path_duration, path.duration)
                    integ_time = step.get("integ_time", 0.0)
                    acq_time += integ_time
                    motion_time += max_path_duration 
                    total_time += integ_time + max_path_duration
                    interval_nb += 1
                    start_pos = end_pos
                if with_interval:
                    interval_nb = self.macro.getIntervalEstimation()
            else:
                while interval_nb < max_iter:
                    step = iterator.next()
                    interval_nb += 1
                total_time = self.macro.getTimeEstimation()
        except StopIteration:
            return total_time, interval_nb
        # max iteration reached.
        return -total_time, -interval_nb
    
    @property
    def data(self):
        return self._data
    
    @property
    def macro(self):
        return self._macro

    @property
    def measurement_group(self):
        return self._measurement_group

    @property
    def generator(self):
        return self._generator

    @property
    def motion(self):
        return self._motion
    
    @property
    def moveables(self):
        return self._moveables
    
    @property
    def steps(self):
        if not hasattr(self, '_steps'):
            self._steps = enumerate(self.generator())
        return self._steps
    
    def start(self):
        self.do_backup()
        env = self._env
        env['startts'] = ts = time.time()
        env['starttime'] = datetime.datetime.fromtimestamp(ts)
        env['acqtime'] = 0
        env['motiontime'] = 0
        env['deadtime'] = 0
        self.data.start()

    def end(self):
        env = self._env
        env['endts'] = end_ts = time.time()
        env['endtime'] = datetime.datetime.fromtimestamp(end_ts)
        total_time = end_ts - env['startts']
        estimated = env['estimatedtime']
        acq_time = env['acqtime']
        #env['deadtime'] = 100.0 * (total_time - estimated) / total_time
        
        env['deadtime'] = total_time - acq_time
        if 'delaytime' in env:
            env['motiontime'] = total_time - acq_time - env['delaytime']
        elif 'motiontime' in env:
            env['delaytime'] = total_time - acq_time - env['motiontime']
                  
        self.data.end()
        try:
            scan_history = self.macro.getEnv('ScanHistory')
        except UnknownEnv:
            scan_history = []
        
        scan_file = env['ScanFile']
        if isinstance(scan_file, (str, unicode)):
            scan_file = scan_file,
        
        names = [ col.name for col in env['datadesc'] ]
        history = dict(startts=env['startts'], endts=env['endts'],
                       estimatedtime=env['estimatedtime'],
                       deadtime=env['deadtime'], title=env['title'],
                       serialno=env['serialno'], user=env['user'],
                       ScanFile=scan_file, ScanDir=env['ScanDir'],
                       channels=names)
        scan_history.append(history)
        while len(scan_history) > self.MAX_SCAN_HISTORY:
            scan_history.pop(0)
        self.macro.setEnv('ScanHistory', scan_history)

    def scan(self):
        for _ in self.step_scan():
            pass
        
    def step_scan(self):
        self.start()
        try:
            ex = None
            try:
                for i in self.scan_loop():
                    self.macro.pausePoint()
                    yield i
            except ScanException, e:
                #self.macro.warning(e.msg)
                ex = e
            self.end()
            if not ex is None: raise e
        finally:
            self.do_restore()
                
    def scan_loop(self):
        raise NotImplementedError('Scan method cannot be called by '
                                  'abstract class')

    def do_backup(self):
        try:
            if hasattr(self.macro, 'do_backup'):
                self.macro.do_backup()
        except:
            self.macro.warning("Failed to execute macro 'do_backup'")
            self.debug("Details:", exc_info=1)
        
    def do_restore(self):
        try:
            if hasattr(self.macro, 'do_restore'):
                self.macro.do_restore()
        except:
            self.macro.warning("Failed to execute macro 'do_restore'")        
            self.debug("Details:", exc_info=1)


class SScan(GScan):
    """Step scan"""
    
    def scan_loop(self):
        lstep = None
        macro = self.macro
        scream = False
        
        if hasattr(macro, "nr_points"):
            nr_points = float(macro.nr_points)
            scream = True
        else:
            yield 0.0
        
        if hasattr(macro, 'getHooks'):
            for hook in macro.getHooks('pre-scan'):
                hook()
        
        self._sum_motion_time = 0
        self._sum_acq_time = 0
        
        for i, step in self.steps:
            # allow scan to be stopped between points
            macro.checkPoint()
            self.stepUp(i, step, lstep)
            lstep = step
            if scream:
                yield ((i+1) / nr_points) * 100.0
        
        if hasattr(macro, 'getHooks'):
            for hook in macro.getHooks('post-scan'):
                hook()

        if not scream:
            yield 100.0
            
        self._env['motiontime'] = self._sum_motion_time
        self._env['acqtime'] = self._sum_acq_time
        
    def stepUp(self, n, step, lstep):
        motion, mg = self.motion, self.measurement_group
        startts = self._env['startts']
        
        #pre-move hooks
        for hook in step.get('pre-move-hooks',()):
            hook()
            try:
                step['extrainfo'].update(hook.getStepExtraInfo())
            except InterruptException:
                raise
            except:
                pass
        
        # Move
        self.debug("[START] motion")
        move_start_time = time.time()
        try:
            state, positions = motion.move(step['positions'])
            self._sum_motion_time += time.time() - move_start_time
        except InterruptException:
            raise
        except:
            self.dump_information(n, step)
            raise
        self.debug("[ END ] motion")
        
        curr_time = time.time()
        dt = curr_time - startts
        
        #post-move hooks
        for hook in step.get('post-move-hooks',()):
            hook()
            try:
                step['extrainfo'].update(hook.getStepExtraInfo())
            except InterruptException:
                raise
            except:
                pass
        
        # allow scan to be stopped between motion and data acquisition
        self.macro.checkPoint()
        
        if state != Ready:
            self.dump_information(n, step)
            m = "Scan aborted after problematic motion: " \
                "Motion ended with %s\n" % str(state)
            raise ScanException({ 'msg' : m })
        
        #pre-acq hooks
        for hook in step.get('pre-acq-hooks',()):
            hook()
            try:
                step['extrainfo'].update(hook.getStepExtraInfo())
            except InterruptException:
                raise
            except: pass
        
        integ_time = step['integ_time']
        # Acquire data
        self.debug("[START] acquisition")
        state, data_line = mg.count(integ_time)
        for ec in self._extra_columns:
            data_line[ec.getName()] = ec.read()
        self.debug("[ END ] acquisition")
        self._sum_acq_time += integ_time

        #post-acq hooks
        for hook in step.get('post-acq-hooks',()):
            hook()
            try:
                step['extrainfo'].update(hook.getStepExtraInfo())
            except InterruptException:
                raise
            except:
                pass
        
        #hooks for backwards compatibility:
        if step.has_key('hooks'):
            self.macro.info('Deprecation warning: you should use '
                            '"post-acq-hooks" instead of "hooks" in the step '
                            'generator')
            for hook in step.get('hooks',()):
                hook()
                try:
                    step['extrainfo'].update(hook.getStepExtraInfo())
                except InterruptException:
                    raise
                except:
                    pass
        
        # Add final moveable positions
        data_line['point_nb'] = n
        data_line['timestamp'] = dt
        for i, m in enumerate(self.moveables):
            data_line[m.moveable.getName()] = positions[i]
        
        #Add extra data coming in the step['extrainfo'] dictionary
        if step.has_key('extrainfo'): data_line.update(step['extrainfo'])
        
        self.data.addRecord(data_line)
    
        #post-step hooks
        for hook in step.get('post-step-hooks',()):
            hook()
            try:
                step['extrainfo'].update(hook.getStepExtraInfo())
            except InterruptException:
                raise
            except:
                pass
        
    def dump_information(self, n, step):
        moveables = self.motion.moveable_list
        msg = ["Report: Stopped at step #" + str(n) + " with:"]
        for moveable in moveables:
            msg.append(moveable.information())
        self.macro.info("\n".join(msg))
        

class CScan(GScan):
    """Continuous scan abstract class. Implements helper methods."""
    
    def __init__(self, macro, generator=None, moveables=[],
                 env={}, constraints=[], extrainfodesc=[]):
        GScan.__init__(self, macro, generator=generator,
                       moveables=moveables, env=env, constraints=constraints,
                       extrainfodesc=extrainfodesc)
        self._current_waypoint_finished = False
        self._all_waypoints_finished = False
        self.motion_event = threading.Event()
        self.motion_end_event = threading.Event()
        data_structures = self.populate_moveables_data_structures(moveables)
        self._moveables_trees, \
        physical_moveables_names, \
        self._physical_moveables = data_structures
        self._physical_motion = self.macro.getMotion(physical_moveables_names)
        
    def populate_moveables_data_structures(self, moveables):
        '''Populates moveables data structures.
        :param moveables: (list<Moveable>) data structures will be generated 
                          for these moveables
        :return (moveable_trees, physical_moveables_names, physical_moveables)
                - moveable_trees (list<Tree>) - each tree represent one Moveables
                            with its hierarchy of inferior moveables.
                - physical_moveables_names (list<str> - list of the names of the 
                            physical moveables. List order is important and preserved.
                - physical_moveables (list<Moveable> - list of the moveable objects.
                            List order is important and preserved.'''
        
        def generate_moveable_node(macro, moveable):
            '''Function to generate a moveable data structures based on moveable object.
            Internally can be recursively called if moveable is a PseudoMotor.
            :param moveable: moveable object
            :return (moveable_node, physical_moveables_names, physical_moveables)
                - moveable_node (BaseNode) - can be a BranchNode if moveable is a PseudoMotor
                                      or a LeafNode if moveable is a PhysicalMotor.
                - physical_moveables_names (list<str> - list of the names of the 
                            physical moveables. List order is important and preserved.
                - physical_moveables (list<Moveable> - list of the moveable objects.
                            List order is important and preserved.'''
            moveable_node = None
            physical_moveables_names = []
            physical_moveables = []
            moveable_type = moveable.getType()
            if moveable_type == "PseudoMotor":
                moveable_node = BranchNode(moveable)    
                moveables_names = moveable.elements                
                sub_moveables = [macro.getMoveable(name) \
                                 for name in moveables_names]
                for sub_moveable in sub_moveables:
                    sub_moveable_node, \
                    _physical_moveables_names, \
                    _physical_moveables = generate_moveable_node(macro,
                                                                 sub_moveable)
                    physical_moveables_names += _physical_moveables_names
                    physical_moveables += _physical_moveables
                    moveable_node.addChild(sub_moveable_node)
            elif moveable_type == "Motor":
                moveable_node = LeafNode(moveable)
                moveable_name = moveable.getName()
                physical_moveables_names.append(moveable_name)
                physical_moveables.append(moveable)
            return moveable_node, physical_moveables_names, physical_moveables
        
        moveable_trees = []
        physical_moveables_names = [] 
        physical_moveables = []
                
        for moveable in moveables:
            moveable_root_node, _physical_moveables_names, _physical_moveables = \
                      generate_moveable_node(self.macro, moveable.moveable) 
            moveable_tree = Tree(moveable_root_node)
            moveable_trees.append(moveable_tree)
            physical_moveables_names += _physical_moveables_names
            physical_moveables += _physical_moveables 
        return moveable_trees, physical_moveables_names, physical_moveables
    
    def get_moveables_trees(self):
        '''Returns reference to the list of the moveables trees'''
        return self._moveables_trees
                    
    def on_waypoints_end(self, restore_positions=None):
        """To be called by the waypoint thread to handle the end of waypoints
        (either because no more waypoints or because a macro abort was
        triggered)"""
        self.set_all_waypoints_finished(True)
        if restore_positions is not None:
            self.macro.info("Correcting overshoot...")
            self._physical_motion.move(restore_positions)
            #self.motion.move(restore_positions)
        self.motion_end_event.set()        
        self.motion_event.set()
            
    def go_through_waypoints(self, iterate_only=False):
        """Go through the different waypoints."""
        try:
            self._go_through_waypoints()
        except:
            self.macro.error("An error occured moving to waypoints. Aborting...")
            self.macro.debug("Details:", exc_info=1)
            self.on_waypoints_end()

    def _go_through_waypoints(self):
        """Internal, unprotected method to go through the different waypoints."""
        raise NotImplementedError("_go_through_waypoints must be implemented " +
                            "in CScan derived classes")
                
    def waypoint_estimation(self):
        """Internal, unprotected method to go through the different waypoints."""
        motion, waypoints = self.motion, self.generator()
        total_duration = 0
        #v_motors = self.get_virtual_motors()
        curr_positions, last_end_positions = motion.readPosition(force=True), None
        for i, waypoint in enumerate(waypoints):
            start_positions = waypoint.get('start_positions', last_end_positions)
            positions = waypoint['positions']
            if start_positions is None:
                last_end_positions = positions
                continue
            
            waypoint_info = self.prepare_waypoint(waypoint, start_positions,
                                                  iterate_only=True)
            motion_paths, delta_start, acq_duration = waypoint_info
    
            start_path, end_path = [] , []
            for path in motion_paths:
                start_path.append(path.initial_user_pos)
                end_path.append(path.final_user_pos)
                       
            # move from last waypoint to start position of this waypoint
            first_duration = 0
            if i == 1:
                # first waypoint means, moving from current position to the
                # start of first waypoint
                initial = curr_positions
            else:
                initial = start_positions
            for _path, start, end in zip(motion_paths, initial, start_path):
                v_motor = _path.motor
                path = MotionPath(v_motor, start, end)
                first_duration = max(first_duration, path.duration)
                        
            # move from waypoint start position to waypoint end position
            second_duration = 0
            for _path, start, end in zip(motion_paths, start_path, end_path):
                v_motor = _path.motor
                path = MotionPath(v_motor, start, end)
                second_duration = max(second_duration, path.duration)
            
            total_duration += first_duration + second_duration
            
            last_end_positions = end_path
        
        # add correct overshoot time
        overshoot_duration = 0
        for _path, start, end in zip(motion_paths, last_end_positions, positions):
            v_motor = _path.motor
            path = MotionPath(v_motor, start, end)
            overshoot_duration = max(overshoot_duration, path.duration)
        
        total_duration += overshoot_duration
        return total_duration       
    
    def prepare_waypoint(self, waypoint, start_positions, iterate_only=False):
        raise NotImplementedError("prepare_waypoint must be implemented in " + 
                                  "CScan derived classes")
        
    def set_all_waypoints_finished(self, v):
        self._all_waypoints_finished = v

    def do_backup(self):
        super(CScan, self).do_backup()
        self._backup = backup = []
        for moveable in self._physical_moveables:
            # first backup all motor parameters
            motor = moveable
            try:
                velocity = motor.getVelocity()
                accel_time = motor.getAcceleration()
                decel_time = motor.getDeceleration()
                motor_backup = dict(moveable=moveable, velocity=velocity,
                                    acceleration=accel_time,
                                    deceleration=decel_time)
                self.debug("Backup of %s", motor)
            except AttributeError:
                motor_backup = None
            backup.append(motor_backup)
           
    def do_restore(self):
        super(CScan, self).do_restore()
        # restore changed motors to initial state
        for motor_backup in self._backup:
            if motor_backup is None:
                continue
            try:
                motor = motor_backup['moveable']
                motor.setVelocity(motor_backup['velocity'])
                motor.setAcceleration(motor_backup['acceleration'])
                motor.setDeceleration(motor_backup['deceleration'])
                self.debug("Restored %s", motor)
            except:
                self.macro.warning("Failed to restore %s", motor)
                self.debug("Details:", exc_info=1)
                
    def get_max_top_velocity(self, motor):
        """Helper method to find the maximum top velocity for the motor.
        If the motor doesn't have a defined range for top velocity,
        then use the current top velocity"""
        
        top_vel_obj = motor.getVelocityObj()
        min_top_vel, max_top_vel = top_vel_obj.getRange()
        try:
            max_top_vel = float(max_top_vel)
        except ValueError:
            try:
                #hack to avoid recursive velocity reduction
                self._maxVelDict = getattr(self,'_maxVelDict',{})
                if not motor in self._maxVelDict:
                    self._maxVelDict[motor] = motor.getVelocity()
                max_top_vel = self._maxVelDict[motor]
            except AttributeError:
                pass
        return max_top_vel
    
    def get_min_acc_time(self, motor):
        """Helper method to find the minimum acceleration time for the motor.
        If the motor doesn't have a defined range for the acceleration time,
        then use the current acceleration time"""
        
        acc_time_obj = motor.getAccelerationObj()
        min_acc_time, max_acc_time = acc_time_obj.getRange()
        try:
            min_acc_time = float(min_acc_time)
        except ValueError:
            min_acc_time = motor.getAcceleration()
        return min_acc_time
    
    def get_min_dec_time(self, motor):
        """Helper method to find the minimum deceleration time for the motor.
        If the motor doesn't have a defined range for the acceleration time,
        then use the current acceleration time"""
        
        dec_time_obj = motor.getDecelerationObj()
        min_dec_time, max_dec_time = dec_time_obj.getRange()
        try:
            min_dec_time = float(min_dec_time)
        except ValueError:
            min_dec_time = motor.getDeceleration()
        return min_dec_time
 
#    def set_max_top_velocity(self, motor):
#        """Helper method to set the maximum top velocity for the motor to 
#        its maximum allowed limit."""
#        
#        v = self.get_max_top_velocity(motor)
#        try:
#            motor.setVelocity(v)
#        except:
#            pass

                
class CSScan(CScan):
    """Continuous scan controlled by software"""
    
    def __init__(self, macro, waypointGenerator=None, periodGenerator=None,
                 moveables=[], env={}, constraints=[], extrainfodesc=[]):
        CScan.__init__(self, macro, generator=waypointGenerator,
                       moveables=moveables, env=env, constraints=constraints,
                       extrainfodesc=extrainfodesc)
        self._periodGenerator = periodGenerator
        

    def _calculateTotalAcquisitionTime(self):
        return None
        
    @property
    def period_generator(self):
        return self._periodGenerator
    
    @property
    def period_steps(self):
        if not hasattr(self, '_period_steps'):
            self._period_steps = enumerate(self.period_generator())
        return self._period_steps
    
    def prepare_waypoint(self, waypoint, start_positions, iterate_only=False):
        slow_down = waypoint.get('slow_down', 1)
        positions = waypoint['positions']
        
        duration, cruise_duration, delta_start = 0, 0, 0
        ideal_paths, real_paths = [], []
        for i, (moveable, position) in enumerate(zip(self.moveables, positions)):
            motor = moveable.moveable
            
            coordinate = True
            try:
                base_vel, top_vel = motor.getBaseRate(), motor.getVelocity()
                accel_time, decel_time = motor.getAcceleration(), motor.getDeceleration()

                if slow_down > 0:
                    # find and set the maximum top velocity for the motor. 
                    # If the motor doesn't have a defined range for top velocity,
                    # then use the current top velocity
                    max_top_vel = self.get_max_top_velocity(motor)
                    if not iterate_only:
                        motor.setVelocity(max_top_vel)
                else:
                    max_top_vel = top_vel
            except AttributeError:
                if not iterate_only:
                    self.macro.warning("%s motion will not be coordinated", motor)
                base_vel, top_vel, max_top_vel = 0, float('+inf'), float('+inf')
                accel_time, decel_time = 0, 0
                coordinate = False

            last_user_pos = start_positions[i]
                        
            real_vmotor = VMotor(min_vel=base_vel, max_vel=max_top_vel,
                                 accel_time=accel_time,
                                 decel_time=decel_time)
            real_path = MotionPath(real_vmotor, last_user_pos, position)
            real_path.moveable = moveable            
            real_path.apply_correction = coordinate
            
            # Find the cruise duration of motion at top velocity. For this create a
            # virtual motor which has instantaneous acceleration and deceleration
            ideal_vmotor = VMotor(min_vel=base_vel, max_vel=max_top_vel,
                                  accel_time=0, decel_time=0)
            
            # create a path which will tell us which is the cruise duration of this
            # motion at top velocity
            ideal_path = MotionPath(ideal_vmotor, last_user_pos, position)
            ideal_path.moveable = moveable
            ideal_path.apply_correction = coordinate
            
            # if really motor is moving in this waypoint
            if ideal_path.displacement > 0:
                # recalculate time to reach maximum velocity
                delta_start = max(delta_start, accel_time)
            
            # recalculate cruise duration of motion at top velocity
            cruise_duration = max(cruise_duration, ideal_path.duration)
            duration = max(duration, real_path.duration)
            
            ideal_paths.append(ideal_path)
            real_paths.append(real_path)
            
        if slow_down <= 0:
            return real_paths, 0, duration
        
        # after finding the duration, introduce the slow down factor added
        # by the user
        cruise_duration /= slow_down
        
        if cruise_duration == 0:
            cruise_duration = float('+inf')
        
        # now that we have the appropriate top velocity for all motors, the
        # cruise duration of motion at top velocity, and the time it takes to
        # recalculate 
        for path in ideal_paths:
            vmotor = path.motor
            # in the case of pseudo motors or not moving a motor...
            if not path.apply_correction or path.displacement == 0:
                continue
            moveable = path.moveable
            motor = moveable.moveable
            new_top_vel = path.displacement / cruise_duration
            vmotor.setMaxVelocity(new_top_vel)
            accel_t, decel_t = motor.getAcceleration(), motor.getDeceleration()
            base_vel = vmotor.getMinVelocity()
            vmotor.setAccelerationTime(accel_t)
            vmotor.setDecelerationTime(decel_t)
            disp_sign = path.positive_displacement and 1 or -1
            new_initial_pos = path.initial_user_pos - accel_t * 0.5 * disp_sign * (new_top_vel + base_vel) - disp_sign * new_top_vel * (delta_start - accel_t)
            path.setInitialUserPos(new_initial_pos)
            new_final_pos = path.final_user_pos + disp_sign * vmotor.displacement_reach_min_vel
            path.setFinalUserPos(new_final_pos)
        
        return ideal_paths, delta_start, cruise_duration

    
    def go_through_waypoints(self, iterate_only=False):
        """go through the different waypoints."""
        try:
            self._go_through_waypoints()
        except Exception, e:
            self.macro.error("An error occured moving to waypoints. Aborting...")
            self.macro.debug("Details:", exc_info=1)
            self.on_waypoints_end()
            raise e

    def _go_through_waypoints(self):
        """Internal, unprotected method to go through the different waypoints."""
        macro, motion, waypoints = self.macro, self.motion, self.steps
        self.macro.debug("_go_through_waypoints() entering...")
        
        last_positions = None
        for _, waypoint in waypoints:
            self.macro.debug("Waypoint iteration...")
            start_positions = waypoint.get('start_positions')
            positions = waypoint['positions']
            if start_positions is None:
                start_positions = last_positions
            if start_positions is None:
                last_positions = positions
                continue
            
            waypoint_info = self.prepare_waypoint(waypoint, start_positions)
            motion_paths, delta_start, acq_duration = waypoint_info
            
            self.acq_duration = acq_duration
                        
            #execute pre-move hooks
            for hook in waypoint.get('pre-move-hooks',[]): 
                hook()
    
            start_pos, final_pos = [] , []
            for path in motion_paths:
                start_pos.append(path.initial_user_pos)
                final_pos.append(path.final_user_pos)
            
            if macro.isStopped():
                self.on_waypoints_end()
                return
                       
            # move to start position
            self.macro.debug("Moving to start position: %s" % repr(start_pos))
            motion.move(start_pos)
            
            if macro.isStopped():
                return self.on_waypoints_end()
            
            # prepare motor(s) to move with their maximum velocity
            for path in motion_paths:
                if not path.apply_correction:
                    continue
                vmotor = path.motor
                motor = path.moveable.moveable
                motor.setVelocity(vmotor.getMaxVelocity())

            if macro.isStopped():
                return self.on_waypoints_end()
                        
            self.timestamp_to_start = time.time() + delta_start
            self.motion_event.set()
            
            # move to waypoint end position
            motion.move(final_pos)

            self.motion_event.clear()

            if macro.isStopped():
                return self.on_waypoints_end()
            
            #execute post-move hooks
            for hook in waypoint.get('post-move-hooks',[]):
                hook()
            
            if start_positions is None:  
                last_positions = positions
        
        self.on_waypoints_end(positions)

    
    def scan_loop(self):
        motion, mg, waypoints = self.motion, self.measurement_group, self.steps
        macro = self.macro
        manager = macro.getManager()
        scream = False
        motion_event = self.motion_event
        startts = self._env['startts']
        
        sum_delay = 0
        sum_integ_time = 0
        
        if hasattr(macro, "nr_points"):
            nr_points = float(macro.nr_points)
            scream = True
        else:
            yield 0.0

        moveables = [ m.moveable for m in self.moveables ]
        period_steps = self.period_steps
        point_nb, step = -1, None
        data = self.data
        
        if hasattr(macro, 'getHooks'):
            for hook in macro.getHooks('pre-scan'):
                hook()
        
        # start move & acquisition as close as possible
        # from this point on synchronization becomes critical
        manager.add_job(self.go_through_waypoints)
        
        while not self._all_waypoints_finished:
        
            # wait for motor to reach start position
            motion_event.wait()
            
            # allow scan to stop
            macro.checkPoint()
            
            if self._all_waypoints_finished:
                break
            
            # wait for motor to reach max velocity
            start_time = time.time()
            deltat = self.timestamp_to_start - start_time
            if deltat > 0:
                time.sleep(deltat)
            curr_time = acq_start_time = time.time()
            integ_time = 0
            
            # Acquisition loop: acquire consecutively until waypoint asks to
            # stop or we see that we will enter deceleration time in next
            # acquisition
            while motion_event.is_set():

                # allow scan to stop
                macro.checkPoint()
            
                try:
                    point_nb, step = period_steps.next()
                except StopIteration:
                    self._all_waypoints_finished = True
                    break

                integ_time = step['integ_time']
                
                # If there is no more time to acquire... stop!
                elapsed_time = time.time() - acq_start_time
                if elapsed_time + integ_time > self.acq_duration:
                    motion_event.clear()
                    break;                
                
                #pre-acq hooks
                for hook in step.get('pre-acq-hooks',()):
                    hook()
                    try:
                        step['extrainfo'].update(hook.getStepExtraInfo())
                    except InterruptException:
                        self._all_waypoints_finished = True
                        raise
                    except: pass

                # allow scan to stop
                macro.checkPoint()
                
                positions = motion.readPosition(force=True)

                dt = time.time() - startts

                # Acquire data
                self.debug("[START] acquisition")
                state, data_line = mg.count(integ_time)
                
                sum_integ_time += integ_time
                
                # allow scan to stop
                macro.checkPoint()
                
                # After acquisition, test if we are asked to stop, probably because
                # the motor are stopped. In this case discard the last acquisition
                if not self._all_waypoints_finished:
                    for ec in self._extra_columns:
                        data_line[ec.getName()] = ec.read()
                    self.debug("[ END ] acquisition")
                    
                    #post-acq hooks
                    for hook in step.get('post-acq-hooks',()):
                        hook()
                        try:
                            step['extrainfo'].update(hook.getStepExtraInfo())
                        except InterruptException:
                            self._all_waypoints_finished = True
                            raise
                        except:
                            pass

                    # Add final moveable positions
                    data_line['point_nb'] = point_nb
                    data_line['timestamp'] = dt
                    for i, m in enumerate(self.moveables):
                        data_line[m.moveable.getName()] = positions[i]
                    
                    #Add extra data coming in the step['extrainfo'] dictionary
                    if step.has_key('extrainfo'): data_line.update(step['extrainfo'])
                    
                    self.data.addRecord(data_line)
                    
                    if scream:
                        yield ((point_nb+1) / nr_points) * 100.0
                else:
                    break
                old_curr_time = curr_time
                curr_time = time.time()
                sum_delay += (curr_time - old_curr_time) - integ_time

        self.motion_end_event.wait()

        if hasattr(macro, 'getHooks'):
            for hook in macro.getHooks('post-scan'):
                hook()
        
        
        env = self._env
        env['acqtime'] = sum_integ_time
        env['delaytime'] = sum_delay
        
        if not scream:
            yield 100.0   


class CTScan(CScan):
    '''Continuous scan controlled by hardware trigger signals. 
    Sequence of trigger signals is programmed in time. '''
    
    class ExtraTrigger:
        '''Helper class and temporary solution for configuring trigger device.
           It is used to configure any Tango device name implementing:
           +) following attributes: 
           - InitialDelayTime [s] - delay time from calling Start to generating first pulse 
           - HighTime [s] - time interval while signal will maintain its high state
           - LowTime [s] - time interval while signal will maintain its low state
           - SampPerChan - nr of pulses to be generated
           - IdleState - state (high or low) which signal will take after the Start command
                         and which will maintain during the InitialDelayTime.  
           +) following commands:
           - Start 
           - Stop)'''
         
        MIN_HIGH_TIME = 0.0000002
        MIN_TIME_PER_TRIGGER = 0.000001
    
        def __init__(self, macro):
            self.macro = macro
            
            triggerDeviceName = self.macro.getEnv("TriggerDevice")
            self.master = None
            self.slaves = []
            masterName = None
            slaveNames = []
            
            if isinstance(triggerDeviceName, str):
                masterName = triggerDeviceName
            elif isinstance(triggerDeviceName, list):
                masterName = triggerDeviceName[0]
                slaveNames = triggerDeviceName[1:]
            
            for name in slaveNames:
                slave = PyTango.DeviceProxy(name)
                self.slaves.append(slave)
            if masterName != None:
                self.master = PyTango.DeviceProxy(masterName)        
    
        def configure(self, scanTime=None, nrOfTriggers=None, idleState="Low", lowTime=None, highTime=None, delayTime=0):
            if not None in (scanTime, nrOfTriggers, delayTime, idleState):
                timePerTrigger = scanTime / nrOfTriggers
                if timePerTrigger < self.MIN_TIME_PER_TRIGGER:
                    raise Exception("scanTime is not long enough to manage this amount of triggers")
                highTime = self.MIN_HIGH_TIME
                lowTime = timePerTrigger - highTime
            elif not None in (lowTime, highTime, delayTime, nrOfTriggers, idleState):
                pass
            else:
                raise Exception("Missing parameters.")
            
            self.master.write_attribute("InitialDelayTime", delayTime)
            self.master.write_attribute("HighTime", highTime) # 162.5 ns
            self.master.write_attribute("LowTime", lowTime) # 2.75 ms
            self.master.write_attribute("SampPerChan", long(nrOfTriggers))
            self.master.write_attribute("IdleState", idleState)
            self.master.write_attribute("SampleTimingType", "Implicit")
    
            for slave in self.slaves:
                slave.write_attribute("HighTime", highTime) # 162.5 ns
                slave.write_attribute("LowTime", lowTime) # 2.75 ms
                slave.write_attribute("SampPerChan", long(nrOfTriggers))
                slave.write_attribute("IdleState", idleState)
                slave.write_attribute("SampleTimingType", "Implicit")
                
            return timePerTrigger
    
        def getConfiguration(self):
            return None, None, None, None
    
        def start(self):
            for slave in self.slaves:
                self.macro.debug("Staring  %s" % slave.name())
                slave.Start()
            if self.master != None:
                self.master.Start()
    
        def stop(self):
            for slave in self.slaves:
                self.macro.debug("Stopping  %s" % slave.name())
                slave.Stop()
            if self.master != None:
                self.master.Stop()

    
    class ExtraMntGrp:
        '''Helper class and temporary solution for configuring experimental channels.
        It assumes that experimental channels are implementing:
        +) following attributes:
        - Data - an array of acquired data
        - TriggerMode - Soft or Gate - to configure/unconfigure channel for hardware trigger
        - NrOfTriggers - to specify how many hardware triggers and acquistions will be done
        - SamplingFrequency - have sence only for sampling experimental channels
        +) following SendToCtrl strings:
        - "pre-start"
        - "start"
        - "pre-stop"
        - "stop"'''
        
        def __init__(self, macro):
            self.macro = macro
            activeMntGrpName = self.macro.getEnv("ActiveMntGrp")
            self.mntGrp = self.macro.getMeasurementGroup(activeMntGrpName)        
            self.activeChannels = []
            self.nrOfTriggers = 0
            channels = self.mntGrp.getChannels()
            for channel in channels:
                channelName = channel["name"]
                expChannel = self.macro.getExpChannel(channelName)
                expChannel.getHWObj().set_timeout_millis(120000) #in case of readout of position channels, it can take really long...
                self.activeChannels.append(expChannel)
    
        def isMoving(self):
            for channel in self.activeChannels:
                if channel.State() == PyTango.DevState.MOVING:
                    return True
            return False
    
        def start(self):
            for channel in self.activeChannels:
                pool = channel.getPoolObj()
                ctrlName = channel.getControllerName()
                axis = channel.getAxis()
                self.macro.debug("Pre-starting controller: %s, axis: %d", ctrlName, axis)
                pool.SendToController([ctrlName, 'pre-start %d' % axis])
    
            for channel in self.activeChannels:
                pool = channel.getPoolObj()
                ctrlName = channel.getControllerName()
                axis = channel.getAxis()
                self.macro.debug("Starting controller: %s, axis: %d", ctrlName, axis)
                pool.SendToController([ctrlName, 'start %d' % axis])
     
        def stop(self):
            for channel in self.activeChannels:
                pool = channel.getPoolObj()
                ctrlName = channel.getControllerName()
                axis = channel.getAxis()
                self.macro.debug("Pre-stopping controller: %s, axis: %d", ctrlName, axis)
                pool.SendToController([ctrlName, 'pre-stop %d' % axis])
    
            for channel in self.activeChannels:
                pool = channel.getPoolObj()
                ctrlName = channel.getControllerName()
                axis = channel.getAxis()
                self.macro.debug("Stopping controller: %s, axis: %d", ctrlName, axis)
                pool.SendToController([ctrlName, 'stop %d' % axis])
    
        def getDataList(self):
            dataList = [ {"point_nb" : i, "timestamp" : 0} for i in xrange(self.nrOfTriggers) ]
            for channel in self.activeChannels:
                dataDesc = channel.getFullName()
                channelData = channel.getAttribute("Data").read().value
                for i, data in enumerate(channelData):
                    dataList[i][dataDesc] = data
            return dataList
    
        def setSamplingFrequency(self, freq):
            for channel in self.activeChannels:
                channel.getAttribute('SamplingFrequency').write(freq)
    
        def setAcquisitionTime(self, acqTime):
            for channel in self.activeChannels:
                channel.getAttribute('AcquisitionTime').write(acqTime)
    
        def setTriggerMode(self, mode):
            if mode not in ["soft", "gate"]:
                raise Exception("Trigger mode must be either soft or gate.")
            for channel in self.activeChannels:
                channel.getAttribute('TriggerMode').write(mode)
    
        def setNrOfTriggers(self, nrOfTriggers):
            self.nrOfTriggers = nrOfTriggers
            for channel in self.activeChannels:
                channel.getAttribute('NrOfTriggers').write(nrOfTriggers)
    
        def configure(self, nrOfTriggers, acqTime, timePerTrigger, sampFreq=-1, triggerMode="gate"):
            self.macro.debug("acqTime: %s" % acqTime)
            if timePerTrigger == None:
                raise Exception("TimePerTrigger attribute must be set")
            acqTime = timePerTrigger * acqTime / 100.0
            self.setTriggerMode(triggerMode)
            self.setNrOfTriggers(nrOfTriggers)
            self.setSamplingFrequency(sampFreq)
            self.setAcquisitionTime(acqTime)
            self.macro.debug("MG: nrOfTriggers: %s, timePerTrigger: %s, acqTime: %s, sampFreq: %s" % (nrOfTriggers,timePerTrigger,acqTime,sampFreq))
    
        def getConfiguration(self):
            return None
    
        def setConfiguration(self, configuration):
            pass

    
    def __init__(self, macro, generator=None,
                 moveables=[], env={}, constraints=[], extrainfodesc=[]):
        CScan.__init__(self, macro, generator=generator,
                       moveables=moveables, env=env, constraints=constraints,
                       extrainfodesc=extrainfodesc)
        self._measurement_group = self.ExtraMntGrp(macro)
        self.extraTrigger = self.ExtraTrigger(macro)
            
        
    def prepare_waypoint(self, waypoint, start_positions, iterate_only=False):
        '''Prepare list of MotionPath objects per each physical motor. 
        :param waypoint: (dict) waypoint dictionary with necessary information
        :param start_positions: (list<float>) list of starting position per each
                                 physical motor
        :return (ideal_paths, acc_time, active_time)
                - ideal_paths: (list<MotionPath> representing motion attributes 
                               of each physical motor)
                - acc_time: acceleration time which will be used during the scan
                            it corresponds to the longest acceleration time of 
                            all the motors
                - active_time: time interval while all the physical motors will
                               maintain constant velocity'''

        positions = waypoint['positions']
        active_time = waypoint["active_time"]
        
        ideal_paths = []
        
        max_acc_time, max_dec_time = 0, 0                
        for moveable, end_position in zip(self._physical_moveables, positions):
            motor = moveable
            self.macro.debug("Motor: %s" % motor.getName())
            self.macro.debug("AccTime: %f" % self.get_min_acc_time(motor))
            self.macro.debug("DecTime: %f" % self.get_min_dec_time(motor))
            max_acc_time = max(self.get_min_acc_time(motor), max_acc_time)
            max_dec_time = max(self.get_min_dec_time(motor), max_dec_time)
            
        acc_time = max_acc_time
        dec_time = max_dec_time
            
        for moveable, start_position, end_position in \
                      zip(self._physical_moveables, start_positions, positions):
            base_vel = moveable.getBaseRate()        
            ideal_vmotor = VMotor(accel_time=acc_time,
                                  decel_time=dec_time,
                                  min_vel=base_vel)
            ideal_path = MotionPath(ideal_vmotor, 
                                    start_position, 
                                    end_position, 
                                    active_time)            
            ideal_path.moveable = moveable
            ideal_path.apply_correction = True        
            ideal_paths.append(ideal_path)                                 
        
        return ideal_paths, acc_time, active_time
    
    def _go_through_waypoints(self):
        """Internal, unprotected method to go through the different waypoints.
           It controls all the three objects: motion, trigger and measurement
           group."""
        macro, motion, waypoints = self.macro, self._physical_motion, self.steps
        self.macro.debug("_go_through_waypoints() entering...")
        
        last_positions = None
        for _, waypoint in waypoints:
            self.macro.debug("Waypoint iteration...")
            start_positions = waypoint.get('start_positions')
            positions = waypoint['positions']
            if start_positions is None:
                start_positions = last_positions
            if start_positions is None:
                last_positions = positions
                continue
            
            waypoint_info = self.prepare_waypoint(waypoint, start_positions)
            motion_paths, delta_start, acq_duration = waypoint_info
            
            self.acq_duration = acq_duration
                        
            #execute pre-move hooks
            for hook in waypoint.get('pre-move-hooks',[]): 
                hook()
    
            start_pos, final_pos = [] , []
            for path in motion_paths:
                start_pos.append(path.initial_user_pos)
                final_pos.append(path.final_user_pos)
            
            if macro.isStopped():
                self.on_waypoints_end()
                return

            self.__mntGrpConfigured = False
            self.__triggerConfigured = False
            self.__mntGrpStarted = False
            self.__triggerStarted = False
            
            #validation of parameters
            for start, end in zip(self.macro.starts, self.macro.finals):
                if start == end:
                    raise Exception("Start and End can not be equal.")

            startTimestamp = time.time()
        
            #extra pre configuration
            if hasattr(macro, 'getHooks'):
                for hook in macro.getHooks('pre-configuration'):
                    hook()
            self.macro.checkPoint()
    
            #configuring trigger lines
            oldHighTime, oldLowTime, oldDelay, oldNrOfTriggers = \
                                        self.extraTrigger.getConfiguration()
            self.__triggerConfigured = True
            timePerTrigger = self.extraTrigger.configure(delayTime=delta_start,
                                           scanTime=acq_duration,
                                           nrOfTriggers=self.macro.nr_of_points)
            self.macro.checkPoint()
    
            #configuring measurementGroup
            self.mntGrpConfiguration = self._measurement_group.getConfiguration()
            self.__mntGrpConfigured = True
            self._measurement_group.configure(self.macro.nr_of_points, 
                                       self.macro.acq_time, 
                                       timePerTrigger)
            self.macro.checkPoint()
    
            #extra post configuration
            if hasattr(macro, 'getHooks'):
                for hook in macro.getHooks('post-configuration'):
                    hook()
            self.macro.checkPoint()
    
            endTimestamp = time.time()
            self.macro.info("Configuration took %s time." % repr(endTimestamp - startTimestamp))

            # move to start position
            self.macro.debug("Moving to start position: %s" % repr(start_pos))
            motion.move(start_pos)
            
            if macro.isStopped():
                return self.on_waypoints_end()
            
            # prepare motor(s) to move with their maximum velocity
            for path in motion_paths:
                motor = path.moveable
                self.macro.debug("Motor: %s" % motor.getName())
                self.macro.debug("Velocity: %f" % path.max_vel)
                self.macro.debug("AccTime: %f" % path.max_vel_time)
                self.macro.debug("DecTime: %f" % path.min_vel_time)
                #TODO: check why we have 0 here
                #if 0 in [path.max_vel, path.max_vel_time, path.min_vel_time]:
                #    continue
                motor.setVelocity(path.max_vel)
                motor.setAcceleration(path.max_vel_time)                
                motor.setDeceleration(path.min_vel_time)
                
            if macro.isStopped():
                return self.on_waypoints_end()
            
            if hasattr(macro, 'getHooks'):
                for hook in macro.getHooks('pre-start'):
                    hook()
            self.macro.checkPoint()
    
            self.macro.debug("Starting measurement group")
            self.__mntGrpStarted = True
            self._measurement_group.start()            
            
            self.timestamp_to_start = time.time() + delta_start
                        
            self.motion_event.set()
            
            # move to waypoint end position
            self.macro.debug("Moving to waypoint position: %s" % repr(final_pos))
            self.macro.debug("Starting triggers")
            self.__triggerStarted = True
            self.extraTrigger.start()
            motion.move(final_pos)
                        
            self.motion_event.clear()

            if macro.isStopped():
                return self.on_waypoints_end()
            
            #execute post-move hooks
            for hook in waypoint.get('post-move-hooks',[]):
                hook()
                    
            self.macro.debug("Waiting for measurement group to finish")            
            while self._measurement_group.isMoving():
                self.macro.checkPoint()
                time.sleep(0.1)
                
            self.macro.debug("Getting data")                
            data_list = self._measurement_group.getDataList()
            
            def populate_ideal_positions():
                moveables = self.moveables
                nr_of_points = self.macro.nr_of_points
                starts = self.macro.starts
                finals = self.macro.finals
                positions_records = [{} for i in xrange(nr_of_points)]
                
                for moveable, start, final in zip(moveables, starts, finals):
                    name = moveable.moveable.getName()
                    step_size = abs((end-start)/nr_of_points)
                    for point_nr, position in enumerate(np.arange(start, \
                                                            final, step_size)):
                        positions_records[point_nr][name] = position    
                    
                return positions_records
            
            #TODO: decide what to do with moveables
            position_list = populate_ideal_positions()

            self.macro.debug("Storing data")
            for data_dict, position_dict in zip(data_list,position_list):
                data_dict.update(position_dict)
                self.data.addRecord(data_dict)    
            
            if start_positions is None:  
                last_positions = positions
        
        self.on_waypoints_end(positions)
        
    def on_waypoints_end(self, restore_positions=None):
        self.macro.debug("on_waypoints_end() entering...")
        CScan.on_waypoints_end(self, restore_positions=restore_positions)
        self.cleanup()

    def scan_loop(self):        
        macro = self.macro
        manager = macro.getManager()
        scream = False
        motion_event = self.motion_event
        startts = self._env['startts']
        
        sum_delay = 0
        sum_integ_time = 0
        
        if hasattr(macro, "nr_points"):
            nr_points = float(macro.nr_points)
            scream = True
        else:
            yield 0.0

        moveables = [ m.moveable for m in self.moveables ]
        
        point_nb, step = -1, None
        data = self.data
        
        if hasattr(macro, 'getHooks'):
            for hook in macro.getHooks('pre-scan'):
                hook()
                
        self.go_through_waypoints()
        
        
        if hasattr(macro, 'getHooks'):
            for hook in macro.getHooks('post-scan'):
                hook()
        
        env = self._env
        env['acqtime'] = sum_integ_time
        env['delaytime'] = sum_delay
        
        if not scream:
            yield 100.0   

    def cleanup(self):
        '''This method is responsible for restoring state of measurement group 
        and trigger to its state before the scan.'''
        startTimestamp = time.time()

        if self.__mntGrpStarted:
            self.debug("Stopping measurement group")
            try:
                self._measurement_group.stop()
            except Exception, e:
                self.warning("Exception while trying to stop measurement group.")
                self.debug(e)

        if self.__triggerStarted:
            self.debug("Stopping triggers")
            try:
                self.extraTrigger.stop()
            except Exception, e:
                self.warning("Exception while trying to stop trigger.")
                self.debug(e)

        if hasattr(self.macro, 'getHooks'):
            for hook in self.macro.getHooks('pre-cleanup'):
                self.debug("Executing pre-cleanup hook")
                try:
                    hook()
                except Exception, e:
                    self.warning("Exception while trying to execute a pre-cleanup hook")
                    self.debug(e)

        if self.__mntGrpConfigured:
            self.debug("Restoring configuration of measurement group")
            try:
                self._measurement_group.setConfiguration(self.mntGrpConfiguration)
                #TODO: mntGrp configuration should contain also: nrOfTriggers, acqTime, sampling frequency
            except:
                self.warning("Exception while trying to restore measurement group parameters")
                self.debug(e)

        if hasattr(self.macro, 'getHooks'):
            for hook in self.macro.getHooks('post-cleanup'):
                self.debug("Executing post-cleanup hook")
                try:
                    hook()
                except Exception, e:
                    self.warning("Exception while trying to execute a post-cleanup hook")
                    self.debug(e)

        endTimestamp = time.time()
        self.debug("Cleanup took %s time." % repr(endTimestamp - startTimestamp))


class HScan(SScan):
    """Hybrid scan"""
    
    def stepUp(self, n, step, lstep):
        motion, mg = self.motion, self.measurement_group
        startts = self._env['startts']
        
        #pre-move hooks
        for hook in step.get('pre-move-hooks',()):
            hook()
            try:
                step['extrainfo'].update(hook.getStepExtraInfo())
            except InterruptException:
                raise
            except:
                pass
                
        positions, integ_time = step['positions'], step['integ_time']
        
        try:
            m_ID = motion.startMove(positions)
            mg_ID = mg.startCount(integ_time)    
        except InterruptException:
            raise
        except:
            self.dump_information(n, step)
            raise

        try:
            motion.waitMove(id=m_ID)
            mg.waitCount(id=mg_ID)
        except InterruptException:
            raise
        except:
            self.dump_information(n, step)
            raise
        self._sum_acq_time += integ_time
        
        curr_time = time.time()
        dt = curr_time - startts
                
        m_state, m_positions = motion.readState(), motion.readPosition()       
         
        if m_state != Ready:
            self.dump_information(n, step)
            m = "Scan aborted after problematic motion: " \
                "Motion ended with %s\n" % str(m_state)
            raise ScanException({ 'msg' : m })

        data_line = mg.getValues()
        
        # Add final moveable positions
        data_line['point_nb'] = n
        data_line['timestamp'] = dt
        for i, m in enumerate(self.moveables):
            data_line[m.moveable.getName()] = m_positions[i]
        
        #Add extra data coming in the step['extrainfo'] dictionary
        if step.has_key('extrainfo'): data_line.update(step['extrainfo'])
        
        self.data.addRecord(data_line)
    
        #post-step hooks
        for hook in step.get('post-step-hooks',()):
            hook()
            try:
                step['extrainfo'].update(hook.getStepExtraInfo())
            except InterruptException:
                raise
            except:
                pass
        
    def dump_information(self, n, step):
        moveables = self.motion.moveable_list
        msg = ["Report: Stopped at step #" + str(n) + " with:"]
        for moveable in moveables:
            msg.append(moveable.information())
        self.macro.info("\n".join(msg))

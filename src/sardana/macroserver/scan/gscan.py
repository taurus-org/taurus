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
           "GScan", "SScan", "CScan"]

__docformat__ = 'restructuredtext'

import os
import sys
import datetime
import operator
import types
import time

import taurus
from taurus.core.util import Enumeration, USER_NAME, Logger, DebugIt, CaselessList, CaselessDict
from taurus.core.tango import FROM_TANGO_TO_STR_TYPE
from taurus.console.table import Table

from sardana.macroserver.msexception import MacroServerException, UnknownEnv, \
    InterruptException
from sardana.macroserver.msparameter import Type
from scandata import ColumnDesc, MoveableDesc, ScanFactory, ScanDataEnvironment
from recorder import OutputRecorder, JsonRecorder, SharedMemoryRecorder, \
    FileRecorder

from taurus.core.tango.sardana.pool import Ready, Standby, Counting, \
    Acquiring, Moving, Alarm, Fault

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
    
    The generator must be a function yielding a dictionary with the following
    content (minimum) at each step of the scan:
      - 'positions'  : In a step scan, the position where the moveables should go
      - 'integ_time' : In a step scan, a number representing the integration time for the step 
                     (in seconds)
      - 'acq_period' : In a continuous scan, the time between acquisitions
      - 'pre-scan-hooks' : (optional) a sequence of callables to be called in strict order before starting the scan.
      - 'pre-move-hooks' : (optional) a sequence of callables to be called in strict order before starting to move.
      - 'post-move-hooks': (optional) a sequence of callables to be called in strict order after finishing the move.
      - 'pre-acq-hooks'  : (optional) a sequence of callables to be called in strict order before starting to acquire.
      - 'post-acq-hooks' : (optional) a sequence of callables to be called in strict order after finishing acquisition but before recording the step.
      - 'post-step-hooks' : (optional) a sequence of callables to be called in strict order after finishing recording the step.
      - 'post-scan-hooks' : (optional) a sequence of callables to be called in strict order after finishing the scan
      - 'hooks' : (deprecated, use post-acq-hooks instead)
      - 'point_id' : a hashable identifing the scan point.
      - 'check_func' : a callable object callable(moveables, counters)
      - 'extravalues': a dictionary containing the values for each extra info
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
        - 'starttime' : a datetime.datetime representing the start of the scan
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
            mnt_grp = macro.getObj(mnt_grp_name, type_class=Type.MeasurementGroup)
        except UnknownEnv:
            mnt_grps = macro.getObjs(".*", type_class=Type.MeasurementGroup)
            if len(mnt_grps) == 0:
                ScanSetupError('No Measurement Group defined')
            mnt_grp = mnt_grps[0]
            macro.info("ActiveMntGrp not defined. Using %s", mnt_grp)
            macro.setEnv('ActiveMntGrp', mnt_grp.getName())

        if mnt_grp is None:
            raise ScanSetupError('ActiveMntGrp is not defined or has invalid value')

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
        except Exception, envexcept:
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
                          'stored persistently. Use "senv ScanDir '
                          '<abs directory>" to enable it')
            return ()
        try:
            file_names = macro.getEnv('ScanFile')
        except InterruptException:
            raise
        except Exception:
            macro.warning('ScanFile is not defined. This operation will not '
                          'be stored persistently. Use "senv ScanDir <scan '
                          'file(s)>" to enable it')
            return ()
        
        if type(file_names) in types.StringTypes:
            file_names = (file_names,)
        
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
    
    def _getSharedMemoryRecorder(self, id):
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
            ch_nb = len(mg.getChannelNames())
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
            
            if id == 0:
                cols += (ch_nb - oned_nb - twod_nb)    # counter/timer & 0D channel columns
            elif id == 1:
                cols = 1024
                
            if id == 0:
                kwargs.update({ 'program' : macro.getDoorName(),
                                  'array' : "%s_0D" % array_prefix,
                                  'shape' : (cols, 4096) } )
            elif id == 1:
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
                      'user' : USER_NAME, #todo: this should be got from self.measurement_group.getChannelsInfo()
                     'title' : self.macro.getCommand() } )
        
        # Initialize the data_desc list (and add the point number column)
        data_desc = [ ColumnDesc(name='point_nb', label='#Pt No',
                                 dtype='int64') ]
        
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
        label = master['label']
        name = master['name']
        
        #add channels from measurement group
        channels_info = self.measurement_group.getChannelsInfo()
#        import pprint
#        pprint.pprint(channels_info[0].__dict__)
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
            column = ColumnDesc(name=ci.name,
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
        counters.remove(master['name'])
        env['counters'] = counters
        
        for extra_column in self._extra_columns:
            data_desc.append(extra_column.getColumnDesc())
        # add extra columns 
        data_desc += self._extrainfodesc
        env['datadesc'] = data_desc
        
        #take the pre-scan snapshot
        try:
            preScanSnapShot = self.macro.getEnv('PreScanSnapshot')
        except UnknownEnv:
            preScanSnapShot = []
        excludelist = CaselessList(ref_moveables + [ci.name for ci in channels_info]) #we will exclude those that are implied in the scan
        preScanSnapShot = [name for name in preScanSnapShot if name not in excludelist]
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
        import PyTango,numpy
        manager = self.macro.getManager()
        all_elements_info = manager.get_elements_with_interface('Element')
        ret = []
        for src,label in elements:
            try:
                if src in all_elements_info:
                    ei = all_elements_info[src]
                    column = ColumnDesc(name=ei.name,
                                        label=label,
                                        instrument = ei.instrument,
                                        source = ei.source)
                else:
                    column = ColumnDesc(name=src,
                                        label=label,
                                        source=src)
                
                v = PyTango.AttributeProxy(column.source).read().value #@Fixme: Tango-centric. It should work for any Taurus Attribute
                column.pre_scan_value = v
                column.shape = numpy.shape(v)
                column.dtype = getattr(v, 'dtype', numpy.dtype(type(v))).name
                ret.append(column)
            except Exception,e:
                self.macro.warning('Error taking pre-scan snapshot of %s (%s)',label,src)
                self.debug('%s',e)
        return ret

    MAX_ITER = 100000

    def _estimate(self, max_iter=None):
        with_time = hasattr(self.macro, "getTimeEstimation")
        with_interval = hasattr(self.macro, "getIntervalEstimation")
        if with_time and with_interval:
            return self.macro.getTimeEstimation(), self.macro.getIntervalEstimation()
        
        max_iter = max_iter or self.MAX_ITER
        iterator = self.generator()
        total_time = 0.0
        interval_nb = 0
        try:
            if not with_time:
                while interval_nb < max_iter:
                    step = iterator.next()
                    integ_time = step.get("integ_time", 0.0)
                    total_time += integ_time
                    interval_nb += 1
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
        self._env['startts'] = ts = time.time()
        self._env['starttime'] = datetime.datetime.fromtimestamp(ts)
        self.data.start()

    def end(self):
        env = self._env
        env['endts'] = end_ts = time.time()
        env['endtime'] = end = datetime.datetime.fromtimestamp(end_ts)
        total_time = end_ts - env['startts']
        estimated = env['estimatedtime']
        env['deadtime'] = 100.0 * (total_time-estimated) / total_time
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
        for step in self.step_scan(): pass
    
    def step_scan(self):
        self.start()
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
    
    def scan_loop(self):
        raise NotImplementedError('Scan method cannot be called by '
                                  'abstract class')


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
        
        if hasattr(macro, "pre_scan_hooks"):
            for hook in macro.pre_scan_hooks:
                hook()
        
        for i, step in self.steps:
            # allow scan to be stopped between points
            self.macro.checkPoint()
            self.stepUp(i, step, lstep)
            lstep = step
            if scream: yield ((i+1) / nr_points) * 100.0
        
        if hasattr(macro, "post_scan_hooks"):
            for hook in macro.post_scan_hooks:
                hook()

        if not scream: yield 100.0
    
    def stepUp(self, n, step, lstep):
        motion, mg = self.motion, self.measurement_group
        
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
        try:
            state, positions = motion.move(step['positions'])
        except InterruptException:
            raise
        except:
            self.dump_information(n, step)
            raise
        self.debug("[ END ] motion")
        
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
        
        # Acquire data
        self.debug("[START] acquisition")
        state, data_line = mg.count(step['integ_time'])
        for ec in self._extra_columns:
            data_line[ec.getName()] = ec.read()
        self.debug("[ END ] acquisition")
        
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
        tab, dtab = 4*' ', 8*' '
        for moveable in moveables:
            msg.append(moveable.information())
        self.macro.info("\n".join(msg))
        
class CScan(GScan):
    """Continuos scan"""
    
    def __init__(self, macro, waypointGenerator=None, periodGenerator=None,
                 moveables=[], env={}, constraints=[], extrainfodesc=[]):
        GScan.__init__(self, macro, generator=waypointGenerator,
                       moveables=moveables, env=env, constraints=constraints,
                       extrainfodesc=extrainfodesc)
        self._periodGenerator = periodGenerator
        self._stop = False

        #for recorder in self._data_handler.recorders:
        #    recorder.setSaveMode(SaveModes.Block)

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
    
    def go_through_waypoints(self):
        motion, waypoints = self.motion, self.steps
        
        for i, waypoint in waypoints:
            
            #execute pre-move hooks
            for hook in waypoint.get('post-move-hooks',[]): hook()
    
            # move to waypoint 
            motion.move(waypoint['positions'])
            
            #execute post-move hooks
            for hook in waypoint.get('post-move-hooks',[]): hook()
    
        self.stop()
    
    def stop(self):
        self._stop = True
    
    def scan_loop(self):
        motion, mg, waypoints = self.motion, self.measurement_group, self.steps
        macro = self.macro
        manager = macro.getManager()
        
        moveables      = [ m.moveable for m in self.moveables ]
        period_steps   = self.period_steps
        point_nb, step = -1, None
        data           = self.data
        
        if hasattr(macro, "pre_scan_hooks"):
            for hook in macro.pre_scan_hooks:
                hook()
        
        # synchronous move to start position
        i, first_waypoint = waypoints.next()
        motion.move(first_waypoint['positions'])
        
        # configure acquisition (1 month)
        mg.setIntegrationTime(1*60.*60.*24*30)
        
        # start move & acquisition as close as possible
        # from this point on synchronization becomes critical
        manager.add_job(self.go_through_waypoints)
        mg.startCount()
        
        while not self._stop:
            try:
                point_nb, step = period_steps.next()
            except StopIteration, si:
                break
            
            # start/stop Count here according to the 'acquire' key given by 
            #the generator
            
            #execute pre-acq hooks
            for hook in step.get('pre-acq-hooks',[]): hook()
            
            #acquire data and motor positions as close as possible
            #data_line,positions = mg.getValues(force=True), motion.readPosition(force=True)
            data_line, positions = mg.getValues(), motion.readPosition()
            
            #execute post-acq hooks
            for hook in step.get('post-acq-hooks',[]): hook()

            data_line['point_nb'] = point_nb
            for i, m in enumerate(moveables):
                data_line[m.getName()] = positions[i]

            #Add extra data coming in the step['extrainfo'] dictionary
            if step.has_key('extrainfo'): data_line.update(step['extrainfo'])
            data.addRecord(data_line)
            time.sleep(step['acq_period'])
            
        mg.abort()

        if hasattr(macro, "pre_scan_hooks"):
            for hook in macro.post_scan_hooks:
                hook()
    

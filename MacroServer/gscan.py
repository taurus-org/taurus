import os
import sys
import datetime
import operator
import types
import time
import taurus
from taurus.core.util import Enumeration, USER_NAME, Logger, DebugIt
from taurus.core.tango import FROM_TANGO_TO_STR_TYPE

from scan import *
from exception import MacroServerException
from parameter import Type
from pool import Ready, Standby, Counting, Acquiring, Moving, Alarm, Fault

class ScanSetupError(Exception): pass

class ScanException(MacroServerException): pass

class ExtraData(object):
    
    def __init__(self, **kwargs):
        """Expected keywords are:
            - model (str, mandatory): represents data source (ex.: a/b/c/d)
            - label (str, mandatory): column label
            - shape (seq, optional): data shape 
            - dtype (numpy.dtype, optional): data type
            - instrument (str, optional): full instrument name"""
        self._label = kwargs['label']
        self._model = kwargs['model']
        if not kwargs.has_key('dtype'):
            kwargs['dtype'] = self.getType()
        if not kwargs.has_key('shape'):
            kwargs['shape'] = self.getShape()
        self._column = ColumnDesc(**kwargs)
    
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
        except:
            return None

class GScan(Logger):
    """Generic Scan object. 
    The idea is that the scan macros create an instance of this Generic Scan, 
    supplying in the constructor a reference to the macro that created the scan,
    a generator function pointer, a list of moveable items, an extra 
    environment and a sequence of contrains.
    
    The generator must be a function yielding a dictionary with the following
    content (minimum) at each step of the scan:
      - 'positions'  : In a step scan, the position where the moveables should go
      - 'integ_time' : In a step scan, a number representing the integration time for the step 
                     (in seconds)
      - 'acq_period' : In a continuous scan, the time between acquisitions   
      - 'pre-move-hooks' : (optional) a sequence of callables to be called in strict order before starting to move.
      - 'post-move-hooks': (optional) a sequence of callables to be called in strict order after finishing the move.
      - 'pre-acq-hooks'  : (optional) a sequence of callables to be called in strict order before starting to acquire.
      - 'post-acq-hooks' : (optional) a sequence of callables to be called in strict order after finishing to move.
      - 'hooks' : (deprecated, use post-acq-hooks instead)
      - 'point_id' : a hashable identifing the scan point.
      - 'check_func' : a callable object callable(moveables, counters)
      - 'extravalues': a dictionary containing the values for each extra info
                       field. The extra information fields must be described in
                       extradesc (passed in the constructor of the Gscan) 
    
    The moveables must be a sequence of Motion objects.
    
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
        - 'estimatedtime' : a datetime.timedelta representing an estimation for 
                          the duration of the scan
        - 'starttime' : a datetime.datetime representing the start of the scan
        - 'instrumentlist' : a list of Instrument objects containing info
                            about the physical setup of the motors, counters,...
        - <extra environment> given in the constructor
        (at the end of the scan an extra key 'endtime' will be added 
        representing the time at the end of the scan)
        This object is passed to all recorders at the begining and at the end 
        of the scan (when startRecordList and endRecordList is called)
    
    At each step of the scan, for each Recorder, the writeRecord method will
    be called with a Record object as parameter. The Record.data member will be
    a dictionary containing:
      - 'point_nb' : the point number of the scan
      - for each column of the scan (motor or counter), a key with the 
      corresponding column name will contain the value"""
      
    env = ('ActiveMntGrp', 'ExtraColumns' 'ScanDir', 'ScanFile', 'SharedMemory', 'OutputCols')
    
    def __init__(self, macro, generator=None, moveables=[], env={}, constraints=[], extrainfodesc=[]):

        self._macro = macro
        self._generator = generator
        self._moveables = moveables
        self._extrainfodesc = extrainfodesc
        
        name = self.__class__.__name__
        self.call__init__(Logger, name)
        
        # ----------------------------------------------------------------------
        # Setup motion objects
        # ----------------------------------------------------------------------
        self._motion = self.macro.getMotion([ m.getName() for m in moveables])

        # ----------------------------------------------------------------------
        # Find the measurement group
        # ----------------------------------------------------------------------
        mnt_grp_name = self.macro.getEnv('ActiveMntGrp')
        mnt_grp = self.macro.getObj(mnt_grp_name, type_class=Type.MeasurementGroup)

        if mnt_grp is None:
            raise ScanSetupError('ActiveMntGrp is not defined or has invalid value')

        self._master_name = mnt_grp.getTimer()

        if not self._master_name:
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
        
        # The File recorder (if any)
        file_recorder = self._getFileRecorder()
        
        # The Shared memory recorder (if any)
        shm_recorder = self._getSharedMemoryRecorder(0)
        shm_recorder_1d = self._getSharedMemoryRecorder(1)
        
        data_handler.addRecorder(output_recorder)
        data_handler.addRecorder(json_recorder)
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
        except:
            self.macro.info('ExtraColumns is not defined')
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
                except Exception, colexcept:
                    print colexcept
                    try:
                        colname = kw['label']
                    except:
                        colname = str(i)
                    self.macro.warning("Extra column %s is invalid: %s", colname, str(colexcept))
        except Exception, envexcept:
            self.macro.warning('ExtraColumns has invalid value. Must be a sequence of maps')
        return ret

    def _getJsonRecorder(self):
        try:
            json_enabled = self.macro.getEnv('JsonRecorder')
            if json_enabled:
                return JsonRecorder(self.macro)
        except:
            pass
        self.macro.info('JsonRecorder is not defined. Use "senv JsonRecorder True" to enable it')

    def _getOutputRecorder(self):
        cols = None
        try:
            cols = self.macro.getEnv('OutputCols')
        except:
            pass
        return OutputRecorder(self.macro, cols=cols, number_fmt='%g')
    
    def _getFileRecorder(self):
        try:
            p = self.macro.getEnv('ScanDir')
        except:
            self.macro.info('ScanDir is not defined. This operation will not be stored persistently')
            return
        try:
            f = self.macro.getEnv('ScanFile')
        except:
            self.macro.info('ScanFile is not defined. This operation will not be stored persistently')
            return
            
        return FileRecorder( filename=os.path.join(p, f) )
    
    def _getSharedMemoryRecorder(self, id):
        macro, mg, shm = self.macro, self.measurement_group, False
        try:
            shm = macro.getEnv('SharedMemory')
        except Exception,e:
            self.macro.info('SharedMemory is not defined.')
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
            except:
                oned_nb = 0
            twod_nb = 0
            try:
                twod_nb = len(mg.TwoDExpChannels)
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
            self.macro.info('SharedMemory %s is not available'%shm)
        return shmRecorder
    
    def _secsToTimedelta(self, secs):
        days, secs = divmod(secs, 86400)
        # we don't have to care about microseconds because if secs is a float
        # timedelta will do it for us
        return datetime.timedelta(days, secs)
    
    def _timedeltaToSecs(self, td):
        return 86400*td.days + td.seconds + 1E-6*td.microseconds
    
    def _setupEnvironment(self, additional_env):
        env = ScanDataEnvironment(
                { 'serialno' : ScanFactory().getSerialNo(),
                      'user' : USER_NAME, 
                     'title' : self.macro.getCommand() } )
        
        # add point no column
        data_desc = [ ColumnDesc(label='point_nb', dtype='int64') ]
        
        # add motor columns
        for moveable in self.moveables:
            instrument = moveable.getInstrument()
            data_desc.append( ColumnDesc(label=moveable.getName(), instrument=instrument) )
        
        # add master column
        ch_obj = self.measurement_group.getChannelObj(self._master_name)
        instrument = ch_obj.getInstrument()
        data_desc.append( ColumnDesc(label=self._master_name, instrument=instrument) )
        #TODO: maybe we want to include the nxpath in the instrument as well????
        
        # add counters
        for ch_name in self.measurement_group.getCounterNames():
            ch_attr = self.measurement_group.getAttrObj("%s_value" % ch_name)
            type = FROM_TANGO_TO_STR_TYPE[ch_attr.getType()]
            shape = ch_attr.getShape()
            ch_obj = self.measurement_group.getChannelObj(ch_name)
            instrument = ch_obj.getInstrument()
            data_desc.append( ColumnDesc(label=ch_name, dtype=type, shape=shape, instrument=instrument) )
        
        for extra_column in self._extra_columns:
            data_desc.append(extra_column.getColumnDesc())
            
        # add extra columns 
        data_desc += self._extrainfodesc
        
        env['macro_id'] = self.macro.getID()
        env['datadesc'] = data_desc
        env['estimatedtime'] = self._calculateTotalAcquisitionTime()
        ##@TODO: (when Pool supports Instruments) uncomment following line 
        env['instrumentlist'] = self._macro.findObjs('.*', type_class=Type.Instrument) 
        

        env.update(additional_env)
        self._env = env
        
        # Give the environment to the ScanData
        self.data.setEnviron(env)

    def _calculateTotalAcquisitionTime(self):
        total_time = datetime.timedelta()
        if hasattr(self.macro, "getTimeEstimation"):
            total_time = self.macro.getTimeEstimation()
        return total_time

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
        self._env['starttime'] = datetime.datetime.now()
        self.data.start()

    def end(self):
        self._env['endtime'] = datetime.datetime.now()
        self.data.end()

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
        raise RuntimeError('Scan method cannot be called by abstract class')

    
class SScan(GScan):

    def scan_loop(self):
        lstep = None
        
        scream = False
        if hasattr(self.macro, "nr_points"):
            nr_points = float(self.macro.nr_points)
            scream = True
        else:
            yield 0.0
            
        for i, step in self.steps:
            self.stepUp(i, step, lstep)
            lstep = step
            if scream: yield ((i+1) / nr_points) * 100.0
    
        if not scream: yield 100.0
    
    def stepUp(self, n, step, lstep):
        motion, mg = self.motion, self.measurement_group
        
        #pre-move hooks
        for hook in step.get('pre-move-hooks',[]):
            hook()
            try: step['extrainfo'].update(hook.getStepExtraInfo())
            except: pass
        
        # Move
        self.debug("[START] motion")
        state, positions = motion.move(step['positions'])
        self.debug("[ END ] motion")
        
        #post-move hooks
        for hook in step.get('post-move-hooks',[]):
            hook()
            try: step['extrainfo'].update(hook.getStepExtraInfo())
            except: pass
        
        if state != Ready:
            m = "Scan aborted after problematic motion: " \
                "Motion ended with %s\n" % str(state)
            raise ScanException({ 'msg' : m })
        
        #pre-acq hooks
        for hook in step.get('pre-acq-hooks',[]):
            hook()
            try: step['extrainfo'].update(hook.getStepExtraInfo())
            except: pass
        
        # Acquire data
        self.debug("[START] acquisition")
        state, data_line = mg.count(step['integ_time'])
        for ec in self._extra_columns:
            data_line[ec.getName()] = ec.read() 
        self.debug("[ END ] acquisition")
        
        #post-acq hooks
        for hook in step.get('post-acq-hooks',[]):
            hook()
            try: step['extrainfo'].update(hook.getStepExtraInfo())
            except: pass
        
        #hooks for backwards compatibility:
        if step.has_key('hooks'):
            self.macro.info('Deprecation warning: you should use "post-acq-hooks" instead of "hooks" in the step generator')
            for hook in step.get('hooks',[]):
                hook()
                try: step['extrainfo'].update(hook.getStepExtraInfo())
                except: pass
        
        # Add final moveable positions
        data_line['point_nb'] = n
        for i, m in enumerate(self.moveables):
            data_line[m.getName()] = positions[i]
        
        #Add extra data coming in the step['extrainfo'] dictionary
        if step.has_key('extrainfo'): data_line.update(step['extrainfo'])
        
        self.data.addRecord(data_line)


class CScan(GScan):
    
    def __init__(self, macro, waypointGenerator=None, periodGenerator=None, moveables=[], env={}, constraints=[], extrainfodesc=[]):
        GScan.__init__(self, macro, generator=waypointGenerator, moveables=moveables, env=env, constraints=constraints, extrainfodesc=extrainfodesc)
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
        manager = self.macro.getManager()

        moveables      = self.moveables
        period_steps   = self.period_steps
        point_nb, step = -1, None
        data           = self.data
        
        # synchronous move to start position
        i, first_waypoint = waypoints.next()
        motion.move(first_waypoint['positions'])
        
        # configure acquisition (1 month)
        mg.setIntegrationTime(1*60.*60.*24*30)
        
        # start move & acquisition as close as possible
        # from this point on synchronization becomes critical
        manager.addJob(self.go_through_waypoints)
        mg.startCount()
        
        while not self._stop:
            try:
                point_nb, step = period_steps.next()
            except StopIteration, si:
                break
            
            # start/stop Count here according to the 'acquire' key given by the generator
            
            #execute pre-acq hooks
            for hook in step.get('pre-acq-hooks',[]): hook()
            
            #acquire data and motor positions as close as possible
            #data_line,positions = mg.getValues(force=True), motion.readPosition(force=True)
            data_line,positions = mg.getValues(), motion.readPosition()
            
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

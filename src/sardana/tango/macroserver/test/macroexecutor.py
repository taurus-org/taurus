import copy
import threading
import PyTango
from sardana.macroserver.macros.test import BaseMacroExecutor
# TODO: not sure if use this codecs, or prepare some easy one...
from taurus.core.util.codecs import CodecFactory
from sardana import sardanacustomsettings

class TangoAttrCb(object):

    def __init__(self, tango_macro_executor):
        self._tango_macro_executor = tango_macro_executor
        
class TangoResultCb(TangoAttrCb):
    '''Callback class for Tango evnts of the Result attribute'''
    
    def push_event(self, *args, **kwargs):
        event_data = args[0]
        if event_data.err:
            result = event_data.errors
        else:
            result = event_data.attr_value.value
            #print 'TangoResultCb.push_event: result = ', result
        self._tango_macro_executor._result = result


class TangoLogCb(TangoAttrCb):
    '''Callback class for Tango events of the log attributes 
    e.g. Output, Error, Critical
    '''

    def __init__(self, tango_macro_executor, log_name):
        self._tango_macro_executor = tango_macro_executor
        self._log_name = log_name

    def push_event(self, *args, **kwargs):
        event_data = args[0]
        if event_data.attr_value:
            log = event_data.attr_value.value
            log_buffer_name = '_%s' % self._log_name
            log_buffer = getattr(self._tango_macro_executor, log_buffer_name) 
            log_buffer.append(log)
            common_buffer = self._tango_macro_executor._common
            if common_buffer != None:
                common_buffer.append(log)


class TangoStatusCb(TangoAttrCb):
    '''Callback class for Tango events of the MacroStatus attribute'''
    
    START_STATES = [u'start']
    DONE_STATES = [u'finish', u'stop', u'exception']

    def push_event(self, *args, **kwargs):
        event_data = args[0]
        if event_data.err:
            self._state_buffer = event_data.errors
            self._tango_macro_executor._done_event.set()
        # make sure we get it as string since PyTango 7.1.4 returns a buffer
        # object and json.loads doesn't support buffer objects (only str)
        attr_value = event_data.attr_value
        v = map(str, attr_value.value)
        if not len(v[1]):
            return
        format = v[0]
        codec = CodecFactory().getCodec(format)

        # make sure we get it as string since PyTango 7.1.4 returns a buffer
        # object and json.loads doesn't support buffer objects (only str)
        v[1] = str(v[1])
        fmt, data = codec.decode(v)
        for macro_status in data:
            state = macro_status['state']
            self._tango_macro_executor._exception = macro_status.get('exc_type')
            if state in self.START_STATES:
                #print 'TangoStatusCb.push_event: setting _started_event'
                self._tango_macro_executor._started_event.set()
            elif state in self.DONE_STATES:
                #print 'TangoStatusCb.push_event: setting _done_event %s' %(state)
                self._tango_macro_executor._done_event.set()
            #else:
            #    print 'State %s' %(state)
            self._tango_macro_executor._state_buffer.append(state)


class TangoMacroExecutor(BaseMacroExecutor):
    '''Macro executor implemented using Tango communication with the Door device
    '''

    def __init__(self, door_name=None):
        super(TangoMacroExecutor, self).__init__()
        if door_name == None:
            door_name = getattr(sardanacustomsettings,'UNITTEST_DOOR_NAME')
        self._door = PyTango.DeviceProxy(door_name)
        self._done_event = None
        self._started_event = None
#        #self.log_levels.append('recorddata')
#        #self._recorddata = []
        
    def _clean(self):
        '''Recreates threading Events in case the macro executor is reused.'''        
        super(TangoMacroExecutor, self)._clean()
        self._started_event = threading.Event() 
        self._done_event = threading.Event()
    
    def _run(self, macro_name, macro_params):
        #import pdb; pdb.set_trace()
        # preaparing RunMacro command input arguments 
        argin = copy.copy(macro_params)
        argin.insert(0, macro_name)
        # registering for MacroStatus events
        status_cb = TangoStatusCb(self)
        self._status_id = self._door.subscribe_event('macrostatus',
                                               PyTango.EventType.CHANGE_EVENT, 
                                               status_cb)

        # executing RunMacro command
        self._door.RunMacro(argin)

    def _wait(self, timeout):
        if self._done_event: 
            self._done_event.wait(timeout)
            self._door.unsubscribe_event(self._status_id)

    def _stop(self, timeout):
        #self._started_event.wait(timeout) #it should be stop_delay
        try:
            self._door.StopMacro()
        except PyTango.DevFailed, e:
            #TODO: what to do with Exceptions???
            print 'DevFailed exception was thrown: ', e
        except Exception, e:
            print 'Exception was thrown: ', e
            
    def _registerLog(self, log_level):
        log_cb = TangoLogCb(self, log_level)
        id_log_name = '_%s_id' % log_level
        id_log =  self._door.subscribe_event(log_level,
                                             PyTango.EventType.CHANGE_EVENT, 
                                             log_cb)
        #print 'subscribed %s with id %d' % (log_level, id_log)
        setattr(self, id_log_name, id_log)
        
    def _unregisterLog(self, log_level):
        id_log_name = '_%s_id' % log_level
        id_log = getattr(self, id_log_name)
        self._door.unsubscribe_event(id_log)
        
    def _registerResult(self):
        result_cb = TangoResultCb(self)
        self._result_id = self._door.subscribe_event('result',
                                               PyTango.EventType.CHANGE_EVENT, 
                                               result_cb)
    
    def _unregisterResult(self):
        self._door.unsubscribe_event(self._result_id)

    def getData(self):
        data = self._door.RecordData
        return CodecFactory().decode(data)


if __name__ == '__main__':
    door_name = getattr(sardanacustomsettings,'UNITTEST_DOOR_NAME')
    testTangoMacroExecutorRunLsm(door_name)

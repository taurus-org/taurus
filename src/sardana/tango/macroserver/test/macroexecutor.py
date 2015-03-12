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

import copy
import threading
import PyTango
from sardana.macroserver.macros.test import BaseMacroExecutor
from taurus.core.util.codecs import CodecFactory
from sardana import sardanacustomsettings


class TangoAttrCb(object):

    '''An abstract callback class for Tango events'''

    def __init__(self, tango_macro_executor):
        self._tango_macro_executor = tango_macro_executor


class TangoResultCb(TangoAttrCb):

    '''Callback class for Tango events of the Result attribute'''

    def push_event(self, *args, **kwargs):
        '''callback method receiving the event'''
        event_data = args[0]
        if event_data.err:
            result = event_data.errors
        else:
            result = event_data.attr_value.value
        self._tango_macro_executor._result = result


class TangoLogCb(TangoAttrCb):

    '''Callback class for Tango events of the log attributes
    e.g. Output, Error, Critical
    '''

    def __init__(self, tango_macro_executor, log_name):
        self._tango_macro_executor = tango_macro_executor
        self._log_name = log_name

    def push_event(self, *args, **kwargs):
        '''callback method receiving the event'''
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

    START_STATES = ['start']
    DONE_STATES = ['finish', 'stop', 'exception']

    def push_event(self, *args, **kwargs):
        '''callback method receiving the event'''
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
        fmt = v[0]
        codec = CodecFactory().getCodec(fmt)

        # make sure we get it as string since PyTango 7.1.4 returns a buffer
        # object and json.loads doesn't support buffer objects (only str)
        v[1] = str(v[1])
        fmt, data = codec.decode(v)
        for macro_status in data:
            state = macro_status['state']
            self._tango_macro_executor._exception = macro_status.get(
                'exc_type')
            if state in self.START_STATES:
                #print 'TangoStatusCb.push_event: setting _started_event'
                self._tango_macro_executor._started_event.set()
            elif state in self.DONE_STATES:
                # print 'TangoStatusCb.push_event: setting _done_event %s'
                # %(state)
                self._tango_macro_executor._done_event.set()
            #else:
            #    print 'State %s' %(state)
            self._tango_macro_executor._state_buffer.append(state)


class TangoMacroExecutor(BaseMacroExecutor):

    '''
    Macro executor implemented using Tango communication with the Door device
    '''

    def __init__(self, door_name=None):
        super(TangoMacroExecutor, self).__init__()
        if door_name == None:
            door_name = getattr(sardanacustomsettings, 'UNITTEST_DOOR_NAME')
        self._door = PyTango.DeviceProxy(door_name)
        self._done_event = None
        self._started_event = None

    def _clean(self):
        '''Recreates threading Events in case the macro executor is reused.'''
        super(TangoMacroExecutor, self)._clean()
        self._started_event = threading.Event()
        self._done_event = threading.Event()

    def _run(self, macro_name, macro_params):
        '''reimplemented from :class:`BaseMacroExecutor`'''
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
        '''reimplemented from :class:`BaseMacroExecutor`'''
        #TODO: In case of timeout = inf if the macro excecutor run a macro
        # with wrong parameters it'll never awake of the done_event wait
        # Pending to remove this comment when Sardana resolves the bug.
        if self._done_event:
            self._done_event.wait(timeout)
            self._door.unsubscribe_event(self._status_id)

    def _stop(self, started_event_timeout=3.0):
        '''reimplemented from :class:`BaseMacroExecutor`'''
        self._started_event.wait(started_event_timeout)
        try:
            self._door.StopMacro()
        except PyTango.DevFailed as e:
            raise Exception("Unable to Stop macro: %s" % e)

    def _registerLog(self, log_level):
        '''reimplemented from :class:`BaseMacroExecutor`'''
        log_cb = TangoLogCb(self, log_level)
        id_log_name = '_%s_id' % log_level
        id_log = self._door.subscribe_event(log_level,
                                            PyTango.EventType.CHANGE_EVENT,
                                            log_cb)
        setattr(self, id_log_name, id_log)

    def _unregisterLog(self, log_level):
        '''reimplemented from :class:`BaseMacroExecutor`'''
        id_log_name = '_%s_id' % log_level
        id_log = getattr(self, id_log_name)
        self._door.unsubscribe_event(id_log)

    def _registerResult(self):
        '''reimplemented from :class:`BaseMacroExecutor`'''
        result_cb = TangoResultCb(self)
        self._result_id = self._door.subscribe_event('result',
                                                     PyTango.EventType.CHANGE_EVENT,
                                                     result_cb)

    def _unregisterResult(self):
        '''reimplemented from :class:`BaseMacroExecutor`'''
        self._door.unsubscribe_event(self._result_id)

    def getData(self):
        '''Returns the data object for the last executed macro

        :return: (obj)
        '''
        data = self._door.RecordData
        return CodecFactory().decode(data)

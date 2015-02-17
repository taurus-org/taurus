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

"""This module contains the class definition for the macro server door"""

__all__ = ["MacroProxy", "BaseInputHandler", "MSDoor"]

__docformat__ = 'restructuredtext'

import weakref
import collections

from taurus.core.util.log import Logger

from sardana import ElementType
from sardana.sardanaevent import EventType

from sardana.macroserver.msbase import MSObject
from sardana.macroserver.msparameter import Type
from sardana.macroserver.msexception import MacroServerException


class MacroProxy(object):

    def __init__(self, door, macro_meta):
        self._door = weakref.ref(door)
        self._macro_meta = weakref.ref(macro_meta)

    @property
    def door(self):
        return self._door()

    @property
    def macro_info(self):
        return self._macro_meta()

    def __call__(self, *args, **kwargs):
        door = self.door
        parent_macro = door.get_running_macro()
        parent_macro.syncLog()
        executor = parent_macro.executor
        opts = dict(parent_macro=parent_macro, executor=executor)
        kwargs.update(opts)
        eargs = [self.macro_info.name]
        eargs.extend(args)
        return parent_macro.execMacro(*eargs, **kwargs)


class MacroProxyCache(dict):

    def __init__(self, door):
        self._door = weakref.ref(door)
        self.rebuild()

    @property
    def door(self):
        return self._door()

    def rebuild(self):
        self.clear()
        door = self.door
        macros = self.door.get_macros()
        for macro_name, macro_meta in macros.items():
            self[macro_name] = MacroProxy(door, macro_meta)


class BaseInputHandler(object):

    def __init__(self):
        try:
            self._input = raw_input
        except NameError:
            self._input = input

    def input(self, input_data=None):
        if input_data is None:
            input_data = {}
        prompt = input_data.get('prompt')
        if prompt is None:
            return self._input()
        else:
            return self._input(prompt)


class MSDoor(MSObject):
    """Sardana door object"""

    def __init__(self, **kwargs):
        self._state = None
        self._status = None
        self._result = None
        self._macro_status = None
        self._record_data = None
        self._macro_proxy_cache = None
        self._input_handler = BaseInputHandler()
        self._pylab_handler = None
        kwargs['elem_type'] = ElementType.Door
        MSObject.__init__(self, **kwargs)

    def get_macro_executor(self):
        return self.macro_server.macro_manager.getMacroExecutor(self)

    macro_executor = property(get_macro_executor)

    def get_running_macro(self):
        return self.macro_executor.getRunningMacro()

    running_macro = property(get_running_macro)

    def get_macro_data(self):
        macro = self.running_macro
        if macro is None:
            raise MacroServerException("No macro has run so far " + \
                            "or the macro data was not preserved.")
        data = macro.data
        return data

    def set_pylab_handler(self, ph):
        self._pylab_handler = ph

    def get_pylab_handler(self):
        return self._pylab_handler

    pylab_handler = property(get_pylab_handler, set_pylab_handler)

    def get_pylab(self):
        ph = self.pylab_handler
        if ph is None:
            import matplotlib.pylab
            ph = matplotlib.pylab
        return ph

    pylab = property(get_pylab)

    def set_pyplot_handler(self, ph):
        self._pyplot_handler = ph

    def get_pyplot_handler(self):
        return self._pyplot_handler

    pyplot_handler = property(get_pyplot_handler, set_pyplot_handler)

    def get_pyplot(self):
        ph = self.pyplot_handler
        if ph is None:
            import matplotlib.pyplot
            ph = matplotlib.pyplot
        return ph

    pyplot = property(get_pyplot)

    def set_input_handler(self, ih):
        self._input_handler = ih

    def get_input_handler(self):
        return self._input_handler

    input_handler = property(get_input_handler, set_input_handler)

    def append_prompt(self, prompt, msg):
        if '?' in prompt:
            prefix, suffix = prompt.rsplit('?', 1)
            if not prefix.endswith(' '):
                prefix += ' '
            prompt = prefix + msg + '?' + suffix
        else:
            prompt += msg + ' '
        return prompt

    def input(self, msg, *args, **kwargs):
        kwargs['data_type'] = kwargs.get('data_type', Type.String)
        kwargs['allow_multiple'] = kwargs.get('allow_multiple', False)

        if args:
            msg = msg % args
        if not msg.endswith(' '):
            msg += ' '
        dv = kwargs.get('default_value')
        if dv is not None:
            dv = '[' + str(dv) + ']'
            msg = self.append_prompt(msg, dv)

        macro = kwargs.pop('macro', self.macro_executor.getRunningMacro())
        if macro is None:
            macro = self

        input_data = dict(prompt=msg, type='input')
        input_data.update(kwargs)
        data_type = kwargs['data_type']
        is_seq = not isinstance(data_type, (str, unicode)) and \
                 isinstance(data_type, collections.Sequence)
        if is_seq:
            handle = self._handle_seq_input
        else:
            handle = self._handle_type_input

        return handle(macro, input_data, data_type)

    def _handle_seq_input(self, obj, input_data, data_type):
        valid = False
        allow_multiple = input_data['allow_multiple']
        while not valid:
            result = self.input_handler.input(input_data)
            if allow_multiple:
                r, dt = set(result), set(data_type)
                if r.issubset(dt):
                    break
            else:
                if result in data_type:
                    break
            obj.warning("Please give a valid option")
        return result

    def _handle_type_input(self, obj, input_data, data_type):
        type_obj = self.type_manager.getTypeObj(data_type)

        valid = False
        while not valid:
            result = self.input_handler.input(input_data)
            try:
                result_type = type_obj.getObj(result)
                if result_type is None:
                    raise Exception("Must give a value")
                valid = True
                return result_type
            except:
                dtype = str(data_type).lower()
                obj.warning("Please give a valid %s.", dtype)

    def get_report_logger(self):
        return self.macro_server.report_logger

    report_logger = property(get_report_logger)

    def report(self, msg, *args, **kwargs):
        """
        Record a log message in the sardana report (if enabled) with default
        level **INFO**. The msg is the message format string, and the args are
        the arguments which are merged into msg using the string formatting
        operator. (Note that this means that you can use keywords in the
        format string, together with a single dictionary argument.)

        *kwargs* are the same as :meth:`logging.Logger.debug` plus an optional
        level kwargs which has default value **INFO**

        Example::

            self.report("this is an official report!")

        :param msg: the message to be recorded
        :type msg: :obj:`str`
        :param args: list of arguments
        :param kwargs: list of keyword arguments"""
        return self.macro_server.report(msg, *args, **kwargs)

    def get_state(self):
        return self._state

    def set_state(self, state, propagate=1):
        self._state = state
        self.fire_event(EventType("state", priority=propagate), state)

    state = property(get_state, set_state)

    def get_status(self):
        return self._status

    def set_status(self, status, propagate=1):
        self._status = status
        self.fire_event(EventType("status", priority=propagate), status)

    status = property(get_status, set_status)

    def get_result(self):
        return self._result

    def set_result(self, result, propagate=1):
        self._result = result
        self.fire_event(EventType("result", priority=propagate), result)

    result = property(get_result, set_result)

    def get_macro_status(self):
        return self._macro_status

    def set_macro_status(self, macro_status, propagate=1):
        self._macro_status = macro_status
        self.fire_event(EventType("macrostatus", priority=propagate),
                        macro_status)

    result = property(get_result, set_result)

    def get_record_data(self):
        return self._record_data

    def set_record_data(self, record_data, codec=None, propagate=1):
        self._record_data = record_data
        self.fire_event(EventType("recorddata", priority=propagate),
                        (codec, record_data))

    record_data = property(get_record_data, set_record_data)

    def get_env(self, key=None, macro_name=None):
        """Gets the environment with the context for this door matching the
        given parameters:

        - macro_name defines the context where to look for the environment. If
          None, the global environment is used. If macro name is given the
          environment in the context of that macro is given
        - If key is None it returns the complete environment, otherwise
          key must be a string containing the environment variable name.

        :param key:
            environment variable name [default: None, meaning all environment]
        :type key: str
        :param macro_name:
            local context for a given macro [default: None, meaning no macro
            context is used]
        :type macro_name: str

        :raises: UnknownEnv"""
        return self.macro_server.environment_manager.getAllDoorEnv(self.name)

    def set_env(self, key, value):
        return self.macro_server.set_env(key, value)

    def _build_macro_proxy_cache(self):
        self._macro_proxy_cache = MacroProxyCache(self)

    def get_macro_proxies(self):
        if self._macro_proxy_cache is None:
            self._macro_proxy_cache = MacroProxyCache(self)
        return self._macro_proxy_cache

    def run_macro(self, par_str_list, asynch=False):
        if isinstance(par_str_list, (str, unicode)):
            par_str_list = par_str_list,

        if not hasattr(self, "Output"):
            import sys
            import logging
            Logger.addLevelName(15, "OUTPUT")

            def output(loggable, msg, *args, **kw):
                loggable.getLogObj().log(Logger.Output, msg, *args, **kw)
            Logger.output = output

            Logger.disableLogOutput()
            Logger.setLogLevel(Logger.Output)
            #filter = taurus.core.util.LogFilter(level=Logger.Output)
            formatter = logging.Formatter(fmt="%(message)s")
            Logger.setLogFormat("%(message)s")
            handler = logging.StreamHandler(stream=sys.stdout)
            #handler.addFilter(filter)
            Logger.addRootLogHandler(handler)
            #handler.setFormatter(formatter)
            #logger.addHandler(handler)
            #logger.addFilter(filter)
            self.__logging_info = handler, filter, formatter

            # result of a macro
            #Logger.addLevelName(18, "RESULT")

        return self.macro_executor.run(par_str_list, asynch=asynch)

    def __getattr__(self, name):
        """Get methods from macro server"""
        return getattr(self.macro_server, name)

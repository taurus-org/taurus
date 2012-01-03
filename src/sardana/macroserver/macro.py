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

from __future__ import with_statement

__all__ = ["OverloadPrint", "PauseEvent", "Hookable", "ExecMacroHook",
           "MacroFinder", "Macro", "Type", "ParamRepeat"]

__docformat__ = 'restructuredtext'

import threading
import traceback
import time
import sys
import operator
import types
import weakref
import functools
import textwrap

from PyTango import DevState
from taurus.core.util import Logger, CodecFactory, propertx

from taurus.core.tango.sardana.pool import PoolElement

from parameter import Type, ParamType, ParamRepeat
from exception import MacroServerException, AbortException, \
    MacroWrongParameterType, UnknownEnv


class OverloadPrint(object):
    
    def __init__(self, m):
        self._macro = m
        self._accum = ""
    
    def __enter__(self):
        self.stdout = sys.stdout
        sys.stdout = self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()
        sys.stdout = self.stdout
    
    def write(self, s):
        self._accum += s
        # while there is no new line, just accumulate the buffer
        try:
            if s[-1] == '\n' or s.index('\n') >= 0:
                self.flush()
        except ValueError:
            pass
        
    def flush(self):
        b = self._accum
        if b is None or len(self._accum) == 0:
            return
        #take the '\n' because the output is a list of strings, each to be
        #interpreted as a separate line in the client
        if b[-1] == '\n': b = b[:-1]
        self._macro.output(b)
        self._accum = ""


class PauseEvent(Logger):
    
    def __init__(self, macro_obj):
        self._name = self.__class__.__name__
        self._pause_cb = None
        self._resume_cb = None
        self._macro_obj_wr = weakref.ref(macro_obj)
        self._macro_name = macro_obj._getName()
        Logger.__init__(self, "Macro_%s %s" % (self._macro_name, self._name))
        # we create an event object that is automatically set
        self._event = threading.Event()
        self._event.set()
    
    @property
    def macro_obj(self):
        return self._macro_obj_wr()
    
    def pause(self, cb=None):
        self.debug("[START] Pause")
        self._pause_cb = cb
        self._event.clear()
        self.debug("[ END ] Pause")
        
    def resume(self, cb=None):
        if self.isPaused():
            self.debug("[START] Resume")
            self._resume_cb = cb
            self._event.set()
            self.debug("[ END ] Resume")

    def wait(self,timeout=None):
        pauseit = not self._event.isSet()
        if pauseit and self._pause_cb is not None:
            self._pause_cb(self.macro_obj)
        self._event.wait(timeout)
        if pauseit and self._resume_cb is not None:
            self._resume_cb(self.macro_obj)
        
    def isPaused(self):
        return not self._event.isSet()


class Hookable(Logger):
    
    # avoid creating an __init__
    
    def _getHooks(self):
        try:
            return self._hooks
        except:
            self._hooks = []
        return self._hooks
    
    def _getHookHintsDict(self):
        try:
            return self._hookHintsDict
        except:
            self._hookHintsDict = {'_ALL_':[], '_NOHINTS_':[]}
        return self._hookHintsDict
    
    def getAllowedHookHints(self):
        return self.__class__.hints.get('allowsHooks')
    
    def getHints(self):
        return self._getHookHintsDict().keys()
    
    def getHooks(self, hint=None):
        '''This will return a list of hooks that have the given hint. Two reserved
        hints are always valid:
          - "_ALL_": which contains all the hooks
          - "_NOHINTS_": which contains the hooks that don't provide any hint
        
        :param hint: (str) a hint. If None is passed, it returns a list of
                     (hook,hints) tuples
        
        :return: (list) an ordered list of hooks that have the given hint
        ''' 
        if hint is None:
            return self._getHooks()
        else:
            return self._getHookHintsDict().get(hint,[])
        
    @propertx
    def hooks():
        def get(self):
            return self._getHooks()
                
        def set(self, hooks):
            '''hooks must be list<callable,list<str>>. Exceptionally, for
            backwards compatibility, list<callable> is also admitted, but may
            not be supported in the future.
            "two variables are created:
                - self._hooks (list<callable,list<str>>) (will be a tuple
                              regardless of what was passed)
                - self._hookHintsDict (dict<str,list>) a dict of key=hint and
                                      value=list of hooks with that hint.
                                      self._hookHintsDict also stores two
                                      special keys: "_ALL_": which contains all
                                      the hooks "_NOHINTS_": which contains the
                                      hooks that don't provide hints
            '''
            if not isinstance(hooks, list):
                self.error('the hooks must be passed as a list<callable,list<str>>')
                return
            
            #store self._hooks, making sure it is of type: list<callable,list<str>>
            self._hooks = []
            for h in hooks: 
                if  isinstance(h,(tuple, list)) and len(h)==2:
                    self._hooks.append(h)
                else: #we assume that hooks is a list<callable>
                    self._hooks.append((h,[]))
                    self.info('Deprecation warning: hooks should be set with a list of hints. See Hookable API docs')
                    
            #create _hookHintsDict
            all = self._getHookHintsDict()['_ALL_'] = zip(*self._hooks)[0]
            nohints = self._hookHintsDict['_NOHINTS_']
            for hook,hints in self._hooks:
                if len(hints) == 0:
                    nohints.append(hook)
                else:
                    for hint in hints:
                        try:
                            self._hookHintsDict[hint].append(hook)
                        except KeyError:
                            self._hookHintsDict[hint] = [hook] 
        return get,set


class ExecMacroHook(object):
    """A speciallized callable hook for executing a sub macro inside another
    macro as a hook"""
    
    def __init__(self, parent_macro, *pars, **kwargs):
        self._macro_obj_wr = weakref.ref(parent_macro)
        self._pars = pars
        self._opts = kwargs
        
    @property
    def macro_obj(self):
        return self._macro_obj_wr()

    def __call__(self):
        self.macro_obj.execMacro(*self._pars, **self._opts)


class MacroFinder:
    
    def __init__(self, macro_obj):
        self._macro_obj_wr = weakref.ref(macro_obj)

    @property
    def macro_obj(self):
        return self._macro_obj_wr()

    def __getattr__(self, name):
        
        def f(*args, **kwargs):
            p_m = self.macro_obj
            p_m.syncLog()
            opts = { 'parent_macro' : p_m, 
                     'executor'     : p_m.getExecutor() }
            kwargs.update(opts)
            eargs = [name]
            eargs.extend(args)
            return p_m.execMacro(*eargs, **kwargs)
        
        setattr(self, name, f)
        
        return f

def mAPI(fn):
    """Wraps the given Macro method as being protected by the abort procedure.
    To be used by the :class:`Macro` as a decorator for all methods.
    :param: macro method
    :return: wrapped macro method"""
    @functools.wraps(fn)
    def new_fn(*args, **kwargs):
        self = args[0]
        is_macro_th = self._macro_thread == threading.current_thread()
        if self._shouldRaiseAbortException():
            if is_macro_th:
                self.setProcessingAbort(True)
            raise AbortException("aborted before calling %s" % fn.__name__)
        ret = fn(*args, **kwargs)
        if self._shouldRaiseAbortException():
            if is_macro_th:
                self.setProcessingAbort(True)
            raise AbortException("aborted after calling %s" % fn.__name__)
        return ret
    return new_fn


class Macro(Logger):
    """ The Macro base class. All macros should inherit directly or indirectly
    from this class."""

    # States
    Init     = DevState.INIT
    Running  = DevState.RUNNING
    Pause    = DevState.STANDBY
    Stop     = DevState.STANDBY
    Fault    = DevState.FAULT
    Finished = DevState.ON
    Ready    = DevState.ON
    Abort    = DevState.ALARM

    All      = ParamType.All
    
    BlockStart = '<BLOCK>'
    BlockFinish = '</BLOCK>'

    #: This property holds the macro parameter description.
    #: It consists of a sequence of parameter information objects.
    #: A parameter information object is either:
    #:
    #:    #. a simple parameter object
    #:    #. a parameter repetition object
    #:
    #: A simple parameter object is a sequence of:
    #:
    #:    #. a string representing the parameter name
    #:    #. a member of :obj:`Macro.Type` representing the parameter data type
    #:    #. a default value for the parameter or None if there is no default value
    #:    #. a string with the parameter description
    #:
    #: Example::
    #:
    #:     param_def = ( ('value', Type.Float, None, 'a float parameter' ) )
    #:
    #: A parameter repetition object is a sequence of:
    #:
    #:    #. a string representing the parameter repetition name
    #:    #. a sequence of parameter information objects
    #:    #. a dictionary representing the parameter repetition semantics or None
    #:       to use the default parameter repetition semantics. Dictionary keys are:
    #:
    #:           * *min* - integer representing minimum number of repetitions or None
    #:             for no minimum.
    #:           * *max* - integer representing maximum number of repetitions or None
    #:             for no maximum.
    #:
    #:       Default parameter repetition semantics is ``{ 'min': 1, 'max' : None }``
    #:       (in other words, "at least one repetition" semantics)
    #:
    #: Example::
    #:
    #:     param_def = (
    #:         ( 'motor_list', ( ( 'motor', Type.Motor, None, 'motor name') ), None, 'List of motors')
    #:     )
    param_def = []

    result_def = []
    hints = {}
    env = ()
    
    def __init__(self, *args, **kwargs):
        """Constructor"""
        self._name = kwargs.get('as', self.__class__.__name__)
        self._in_pars = args
        self._out_pars = None
        self._aborted = False
        self._processingAbort = False
        self._parent_macro = kwargs.get('parent_macro')
        self._executor = kwargs.get('executor')
        self._macro_line = kwargs.get('macro_line')
        self._macro_thread = None
        self._id = kwargs.get('id')
        self._desc = "Macro '%s'" % self._macro_line
        self._macro_status = { 'id' : self._id,
                               'range' : (0.0, 100.0),
                               'state' : 'start',
                               'step' : 0.0 }
        self._pause_event = PauseEvent(self)
        log_parent = self._parent_macro or self.getDoorObj() or self.getManager()
        Logger.__init__(self, "Macro[%s]" % self._name, log_parent)
        self._reserveObjs(args)

    ## @name Official Macro API
    #  This list contains the set of methods that are part of the official macro
    #  API. This means that they can be safely used inside any macro.
    #@{

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Methods to be implemented by the actual macros
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def run(self, *args):
        """**Macro API**. Runs the macro. **Overwrite MANDATORY!** Default implementation
        raises RuntimeError.
        
        :raises: RuntimeError"""
        raise RuntimeError("Macro %s does not implement run method" % self.getName())

    def prepare(self, *args, **kwargs):
        """**Macro API**. Prepare phase. Overwrite as necessary"""
        pass
    
    def on_abort(self):
        """**Macro API**. Hook executed when an abort occurs. Overwrite as necessary"""
        pass

    def on_pause(self):
        """**Macro API**. Hook executed when a pause occurs. Overwrite as necessary"""
        pass

    def on_stop(self):
        """**Macro API**. Hook executed when a stop occurs. Overwrite as necessary"""
        pass
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    @mAPI
    def checkPoint(self):
        """**Macro API**.
           Empty method that just performs a checkpoint. This can be used
           to check for the abort. Usually you won't need to call this method"""
        pass

    @mAPI
    def pausePoint(self, timeout=None):
        """**Macro API**.
           Will establish a pause point where called. If an external source as
           invoked a pause then this method will be block until the external
           source calls resume
           
           :param timeout: timeout in seconds. Default is None meaning wait forever
           :type timeout: float"""
        return self._pausePoint(timeout=timeout)
    
    @property
    def macros(self):
        """**Macro API**.
           An object that contains all macro classes as members. With
           the returning object you can invoke other macros. Example::
        
               m = self.macros.ascan('th', '0', '90', '10', '2')
               scan_data = m.data
        """
        self.checkPoint()
        if not hasattr(self, '_macros'):
            self._macros = MacroFinder(self)
        return self._macros
    
    @mAPI
    def getMacroStatus(self):
        """**Macro API**.
           Returns the current macro status
           
           :return: the macro status"""
        return self._macro_status
    
    @mAPI
    def getManager(self):
        """**Macro API**.
           Returns the manager for this macro
           
           :return: MacroServerManager reference
        """
        import manager
        return manager.MacroServerManager()
    
    @mAPI
    def getName(self):
        """**Macro API**.
           Returns this macro name
           
           :return: the macro name
           :rtype: str
        """
        return self._name
    
    @mAPI
    def getID(self):
        """**Macro API**.
           Returns this macro id
           
           :return: the macro id
           :rtype: str
        """
        return self._id
    
    @mAPI
    def getParentMacro(self):
        """**Macro API**.
           Returns the parent macro reference.
           
           :return: the parent macro reference or None if there is no parent macro
           :rtype: Macro
        """
        return self._parent_macro
    
    @mAPI
    def getDescription(self):
        """**Macro API**.
           Returns a string description of the macro.
           
           :return: the string description of the macro
           :rtype: str"""
        return self._desc

    @mAPI
    def getParameters(self):
        """**Macro API**.
           Returns a the macro parameters.
           
           :return: the macro parameters"""
        return self._in_pars

    @mAPI
    def getExecutor(self):
        """**Macro API**.
           Returns the reference to the object that invoked this macro. Usually
           is a Door object.
        
           :return: the reference to the object that invoked this macro"""
        return self._executor

    @mAPI
    def getDoorObj(self):
        """**Macro API**.
           Returns the reference to the Door that invoked this macro.
           
           :return: the reference to the Door that invoked this macro."""
        return self.getExecutor().getDoor()

    @mAPI
    def getDoorName(self):
        """**Macro API**.
           Returns the string with the name of the Door that invoked this macro.
           
           :return: the string with the name of the Door that invoked this macro."""
        return self.getDoorObj().get_name()
    
    @mAPI
    def getCommand(self):
        """**Macro API**.
           Returns the string used to execute the macro.
           Ex.: 'ascan M1 0 1000 100 0.8'
        
           :return: the macro command.
           :rtype: str"""
        return '%s %s' % (self.getName(), ' '.join([str(p) for p in self._in_pars]))

    @mAPI
    def getDateString(self, time_format='%a %b %d %H:%M:%S %Y'):
        """**Macro API**.
           Helper method. Returns the current date in a string.
        
           :param time_format: the format in which the date should be 
                               returned (optional, default value is 
                               '%a %b %d %H:%M:%S %Y'
           :type time_format: str
           :return: the current date
           :rtype: str"""
        return time.strftime(time_format)
    
    @mAPI
    def outputDate(self, time_format='%a %b %d %H:%M:%S %Y'):
        """**Macro API**.
           Helper method. Outputs the current date into the output buffer
        
           :param time_format: (str) the format in which the date should be 
                               returned (optional, default value is 
                               '%a %b %d %H:%M:%S %Y'
           :type time_format: str
        """
        self.output(self.getDateString(time_format=time_format))

    @mAPI
    def sendRecordData(self, *data):
        """**Macro API**.
           Sends the given data to the RecordData attribute of the Door
           
           :param data: (sequence) the data to be sent
        """
        self.getExecutor().sendRecordData(*data)
    
    @mAPI
    def plot(self, *args, **kwargs):
        """**Macro API**.
           Sends the plot command to the client using the 'RecordData' DevEncoded
           attribute. The data is encoded using the JSON -> BZ2 codec.
        
           :param args: the plotting args
           :param kwargs: the plotting keyword args"""
           
        codec = CodecFactory().getCodec('bz2_json_plot')
        data = { 'args' : args, 'kwargs' : kwargs } 
        data = codec.encode(data)
        self.sendRecordData(*data)

    @property
    def data(self):
        """**Macro API**.
           Returns the data produced by the macro. Default implementation 
           raises an exception.
        
           :raises: Exception"""
        self.checkPoint()
        raise Exception("Macro '%s' does not produce any data" % self.getName())

    @mAPI
    def trace(self, msg, *args, **kwargs):
        """**Macro API**. Record a trace message in this object's logger.
        
           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        return Logger.trace(self, msg, *args, **kwargs)
    
    
    @mAPI
    def traceback(self, *args, **kwargs):
        """**Macro API**.
           Logs the traceback with level TRACE on the macro logger."""
        return Logger.traceback(self, *args, **kwargs)

    @mAPI
    def stack(self, *args, **kwargs):
        """**Macro API**.
           Logs the stack with level TRACE on the macro logger."""
        return Logger.stack(self, *args, **kwargs)

    @mAPI
    def log(self, *args, **kwargs):
        """**Macro API**.
           Record a log message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.log`.
        
           :param level: (int) the record level
           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        return Logger.log(self, *args, **kwargs)

    @mAPI
    def debug(self, *args, **kwargs):
        """**Macro API**.
           Record a debug message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.debug`.
        
           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        return Logger.debug(self, *args, **kwargs)

    @mAPI
    def info(self, *args, **kwargs):
        """**Macro API**.
           Record an info message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.info`.
        
           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        return Logger.info(self, *args, **kwargs)

    @mAPI
    def warning(self, *args, **kwargs):
        """**Macro API**.
           Record a warning message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.warning`.
        
           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        return Logger.warning(self, *args, **kwargs)

    @mAPI
    def error(self, *args, **kwargs):
        """**Macro API**.
           Record an error message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.error`.
        
           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        return Logger.error(self, *args, **kwargs)

    @mAPI
    def critical(self, *args, **kwargs):
        """**Macro API**.
           Record a critical message in this object's logger. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.critical`.
        
           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        return Logger.critical(self, *args, **kwargs)
    
    @mAPI
    def output(self, *args, **kwargs):
        """**Macro API**.
           Record a log message in this object's output. Accepted *args* and
           *kwargs* are the same as :meth:`logging.Logger.log`.
        
           :param msg: (str) the message to be recorded
           :param args: list of arguments
           :param kw: list of keyword arguments
        """
        return Logger.output(self, *args, **kwargs)
    
    @mAPI
    def flushOutput(self):
        """**Macro API**.
           Flushes the output buffer."""
        return Logger.flushOutput(self)

    @mAPI
    def getMacroThread(self):
        """**Macro API**.
           Returns the python thread where this macro is running
           
           :return: the python thread where this macro is running
           :rtype: threading.Thread"""
        return self._macro_thread
    
    @mAPI
    def getMacroThreadID(self):
        """**Macro API**.
           Returns the python thread id where this macro is running
           
           :return: the python thread id where this macro is running
           :rtype: int"""
        return self.getMacroThread().ident

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Hook helper API
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    @mAPI
    def createExecMacroHook(self, par_str_sequence, parent_macro=None):
        """**Macro API**.
           Creates a hook that executes the macro given as a sequence of strings
           where the first string is macro name and the following strings the
           macro parameters
           
           :param par_str_sequence: the macro parameters
           :param parent_macro: the parent macro object. If None is given (default) 
                                then the parent macro is this macro
           
           :return: a ExecMacroHook object (which is a callable object)"""
        return ExecMacroHook(parent_macro or self, par_str_sequence)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Handle child macro execution
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @mAPI
    def createMacro(self, *pars):
        """**Macro API**.
           Create a new macro and prepare it for execution
           Several different parameter formats are supported::
               
               # several parameters:
               self.createMacro('ascan', 'th', '0', '100', '10', '1.0')
               self.createMacro('ascan', 'th', 0, 100, 10, 1.0)
               th = self.getObj('th')
               self.createMacro('ascan', th, 0, 100, 10, 1.0)
               
               # a sequence of parameters:
               self.createMacro(['ascan', 'th', '0', '100', '10', '1.0')
               self.createMacro(('ascan', 'th', 0, 100, 10, 1.0))
               th = self.getObj('th')
               self.createMacro(['ascan', th, 0, 100, 10, 1.0])
                
               # a space separated string of parameters:
               self.createMacro('ascan th 0 100 10 1.0')

           :param pars: the command parameters as explained above
                                      
           :return: a tuple of two elements: macro_class, sequence of parameter objects
        """
        return self.prepareMacro(*pars)
    
    @mAPI
    def prepareMacroObj(self, macro_name_or_klass, *args, **kwargs):
        """**Macro API**. Prepare a new macro for execution
        
        :param macro_name_or_klass name: name of the macro to be prepared or 
                                         the macro class itself
        :param pars: list of parameter objects
        :param init_opts: keyword parameters for the macro constructor
        :param prepare_opts: keyword parameters for the macro prepare
           
        :return: a tuple of two elements: macro object, the result of preparing the macro"""
        # sync our log before calling the child macro prepare in order to avoid
        # mixed outputs between this macro and the child macro
        self.syncLog()
        init_opts = { 'parent_macro' : self }
        return self.getExecutor().prepareMacroObj(macro_name_or_klass, args, init_opts, kwargs)

    @mAPI
    def prepareMacro(self, *args, **kwargs):
        """**Macro API**. Prepare a new macro for execution
           Several different parameter formats are supported::
           
            # several parameters:
            executor.prepareMacro('ascan', 'th', '0', '100', '10', '1.0')
            executor.prepareMacro('ascan', 'th', 0, 100, 10, 1.0)
            th = self.getObj('th')
            executor.prepareMacro('ascan', th, 0, 100, 10, 1.0)
            
            # a sequence of parameters:
            executor.prepareMacro(['ascan', 'th', '0', '100', '10', '1.0')
            executor.prepareMacro(('ascan', 'th', 0, 100, 10, 1.0))
            th = self.getObj('th')
            executor.prepareMacro(['ascan', th, 0, 100, 10, 1.0])
            
            # a space separated string of parameters:
            executor._prepareMacro('ascan th 0 100 10 1.0')

        :param args: the command parameters as explained above
        :param kwargs: keyword optional parameters for prepare
        :return: a tuple of two elements: macro object, the result of preparing the macro
        """
        # sync our log before calling the child macro prepare in order to avoid
        # mixed outputs between this macro and the child macro
        self.syncLog()
        init_opts = { 'parent_macro' : self }
        return self.getExecutor().prepareMacro(args, init_opts, kwargs)
    
    @mAPI
    def runMacro(self, macro_obj):
        """**Macro API**. Runs the macro. This the lower level version of execMacro.
           The method only returns after the macro is completed or an exception
           is thrown.
           It should be used instead of execMacro when some operation needs to
           be done between the macro preparation and the macro execution.
           Example::
           
               macro = self.prepareMacro("mymacro", "myparam")
               self.do_my_stuff_with_macro(macro)
               self.runMacro(macro)
           
           :param macro_obj: macro object
           :return: the output of the macro"""

        # sync our log before calling the child macro prepare in order to avoid
        # mixed outputs between this macro and the child macro
        self.syncLog()
        return self.getExecutor().runMacro(macro_obj)

    @mAPI
    def execMacroObj(self, name, *args, **kwargs):
        """**Macro API**. Execute a macro in this macro. The method only returns after the macro
           is completed or an exception is thrown.
           This is a higher level version of runMacro method.
           It is the same as::
           
               macro = self.prepareMacroObjs(name, *args, **kwargs)
               self.runMacro(macro)
               return macro
        
           :param name: name of the macro to be prepared
           :param args: list of parameter objects
           :param kwargs: list of keyword parameters
           
           :return: a macro object"""
        self.debug("Executing macro: %s" % name)
        macro_obj, prepare_result = self.prepareMacroObj(name, *args, **kwargs)
        result = self.runMacro(macro_obj)
        return macro_obj

    @mAPI
    def execMacro(self, *args, **kwargs):
        """**Macro API**. Execute a macro in this macro. The method only returns after the macro
           is completed or an exception is thrown.
           Several different parameter formats are supported::
           
               # several parameters:
               self.execMacro('ascan', 'th', '0', '100', '10', '1.0')
               self.execMacro('ascan', 'th', 0, 100, 10, 1.0)
               th = self.getObj('th')
               self.execMacro('ascan', th, 0, 100, 10, 1.0)
               
               # a sequence of parameters:
               self.execMacro(['ascan', 'th', '0', '100', '10', '1.0')
               self.execMacro(('ascan', 'th', 0, 100, 10, 1.0))
               th = self.getObj('th')
               self.execMacro(['ascan', th, 0, 100, 10, 1.0])
               
               # a space separated string of parameters:
               self.execMacro('ascan th 0 100 10 1.0')

           :param pars: the command parameters as explained above

           :return: a macro object"""
        par0 = args[0]
        if len(args) == 1:
            if type(par0) in types.StringTypes :
                args = par0.split(' ')
            elif operator.isSequenceType(par0):
                args = par0
        args = map(str, args)
        
        self.debug("Executing macro: %s" % args[0])
        macro_obj, prepare_result = self.prepareMacro(*args, **kwargs)
        result = self.runMacro(macro_obj)
        return macro_obj
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # taurus helpers
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @mAPI
    def getTangoFactory(self):
        """**Macro API**. Helper method that returns the tango factory.
        
        :return: the tango factory singleton
        :rtype: :class:`~taurus.core.tango.TangoFactory`"""
        import taurus
        return taurus.Factory()

    @mAPI
    def getDevice(self, dev_name):
        """**Macro API**. Helper method that returns the device for the given
        device name
        
        :return: the taurus device for the given device name
        :rtype: :class:`~taurus.core.TaurusDevice`"""
        import taurus
        return taurus.Device(dev_name)
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Handle parameter objects
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @mAPI
    def setLogBlockStart(self):
        """**Macro API**. Specifies the begining of a block of data. Basically
        it outputs the 'BLOCK' tag"""
        self.output(Macro.BlockStart)
    
    @mAPI
    def setLogBlockFinish(self):
        """**Macro API**. Specifies the end of a block of data. Basically it
        outputs the '/BLOCK' tag"""
        self.output(Macro.BlockFinish)
    
    @mAPI
    def outputBlock(self, line):
        """**Macro API**. Sends an line tagged as a block to the output
        
        :param str line: line to be sent"""
        if isinstance(line, (str, unicode)):
            o = line
        elif operator.isSequenceType(line):
            o = "\n".join(line)
        else:
            o = str(line)
        self.output("%s\n%s\n%s" % (Macro.BlockStart, o, Macro.BlockFinish))
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Handle parameter objects
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @mAPI
    def addObj(self, obj, priority=0):
        """**Macro API**. Adds the given object to the list of controlled objects of this macro.
           In practice it means that if an abort is executed the abort method of
           the given object will be called.
           
           :param obj: the object to be controlled
           :param priority: wheater or not reserve with priority. Default is 0
                            meaning no priority
           :type priority: int
        """
        self.getExecutor().reserveObj(obj, self, priority=priority)
    
    @mAPI
    def addObjs(self, obj_list):
        """**Macro API**. Adds the given objects to the list of controlled objects of this 
           macro. In practice it means that if an abort is executed the abort 
           method of the given object will be called
           
           :param obj_list: list of objects to be controlled
           :type obj_list: sequence
        """
        executor = self.getExecutor()
        for o in obj_list:
            self.addObj(o)

    def returnObj(self, obj):
        """Removes the given objects to the list of controlled objects of this 
           macro.

           :param obj: object to be released from the control"""
        self.getExecutor().returnObj(obj)

    @mAPI
    def getObj(self, name, type_class=All, subtype=All, pool=All, reserve=True):
        """**Macro API**. Gets the object of the given type belonging to the given
           pool with the given name. The object (if found) will automatically
           become controlled by the macro.
           
           :raises: MacroWrongParameterType if name is not a string
           :raises: AttributeError if more than one matching object is found
           
           :param name: string representing the name of the object.
                        Can be a regular expression
           :type name: str
           :param type_class: the type of object (optional, default is All)
           :param subtype: a string representing the subtype (optional,
                           default is All)
                           Ex.: if type_class is Type.ExpChannel, subtype could be 'CounterTimer'
           :param pool: the pool to which the object should belong (optional,
                        default is All)
           :param reserve: automatically reserve the object for this macro
                           (optional, default is True)
           
           :return: the object or empty list if no compatible object is found"""
        if not isinstance(name, str):
            raise self._buildWrongParamExp("getObj", "name", "string", str(type(name)))
        
        obj = self.getManager().getObj(name, type_class=type_class, subtype=subtype, pool=pool)
        if obj and reserve:
            self.addObj(obj)
        return obj or []
    
    @mAPI
    def getObjs(self, names, type_class=All, subtype=All, pool=All, reserve=True):
        """**Macro API**. Gets the objects of the given type belonging to the given
           pool with the given names. The objects (if found) will automatically
           become controlled by the macro.
           
           :param names: a string or a sequence of strings representing the 
                         names of the objects. Each string can be a regular 
                         expression
           :param type_class: the type of object (optional, default is All).
                             Example: Type.Motor, Type.ExpChannel
           :param subtype: a string representing the subtype (optional, 
                           default is All)
                           Ex.: if type_class is Type.ExpChannel, subtype could be 'CounterTimer'
           :param pool: the pool to which the object should belong (optional, 
                        default is All)
           :param reserve: automatically reserve the object for this macro
                           (optional, default is True)
           
           :return: a list of objects or empty list if no compatible object is found"""
        obj_list = self.getManager().getObjs(names, type_class=type_class, subtype=subtype, pool=pool)
        if reserve:
            self.addObjs(obj_list)
        return obj_list or []
    
    @mAPI
    def findObjs(self, names, type_class=All, subtype=All, pool=All, reserve=True):
        """**Macro API**. Gets the objects of the given type belonging to the given pool with 
           the given names. The objects (if found) will automatically become 
           controlled by the macro.
           
           :param names: a string or a sequence of strings representing the 
                         names of the objects. Each string can be a regular 
                         expression
           :param type_class: the type of object (optional, default is All)
           :param subtype: a string representing the subtype (optional, 
                           default is All)
                           Ex.: if type_class is Type.ExpChannel, subtype could be 'CounterTimer'
           :param pool: the pool to which the object should belong (optional, 
                        default is All)
           :param reserve: automatically reserve the object for this macro
                           (optional, default is True)
           
           :return: a list of objects or empty list if no compatible object 
                    is found"""
        obj_list = self.getManager().findObjs(names, type_class=type_class, subtype=subtype, pool=pool)
        if reserve:
            self.addObjs(obj_list)
        return obj_list

    @mAPI
    def getMacroNames(self):
        """**Macro API**. Returns a list of strings containing the names of all known macros
           
           :return: a list of macro names
           :rtype: list<str>"""
        return self.getManager().getMacroNames()

    @mAPI
    def getMacros(self, filter=None):
        """**Macro API**. Returns a sequence of MacroClass objects for all
        known macros that obey the filter expression.
           
        :param filter:
            a regular expression for the macro name (optional, default is None
            meaning match all macros)
        :return: a sequence of MacroClass objects"""
        return self.getManager().getMacros(filter=filter)

    @mAPI
    def getMacroInfo(self, macro_name):
        """**Macro API**. Returns the corresponding MacroClass object.

        :param macro_name: a string with the desired macro name.
        :type macro_name: str
        :return: a MacroClass object or None if the macro with the given name 
                was not found"""
        return self.getManager().getMacroMetaClass(macro_name)

    @mAPI
    def getMotion(self, elems, motion_source=None, read_only=False, cache=True):
        """**Macro API**. Returns a new Motion object containing the given
        elements.
        
        :raises:
            Exception if no elements are defined or the elems is not recognized
            as valid, or an element is not found or an element appears more
            than once

        :param elems: list of moveable object names
        :param motion_source:
            obj or list of objects containing moveable elements. Usually this
            is a Pool object or a list of Pool objects (optional, default is
            None, meaning all known pools will be searched for the given
            moveable items
        :param read_only: not used. Reserved for future use
        :param cache: not used. Reserved for future use

        :return: a Motion object """
        
        decoupled=False
        try:
            decoupled = self.getEnv("MotionDecoupled")
        except UnknownEnv:
            pass
        
        motion = self.getManager().getMotion(elems, motion_source=motion_source,
                                             read_only=read_only, cache=cache,
                                             decoupled=decoupled)
        if motion is not None:
            self.addObj(motion, priority=1)
        return motion

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Handle macro environment
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @mAPI
    def getEnv(self, key, macro_name=None, door_name=None):
        """**Macro API**. Returns the environment value for the given
        environment name (key). If macro_name is None it will consider the
        current running macro. If door_name is None it will consider the door
        that executed the running macro."""
        door_name = door_name or self.getDoorName()
        macro_name = macro_name or self._name
        return self.getManager().getEnv(key=key, macro_name=macro_name, door_name=door_name)

    @mAPI
    def getAllEnv(self):
        """**Macro API**. Returns the enviroment for the current macro"""
        door_name = self.getDoorName()
        macro_name = self._name
        return self.getManager().getEnv(macro_name=macro_name, door_name=door_name)
    
    @mAPI
    def setEnv(self, key, value_str):
        """**Macro API**. Sets the environment key to the new value and stores it persistently.
        Returns a tuple with the key and value objects stored"""
        return self.getManager().setEnv(key, value_str)

    @mAPI
    def unsetEnv(self, key):
        """**Macro API**. Unsets the environment key."""
        return self.getManager().unsetEnv(key)
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Reload API
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    @mAPI
    def reloadMacro(self, macro_name):
        """**Macro API**. Reloads the module corresponding to the given macro name
        
        :raises: MacroServerExceptionList in case the macro is unknown or the
                 reload process is not successfull
        
        :param macro_name: macro name
        :type macro_name: str
        """
        return self.getManager().reloadMacro(macro_name)
    
    @mAPI
    def reloadMacros(self, macro_names):
        """**Macro API**. Reloads the modules corresponding to the given macro names
        
        :raises: MacroServerExceptionList in case the macro(s) are unknown or the
                 reload process is not successfull
        
        :param macro_names: a list of macro names
        :type macro_names: sequence<str>
        """
        return self.getManager().reloadMacros(macro_names)
    
    @mAPI
    def reloadMacroLib(self, lib_name):
        """**Macro API**. Reloads the given lib(=module) names
        
           :raises: MacroServerExceptionList in case the reload process is not 
                    successfull
        
           :param lib_name: library(=module) name
           :type lib_name: str
           
           :return: the MacroLib object for the reloaded library"""
        return self.getManager().reloadMacroLib(lib_name)

    @mAPI
    def reloadMacroLibs(self, lib_names):
        """**Macro API**. Reloads the given lib(=module) names
        
        :raises: MacroServerExceptionList in case the reload process is not 
                 successfull for at least one lib
        
        param lib_names: a list of library(=module) names
        
        :return: a list of MacroLib objecst for the reloaded libraries"""
        return self.getManager().reloadMacroLibs(lib_names)
    #@}
    
    ## @name Unofficial Macro API
    #    This list contains the set of methods that are <b>NOT</b> part of the 
    #  the macro developer knows what he is doing.
    #    Please check before is there is an official API that does the samething
    #  before executing any of these methods.
    #    If you see that your macro needs to execute any of these methods please
    #  consider informing the MacroServer developer so he may expose this in a 
    #  safe way.
    #@{

    @property
    def parent_macro(self):
        """**Unofficial Macro API**. Alternative to getParentMacro that does not
        throw AbortException in case of an Abort. This should be called only
        internally by the *Executor*"""
        return self._parent_macro
    
    @property
    def description(self):
        """**Unofficial Macro API**. Alternative to :meth:`getDescription` that does not
        throw AbortException in case of an Abort. This should be called only
        internally by the *Executor*"""
        return self._desc
    
    def isAborted(self):
        """**Unofficial Macro API**."""
        return self._aborted

    def isPaused(self):
        """**Unofficial Macro API**."""
        return self._pause_event.isPaused()

    @classmethod
    def hasResult(cls):
        """**Unofficial Macro API**. Returns True if the macro should return
        a result or False otherwise
        
        :return: (bool) True if the macro should return a result or False otherwise
        """
        return len(cls.result_def) > 0

    def getResult(self):
        """**Unofficial Macro API**. Returns the macro result object (if any)
        
        :return: the macro result object or None
        """
        return self._out_pars

    def setResult(self, result):
        """**Unofficial Macro API**. Sets the result of this macro
        
        :param result: (object) the result for this macro
        """
        self._out_pars = result
        
    ## @name Internal methods
    #  This list contains the set of methods that are for INTERNAL macro usage.
    #  Macro developers should never call any of these methods
    #@{
    
    @staticmethod
    def _buildWrongParamExp(method_name, param_name, expected, found):
        """**Internal method**. """
        s = "Macro.%s called with wrong parameter type in '%s'. " \
            "Expected %s got %s" % (method_name, param_name, expected, found)
        return MacroWrongParameterType(s)

    def _getName(self):
        """**Internal method**. """
        return self._name
    
    def _getDescription(self):
        """**Internal method**. """
        return self._desc
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Macro execution methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def _shouldRaiseAbortException(self):
        return self.isAborted() and not self.isProcessingAbort()
    
    def _reserveObjs(self, args):
        """**Internal method**. Used to reserve a set of objects for this macro"""
        for obj in args:
            # isiterable
            if not type(obj) in map(type,([],())):
            #if not operator.isSequenceType(obj) or type(obj) in types.StringTypes:
                obj = (obj,)
            for sub_obj in obj:
                if isinstance(sub_obj, PoolElement):
                    self.addObj(sub_obj)

    def exec_(self):
        """**Internal method**. Execute macro as an iterator"""
        self._macro_thread = threading.current_thread()
        macro_status = self.getMacroStatus()
        
        # make sure a 0.0 progress is sent
        yield macro_status
        
        # allow any macro to be paused at the beginning of its execution
        self.pausePoint()
        
        #global print
        #print = self.output
        #try:
        #    res = self.run(*self._in_pars)
        #finally:
        #    print = _orig_print
            
        with OverloadPrint(self):
            res = self.run(*self._in_pars)
        
        if type(res) == types.GeneratorType:
            it = iter(res)
            for i in it:
                if operator.isMappingType(i):
                    new_range = i.get('range')
                    if new_range is not None: macro_status['range'] = new_range
                    new_step = i.get('step')
                    if new_step is not None: macro_status['step'] = new_step
                elif operator.isNumberType(i):
                    macro_status['step'] = i
                macro_status['state'] = 'step'
                yield macro_status
            # make sure a 'stop' progress is sent
            macro_status['state'] = 'stop'
        else:
            self._out_pars = res
            macro_status['step'] = 100.0
        macro_status['state'] = 'stop'
        yield macro_status
        
    def __prepareResult(self,out):
        """**Internal method**. Decodes the given output in order to be able to
        send to the result channel
           
        :param out: output value
           
        :return: the output as a sequence of strings
        """
        if out is None:
            out = ()
        if operator.isSequenceType(out) and not type(out) in types.StringTypes:
            out = map(str,out)
        else:
            out = (str(out),)
        return out
        
    def _abortOnError(self):
        """**Internal method**. The abort procedure. Calls the user 'on_abort'
        protecting it against exceptions"""
        try:
            self.on_abort()
        except Exception, err:
            exc_info = traceback.format_exc()
            self.error("Error in on_abort(): %s" % exc_info)

    def _pausePoint(self, timeout=None):
        """**Internal method**."""
        if self._pause_event.isPaused():
            self.on_pause()
        self._pause_event.wait(timeout)

    def abort(self):
        """**Internal method**. Activates the abort flag on this macro."""
        self._aborted = True

    def setProcessingAbort(self, yesno):
        """**Internal method**. Activates the processing abort flag on this macro"""
        self._processingAbort = yesno
    
    def isProcessingAbort(self):
        """**Internal method**. Checks if this macro is processing abort"""
        return self._processingAbort
    
    def pause(self, cb=None):
        """**Internal method**. Pauses the macro execution. To be called by the Door running the
        macro to pause the current macro"""
        self._pause_event.pause(cb=cb)

    def resume(self, cb=None):
        """**Internal method**. Resumes the macro execution. To be called by the Door running the
        macro to resume the current macro"""
        self._pause_event.resume(cb=cb)
        
    #@}

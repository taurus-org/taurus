from __future__ import with_statement
import threading
import traceback
import time
import sys
import operator
import types
import weakref

import PyTango
import taurus.core.util

import pool

from parameter import Type, ParamType, ParamRepeat
from exception import MacroServerException, AbortException, MacroWrongParameterType
from gscan import *

class OverloadPrint(object):
    
    def __init__(self, m):
        self._macro = m
        self._accum = ""
        
    def __enter__(self):
        sys.stdout = self

    def __exit__(self, exc_type, exc_value, traceback):
        self.flush()
        sys.stdout = sys.__stdout__
    
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

class PauseEvent(taurus.core.util.Logger):
    
    def __init__(self, macro_obj):
        self._name = self.__class__.__name__
        self._pause_cb = None
        self._resume_cb = None
        self._macro_obj_wr = weakref.ref(macro_obj)
        self._macro_name = macro_obj._getName()
        taurus.core.util.Logger.__init__(self, "Macro_%s %s" % (self._macro_name, self._name))
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


class Hookable(taurus.core.util.Logger):
    
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
        
    @taurus.core.util.propertx
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
    
    def __init__(self, parent_macro, *pars, **opts):
        self._macro_obj_wr = weakref.ref(parent_macro)
        self._pars = pars
        self._opts = opts
        
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
        import manager
        m = manager.MacroServerManager()
        
        klass = m.getMacroClass(name)
        
        def f(*args, **kwargs):
            p_m = self.macro_obj
            p_m.syncLog()
            opts = { 'parent_macro' : p_m, 
                     'executor'     : p_m.getExecutor() }
            kwargs.update(opts)
            m = klass(*args, **kwargs)
            return m
        
        setattr(self, name, f)
        
        return f

def mAPI(fn):
    def new_fn(*args, **kwargs):
        self = args[0]
        if self.isAborted() and not self.isProcessingAbort():
            self.setProcessingAbort(True)
            raise AbortException("aborted before calling %s" % fn.__name__)
        ret = fn(*args, **kwargs)
        if self.isAborted() and not self.isProcessingAbort():
            self.setProcessingAbort(True)
            raise AbortException("aborted after calling %s" % fn.__name__)
        return ret
    
    return new_fn

class Macro(taurus.core.util.Logger):
    """ The Macro base class"""

    # States
    Init     = PyTango.DevState.INIT
    Running  = PyTango.DevState.RUNNING
    Pause    = PyTango.DevState.STANDBY
    Stop     = PyTango.DevState.STANDBY
    Fault    = PyTango.DevState.FAULT
    Finished = PyTango.DevState.ON
    Ready    = PyTango.DevState.ON
    Abort    = PyTango.DevState.ALARM

    All      = ParamType.All
    
    BlockStart = '<BLOCK>'
    BlockFinish = '</BLOCK>'
    
    param_def = []
    result_def = []
    hints = {}
    env = ()
    
    def __init__(self, *args, **opts):
        """Constructor"""
        self._name = opts.get('as', self.__class__.__name__)
        self._in_pars = args
        self._out_pars = None
        self._aborted = False
        self._processingAbort = False
        self._parent_macro = opts.get('parent_macro')
        self._executor = opts.get('executor')
        self._macro_line = opts.get('macro_line')
        self._id = opts.get('id')
        self._desc = "Macro '%s'" % self._macro_line
        self._macro_status = { 'id' : self._id,
                               'range' : (0.0, 100.0),
                               'state' : 'start',
                               'step' : 0.0 }
        self._pause_event = PauseEvent(self)
        self._macros = MacroFinder(self)
        log_parent = self._parent_macro or self.getDoorObj() or self.getManager()
        taurus.core.util.Logger.__init__(self, "Macro[%s]" % self._name, log_parent)
        self._reserveObjs(args)

    def _reserveObjs(self, args):
        for obj in args:
            # isiterable
            if not type(obj) in map(type,([],())):
            #if not operator.isSequenceType(obj) or type(obj) in types.StringTypes:
                obj = (obj,)
            for sub_obj in obj:
                if isinstance(sub_obj, pool.PoolElement):
                    self.addObj(sub_obj)

    ## @name Official Macro API
    #  This list contains the set of methods that are part of the official macro
    #  API. This means that they can be safelly used inside any macro.
    #@{

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Methods to be implemented by the actual macros
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    def on_abort(self):
        """Hook executed when an abort occurs. Overwrite as necessary"""
        pass

    def on_pause(self):
        """Hook executed when a pause occurs. Overwrite as necessary"""
        pass

    def on_stop(self):
        """Hook executed when a stop occurs. Overwrite as necessary"""
        pass

    def prepare(self, *args, **opts):
        """Prepare phase. Overwrite as necessary"""
        pass

    def run(self, *args):
        """Runs the macro. Overwrite MANDATORY!"""
        raise RuntimeError("Macro %s does not implement run method" % self.getName())
    
    def exec_(self):
        """Execute macro as an iterator"""
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
    
    @property
    def parent_macro(self):
        """Alternative to getParentMacro that does not throw AbortException in
        case of an Abort. This should be called only internally by the Executor"""
        return self._parent_macro
    
    @property
    def description(self):
        """Alternative to getDescription that does not throw AbortException in
        case of an Abort. This should be called only internally by the Executor"""
        return self._desc
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # API
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    @mAPI
    def trace(self, msg, *args, **kw):
        return taurus.core.util.Logger.trace(self, msg, *args, **kw)
    
    @mAPI
    def traceback(self, *args, **kw):
        return taurus.core.util.Logger.traceback(self, *args, **kw)

    @mAPI
    def stack(self, *args, **kw):
        return taurus.core.util.Logger.stack(self, *args, **kw)

    @mAPI
    def log(self, *args, **kw):
        return taurus.core.util.Logger.log(self, *args, **kw)

    @mAPI
    def debug(self, *args, **kw):
        return taurus.core.util.Logger.debug(self, *args, **kw)

    @mAPI
    def info(self, *args, **kw):
        return taurus.core.util.Logger.info(self, *args, **kw)

    @mAPI
    def warning(self, *args, **kw):
        return taurus.core.util.Logger.warning(self, *args, **kw)

    @mAPI
    def error(self, *args, **kw):
        return taurus.core.util.Logger.error(self, *args, **kw)

    @mAPI
    def critical(self, *args, **kw):
        return taurus.core.util.Logger.critical(self, *args, **kw)

    @mAPI
    def output(self, *args, **kw):
        return taurus.core.util.Logger.output(self, *args, **kw)

    @mAPI
    def flushOutput(self):
        return taurus.core.util.Logger.flushOutput(self)

    @mAPI
    def checkPoint(self):
        """Empty method that just performs a checkpoint. This can be used
        to check for the abort. Usually you won't need to call this method"""
        pass

    @mAPI
    def pausePoint(self, timeout=None):
        """Will establish a pause point where called. If an external source as
        invoked a pause then this method will be block until the external source
        calls resume"""
        return self._pausePoint(timeout=timeout)
    
    @mAPI
    @property
    def macros(self):
        """Returns an object that contains all macro classes as members. With
        the returning object you can invoke other macros. Example:
        
        macros = self.getMacros()
        m = macros.ascan('th', '0', '90', '10', '2')
        scan_data = m.data
        ...
        
        :return: macro provider object
        """
        return self._macros
    
    @mAPI
    def getMacroStatus(self):
        return self._macro_status
    
    @mAPI
    def getManager(self):
        """Returns the manager for this macro
        :return: MacroServerManager reference
        """
        import manager
        return manager.MacroServerManager()
    
    @mAPI
    def getName(self):
        """Returns this macro name
        :return: (str) the macro name
        """
        return self._name
    
    @mAPI
    def getID(self):
        """Returns this macro id
        :return: (str) yhe macro id
        """
        return self._id
    
    @mAPI
    def getParentMacro(self):
        """Returns the parent macro reference
        :return: the parent macro reference or None if there is no parent macro
        """
        return self._parent_macro
    
    @mAPI
    def getDescription(self):
        """Returns a string description of the macro
           @return the string description of the macro"""
        return self._desc

    @mAPI
    def getParameters(self):
        return self._in_pars

    @mAPI
    def getExecutor(self):
        """Returns the reference to the object that invoked this macro. Usually
        is a Door object.
        :return: the reference to the object that invoked this macro
        """
        return self._executor

    @mAPI
    def getDoorObj(self):
        """Returns the reference to the Door that invoked this macro.
        :return: the reference to the Door that invoked this macro.
        """
        return self.getExecutor().getDoor()

    @mAPI
    def getDoorName(self):
        """Returns the string with the name of the Door that invoked this macro.
        :return:the string with the name of the Door that invoked this macro.
        """
        return self.getDoorObj().get_name()
    
    @mAPI
    def getCommand(self):
        """Returns the string used to execute the macro.
        Ex.: 'ascan M1 0 1000 100 0.8'
        
        :return: (str) the macro command.
        """
        return '%s %s' % (self.getName(), ' '.join([str(p) for p in self._in_pars]))

    @mAPI
    def getDateString(self, time_format='%a %b %d %H:%M:%S %Y'):
        """Helper method. Returns the current date in a string
        
        :param time_format: (str) the format in which the date should be 
                            returned (optional, default value is 
                            '%a %b %d %H:%M:%S %Y'
        :return: (str) the current date"""
        return time.strftime(time_format)
    
    @mAPI
    def outputDate(self, time_format='%a %b %d %H:%M:%S %Y'):
        """Helper method. Outputs the current date into the output buffer
        
        :param time_format: (str) the format in which the date should be 
                            returned (optional, default value is 
                            '%a %b %d %H:%M:%S %Y'
        """
        self.output(self.getDateString(time_format=time_format))

    @mAPI
    def sendRecordData(self, *data):
        """Sends the given data to the RecordData attribute of the Door
           
        :param data: (sequence) the data to be sent
        """
        self.getExecutor().sendRecordData(*data)
    
    @mAPI
    def plot(self, *args, **kwargs):
        """Sends the plot command to the client using the 'RecordData' DevEncoded
        attribute. The data is encoded using the JSON -> BZ2 codec.
        
           @param[in] args the plotting args
           @param[in] kwargs the plotting keyword args"""
           
        codec = taurus.core.util.CodecFactory().getCodec('bz2_json_plot')
        data = { 'args' : args, 'kwargs' : kwargs } 
        data = codec.encode(data)
        self.sendRecordData(*data)

    @mAPI
    @property
    def data(self):
        """Returns the data produced by the macro. Default implementation 
           raises an exception.
        
            @throws Exception"""
        raise Exception("Macro '%s' does not produce any data" % self.getName())

    @mAPI
    def getMacroThread(self):
        return self._macro_thread
    
    @mAPI
    def getMacroThreadID(self):
        return self.getMacroThread().ident

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Hook helper API
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    @mAPI
    def createExecMacroHook(self, par_str_sequence, parent_macro=None):
        """creates a hook that executes the macro given as a sequence of strings
           where the first string is macro name and the following strings the
           macro parameters
           
           @param par_str_sequence the macro parameters
           @param parent_macro the parent macro object. If None is given (default) 
                               then the parent macro is this macro
           
           @return a ExecMacroHook object (which is a callable object)"""
        return ExecMacroHook(parent_macro or self, par_str_sequence)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Handle child macro execution
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @mAPI
    def createMacro(self, *pars):
        """Create a new macro and prepare it for execution
           Several different parameter formats are supported:
           1. several parameters:
             1.1 self.createMacro('ascan', 'th', '0', '100', '10', '1.0')
             1.2 self.createMacro('ascan', 'th', 0, 100, 10, 1.0)
             1.3 th = self.getObj('th');
                 self.createMacro('ascan', th, 0, 100, 10, 1.0)
           2. a sequence of parameters:
              2.1 self.createMacro(['ascan', 'th', '0', '100', '10', '1.0')
              2.2 self.createMacro(('ascan', 'th', 0, 100, 10, 1.0))
              2.3 th = self.getObj('th');
                  self.createMacro(['ascan', th, 0, 100, 10, 1.0])
           3. a space separated string of parameters:
              self.createMacro('ascan th 0 100 10 1.0')

           @param[in] pars the command parameters as explained above
                                      
           @return a tuple of two elements: macro_class, sequence of parameter objects
        """
        return self.prepareMacro(*pars)
    
    @mAPI
    def prepareMacroObj(self, macro_name_or_klass, *pars, **opts):
        """Prepare a new macro for execution
        
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
        return self.getExecutor().prepareMacroObj(macro_name_or_klass, pars, init_opts, opts)

    @mAPI
    def prepareMacro(self, *pars, **opts):
        """Prepare a new macro for execution
           Several different parameter formats are supported:
           1. several parameters:
             1.1 executor.prepareMacro('ascan', 'th', '0', '100', '10', '1.0')
             1.2 executor.prepareMacro('ascan', 'th', 0, 100, 10, 1.0)
             1.3 th = self.getObj('th');
                 executor.prepareMacro('ascan', th, 0, 100, 10, 1.0)
           2. a sequence of parameters:
              2.1 executor.prepareMacro(['ascan', 'th', '0', '100', '10', '1.0')
              2.2 executor.prepareMacro(('ascan', 'th', 0, 100, 10, 1.0))
              2.3 th = self.getObj('th');
                  executor.prepareMacro(['ascan', th, 0, 100, 10, 1.0])
           3. a space separated string of parameters:
              executor._prepareMacro('ascan th 0 100 10 1.0')

        :param pars: the command parameters as explained above
        :param opts: keyword optional parameters for prepare
        :return: a tuple of two elements: macro object, the result of preparing the macro
        """
        # sync our log before calling the child macro prepare in order to avoid
        # mixed outputs between this macro and the child macro
        self.syncLog()
        init_opts = { 'parent_macro' : self }
        return self.getExecutor().prepareMacro(pars, init_opts, opts)
    
    @mAPI
    def runMacro(self, macro_obj):
        """Runs the macro. This the lower level version of execMacro.
           The method only returns after the macro is completed or an exception
           is thrown.
           It should be used instead of execMacro when some operation needs to
           be done between the macro preparation and the macro execution.
           Example:
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
    def execMacroObj(self, name, *pars, **opts):
        """Execute a macro in this macro. The method only returns after the macro
           is completed or an exception is thrown.
           This is a higher level version of runMacro method.
           It is the same as:
           macro = self.prepareMacroObjs(name, *pars, **opts)
           self.runMacro(macro)
           return macro
        
           @param name name of the macro to be prepared
           @param pars list of parameter objects
           @param opts list of keyword parameters
           
           @return a macro object"""
        self.debug("Executing macro: %s" % name)
        macro_obj, prepare_result = self.prepareMacroObj(name, *pars, **opts)
        result = self.runMacro(macro_obj)
        return macro_obj

    @mAPI
    def execMacro(self, *pars, **opts):
        """Execute a macro in this macro. The method only returns after the macro
           is completed or an exception is thrown.
           Several different parameter formats are supported:
           1. several parameters:
             1.1 self.execMacro('ascan', 'th', '0', '100', '10', '1.0')
             1.2 self.execMacro('ascan', 'th', 0, 100, 10, 1.0)
             1.3 th = self.getObj('th');
                 self.execMacro('ascan', th, 0, 100, 10, 1.0)
           2. a sequence of parameters:
              2.1 self.execMacro(['ascan', 'th', '0', '100', '10', '1.0')
              2.2 self.execMacro(('ascan', 'th', 0, 100, 10, 1.0))
              2.3 th = self.getObj('th');
                  self.execMacro(['ascan', th, 0, 100, 10, 1.0])
           3. a space separated string of parameters:
              self.execMacro('ascan th 0 100 10 1.0')

           @param[in] pars the command parameters as explained above

           @return a macro object"""
        par0 = pars[0]
        if len(pars) == 1:
            if type(par0) in types.StringTypes :
                pars = par0.split(' ')
            elif operator.isSequenceType(par0):
                pars = par0
        pars = map(str, pars)
        
        self.debug("Executing macro: %s" % pars[0])
        macro_obj, prepare_result = self.prepareMacro(*pars, **opts)
        result = self.runMacro(macro_obj)
        return macro_obj
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # taurus helpers
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @mAPI
    def getTangoFactory(self):
        import taurus
        return taurus.Factory()

    @mAPI
    def getDevice(self, dev_name):
        import taurus
        return taurus.Device(dev_name)
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Handle parameter objects
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @mAPI
    def setLogBlockStart(self):
        """Specifies the begining of a block of data. Basically it outputs the
        'BLOCK' tag"""
        self.output(Macro.BlockStart)

    @mAPI
    def setLogBlockFinish(self):
        """Specifies the end of a block of data. Basically it outputs the
        '/BLOCK' tag"""
        self.output(Macro.BlockFinish)

    @mAPI
    def outputBlock(self, line):
        if type(line) in types.StringTypes:
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
        """Adds the given object to the list of controlled objects of this macro.
           In practice it means that if an abort is executed the abort method of
           the given object will be called
           
           @param[in] obj the object to be controlled
        """
        self.getExecutor().reserveObj(obj, self, priority=priority)
    
    @mAPI
    def addObjs(self, obj_list):
        """Adds the given objects to the list of controlled objects of this 
           macro. In practice it means that if an abort is executed the abort 
           method of the given object will be called
           
           @param[in] obj_list list of objects to be controlled
        """
        executor = self.getExecutor()
        for o in obj_list:
            self.addObj(o)

    def returnObj(self, obj):
        """Removes the given objects to the list of controlled objects of this 
           macro. 

           @param[in] obj object to be released from the control"""
        self.getExecutor().returnObj(obj)

    @mAPI
    def getObj(self, name, type_class=All, subtype=All, pool=All):
        """Gets the object of the given type belonging to the given pool with 
           the given name. The object (if found) will automatically become 
           controlled by the macro.
           
           @throws MacroWrongParameterType if name is not a string
           @throws AttributeError if more than one matching object is found
           
           @param[in] name string representing the name of the object. 
                           Can be a regular expression
           @param[in] type_class the type of object (optional, default is All)
           @param[in] subtype a string representing the subtype (optional, 
                              default is All)
                              Ex.: if type_class is Type.ExpChannel, subtype 
                                   could be 'CounterTimer'
           @param[in] pool the pool to which the object should belong (optional, 
                           default is All)
           
           @return the object or empty list if no compatible object is found"""
        if not isinstance(name, str):
            raise self._buildWrongParamExp("getObj", "name", "string", str(type(name)))
        
        obj = self.getManager().getObj(name, type_class=type_class, subtype=subtype, pool=pool)
        if obj: self.addObj(obj)
        return obj or []
    
    @mAPI
    def getObjs(self, names, type_class=All, subtype=All, pool=All):
        """Gets the objects of the given type belonging to the given pool with 
           the given names. The objects (if found) will automatically become 
           controlled by the macro.
           
           @param[in] names a string or a sequence of strings representing the 
                            names of the objects. Each string can be a regular 
                            expression
           @param[in] type_class the type of object (optional, default is All).
                                 Ex.: Type.Motor, Type.ExpChannel
           @param[in] subtype a string representing the subtype (optional, 
                              default is All)
                              Ex.: if type_class is Type.ExpChannel, subtype 
                                   could be 'CounterTimer'
           @param[in] pool the pool to which the object should belong (optional, 
                           default is All)
           
           @return a list of objects or empty list if no compatible object 
                   is found"""
        
        obj_list = self.getManager().getObjs(names, type_class=type_class, subtype=subtype, pool=pool)
        self.addObjs(obj_list)
        return obj_list or []
    
    @mAPI
    def findObjs(self, names, type_class=All, subtype=All, pool=All):
        """Gets the objects of the given type belonging to the given pool with 
           the given names. The objects (if found) will automatically become 
           controlled by the macro.
           
           @param[in] names a string or a sequence of strings representing the 
                            names of the objects. Each string can be a regular 
                            expression
           @param[in] type_class the type of object (optional, default is All)
           @param[in] subtype a string representing the subtype (optional, 
                              default is All)
                              Ex.: if type_class is Type.ExpChannel, subtype 
                                   could be 'CounterTimer'
           @param[in] pool the pool to which the object should belong (optional, 
                           default is All)
           
           @return a list of objects or empty list if no compatible object 
                   is found"""
        obj_list = self.getManager().findObjs(names, type_class=type_class, subtype=subtype, pool=pool)
        self.addObjs(obj_list)
        return obj_list

    @mAPI
    def getMacroNames(self):
        """Returns a list of strings containing the names of all known macros
            @return a list of macro names"""
        return self.getManager().getMacroNames()

    @mAPI
    def getMacros(self, filter=None):
        """Returns a sequence of MacroClass objects for all known macros that
           obey the filter expression.
           @param filter a regular expression for the macro name (optional, 
                         default is None meaning match all macros)
           @return a sequence of MacroClass objects"""
        return self.getManager().getMacros(filter=filter)

    @mAPI
    def getMacroInfo(self, macro_name):
        """Returns the corresponding MacroClass object
           @param macro_name a string with the desired macro name
           @return a MacroClass object or None if the macro with the given name 
                   was not found"""
        return self.getManager().getMacroMetaClass(macro_name)

    @mAPI
    def getMotion(self, elems, motion_source=None, read_only=False, cache=True):
        """Returns a new Motion object containing the given elements
        
           @throws Exception if no elements are defined or the elems is not 
                             recognized as valid, or an element is not found or
                             an element appears more than once
           
           @param[in] elems list of moveable object names
           @param[in] motion_source obj or list of objects containing moveable
                                    elements. Usually this is a Pool object or a
                                    list of Pool objects (optional, default is
                                    None, meaning all known pools will be 
                                    searched for the given moveable items
           @param[in] read_only not used. Reserved for future use
           @param[in] cache not used. Reserved for future use
           
           @return a Motion object """
        motion = self.getManager().getMotion(elems, motion_source=motion_source,
                                             read_only=read_only, cache=cache)
        if motion is not None:
            self.addObj(motion, priority=1)
        return motion

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Handle macro environment
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @mAPI
    def getEnv(self, key, macro_name=None, door_name=None):
        """Returns the environment value for the given environment name (key).
        if macro_name is None it will consider the current running macro. If 
        door_name is None it will consider the door that executed the running 
        macro."""
        door_name = door_name or self.getDoorName()
        macro_name = macro_name or self._name
        return self.getManager().getEnv(key=key, macro_name=macro_name, door_name=door_name)

    @mAPI
    def getAllEnv(self):
        """Returns the enviroment for the current macro"""
        door_name = self.getDoorName()
        macro_name = self._name
        return self.getManager().getEnv(macro_name=macro_name, door_name=door_name)
    
    @mAPI
    def setEnv(self, key, value_str):
        """Sets the environment key to the new value and stores it persistently.
        Returns a tuple with the key and value objects stored"""
        return self.getManager().setEnv(key, value_str)

    @mAPI
    def unsetEnv(self, key):
        """Unsets the environment key."""
        return self.getManager().unsetEnv(key)
        
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Reload API
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    
    @mAPI
    def reloadMacro(self, macro_name):
        """Reloads the module corresponding to the given macro name
        
        @throws MacroServerExceptionList in case the macro is unknown or the
        reload process is not successfull
        
        @param[in] macro_name macro name"""
        return self.getManager().reloadMacro(macro_name)
    
    @mAPI
    def reloadMacros(self, macro_names):
        """Reloads the modules corresponding to the given macro names
        
        @throws MacroServerExceptionList in case the macro(s) are unknown or the
        reload process is not successfull
        
        @param[in] macro_names a list of macro names"""
        return self.getManager().reloadMacros(macro_names)
    
    @mAPI
    def reloadMacroLib(self, lib_name):
        """Reloads the given lib(=module) names
        
           @throws MacroServerExceptionList in case the reload process is not 
                                            successfull
        
           @param[in] lib_name library(=module) name 
           
           @return the MacroLib object for the reloaded library"""
        return self.getManager().reloadMacroLib(lib_name)

    @mAPI
    def reloadMacroLibs(self, lib_names):
        """Reloads the given lib(=module) names
        
        @throws MacroServerExceptionList in case the reload process is not 
        successfull for at least one lib
        
        @param[in] lib_names a list of library(=module) names
        
        @return a list of MacroLib objecst for the reloaded libraries"""
        return self.getManager().reloadMacroLibs(lib_names)
    #@}
    
    ## @name Unofficial Macro API
    #    This list contains the set of methods that are <b>NOT</b> part of the 
    #  official macro API but can be called by the macro code as a workaround if
    #  the macro developer knows what he is doing.
    #    Please check before is there is an official API that does the samething
    #  before executing any of these methods.
    #    If you see that your macro needs to execute any of these methods please
    #  consider informing the MacroServer developer so he may expose this in a 
    #  safe way.
    #@{

    def isAborted(self):
        return self._aborted

    def isPaused(self):
        return self._pause_event.isPaused()

    @classmethod
    def hasResult(cls):
        """Returns True if the macro should return a result or False otherwise
        
        :return: (bool) True if the macro should return a result or False otherwise
        """
        return len(cls.result_def) > 0

    def getResult(self):
        """Returns the macro result object (if any)
        
        :return: the macro result object or None
        """
        return self._out_pars

    def setResult(self, result):
        """Sets the result of this macro
        
        :param result: (object) the result for this macro
        """
        self._out_pars = result
        
    ## @name Internal methods
    #  This list contains the set of methods that are for INTERNAL macro usage.
    #  Macro developers should never call any of these methods
    #@{
    
    @staticmethod
    def _buildWrongParamExp(method_name, param_name, expected, found):
        s = "Macro.%s called with wrong parameter type in '%s'. " \
            "Expected %s got %s" % (method_name, param_name, expected, found)
        return MacroWrongParameterType(s)

    def _getName(self):
        return self._name
    
    def _getDescription(self):
        return self._desc
    
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Macro execution methods
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def __prepareResult(self,out):
        """decodes the given output in order to be able to send to the result
        channel
           
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
        """The abort procedure. Calls the user 'on_abort' protecting it against 
        exceptions"""
        try:
            self.on_abort()
        except Exception, err:
            exc_info = traceback.format_exc()
            self.error("Error in on_abort(): %s" % exc_info)

    def _pausePoint(self, timeout=None):
        if self._pause_event.isPaused():
            self.on_pause()
        self._pause_event.wait(timeout)

    def abort(self):
        self.debug("Aborting %s", self._desc)
        self._aborted = True

    def setProcessingAbort(self, yesno):
        self._processingAbort = yesno
    
    def isProcessingAbort(self):
        return self._processingAbort
    
    def pause(self, cb=None):
        """Pauses the macro execution. To be called by the Door running the
        macro to pause the current macro"""
        self._pause_event.pause(cb=cb)

    def resume(self, cb=None):
        """Resumes the macro execution. To be called by the Door running the
        macro to resume the current macro"""
        self._pause_event.resume(cb=cb)
        
    #@}


class Table:

    DefTermWidth = 80

    PrettyOpts   = {'col_sep': ' |', 'col_head_sep': '-', 'border': '='}
    
    def __init__(self, elem_list, elem_fmt=['%*s'], term_width=None,
                 row_head_str=None, row_head_fmt='%-*s', row_head_width=None,
                 col_head_str=None, col_head_fmt='%*s',  col_head_width=None,
                 col_sep=' ', row_sep=' ', col_head_sep=None, border=None):

        self.nr_col = len(elem_list)
        self.nr_row = len(elem_list[0])
        self.elem_list = elem_list
        self.elem_fmt  = elem_fmt
        if len(elem_fmt) == 1:
            elem_fmt *= self.nr_row
        
        self.term_width = term_width or Table.DefTermWidth
        self.col_sep      = col_sep
        self.row_sep      = row_sep
        self.col_head_sep = col_head_sep
        self.border       = border
        
        max_len_fn = lambda x: reduce(max, map(len, x))
        
        self.row_head_str = row_head_str
        self.row_head_fmt = row_head_fmt
        if row_head_str is not None and len(row_head_str) != self.nr_row:
            msg = 'RowHeadStr nr (%d) and RowNr (%d) mistmatch' % \
                  len(row_head_str), self.nr_row
            raise ValueError, msg
        if row_head_width is None:
            if row_head_str is not None:
                row_head_width = max_len_fn(row_head_str)
            else:
                row_head_width = 0
        self.row_head_width = row_head_width
            
        self.col_head_str = col_head_str
        self.col_head_fmt = col_head_fmt
        if col_head_str is not None and len(col_head_str) != self.nr_col:
            msg = 'ColHeadStr nr (%d) and ColNr (%d) mistmatch' % \
                  len(col_head_str), self.nr_col
            raise ValueError, msg
        if col_head_width is None:
            if col_head_str is not None:
                col_head_width = reduce(max, map(max_len_fn, col_head_str))
            else:
                col_head_width = 10
        self.col_head_width = col_head_width
        if col_head_str is not None:
            self.col_head_lines = len(col_head_str[0])
        else:
            self.col_head_lines = 0
        
    def updateElem(self, elem_list):
        new_col, new_row = len(elem_list), len(elem_list[0])
        if new_col != self.nr_col or new_row != self.nr_row:
            raise 'Invalid new elem list size %dx%d, was %dx%d' % \
                  (new_col, new_row, self.nr_col, self.nr_row)
        self.elem_list = elem_list
        
    def genOutput(self, term_width=None):
        if term_width is None:
            term_width = self.term_width

        
        rhw, chw = self.row_head_width, self.col_head_width
        chl = self.col_head_lines
        lcs = len(self.col_sep)
        width = term_width - chw   # At least one disp column!
        if rhw > 0:
            width -= rhw + lcs
        disp_cols = width / (chw + lcs) + 1
        tot_width = chw + (disp_cols - 1) * (chw + lcs)
        tot_rows = chl + self.nr_row
        if rhw > 0:
            tot_width += rhw + lcs
            
        output = []

        if self.row_head_str is not None:
            row_head = []
            fmt = self.row_head_fmt
            for head in [''] * chl + self.row_head_str:
                head = fmt % (rhw, head)
                row_head.append(head + self.col_sep)
        else:
            row_head = [''] * tot_rows

        for i in xrange(0, self.nr_col, disp_cols):
            if i > 0:
                nr_sep = tot_width / len(self.row_sep)
                output.append(self.row_sep * nr_sep)

            row_end = min(i + disp_cols, self.nr_col)
            line = list(row_head)
            for j in xrange(i, row_end):
                elem = self.elem_list[j]
                if chl:
                    col_head = self.col_head_str[j]
                    if j > i:
                        for k in xrange(tot_rows):
                            line[k] += self.col_sep
                    fmt = self.col_head_fmt
                    for k in xrange(chl):
                        line[k] += fmt % (chw, col_head[k])
                        
                for k in xrange(self.nr_row):
                    fmt = self.elem_fmt[k]
                    line[chl+k] += fmt % (chw, elem[k])

            max_width = reduce(max, map(len, line))
            if self.border is not None:
                nr_border = max_width / len(self.border)
                output.append(self.border * nr_border)
            for l in line[:chl]:
                output.append(l)
            if self.col_head_sep is not None:
                nr_sep = max_width / len(self.col_head_sep)
                output.append(self.col_head_sep * nr_sep)
            for l in line[chl:]:
                output.append(l)
            if self.border is not None:
                output.append(self.border * nr_border)

        return output

class List:
    
    def __init__(self, header, border='-'):
        self.col_nb = len(header)
        self.rows = [list(header), self.col_nb*[border]]
        self.col_lens = self.col_nb*[0,]
        self.border = '-'
        self.line = ''
        
    def recalc_col_sizes(self):
        for i,row in enumerate(self.rows):
            for j,cell in enumerate(row):
                cell = str(cell)
                row[j] = cell
                n = len(cell)
                if n >= self.col_lens[j]:
                    new_len = n + 3
                    self.col_lens[j] = new_len
                    self.rows[1][j] = (n+2)*self.border
        self.line = ''
        for n in self.col_lens:
            self.line += '%c%ds' % ('%',n)
    
    def appendRow(self,row):
        row = list(row[:self.col_nb])
        self.rows.append(row)
    
    def putRow(self,row,idx):
        row = list(row[:self.col_nb])
        self.rows[idx] = row

    def genOutput(self):
        self.recalc_col_sizes()
        ret = []
        for row in self.rows:
            ret.append(self.line % tuple(row))
        return ret


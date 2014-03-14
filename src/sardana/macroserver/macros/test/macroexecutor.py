
from taurus.core.util.singleton import Singleton

class BaseMacroExecutor(object):
    '''
    Abstract MacroExecutor class. Inherit from it if you want to create your 
    own macro executor.
    '''

    log_levels = ['debug', 'output', 'info', 'warning', 'critical', 'error'] 

    def __init__(self):
        # macro result
        self._result = None
        # buffer for state history
        self._state_buffer = []
        # log buffers, one for each level
        for level in self.log_levels:
            setattr(self, '_%s' % level, None)
        # common buffer, any registered log level will be appended here
        self._common = None

    def _clean(self):
        '''
        In case of reuse of the macro executor object this method executes the 
        necessary cleanups. Extend if you need to clean your particular setups. 
        '''
        for level in self.log_levels:
            log_buffer = getattr(self, '_%s' % level)
            if not log_buffer is None:
                log_buffer.__init__()
            
        if self._common:
            self._common.__init__()

    def run(self, macro_name, macro_params=None, sync=True, 
                                                        timeout=float("inf")):
        # TODO how to use 'see' in documentation?? to point to wait method 
        # in case of asynchronous call
        '''
        Execute macro.
         
        :param macro_name: (string) name of macro to be executed
        :param macro_params: (list<string>) macro parameters 
                             (default is macro_params=None for macros without
                             parameters or with the default values)
        :param sync: (bool) whether synchronous or asynchronous call
                     (default is sync=True)
        :param timeout: (float) timeout that will be passed to the wait method,
                        in case of synchronous execution
        '''
        if macro_params == None:
            macro_params = []

        self._clean()
        self._run(macro_name, macro_params)

        #sync events when a macro fail #TODO
        if sync:
            self.wait(timeout)


    def _run(self, macro_name, macro_params):
        '''
        Method responsible for triggering the macro execution. Must be
        implemented in your macro executor.
        
        :param macro_name: (string) name of macro to be executed
        :param macro_params: (list<string>) macro parameters 
                             (default is macro_params=None for macros without
                             parameters or with the default values)
        '''
        raise NotImplementedError('Method _run not implemented in class %s' %
                                  self.__class__.__name__)

    def wait(self, timeout = float("inf")):
        '''
        Wait until macro is done. Use it in asynchronous executions.
        
        param timeout: (float) waiting timeout'''
        if timeout <= 0:
            timeout =  float("inf")

        self._wait(timeout)
    
    def _wait(self, timeout):
        '''
        Method responsible for waiting until macro is done. Must be
        implemented in your macro executor.
        
        param timeout: (float) waiting timeout
        '''
        raise NotImplementedError('Method _wait not implemented in class %s' %
                                  self.__class__.__name__)

    def stop(self, timeout = float("inf")):
        '''
        Stop macro execution. Execute macro in synchronous way before using
        this method.
        
        param: timeout (float) waiting timeout
        '''
        self._stop(timeout)

    def _stop(self):
        '''
        Method responsible for stopping the macro execution. Must be
        implemented in your macro executor.
        '''
        raise NotImplementedError('Method _stop not implemented in class %s' %
                                  self.__class__.__name__)

    def registerLog(self, log_level):
        '''
        Start registering log messages.
        
        param: log_level (string) string indicating the log level
        '''
        log_buffer_name = '_%s' % log_level
        setattr(self, log_buffer_name, [])
        self._registerLog(log_level)
        
    def _registerLog(self, log_level):
        '''
        Method responsible for starting log registration. Must be
        implemented in your macro executor.
        
        param: log_level (string) string indicating the log level
        '''
        raise NotImplementedError('Method _registerLog not implemented in '
                                  'class %s' % self.__class__.__name__)
                                  
    def unregisterLog(self, log_level):
        '''
        Stop registering log messages.
        
        param: log_level (string) string indicating the log level
        '''
        self._unregisterLog(log_level)
        
    def _unregisterLog(self, log_level):
        '''
        Method responsible for stopping log registration. Must be
        implemented in your macro executor.
        
        param: log_level (string) string indicating the log level
        '''
        raise NotImplementedError('Method _unregisterLog not implemented in '
                                  'class %s' % self.__class__.__name__)
                                  
    def getLog(self, log_level):
        '''
        Get log messages.
        
        param: log_level (string) string indicating the log level
        '''
        log_buffer_name = '_%s' % log_level
        log = getattr(self, log_buffer_name)
        return log

    def registerAll(self):
        '''
        Register for macro result, all log levels and common buffer.
        '''
        for log_level in self.log_levels:
            self.registerLog(log_level)
        self.registerResult()
        self.createCommonBuffer()

    def unregisterAll(self):
        '''
        Unregister macro result, all log levels and common buffer.
        '''
        for log_level in self.log_levels:
            self.unregisterLog(log_level)
        self.unregisterResult()
        
    def registerResult(self):
        '''
        Register for macro result
        '''
        self._registerResult()
    
    def _registerResult(self):
        '''
        Method responsible for registering for macro result. Must be
        implemented in your macro executor.
        '''
        raise NotImplementedError('Method _registerResult not implemented in '
                                  'class %s' % self.__class__.__name__)

    def unregisterResult(self):
        '''
        Unregister macro result.
        '''
        self._unregisterResult()
    
    def _unregisterResult(self):
        '''
        Method responsible for unregistering for macro result. Must be
        implemented in your macro executor.
        '''
        raise NotImplementedError('Method _unregisterResult not implemented in'
                                  ' class %s' % self.__class__.__name__)

    def getResult(self):
        '''
        Get macro result.
        '''
        return self._result
        
    def createCommonBuffer(self):
        '''
        Create a common buffer, where all the registered logs will be stored.
        '''
        self._common = []
        
    def getCommonBuffer(self):
        #TODO. See createCommonBuffer method
        '''
        Get common buffer. 
        '''
        return self._common

    def getState(self):
        '''
        Get macro execution state.
        '''
        state = None
        if len(self._state_buffer) > 0:
            state = self._state_buffer[-1]
        return state

    def getStateBuffer(self):
        '''
        Get buffer (history) of macro execution states.
        '''
        return self._state_buffer
    

class MacroExecutorFactory(Singleton):
    '''A scheme-agnostic factory for MacroExecutor instances
    
    Example::
    
        f =  MacroExecutorFactory()
        f.getMacroExecutor('tango://my/door/name') #returns a TangoMacroExecutor
    
    ..note:: For the moment, only TangoMacroExecutor is supported
    '''
        
    def getMacroExecutor(self, door_name=None):
        '''
        Returns a macro executor instance (a subclass of 
        :class:`BaseMacroExecutor`) depending on the door being used.
        ''' 
        if door_name == None:
            from sardana import sardanacustomsettings
            door_name = getattr(sardanacustomsettings,'UNITTEST_DOOR_NAME')
    
        #=======================================================================
        # TODO: Once SEP3 is done, it will define a better way to get the scheme
        # from a model name (including customized default schemes)
        # For the moment I implement it by calling an internal member of 
        # TaurusManager
        from taurus.core import TaurusManager
        scheme = TaurusManager()._get_scheme(door_name)
        #=======================================================================

        if scheme == 'tango':
            return self._getTangoMacroExecutor(door_name)
        else:
            raise ValueError('No MacroExecutor supported for scheme %s' % \
                             scheme)
                        
    def _getTangoMacroExecutor(self, door_name):
        from sardana.tango.macroserver.test.macroexecutor import (
                 TangoMacroExecutor)
        return TangoMacroExecutor(door_name=door_name)
    
if __name__ == '__main__':
    from sardana import sardanacustomsettings
    door_name = getattr(sardanacustomsettings,'UNITTEST_DOOR_NAME')
    print MacroExecutorFactory().getMacroExecutor(door_name)
    

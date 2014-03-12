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

"""System tests for Macros"""

__all__ =  ['macroTest', 'BaseMacroTestCase', 'RunMacroTestCase', 
            'RunStopMacroTestCase', 'macroTestRun', 'macroTestStop']
import time
import functools
from sardana import sardanacustomsettings
from sardana.macroserver.macros.test.macroexecutor import MacroExecutorFactory

# macroTest Decorator
#
# This decorator will add tests in the macro test cases and define the 
# macro parameters.
#
# Inputs: Test type and test params
#
# The resulting test method will be the addition of the inherited test and 
# the class test.
# The test method name is composed by "test", test type and macro name
#
# For example:
# @macroTest('run', 'mot2', '0', '100', '10', '.1'])
# @macroTest('run', 'mot1', '0', '100', '10', '.1'])
# <test running ascan macro>
#
# will add the test "test_run_ascan_0 and test_run_ascan_1".
# Both will be the addition of inherited and class defined _test_run methods,
# test_run_ascan_0 will be tested with mot1 and test_run_ascan_1 with mot2.
# Since they are nested decorators, the last will be applied first.

def macroTest(test, params=None, wait_timeout=1000):
    '''Decorator to create tests'''

    # Name of the test implementation 
    testName = '_test_%s' % test

    def decorator(klass):
        # New test implementation
        # Sets the passed parameters and adds super and self implementation
        def newTest(self):
            if params:
                self.macro_params = list(params)
            self.wait_timeout = wait_timeout
            # If the test method would be overrided the super method is added
            if testName in klass.__dict__.keys():
                getattr(super(klass, self),testName)()
            getattr(self, testName)()
        
        # To avoid overriding tests defined by other decorators a counter is
        # added in the test name.
        method_index = 0
        methodName = 'test_%s_%s_0' % (test, klass.macro_name)
        while (hasattr(klass, methodName)):
            method_index += 1
            methodName = 'test_%s_%s_%d' % (test, klass.macro_name, method_index)

        # Add the new test method with the new implementation
        setattr(klass, methodName, newTest)
        return klass
    return decorator


macroTestRun = functools.partial(macroTest, 'run')
macroTestStop = functools.partial(macroTest, 'stop')

class BaseMacroTestCase(object):
    '''
    A base class for macro testing 
    
    To use it, simply inherit from BaseWidgetTestCase *and* unittest.TestCase
    and provide the following class members:
    
      - door_name (string) name of the door where the macro will be executed
                 (default='door/sardana_test/1')
      - macro_name (string) name of the macro to be tested (mandatory)
      - macro_params (list<string>) macro parameters, if any
    '''
    door_name = getattr(sardanacustomsettings,'UNITTEST_DOOR_NAME') 
    macro_name = None
    macro_params = []
    
    def setUp(self):
        """ 
        Preconditions: 
        
        """
        
        if self.macro_name is None:
            raise Exception('_macro_name is None') 

        mefact = MacroExecutorFactory()
        self.macro_executor = mefact.getMacroExecutor(self.door_name)


class RunMacroTestCase(BaseMacroTestCase):
    #TODO how to pass necessary class members from the super class?
    '''A base class for testing execution of arbitrary Sardana macros.
    
    To use it, simply inherit from RunMacroTestCase *and* unittest.TestCase
    and provide the following class members:
    - wait_timeout (float): normal macro execution should not exceed this time
    '''
    
    wait_timeout = 2000

    def assertFinished(self, msg):
        '''Asserts that macro has finished.'''
        finishStates = [u'finish']
        state = self.macro_executor.getState()
        #TODO buffer is just for debugging, attach only the last state
        state_buffer = self.macro_executor.getStateBuffer()
        msg = msg + '; State was buffer %s' % state_buffer
        self.assertIn(state, finishStates, msg)

    def setUp(self):
        '''
        Preconditions: 
        - Those from :class:`BaseWidgetTestCase`
        '''
        BaseMacroTestCase.setUp(self)
        self.macro_executor.registerAll()
        
                  
    def _test_run(self):
        '''Check that the macro can be executed'''
        self.macro_executor.run(macro_name = self.macro_name, 
                                 macro_params = self.macro_params,
                                 sync = True, timeout = self.wait_timeout)
        self.assertFinished('Macro %s did not finish' % self.macro_name)
        #TODO debug stream
        #print self.macro_executor.getStateBuffer()

    def tearDown(self):
        self.macro_executor.unregisterAll()
     

class RunStopMacroTestCase(RunMacroTestCase):
    '''A base class for testing common cases of arbitrary Sardana macros.
       Useful for Runnable and Stopable macros.

    To use it, simply inherit from StopMacroTestCase *and* unittest.TestCase
    and provide the following class members:
      - stop_delay (float): macro will be stopped after this amount of time
      - wait_timeout (float): macro execution should get stopped within this 
time
      - _klass (typeobject) the widget class to test (mandatory)
      - initargs (list) a list of arguments for the klass init method 
                 (default=[])
      - initkwargs (dict) a dict of keyword arguments for the klass init method
                   (default={})
      
    '''

    stop_delay = None

    def assertStopped(self, msg):
        '''Asserts that macro was stopped'''
        stoppedStates = [u'stop']
        state = self.macro_executor.getState()
        #TODO buffer is just for debugging, attach only the last state
        state_buffer = self.macro_executor.getStateBuffer()
        msg = msg + '; State buffer was %s' % state_buffer
        self.assertIn(state, stoppedStates, msg) 

    def setUp(self):
        '''
        Preconditions: 
        - Those from :class:`RunMacroTestCase`
        '''
        RunMacroTestCase.setUp(self)
   
    def _test_stop(self):
        '''Check that the macro can be aborted'''
        self.macro_executor.run(macro_name = self.macro_name, 
                                 macro_params = self.macro_params, 
                                 sync = False)

        if not self.stop_delay is None:
            time.sleep(self.stop_delay)
        self.macro_executor.stop()
        self.macro_executor.wait(timeout = self.wait_timeout)
        self.assertStopped('Macro %s did not stop' % self.macro_name)
        #TODO debug stream
        #print self.macro_executor.getStateBuffer()



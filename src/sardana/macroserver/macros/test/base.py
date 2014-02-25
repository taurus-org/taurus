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

import copy
import time
import unittest


class BaseMacroTestCase(object):
    '''
    A base class for macro testing 
    
    To use it, simply inherit from BaseWidgetTestCase *and* unittest.TestCase
    and provide the following class members:
    
      - door_name (string) name of the door where the macro will be executed
                 (default='door/sardana_test/1')
      - macro_name (string) name of the macro to be tested (mandatory)
      - macro_params (list<string>) macro parameters, if any
      .. warning:: the following class members probably will be removed
      - macro_executor_klass (class) class of the macro executor to be used
      - macro_executor_initargs (list) a list of arguments for the klass init method 
                 (default=[])
      - macro_executor_initkwargs (dict) a dict of keyword arguments for the klass init method 
                   (default={})
    '''
    door_name = 'door/sardana_test/1' 
    macro_name = None
    macro_params = None
    #TODO implement proper macro executor factory
    macro_executor_klass = None
    macro_executor_initargs = []
    macro_executor_initkwargs = {}
    
    def setUp(self):
        """ 
        Preconditions: 
        
        """
        if self.macro_name is None:
            self.skipTest('_macro_name is None')
            return
        
        unittest.TestCase.setUp(self)
        
        klass = self.macro_executor_klass
        #TODO implement proper factory of the macro executors
        initargs = copy.copy(self.macro_executor_initargs)
        initargs.insert(0, self.door_name)
        initkwargs = self.macro_executor_initkwargs
        self.macro_executor = klass(*initargs, **initkwargs)

    def assertFinished(self, msg):
        '''Asserts that macro has finished.'''
        finishStates = [u'finish']
        state = self.macro_executor.getState()
        #TODO buffer is just for debugging, attach only the last state
        state_buffer = self.macro_executor.getStateBuffer()
        msg = msg + '; State was buffer %s' % state_buffer
        self.assertIn(state, finishStates, msg)

    def assertStopped(self, msg):
        '''Asserts that macro was stopped'''
        stoppedStates = [u'stop']
        state = self.macro_executor.getState()
        #TODO buffer is just for debugging, attach only the last state
        state_buffer = self.macro_executor.getStateBuffer()
        msg = msg + '; State buffer was %s' % state_buffer
        self.assertIn(state, stoppedStates, msg)          

class RunMacroTestCase(BaseMacroTestCase):
    #TODO how to pass necessary class members from the super class?
    '''A base class for testing execution of arbitrary Sardana macros
    
    To use it, simply inherit from RunMacroTestCase *and* unittest.TestCase
    and provide the following class members:
      - run_timeout (float): normal macro execution should not exceed this time
    '''

    wait_timeout = 3.
    
    def setUp(self):
        '''
        Preconditions: 
        - Those from :class:`BaseWidgetTestCase`
        '''
        BaseMacroTestCase.setUp(self)
               
    def test_Run(self):
        '''Check that the macro can be executed'''
        self.macro_executor.run(macro_name = self.macro_name, 
                                 macro_params = self.macro_params,
                                 sync = True, timeout = self.wait_timeout)
        self.assertFinished('Macro %s did not finish' % self.macro_name)
        #TODO debug stream
        print self.macro_executor.getStateBuffer()
    
        
class StopMacroTestCase(BaseMacroTestCase):
    '''A base class for testing common cases of arbitrary Sardana macros
    
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
    wait_timeout = 3.
    
    def setUp(self):
        '''
        Preconditions: 
        - Those from :class:`BaseWidgetTestCase`
        '''
        BaseMacroTestCase.setUp(self)
                   
    def test_Stop(self):
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
        print self.macro_executor.getStateBuffer()
        
class GenericMacroTestCase(RunMacroTestCase, StopMacroTestCase):
    #TODO setUp is called twice! maybe it is not the best solution
    
    def setUp(self):
        RunMacroTestCase.setUp(self)
        StopMacroTestCase.setUp(self)

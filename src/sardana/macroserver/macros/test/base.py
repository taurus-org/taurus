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
            'RunStopMacroTestCase', 'testRun', 'testStop']
import time
import functools
from sardana import sardanacustomsettings
from sardana.macroserver.macros.test.macroexecutor import MacroExecutorFactory

#Define a "NotPassed" object to mark a keyword arg which is not passed
# Note that we do not want to use None because one may want to pass None
class __NotPassedType(int):
    pass
NotPassed = __NotPassedType()

def macroTest(klass=None, helper_name=None, test_method_name=None, 
              test_method_doc = None, **helper_kwargs):
    '''Decorator to insert test methods from a helper method that accepts
    arguments'''
    #TODO Doc it!
    #TODO: Note: this could be generalized to general tests. 
    #      In fact the only "macro-specific" thing here is the assumption 
    #      that klass.macro_name exists

    if klass is None: #recipe to use 
        return functools.partial(macroTest, helper_name=helper_name, 
                                 test_method_name=test_method_name,
                                 test_method_doc = test_method_doc,
                                 **helper_kwargs)
    
    if helper_name is None:
        raise ValueError('helper_name argument is not optional')
    
    if test_method_name is None:
        test_method_name = 'test_%s_%s' % (klass.macro_name, helper_name)
    #Append an index if necessary to avoid overwriting the test method
    name, i = test_method_name, 1
    while (hasattr(klass, name)):
        i += 1
        name = "%s_%i" % (test_method_name, i)
    test_method_name = name
    
    if test_method_doc is None:
        argsrep = ', '.join(['%s=%s'%(k,v) for k,v in helper_kwargs.items()])
        test_method_doc = 'Testing %s with %s(%s)'%(klass.macro_name, 
                                                    helper_name, argsrep)
            
    # New test implementation
    # Sets the passed parameters and adds super and self implementation
    def newTest(obj):
        helper = getattr(obj, helper_name)
        return helper(**helper_kwargs)
    
    #setup a custom docstring
    newTest.__doc__ = test_method_doc
        
    # Add the new test method with the new implementation
    setattr(klass, test_method_name, newTest)
    
    return klass
    
#TODO: Document these decorators!
testRun = functools.partial(macroTest, helper_name='macro_runs')
testStop = functools.partial(macroTest, helper_name='macro_stops')

class BaseMacroTestCase(object):
    '''
    A base class for macro testing 
    
    To use it, simply inherit from BaseMacroTestCase *and* unittest.TestCase
    and provide the following class members:
    
      - door_name (string) name of the door where the macro will be executed.
                 If not set, it will use the value of 
                 sardanacustomsettings.UNITTEST_DOOR_NAME
      - macro_name (string) name of the macro to be tested (mandatory)
      
    Then you may define test methods.
    
    BaseMacroTestCase will provide a macro_executor member which is an instance
    of BaseMacroExecutor
    '''
    door_name = getattr(sardanacustomsettings,'UNITTEST_DOOR_NAME') 
    macro_name = None
    
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
    '''
    
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
        
                  
    def macro_runs(self, macro_params=None, wait_timeout=float("inf"),
                   data=NotPassed):
        '''Check that the macro can be executed'''
        self.macro_executor.run(macro_name = self.macro_name, 
                                macro_params = macro_params,
                                sync = True, timeout = wait_timeout)
        self.assertFinished('Macro %s did not finish' % self.macro_name)
        
        #check if the data of the macro is the expected one 
        if data is not NotPassed:
            actual_data = self.macro_executor.getData()
            msg = 'macro data does not match expected data:\n' + \
                  'obtained=%s\nexpected=%s'%(actual_data, data)
            self.assertEqual(actual_data, data, msg)
        
        #TODO: implement generic asserts for macro result and macro output, etc
        #      in a similar way to what is done for macro data
            
        #TODO debug stream
        #print self.macro_executor.getStateBuffer()

    def tearDown(self):
        self.macro_executor.unregisterAll()
     

class RunStopMacroTestCase(RunMacroTestCase):
    '''A base class for testing common cases of arbitrary Sardana macros.
       Useful for Runnable and Stopable macros.

    To use it, simply inherit from StopMacroTestCase *and* unittest.TestCase
    and provide the following class members:
      
    '''
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
   
    def macro_stops(self, macro_params=None, stop_delay=0.1, 
                                                    wait_timeout=float("inf")):
        '''Check that the macro can be aborted'''
        self.macro_executor.run(macro_name = self.macro_name, 
                                 macro_params = macro_params, 
                                 sync = False)

        if stop_delay is not None:
            time.sleep(stop_delay)
        self.macro_executor.stop()
        self.macro_executor.wait(timeout = wait_timeout)
        self.assertStopped('Macro %s did not stop' % self.macro_name)
        #TODO debug stream
        #print self.macro_executor.getStateBuffer()

if __name__ == '__main__':
    import unittest
    from sardana.macroserver.macros.test.sardemoenv import SarDemoEnv
    
    _m1 = SarDemoEnv().getMotors()[0]
    
    
    #@testRun(macro_params=[_m1, '0', '100', '4', '.1'])
    @testRun(macro_params=[_m1, '1', '0', '2', '.1'])
    @testRun(macro_params=[_m1, '0', '1', '4', '.1'])
    class dummyAscanTest(RunStopMacroTestCase, unittest.TestCase):
        macro_name = 'ascan'
      
    
    @testRun(macro_params=['1'], data={'in':1,'out':2})
    @testRun(macro_params=['5'])
    @testRun
    class dummyTwiceTest(RunStopMacroTestCase, unittest.TestCase):
        macro_name = 'twice'
    
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(dummyTwiceTest)
    unittest.TextTestRunner(descriptions=True, verbosity=2).run(suite)  

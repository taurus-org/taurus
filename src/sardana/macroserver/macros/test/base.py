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

__all__ = ['macroTest', 'BaseMacroTestCase', 'RunMacroTestCase',
           'RunStopMacroTestCase', 'testRun', 'testFail', 'testStop']
import time
import functools
from sardana import sardanacustomsettings
from sardana.macroserver.macros.test import MacroExecutorFactory
from taurus.test import insertTest

#Define a "_NOT_PASSED" object to mark a keyword arg which is not passed
# Note that we do not want to use None because one may want to pass None
class __NotPassedType(int):
    pass
_NOT_PASSED = __NotPassedType()


def macroTest(klass=None, helper_name=None, test_method_name=None,
              test_method_doc=None, **helper_kwargs):
    """This decorator is an specialization of :function::`taurus.test.insertTest`
    for macro testing. It inserts test methods from a helper method that may 
    accept arguments.

    macroTest provides a very economic API for creating new tests for a given
    macro based on a helper method.

    macroTest accepts the following arguments:

        - helper_name (str): the name of the helper method. macroTest will
                             insert a test method which calls the helper with
                             any  the helper_kwargs (see below).
        - test_method_name (str): Optional. Name of the test method to be used.
                                 If None given, one will be generated from the
                                 macro and helper names.
        - test_method_doc (str): The docstring for the inserted test method
                                 (this shows in the unit test output). If None
                                 given, a default one is generated which
                                 includes the input parameters and the helper
                                 name.
        - \*\*helper_kwargs: All remaining keyword arguments are passed to the
                             helper.

    `macroTest` assumes that the decorated class has a `macro_name` 
    class member.

    This decorator can be considered a "base" decorator. It is often used to
    create other decorators in which the helper method is pre-set. Some
    of them are already provided in this module:

    - :meth:`testRun` is equivalent to macroTest with helper_name='macro_runs'
    - :meth:`testStop` is equivalent to macroTest with helper_name='macro_stops'
    - :meth:`testFail` is equivalent to macroTest with helper_name='macro_fails'

    The advantage of using the decorators compared to writing the test methods
    directly is that the helper method can get keyword arguments and therefore
    avoid duplication of code for very similar tests (think, e.g. on writing
    similar tests for various sets of macro input parameters):

    Consider the following code written using the
    :meth:`RunMacroTestCase.macro_runs` helper::

        class FooTest(RunMacroTestCase, unittest.TestCase)
            macro_name = twice

            def test_foo_runs_with_input_2(self):
                '''test that twice(2) runs'''
                self.macro_runs(macro_params=['2'])

            def test_foo_runs_with_input_minus_1(self):
                '''test that twice(2) runs'''
                self.macro_runs(macro_params=['-1'])

    The equivalent code could be written as::

        @macroTest(helper_name='macro_runs', macro_params=['2'])
        @macroTest(helper_name='macro_runs', macro_params=['-1'])
        class FooTest(RunMacroTestCase, unittest.TestCase):
            macro_name = 'twice'

    Or, even better, using the specialized testRun decorator::

        @testRun(macro_params=['2'])
        @testRun(macro_params=['-1'])
        class FooTest(RunMacroTestCase, unittest.TestCase):
            macro_name = 'twice'
            
    .. seealso:: :function::`taurus.test.insertTest`

    """
    #recipe to allow decorating with and without arguments
    if klass is None:
        return functools.partial(macroTest, helper_name=helper_name,
                                 test_method_name=test_method_name,
                                 test_method_doc=test_method_doc,
                                 **helper_kwargs)
        
    return insertTest(klass=klass, helper_name=helper_name, 
                      test_method_name=test_method_name,
                      test_method_doc=test_method_doc, 
                      tested_name = klass.macro_name, 
                      **helper_kwargs)


#Definition of specializations of the macroTest decorator:
testRun = functools.partial(macroTest, helper_name='macro_runs')
testStop = functools.partial(macroTest, helper_name='macro_stops')
testFail = functools.partial(macroTest, helper_name='macro_fails')


class BaseMacroTestCase(object):

    """An abstract class for macro testing.
    BaseMacroTestCase will provide a `macro_executor` member which is an
    instance of BaseMacroExecutor and which can be used to run a macro.

    To use it, simply inherit from BaseMacroTestCase *and* unittest.TestCase
    and provide the following class members:

      - macro_name (string) name of the macro to be tested (mandatory)
      - door_name (string) name of the door where the macro will be executed.
                 This is optional. If not set,
                 `sardanacustomsettings.UNITTEST_DOOR_NAME` is used

    Then you may define test methods.
    """
    macro_name = None
    door_name = getattr(sardanacustomsettings, 'UNITTEST_DOOR_NAME')

    def setUp(self):
        """ A macro_executor instance must be created
        """
        if self.macro_name is None:
            msg = '%s does not define macro_name' % self.__class__.__name__
            raise NotImplementedError(msg)

        mefact = MacroExecutorFactory()
        self.macro_executor = mefact.getMacroExecutor(self.door_name)

    def tearDown(self):
        """The macro_executor instance must be removed
        """
        self.macro_executor.unregisterAll()
        self.macro_executor = None


class RunMacroTestCase(BaseMacroTestCase):

    """A base class for testing execution of arbitrary Sardana macros.
    See :class:`BaseMacroTestCase` for requirements.

    It provides the following helper methods:
      - :meth:`macro_runs`
      - :meth:`macro_fails`
    """

    def assertFinished(self, msg):
        """Asserts that macro has finished.
        """
        finishStates = [u'finish']
        state = self.macro_executor.getState()
        #TODO buffer is just for debugging, attach only the last state
        state_buffer = self.macro_executor.getStateBuffer()
        msg = msg + '; State history=%s' % state_buffer
        self.assertIn(state, finishStates, msg)

    def setUp(self):
        """Preconditions:
        - Those from :class:`BaseMacroTestCase`
        - the macro executor registers to all the log levels
        """
        BaseMacroTestCase.setUp(self)
        self.macro_executor.registerAll()

    def macro_runs(self, macro_params=None, wait_timeout=float("inf"),
                   data=_NOT_PASSED):
        """A helper method to create tests that check if the macro can be
        successfully executed for the given input parameters. It may also
        optionally perform checks on the outputs from the execution.

        :param macro_params: (seq<str>): parameters for running the macro.
                             If passed, they must be given as a sequence of
                             their string representations.
        :param wait_timeout: (float) maximum allowed time (in s) for the macro
                             to finish. By default infinite timeout is used.
        :param data: (obj) Optional. If passed, the macro data after the
                     execution is tested to be equal to this.
        """
        self.macro_executor.run(macro_name=self.macro_name,
                                macro_params=macro_params,
                                sync=True, timeout=wait_timeout)
        self.assertFinished('Macro %s did not finish' % self.macro_name)

        #check if the data of the macro is the expected one
        if data is not _NOT_PASSED:
            actual_data = self.macro_executor.getData()
            msg = 'Macro data does not match expected data:\n' + \
                  'obtained=%s\nexpected=%s' % (actual_data, data)
            self.assertEqual(actual_data, data, msg)

        #TODO: implement generic asserts for macro result and macro output, etc
        #      in a similar way to what is done for macro data

    def macro_fails(self, macro_params=None, wait_timeout=float("inf"),
                    exception=None):
        """Check that the macro fails to run for the given input parameters

        :param macro_params: (seq<str>) input parameters for the macro
        :param wait_timeout: maximum allowed time for the macro to fail. By
                             default infinite timeout is used.
        :param exception: (str or Exception) if given, an additional check of
                        the type of the exception is done.
                        (IMPORTANT: this is just a comparison of str
                        representations of exception objects)
        """
        self.macro_executor.run(macro_name=self.macro_name,
                                macro_params=macro_params,
                                sync=True, timeout=wait_timeout)
        state = self.macro_executor.getState()
        actual_exc_str = self.macro_executor.getExceptionStr()
        msg = 'Post-execution state should be "exception" (got "%s")' % state
        self.assertEqual(state, 'exception', msg)

        if exception is not None:
            msg = 'Raised exception does not match expected exception:\n' + \
                  'raised=%s\nexpected=%s' % (actual_exc_str, exception)
            self.assertEqual(actual_exc_str, str(exception), msg)


class RunStopMacroTestCase(RunMacroTestCase):

    """This is an extension of :class:`RunMacroTestCase` to include helpers for
    testing the abort process of a macro. Useful for Runnable and Stopable
    macros.

    It provides the :meth:`macro_stops` helper
    """

    def assertStopped(self, msg):
        """Asserts that macro was stopped
        """
        stoppedStates = [u'stop']
        state = self.macro_executor.getState()
        #TODO buffer is just for debugging, attach only the last state
        state_buffer = self.macro_executor.getStateBuffer()
        msg = msg + '; State buffer was %s' % state_buffer
        self.assertIn(state, stoppedStates, msg)

    def macro_stops(self, macro_params=None, stop_delay=0.1,
                    wait_timeout=float("inf")):
        """A helper method to create tests that check if the macro can be
        successfully stoped (a.k.a. aborted) after it has been launched.

        :param macro_params: (seq<str>): parameters for running the macro.
                             If passed, they must be given as a sequence of
                             their string representations.
        :param stop_delay: (float) Time (in s) to wait between launching the
                           macro and sending the stop command. default=0.1
        :param wait_timeout: (float) maximum allowed time (in s) for the macro
                             to finish. By default infinite timeout is used.
        """
        self.macro_executor.run(macro_name=self.macro_name,
                                macro_params=macro_params,
                                sync=False)

        if stop_delay is not None:
            time.sleep(stop_delay)
        self.macro_executor.stop()
        self.macro_executor.wait(timeout=wait_timeout)
        self.assertStopped('Macro %s did not stop' % self.macro_name)


if __name__ == '__main__':
    from taurus.external import unittest
    from sardana.macroserver.macros.test import SarDemoEnv

    _m1 = SarDemoEnv().getMotors()[0]

    #@testRun(macro_params=[_m1, '0', '100', '4', '.1'])
    @testRun(macro_params=[_m1, '1', '0', '2', '.1'])
    @testRun(macro_params=[_m1, '0', '1', '4', '.1'])
    class dummyAscanTest(RunStopMacroTestCase, unittest.TestCase):
        macro_name = 'ascan'

    @testRun(macro_params=['1'], data={'in': 1, 'out': 2})
    @testRun(macro_params=['5'])
    @testRun
    class dummyTwiceTest(RunStopMacroTestCase, unittest.TestCase):
        macro_name = 'twice'

    @testFail
    @testFail(exception=Exception)
    class dummyRaiseException(RunStopMacroTestCase, unittest.TestCase):
        macro_name = 'raise_exception'

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        dummyRaiseException)
    unittest.TextTestRunner(descriptions=True, verbosity=2).run(suite)


.. currentmodule:: sardana.test.

.. _sardana-test-driven-devel-example:



===============================
Test-driven development example
===============================


In this section it is presented a practical example of how to code a macro
by doing test-driven development thanks to the tools provided by the Sardana
Test Framework.

Consider that we want to write a new macro named "sqrtmac" for calculating the 
square root of an input number. The "sqrtmac" specifications are:

1. Its data must be given in the form {'in':x,'out':s}
2. Its output ('out') must be the square root of the input data ('in').
3. Macro must raise an Exception of type ValueError if negative numbers are given as input.


Test development
----------------

First we design the tests according to the specifications considering the 
features that are required for the macro. For doing so we will need some 
imports in order to be able to use the base classes and decorators. 
In this case the important base class is RunMacroTestCase, and
we import testRun and testFail to be used as decorators::

    """Tests for sqrt macro"""
    import numpy as np
    import unittest
    from sardana.macroserver.macros.test import RunMacroTestCase, testRun, testFail


Now we will write a basic test, that will check the execution of the sqrtmac for 
a given input x = 12345.678. For doing so, we inherit from unittest and 
from RunMacroTestCase. In this implementation we will calculate in the test the 
sqrt of the input parameter and then, using assertEqual, we will verify that 
this value is equal to the output of the macro. The helper method macro_runs is 
used for executing the macro::

    """Tests for a macro calculating the sqrt of an input number"""
    import numpy as np
    import unittest
    from sardana.macroserver.macros.test import RunMacroTestCase, testRun, testFail


    class sqrtmacTest(RunMacroTestCase, unittest.TestCase):
        """Test of sqrt macro. It verifies that macro sqrt can be executed.
        """
        macro_name = "sqrtmac"

        def test_sqrtmac(self):
            
            macro_params = [str(x)]
            self.macro_runs(macro_params)

            data=self.macro_executor.getData()
            expected_output = 49

            msg = 'Macro output does not equals the expected output'
            self.assertEqual(data['in'] ,float(macro_params[0]), msg)      
            self.assertEqual(data['out'] ,expected_output, msg)


Now, two new tests are added thanks to the decorator and the helper functions. 
In this case we will use the decorator @testRun. The same test case can be
launched with different sets of parameters. One decorator is used for each set 
of parameters. 

One of the tests will run the sqrtmac macro for an input value of 9 and 
verify that the macro has been executed without problems. 

Another test added will run the sqrt for an input of 2.25 and will verify 
its input and output values against the expected values which we pass to the 
decorator. A wait_timeout of 5s will be given;  this means, that if the test 
does not finish within 5 seconds, the current test will give an error and 
the following test will be executed:: 


    """Tests for a macro calculating the sqrt of an input number"""
    import numpy as np
    import unittest
    from sardana.macroserver.macros.test import RunMacroTestCase, testRun, testFail


    @testRun(macro_params=['9'])
    @testRun(macro_params=['2.25'], data={'in':2.25,'out':1.5}, wait_timeout=5)
    class sqrtmacTest(RunMacroTestCase, unittest.TestCase):
        """Test of sqrt macro. It verifies that macro sqrt can be executed.
        """
        macro_name = "sqrtmac"

        def test_sqrtmac(self):
            
            macro_params = [str(x)]
            self.macro_runs(macro_params)

            data=self.macro_executor.getData()
            expected_output = 49

            msg = 'Macro output does not equals the expected output'
            self.assertEqual(data['in'] ,float(macro_params[0]), msg)      
            self.assertEqual(data['out'] ,expected_output, msg)



The following test implemented must check that the macro is raising an Exception 
if negative numbers are passed as input. The type of exception raised must be a 
ValueError. For developing this test we will use the decorator testFail which 
allows to test if a macro is raising an Exception before finishing its 
execution. The final implementation of our test file test_sqrt.py is as 
follows::


    """Tests for a macro calculating the sqrt of an input number"""
    import numpy as np
    import unittest
    from sardana.macroserver.macros.test import RunMacroTestCase, testRun, testFail

    @testRun(macro_params=['9'])
    @testRun(macro_params=['2.25'], data={'in':2.25,'out':1.5}, wait_timeout=5)
    @testFail(macro_params=['-3.0'], exception=ValueError, wait_timeout=5)
    class sqrtmacTest(RunMacroTestCase, unittest.TestCase):
        """Test of sqrt macro. It verifies that macro sqrt can be executed.
        """
        macro_name = "sqrtmac"

        def test_sqrtmac(self):
            
            macro_params = [str(x)]
            self.macro_runs(macro_params)

            data=self.macro_executor.getData()
            expected_output = 49

            msg = 'Macro output does not equals the expected output'
            self.assertEqual(data['in'] ,float(macro_params[0]), msg)      
            self.assertEqual(data['out'] ,expected_output, msg)



Macro development
-----------------

Thanks to the test that we have designed precedently we can now implement 
the macro and check if it is developed according to the specifications.

We do a first implementation of the macro by calculating the square root
of an input number. Then we will execute the test and analyze the results. The
first implementation looks like this::

    import numpy as np
    from sardana.macroserver.macro import Macro, Type

    class sqrtmac(Macro):
        """Macro sqrtmac"""

        param_def = [ [ "value", Type.Float, 9, 
                        "input value for which we want the square root"] ]
        result_def = [ [ "result", Type.Float, None,
                         "square root of the input value"] ]

        def run (self, n):
            ret = np.sqrt(n)
            return ret



An its ouput on the screen::

    sardana/src/sardana/macroserver/macros/test> python -m unittest -v test_sqrtmac
    test_sqrtmac (test_sqrtmac.sqrtmacTest) ... ERROR
    test_sqrtmac_macro_fails (test_sqrtmac.sqrtmacTest)
    Testing sqrtmac with macro_fails(macro_params=['-3.0'], exception=<type 'exceptions.ValueError'>, wait_timeout=5) ... FAIL
    test_sqrtmac_macro_runs (test_sqrtmac.sqrtmacTest)
    Testing sqrtmac with macro_runs(macro_params=['2.25'], wait_timeout=5, data={'out': 1.5, 'in': 2.25}) ... ERROR
    test_sqrtmac_macro_runs_2 (test_sqrtmac.sqrtmacTest)
    Testing sqrtmac with macro_runs(macro_params=['9']) ... ok

    ======================================================================
    ERROR: test_sqrtmac (test_sqrtmac.sqrtmacTest)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
                .
                .
                .
        desc = Exception: Macro 'sqrtmac' does not produce any data


    ======================================================================
    ERROR: test_sqrtmac_macro_runs (test_sqrtmac.sqrtmacTest)
    Testing sqrtmac with macro_runs(macro_params=['2.25'], wait_timeout=5, data={'out': 1.5, 'in': 2.25})
    ----------------------------------------------------------------------
    Traceback (most recent call last):
                .
                .
                .
        desc = Exception: Macro 'sqrtmac' does not produce any data
               

    ======================================================================
    FAIL: test_sqrtmac_macro_fails (test_sqrtmac.sqrtmacTest)
    Testing sqrtmac with macro_fails(macro_params=['-3.0'], exception=<type 'exceptions.ValueError'>, wait_timeout=5)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/siciliarep/tmp/mrosanes/workspace/GIT/projects/sardana/src/sardana/macroserver/macros/test/base.py", line 144, in newTest
        return helper(**helper_kwargs)
      File "/siciliarep/tmp/mrosanes/workspace/GIT/projects/sardana/src/sardana/macroserver/macros/test/base.py", line 271, in macro_fails
        self.assertEqual(state, 'exception', msg)
    AssertionError: Post-execution state should be "exception" (got "finish")

    ----------------------------------------------------------------------
    Ran 4 tests in 0.977s

    FAILED (failures=1, errors=2)


At this moment two tests are giving an error because 'sqrtmac' does not produce
data, and one test is failing because the exception is not treat. 
The test that is giving 'Ok' is only testing that the macro can be
executed.

The second step will be to set the input and output data of the macro and 
execute the test again::

    import numpy as np
    from sardana.macroserver.macro import Macro, Type

    class sqrtmac(Macro):
        """Macro sqrtmac"""

        param_def = [ [ "value", Type.Float, 9, 
                        "input value for which we want the square root"] ]
        result_def = [ [ "result", Type.Float, None,
                         "square root of the input value"] ]

        def run (self, n):
            ret = np.sqrt(n)
            self.setData({'in':n,'out':ret})
            return ret


An its ouput on the screen::

    sardana/macroserver/macros/test> python -m unittest -v test_sqrtmac
    test_sqrtmac (test_sqrtmac.sqrtmacTest) ... ok
    test_sqrtmac_macro_fails (test_sqrtmac.sqrtmacTest)
    Testing sqrtmac with macro_fails(macro_params=['-3.0'], exception=<type 'exceptions.ValueError'>, wait_timeout=5) ... FAIL
    test_sqrtmac_macro_runs (test_sqrtmac.sqrtmacTest)
    Testing sqrtmac with macro_runs(macro_params=['2.25'], wait_timeout=5, data={'out': 1.5, 'in': 2.25}) ... ok
    test_sqrtmac_macro_runs_2 (test_sqrtmac.sqrtmacTest)
    Testing sqrtmac with macro_runs(macro_params=['9']) ... ok

    ======================================================================
    FAIL: test_sqrtmac_macro_fails (test_sqrtmac.sqrtmacTest)
    Testing sqrtmac with macro_fails(macro_params=['-3.0'], exception=<type 'exceptions.ValueError'>, wait_timeout=5)
    ----------------------------------------------------------------------
    Traceback (most recent call last):
      File "/siciliarep/tmp/mrosanes/workspace/GIT/projects/sardana/src/sardana/macroserver/macros/test/base.py", line 142, in newTest
        return helper(**helper_kwargs)
      File "/siciliarep/tmp/mrosanes/workspace/GIT/projects/sardana/src/sardana/macroserver/macros/test/base.py", line 267, in macro_fails
        self.assertEqual(state, 'exception', msg)
    AssertionError: Post-execution state should be "exception" (got "finish")

    ----------------------------------------------------------------------
    Ran 4 tests in 0.932s

    FAILED (failures=1)

As we can see, the test_sqrtmac_macro_fails is Failing, because the case of
negative numbers is still not suppported. The rest of tests that are testing the 
execution and the expected output values are OK.



Finally we arrive to the complete implementation of the macro taking into 
account the Exception that should be raised if we enter a negative number
as input parameter. For coding this macro test-driven development has been
used::

    import numpy as np
    from sardana.macroserver.macro import Macro, Type

    class sqrtmac(Macro):
        """Macro sqrtmac"""

        param_def = [ [ "value", Type.Float, 9, 
                        "input value for which we want the square root"] ]
        result_def = [ [ "result", Type.Float, None,
                         "square root of the input value"] ]

        def run (self, n):
            if (n<0):
                raise ValueError("Negative numbers are not accepted.")

            ret = np.sqrt(n)
            self.setData({'in':n,'out':ret})
            return ret  


An the output on the console after executing the test looks like this::

    sardana/macroserver/macros/test> python -m unittest -v test_sqrtmac
    test_sqrtmac (test_sqrtmac.sqrtmacTest) ... ok
    test_sqrtmac_macro_fails (test_sqrtmac.sqrtmacTest)
    Testing sqrtmac with macro_fails(macro_params=['-3.0'], exception=<type 'exceptions.ValueError'>, wait_timeout=5) ... ok
    test_sqrtmac_macro_runs (test_sqrtmac.sqrtmacTest)
    Testing sqrtmac with macro_runs(macro_params=['2.25'], wait_timeout=5, data={'out': 1.5, 'in': 2.25}) ... ok
    test_sqrtmac_macro_runs_2 (test_sqrtmac.sqrtmacTest)
    Testing sqrtmac with macro_runs(macro_params=['9']) ... ok

    ----------------------------------------------------------------------
    Ran 4 tests in 0.928s

    OK



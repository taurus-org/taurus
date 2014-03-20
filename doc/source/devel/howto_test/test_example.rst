
.. currentmodule:: sardana.test.

.. _sardana-test-driven-devel-example:



===============================
Test-driven development example
===============================


In this section it is presented a practical example of how to code a macro
by doing test-driven development thanks to the tools provided by the Sardana
test framwork.

Consider that we want to write a new macro named "sqrtmac" and we want to do 
test-driven development. The "sqrtmac" specifications are:

1. Its data must be {'input':x,'output':s}
2. Its output must be the square root of the input data.
3. Macro must rase an Exception of type ValueError if negative numbers are 
given as input.


Test development
----------------

First we design the Test according to the specifications and knowing the 
features that are required for the macro.

First we need some imports in order to be able to use the base classes and
decorators. In this case the important base class is RunMacroTestCase, and
we import testRun and testFail. The decorator will allow us::

    """Tests for sqrt macro"""
    import math
    import unittest
    from sardana.macroserver.macros.test import RunMacroTestCase
    from sardana.macroserver.macros.test import testRun
    from sardana.macroserver.macros.test import testFail


Now we will write a basic test: "the macro should run Ok if we give x=9".
For that we inherit from unittest and from RunMacroTestCase. That will allow
to run the macro and see if the execution is Ok. For doing so we will use the
decorator @testRun with an input parameter of 9. We use a wait_timeout to 
specify that the test will fail if it is not finished in a given time::

    @testRun(macro_params=['9'], wait_timeout=5)
    class sqrtRunMacroAutoTest(RunMacroTestCase, unittest.TestCase):
        """Test of sqrt macro. It verifies that macro sqrt can be executed.
        """
        macro_name = "sqrtmac"


The output in the console for this test when executing:

**python -m unittest -v test_sqrtmac**

is:

test_sqrtmac_macro_runs_2 (test_sqrtmac.sqrtRunMacroAutoTest)

Testing sqrtmac with macro_runs(macro_params=['9'], wait_timeout=5) ... ok


Then we will complete our precedent implementation. With the help of the 
decorator we will include another test. In this case the class RunMacroTestCase 
with the helper method macro_runs will allow to test the input and the output 
data of the macro against the expected values that we give as input parameters 
to the decorator::

    @testRun(macro_params=['9'], wait_timeout=5)
    @testRun(macro_params=['2.25'], data={'in':2.25,'out':1.5}, wait_timeout=5)
    class sqrtRunMacroAutoTest(RunMacroTestCase, unittest.TestCase):
        """Test of sqrt macro. It verifies that macro sqrt can be executed.
        """
        macro_name = "sqrtmac"


In this case we give an input of 2.25 and we verify that its square root is 1.5.
If we execute the test again, the outputs in the console are:

Testing sqrtmac with macro_runs(macro_params=['9'], wait_timeout=5) ... ok

test_sqrtmac_macro_fails (test_sqrtmac.sqrtRunMacroExceptionTest)

Testing sqrtmac with macro_runs(macro_params=['2.25'], wait_timeout=5, data={'out': 1.5, 'in': 2.25}) ... ok

test_sqrtmac_macro_runs_2 (test_sqrtmac.sqrtRunMacroAutoTest)





The following test must check if the macro is raising an Exception if 
negative numbers are passed as input. The type of exception raised must be a 
ValueError::

    @testFail(macro_params=['-3.0'], exception=ValueError, wait_timeout=5)
    class sqrtRunMacroExceptionTest(RunMacroTestCase, unittest.TestCase):
        """Test of sqrt macro gives an exception when input value is negative. 
        """
        macro_name = "sqrtmac"

And the console output after execution:

Testing sqrtmac with macro_fails(macro_params=['-3.0'], exception=<type 'exceptions.ValueError'>, wait_timeout=5) ... ok

test_sqrtmac_macro_runs (test_sqrtmac.sqrtRunMacroTest)

Finally it is shown how to develop a test for testing the macro in an 
alternative way. This gives more control to the developer, as it allows to
override the method macro_runs from the parent class RunMacroTestCase.
Here we will calculate ourselves the sqrt of the input parameter and then
with assertEqual we will verify that this value is equal to the output of 
the macro::


    @testRun(macro_params=['16.0'], wait_timeout=5)
    class sqrtRunMacroTest(RunMacroTestCase, unittest.TestCase):
        """Test of sqrt macro. It verifies that macro sqrt can be executed.
        """
        macro_name = "sqrtmac"

        def macro_runs(self, macro_params=None, wait_timeout=float("inf")):
            
            RunMacroTestCase.macro_runs(self, macro_params=macro_params, 
                                  wait_timeout=wait_timeout)

            data=self.macro_executor.getData()
            expected_output = math.sqrt(float(macro_params[0]))

            msg = 'Macro output does not equals the expected output'        
            self.assertEqual(data['out'] ,expected_output, msg) 
 


And putting all the code together we have the following test module 
test_sqrtmac::

    """Tests for sqrt macro"""
    import math
    import unittest
    from sardana.macroserver.macros.test import RunMacroTestCase
    from sardana.macroserver.macros.test import testRun
    from sardana.macroserver.macros.test import testFail


    @testRun(macro_params=['9'], wait_timeout=5)
    @testRun(macro_params=['2.25'], data={'in':2.25,'out':1.5}, wait_timeout=5)
    class sqrtRunMacroAutoTest(RunMacroTestCase, unittest.TestCase):
        """Test of sqrt macro. It verifies that macro sqrt can be executed.
        """
        macro_name = "sqrtmac"


    @testFail(macro_params=['-3.0'], exception=ValueError, wait_timeout=5)
    class sqrtRunMacroExceptionTest(RunMacroTestCase, unittest.TestCase):
        """Test of sqrt macro gives an exception when input value is negative. 
        """
        macro_name = "sqrtmac"


    @testRun(macro_params=['16.0'], wait_timeout=5)
    class sqrtRunMacroTest(RunMacroTestCase, unittest.TestCase):
        """Test of sqrt macro. It verifies that macro sqrt can be executed.
        """
        macro_name = "sqrtmac"

        def macro_runs(self, macro_params=None, wait_timeout=float("inf")):
            
            RunMacroTestCase.macro_runs(self, macro_params=macro_params, 
                                  wait_timeout=wait_timeout)

            data=self.macro_executor.getData()
            expected_output = math.sqrt(float(macro_params[0]))

            msg = 'Macro output does not equals the expected output'        
            self.assertEqual(data['out'] ,expected_output, msg)





And the output in the console when we execute:

**python -m unittest -v test_sqrtmac**

is:

test_sqrtmac_macro_runs (test_sqrtmac.sqrtRunMacroAutoTest)

Testing sqrtmac with macro_runs(macro_params=['2.25'], wait_timeout=5, data={'out': 1.5, 'in': 2.25}) ... ok

test_sqrtmac_macro_runs_2 (test_sqrtmac.sqrtRunMacroAutoTest)

Testing sqrtmac with macro_runs(macro_params=['9'], wait_timeout=5) ... ok

test_sqrtmac_macro_fails (test_sqrtmac.sqrtRunMacroExceptionTest)

Testing sqrtmac with macro_fails(macro_params=['-3.0'], exception=<type 'exceptions.ValueError'>, wait_timeout=5) ... ok

test_sqrtmac_macro_runs (test_sqrtmac.sqrtRunMacroTest)

Testing sqrtmac with macro_runs(macro_params=['16.0'], wait_timeout=5) ... ok

Ran 4 tests in 0.981s

OK



Macro development
-----------------

Thanks to the test that we have designed precedently we can now design 
the macro and check if it is developed according to the specifications.
We will name 'sqrtmac' our test-driven developed macro; and it will look
like this::


    import math
    from sardana.macroserver.macro import Macro, macro, Type


    class sqrtmac(Macro):
        """Macro sqrtmac"""

        param_def = [ [ "value", Type.Float, 23, 
                        "input value for which we want the square root" ] ]
        result_def = [ [ "result", Type.Float, 23, 
                        "square root of the input value" ] ]
        
        def run(self, n):
            if (n>=0):
                ret = math.sqrt(n)
            else:
                raise ValueError("negative numbers are not accepted")
                ret = None
            self.setData({'in':n, 'out':ret})
            return ret 





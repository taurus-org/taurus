.. highlight:: python
   :linenothreshold: 5
   
.. currentmodule:: sardana.macroserver.macros.test


.. _sardana-test-general-howto:


===============
Sardana Testing
===============

Sardana Test Framework
----------------------------


A testing framework allowing to test the Sardana features is included with the
Sardana distribution. It is useful for test-driven development and it allows 
to find bugs in the code. 

The first implementation of the Framework is an outcome of the `Sardana 
Enhancement Proposal 5 (SEP5)`_. 

Ideally, whenever possible, bug reports should be accompanied by a test 
revealing the bug.


The first tests implemented are focused on Unit Tests, but the same framework
should be used for integration and system tests as well.

The sardana.test module includes testsuite.py. This file provides an 
auto-discovering suite for all tests implemented in Sardana.

The following are some key points to keep in mind when using this framework:

- The Sardana Test Framework is based on :mod:`unittest` which should be 
  imported from :mod:`taurus.external` in order to be compatible with all 
  versions of python supported by Taurus. 

- all test-related code is contained in submodules named `test` which appear 
  in any module of Sardana.
  
- test-related code falls in one of these three categories: 
    * Actual test code (classes that derive from unittest.TestCase)
    * Utility classes/functions (code to simplify development of test code)
    * Resources (accessory files required by some test). They are located in 
      subdirectories named `res` situated inside the folders named `test`. 

For a more complete description of the conventions on how to write tests with
the Sardana Testing Framework, please refer to the 
[SEP5](http://sourceforge.net/p/sardana/wiki/SEP5/).



Sardana Test Framework for testing macros
-----------------------------------------

Sardana Test Framework provides tools for testing macros. These tools come 
from sardana.macroserver.macros.test module

Tests meant to be incorporated in the Sardana distribution must be portable. 
For this reason it is strongly encouraged to use only elements created
by the sar_demo macro. Only in the case where this is not possible, one may 
create specific elements for a test; these elements must be removed at the 
end of the test execution (e.g. using the tearDown method).

The module :mod:`sardana.macroserver.macros.test` provides utilities to simplify 
the tests for macro execution and macro stop. Macro test classes can inherit 
from :class:`.RunMacroTestCase`, 
:class:`.RunStopMacroTestCase` or 
:class:`.BaseMacroTestCase`.

Another utility provided is the option to execute the same test with 
many different macro input parameters. This is done  by decorating the test 
class with any of the decorators of the the macro tests family. 

This decorator is provided by :mod:`sardana.macroserver.macros.test`.


**Specificities:**

* Macros such as 'lsm' inherit from RunMacroTestCase as it is interesting to 
  test if the macros can be executed. Helper methods 
  ( such as :meth:`.RunMacroTestCase.macro_runs` ) can be overriden when 
  programming new test cases. New helpers can be created as well.

* Scan macros inherits from RunStopMacroTestCase as it is interesting to test 
  both: if the macros can be executed and if they can be aborted.




Links
-----

For a more complete description of the conventions used when writing tests, see:
http://sourceforge.net/p/sardana/wiki/SEP5/

For more information about unittest framework:
http://docs.python.org/2/library/unittest.html


.. _Sardana Enhancement Proposal 5 (SEP5): http://sourceforge.net/p/sardana/wiki/SEP5/ 






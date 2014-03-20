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

A first implementation of the Framework is an outcome of the Sardana Enhancement 
Proposal 5 (SEP5). 

SEP5 documentation is located here: http://sourceforge.net/p/sardana/wiki/SEP5/ 

Ideally, each bug found should be accompanied by a test revealing the bug.
That eases the process of correcting them. 

Sardana test framework should ease Sardana collaborations and allow people from 
different institutions to provide their own test classes.

Currently (03-2014) Sardana testing is focused on unit tests, but in the future 
the objective is to extend it to integration and system tests as well.

The test framework is based on 'unittest'. This means that each of the 
Sardana python test classes inherits from unittest.TestCase. 

More information about the module unittest can be found here: 
http://docs.python.org/2/library/unittest.html

All tests have to be written in folders named 'test/'.
Each of the Sardana Tests has to be acompanied by a documentation that is
written in the module, class and method docstrings; as well as in the assert
methods. 

Sardana test framework provides tools for testing macros. These tools comes 
from:

* sardana/src/sardana/macroserver/macros/test/base.py
* sardana/src/sardana/macroserver/macros/test/macroexecutor.py
* sardana/src/sardana/macroserver/macros/test/sardemoenv.py
* sardana/src/sardana/tango/macroserver/test/macroexecutor.py

Tests meant to be incorporated in the Sardana distribution must be portable. 
For this reason the elements used in them must be the elements that are created
with sar_demo macro. Only in the case where this is not possible, it is allowed 
to create specific elements for a test; these elements has to be removed at the 
end of the test execution.

The module **base** provides the mean of executing macros and test the that can 
be executed and some of them stopped (e.g. the scans). Macro test classes 
can inherit from RunMacroTestCase, RunStopMacroTestCase or BaseMacroTestCase.

Macros as 'lsm' inherits from RunMacroTestCase as it is interesting to test
if the macros can be executed. The method macro_runs() defined in the class 
RunMacroTestCase can be overrided unittest.TestCase classes if we want to 
provide the method with more functionalities.

Scan macros inherits from RunStopMacroTestCase as it is interesting 
to test both: if the macros can be executed and if they can be aborted.

Another capacity provided by the framework is the option to execute the 
same test method with many different macro input parameters. This is done 
thanks to a decorator inserted at the beginning of each test method.
This decorator is written in the module **base**.

One decorator has to be used for each set of macro input parameters. Examples 
of the decorator usage can be seen in: test_scan.py

If new tests of scan macros or list macros have to be added, that can be 
done in test_scan.py or in test_list.py where a useful base class is 
provided.



Examples of tests
-----------------

Examples of Sardana tests included in the Sardana distribution are:

* sardana/src/sardana/test/test_sardanavalue.py 
* sardana/src/sardana/test/test_parameter.py
* sardana/src/sardana/macroserver/macros/test_ct.py
* sardana/src/sardana/macroserver/macros/test_list.py
* sardana/src/sardana/macroserver/macros/test_wm.py




Links
-----

http://sourceforge.net/p/sardana/wiki/SEP5/

http://docs.python.org/2/library/unittest.html



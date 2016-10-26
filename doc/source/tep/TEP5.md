Title: Implementation of tests infrastructure
TEP: 5
State: DRAFT
Date: 2014-01-27
Drivers: Marc Rosanes Siscart <mrosanes@cells.es>; Carlos Pascual Izarra <cpascual@cells.es>; Tiago Coutinho <coutinho@esrf.fr>
URL: https://sourceforge.net/p/tauruslib/wiki/TEP5
License: http://www.jclark.com/xml/copying.txt
Abstract:
This TEP describes how to implement code testing in Taurus. 
It defines the conventions used in relation with code testing and describes the tools provided by taurus to help in developing tests


Introduction
------------

*This TEP is a copy of [SEP5](https://sourceforge.net/p/sardana/wiki/SEP5 "Sardana Enhancement Proposal 5")*

Code testing is necessary in Taurus mainly for the following reasons:
- It is necessary for Continuous Integration
- It helps integration managers in evaluating contributed code
- It facilitates adoption, contribution and packaging
- It helps detecting errors, bugs and regressions in the code
- It enables test-driven programming techniques
 
This TEP describes how to implement code testing in Taurus.
It focuses in:

- Describing concepts and conventions regarding code testing in taurus
- Defining a methodology for performing the tests
- Providing tools and reusable code to automate/facilitate test creation

Note that this TEP does not pretend to provide a set of tests covering most of Taurus, but just providing the general tools and guidelines which would enable such tests to be written.


Glossary
-------------------

[Unit testing](http://en.wikipedia.org/w/index.php?title=Unit_testing&oldid=585783088): has the goal of isolate each part of the program and show that individual parts are correct in terms of requirements and functionality.

[Integration testing](http://en.wikipedia.org/w/index.php?title=Integration_testing&oldid=579207501): consists of testing combined parts of an application to determine if they function correctly together.

[System testing](http://en.wikipedia.org/w/index.php?title=System_testing&oldid=563079756): System tests are used to test the system as a whole. Here the system is typically seen as a black-box.

Module: in this TEP we use 'module' to refer to a Python (sub)module that can be implemented either as a .py file or as a directory containing an `__init__.py` file.  

 



Description of situation previous to TEP5
-----------------------------------------

The situation in pre-TEP5 is that the testing process is poorly implemented in Taurus: testing is informal and non-automatic, and different approaches for testing are used for different parts of the code. 

Goals & Constrains
------------------

The following goals and constraints are taken into consideration for this proposal:

- A common framework should be defined.
- Tests code should be easily identifiable and not mixed with "implementation" code.
- Tests included in taurus must not depend on external infrastructure: an isolated machine in which taurus is installed and configured should be able to run all the tests.
- The testing framework should avoid or minimize introducing new dependencies to Taurus.
- Whenenever possible, tests should be automatic (capable of running unatended).
- Taurus should provide helper code to simplify the creation of new tests.
- Optionally: Ease code coverage report.



Implementation
--------------

In this section we present the framework, naming convention and organizational structure that we should follow when testing Taurus. Hereafter the basis for documenting and coding using the framework PyUnit are presented.

In Taurus we use Unit testing (white box testing) as a first testing level. Integration and System testing (grey/black box testing) are performed as a second testing level.

####1- Framework####
The framework used to perform the Tests is PyUnit. A great number of features provided by PyUnit are only available for Python >= 2.7. For this reason Taurus tests are coded with *Python >= 2.7*; therefore this is an exception of the Taurus convention.

PyUnit framework is used by importing the module 'unittest'. It allows us to avoid adding extra dependencies for testing because this framework is present in the standard Python library.
See following link: 
http://docs.python.org/2/library/unittest.html#module-unittest

If needed, PyQt4.QtTest can be used for aiding in the test of Qt widgets.




####2- Organization####

Three main kind of files can be found in our Test framework. The **Test modules** inside which the tests will be coded, the **Util modules** and the **Resources**. 

All these files shall be placed under subdirectories named 'test'. The *test* subdirectories can be located inside any Taurus source subfolder according with the part of the code that our test module is testing. 

Each *test* directory must have an `__init__.py` file in order to allow them to be importable. This file can be empty except for the standard license header or it can contain documentation in the module docstring.


**Test modules**

Names of python modules for testing are formed by the 'test_' prefix, followed by the name of the module being tested (in the case of Unit tests) or by a name describing the functionality being tested (in the case of Integration and System tests).

Hereafter we give some examples of possible Taurus test modules and its organization inside the Taurus code tree:

Example1: for a Unit Test which is testing the module taurusdevice.py located in taurus/lib/taurus/core, we create a folder **test** inside the folder core (taurus/lib/taurus/core/test) and we can place here our test module test_taurusdevice (either implemented as a test_taurusdevice.py file or as a subdirectory named test_taurusdevice containing an `__init__.py` file).

Example2: for a stress test of the taurusform, the test module is located in taurus/lib/taurus/qt/qtgui/panel/test/ and can be called test_stress.py.

**Util modules** 
Test directories can have a series of *Util modules* containing common classes and methods that can be imported by other modules (i.e. start gui, stop gui, command execution, etc.). These *Util modules* will not contain any test case and shall NOT be prefixed by 'test_'. Other than that, they can be named freely.

**Resources**
Test directories can contain a directory named **res**, with any necessary resource files for our test. A resource file could be for example: myresource.txt. There are no restrictions at all for the resource naming.

*res* directories must contain an `__init__.py` file in order to ease resource localization.




####3- Coding####
In order to begin coding tests, the information presented here is useful for the test developer. 

The first point refers to the test documentation, that has to be written while coding a specific test. The second point refers to the coding itself using the 'unittest' python module from PyUnit framework. 



#####**Test Case Documentation**#####


Every python test module can contain multiple classes. Each one of these classes is a Test Case that inherits from 'unittest.TestCase'. Each class can have multiple methods testing different features. 

The tests documentation is written at the Module, Class and Method docstrings using sphinx. In the case of method docstrings, it is recommended to limit the use of sphinx formatting to a level where it is legible as plain text (because PyUnit uses method docstrings in its test summaries).

The following is a list of elements that should be documented (while they are mandatory for integration/system tests, most are optional for unit tests, as indicated in each case):

TODO: describe documentation formatting conventions (for the moment just see attached example). 

- General module comments: 
    - Description of common aspects to the various classes inside a test module.
    - Location inside the code: General comments are written in the module docstring.
    - Optional in all cases (unit, integration and system test modules) 

- Test Case ID: 
    - try to be unique, compose the id from project name, module, submodule, etc. and assign them consecutive numbers. Uppercase and underscore separated IDs are preferred. E.g. MACROSERVER_SCAN_1, POOL_MOTION_123.
    - Location inside the code: Test Case ID is written in the Class docstring.
    - Optional for unit tests

- Title: 
    - Test case title. 
    - Location inside the code: The Title is written in the Class docstring.
    - Optional for unit tests

- Description:
    - Brief explanation about the aspect of the system that is going to be tested. All aspects common in all the methods belonging to the Class can be commented in this field. 
    - Location inside the code: The Description is written in the Class docstring. 

- Automation
    - Whether this test case is automated or not.
    - Location inside the code: The Automation field is written in the Class docstring.
    - Optional for unit tests.

- Steps
    - List the test execution steps in detail. Write the test steps in the order in which these should be executed. Make sure to provide as much details as you can.
    - Location inside the code: The Steps are written in the TestCase Class docstring and may be referenced in the method docstring.
    - Optional for unit tests.

- Preconditions
    - Any prerequisite that must be fulfilled before execution of the test case. List all pre-conditions in order to successfully execute this test case.  
    - Location inside the code: The Preconditions are written in the docstring of the setUp method.

- Purpose
    - Brief explanation of what a given method is testing.
    - Location inside the code: The Purpose is written in each Test Case method docstring.

- Input Data
    - Description of the input data to be used for this test case. Different data sets with exact values can be provided to be used as input.
    - Location inside the code: The Input Data is written in each Test Case method docstring.

- Expected Results
    - Description of what should be the system output after test execution. Describe the expected results including message/error that should be displayed on screen. 
    - Location inside the code: The expected results are written in the *assert* strings. Optionally they can be described in each Test Case method docstring.

- Post-Conditions
    - What should be the state of the system after executing this test case.
    - Location inside the code: The Post-Conditions are written in the docstring of the method tearDown.





#####**Testing using PyUnit unittest framework**######

Each Taurus Test Case is a class that inherits from unittest.TestCase.

Abstract classes to be inherited by a Taurus Test Case must not inherit from unittest.TestCase, to avoid them being automatically included in test suites by unittest. Instead, multiple inheritance is to be used by the Taurus Test Case class.

Each test is implemented in a separate method which name begins by 'test' and it is written in camelCase. 

Preconditions are implemented in the 'setUp' method, and postconditions are implemented in the 'tearDown' method. Note that 'setUp' and 'tearDown' will be executed before and after each test method. The implementation of these two methods is not mandatory but it can be useful.

(TODO: Describe Taurus specific conventions for test Suites).

For a detailed description on how to code using the PyUnit framework, you can refer to the following link: 
http://docs.python.org/2/library/unittest.html



Links for more details and discussions
--------------------------------------
The discussions about the TEP5 itself are in the [tauruslib-devel mailing list](https://sourceforge.net/p/tauruslib/mailman/).



License
-------
The following copyright statement and license apply to TEP5 (this
document).

Copyright (c) 2013 Marc Rosanes Siscart - Carlos Pascual Izarra

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Changes
-------

2013-07-01
[mrosanes](https://sourceforge.net/u/mrosanes/) Creation of SEP5

2013-08-19
[mrosanes](https://sourceforge.net/u/mrosanes/) modified SEP5. We have added various sections: logical structure, implementation, etc. Reason: Internal discussions at Alba between zreszela, cpascual and mrosanes.

2013-08-21
[mrosanes](https://sourceforge.net/u/mrosanes/) added the section Changes in order to keep a tracking of the changed done, by creating a log. Reason: Internal discussions at Alba between zreszela, cpascual and mrosanes.

2013-08-22
[mrosanes](https://sourceforge.net/u/mrosanes/) deletes references to Taurus, as Taurus is part of Sardana.

2013-08-23
[mrosanes](https://sourceforge.net/u/mrosanes/) modified the chapter implementation, structure and naming convention after speaking about it at Alba between cpascual, zreszela and mrosanes.

2013-08-26
[mrosanes](https://sourceforge.net/u/mrosanes/) modified the chapter documentation after speaking about it at Alba between cpascual, zreszela and mrosanes.

2013-08-26
[mrosanes](https://sourceforge.net/u/mrosanes/) documented the chapter coding by presenting the PyUnit framework.

2013-08-29
[mrosanes](https://sourceforge.net/u/mrosanes/) documented the chapter Implementation/Framework, remarking the usage of Python2.7 for coding the test modules. PyUnit requires Python2.7 for its full functionality.  

2013-09-02
[mrosanes](https://sourceforge.net/u/mrosanes/) added link to Sardana mailing list and archives.

2013-09-02
[mrosanes](https://sourceforge.net/u/mrosanes/) added details in integration/system test documentation.

2013-09-05
[mrosanes](https://sourceforge.net/u/mrosanes/) added details and corrections in test documentation.

2013-09-06
[mrosanes](https://sourceforge.net/u/mrosanes/) added example of test case documentation generated with Sphinx.

2013-09-06
[cpascual](https://sourceforge.net/u/cpascual/) of introductory text (abstract, intro, goals,... )

2013-11-26
[mrosanes](https://sourceforge.net/u/mrosanes/) minor changes in style and Implementation/Framework

2013-12-13
[mrosanes](https://sourceforge.net/u/mrosanes/) Section 'Theory' disappears and is fused with implementation. 'Glossary' section is created. 

2013-01-14
[mrosanes](https://sourceforge.net/u/mrosanes/) [cpascual](https://sourceforge.net/u/cpascual/) [zreszela](https://sourceforge.net/u/zreszela/) Modified and upgraded Implementation section.

2014-01-27
[tiagocoutinho](https://sourceforge.net/u/tiagocoutinho/) Initial version written as a copy of SEP5


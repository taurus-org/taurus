#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""

Taurus includes a framework allowing to test its features. This framework is 
aimed to be used with the objective of finding bugs and promote test driven 
development. \n

This Framework is the outcome of the Sardana Enhancement Proposal 5 (SEP5). Its 
documentation is located here: 
http://sourceforge.net/p/sardana/wiki/SEP5/ \n

Ideally, each bug found should be accompanied by a test revealing the bug.
That eases the process of correcting bugs. \n

The objective of the Taurus Test Framework is not to provide a test for 
every piece of code, but rather to ease the process of testing, boost 
collaborations and allow people from other institutions to provide their 
own tests. \n

At the moment Taurus testing is focused on Unit Tests, but in the future 
the objective is to extend it to integration and system tests as well. \n

In order to run all the tests provided by Taurus Test Framework, at a given 
moment, just go to 'sardana/taurus/lib/taurus/test' and execute:
python testsuite.py \n

All tests have to be written in folders named 'test/'. \n

Taurus Test Framework is based on 'unittest'. This means that each of the 
Taurus python test classes inherits from unittest.TestCase. \n

Each of the Taurus Tests has to be acompanied by a documentation that is
written in the module, class and method docstrings; as well as in the assert
methods. \n

Devices as motors and experimental channels used by the tests are coming from 
the execution of the macro sar_demo, because tests have to be reproducible. \n

Taurus Test Framework provides some testing utils. Some of them are: \n
* sardana/taurus/lib/taurus/test/moduleexplorer.py
* sardana/taurus/lib/taurus/test/resource.py
* sardana/taurus/lib/taurus/qt/qtgui/test/base.py

In base.py we found two classes that helps to program tests for widgets:
BaseWidgetTestCase and GenericWidgetTestCase. GenericWidgetTestCase inherits 
from BaseWidgetTestCase. It is possible to inherit from one of these classes
in order to program a new widget test case class. \n

Examples of Taurus tests using tools of Taurus Test Framework are: \n
* sardana/taurus/lib/taurus/test/test_import.py
* sardana/taurus/lib/taurus/qt/qtgui/button/test/test_taurusbutton.py
* sardana/taurus/lib/taurus/qt/qtgui/display/test/test_tauruslabel.py
* sardana/taurus/lib/taurus/qt/qtgui/panel/test/test_taurusform.py

"""



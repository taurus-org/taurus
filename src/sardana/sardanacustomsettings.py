#!/usr/bin/env python

#############################################################################
##
## This file is part of Sardana
## 
## http://www.sardana-controls.org/
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

"""This module contains some Sardana-wide default configurations.

The idea is that the final user may edit the values here to customize certain
aspects of Sardana.
"""

#:UnitTest door name: the door to be used by unit tests.
#:UNITTEST_DOOR_NAME Must be defined for running sardana unittests. 
UNITTEST_DOOR_NAME = "door/demo1/1"
#:UnitTests Pool DS name: Pool DS to use in unit tests.
UNITTEST_POOL_DS_NAME = "unittest1"
#:UnitTests Pool Device name: Pool Device to use in unit tests.
UNITTEST_POOL_NAME = "pool/demo1/1"

#:Size and number of rotating backups of the log files.
#:The Pool and MacroServer Device servers will use these values for their logs. 
LOG_FILES_SIZE = 1e7
LOG_BCK_COUNT = 5

#:Input handler for spock interactive macros. Accepted values are:
#: - "CLI": Input via spock command line. This is the default.
#: - "Qt": Input via Qt dialogs
SPOCK_INPUT_HANDLER = "CLI"

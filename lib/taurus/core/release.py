#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus
## 
## http://taurus-scada.org
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

__docformat__ = "restructuredtext"

"""
Release data for the taurus project. It contains the following members:

    - version : (str) version string
    - description : (str) brief description
    - long_description : (str) a long description
    - license : (str) license
    - authors : (dict<str, tuple<str,str>>) the list of authors
    - url : (str) the project url
    - download_url : (str) the project download url
    - platforms : list<str> list of supported platforms
    - keywords : list<str> list of keywords
"""

# -*- coding: utf-8 -*-



# Name of the package for release purposes.  This is the name which labels
# the tarballs and RPMs made by distutils, so it's best to lowercase it.
name = 'taurus'

# For versions with substrings (like 0.6.16.svn), use an extra . to separate
# the new substring.  We have to avoid using either dashes or underscores,
# because bdist_rpm does not accept dashes (an RPM) convention, and
# bdist_deb does not accept underscores (a Debian convention).


version_info = (3,6,0,'rc',0)
version = '.'.join(map(str, version_info[:3]))
revision = str(version_info[4])

description = "A framework for scientific/industrial CLIs and GUIs"

long_description = """Taurus is a python framework for control and data 
acquisition CLIs and GUIs in scientific/industrial environments. 
It supports multiple control systems or data sources: Tango, EPICS, spec... 
New control system libraries can be integrated through plugins."""

license = 'LGPL'

authors = {'Tiago'          : ('Tiago Coutinho','tiago.coutinho@esrf.fr'),
           'Pascual-Izarra' : ('Carlos Pascual-Izarra','cpascual@cells.es'),
           'Reszela'        : ('Zbigniew Reszela','zreszela@cells.es') }
            

url = 'http://www.taurus-scada.org'

download_url = 'http://pypi.python.org/packages/source/t/taurus'

platforms = ['Linux','Windows XP/2000/NT','Windows 95/98/ME']

keywords = ['CLI', 'GUI', 'PyTango', 'Tango', 'Shell']

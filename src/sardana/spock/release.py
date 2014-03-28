#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""Release data for the Spock project.
"""

# Name of the package for release purposes.  This is the name which labels
# the tarballs and RPMs made by distutils, so it's best to lowercase it.
name = 'spock'

# For versions with substrings (like 0.6.16.svn), use an extra . to separate
# the new substring.  We have to avoid using either dashes or underscores,
# because bdist_rpm does not accept dashes (an RPM) convention, and
# bdist_deb does not accept underscores (a Debian convention).

revision = '1'

#version = '0.8.1.svn.r' + revision.rstrip('M')
version = '1.0.0'

description = "An enhanced interactive Macro Server shell."

long_description = \
"""
Spock provides an interactive environment for interacting with the Tango
MacroServer Device. It is completely based on IPython which itself provides a 
replacement for the interactive Python interpreter with extra functionality.
 """

license = 'GNU'

authors = {'Tiago'          : ('Tiago Coutinho','tiago.coutinho@esrf.fr'),
           'Reszela'        : ('Zbigniew Reszela','zreszela@cells.es') ,
           'Pascual-Izarra' : ('Carlos Pascual-Izarra','cpascual@cells.es') }

url = ''

download_url = ''

platforms = ['Linux','Windows XP/2000/NT','Windows 95/98/ME']

keywords = ['Sardana', 'Interactive', 'MacroServer', 'Tango', 'Shell']

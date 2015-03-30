#!/bin/bash

#############################################################################
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

# Note: this is a helper script for creating the distribution packages
# It is meant for internal taurus distribution managers use so do not expect 
# in an arbitrary system (i.e. do not cry about bugs in this script)

#Create distribution packages
rm -rf build
#create windows installable
python setup.py bdist_wininst --plat-name win install --no-doc install_scripts --wrappers --ignore-shebang build --no-doc
#create source tarball (without docs)
rm  -rf build
python setup.py sdist 

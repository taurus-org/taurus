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

"""The core module"""

__docformat__ = "restructuredtext"

import release as Release
#from .enums import * #note: all the enums from enums.py were moved to taurusbasetypes.py
from .taurusbasetypes import *
from .taurusexception import *
from .taurusmodel import *
from .tauruslistener import *
from .taurusdevice import *
from .taurusattribute import *
from .taurusconfiguration import *
from .taurusdatabase import *
from .taurusfactory import *
from .taurusmanager import *
from .taurusoperation import *
from .tauruspollingtimer import *
from .taurusvalidator import *

# enable compatibility code with tau V1 if tauv1 package is present
try:
    from .tauv1 import *
except:
    pass


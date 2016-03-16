#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This package contains a collection of taurus widgets designed to display taurus
information, typically in a read-only fashion (no user interaction is possible).
Examples of widgets that suite this rule are labels, leds and LCDs"""

__docformat__ = 'restructuredtext'

from .qfallback import *
from .qpixmapwidget import *
from .qled import *
from .qlogo import *
from .qsevensegment import *
from .tauruslabel import *
from .taurusled import *
from .tauruslcd import *

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

"""
Old module supporting resources (now it just contains a reimplementation
based on taurus.qt.qtgui.icon for bck-compat)
"""

from __future__ import absolute_import

from taurus.core.util.log import deprecated as __deprecated

__deprecated(dep='taurus.qt.qtgui.resource',
           alt='taurus.qt.qtgui.icon',
           rel='4.0')

from .taurus_resource_utils import *

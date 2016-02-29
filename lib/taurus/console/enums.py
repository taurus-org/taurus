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

""" """

__all__ = ["Alignment"]

__docformat__ = "restructuredtext"

from taurus.core.util.enumeration import Enumeration

#: Flaggable alignment for both horizontal and vertical text
#: Conflicting combinations of flags have undefined meanings.
Alignment = Enumeration("Alignment", (
    ("Left",    0x0001),
    ("Right",   0x0002),
    ("HCenter", 0x0004),
    ("Top",     0x0020),
    ("Bottom",  0x0040),
    ("VCenter", 0x0080),
    ("Center",  0x0004 | 0x0080)))

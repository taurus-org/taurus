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
.. currentmodule:: taurus.core.simulation

Simulation extension for taurus core mode.
The simulation extension is a special extension that provides simulation
objects. The official scheme name is 'simulation'.

The main usage for this extension is to provide a useful value when using the
Qt designer to design the GUI.
The widgets have in their constructor a 'designMode' parameter that inside
the designer is set to True by the different plugins that export the different
taurus widgets to the designer. This way the developer can have a better idea
of what the GUI will look like in the end without connecting to the actual device
in design time (which could be dangerous at times) even if the values don't make 
much sence.
"""
from simfactory import *
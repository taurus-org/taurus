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
This module provides the taurus Command Line Interface

It is based on the click module to provide CLI utilities.

It defines a `taurus` command which can accept subcommands defined in
other taurus submodules or even in 3rd party plugins.

To define a subcommand for taurus, you need to register it in the
`taurus.cli.subcommands` entry point group via setuptools.

.. todo:: add click link , add code snippet for plugins, etc.

This module provides also common options/flags for command-line interfaces
that can be used by taurus plugins. For list of available options,
see :mod:`taurus.cli.common`

.. seealso:: :mod:`taurus.cli.alt`

"""

from .cli import main, register_subcommands, taurus_cmd

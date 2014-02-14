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

"""This package contains a collection of taurus console widgets"""

__all__ = ["TaurusConsoleWidget"]

__docformat__ = 'restructuredtext'

from IPython.utils.traitlets import Unicode
try:
    from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
except ImportError:
    from IPython.frontend.qt.console.rich_ipython_widget \
         import RichIPythonWidget

default_gui_banner = """\
Taurus console -- An enhanced IPython console for taurus.

?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.
%guiref   -> A brief reference about the graphical user interface.
"""


class TaurusConsoleWidget(RichIPythonWidget):

    banner = Unicode(config=True)

    #------ Trait default initializers ---------------------------------------
    def _banner_default(self):
        banner = default_gui_banner
        if 'TerminalInteractiveShell' in self.config:
            shell = self.config.TerminalInteractiveShell
            if 'banner' in shell:
                banner = shell.banner
            elif 'banner1' in shell and 'banner2' in shell:
                banner = "\n".join((shell.banner1, shell.banner2))
        return banner

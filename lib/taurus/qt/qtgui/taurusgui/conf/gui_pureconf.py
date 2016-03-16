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
###########################################################################

'''An example of usage of TaurusGui in which the current file is a pure
declarative configuration file that should be interpreted by the tarusgui
script by running `taurusgui gui_pureconf` (if gui_pureconf.py is in the
PYTHONPATH) or `taurusgui <full_path_to_gui_pureconf.py>` (if it is not
in the PYTHONPATH)'''


from taurus.qt.qtgui.taurusgui.utils import PanelDescription

GUI_NAME = 'MyGui'
panel = PanelDescription('Foo', classname='taurus.external.qt.Qt.QWidget')

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

"""A Qt MainWindow for the TaurusConsole

This is a tabbed pseudo-terminal of IPython sessions, with a menu bar for
common actions.
"""

__all__ = ["TaurusConsole"]

__docformat__ = 'restructuredtext'

###############################################################################
# required to avoid qtcoconsole importing PyQt5 by default
from taurus.external.qt import Qt
###############################################################################

from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager


class TaurusConsole(RichJupyterWidget):
    """
    TaurusConsole is a widget providing a self-contained Jupyter (IPython)
    console. "Self-contained" here means that it provides a
    :class:`qtconsole.rich_jupyter_widget.RichJupyterWidget` which by default
    also takes care of running its own in-process IPython kernel Manager and
    start the  kernel client threads, so that the console is initialized and
    ready to accept commands. See the parameter `start_on_init` of the
    constructor.

    """

    def __init__(self, *args, **kw):
        """
        :param start_on_init: (bool) If True (default), the kernel manager will
                              be initialized and the kernel threads will be
                              started

        .. note:: `TaurusConsole.__init__` also accepts all args and kwargs
                  of :class:`qtconsole.rich_jupyter_widget.RichJupyterWidget`

        """
        self.kernel_manager = None
        start_on_init = kw.pop('start_on_init', True)
        RichJupyterWidget.__init__(self, *args, **kw)
        if start_on_init:
            self.startKernelClient()

    @staticmethod
    def getKernelManager():
        """
        Returns a QtInProcessKernelManager, already initialized.

        :return: `qtconsole.inprocess.QtInProcessKernelManager`
        """
        kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel(show_banner=False)
        kernel_manager.kernel.gui = 'qt4'
        return kernel_manager

    def startKernelClient(self):
        """Initializes a client from the existing kernel manager (it initializes
         the manager if it did not exist) and starts the communication channels
        """
        if self.kernel_manager is None:
            self.kernel_manager = self.getKernelManager()
        self.kernel_client = self.kernel_manager.client()
        self.kernel_client.start_channels()


def main():

    import taurus.qt.qtgui.application
    app = taurus.qt.qtgui.application.TaurusApplication()
    w = TaurusConsole()
    w.show()
    app.exec_()

if __name__ == '__main__':
    main()

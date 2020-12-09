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

"""This module provides a base widget that can be used to display a taurus
model in a table widget"""

# todo: tango-centric!!!

from __future__ import absolute_import

from taurus.external.qt import Qt
from taurus.core.taurusbasetypes import TaurusElementType
from taurus.qt.qtcore.model import *
from taurus.core.taurusauthority import TaurusAuthority
from taurus.qt.qtgui.icon import getElementTypeIcon, getElementTypeIconName
from .taurustable import TaurusBaseTableWidget


__all__ = ["TaurusDbTableWidget"]

__docformat__ = 'restructuredtext'


class TaurusDbTableWidget(TaurusBaseTableWidget):
    """A class:`taurus.qt.qtgui.tree.TaurusBaseTableWidget` that connects to a
    :class:`taurus.core.taurusauthority.TaurusAuthority` model. It can show
    the list of database elements in two different perspectives:

    - device : a device list based perspective
    - server : a server list based perspective

    Filters can be inserted into this widget to restrict the items that are
    seen.
    """

    KnownPerspectives = {
        TaurusElementType.Device: {
            "label": "Devices",
            "icon": getElementTypeIconName(TaurusElementType.Device),
            "tooltip": "View by device",
            "model": [TaurusDbDeviceProxyModel, TaurusDbBaseModel, ],
        },
        TaurusElementType.Server: {
            "label": "Servers",
            "icon": getElementTypeIconName(TaurusElementType.Server),
            "tooltip": "View by server",
            "model": [TaurusDbServerProxyModel, TaurusDbPlainServerModel, ],
        },
    }

    DftPerspective = TaurusElementType.Device

    def getModelClass(self):
        return TaurusAuthority

    def sizeHint(self):
        return Qt.QSize(1024, 512)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseTableWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.table'
        ret['group'] = 'Taurus Views'
        ret['icon'] = "designer:table.png"
        return ret


def main_TaurusDbTableWidget(host, perspective=TaurusElementType.Device):
    w = TaurusDbTableWidget(perspective=perspective)
    w.setWindowIcon(getElementTypeIcon(perspective))
    w.setWindowTitle("A Taurus Table Example")
    w.setModel(host)
    w.show()
    return w


def demo():
    """Table panels"""
    import taurus
    db = taurus.Authority()
    host = db.getNormalName()
    w = main_TaurusDbTableWidget(host, TaurusElementType.Device)

    return w


def main():
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication

    app = Application.instance()
    owns_app = app is None

    if owns_app:
        app = Application(app_name="DB model demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")
    w = demo()
    w.show()

    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == "__main__":
    main()

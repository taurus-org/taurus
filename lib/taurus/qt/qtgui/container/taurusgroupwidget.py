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

"""This module provides a taurus group widget"""

from __future__ import absolute_import

from taurus.external.qt import Qt
from .qcontainer import QGroupWidget
from .taurusbasecontainer import TaurusBaseContainer


__all__ = ["TaurusGroupWidget"]

__docformat__ = 'restructuredtext'


class TaurusGroupWidget(QGroupWidget, TaurusBaseContainer):
    """This is a :class:`taurus.qt.qtgui.container.QGroupWidget` that additionally
    accepts a model property.
    This type of taurus container classes are specially useful if you define
    a parent taurus model to them and set all contained taurus widgets to use parent
    model. Example::

        from taurus.qt.qtgui.container import *
        from taurus.qt.qtgui.display import *

        widget = QGroupWidget(title="Example")
        layout = Qt.QVBoxLayout()
        widget.setLayout(layout)
        widget.model = 'sys/database/2'
        stateWidget = TaurusLabel()
        layout.addWidget(stateWidget)
        stateWidget.model = 'sys/database/2/state'
        """

    modelChanged = Qt.pyqtSignal('const QString &')

    def __init__(self, parent=None, designMode=False):
        name = self.__class__.__name__
        self.call__init__(QGroupWidget, parent=parent, designMode=designMode)
        self.call__init__(TaurusBaseContainer, name, designMode=designMode)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Public slots for apply/restore changes
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @Qt.pyqtSlot()
    def applyPendingChanges(self):
        self.applyPendingOperations()

    @Qt.pyqtSlot()
    def resetPendingChanges(self):
        self.resetPendingOperations()

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseContainer.getQtDesignerPluginInfo()
        if cls is TaurusGroupWidget:
            ret['module'] = 'taurus.qt.qtgui.container'
            ret['group'] = 'Taurus Containers'
            ret['icon'] = "designer:groupwidget.png"
            ret['container'] = True
        return ret

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    model = Qt.pyqtProperty("QString", TaurusBaseContainer.getModel,
                            TaurusBaseContainer.setModel,
                            TaurusBaseContainer.resetModel)

    useParentModel = Qt.pyqtProperty("bool", TaurusBaseContainer.getUseParentModel,
                                     TaurusBaseContainer.setUseParentModel,
                                     TaurusBaseContainer.resetUseParentModel)

    showQuality = Qt.pyqtProperty("bool", TaurusBaseContainer.getShowQuality,
                                  TaurusBaseContainer.setShowQuality,
                                  TaurusBaseContainer.resetShowQuality)


def demo():
    """Group widget"""

    import taurus.qt.qtgui.display
    w = Qt.QWidget()
    w.setWindowTitle(Qt.QApplication.instance().applicationName())
    layout = Qt.QGridLayout()
    w.setLayout(layout)

    groupwidget = TaurusGroupWidget()
    groupwidget.model = "sys/tg_test/1"
    groupwidget.titleIcon = Qt.QIcon.fromTheme("video-x-generic")

    layout.addWidget(groupwidget, 0, 0)
    layout1 = Qt.QFormLayout()
    content = groupwidget.content()
    content.setLayout(layout1)

    state_led = taurus.qt.qtgui.display.TaurusLed()
    state_led.model = groupwidget.model + "/state"
    status_label = taurus.qt.qtgui.display.TaurusLabel()
    status_label.model = groupwidget.model + "/status"
    double_scalar_label = taurus.qt.qtgui.display.TaurusLabel()
    double_scalar_label.model = groupwidget.model + "/double_scalar"
    layout1.addRow("State:", state_led)
    layout1.addRow("Status:", status_label)
    layout1.addRow("Double scalar:", double_scalar_label)

    groupwidget = TaurusGroupWidget()
    groupwidget.model = "sys/tg_test/1"
    groupwidget.setTitleStyle({
        'start_color': 'rgb(255, 60, 60)',
        'stop_color': 'rgb(200, 0, 0)',
        'font_color': 'rgb(140, 0, 0)',
        'border_radius': '10px',
    })
    groupwidget.setContentStyle({
        'border_radius': '0px',
    })
    layout.addWidget(groupwidget, 1, 0)
    layout1 = Qt.QFormLayout()
    content = groupwidget.content()
    content.setLayout(layout1)
    import taurus.qt.qtgui.display
    long_scalar_label = taurus.qt.qtgui.display.TaurusLabel()
    long_scalar_label.model = groupwidget.model + "/long_scalar"
    boolean_scalar_led = taurus.qt.qtgui.display.TaurusLed()
    boolean_scalar_led.model = groupwidget.model + "/boolean_scalar"
    layout1.addRow("Long scalar:", long_scalar_label)
    layout1.addRow("Boolean scalar:", boolean_scalar_led)

    groupwidget = TaurusGroupWidget()
    groupwidget.model = "sys/tg_test/1"
    groupwidget.titleVisible = False
    layout.addWidget(groupwidget, 2, 0)
    layout1 = Qt.QFormLayout()
    content = groupwidget.content()
    content.setLayout(layout1)
    short_scalar_label = taurus.qt.qtgui.display.TaurusLabel()
    short_scalar_label.model = groupwidget.model + "/short_scalar"
    layout1.addRow("short scalar:", short_scalar_label)

    layout.addWidget(Qt.QWidget(), 3, 0)
    layout.setRowStretch(3, 1)
    w.show()
    return w


def main():
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication

    app = Application.instance()
    owns_app = app is None

    if owns_app:
        import taurus.core.util.argparse
        parser = taurus.core.util.argparse.get_taurus_parser()
        parser.usage = "%prog [options] <full_device_name(s)>"
        app = Application(sys.argv, cmd_line_parser=parser,
                          app_name="Taurus frame demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")

    args = app.get_command_line_args()

    if len(args) == 0:
        w = demo()
    else:
        models = map(str.lower, args)

        w = Qt.QWidget()
        w.setWindowTitle(app.applicationName())
        layout = Qt.QGridLayout()
        w.setLayout(layout)
        for model in models:
            groupwidget = TaurusGroupWidget()
            groupwidget.model = model
            layout.addWidget(groupwidget)
    w.show()

    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == '__main__':
    main()

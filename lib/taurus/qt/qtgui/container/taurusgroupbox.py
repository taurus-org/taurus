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

"""This module provides basic taurus group box widget"""

from __future__ import absolute_import

from taurus.external.qt import Qt
from .taurusbasecontainer import TaurusBaseContainer

__all__ = ["TaurusGroupBox"]

__docformat__ = 'restructuredtext'


class TaurusGroupBox(Qt.QGroupBox, TaurusBaseContainer):
    """This is a Qt.QGroupBox that additionally accepts a model property.
    This type of taurus container classes are specially useful if you define
    a parent taurus model to them and set all contained taurus widgets to use parent
    model. Example::

        from taurus.qt.qtgui.container import *
        from taurus.qt.qtgui.display import *

        widget = TaurusGroupBox("Example")
        layout = Qt.QVBoxLayout()
        widget.setLayout(layout)
        widget.model = 'sys/database/2'
        stateWidget = TaurusLabel()
        layout.addWidget(stateWidget)
        stateWidget.model = 'sys/database/2/state'
        """
    modelChanged = Qt.pyqtSignal('const QString &')
    pendingOperationsChanged = Qt.pyqtSignal(bool)

    def __init__(self, parent=None, designMode=False):
        name = self.__class__.__name__
        self._prefix = ''
        self._suffix = ''

        self.call__init__wo_kw(Qt.QGroupBox, parent)
        self.call__init__(TaurusBaseContainer, name, designMode=designMode)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Public slots for apply/restore changes
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    @Qt.pyqtSlot(bool)
    def pendingOperationsChanged(self, yesno):
        self.debug("emiting pendingOperationsChanged(%s)" % str(yesno))
        self.pendingOperationsChanged.emit(yesno)

    @Qt.pyqtSlot()
    def applyPendingChanges(self):
        self.applyPendingOperations()

    @Qt.pyqtSlot()
    def resetPendingChanges(self):
        self.resetPendingOperations()

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # TaurusBaseWidget over writing
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getDisplayValue(self):
        v = TaurusBaseContainer.getDisplayValue(self)
        return "%s%s%s" % ((self._prefix or ''), v, (self._suffix or ''))

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # QT properties
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def getPrefixText(self):
        return self._prefix

    @Qt.pyqtSlot('QString')
    def setPrefixText(self, prefix):
        self._prefix = prefix
        import taurus.core
        self.fireEvent(
            evt_type=taurus.core.taurusbasetypes.TaurusEventType.Change)

    def getSuffixText(self):
        return self._suffix

    @Qt.pyqtSlot('QString')
    def setSuffixText(self, suffix):
        self._suffix = suffix
        import taurus.core
        self.fireEvent(
            evt_type=taurus.core.taurusbasetypes.TaurusEventType.Change)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusBaseContainer.getQtDesignerPluginInfo()
        if cls is TaurusGroupBox:
            ret['module'] = 'taurus.qt.qtgui.container'
            ret['group'] = 'Taurus Containers'
            ret['icon'] = "designer:groupbox.png"
            ret['container'] = True
        return ret

    model = Qt.pyqtProperty("QString", TaurusBaseContainer.getModel,
                            TaurusBaseContainer.setModel,
                            TaurusBaseContainer.resetModel)

    useParentModel = Qt.pyqtProperty("bool",
                                     TaurusBaseContainer.getUseParentModel,
                                     TaurusBaseContainer.setUseParentModel,
                                     TaurusBaseContainer.resetUseParentModel)

    showQuality = Qt.pyqtProperty("bool", TaurusBaseContainer.getShowQuality,
                                  TaurusBaseContainer.setShowQuality,
                                  TaurusBaseContainer.resetShowQuality)

    showText = Qt.pyqtProperty("bool", TaurusBaseContainer.getShowText,
                               TaurusBaseContainer.setShowText,
                               TaurusBaseContainer.resetShowText)

    prefixText = Qt.pyqtProperty("QString", getPrefixText, setPrefixText,
                                 doc="prefix text (optional)")

    suffixText = Qt.pyqtProperty("QString", getSuffixText, setSuffixText,
                                 doc="suffix text (optional)")


def demo():
    "Group box"
    w = Qt.QWidget()
    w.setWindowTitle(Qt.QApplication.instance().applicationName())
    layout = Qt.QGridLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    w.setLayout(layout)
    groupbox = TaurusGroupBox()
    groupbox.model = "sys/tg_test/1"
    layout.addWidget(groupbox)
    layout = Qt.QFormLayout()
    groupbox.setLayout(layout)
    import taurus.qt.qtgui.display
    state_led = taurus.qt.qtgui.display.TaurusLed()
    state_led.model = groupbox.model + "/state"
    status_label = taurus.qt.qtgui.display.TaurusLabel()
    status_label.model = groupbox.model + "/status"
    double_scalar_label = taurus.qt.qtgui.display.TaurusLabel()
    double_scalar_label.model = groupbox.model + "/double_scalar"
    layout.addRow("State:", state_led)
    layout.addRow("Status:", status_label)
    layout.addRow("Double scalar:", double_scalar_label)
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
            groupbox = TaurusGroupBox()
            groupbox.model = model
            layout.addWidget(groupbox)
    w.show()

    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == '__main__':
    main()

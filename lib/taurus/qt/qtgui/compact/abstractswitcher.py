#!/usr/bin/env python

#############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2013 CELLS / ALBA Synchrotron, Bellaterra, Spain
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
This module provides base classes from which the compact widgets should inherit
"""

__all__ = ["TaurusReadWriteSwitcher"]

__docformat__ = 'restructuredtext'

from future.utils import string_types

from taurus.external.qt import Qt
from taurus.qt.qtgui.container import TaurusWidget
# from taurus.qt.qtgui.base import TaurusBaseWritableWidget


class TaurusReadWriteSwitcher(TaurusWidget):
    '''
    This is a base class for creating widgets that can switch
    beetween read and write mode by combining a Taurus widget for reading
    and a Taurus Widget for writing.

    For example, if you want to combine a TaurusLabel with a
    TaurusValueLineEdit, you can implement it as follows::

        class MyRWSwitcher(TaurusReadWriteSwitcher):
            readWClass = TaurusLabel
            writeWClass = TaurusValueLineEdit

    Alternatively, you can instantiate the TaurusReadWriteSwitcher class
    directly and pass the read and write classes to the constructor::

        w = TaurusReadWriteSwitcher(readWClass=TaurusLabel,
                                    writeWClass=TaurusValueLineEdit)

    Or you can even set the read and write widgets (instead of classes)
    after instantiation::

        w = TaurusReadWriteSwitcher()
        a = TaurusLabel()
        b = TaurusValueLineEdit()
        w.setReadWidget(a)
        w.setWriteWidget(b)

    TaurusReadWriteSwitcher will normally show the read widget by default,
    but it will allow to switch to "edit mode" (where the write widget
    is shown instead). Enetering and exiting the edit mode is controlled
    by "triggers". Triggers can be key presses, QEvents or signals.

    The default implementation sets pressing F2 or doubleclicking the read
    widget as the triggers for entering edit mode, and pressing Escape,
    losing the focus or applying the value on the write widget as the
    triggers for leaving the edit mode. This can be customized by changing
    `enterEditTriggers` and `exitEditTriggers` class members or by passing
    `enterEditTriggers` and `exitEditTriggers` keyword parameters to the
    constructor of TaurusReadWriteSwitcher:

        - `enterEditTriggers` is a tuple containing one or more of the following:

            - key shortcut (either a Qt.Qt.Key or a QKeySequence)
            - event type on the read widget (a Qt.QEvent.Type)
            - signal from the read widget (a str representing a Signal signature)

        - `exitEditTriggers` is a tuple containing one or more of the following:

            - key shortcut (either a Qt.Qt.Key or a QKeySequence)
            - event type on the write widget (a Qt.QEvent.Type)
            - signal from the write widget (a str representing a Signal signature)

    #@todo: check integration with designer

    '''
    readWClass = None
    writeWClass = None

    enterEditTriggers = (Qt.Qt.Key_F2, Qt.QEvent.MouseButtonDblClick)
    exitEditTriggers = (Qt.Qt.Key_Escape, Qt.QEvent.FocusOut, 'applied')

    def __init__(self, parent=None, designMode=False,
                 readWClass=None, writeWClass=None,
                 enterEditTriggers=None, exitEditTriggers=None):

        TaurusWidget.__init__(self, parent=parent, designMode=designMode)

        self.setFocusPolicy(Qt.Qt.StrongFocus)
        self.setLayout(Qt.QStackedLayout())
        self.readWidget = None
        self.writeWidget = None

        # Use parameters from constructor args or defaults from class
        self.readWClass = readWClass or self.readWClass
        self.writeWClass = writeWClass or self.writeWClass
        self.enterEditTriggers = enterEditTriggers or self.enterEditTriggers
        self.exitEditTriggers = exitEditTriggers or self.exitEditTriggers

        # classify the triggers
        sc, et, sig = self._classifyTriggers(self.enterEditTriggers)
        self.enterEditShortCuts = sc
        self.enterEditEventTypes = et
        self.enterEditSignals = sig
        sc, et, sig = self._classifyTriggers(self.exitEditTriggers)
        self.exitEditShortCuts = sc
        self.exitEditEventTypes = et
        self.exitEditSignals = sig

        # Actions for entering and exiting the edit
        self.enterEditAction = Qt.QAction("Start Editing", self)
        self.enterEditAction.setShortcuts(self.enterEditShortCuts)
        self.enterEditAction.setShortcutContext(
            Qt.Qt.WidgetWithChildrenShortcut)
        self.addAction(self.enterEditAction)
        self.exitEditAction = Qt.QAction("Abort Editing", self)
        self.exitEditAction.setShortcuts(self.exitEditShortCuts)
        self.exitEditAction.setShortcutContext(
            Qt.Qt.WidgetWithChildrenShortcut)
        self.addAction(self.exitEditAction)
        self.enterEditAction.triggered.connect(self._onEnterEditActionTriggered)
        self.exitEditAction.triggered.connect(self._onExitEditActionTriggered)

        # add read and write widgets
        if self.readWClass is not None:
            self.setReadWidget(self.readWClass())
        if self.writeWClass is not None:
            self.setWriteWidget(self.writeWClass())

    def _classifyTriggers(self, triggers):
        '''classifies the diferent types of triggers

        :return: (tuple) a tuple of 3 lists: shortcuts,enventypes,signals
        '''
        shortcuts = []
        eventTypes = []
        signals = []
        for e in triggers:
            if isinstance(e, (Qt.Qt.Key, Qt.QKeySequence)):
                shortcuts.append(Qt.QKeySequence(e))
            elif isinstance(e, Qt.QEvent.Type):
                eventTypes.append(e)
            elif isinstance(e, string_types):
                signals.append(e)
            else:
                raise TypeError('Unsupported trigger type: %s' % repr(type(e)))
        return shortcuts, eventTypes, signals

    def eventFilter(self, obj, event):
        '''reimplemented to intercept events from the read and write widgets'''
        if obj is self.readWidget and event.type() in self.enterEditEventTypes:
            self.enterEdit()
            return True  # Note that we do not let it propagate further!
        if obj is self.writeWidget and event.type() in self.exitEditEventTypes:
            self.exitEdit()
            return True  # Note that we do not let it propagate further!
        # default fallback
        return obj.eventFilter(obj, event)

    def setReadWidget(self, widget):
        '''set the read Widget to be used. You can reimplement this
        method to tweak the read widget.

        :param widget: (QWidget) This should be Taurus widget
        '''
        if self.readWidget is not None:
            # @todo: relax this limitation
            raise RuntimeError('ReadWidget already set')
        self.readWidget = widget
        self.layout().insertWidget(0, self.readWidget)
        self.readWidget.setCursor(Qt.Qt.IBeamCursor)
        self.readWidget.setModel(self.getModelName())
        # setup EnterEdit triggers
        if self.enterEditEventTypes:
            self.readWidget.installEventFilter(self)
        for sig in self.enterEditSignals:
            try:
                getattr(self.readWidget, sig).connect(self.enterEdit)
            except Exception as e:
                self.debug('Cannot connect signal. Reason: %s', e)
        # update size policy
        self._updateSizePolicy()
        # register configuration (we use the class name to avoid mixing configs
        # in the future)
        self.registerConfigDelegate(
            self.readWidget, name='_R_' + self.readWidget.__class__.__name__)

    def setWriteWidget(self, widget):
        '''set the write Widget to be used You can reimplement this
        method to tweak the write widget.

        :param widget: (Qt.QWidget) This should be Taurus widget
                       (typically a TaurusBaseWritableWidget)
        '''
        if self.writeWidget is not None:
            # @todo: relax this limitation
            raise RuntimeError('WriteWidget already set')
        self.writeWidget = widget
        self.layout().insertWidget(1, self.writeWidget)
        self.writeWidget.setModel(self.getModelName())
        if self.exitEditEventTypes:
            self.writeWidget.installEventFilter(self)
        for sig in self.exitEditSignals:
            try:
                getattr(self.writeWidget, sig).connect(self.exitEdit)
            except Exception as e:
                if isinstance(e, AttributeError) and hasattr(Qt, "SIGNAL"):
                    # Support old-style signal
                    self.connect(self.writeWidget, Qt.SIGNAL(sig),
                                 self.exitEdit)
                    self.debug('Cannot connect %s using new style signal.' +
                               'Falling back to old style', sig)
                else:
                    self.debug('Cannot connect signal. Reason: %s', e)

        # update size policy
        self._updateSizePolicy()
        # register configuration (we use the class name to avoid mixing configs
        # in the future)
        self.registerConfigDelegate(
            self.readWidget, name='_W_' + self.writeWidget.__class__.__name__)

    def enterEdit(self, *args, **kwargs):
        '''Slot for entering Edit mode

        .. note:: args and kwargs are ignored
        '''
        self.enterEditAction.trigger()

    def exitEdit(self, *args, **kwargs):
        '''Slot for entering Edit mode

        .. note:: args and kwargs are ignored
        '''
        self.exitEditAction.trigger()

    def _onEnterEditActionTriggered(self):
        self.layout().setCurrentIndex(1)

    def _onExitEditActionTriggered(self):
        self.layout().setCurrentIndex(0)

    def _updateSizePolicy(self):
        '''Update the size policy of the switcher widget to the most restrictive
        combination of the policies of the read and write widgets'''
        policy = None
        for w in self.readWidget, self.writeWidget:
            if w is not None:
                p = w.sizePolicy()
                if policy is None:
                    policy = p
                else:
                    h = policy.horizontalPolicy() & p.horizontalPolicy()
                    v = policy.verticalPolicy() & p.verticalPolicy()
                    policy = Qt.QSizePolicy(Qt.QSizePolicy.Policy(h),
                                            Qt.QSizePolicy.Policy(v))
        if policy is not None:
            self.setSizePolicy(policy)

    def setModel(self, model):
        '''This implementation propagates the model to the read and write widgets.
        You may reimplement it to do things like passing different models to each.
        '''
        if self.readWidget is not None:
            self.readWidget.setModel(model)
        if self.writeWidget is not None:
            self.writeWidget.setModel(model)
        TaurusWidget.setModel(self, model)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusWidget.getQtDesignerPluginInfo()
        ret['module'] = 'taurus.qt.qtgui.compact'
        ret['group'] = 'Taurus R+W'
        ret['icon'] = "designer:frame.png"
        if (cls.readWClass or cls.readWClass) is None:
            ret['container'] = True  # for base classes
        else:
            # for classes which already define the subwidgets
            ret['container'] = False
        return ret

    model = Qt.pyqtProperty("QString", TaurusWidget.getModel,
                            setModel,
                            TaurusWidget.resetModel)

######################################
# This block (and something more would be needed if we decide
# to implement TaurusReadWriteSwitcher as a TaurusBaseWritableWidget
######################################
#
#    def setDangerMessage(self, dangerMessage=None):
#        '''propagate to writeWidget'''
#        TaurusWidget.setDangerMessage(self, dangerMessage)
#        try:
#            return self.writeWidget.setDangerMessage(dangerMessage)
#        except AttributeError:
#            pass
#
#    def setForceDangerousOperations(self, yesno):
#        '''propagate to writeWidget'''
#        TaurusWidget.setForceDangerousOperations(self, yesno)
#        try:
#            return self.writeWidget.setForceDangerousOperations(yesno)
#        except AttributeError:
#            pass
#
#
#######################################


def demo1():
    '''Simple demo'''
    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.display import TaurusLabel
    from taurus.qt.qtgui.input import TaurusValueLineEdit

    app = TaurusApplication(cmd_line_parser=None)

    w = TaurusReadWriteSwitcher(readWClass=TaurusLabel,
                                writeWClass=TaurusValueLineEdit)
    w.model = "sys/tg_test/1/long_scalar"

    w.show()
    sys.exit(app.exec_())


def demo2():
    '''demo of integrability in a form'''
    import sys
    from taurus.qt.qtgui.panel import TaurusForm
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.display import TaurusLabel
    from taurus.qt.qtgui.input import TaurusValueLineEdit

    class DemoSwitcher(TaurusReadWriteSwitcher):
        readWClass = TaurusLabel
        writeWClass = TaurusValueLineEdit
        exitEditTriggers = ('editingFinished()', Qt.Qt.Key_Escape)

    app = TaurusApplication(cmd_line_parser=None)

    f = TaurusForm()
    f.model = ['sys/tg_test/1/long_scalar', 'sys/tg_test/1/long_scalar']

    f[0].setReadWidgetClass(DemoSwitcher)
    f[0].setWriteWidgetClass(None)

    f.show()
    sys.exit(app.exec_())


def demo3():
    '''simple demo including more than one widget'''

    import sys
    from taurus.qt.qtgui.application import TaurusApplication
    from taurus.qt.qtgui.display import TaurusLabel, TaurusLed
    from taurus.qt.qtgui.input import TaurusValueLineEdit, TaurusValueCheckBox

    app = TaurusApplication(cmd_line_parser=None)

    w1 = TaurusReadWriteSwitcher(readWClass=TaurusLabel,
                                 writeWClass=TaurusValueLineEdit)
    w1.model = "sys/tg_test/1/long_scalar"

    w2 = TaurusReadWriteSwitcher(readWClass=TaurusLed,
                                 writeWClass=TaurusValueCheckBox)
    w2.model = "sys/tg_test/1/boolean_scalar"

    f = Qt.QWidget()
    f.setLayout(Qt.QVBoxLayout())
    f.layout().addWidget(w1)
    f.layout().addWidget(w2)
    f.layout().addWidget(TaurusReadWriteSwitcher())  # add non-initialized switcher
    f.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    # demo1()
    # demo2()
    demo3()

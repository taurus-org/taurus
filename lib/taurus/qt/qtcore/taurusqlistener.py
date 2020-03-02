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

""""""

from __future__ import print_function

__all__ = ["QTaurusBaseListener", "QObjectTaurusListener"]

__docformat__ = 'restructuredtext'

from taurus.qt.qtcore.util import baseSignal
from taurus.core.util.log import deprecation_decorator
from taurus.core.tauruslistener import TaurusListener
from taurus.external.qt import Qt


class QTaurusBaseListener(TaurusListener):
    """Base class for QObjects listening to taurus events.

    .. note::
           :meth:`getSignaller` is now unused and deprecated. This is because
           `taurusEvent` is implemented using :func:`baseSignal`, that doesn't
           require the class to inherit from QObject.
    """

    taurusEvent = baseSignal('taurusEvent', object, object, object)

    def __init__(self, name=None, parent=None):
        if name is None:
            name = self.__class__.__name__
        super(QTaurusBaseListener, self).__init__(name, parent=parent)
        self._eventFilters = []
        self.taurusEvent.connect(self.filterEvent)

    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
    # Event handling chain
    #-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    def eventReceived(self, evt_src, evt_type, evt_value):
        """The basic implementation of the event handling chain is as
        follows:

            - eventReceived just calls :meth:`fireEvent` which emits a "taurusEvent"
              PyQt signal that is connected (by :meth:`preAttach`) to the
              :meth:`filterEvent` method.
            - After filtering, :meth:`handleEvent` is invoked with the resulting
              filtered event

        .. note::
            in the earlier steps of the chain (i.e., in :meth:`eventReceived`/:meth:`fireEvent`),
            the code is executed in a Python thread, while from eventFilter
            ahead, the code is executed in a Qt thread.
            When writing widgets, one should normally work on the Qt thread
            (i.e. reimplementing :meth:`handleEvent`)

        :param evt_src: (object) object that triggered the event
        :param evt_type: (taurus.core.taurusbasetypes.TaurusEventType) type of event
        :param evt_value: (object) event value
        """
        self.fireEvent(evt_src, evt_type, evt_value)

    def fireEvent(self, evt_src=None, evt_type=None, evt_value=None):
        """Emits a "taurusEvent" signal.
        It is unlikely that you may need to reimplement this method in subclasses.
        Consider reimplementing :meth:`eventReceived` or :meth:`handleEvent`
        instead depending on whether you need to execute code in the python
        or Qt threads, respectively

        :param evt_src: (object or None) object that triggered the event
        :param evt_type: (taurus.core.taurusbasetypes.TaurusEventType or None) type of event
        :param evt_value: (object or None) event value
        """
        try:
            self.taurusEvent.emit(evt_src, evt_type, evt_value)
        except:
            pass

    def filterEvent(self, evt_src=-1, evt_type=-1, evt_value=-1):
        """The event is processed by each and all filters in strict order
        unless one of them returns None (in which case the event is discarded)

        :param evt_src: (object) object that triggered the event
        :param evt_type: (taurus.core.taurusbasetypes.TaurusEventType) type of event
        :param evt_value: (object) event value
        """
        r = evt_src, evt_type, evt_value

        if r == (-1, -1, -1):
            # @todo In an ideal world the signature of this method should be
            # (evt_src, evt_type, evt_value). However there's a bug in PyQt:
            # If a signal is disconnected between the moment it is emitted and
            # the moment the slot is called, then the slot is called without
            # parameters (!?). We added this default values to detect if
            # this is the case without printing an error message each time.
            # If this gets fixed, we should remove this line.
            return

        for f in self._eventFilters:
            r = f(*r)
            if r is None:
                return
        self.handleEvent(*r)

    def handleEvent(self, evt_src, evt_type, evt_value):
        """Event handling. Default implementation does nothing.
        Reimplement as necessary

        :param evt_src: (object or None) object that triggered the event
        :param evt_type: (taurus.core.taurusbasetypes.TaurusEventType or None) type of event
        :param evt_value: (object or None) event value
        """
        pass

    def setEventFilters(self, filters=None):
        """sets the taurus event filters list.
        The filters are run in order, using each output to feed the next filter.
        A filter must be a function that accepts 3 arguments ``(evt_src, evt_type, evt_value)``
        If the event is to be ignored, the filter must return None.
        If the event is  not to be ignored, filter must return a
        ``(evt_src, evt_type, evt_value)`` tuple which may (or not) differ from the input.

        For a library of common filters, see taurus/core/util/eventfilters.py

        :param filters: (sequence) a sequence of filters

        See also: insertEventFilter
        """
        if filters is None:
            filters = []
        self._eventFilters = list(filters)

    def getEventFilters(self):
        """Returns the list of event filters for this widget

        :return: (sequence<callable>) the event filters
        """
        return self._eventFilters

    def insertEventFilter(self, filter, index=-1):
        """insert a filter in a given position

        :param filter: (callable(evt_src, evt_type, evt_value)) a filter
        :param index: (int) index to place the filter (default = -1 meaning place at the end)

        See also: setEventFilters
        """
        self._eventFilters.insert(index, filter)

    @deprecation_decorator(rel='4.0')
    def getSignaller(self):
        return self


class QObjectTaurusListener(Qt.QObject, QTaurusBaseListener):

    def __init__(self, name=None, parent=None):
        self.call__init__wo_kw(Qt.QObject, parent)
        self.call__init__(QTaurusBaseListener, name=name)


class ListenerDemo(QObjectTaurusListener):

    def eventReceived(self, evt_src, evt_type, evt_value):
        self.info("New %s event from %s",
                  taurus.core.taurusbasetypes.TaurusEventType[evt_type], evt_src)
        return super(ListenerDemo, self).eventReceived(evt_src, evt_type, evt_value)

    def handleEvent(self, evt_src, evt_type, evt_value):
        self.info("New %s event from %s",
                  taurus.core.taurusbasetypes.TaurusEventType[evt_type], evt_src)


if __name__ == "__main__":
    import time
    import taurus
    qlistener = ListenerDemo(name="DemoObject")

    attr = taurus.Attribute("sys/tg_test/1/double_scalar")
    attr.addListener(qlistener)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Finished!")

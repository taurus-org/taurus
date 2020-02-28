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

"""
emitter.py: This module provides a task scheduler used by TaurusGrid and 
    TaurusDevTree widgets
"""

from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import object
from queue import Queue, Empty
import traceback

from future.utils import string_types

import taurus
from taurus.external.qt import Qt
from taurus.core.util.log import Logger


###############################################################################
# Helping methods


def isString(seq):
    if isinstance(seq, string_types):
        return True  # It matches most python str-like classes
    if any(s in str(type(seq)).lower() for s in ('vector', 'array', 'list',)):
        return False
    if 'qstring' == str(type(seq)).lower():
        return True  # It matches QString
    return False


def modelSetter(obj, model):
    """
    This class is used for convenience as TaurusEmitterThread standard method
    """
    # print 'In modelSetter(%s,%s)' % (str(obj),str(model))
    if hasattr(obj, 'setModel') and model is not None:
        obj.setModel(model)
    return


class MethodModel(object):
    """
    Class to emulate method execution as a setModel
    """

    def __init__(self, method):
        self.method = method

    def setModel(self, value):
        return self.method(value)


class QEmitter(Qt.QObject):
    """Emitter class providing two signals."""

    doSomething = Qt.pyqtSignal(list)
    somethingDone = Qt.pyqtSignal()
    newQueue = Qt.pyqtSignal()


###############################################################################


class TaurusEmitterThread(Qt.QThread):
    """
    This object get items from a python Queue and performs a thread safe 
    operation on them.
    It is useful to serialize Qt tasks in a background thread.

    :param parent: a Qt/Taurus object
    :param name: identifies object logs
    :param queue: if None parent.getQueue() is used, if not then the queue 
        passed as argument is used
    :param method: the method to be executed using each queue item as argument
    :param cursor: if True or QCursor a custom cursor is set while 
        the Queue is not empty

    How TaurusEmitterThread works:

    TaurusEmitterThread is a worker thread that processes a queue of iterables 
    passed as arguments to the specified method every time that  
    ``doSomething()`` is called:

     * ``self.method(*item)`` will be called if TaurusEmitterThread.method 
        has been initialized.
     * ``item[0](item[1:])`` will be called if ``method`` is not initialized 
        and the first element of the queued iterable is *callable*.

    TaurusEmitterThread uses two queues:

     * ``self.queue`` manages the objects added externally:

      + the ``next()`` method passes objects from ``self.queue`` 
        to ``self.todo queue``
      + every time that a *somethingDone* signal arrives ``next()`` is called.
      + ``next()`` can be called also externally to ensure that the main queue 
        is being processed.
      + the queue can be accessed externally using ``getQueue()``
      + ``getQueue().qsize()`` returns number of remaining objects in queue.
      + while there are objects in queue the ``.next()`` method will 
        override applications cursor. a call to ``next()`` with an empty queue 
        will restore the original cursor.

     * ``self.todo`` is managed by the ``run()/start()`` method:

      - a loop waits continuously for new objects in ``self.todo`` queue.
      - if an object is found, it is sent in a *doSomething* signal.
      - if *"exit"* is found the loop exits.

    Usage example:

    .. code-block:: python

        #Applying TaurusEmitterThread to an existing class:
        from queue import Queue
        from functools import partial

        def modelSetter(args):
            obj,model = args[0],args[1]
            obj.setModel(model)

        klass TaurusGrid(Qt.QFrame, TaurusBaseWidget):
            ...
            def __init__(self, parent = None, designMode = False):
                ...
                self.modelsQueue = Queue()
                self.modelsThread = TaurusEmitterThread(parent=self,
                        queue=self.modelsQueue,method=modelSetter )
                ...
            def build_widgets(...):
                ...
                            previous,synoptic_value = \
                                synoptic_value,TaurusValue(cell_frame)
                            #synoptic_value.setModel(model)
                            self.modelsQueue.put((synoptic_value,model))
                ...
            def setModel(self,model):
                ...
                if hasattr(self,'modelsThread') and \
                        not self.modelsThread.isRunning():
                    self.modelsThread.start()
                elif self.modelsQueue.qsize():
                    self.modelsThread.next()
                ...

    """

    def __init__(self, parent=None, name='', queue=None, method=None,
                 cursor=None, sleep=5000, polling=0, loopwait=5):
        """
        Parent must be not None and must be a TaurusGraphicsScene!

        :param queue: pass an external action queue (optional)
        :param method: action processor (e.g. modelSetter)
        :param cursor: QCursor during process (optional)
        :param sleep: delay in ms before thread start
        :param polling: process actions at fix period (milliseconds)
        :param loopwait: wait N milliseconds between actions
        """
        Qt.QThread.__init__(self, parent)
        self.name = name
        self.log = Logger('TaurusEmitterThread(%s)' % self.name)
        self.log.setLogLevel(self.log.Info)
        self.queue = queue or Queue()
        self.todo = Queue()
        self.method = method
        self.cursor = Qt.QCursor(
            Qt.Qt.WaitCursor) if cursor is True else cursor
        self._cursor = False
        self.timewait = int(sleep)
        self.polling = int(polling)
        self.loopwait = int(loopwait)
        if self.polling:
            self.refreshTimer = Qt.QTimer()
            self.refreshTimer.timeout.connect(self.onRefresh)
        else:
            self.refreshTimer = None

        self.emitter = QEmitter()
        self.emitter.moveToThread(Qt.QApplication.instance().thread())
        # Mandatory!!! if parent is set before changing thread it could lead to
        # segFaults!
        self.emitter.setParent(Qt.QApplication.instance())
        self._done = 0
        # Moved to the end to prevent segfaults ...
        self.emitter.doSomething.connect(self._doSomething)

        if not self.refreshTimer:
            self.emitter.somethingDone.connect(self.next)

    def onRefresh(self):
        try:
            size = self.getQueue().qsize()
            if size:
                self.log.info('onRefresh(%s)' % size)
                self.next()
            else:
                self.log.debug('onRefresh()')
        except:
            self.log.warning(traceback.format_exc())

    def getQueue(self):
        if self.queue:
            return self.queue
        elif hasattr(self.parent(), 'getQueue'):
            self.parent().getQueue()
        else:
            return None

    def getDone(self):
        """ Returns % of done tasks in 0-1 range """
        pending = self.getQueue().qsize()
        return float(self._done) / (self._done + pending)

    def clear(self):
        while not self.todo.empty():
            self.todo.get()
        while not self.getQueue().empty():
            self.getQueue().get()
            self._done += 1

    def purge(self, obj):
        """
        Remove a given object from all queues
        """
        nqueue = Queue()
        while not self.todo.empty():
            i = self.todo.get()
            if obj not in i:
                nqueue.put(i)
        while not self.queue.empty():
            i = self.queue.get()
            if obj not in i:
                nqueue.put(i)
        while not nqueue.empty():
            self.queue.put(nqueue.get())
        self.next()

    def _doSomething(self, params):
        self.log.debug('At TaurusEmitterThread._doSomething(%s)' % str(params))
        if not self.method:
            method, args = params[0], params[1:]
        else:
            method, args = self.method, params
        if method:
            try:
                method(*args)
            except:
                self.log.error('At TaurusEmitterThread._doSomething(%s): \n%s'
                               % (list(map(str, args)), traceback.format_exc()))
        self.emitter.somethingDone.emit()
        self._done += 1
        return

    def next(self):
        queue = self.getQueue()
        msg = ('At TaurusEmitterThread.next(), %d items remaining.'
               % queue.qsize())
        if (queue.empty() and not self.polling):
            self.log.info(msg)
        else:
            self.log.debug(msg)
        try:
            if not queue.empty():
                if not self._cursor and self.cursor is not None:
                    Qt.QApplication.instance().setOverrideCursor(
                        Qt.QCursor(self.cursor))
                    self._cursor = True
                # A blocking get here would hang the GUIs!!!
                item = queue.get(False)
                self.todo.put(item)
                self.log.debug('Item added to todo queue: %s' % str(item))
            elif self._cursor:
                Qt.QApplication.instance().restoreOverrideCursor()
                self._cursor = False

        except Empty:
            self.log.warning(traceback.format_exc())
            pass
        except:
            self.log.warning(traceback.format_exc())
        return

    def run(self):
        Qt.QApplication.instance().thread().msleep(self.timewait)
        self.log.info('#' * 80)
        self.log.info('At TaurusEmitterThread.run()')
        self.next()

        if self.refreshTimer:
            self.refreshTimer.start(self.polling)

        while True:
            self.log.debug('At TaurusEmitterThread.run() loop.')
            item = self.todo.get(True)
            if isString(item):
                if item == "exit":
                    break
                else:
                    continue
            self.log.debug('Emitting doSomething signal ...')
            self.emitter.doSomething.emit(item)
            if self.loopwait:
                self.msleep(self.loopwait)
                # End of while
        self.log.info(
            '#' * 80 + '\nOut of TaurusEmitterThread.run()' + '\n' + '#' * 80)
        # End of Thread


class DelayedSubscriber(Logger):
    """
    DelayedSubscriber(schema) will use a TaurusEmitterThread to perform
    a thread safe delayed subscribing on all Attributes of a given 
    Taurus Schema that has not been previously subscribed.

    .. warning:: This class belongs to a "Delayed Event Subscription" API added
                 in v.4.2.1-alpha as an *experimental* feature. This API may
                 not be stable and/or it may be removed in a future release
                 (even on a minor version change)
    """

    def __init__(self, schema, parent=None, sleep=10000, pause=5, period=0):

        self._schema = schema
        self.call__init__(Logger, 'DelayedSubscriber(%s)' % self._schema, None)
        self._factory = taurus.Factory(schema)

        self._modelsQueue = Queue()
        self._modelsThread = TaurusEmitterThread(parent=parent,
                                                 queue=self._modelsQueue,
                                                 method=self._modelSubscriber,
                                                 sleep=sleep, loopwait=pause,
                                                 polling=period)

        self._modelsQueue.put([self.addUnsubscribedAttributes])
        self._modelsThread.start()

    def _modelSubscriber(self, method, args=[]):
        self.debug('modelSubscriber(%s,%s)' % (method, args))
        return method(*args)

    def getUnsubscribedAttributes(self):
        """Check all pending subscriptions in the current factory
        """
        attrs = []
        for name, attr in self._factory.getExistingAttributes().items():
            if attr is None:
                continue
            elif attr.hasListeners() and not attr.isUsingEvents():
                attrs.append(attr)

        return attrs

    def addUnsubscribedAttributes(self):
        """Schedule subscription for all pending attributes
        """
        try:
            items = self.getUnsubscribedAttributes()
            if len(items):
                self.info('addUnsubscribedAttributes([%d])' % len(items))
                for attr in items:
                    self._addModelObj(attr)
                self._modelsThread.next()
                self.info('Thread queue: [%d]' % (self._modelsQueue.qsize()))
        except:
            self.warning(traceback.format_exc())

    def _addModelObj(self, modelObj):
        parent = modelObj.getParentObj()
        if parent:
            proxy = parent.getDeviceProxy()
            if not proxy:
                self.debug('addModelObj(%s), proxy not available' % modelObj)
                return

        self._modelsQueue.put([modelObj.subscribePendingEvents])
        self.debug('addModelObj(%s)' % str(modelObj))

    def cleanUp(self):
        self.trace("[DelayedSubscriber] cleanUp")
        self._modelsThread.stop()
        Logger.cleanUp(self)


class SingletonWorker(object):
    """
    SingletonWorker is used to manage TaurusEmitterThread as Singleton objects

    SingletonWorker is constructed using the same arguments 
    than TaurusTreadEmitter ; but instead of creating a QThread for each 
    instance it creates a single QThread for all instances.

    The Queue is still different for each of the instances; it is connected 
    to the TaurusEmitterThread signals (*next()* and *somethingDone()*) 
    and each Worker queue is used as a feed for the shared QThread.

    This implementation reduced the cpu of vacca application in a 50% factor.

    :param parent: a Qt/Taurus object
    :param name: identifies object logs
    :param queue: if None parent.getQueue() is used, if not then the queue 
        passed as argument is used
    :param method: the method to be executed using each queue item as argument
    :param cursor: if True or QCursor a custom cursor is set while 
        the Queue is not empty
    """
    _thread = None

    def __init__(self, parent=None, name='', queue=None, method=None,
                 cursor=None, sleep=5000, log=Logger.Warning, start=True):
        self.name = name
        self.log = Logger('SingletonWorker(%s)' % self.name)
        self.log.setLogLevel(log)
        self.log.info('At SingletonWorker.__init__(%s)' % self.name)
        self.parent = parent
        self.method = method
        self._running = False
        if SingletonWorker._thread is None:
            SingletonWorker._thread = TaurusEmitterThread(
                parent, name='SingletonWorker', cursor=cursor, sleep=sleep)
        self.thread = SingletonWorker._thread
        self.queue = queue or Queue()
        if start:
            self.start()

    def put(self, item, block=True, timeout=None):
        self.getQueue().put(item, block, timeout)

    def size(self):
        return self.getQueue().qsize()

    def next(self, item=None):
        if item is not None:
            self.put(item)
        elif self.queue.empty():
            return
        msg = ('At SingletonWorker.next(), '
               '%d items not passed yet to Emitter.'
               % self.queue.qsize())
        self.log.info(msg)
        # (queue.empty() and self.log.info or self.log.debug)(msg)
        try:
            i = 0
            while not self.queue.empty():
                # A blocking get here would hang the GUIs!!!
                item = self.queue.get(False)
                if self.method:
                    self.thread.getQueue().put([self.method] + list(item))
                else:
                    self.thread.getQueue().put(item)
                i += 1
            self.log.info('%d Items added to emitter queue' % i)
            self.thread.emitter.newQueue.emit()
        except Empty:
            self.log.warning(traceback.format_exc())
        except:
            self.log.warning(traceback.format_exc())
        return

    def getQueue(self):
        return self.queue

    def getDone(self):
        return self.thread.getDone()

    def start(self):
        self.thread.emitter.somethingDone.connect(self.next)
        self.thread.emitter.newQueue.connect(self.thread.next)
        try:
            self.thread.start()
        except:
            pass
        self.next()
        self._running = True
        return

    def stop(self):
        self.thread.emitter.somethingDone.disconnect(self.next)
        self.thread.emitter.newQueue.disconnect(self.thread.next)
        self._running = False
        return

    def clear(self):
        """
        This method will clear queue only if next() has not been called.
        If you call self.thread.clear() it will clear objects for all workers!,
        be careful
        """
        while not self.queue.empty():
            self.queue.get()
            # self.thread.clear()

    def purge(self, obj):
        """
        Remove a given object from all queues
        """
        nqueue = Queue()
        while not self.queue.empty():
            i = self.queue.get()
            if obj not in i:
                nqueue.put(i)
        while not nqueue.empty():
            self.queue.put(nqueue.get())
        self.next()

    def isRunning(self):
        return self._running

    def isFinished(self):
        return self.thread.isFinished()

    def finished(self):
        return self.thread.finished()

    def started(self):
        return self._running

    def terminated(self):
        return self.thread.terminated()

    def sleep(self, s):
        return self.thread.sleep(s)

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
event.py:
"""
from __future__ import print_function
from __future__ import absolute_import
from builtins import range
from builtins import object
import sys
import weakref
import threading
import time
try:
    from collections.abc import Sequence
except ImportError:  # bck-compat py 2.7
    from collections import Sequence
import taurus.core


__all__ = ["BoundMethodWeakref", "CallableRef", "EventGenerator",
           "ConfigEventGenerator", "ListEventGenerator", "EventListener",
           "AttributeEventWait", "AttributeEventIterator"]

__docformat__ = "restructuredtext"


class BoundMethodWeakref(object):
    """This class represents a weak reference to a method of an object since
    weak references to methods don't work by themselves"""

    def __init__(self, bound_method, del_cb=None):
        cb = (del_cb and self._deleted)
        self.func_ref = weakref.ref(bound_method.__func__, cb)
        self.obj_ref = weakref.ref(bound_method.__self__, cb)
        if cb:
            self.del_cb = CallableRef(del_cb)
        self.already_deleted = 0

    def _deleted(self, obj):
        if not self.already_deleted:
            del_cb = self.del_cb()
            if del_cb is not None:
                del_cb(self)
                self.already_deleted = 1

    def __call__(self):
        obj = self.obj_ref()
        if obj is not None:
            func = self.func_ref()
            if func is not None:
                return func.__get__(obj)

    def __hash__(self):
        return id(self)

    def __cmp__(self, other):
        if other.__class__ == self.__class__:
            from past.builtins import cmp
            ret = cmp((self.func_ref, self.obj_ref),
                      (other.func_ref, other.obj_ref))
            return ret
        return 1

    def __eq__(self, other):
        if hasattr(other, 'func_ref') and hasattr(other, 'obj_ref'):
            return ((self.func_ref, self.obj_ref)
                    == (other.func_ref, other.obj_ref))
        return False

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        obj, func = self.obj_ref(), self.func_ref()
        return 'BoundMethodWeakRef of %s.%s' % (obj, func)


def CallableRef(object, del_cb=None):
    """This function returns a callable weak reference to a callable object.
    Object can be a callable object, a function or a method.

    :param object: a callable object
    :type object: callable object
    :param del_cb: calback function. Default is None meaning to callback.
    :type del_cb: callable object or None

    :return: a weak reference for the given callable
    :rtype: taurus.core.util.BoundMethodWeakref or weakref.ref
    """
    im_self = None
    if hasattr(object, '__self__'):
        im_self = object.__self__
    elif hasattr(object, 'im_self'):
        im_self = object.im_self

    if im_self is not None:
        return BoundMethodWeakref(object, del_cb)
    return weakref.ref(object, del_cb)


# Reimplementation of BoundMethodWeakref class to avoid to have a hard
# reference in the event callbacks.
# Related to "Keeping references to event callbacks after unsubscribe_event"
# PyTango #185 issue.
class _BoundMethodWeakrefWithCall(BoundMethodWeakref):

    def __init__(self, bound_method, del_cb=None):
        """ Reimplementation of __init__ method"""
        super(_BoundMethodWeakrefWithCall, self).__init__(bound_method,
                                                          del_cb=del_cb)
        self.__name__ = self.func_ref().__name__

    def __call__(self, *args, **kwargs):
        """ Retrieve references and call callback with arguments
        """
        obj = self.obj_ref()
        if obj is not None:
            func = self.func_ref()
            if func is not None:
                return func(obj, *args, **kwargs)


class EventStack(object):
    "internal usage event stack"

    def __init__(self, history=True):
        self.unread_stack = []
        self.read_stack = []
        self.history = history

    def isEmpty(self):
        return len(self.unread_stack) == 0

    def push(self, event):
        self.unread_stack.append(event)

    def getNext(self):
        if self.isEmpty():
            return None
        event = self.unread_stack[0]
        del self.unread_stack[0]
        if self.history:
            self.read_stack.append(event)

        return event

    def getAllUnread(self):
        unread = self.unread_stack
        self.unread_stack = []
        return unread

    def getAllRead(self):
        read = self.read_stack
        self.read_stack = []
        return read


from .object import Object


class EventGenerator(Object):
    """Base class capable of firing events"""

    WaitTimeout = 0.1

    def __init__(self, name, events_active=True):
        """Event generator constructor.

        :param name: the event generator name
        :type  name: str
        :param events_active: generate events (default is True)
        :type  events_active: bool
        :return: a new EventGenerator
        :rtype: EventGenerator"""
        self.call__init__(Object)
        self.event_name = name
        self.cb_list = []
        self.last_val = None
        self.first_event_val = None
        self.events_active = events_active
        self.cond = threading.Condition()
        self.wait_list = []

    def lock(self):
        """Locks this event generator"""
        self.cond.acquire()

    def unlock(self):
        """Unlocks this event generator"""
        if self.cond._is_owned():
            self.cond.release()
        else:
            pass

    def subscribeEvent(self, cb, data=None, with_first_event=True):
        """Subscribes to the event

        :param cb: a callable object
        :type  cb: callable
        :param data: extra data to send each time an event is triggered on the
            given callback. Default is None.
        :type  data: object
        :param with_first_event: whether call the callback with the first event
            value (the most recent value) during the subscription process.
            Default is True.
        :type data: boolean
        """
        if not self.events_active:
            raise RuntimeError('%s does not have '
                                 'events/polling active' % self.event_name)

        cb_ref = CallableRef(cb, self.unsubscribeDeletedEvent)

        try:
            self.lock()
            if (cb_ref, data) in self.cb_list:
                raise RuntimeError('Callback %s(%s) already reg. on %s' %
                                     (cb, data, self.event_name))
            self.cb_list.append((cb_ref, data))
            if with_first_event:
                cb(data, self.first_event_val)
        finally:
            self.unlock()

    def unsubscribeDeletedEvent(self, cb_ref):
        """for internal usage only"""
        try:
            self.lock()
            aux_list = list(self.cb_list)
            for i in range(len(aux_list) - 1, -1, -1):
                pair = self.cb_list[i]
                if pair[0] is cb_ref:
                    del self.cb_list[i]
        finally:
            self.unlock()

    def unsubscribeEvent(self, cb, data=None):
        """Unsubscribes the given callback from the event. If the callback is not
        a listener for this event a debug message is generated an nothing happens.

        :param cb: a callable object
        :type  cb: callable
        :param data: extra data to send each time an event is triggered on the
                     given callback. Default is None
        :type  data: object"""
        cb_ref = CallableRef(cb)
        try:
            self.lock()
            if (cb_ref, data) in self.cb_list:
                self.cb_list.remove((cb_ref, data))
            else:
                self.debug("Trying to unsubscribe: %s is not a listener of %s" % (
                    str(cb_ref), self.event_name))
        finally:
            self.unlock()

    def isSubscribed(self, cb, data=None):
        """Determines if the given callback is registered for this event.

        :param cb: a callable object
        :type  cb: callable
        :param data: extra data to send each time an event is triggered on the
                     given callback. Default is None
        :type  data: object
        :return: True if callback is registered or False otherwise
        :rtype: bool"""
        cb_ref = CallableRef(cb, self.unsubscribeDeletedEvent)
        return (cb_ref, data) in self.cb_list

    def setEventsActive(self, events_active):
        """(De)activates events on this event generator.

        :param events_active: activate/deactivate events
        :type  events_active: bool"""
        self.events_active = events_active

    def getEventsActive(self):
        """Determines is events are active
        :return: True if events are active or False otherwise
        :rtype: bool"""
        return self.events_active

    def fireEvent(self, val, event_val=None):
        """Fires an event.
        :param val: event value
        :type  val: object"""
        try:
            self.lock()
            self.last_val = val
            self.cond.notifyAll()
            if event_val is None:
                event_val = val
            self.first_event_val = event_val
            for stack in self.wait_list:
                stack.push(event_val)
            for cb_ref, data in self.cb_list:
                cb = cb_ref()
                if cb is not None:
                    cb(data, event_val)
        finally:
            self.unlock()

    def waitEvent(self, val=None, equal=True, any=False, timeout=None,
                  stack=None):
        """Waits for an event to occur

        :param val: event value
        :type  val: object
        :param equal: check for equality. Default is True
        :type  equal: bool
        :param any: if True unblock after first event, not matter what value it
                    has. Default is False.
        :type  any: bool
        :param timeout: maximum time to wait (seconds). Default is None meaning
               wait forever.
        :type  timeout: float
        :param stack: For internal usage only.
        :return: the value of the event that unblocked the wait
        :rtype: object"""
        if not self.events_active:
            raise RuntimeError('%s does not have '
                                 'events/polling active' % self.event_name)
        try:
            self.lock()
            t0 = time.time()
            timeout_expired = False
            stack = stack or EventStack(history=False)
            while True:
                curr_val = self.last_val
                avail = not stack.isEmpty()
                if avail:
                    curr_val = stack.getNext()
                if any:
                    block = not avail
                else:
                    block = ((equal and (val != curr_val)) or
                             (not equal and (val == curr_val)))
                if timeout:
                    timeout_expired = (time.time() - t0 > timeout)
                if not block or timeout_expired:
                    break
                self.wait_list.append(stack)
                self.cond.wait(self.WaitTimeout)
                self.wait_list.remove(stack)
            val = curr_val
        finally:
            self.unlock()

        return val

    def read(self):
        """Read the last event

        :return: the last event value
        :rtype: object"""
        return self.last_val


class EventListener(object):
    """A class that listens for an event with a specific value

    Note: Since this class stores for each event value the last timestamp when
    it occured, it should only be used for events for which the event value
    domain (possible values) is limited and well known (ex: an enum)"""

    def __init__(self):
        self.last_val = None
        self.cond = threading.Condition()

        # a set implemented as a dictionary
        # dict<object, float>
        # key - event value
        # value - timestamp of last event with that value
        self.event_set = {}
        self.attr.addListener(self)

    def lock(self):
        """Locks this event listener"""
        self.cond.acquire()

    def unlock(self):
        """Unlocks this event listener"""
        if self.cond._is_owned():
            self.cond.release()
        else:
            pass

    def clearEventSet(self):
        "Clears the internal event buffer"
        self.event_set.clear()

    def fireEvent(self, v):
        """Notifies that a given event has arrived
        This function is protected inside with the object's lock. Do NOT call
        this function when you have the lock acquired on this object.

        :param v: event value
        :type  v: object"""
        try:
            t = time.time()
            self.lock()
            self.last_val = v
            self.event_set[v] = t
            self.cond.notifyAll()
        finally:
            self.unlock()

    def waitEvent(self, val, after=0, equal=True):
        """Wait for an event with the given value. You MUST protect this function
        with this object's lock before calling this method and always unlock it
        afterward, of course::

            from taurus.core.util.event import EventListener

            class MyEvtListener(EventListener):
                # Your specific listener code here
                pass

            evt_listener = EventListener()
            try:
                evt_listener.lock()
                t = time.time()
                go()
                evt_listener.waitEvent(Stop, t)
            finally:
                evt_listener.unlock()

        :param val: value to compare
        :type  val: object
        :param after: timestamp. wait for events comming after the given time.
                      default value is 0 meaning any event after Jan 1, 1970
        :type  after: float
        :param equal: compare for equality. equal=True means an event with the
                      given value, equal=False means any event which as a different value
        :type  equal: bool
        """
        s = self.event_set
        while True:
            if equal:
                t = s.get(val)
                if t and t >= after:
                    return
            else:
                for v, t in list(s.items()):
                    if v == val:
                        continue
                    if t >= after:
                        return
            self.cond.wait()


class ConfigEventGenerator(EventGenerator):
    """Manage configuration events"""

    def fireEvent(self, val, event_val=None):
        EventGenerator.fireEvent(self, val, event_val)


class ListEventGenerator(EventGenerator):
    """Manage list events, detecting changes in the list"""

    def __init__(self, name, events_active=True):
        self.call__init__(EventGenerator, name, events_active)
        self.last_val = []
        self.first_event_val = [], [], []

    def fireEvent(self, val):
        """Notifies that a given event has arrived
        This function is protected inside with the object's lock. Do NOT call
        this function when you have the lock acquired on this object.

        :param val: event value
        :type  val: object"""
        # if attribute is not alive and last time was also not alive then
        # skip the event propagation
        if val is None:
            if len(self.last_val) == 0:
                return
            val = []

        try:
            self.lock()
            val = list(val)
            last_val = self.last_val
            rm = [x for x in last_val if x not in val]
            add = [x for x in val if x not in last_val]
            event_val = val, rm, add
            EventGenerator.fireEvent(self, val, event_val)
            self.first_event_val = val, [], val
        finally:
            self.unlock()


class AttributeEventWait(object):
    """Class designed to connect to a :class:`taurus.core.taurusattribute.TaurusAttribute` and
    fire events or wait for a certain event."""

    def __init__(self, attr=None):
        self._last_val = None
        self._attr = None
        self._cond = threading.Condition()
        self._event_set = {}
        if attr is not None:
            self.connect(attr)

    def connect(self, attr):
        """Connect to the given attribute
        :param attr: the attribute to connect to
        :type  attr: taurus.core.taurusattribute.TaurusAttribute"""
        needAdd = True
        if self._attr is not None:
            if attr == self._attr:
                needAdd = False
            else:
                self._attr.removeListener(self)
        self.clearEventSet()
        self._last_val = None
        self._attr = attr
        if needAdd:
            self._attr.addListener(self)

    def disconnect(self):
        """Disconnects from the attribute. If not connected nothing happens."""
        self.clearEventSet()
        if self._attr:
            self._attr.removeListener(self)
        self._attr = None
        self._last_val = None

    def lock(self):
        """Locks this event listener"""
        self._cond.acquire()

    def unlock(self):
        """Unocks this event listener"""
        if self._cond._is_owned():
            self._cond.release()
        else:
            lock = getattr(self._cond, "_Condition__lock")
            th = getattr(lock, "_RLock__owner")
            curr_th = threading.current_thread()
            if th is not None:
                name = th.name
            else:
                name = "<unknown>"
            print("WARNING: Thread %s trying to unlock condition previously " \
                  "locked by thread %s" % (curr_th.name, name))

    def clearEventSet(self):
        "Clears the internal event buffer"
        self._event_set.clear()
        self._last_val = None

    def eventReceived(self, s, t, v):
        """Event listener method for the underlying attribute. Do not call this
        method. It will be called internally when the attribute generates
        an event."""
        if t == taurus.core.taurusbasetypes.TaurusEventType.Config:
            return
        elif t == taurus.core.taurusbasetypes.TaurusEventType.Error:
            self.fireEvent(None)
        else:
            self.fireEvent(v.rvalue)

    def fireEvent(self, v):
        """Notifies that a given event has arrived
        This function is protected inside with the object's lock. Do NOT call
        this function when you have the lock acquired on this object.

        :param v: event value
        :type  v: object"""
        t = time.time()
        self.lock()
        try:
            self._last_val = v
            self._event_set[v] = t
            self._cond.notifyAll()
        finally:
            self.unlock()

    def getLastRecordedEvent(self):
        """returns the value of the last recorded event or None if no event has
        been received or the last event was an error event

        :return: the last event value to be recorded
        :rtype: object"""
        return self._last_val

    def getRecordedEvents(self):
        """Returns a reference to the internal dictionary used to store the internal
        events. Modify the return dictionary at your own risk!

        :return: reference to the internal event dictionary
        :rtype: dict"""
        return self._event_set

    def getRecordedEvent(self, v):
        """Returns the the recorded local timestamp for the event with the given
        value or None if no event with the given value has been recorded.

        :param v: event value
        :type  v: object
        :return: local timestamp for the event or None if no event has been recorded
        :rtype: float"""
        return self._event_set.get(v)

    def waitEvent(self, val, after=0, equal=True, timeout=None, retries=-1,
                  any=False):
        """Wait for an event with the given value.

        :param val: value to compare
        :type  val: object
        :param after: timestamp. wait for events comming after the given time.
                      default value is 0 meaning any event after Jan 1, 1970
        :type  after: float
        :param equal: compare for equality. equal=True means an event with the
                      given value, equal=False means any event which as a different value
        :type  equal: bool
        :param timeout: maximum time to wait (seconds). Default is None meaning
               wait forever.
        :type  timeout: float
        :param retries: number of maximum retries of max timeout to attempts.
                        Default is -1 meaning infinite number of retries.
                        0 means no wait. Positive number is obvious.
        :param any: if any is True ignore 'val' parameter and accept any event.
                    If False (default),check with given 'val' parameter
        :type  any: bool
        """
        if retries == 0:
            return
        if timeout is None:
            # if waitting forever doesn't make sense to retry
            retries = 1
        if after is None:
            after = 0
        s = self._event_set
        self.lock()
        try:
            # increase the retries by one just because of how the loop is done
            if retries > 0:
                retries += 1
            while retries != 0:
                if any:
                    for v, t in s.items():
                        if t >= after:
                            return
                if equal:
                    t = s.get(val)
                    if (t is not None) and (t >= after):
                        return
                else:
                    for v, t in s.items():
                        if v == val:
                            continue
                        if t >= after:
                            return
                self._cond.wait(timeout)
                retries -= 1
        except Exception as e:
            sys.stderr.write(
                "AttributeEventWait: Caught exception while waiting: %s\n" % str(e))
            raise e
        finally:
            self.unlock()


class AttributeEventIterator(object):
    """Internal class. For test purposes"""

    def __init__(self, *attrs):
        self._attrs = None
        self._cond = threading.Condition()
        if len(attrs) > 0:
            self.connect(attrs)

    def connect(self, attrs):
        if not isinstance(attrs, Sequence):
            attrs = (attrs,)
        self.disconnect()
        self._attrs = attrs
        for attr in self._attrs:
            attr.addListener(self)

    def disconnect(self):
        if self._attrs is None:
            return
        for attr in self._attrs:
            attr.removeListener(self)

    def lock(self):
        self._cond.acquire()

    def unlock(self):
        if self._cond._is_owned():
            self._cond.release()
        else:
            lock = getattr(self._cond, "_Condition__lock")
            th = getattr(lock, "_RLock__owner")
            curr_th = threading.current_thread()
            print(("WARNING: Thread %s trying to unlock condition previously "
                   + "locked by thread %s") % (curr_th.name, th.name))

    def eventReceived(self, s, t, v):
        if t not in (taurus.core.taurusbasetypes.TaurusEventType.Change, taurus.core.taurusbasetypes.TaurusEventType.Periodic):
            return
        self.fireEvent(s, v.rvalue)

    def fireEvent(self, s, v):
        t = time.time()
        self.lock()
        try:
            self._data = s, v
            self._cond.notifyAll()
        finally:
            self.unlock()

    def events(self, timeout=1):
        self.lock()
        try:
            while True:
                self._cond.wait(timeout)
                yield self._data
        except Exception as e:
            print("INFO: Caught exception while waiting", str(e))
        finally:
            self.unlock()

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
This module contains a set of useful containers that are not part of the standard
python distribution.
"""
from __future__ import print_function

from builtins import range
from builtins import object

from future.utils import string_types

import copy
import time
import weakref
try:
    from collections.abc import Sequence
except ImportError:  # bck-compat py 2.7
    from collections import Sequence

__all__ = ["CaselessList", "CaselessDict", "CaselessWeakValueDict", "LoopList",
           "CircBuf", "LIFO", "TimedQueue", "self_locked", "ThreadDict",
           "defaultdict", "defaultdict_fromkey", "CaselessDefaultDict",
           "DefaultThreadDict", "getDictAsTree", "ArrayBuffer", ]

__docformat__ = "restructuredtext"


class CaselessList(list):
    """A case insensitive lists that has some caseless methods. Only allows
    strings as list members. Most methods that would normally return a list,
    return a CaselessList. (Except list() and lowercopy())
    Sequence Methods implemented are :
    __contains__, remove, count, index, append, extend, insert,
    __getitem__, __setitem__, __getslice__, __setslice__
    __add__, __radd__, __iadd__, __mul__, __rmul__
    Plus Extra methods:
    findentry, copy , lowercopy, list
    Inherited methods :
    __imul__, __len__, __iter__, pop, reverse, sort
    """

    def __init__(self, inlist=[]):
        list.__init__(self)
        for entry in inlist:
            if not isinstance(entry, string_types):
                raise TypeError('Members of this object must be strings. '
                                'You supplied \"%s\" which is \"%s\"' %
                                (entry, type(entry)))
            self.append(entry)

    def __lowerstreq(self, a, b):
        a = str(a)
        b = str(b)
        return (a.lower() == b.lower())

    def findentry(self, item):
        """A caseless way of checking if an item is in the list or not.
        It returns None or the entry."""
        if not isinstance(item, string_types):
            raise TypeError('Members of this object must be strings. '
                            'You supplied \"%s\"' % type(item))
        for entry in self:
            if self.__lowerstreq(item, entry):
                return entry
        return None

    def __contains__(self, item):
        """A caseless way of checking if a list has a member in it or not."""
        for entry in self:
            if self.__lowerstreq(item, entry):
                return True
        return False

    def remove(self, item):
        """Remove the first occurence of an item, the caseless way."""
        for entry in self:
            if self.__lowerstreq(item, entry):
                list.remove(self, entry)
                return
        raise ValueError(': list.remove(x): x not in list')

    def copy(self):
        """Return a CaselessList copy of self."""
        return CaselessList(self)

    def list(self):
        """Return a normal list version of self."""
        return list(self)

    def lowercopy(self):
        """Return a lowercase (list) copy of self."""
        return [str(entry).lower() for entry in self]

    def append(self, item):
        """Adds an item to the list and checks it's a string."""
        if not isinstance(item, string_types):
            raise TypeError('Members of this object must be strings. '
                            'You supplied \"%s\"' % type(item))
        list.append(self, item)

    def extend(self, item):
        """Extend the list with another list. Each member of the list must be
        a string."""
        if not isinstance(item, list):
            raise TypeError('You can only extend lists with lists. '
                            'You supplied \"%s\"' % type(item))
        for entry in item:
            if not isinstance(entry, string_types):
                raise TypeError('Members of this object must be strings. '
                                'You supplied \"%s\"' % type(entry))
            list.append(self, entry)

    def count(self, item):
        """Counts references to 'item' in a caseless manner.
        If item is not a string it will always return 0."""
        if not isinstance(item, string_types):
            return 0
        count = 0
        for entry in self:
            if self.__lowerstreq(item, entry):
                count += 1
        return count

    def index(self, item, minindex=0, maxindex=None):
        """Provide an index of first occurence of item in the list. (or raise
        a ValueError if item not present)
        If item is not a string, will raise a TypeError.
        minindex and maxindex are also optional arguments
        s.index(x[, i[, j]]) return smallest k such that s[k] == x and i <= k < j
        """
        if maxindex is None:
            maxindex = len(self)
        minindex = max(0, minindex) - 1
        maxindex = min(len(self), maxindex)
        if not isinstance(item, string_types):
            raise TypeError('Members of this object must be strings. '
                            'You supplied \"%s\"' % type(item))
        index = minindex
        while index < maxindex:
            index += 1
            if self.__lowerstreq(item, self[index]):
                return index
        raise ValueError(': list.index(x): x not in list')

    def insert(self, i, x):
        """s.insert(i, x) same as s[i:i] = [x]
        Raises TypeError if x isn't a string."""
        if not isinstance(x, string_types):
            raise TypeError('Members of this object must be strings. '
                            'You supplied \"%s\"' % type(x))
        list.insert(self, i, x)

    def __setitem__(self, index, value):
        """For setting values in the list.
        index must be an integer or (extended) slice object. (__setslice__ used
        for simple slices)
        If index is an integer then value must be a string.
        If index is a slice object then value must be a list of strings - with
        the same length as the slice object requires.
        """
        if isinstance(index, int):
            if not isinstance(value, string_types):
                raise TypeError('Members of this object must be strings. '
                                'You supplied \"%s\"' % type(value))
            list.__setitem__(self, index, value)
        elif isinstance(index, slice):
            if not hasattr(value, '__len__'):
                raise TypeError(
                    'Value given to set slice is not a sequence object.')
            for entry in value:
                if not isinstance(entry, string_types):
                    raise TypeError('Members of this object must be strings. '
                                    'You supplied \"%s\"' % type(entry))
            list.__setitem__(self, index, value)
        else:
            raise TypeError('Indexes must be integers or slice objects.')

    def __setslice__(self, i, j, sequence):
        """Called to implement assignment to self[i:j]."""
        for entry in sequence:
            if not isinstance(entry, string_types):
                raise TypeError('Members of this object must be strings. '
                                'You supplied \"%s\"' % type(entry))
        list.__setslice__(self, i, j, sequence)

    def __getslice__(self, i, j):
        """Called to implement evaluation of self[i:j].
        Although the manual says this method is deprecated - if I don't define
        it the list one is called.
        (Which returns a list - this returns a CaselessList)"""
        return CaselessList(list.__getslice__(self, i, j))

    def __getitem__(self, index):
        """For fetching indexes.
        If a slice is fetched then the list returned is a CaselessList."""
        if not isinstance(index, slice):
            return list.__getitem__(self, index)
        else:
            return CaselessList(list.__getitem__(self, index))

    def __add__(self, item):
        """To add a list, and return a CaselessList.
        Every element of item must be a string."""
        return CaselessList(list.__add__(self, item))

    def __radd__(self, item):
        """To add a list, and return a CaselessList.
        Every element of item must be a string."""
        return CaselessList(list.__add__(self, item))

    def __iadd__(self, item):
        """To add a list in place."""
        for entry in item:
            self.append(entry)

    def __mul__(self, item):
        """To multiply itself, and return a CaselessList.
        Every element of item must be a string."""
        return CaselessList(list.__mul__(self, item))

    def __rmul__(self, item):
        """To multiply itself, and return a CaselessList.
        Every element of item must be a string."""
        return CaselessList(list.__rmul__(self, item))


class CaselessDict(dict):
    """A case insensitive dictionary. Use this class as a normal dictionary.
    The keys must be strings"""

    def __init__(self, other=None):
        if other:
            # Doesn't do keyword args

            # -------------------------------------------------------
            # TODO: when we drop py2 support, change this to
            #       `if isinstance(other, collections.abc.Mapping)`
            #
            if hasattr(other, 'items'):
                for k, v in other.items():
                    dict.__setitem__(self, k.lower(), v)
            # -------------------------------------------------------
            else:
                for k, v in other:
                    dict.__setitem__(self, k.lower(), v)

    def __getitem__(self, key):
        return dict.__getitem__(self, key.lower())

    def __setitem__(self, key, value):
        dict.__setitem__(self, key.lower(), value)

    def __contains__(self, key):
        return dict.__contains__(self, key.lower())

    def has_key(self, key):
        """overwritten from :meth:`dict.has_key` (needed for python2)"""
        return key.lower() in self

    def get(self, key, def_val=None):
        """overwritten from :meth:`dict.get`"""
        return dict.get(self, key.lower(), def_val)

    def setdefault(self, key, def_val=None):
        """overwritten from :meth:`dict.setdefault`"""
        return dict.setdefault(self, key.lower(), def_val)

    def update(self, other):
        """overwritten from :meth:`dict.update`"""
        for k, v in other.items():
            dict.__setitem__(self, k.lower(), v)

    def fromkeys(self, iterable, value=None):
        d = CaselessDict()
        for k in iterable:
            dict.__setitem__(d, k.lower(), value)
        return d

    def pop(self, key, def_val=None):
        """overwritten from :meth:`dict.pop`"""
        return dict.pop(self, key.lower(), def_val)

    def __delitem__(self, k):
        dict.__delitem__(self, k.lower())


class CaselessWeakValueDict(weakref.WeakValueDictionary):

    def __init__(self, other=None):
        weakref.WeakValueDictionary.__init__(self, other)
        if other:
            # Doesn't do keyword args
            if isinstance(other, dict):
                for k, v in other.items():
                    weakref.WeakValueDictionary.__setitem__(self, k.lower(), v)
            else:
                for k, v in other:
                    weakref.WeakValueDictionary.__setitem__(self, k.lower(), v)

    def __getitem__(self, key):
        return weakref.WeakValueDictionary.__getitem__(self, key.lower())

    def __setitem__(self, key, value):
        weakref.WeakValueDictionary.__setitem__(self, key.lower(), value)

    def __contains__(self, key):
        return weakref.WeakValueDictionary.__contains__(self, key.lower())

    def has_key(self, key):
        """overwritten from :meth:`weakref.WeakValueDictionary`
        (needed for python2)
        """
        return key in self

    def get(self, key, def_val=None):
        """overwritten from :meth:`weakref.WeakValueDictionary.get`"""
        return weakref.WeakValueDictionary.get(self, key.lower(), def_val)

    def setdefault(self, key, def_val=None):
        """overwritten from :meth:`weakref.WeakValueDictionary.setdefault`"""
        return weakref.WeakValueDictionary.setdefault(self, key.lower(), def_val)

    def update(self, other):
        """overwritten from :meth:`weakref.WeakValueDictionary.update`"""
        if other:
            for k, v in other.items():
                weakref.WeakValueDictionary.__setitem__(self, k.lower(), v)

    def fromkeys(self, iterable, value=None):
        d = CaselessWeakValueDict()
        for k in iterable:
            weakref.WeakValueDictionary.__setitem__(d, k.lower(), value)
        return d

    def pop(self, key, def_val=None):
        """overwritten from :meth:`weakref.WeakValueDictionary.pop`"""
        return weakref.WeakValueDictionary.pop(self, key.lower(), def_val)

    def __delitem__(self, k):
        weakref.WeakValueDictionary.__delitem__(self, k.lower())


# {{{ http://code.activestate.com/recipes/576642/ (r10)
import pickle
import json
import csv
import os
import shutil


class PersistentDict(dict):
    ''' Persistent dictionary with an API compatible with shelve and anydbm.

    The dict is kept in memory, so the dictionary operations run as fast as
    a regular dictionary.

    Write to disk is delayed until close or sync (similar to gdbm's fast mode).

    Input file format is automatically discovered.
    Output file format is selectable between pickle, json, and csv.
    All three serialization formats are backed by fast C implementations.

    '''

    def __init__(self, filename, flag='c', mode=None, format='pickle', *args, **kwds):
        self.flag = flag                    # r=readonly, c=create, or n=new
        self.mode = mode                    # None or an octal triple like 0644
        self.format = format                # 'csv', 'json', or 'pickle'
        self.filename = filename
        if flag != 'n' and os.access(filename, os.R_OK):
            fileobj = open(filename, 'rb' if format == 'pickle' else 'r')
            with fileobj:
                self.load(fileobj)
        dict.__init__(self, *args, **kwds)

    def sync(self):
        'Write dict to disk'
        if self.flag == 'r':
            return
        filename = self.filename
        tempname = filename + '.tmp'
        fileobj = open(tempname, 'wb' if self.format == 'pickle' else 'w')
        try:
            self.dump(fileobj)
        except Exception:
            os.remove(tempname)
            raise
        finally:
            fileobj.close()
        shutil.move(tempname, self.filename)    # atomic commit
        if self.mode is not None:
            os.chmod(self.filename, self.mode)

    def close(self):
        self.sync()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def dump(self, fileobj):
        if self.format == 'csv':
            csv.writer(fileobj).writerows(list(self.items()))
        elif self.format == 'json':
            json.dump(self, fileobj, separators=(',', ':'))
        elif self.format == 'pickle':
            pickle.dump(dict(self), fileobj, 2)
        else:
            raise NotImplementedError('Unknown format: ' + repr(self.format))

    def load(self, fileobj):
        # try formats from most restrictive to least restrictive
        for loader in (pickle.load, json.load, csv.reader):
            fileobj.seek(0)
            try:
                return self.update(loader(fileobj))
            except Exception:
                pass
        raise ValueError('File not in a supported format')


class LoopList(object):
    '''this class provides an effectively cyclic list.
    It can be used, e.g., for storing colors or pen properties to be changed automatically in a plot

    A LoopList stores an internal index to remember the last accessed item in the list
    It provides  previous(), current() and next() methods that return the previous,current and next items in the list.
    The method allItems() returns a copy of all items contained in the list.
    The index can be accessed by setCurrentIndex() and getCurrentIndex()  (setCurrentIndex(i) additionally returns new current item)
    Items can be accessed ***without modifying the current index*** by using llist[i]  and llist[i]=x syntax
    len(llist) returns the **period** of the list.

    .. note::

        only basic methods of lists are implemented for llists. In particular,
        the following are **not** implemented:

            - slicing
            - resizing (append, insert, del,...)
            - binary operators (+,*,...)

    ..note::

        it can be used for loops, but the loop will be infinite unless other
        condition is used for exiting it:

            - for item in llist: print item  # This is a infinite loop!!
            - for i in range(len(llist)):print  llist[i]  #This is not infinite
              since len(llist) returns the period of the list'''

    def __init__(self, itemlist=[]):
        self.setItemList(itemlist)

    def setItemList(self, itemlist):
        '''sets the item list'''
        self._itemlist = list(itemlist)
        self._index = 0
        self._nitems = len(self._itemlist)

    def current(self):
        '''returns current item'''
        try:
            # makes the list effectively cyclic
            return self._itemlist[self._index % self._nitems]
        except ZeroDivisionError:
            raise IndexError('cyclic list is empty')

    def setCurrentIndex(self, index):
        '''sets current index (and returns the corresponding item)'''
        self._index = index
        return self.current()

    def getCurrentIndex(self):
        '''returns the current index'''
        return self._index

    def __next__(self):
        '''advances one item in the list and returns it'''
        self._index += 1
        return self.current()

    next = __next__

    def previous(self):
        '''goes one item back in the list and returns it'''
        self._index -= 1
        return self.current()

    def allItems(self):
        """returns the items list (one period)"""
        return self._itemlist

    def __getitem__(self, i):
        try:
            return self._itemlist[i % self._nitems]
        except ZeroDivisionError:
            raise IndexError('cyclic list is empty')

    def __setitem__(self, i, y):
        self._itemlist[i % self._nitems] = y

    def __len__(self):
        return self._nitems


class CircBuf(object):
    """A circular buffer of Python values.

    Examples::

        >>> cb = CircBuf(3)
        >>> cb.is_empty()
        1
        >>> cb.put('first')
        >>> cb.is_empty()
        0
        >>> cb.put('second')
        >>> cb.put('third')
        >>> cb.is_full()
        1
        >>> cb.put('fourth')
        >>> cb.get()
        'second'
        >>> cb.get()
        'third'
        >>> cb.get()
        'fourth'
        >>> cb.is_empty()
        1"""

    def __init__(self, leng):
        """Construct an empty circular buffer."""

        self.buf = leng * [None]
        self.len = self.g = self.p = 0

    def is_empty(self):
        """Returns true only if CircBuf has no items."""
        return self.len == 0

    def is_full(self):
        """Returns true only if CircBuf has no space."""
        return self.len == len(self.buf)

    def get(self):
        """Retrieves an item from a non-empty circular buffer."""
        result = self.buf[self.g]
        self.g = (self.g + 1) % len(self.buf)
        self.len -= 1
        return result

    def put(self, item):
        """Puts an item onto a circular buffer."""
        self.buf[self.p] = item
        self.p = (self.p + 1) % len(self.buf)
        if self.len == len(self.buf):
            self.g = self.p
        else:
            self.len += 1


class LIFO(object):

    def __init__(self, max=10):
        self._data = []
        self._max = max

    def append(self, elem):
        if self._max == 0:
            return

        while len(self._data) >= self._max:
            self._data.pop(0)
        self._data.append(elem)

    def extend(self, lst):
        if self._max == 0:
            return
        s = len(lst)
        if s >= self._max:
            self._data = lst[s - self._max:]
        else:
            while len(self._data) + len(lst) > self._max:
                self._data.pop(0)
            self._data.extend(lst)

    def pop(self, index=0):
        self._data.pop(index)

    def clear(self):
        self._data = []

    def get(self):
        return self._data

    def getCopy(self):
        return copy.copy(self._data)

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, str(self._data))


class TimedQueue(list):
    """ A FIFO that keeps all the values introduced at least for a given time.
    Applied to some device servers, to force States to be kept at least a minimum time.
    Previously named as PyTango_utils.device.StateQueue
    pop(): The value is removed only if delete_time has been reached.
    at least 1 value is always kept in the list
    """

    def __init__(self, arg=None):
        """ Initializes the list with a sequence or an initial value. """
        if arg is None:
            list.__init__(self)
        elif isinstance(arg, Sequence):
            list.__init__(self, arg)
        else:
            list.__init__(self)
            self.append(arg, 1)

    def append(self, obj, keep=15):
        """ Inserts a tuple with (value,insert_time,delete_time=now+keep) """
        now = time.time()
        l = (obj, now, now + keep)
        list.append(self, l)

    def pop(self, index=0):
        """ Returns the indicated value, or the first one; but removes only if delete_time has been reached.
        All values are returned at least once.
        When the queue has only a value, it is not deleted.
        """
        if not self:
            return None  # The list is empty
        now = time.time()
        s, t1, t2 = self[index]
        if now < t2 or len(self) == 1:
            return s
        else:
            return list.pop(self, index)[0]

    def index(self, obj):
        for i in range(len(self)):
            if self[i][0] == obj:
                return i
        return None

    def __contains__(self, obj):
        for t in self:
            if t[0] == obj:
                return True
        return False
    pass


def self_locked(func, reentrant=True):
    '''Decorator to make thread-safe class members
       Decorator to create thread-safe objects.

       .. warning::

            - With Lock() this decorator should not be used to decorate
              nested functions; it will cause Deadlock!
            - With RLock this problem is avoided ... but you should rely more
              on python threading'''
    import threading

    def lock_fun(self, *args, **kwargs):
        if not hasattr(self, 'lock'):
            if reentrant:
                setattr(self, 'lock', threading.RLock())
            else:
                setattr(self, 'lock', threading.Lock())
        if not hasattr(self, 'trace'):
            setattr(self, 'trace', False)
        self.lock.acquire()
        try:
            if self.trace:
                print("locked: %s" % self.lock)
            result = func(self, *args, **kwargs)
        finally:
            self.lock.release()
            if self.trace:
                print("released: %s" % self.lock)
        return result
    return lock_fun


class ThreadDict(dict):
    ''' Thread safe dictionary with redefinable read/write methods and a
    background thread for hardware update.  All methods are thread-safe using
    *@self_lock* decorator.

    .. note::
        any method decorated in this way CANNOT call other decorated methods!
        All values of the dictionary will be automatically updated in a separate
        Thread using read_method provided. Any value overwritten in the dict
        should launch the write_method.

    Briefing::

        a[2] equals to a[2]=read_method(2)
        a[2]=1 equals to a[2]=write_method(2,1)'''

    def __init__(self, other=None, read_method=None, write_method=None, timewait=0.1, threaded=True):
        self.read_method = read_method
        self.write_method = write_method
        self.timewait = timewait
        self.threaded = threaded
        self._threadkeys = []
        self.trace = False
        self.last_update = 0
        self.last_cycle_start = 0
        # equals to self.__class__.__base__ or type(self).__bases__[0]
        self.parent = type(self).mro()[1]

    def tracer(self, text):
        print(text)

    def start(self):
        import threading
        if not self.threaded:
            return
        if hasattr(self, '_Thread') and self._Thread and self._Thread.is_alive():
            return
        self.event = threading.Event()
        self.event.clear()
        self._Thread = threading.Thread(target=self.run)
        self._Thread.setDaemon(True)
        self._Thread.start()

    def stop(self):
        if self.threaded and hasattr(self, 'event'):
            self.event.set()
        if hasattr(self, '_Thread'):
            self._Thread.join()

    def alive(self):
        if not hasattr(self, '_Thread') or not self._Thread:
            return False
        else:
            return self._Thread.is_alive()

    def __del__(self):
        self.stop()
        # dict.__del__(self)

    def run(self):
        while not self.event.isSet():
            keys = self.threadkeys()
            for k in keys:
                try:
                    #@todo It must be checked wich method for reading is better for thread_safe
                    if True:
                        self.__getitem__(k, hw=True)
                    # try this alternative in case of deadlock (it could need
                    # extra locks inside read_method)
                    else:
                        if self.read_method:
                            value = self.read_method(k)
                            self.__setitem__(k, value, hw=False)
                finally:
                    self.event.wait(self.timewait)
                if self.event.isSet():
                    break
            timewait = self.get_timewait()
            self.event.wait(timewait)

    @self_locked
    def get_last_update(self):
        return self.last_update

    @self_locked
    def set_last_update(self, value):
        self.last_update = value

    @self_locked
    def get_last_cycle_start(self):
        return self.last_cycle_start

    @self_locked
    def set_last_cycle_start(self, value):
        self.last_cycle_start = value

    @self_locked
    def get_timewait(self):
        return self.timewait

    @self_locked
    def set_timewait(self, value):
        self.timewait = value

    @self_locked
    def append(self, key, value=None):
        if key not in self:
            self.parent.__setitem__(self, key, value)
        if key not in self._threadkeys:
            self._threadkeys.append(key)

    @self_locked
    def threadkeys(self):
        return self._threadkeys[:]

    @self_locked
    def __getitem__(self, key, hw=False):
        ''' This method launches a read_method execution if there's no thread on charge of doing that or if the hw flag is set to True. '''
        import time
        if (hw or not self.threaded) and self.read_method:
            dict.__setitem__(self, key, self.read_method(key))
            self.last_update = time.time()
        return dict.__getitem__(self, key)

    @self_locked
    def __setitem__(self, key, value, hw=True):
        ''' This method launches a write_method execution if the hw flag is not explicitly set to False. '''
        import time
        if hw and self.write_method:
            # It implies that a key will not be added here to read thread!
            dict.__setitem__(self, key, self.write_method(*[key, value]))
        else:
            dict.__setitem__(self, key, value)
        self.last_update = time.time()

    @self_locked
    def get(self, key, default=None):
        import time
        if not self.threaded and self.read_method:
            dict.__setitem__(self, key, self.read_method(key))
            self.last_update = time.time()
        if default is False:
            return dict.get(self, key)
        else:
            return dict.get(self, key, default)

    #__getitem__ = self_locked(dict.__getitem__)
    #__setitem__ = self_locked(dict.__setitem__)
    __delitem__ = self_locked(dict.__delitem__)
    __contains__ = self_locked(dict.__contains__)
    __iter__ = self_locked(dict.__iter__)

    pop = self_locked(dict.pop)
    #@self_locked
    # def pop(self,k,d=None):
    # if k in self.keys():
    # self.stop()
    #d = dict.pop(self,k)
    # self.start()
    # return d

    @self_locked
    def __str__(self):
        return "{" + ",".join(["'" + str(k) + "'" + ":" + "'" + str(v) + "'" for k, v in zip(dict.keys(self), dict.values(self))]) + "}"

    @self_locked
    def __repr__(self):
        return "{\n" + "\n,".join(["'" + str(k) + "'" + ":" + "'" + str(v) + "'" for k, v in zip(dict.keys(self), dict.values(self))]) + "\n}"
    #__str__ = self_locked(dict.__str__)
    #__repr__ = self_locked(dict.__repr__)

    #get = self_locked(dict.get)
    #has_key = self_locked(dict.has_key)
    update = self_locked(dict.update)
    copy = self_locked(dict.copy)

    keys = self_locked(dict.keys)
    values = self_locked(dict.values)
    items = self_locked(dict.items)
    #iterkeys = self_locked(dict.iterkeys)
    #itervalues = self_locked(dict.itervalues)
    #iteritems = self_locked(dict.iteritems)


class SortedDict(dict):
    """ This class implements a dictionary that returns keys in the same order they were inserted. """

    def __init__(self, other=None):
        dict.__init__(self)
        self._keys = []
        if other is not None:
            self.update(other)
        return

    def sort(self, key):
        """
        This method modifies the sorting of the dictionary overriding the existing sort key.
        :param key: it can be a sequence containing all the keys already existing in the dictionary
                    or a callable providing a sorting key algorithm.
        """
        import operator
        if hasattr(key, '__call__'):
            self._keys = sorted(self._keys, key=key)
        else:
            for k in self._keys:
                if k not in self._keys:
                    raise KeyError(k)
            self._keys = list(key)
        return self._keys[:]

    def __setitem__(self, k, v):
        if k not in self._keys:
            self._keys.append(k)
        dict.__setitem__(self, k, v)

    def update(self, other):
        if hasattr(other, 'items'):
            other = other.items()
        for k, v in other:
            self.__setitem__(k, v)

    @staticmethod
    def fromkeys(S, v=None):
        return SortedDict((s, v) for s in S)

    def pop(self, k, d=None):
        """Removes key and returns its (self[key] or d or None)"""
        if k not in self:
            return d
        self._keys.remove(k)
        return dict.pop(self, k)

    def popitem(self):
        """Removes and returns last key,value pair"""
        k = self._keys[-1]
        v = self[k]
        self.pop(k)
        return k, v

    def clear(self):
        self._keys = []
        return dict.clear(self)

    def keys(self):
        return self._keys[:]

    def values(self):
        return [self[k] for k in self._keys]

    def items(self):
        return [(k, self[k]) for k in self._keys]

    def __iter__(self):
        return (i for i in self._keys)

    def iteritems(self):
        return ((k, self[k]) for k in self._keys)

    def iterkeys(self):
        return (i for i in self._keys)

    def itervalues(self):
        return (self[k] for k in self._keys)

try:
    from collections import defaultdict
except:
    class defaultdict(dict):

        def __init__(self, default_factory=None, *a, **kw):
            if (default_factory is not None and
                    not hasattr(default_factory, '__call__')):
                raise TypeError('first argument must be callable')
            dict.__init__(self, *a, **kw)
            self.default_factory = default_factory

        def __getitem__(self, key):
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                return self.__missing__(key)

        def __missing__(self, key):
            if self.default_factory is None:
                raise KeyError(key)
            self[key] = value = self.default_factory()
            return value

        def __reduce__(self):
            if self.default_factory is None:
                args = tuple()
            else:
                args = self.default_factory,
            return type(self), args, None, None, list(self.items())

        def copy(self):
            return self.__copy__()

        def __copy__(self):
            return type(self)(self.default_factory, self)

        def __deepcopy__(self, memo):
            import copy
            return type(self)(self.default_factory,
                              copy.deepcopy(list(self.items())))

        def __repr__(self):
            return 'defaultdict(%s, %s)' % (self.default_factory,
                                            dict.__repr__(self))


class defaultdict_fromkey(defaultdict):
    """ Creates a dictionary with a default_factory function that creates new elements using key as argument.
    Usage : new_dict = defaultdict_fromkey(method); where method like (lambda key: return new_obj(key))
    Each time that new_dict[key] is called with a key that doesn't exist, method(key) is used to create the value
    Copied from PyAlarm device server
    """

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory(key)
        return value


class CaselessDefaultDict(defaultdict_fromkey, CaselessDict):
    """ a join venture between caseless and default dict
    This class merges the two previous ones.
    This declaration equals to::

        CaselessDefaultDict = type('CaselessDefaultType',(CaselessDict,defaultdict_fromkey),{})
    """

    def __getitem__(self, key):
        return defaultdict_fromkey.__getitem__(self, key.lower())
    pass


class DefaultThreadDict(defaultdict_fromkey, ThreadDict):
    """a join venture between thread and default dict
    This class merges the two previous ones.
    @todo This two classes are not yet well integrated ... the way a new key is added to the dict must be rewritten explicitly.
    """

    def __init__(self, other=None, default_factory=None, read_method=None, write_method=None, timewait=0.1, threaded=True):
        defaultdict_fromkey.__init__(self, default_factory)
        ThreadDict.__init__(self, other, read_method,
                            write_method, timewait, threaded)
    pass


def getDictAsTree(dct):
    """This method will print a recursive dict in a tree-like
       shape::

           >>> print(getDictAsTree({'A':{'B':[1,2],'C':[3]}}))"""
    def add_to_level(l, d):
        lines = []
        if isinstance(d, dict):
            for k, v in d.items():
                print('with key "%s"' % k)
                lines.append([''] * l + [str(k)])
                lines += add_to_level(l + 1, v)
        elif type(d) in [list, set]:  # End of recursion
            for e in d:
                if isinstance(e, dict):
                    lines += add_to_level(l, e)
                else:
                    lines.append([''] * l + [str(e)])
        else:
            lines.append([''] * l + [str(d)])
        return lines
    ls = ['\t'.join(line) for line in add_to_level(0, dct)]
    print('lines are : \n', ls)
    return '\n'.join(ls)


class ArrayBuffer(object):
    '''A data buffer which internally uses a preallocated numpy.array.
    An ArrayBuffer will only present the actual contents, not the full internal
    buffer, so when appending or extending, it behaves as if dynamic
    reallocation was taking place.

    The contents of the class:`ArrayBuffer` can be accessed as if it was a numpy
    array (i.e slicing notation like b[2:3], b[:,2], b[-1],... are all valid).

    For retrieving the full contents, see :meth:`ArrayBuffer.contents` and
    :meth:`ArrayBuffer.toArray`

    On creation, a given initial internal buffer and a maximum size are set. If
    the maximum size is larger than the original internal buffer, this will be
    automatically grown in geometrical steps if needed to accommodate the
    contents, up to the maximum size. Once the contents fill the maximum size,
    appending or extending the contents will result in older contents being
    discarded (in a FIFO way)

    The :meth:`append` and meth:`extend` methods are designed to be cheap
    (especially if the internal buffer size is already at the maximum size), at
    the expense of memory usage'''

    def __init__(self, buffer, maxSize=0):
        '''Creator.

        :param buffer: (numpy.array) a numpy.array suitable to be used as the
                       internal buffer.

        :param maxSize: (int) Maximum size of the internal buffer. The internal
                        buffer length will be allowed to grow up to this value.
                        If maxSize=0 (default), the maximum size will be that of
                        the given buffer
        '''

        self.__buffer = buffer
        self.__end = 0
        self.__bsize = self.__buffer.shape[0]
        self.__maxSize = max(maxSize, self.__bsize)

    def __getitem__(self, i):
        return self.__buffer[:self.__end].__getitem__(i)

    def __getslice__(self, i, j):
        return self.__buffer[:self.__end].__getslice__(i, j)

    def __len__(self):
        return self.__end

    def __repr__(self):
        return "ArrayBuffer with contents = %s" % self.__buffer[:self.__end].__repr__()

    def __str__(self):
        return self.__buffer[:self.__end].__str__()

    def __bool__(self):
        return self.__buffer[:self.__end].__bool__()

    def __setitem__(self, i, x):
        self.__buffer[:self.__end].__setitem__(i, x)

    def __setslice__(self, i, j, a):
        if i >= self.__end or j > self.__end:
            raise IndexError()
        self.__buffer[:self.__end].__setslice__(i, j, a)

    def resizeBuffer(self, newlen):
        '''resizes the internal buffer'''
        if newlen < self.__end:
            self.__end = newlen
        shape = list(self.__buffer.shape)
        shape[0] = newlen
        try:
            self.__buffer.resize(shape)  # first try to resize in-place
        except:
            import numpy
            # if not possible, do it by copying
            self.__buffer = numpy.resize(self.__buffer, shape)
        self.__bsize = self.__buffer.shape[0]

    def append(self, x):
        ''' similar to the append method in a list, except that once the maximum
        buffer size is reached, elements get discarded on the begginning to keep
        the size within the limit

        :param x: (scalar) element to be appended

        .. seealso:: :meth:`extend`
        '''
        try:
            self.__buffer[self.__end] = x
        except IndexError:
            if self.__bsize < self.__maxSize:
                self.resizeBuffer(min(2 * self.__bsize, self.__maxSize))
                # recursively call itself again after resizing
                return self.append(x)
            self.moveLeft(1)
            self.__buffer[self.__end] = x
        self.__end += 1

    def extend(self, a):
        ''' similar to the extend method of a list, except that once the maximum
        buffer size is reached, elements get discarded on the begginning to keep
        the size within the limit

        :param a: (numpy.array) array of elements to append

        .. seealso:: :meth:`append`, :meth:`extendLeft`
        '''
        newend = self.__end + a.shape[0]
        if newend < self.__bsize:
            self.__buffer[self.__end:newend] = a
            self.__end = newend
        elif self.__bsize < self.__maxSize:
            self.resizeBuffer(min(2 * self.__bsize, self.__maxSize))
            # recursively call itself again after resizing
            return self.extend(a)
        else:
            self.moveLeft(newend - self.__bsize)
            self.__buffer[self.__end:] = a[-min(a.shape[0], self.__bsize):]
            self.__end = self.__bsize

    def extendLeft(self, a):
        ''' Prepends data to the current contents. Note that, contrary to the
        extent method, no data will be discarded if the maximum size limit is
        reached. Instead, an exception will be raised.

        :param a: (numpy.array) array of elements to append

        .. seealso:: :meth:`extend`'''
        len_a = a.shape[0]
        newend = self.__end + len_a
        if newend < self.__bsize:
            self.__buffer[len_a:newend] = self.__buffer[
                0:self.__end]  # move the contents to the right
            self.__buffer[0:len_a] = a
            self.__end = newend
        elif newend < self.__maxSize:
            self.resizeBuffer(min(2 * self.__bsize, self.__maxSize))
            # recursively call itself again after resizing
            return self.extendLeft(a)
        else:
            raise ValueError(
                'Maximum buffer size cannot be exceeded when calling extendLeft ')

    def moveLeft(self, n):
        '''discards n elements from the begginning to make space at the end of
        the buffer. Moves all elements n positions to the left and the contents
        size gets decreased by n

        **Note:** if n is larger or equal than the maximum buffer size, the
        whole buffer is wiped

        :param n: (int)'''
        newend = max(0, self.__end - n)
        self.__buffer[0:newend] = self.__buffer[n:self.__end]
        self.__end = newend

    def contents(self):
        '''returns the array of the contents that have already been filled. Note
        that it does not return the full buffer, only those elements that have
        been already set.

        It is equivalent to b[:]

        :return: (numpy.array) array of contents

        .. seealso:: :meth:`toArray`
        '''
        return self.__buffer[:self.__end]

    def toArray(self):
        '''returns a copy of the array of the contents. It is equivalent to
        ``b.contents.copy()``

        :return: (numpy.array) copy of array of contents

        .. seealso:: :meth:`contents`
        '''
        return self.contents().copy()

    def contentsSize(self):
        '''Equivalent to len(b)

        :return: (int) length of the current contents of the ArrayBuffer (not
                 the maximum size of the buffer)

        .. seealso:: :meth:`maxSize`
        '''
        return self.__end

    def bufferSize(self):
        '''Returns the current size of the internal buffer

        :return: (int) lcurrent length of the internal buffer

        .. seealso:: :meth:`contentsSize`, :meth:`maxSize`
        '''
        return self.__bsize

    def maxSize(self):
        '''Returns the maximum size of the internal buffer, beyond which the
        ArrayBuffer starts discarding elements when appending

        :return: (int) maximum length of the internal buffer

        .. seealso:: :meth:`contentsSize`, :meth:`append`, :meth:`extend`, :meth:`isFull`
        '''
        return self.__maxSize

    def setMaxSize(self, maxSize):
        '''Sets the maximum size of the internal buffer, beyond which the
        ArrayBuffer starts discarding elements when appending

        :param maxSize: (int) maximum length of the internal buffer

        .. seealso:: :meth:`contentsSize`, :meth:`append`, :meth:`extend`, :meth:`isFull`
        '''
        if maxSize < self.__bsize:
            raise ValueError(
                'Cannot set a maximum size below the current buffer size (%i)' % self.__bsize)
        self.__maxSize = maxSize

    def isFull(self):
        '''Whether the contents fill the whole of the internal buffer

        :return: (bool) True if the contents fill the maximum size. False otherwise.

        .. seealso:: :meth:`maxSize`
        '''
        return self.__end >= self.__maxSize

    def remainingSize(self):
        '''returns the remaining free space in the internal buffer (e.g., 0 if it is full)

        :return: (int) length of the unused space in the internal buffer

        .. seealso:: :meth:`contentsSize`, :meth:`maxSize`,
        '''
        return self.maxSize() - self.contentsSize()


def chunks(l, n):
    '''Generator which yields successive n-sized chunks from l'''
    for i in range(0, len(l), n):
        yield l[i:i + n]

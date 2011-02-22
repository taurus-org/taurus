#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""adapted from http://code.activestate.com/recipes/576576/"""

__all__ = ["ThreadPool", "Worker"]

__docformat__ = "restructuredtext"

from threading import Thread
from Queue import Queue
from time import sleep

from prop import propertx
from log import Logger, DebugIt, TraceIt

class ThreadPool(Logger):
    """"""
    threadId = 0
    
    def __init__(self, name=None, parent=None, Psize=20, Qsize=20, daemons=True):
        name = name or self.__class__.__name__
        Logger.__init__(self, name, parent)
        self._daemons = daemons
        self.workers = []
        self.jobs = Queue(Qsize)
        self.size = Psize
        self.accept = True
        
    @propertx
    def size():
        def set(self, newSize):
            """set method for the size property"""
            for i in xrange(newSize-len(self.workers)):
                ThreadPool.threadId += 1
                name = "%s.W%03i" % (self.log_name, ThreadPool.threadId)
                new = Worker(self, name, self._daemons)
                self.workers.append(new)
                self.debug("Starting %s" % name)
                new.start()
            # remove the old worker threads
            for i in xrange(len(self.workers)-newSize):
                self.jobs.put((None, None, None, None))
                
        def get(self):
            """get method for the size property"""
            return len(self.workers)
        
        return get, set, None, "number of threads"
    
    def add(self, job, callback=None, *args, **kw):
        if self.accept:
            self.jobs.put((job, args, kw, callback))
            
    def join(self):
        self.accept=False
        while True:
            for w in self.workers:
                if w.isAlive() :
                    self.jobs.put((None, None, None, None))
                    break
            else:
                break

    @property
    def qsize(self): return self.jobs.qsize()

class Worker(Thread, Logger):
    
    def __init__(self, pool, name=None, daemon=True):
        name = name or self.__class__.__name__
        Thread.__init__(self, name=name)
        Logger.__init__(self, name, pool)
        self.daemon = daemon
        self.pool = pool
        self.cmd=''
    
    #@TraceIt()
    def run(self):
        get = self.pool.jobs.get
        while True:
            cmd, args, kw, callback = get()
            if cmd:
                self.cmd = cmd.__name__
                if callback:
                    callback(cmd(*args, **kw))
                else:
                    cmd(*args, **kw)
                self.cmd = ''
            else:
                self.pool.workers.remove(self)
                return

if __name__=='__main__':

    def easyJob(*arg, **kw):
        n=arg[0]
        print '\tSleep\t\t', n
        sleep(n)
        return 'Slept\t%d' % n
    def longJob(*arg, **kw):
        print "\tStart\t\t\t", arg, kw
        n=arg[0]*3
        sleep(n)
        return "Job done in %d" % n
    def badJob(*a, **k):
        print '\n !!! OOOPS !!!\n'
        a=1/0
    def show(*arg, **kw):
        print 'callback : %s' % arg[0]

    pool = ThreadPool(5, 50)
    print "\n\t\t... let's add some jobs ...\n"
    for j in range(5):
        if j==1: pool.add(badJob)
        for i in range(5,0,-1):
            pool.add(longJob, show, i)
            pool.add(easyJob, show, i)
    print '''
        \t\t... and now, we're waiting for the %i workers to get the %i jobs done ...
    ''' % (pool.size, pool.qsize)
    sleep(15)
    print "\n\t\t... ok, that may take a while, let's get some reinforcement ...\n"
    sleep(5)
    pool.size=50
    print '\n\t\t... Joining ...\n'
    pool.join()
    print '\n\t\t... Ok ...\n'

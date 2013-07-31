#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
##
## http://www.tango-controls.org/static/tau/latest/doc/html/index.html
##
## (copyleft) CELLS / ALBA Synchrotron, Bellaterra, Spain
##
## This is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This software is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
###########################################################################

"""
emitter.py: This module provides a task scheduler used by TaurusGrid and TaurusDevTree widgets
"""

from functools import partial
import taurus
from taurus.qt import Qt
from taurus.core.util.log import Logger
from taurus.core.util.singleton import Singleton
import Queue,traceback

###############################################################################
# Helping methods

def isString(seq):
    if isinstance(seq,basestring): return True # It matches most python str-like classes
    if any(s in str(type(seq)).lower() for s in ('vector','array','list',)): return False
    if 'qstring' == str(type(seq)).lower(): return True # It matches QString
    return False
    
def modelSetter(obj,model):
    """
    This class is used for convenience as TaurusEmitterThread standard method
    """
    #print 'In modelSetter(%s,%s)' % (str(obj),str(model))
    if hasattr(obj,'setModel') and model is not None: obj.setModel(model)
    return
    
class MethodModel(object):
    """
    Class to emulate method execution as a setModel
    """
    def __init__(self,method): self.method = method
    def setModel(self,value): return self.method(value)
    
###############################################################################

class TaurusEmitterThread(Qt.QThread):
    """
    The TaurusEmitterThread Class
    ==========================

    This object get items from a python Queue and performs a thread safe operation on them.
    It is useful to serialize Qt tasks in a background thread.
    
    :param parent: a Qt/Taurus object
    :param name: identifies object logs
    :param queue: if None parent.getQueue() is used, if not then the queue passed as argument is used
    :param method: the method to be executed using each queue item as argument
    :param cursor: if True or QCursor a custom cursor is set while the Queue is not empty

    How TaurusEmitterThread works
    --------------------------

    TaurusEmitterThread is a worker thread that processes a queue of iterables passed as arguments to the specified method every time that  ``doSomething()`` is called:

     * ``self.method(*item)`` will be called if TaurusEmitterThread.method has been initialized.
     * ``item[0](item[1:])`` will be called if ``method`` is not initialized and the first element of the queued iterable is *callable*.

    TaurusEmitterThread uses two queues:

     * ``self.queue`` manages the objects added externally:

      + the ``next()`` method passes objects from ``self.queue`` to ``self.todo queue``
      + every time that a *somethingDone* signal arrives ``next()`` is called.
      + ``next()`` can be called also externally to ensure that the main queue is being processed.
      + the queue can be accessed externally using ``getQueue()``
      + ``getQueue().qsize()`` returns the number of remaining objects in queue.
      + while there are objects in queue the ``.next()`` method will override applications cursor. a call to ``next()`` with an empty queue will restore the original cursor.

     * ``self.todo`` is managed by the ``run()/start()`` method:

      - a loop waits continuously for new objects in ``self.todo`` queue.
      - if an object is found, it is sent in a *doSomething* signal.
      - if *"exit"* is found the loop exits.

    Usage example
    -------------

    .. code-block:: python

        #Applying TaurusEmitterThread to an existing class:
        import Queue
        from functools import partial
        
        def modelSetter(args):
            obj,model = args[0],args[1]
            obj.setModel(model)
        
        klass TaurusGrid(Qt.QFrame, TaurusBaseWidget):
            ...
            def __init__(self, parent = None, designMode = False):
                ...
                self.modelsQueue = Queue.Queue()
                self.modelsThread = TaurusEmitterThread(parent=self,queue=self.modelsQueue,method=modelSetter )
                ...
            def build_widgets(...):
                ...
                            previous,synoptic_value = synoptic_value,TaurusValue(cell_frame)
                            #synoptic_value.setModel(model)
                            self.modelsQueue.put((synoptic_value,model))
                ...
            def setModel(self,model):
                ...
                if hasattr(self,'modelsThread') and not self.modelsThread.isRunning(): 
                    self.modelsThread.start()
                elif self.modelsQueue.qsize():
                    self.modelsThread.next()
                ...    

    """
    def __init__(self, parent=None,name='',queue=None,method=None,cursor=None,sleep=5000):
        """
        Parent most not be None and must be a TaurusGraphicsScene!
        """
        Qt.QThread.__init__(self, parent)
        self.name = name
        self.log = Logger('TaurusEmitterThread(%s)'%self.name)
        self.log.setLogLevel(self.log.Info)
        self.queue = queue or Queue.Queue()
        self.todo = Queue.Queue()
        self.method = method
        self.cursor = Qt.QCursor(Qt.Qt.WaitCursor) if cursor is True else cursor
        self._cursor = False
        self.timewait = sleep
        
        self.emitter = Qt.QObject()
        self.emitter.moveToThread(Qt.QApplication.instance().thread())
        self.emitter.setParent(Qt.QApplication.instance()) #Mandatory!!! if parent is set before changing thread it could lead to segFaults!
        self._done = 0
        #Moved to the end to prevent segfaults ...
        Qt.QObject.connect(self.emitter, Qt.SIGNAL("doSomething"), self._doSomething)
        Qt.QObject.connect(self.emitter, Qt.SIGNAL("somethingDone"), self.next) 
        
    def getQueue(self):
        if self.queue: return self.queue
        elif hasattr(self.parent(),'getQueue'): self.parent().getQueue()
        else: return None

    def getDone(self):
        """ Returns % of done tasks in 0-1 range """
        return self._done/(self._done+self.getQueue().qsize()) if self._done else 0.
    
    def clear(self):
        while not self.todo.empty():
            self.todo.get()
        while not self.getQueue().empty():
            self.getQueue().get()
            self._done+=1
            
    def purge(obj):
        nqueue = Queue.Queue()
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

    def _doSomething(self,params):
        self.log.debug('At TaurusEmitterThread._doSomething(%s)'%str(params))
        if not self.method: 
            method,args = params[0],params[1:]
        else: 
            method,args = self.method,params
        if method:
            try:
                method(*args)
            except:
                self.log.error('At TaurusEmitterThread._doSomething(%s): \n%s' % (map(str,args),traceback.format_exc()))
        self.emitter.emit(Qt.SIGNAL("somethingDone"))
        self._done += 1
        return
                
    def next(self):
        queue = self.getQueue()
        msg = 'At TaurusEmitterThread.next(), %d items remaining.' % queue.qsize()
        (queue.empty() and self.log.info or self.log.debug)(msg)
        try:
            if not queue.empty():            
                if not self._cursor and self.cursor is not None: 
                    Qt.QApplication.instance().setOverrideCursor(Qt.QCursor(self.cursor))
                    self._cursor=True                
                item = queue.get(False) #A blocking get here would hang the GUIs!!!
                self.todo.put(item)
                self.log.debug('Item added to todo queue: %s' % str(item))
            elif self._cursor: 
                Qt.QApplication.instance().restoreOverrideCursor()
                self._cursor = False        
                
        except Queue.Empty:
            self.log.warning(traceback.format_exc())
            pass
        except: 
            self.log.warning(traceback.format_exc())
        return
        
    def run(self):
        Qt.QApplication.instance().thread().sleep(int(self.timewait/1000) if self.timewait>10 else int(self.timewait)) #wait(self.sleep)
        self.log.info('#'*80)
        self.log.info('At TaurusEmitterThread.run()')
        self.next()
        while True:
            self.log.debug('At TaurusEmitterThread.run() loop.')
            item = self.todo.get(True)
            if isString(item):
                if item == "exit":
                    break
                else:
                    continue
            self.log.debug('Emitting doSomething signal ...')
            self.emitter.emit(Qt.SIGNAL("doSomething"), item)
            #End of while
        self.log.info('#'*80+'\nOut of TaurusEmitterThread.run()'+'\n'+'#'*80)
        #End of Thread 
        
class SingletonWorker():#Qt.QObject):
    """
    The SingletonWorker works
    =========================
    
    The SingletonWorker class is constructed using the same arguments than the TaurusTreadEmitter class ; but instead of creating a QThread for each instance of the class it creates a single QThread for all instances.
    
    The Queue is still different for each of the instances; it is connected to the TaurusEmitterThread signals (*next()* and *somethingDone()*) and each Worker queue is used as a feed for the shared QThread.
    
    This implementation reduced the cpu of vacca application in a 50% factor.

    :param parent: a Qt/Taurus object
    :param name: identifies object logs
    :param queue: if None parent.getQueue() is used, if not then the queue passed as argument is used
    :param method: the method to be executed using each queue item as argument
    :param cursor: if True or QCursor a custom cursor is set while the Queue is not empty
    This class is used to manage TaurusEmitterThread as Singleton objects:
    """
    _thread = None
        
    def __init__(self,parent=None,name='',queue=None,method=None,cursor=None,sleep=5000,log=Logger.Warning,start=True):
        self.name = name
        self.log = Logger('SingletonWorker(%s)'%self.name)
        self.log.setLogLevel(log)
        self.log.info('At SingletonWorker.__init__(%s)'%self.name)
        self.parent = parent
        self.method = method
        self._running = False
        if SingletonWorker._thread is None:
            SingletonWorker._thread = TaurusEmitterThread(parent,name='SingletonWorker',cursor=cursor,sleep=sleep)
        self.thread = SingletonWorker._thread
        self.queue = queue or Queue.Queue()
        if start: self.start()
        
    def put(self,item,block=True,timeout=None):
        self.getQueue().put(item,block,timeout)
        
    def size(self):
        self.getQueue().qsize()
        
    def next(self,item=None):
        if item is not None: self.put(item)
        elif self.queue.empty(): return
        msg = 'At SingletonWorker.next(), %d items not passed yet to Emitter.' % self.queue.qsize()
        self.log.info(msg)
        #(queue.empty() and self.log.info or self.log.debug)(msg)
        try:
            i = 0
            while not self.queue.empty():
                item = self.queue.get(False) #A blocking get here would hang the GUIs!!!
                if self.method: 
                    self.thread.getQueue().put([self.method]+list(item))
                else:
                    self.thread.getQueue().put(item)
                i+=1
            self.log.info('%d Items added to emitter queue' % i)
            self.thread.emitter.emit(Qt.SIGNAL("newQueue"))
        except Queue.Empty:
            self.log.warning(traceback.format_exc())
        except: 
            self.log.warning(traceback.format_exc())
        return
    
    def getQueue(self): return self.queue
    def getDone(self): return self.thread.getDone()
    
    def start(self): 
        Qt.QObject.connect(self.thread.emitter, Qt.SIGNAL("somethingDone"), self.next) 
        Qt.QObject.connect(self.thread.emitter, Qt.SIGNAL("newQueue"), self.thread.next)
        try: self.thread.start()
        except: pass
        self.next()
        self._running = True
        return
    
    def stop(self): 
        Qt.QObject.disconnect(self.thread.emitter, Qt.SIGNAL("somethingDone"), self.next) 
        Qt.QObject.disconnect(self.thread.emitter, Qt.SIGNAL("newQueue"), self.thread.next)
        self._running = False
        return
    
    def clear(self):
        """ 
        This method will clear queue only if next() has not been called.
        If you call self.thread.clear() it will clear objects for all workers!, be careful
        """
        while not self.queue.empty(): self.queue.get()
        #self.thread.clear()
        
    def purge(obj):
        nqueue = Queue.Queue()
        while not self.queue.empty(): 
            i = self.queue.get()
            if obj not in i:
                nqueue.put(i)
        while not nqueue.empty():
            self.queue.put(nqueue.get())
        
    def isRunning(self): return self._running
    def isFinished(self): return self.thread.isFinished()
    def finished(self): return self.thread.finished()
    def started(self): return self._running
    def terminated(self): return self.thread.terminated()
    def sleep(self,s): return self.thread.sleep(s)
    

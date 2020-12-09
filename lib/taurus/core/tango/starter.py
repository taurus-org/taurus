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

"""This module provides a very simple API for starting and killing device
servers

It is not a replacement of the Tango Starter Device Server since this is much
more limited in scope.
"""
from __future__ import print_function
from builtins import object

import os
import time
import subprocess
import PyTango
from taurus.core.util.log import Logger


__docformat__ = 'restructuredtext'

_log = Logger('Starter')


class Starter(object):
    '''Abstract class for managing (starting, stopping, registering and
    removing) a Tango Device Server.

    Derived classes should provide the methods for starting and stopping a
    device.
    '''

    def __init__(self, ds_name):
        '''
        :param ds_name: (str) Device Server name in the form "server/instance"
        '''
        self.ds_name = ds_name
        self.dserver_name = 'dserver/%s' % ds_name
        try:
            self.dserver = PyTango.DeviceProxy(self.dserver_name)
            self.serverExisted = True
        except PyTango.DevFailed:  # not registered?
            self.dserver = None
            self.serverExisted = False
        self._addedDevices = []

    def hardKill(self):
        raise NotImplementedError('hardKill method is mandatory')

    def terminate(self):
        raise NotImplementedError('terminate method is mandatory')

    def start(self):
        raise NotImplementedError('start method is mandatory')

    def stopDs(self, synch=True, hard_kill=False, wait_seconds=10):
        if hard_kill:
            _log.info('Hard killing server %s...' % self.ds_name)
            self.hardKill()
        else:
            _log.info('Stopping server %s...' % self.ds_name)
            self.terminate()
        if not synch:
            return
        for i in range(wait_seconds):
            _log.debug('Waiting for server %s to get stopped. Iteration: %d' %
                       (self.ds_name, i))
            if self.isRunning():
                time.sleep(1)
            else:
                ##############################################################
                # TODO: this workaround doesn't seem necessary (see isRunning)
                # time.sleep(3)
                ##############################################################
                _log.info('Server %s has been stopped' % self.ds_name)
                return
        _log.warning('Server %s did not stop within %d seconds' %
                     (self.ds_name, wait_seconds))

    def startDs(self, synch=True, wait_seconds=10):
        if self.isRunning():
            _log.warning('Server already running')
            return
        _log.info('Starting server %s...' % self.ds_name)
        self.start()
        if not synch:
            return
        for i in range(wait_seconds):
            _log.debug('Waiting for server %s to get started... %d' %
                       (self.ds_name, i))
            if self.isRunning():
                _log.info('Server %s has been started' % self.ds_name)
                ##############################################################
                # Workaround to avoid race conditions
                # TODO: Find root cause of race condition and fix
                _wait = float(os.environ.get('TAURUS_STARTER_WAIT', 0))
                if _wait:
                    _log.info('Waiting %g s after start' % _wait)
                    time.sleep(_wait)
                ##############################################################
                return
            else:
                time.sleep(1)
        _log.warning('Server %s did not start within %d seconds' %
                     (self.ds_name, wait_seconds))

    def addNewDevice(self, device, klass=None):
        """
        Register a device of this server in the DB (register the server if
        not present)
        e.g. to create Starter in an init script::

            addNewDevice('sys/tg_test/foobar', klass='TangoTest')

        :param klass: class name. If None passed, it defaults to the server
                      name (without instance name)
        """
        if device in self._addedDevices:
            _log.warning('%s already added. Skipping' % device)
            return
        if klass is None:
            klass = self.ds_name.split('/')[0]
        # in case the device is already defined, skipping...
        db = PyTango.Database()
        try:
            db.import_device(device)
            _log.warning('%s already exists. Skipping' % device)
            return
        except:
            pass
        # register the device,
        # in case the server did not exist before this will define it
        dev_info = PyTango.DbDevInfo()
        dev_info.name = device
        dev_info.klass = klass
        dev_info.server = self.ds_name
        db.add_device(dev_info)
        # create proxy to dserver
        self.dserver = PyTango.DeviceProxy(self.dserver_name)
        # keep track of added devices
        self._addedDevices.append(device)

    def cleanDb(self, force=False):
        '''removes devices which have been added by :meth:`addNewDevice`
        and then removes the server if it was registered by this starter
        (or, if force is True, it removes the server in any case)

        :param force: (bool) force removing of the Server even if it was
                      not registered within this starter
        '''
        for device in self._addedDevices:
            PyTango.Database().delete_device(device)
            _log.info('Deleted device %s' % device)
        if (self.serverExisted or len(self._addedDevices) == 0) and not force:
            msg = ('%s was not registered by this starter. Not removing. ' +
                   'Use %s.cleanDb(force=True) to force cleanup') % \
                (self.ds_name, self.__class__.__name__)
            _log.warning(msg)
        else:
            self.stopDs(hard_kill=True)
            PyTango.Database().delete_server(self.ds_name)
            _log.info('Deleted Server %s' % self.ds_name)

    def isRunning(self):
        # TODO: In case the sleeps in startDS and stopDS need to be re-added,
        #       we should study another implementation for this method.
        if self.dserver is None:
            return False
        try:
            self.dserver.ping()
        except PyTango.DevFailed:
            return False
        return True


class ProcessStarter(Starter):
    '''A :class:`Starter` which uses subprocess to start and stop a device
    server.
    '''

    def __init__(self, execname, ds_name):
        '''
        :param execname: (str) path to the executable to launch the server
        :param ds_name: (str) Device Server name in the form "server/instance"
        '''
        super(ProcessStarter, self).__init__(ds_name)
        self.ds_instance = ds_name.split('/')[1]
        self.exec_name = os.path.abspath(execname)
        self.process = None

    def start(self):
        dev_null = open(os.devnull, 'wb')
        args = [self.exec_name, self.ds_instance]
        self.process = subprocess.Popen(args, stdout=dev_null, stderr=dev_null)

    def terminate(self):
        if self.process:
            self.process.terminate()
        else:
            _log.warning('Process not started, cannot terminate it.')

    def hardKill(self):
        if self.process:
            self.process.kill()
        else:
            _log.warning('Process not started, cannot terminate it.')


if __name__ == '__main__':

    from taurus.test.resource import getResourcePath
    exe = getResourcePath('taurus.core.tango.test.res', 'TangoSchemeTest')
    s = ProcessStarter(exe, 'TangoSchemeTest/test_removeme')
    devname = 'testing/tangoschemetest/temp-1'
    s.addNewDevice(devname, klass='TangoSchemeTest')
    s.startDs()
    try:
        print('Is running:', s.isRunning())
        print("ping:", PyTango.DeviceProxy(devname).ping())
    except Exception as e:
        print(e)
    s.stopDs()
    s.cleanDb(force=False)


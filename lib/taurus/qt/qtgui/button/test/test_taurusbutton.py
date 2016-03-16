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


"""Unit tests for taurus.button"""


from taurus.external import unittest

from taurus.test import getResourcePath
from taurus.qt.qtgui.test import BaseWidgetTestCase, GenericWidgetTestCase
from taurus.qt.qtgui.button import TaurusCommandButton

# The following are Tango-centric imports.
# TODO: change them if/when TaurusCommandbuttongets generalized
from PyTango import CommunicationFailed
from taurus.core.tango.starter import ProcessStarter


class TaurusCommandButtonTest(GenericWidgetTestCase, unittest.TestCase):
    _klass = TaurusCommandButton
    _modelnames = ['sys/tg_test/1', None, 'sys/database/2', '']


class TaurusCommandButtonTest2(BaseWidgetTestCase, unittest.TestCase):

    _klass = TaurusCommandButton
    initkwargs = dict(command='TimeoutCmd')

    def setUp(self):
        '''
        Requisites:
         - instantiate the widget
         - make sure that the the timeout server is ready
        '''
        # Call base class setup (instantiate the widget,...)
        BaseWidgetTestCase.setUp(self)
        # get path to DS and executable
        timeoutExec = getResourcePath('taurus.qt.qtgui.button.test.res',
                                      'Timeout')
        # create starter for the Timeout server
        self._starter = ProcessStarter(timeoutExec, 'Timeout/unittest')
        # register timeoutserver  #TODO: guarantee that devname is not in use
        devname = 'unittests/timeout/temp-1'
        self._starter.addNewDevice(devname, klass='Timeout')
        # start Timeout server
        self._starter.startDs()

        # Configure the widget
        self._widget.setModel(devname)

    def tearDown(self):
        '''Stop the timeout server and undo changes to the database'''

        self._widget.setModel(None)
        # remove timeoutserver
        self._starter.cleanDb(force=True)

    def testTimeOutError(self):
        '''Check that the timeout property works'''
        # lets use commands that take at least 200ms in returning
        self._widget.setParameters([.2])
        # With a long timeout it should work...
        self._widget.setTimeout(10)
        ret = self._widget._onClicked()
        msg = 'expected return None when timeout >> command response time'
        self.assertIsNone(ret, msg)
        #...but with a shorter timeout we expect a timeout exception
        self._widget.setTimeout(.1)
        self.assertRaises(CommunicationFailed, self._widget._onClicked)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()

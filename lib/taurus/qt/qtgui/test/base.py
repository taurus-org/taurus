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


"""Utilities for creating generic tests for Taurus widgets"""

from builtins import range
from builtins import object
import time
import taurus.core
import unittest
from taurus.qt.qtgui.application import TaurusApplication


class BaseWidgetTestCase(object):
    '''
    DEPRECATED: use pytest-qt instead of this

    A base class for tests that need a widget instance

    To use it, simply inherit from BaseWidgetTestCase *and* unittest.TestCase
    and provide the following class members:

      - _klass (typeobject) the widget class to test (mandatory)
      - initargs (list) a list of arguments for the klass init method
                 (default=[])
      - initkwargs (dict) a dict of keyword arguments for the klass init method
                   (default={})
    '''
    _klass = None
    initargs = []
    initkwargs = {}

    def setUp(self):
        """
        Preconditions:

          - A TaurusApplication must be initialized.
          - The widget must be instantiated

        """
        from taurus.core.util import deprecated
        deprecated(dep="BaseWidgetTestCase", alt="pytest-qt", rel="4.6.5")
        raise unittest.SkipTest("*WidgetTestCase is deprecated. Use pytest-qt")

        unittest.TestCase.setUp(self)

        from taurus.core.util.log import _DEPRECATION_COUNT
        self._depCounter = _DEPRECATION_COUNT
        self._depCounter.clear()
        app = TaurusApplication.instance()
        if app is None:
            app = TaurusApplication([], cmd_line_parser=None)
        self._app = app

        if self._klass is not None:
            self._widget = self._klass(*self.initargs, **self.initkwargs)

    def assertMaxDeprecations(self, maximum, msg=None):
        """Assertion method that checks that the number of deprecations issued
        during the current test is equal to or below a given maximum

        :param maximum: (int) maximum number of deprecation warnings allowed
        """
        deps = self._depCounter.getTotal()
        if msg is None:
            msg = ('%d deprecation warnings issued (max=%d):\n%s' %
                   (deps, maximum, self._depCounter.pretty()))
        self.assertTrue(deps <= maximum, msg)

    def processEvents(self, repetitions=1, sleep=0):
         for i in range(repetitions):
            time.sleep(sleep)
            self._app.processEvents()


class GenericWidgetTestCase(BaseWidgetTestCase):
    '''
    DEPRECATED: use pytest-qt instead of this

    a base class for testing common cases of arbitrary Taurus widget classes

    To use it, simply inherit from GenericWidgetTestCase *and* unittest.TestCase
    and provide the following class members:

      - _klass (typeobject) the widget class to test (mandatory)
      - initargs (list) a list of arguments for the klass init method
                 (default=[])
      - initkwargs (dict) a dict of keyword arguments for the klass init method
                   (default={})
      - modelnames (list) a list of model names which the widget should be able
                   to handle (default=[])
    '''
    modelnames = []

    def setUp(self):
        """
        Preconditions:

          - Those from :class:`BaseWidgetTestCase`
          - A list of models corresponding to the modelnames list
            should be created without using the widget being tested
            (e.g. by using taurusManager.findObject()).
            None should be used as a placeholder when a model cannot be created
            for a given modelname.
        """
        from taurus.core.util import deprecated
        deprecated(
            dep="GenericWidgetTestCase",
            alt="test_set_models and pytest-qt",
            rel="4.6.5"
        )

        # Make sure the basics are taken care of (QApplication, etc)
        BaseWidgetTestCase.setUp(self)

        # construct a list of models corresponding to the test model names
        # provided by the widget
        taurusManager = taurus.core.TaurusManager()
        self._models = []
        for n in self.modelnames:
            if not n:
                # an empty string or None are "valid" modelnames which should
                # lead to a reset in the model
                self._models.append(None)
            else:
                try:
                    # note, an unsupported model name will result in a None,
                    # which will be caught later on
                    model = taurusManager.findObject(n)
                except:
                    model = None
                self._models.append(model)

    def test00_Instantiation(self):
        '''Check that the widget instantiates correctly'''
        self.assertIsInstance(self._widget, self._klass)
        self.assertMaxDeprecations(0)

    def test10_SetModelsSequentially(self):
        '''Check that we can set several models sequentially'''

        for name, model in zip(self.modelnames, self._models):
            self._widget.setModel(name)
            modelobj = self._widget.getModelObj()
            if model is None and name:
                # the modelname is not supported by the manager (we cannot test
                # it apart from the fact that setModel does not raise an
                # exception
                continue
            else:
                self.assertIs(modelobj, model,
                              'failed to set model "%s" for %s' %
                              (name, self._klass.__name__))
        self.assertMaxDeprecations(0)

#    def test10_ModelProperty(self):
#        pass


if __name__ == "__main__":
    from taurus.qt.qtgui.display import TaurusLabel

    class TaurusLabelTest(GenericWidgetTestCase, unittest.TestCase):
        _klass = TaurusLabel
        modelnames = ['sys/tg_test/1/wave', '', 'eval:1', None]

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TaurusLabelTest)
    unittest.TextTestRunner(descriptions=True, verbosity=2).run(suite)
    # unittest.main()
    # TaurusLabelTest().run()

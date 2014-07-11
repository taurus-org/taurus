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

"""Test for taurus.qt.qtgui.panel.taurusvalue"""

from taurus.external import unittest
from taurus.qt.qtgui.test import  BaseWidgetTestCase
from taurus.qt.qtgui.panel import TaurusValue 

class TestTaurusValue(BaseWidgetTestCase, unittest.TestCase):
    '''Specific test for the TaurusValue widget'''    
    _klass = TaurusValue

    def setUp(self):
        '''Do all what is done in BaseWidgetTestCase.setUp and also set a 
        model and show the widget'''
        
        #Make sure the basics are taken care of (QApplication, etc)
        BaseWidgetTestCase.setUp(self)
        self._widget.setModel('eval://1')
        self._widget.show()
 
    def tearDown(self):
        '''Set Model to None'''
        self._widget.setModel(None)
        unittest.TestCase.tearDown(self)
 
    def test_bug126(self):
        '''Verify that case is not lost when customizing a label (bug#126)'''
        w = self._widget
        label = 'MIXEDcase'
        w.setLabelConfig(label)
        self._app.processEvents() #required
        shownLabel = str(w.labelWidget().text())
        msg = 'Shown label ("%s") differs from set label ("%s")' % (shownLabel,
                                                                    label)
        self.assertEqual(label, shownLabel, msg)

if __name__ == '__main__':
    pass

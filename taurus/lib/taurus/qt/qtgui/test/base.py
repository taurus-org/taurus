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



"""Unit tests for Taurus"""
import unittest
import taurus.core


class GenericWidgetTestCase(object):
    '''a base class for testing common cases of arbitrary Taurus widget classes
    
    To use it, simply inherit from GenericWidgetTestCase *and* unittest.TestCase
    and provide the following class members:
    
      - _klass (typeobject) the widget class to test (mandatory)
      - initargs (list) a list of arguments for the klass init method (default=[])
      - initkwargs (dict) a dict of keyword arguments for the klass init method (default={})
      - modelnames (list) a list of model names which the widget should be able to handle (default=[])
    ''' 
    _klass = None
    initargs = []
    initkwargs = {}
    modelnames = []
    
    def setUp(self):
        if self._klass is None:
            self.skipTest('klass is None')
            return
        
        unittest.TestCase.setUp(self)
        
        from taurus.qt.qtgui.application import TaurusApplication
        if getattr(self, '_app', None) is None:
            self._app = TaurusApplication([])
        self._widget = self._klass(*self.initargs, **self.initkwargs)
               
        #construct a list of models corresponding to the test model names provided by the widget
        taurusManager = taurus.core.TaurusManager()
        self._models = []
        for n in self.modelnames:
            if not n: #an empty string or None are "valid" modelnames which should lead to a reset in the model
                self._models.append(None)
            else:
                try:
                    model = taurusManager.findObject(n) #note, an unsupported model name will result in a None, which will be caught later on
                except:
                    model = None
                self._models.append(model)
        
    def test00_Instantiation(self):
        '''check that the widget instantiates correctly'''
        self.assertIsInstance(self._widget, self._klass)
                
    def test10_SetModelsSequentially(self):
        '''check that we can set several models sequentially'''
#        if not any(self._models): 
#            self.skipTest('%s does not provide enough non-trivial models for testing') 
        for name,model in zip(self.modelnames, self._models):
            self._widget.setModel(name)
            modelobj = self._widget.getModelObj() #model obj is the one returned by the widget while model is the ine returned by the manager
            if model is None and name:
                continue #the modelname is not supported by the manager (we cannot test it apart from the fact that setModel does not raise an exception
            else:
                self.assertIs(modelobj, model,'failed to set model "%s" for %s'%(name, self._klass.__name__) )

#    def test10_ModelProperty(self):
#        pass



if __name__ == "__main__":
    from taurus.qt.qtgui.display  import TaurusLabel
       
    class TaurusLabelTest(GenericWidgetTestCase, unittest.TestCase):
        _klass = TaurusLabel
        modelnames = ['sys/tg_test/1/wave','', 'eval://1', None]
        
#     suite = unittest.defaultTestLoader.loadTestsFromTestCase(TaurusLabelTest)
#     unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()
    TaurusLabelTest().run()

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

"""Test for taurus.core.evaluation.test.test_evalfactory..."""

import re

import taurus
import unittest
from taurus.test import insertTest


@insertTest(helper_name='checkAttributeName', model='eval://1', oldstyle=True)
@insertTest(helper_name='checkAttributeName', model='a=2;a*3')
@insertTest(helper_name='checkAttributeName', model='1')
@insertTest(helper_name='checkAttributeID', model='eval://1', oldstyle=True)
@insertTest(helper_name='checkAttributeID', model='a=2;a*3')
@insertTest(helper_name='checkAttributeID', model='1')
@insertTest(helper_name='checkAttributeID', model='eval:1')
class EvaluationFactoryTestCase(unittest.TestCase):
    fragments = ['#', '#label', '#units']

    def setUp(self):
        self.f = taurus.Factory('eval')

    def convert2oldstyle(self, fragment):
        if fragment == '#':
            return '?configuration'
        return re.sub("#(?=.+)", "?configuration=", fragment)

    def checkAttributeID(self, model, oldstyle=False):
        '''Helper for test the attributes (by ID) when some different models
        of the same attribute are given (adding fragments in the models)
        '''
        attr = self.f.getAttribute(model)
        for fragment in self.fragments:
            if oldstyle:
                fragment = self.convert2oldstyle(fragment)
            attr2 = self.f.getAttribute(model + fragment)
            msg = '%s and %s has different id' % (attr.getFullName(),
                                                  attr2.getFullName())
            self.assertTrue(id(attr) == id(attr2), msg)

    def checkAttributeName(self, model, oldstyle=False):
        '''Helper for test the attribute names of the same attribute
        with different models (adding fragments in the models)
        '''
        attr = self.f.getAttribute(model)
        for fragment in self.fragments:
            if oldstyle:
                fragment = self.convert2oldstyle(fragment)
            attr2 = self.f.getAttribute(model + fragment)
            msg = '%s and %s has different ' % (attr.getFullName(),
                                                attr2.getFullName())
            self.assertTrue(attr.getFullName() == attr2.getFullName(),
                            msg + "fullname")
            self.assertTrue(attr.getNormalName() == attr2.getNormalName(),
                            msg + "normalname")
            self.assertTrue(attr.getSimpleName() == attr2.getSimpleName(),
                            msg + "simplename")

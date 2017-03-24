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
This module is used for the tests of custom evaluation devices.
"""

import os
from taurus.external.pint import Quantity


modattr = 'hello world'

class MyClass(object):

    _foo = Quantity(123, "m")


    def get_foo(self):
        return self._foo


    def set_foo(self, value):
        self._foo = value

    foo = property(get_foo, set_foo)

    @property
    def bar(self):
        return int(os.environ.get('__MYMOD_TEST_BAR', '321'))

    @bar.setter
    def set_bar(self, value):
        os.environ['__MYMOD_TEST_BAR'] = str(value)

    # bar = property(get_bar, set_bar)

    baz = 'hello'

    @property
    def float_ro(self):
        return 1.234

    @classmethod
    def classmeth(cls):
        return cls._foo


if __name__ == "__main__":
    # print bar, float_ro
    import taurus
    # a = taurus.Attribute('eval:@taurus.core.evaluation.test.res.mymod.*/foo')
    a = taurus.Attribute('eval:@taurus.core.evaluation.test.res.mymod.MyClass()/foo')

    print a.read()
    print a.range
    # a.write(99)
    print a.read()
    print
    print

    models = [
      # instance models
      'eval:@taurus.core.evaluation.test.res.mymod.MyClass()/foo',
      'eval:@taurus.core.evaluation.test.res.mymod.MyClass()/bar',
      'eval:@taurus.core.evaluation.test.res.mymod.MyClass()/baz',
      'eval:@taurus.core.evaluation.test.res.mymod.MyClass()/float_ro',
      'eval:@taurus.core.evaluation.test.res.mymod.MyClass()/__self__.__class__.__name__',

      # class models
      'eval:@taurus.core.evaluation.test.res.mymod.MyClass/_foo',
      #'eval:@taurus.core.evaluation.test.res.mymod.MyClass/classmeth()',  # <--fails

      # module models
      'eval:@taurus.core.evaluation.test.res.mymod.*/modattr',
      'eval:@taurus.core.evaluation.test.res.mymod.*/MyClass().foo',

    ]

    for m in models:
        print m
        a = taurus.Attribute(m)
        print "   -->", a.writable, a.read().rvalue


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

"""Test for taurus.core.util.codecs"""

#__all__ = []

__docformat__ = 'restructuredtext'

import copy
import unittest
from taurus.test import insertTest
from taurus.core.util.codecs import CodecFactory
import numpy


@insertTest(helper_name='encDec', cname='json', data=[1, 2, 3])
@insertTest(helper_name='encDec', cname='zip', data=b'foobar')
@insertTest(helper_name='encDec', cname='zip_utf8_json', data=[1, 2, 3])
@insertTest(helper_name='encDec', cname='videoimage',
            data=numpy.ones((2, 2), dtype='uint8'))
@insertTest(helper_name='encDec', cname='zip_null_zip_videoimage',
            data=numpy.ones((2, 2), dtype='uint8'))
@insertTest(helper_name='dec', cname='videoimage',
            data=b'VDEO\x00\x01\x00\x07\x00\x00\x00\x00\x00\x00\x00' +
            b'\x01\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00 ' +
            b'\x00\x00\x00\x00\x01\x01\x01\x01\x01\x01\x01\x01' +
            b'\x01\x01\x01\x01\x01\x01\x01\x01',
            expected=numpy.ones((2, 2, 3), dtype='uint8'))
class CodecTest(unittest.TestCase):
    '''TestCase for checking codecs'''

    def encDec(self, cname=None, data=None, expected=None):
        '''Check that data can be encoded-decoded properly'''
        if expected is None:
            expected = copy.deepcopy(data)
        _, enc = self.enc(cname=cname, data=data)
        self.dec(cname=cname, data=enc, expected=expected)

    def enc(self, cname=None, data=None, expected=None):
        '''Check that data can be encoded-decoded properly'''
        cf = CodecFactory()
        codec = cf.getCodec(cname)
        fmt, enc = codec.encode(('', data))
        if expected is not None:
            msg = ('Wrong data after encoding with %s:\n' +
                   ' -expected:%s\n -obtained:%s') % (cname, expected, enc)
            if numpy.isscalar(expected):
                equal = enc == expected
            else:
                equal = numpy.all(enc == expected)
            self.assertTrue(equal, msg)
        return fmt, enc

    def dec(self, cname=None, data=None, expected=None):
        '''Check that data can be encoded-decoded properly'''
        cf = CodecFactory()
        codec = cf.getCodec(cname)
        fmt, dec = codec.decode((cname, data))
        if expected is not None:
            msg = ('Wrong data after decoding with %s:\n' +
                   ' -expected:%s\n -obtained:%s') % (cname, expected, dec)
            if numpy.isscalar(expected):
                equal = dec == expected
            else:
                equal = numpy.all(dec == expected)
            self.assertTrue(equal, msg)
        return fmt, dec

if __name__ == '__main__':
    pass

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
This module contains a list of codecs for the DEV_ENCODED attribute type.
All codecs are based on the pair *format, data*. The format is a string
containing the codec signature and data is a sequence of bytes (string)
containing the encoded data.

This module contains a list of codecs capable of decoding several codings like
bz2, zip and json.

The :class:`CodecFactory` class allows you to get a codec object for a given
format and also to register new codecs.
The :class:`CodecPipeline` is a special codec that is able to code/decode a
sequence of codecs. This way you can have codecs 'inside' codecs.

Example::

    >>> from taurus.core.util.codecs import CodecFactory
    >>> cf = CodecFactory()
    >>> json_codec = cf.getCodec('json')
    >>> bz2_json_codec = cf.getCodec('bz2_json')
    >>> data = range(100000)
    >>> f1, enc_d1 = json_codec.encode(('', data))
    >>> f2, enc_d2 = bz2_json_codec.encode(('', data))
    >>> print len(enc_d1), len(enc_d2)
    688890 123511
    >>>
    >>> f1, dec_d1 = json_codec.decode((f1, enc_d1))
    >>> f2, dec_d2 = bz2_json_codec.decode((f2, enc_d2))

A Taurus related example::

    >>> # this example shows how to automatically get the data from a DEV_ENCODED attribute
    >>> import taurus
    >>> from taurus.core.util.codecs import CodecFactory
    >>> cf = CodecFactory()
    >>> devenc_attr = taurus.Attribute('a/b/c/devenc_attr')
    >>> v = devenc_attr.read()
    >>> codec = CodecFactory().getCodec(v.format)
    >>> f, d = codec.decode((v.format, v.value))
"""
from __future__ import absolute_import
from builtins import str, bytes

import copy

# need by VideoImageCodec
import struct
import sys
import numpy

from future.utils import (PY2, string_types)

from .singleton import Singleton
from .log import Logger
from .containers import CaselessDict

__all__ = ["Codec", "NullCodec", "ZIPCodec", "BZ2Codec", "JSONCodec",
           "Utf8Codec", "FunctionCodec", "PlotCodec", "CodecPipeline",
           "CodecFactory"]

__docformat__ = "restructuredtext"

if PY2:
    buffer_types = buffer, memoryview,
else:
    buffer_types = memoryview,


class Codec(Logger):
    """The base class for all codecs"""

    def __init__(self):
        """Constructor"""
        Logger.__init__(self, self.__class__.__name__)

    # TODO: similar code exists in encode and decode methods from different
    # codecs. It should be implemented in this base class 'Codec'.
    def encode(self, data, *args, **kwargs):
        """encodes the given data. This method is abstract an therefore must
        be implemented in the subclass.

        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object

        :raises: NotImplementedError"""
        raise NotImplementedError("encode cannot be called on abstract Codec")

    def decode(self, data, *args, **kwargs):
        """decodes the given data. This method is abstract an therefore must
        be implemented in the subclass.

        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object

        :raises: NotImplementedError"""
        raise NotImplementedError("decode cannot be called on abstract Codec")

    def __str__(self):
        return '%s()' % self.__class__.__name__

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class NullCodec(Codec):

    def encode(self, data, *args, **kwargs):
        """encodes with Null encoder. Just returns the given data

        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        format = 'null'
        if len(data[0]):
            format += '_%s' % data[0]
        return format, data[1]

    def decode(self, data, *args, **kwargs):
        """decodes with Null encoder. Just returns the given data

        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        if not data[0].startswith('null'):
            return data
        format = data[0].partition('_')[2]
        return format, data[1]


class ZIPCodec(Codec):
    """A codec able to encode/decode to/from gzip format. It uses the :mod:`zlib` module

    Example::

        >>> from taurus.core.util.codecs import CodecFactory

        >>> # first encode something
        >>> data = 100 * "Hello world\\n"
        >>> cf = CodecFactory()
        >>> codec = cf.getCodec('zip')
        >>> format, encoded_data = codec.encode(("", data))
        >>> print len(data), len(encoded_data)
        1200, 31
        >>> format, decoded_data = codec.decode((format, encoded_data))
        >>> print decoded_data[20]
        'Hello world\\nHello wo'"""

    def encode(self, data, *args, **kwargs):
        """encodes the given data to gzip bytes. The given data **must** be bytes

        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        import zlib
        format = 'zip'
        if len(data[0]):
            format += '_%s' % data[0]
        return format, zlib.compress(data[1])

    def decode(self, data, *args, **kwargs):
        """decodes the given data from a gzip bytes.

        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        import zlib
        if not data[0].startswith('zip'):
            return data
        format = data[0].partition('_')[2]
        return format, zlib.decompress(data[1])


class BZ2Codec(Codec):
    """A codec able to encode/decode to/from BZ2 format. It uses the :mod:`bz2` module

    Example::

        >>> from taurus.core.util.codecs import CodecFactory

        >>> # first encode something
        >>> data = 100 * "Hello world\\n"
        >>> cf = CodecFactory()
        >>> codec = cf.getCodec('bz2')
        >>> format, encoded_data = codec.encode(("", data))
        >>> print len(data), len(encoded_data)
        1200, 68
        >>> format, decoded_data = codec.decode((format, encoded_data))
        >>> print decoded_data[20]
        'Hello world\\nHello wo'"""

    def encode(self, data, *args, **kwargs):
        """encodes the given data to bz2 bytes. The given data **must** be bytes

        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        import bz2
        format = 'bz2'
        if len(data[0]):
            format += '_%s' % data[0]
        return format, bz2.compress(data[1])

    def decode(self, data, *args, **kwargs):
        """decodes the given data from bz2 bytes.

        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        import bz2
        if not data[0].startswith('bz2'):
            return data
        format = data[0].partition('_')[2]
        return format, bz2.decompress(data[1])


class PickleCodec(Codec):
    """A codec able to encode/decode to/from pickle format. It uses the
    :mod:`pickle` module.

    Example::

        >>> from taurus.core.util.codecs import CodecFactory

        >>> cf = CodecFactory()
        >>> codec = cf.getCodec('pickle')
        >>>
        >>> # first encode something
        >>> data = { 'hello' : 'world', 'goodbye' : 1000 }
        >>> format, encoded_data = codec.encode(("", data))
        >>>
        >>> # now decode it
        >>> format, decoded_data = codec.decode((format, encoded_data))
        >>> print decoded_data
        {'hello': 'world', 'goodbye': 1000}"""

    def encode(self, data, *args, **kwargs):
        """encodes the given data to pickle bytes. The given data **must** be
        a python object that :mod:`pickle` is able to convert.

        :param data: (sequence[str, obj]) a sequence of two elements where the
                     first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the
                 first item is the encoding format of the second item object"""
        import pickle
        format = 'pickle'
        if len(data[0]):
            format += '_%s' % data[0]
        # make it compact by default
        kwargs['protocol'] = kwargs.get('protocol', pickle.HIGHEST_PROTOCOL)
        return format, pickle.dumps(data[1], *args, **kwargs)

    def decode(self, data, *args, **kwargs):
        """decodes the given data from a pickle string.

        :param data: (sequence[str, obj]) a sequence of two elements where the
                     first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the
                 first item is the encoding format of the second item object"""
        import pickle
        if not data[0].startswith('pickle'):
            return data
        format = data[0].partition('_')[2]

        if isinstance(data[1], buffer_types):
            data = data[0], bytes(data[1])

        return format, pickle.loads(data[1])


class JSONCodec(Codec):
    """A codec able to encode/decode to/from json format. It uses the
    :mod:`json` module.

    Example::

        >>> from taurus.core.util.codecs import CodecFactory

        >>> cf = CodecFactory()
        >>> codec = cf.getCodec('json')
        >>>
        >>> # first encode something
        >>> data = { 'hello' : 'world', 'goodbye' : 1000 }
        >>> format, encoded_data = codec.encode(("", data))
        >>> print encoded_data
        '{"hello": "world", "goodbye": 1000}'
        >>>
        >>> # now decode it
        >>> format, decoded_data = codec.decode((format, encoded_data))
        >>> print decoded_data
        {'hello': 'world', 'goodbye': 1000}"""

    def encode(self, data, *args, **kwargs):
        """encodes the given data to a json string. The given data **must** be
        a python object that json is able to convert.

        :param data: (sequence[str, obj]) a sequence of two elements where the
                     first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the
                 first item is the encoding format of the second item object"""
        import json
        format = 'json'
        if len(data[0]):
            format += '_%s' % data[0]
        # make it compact by default
        kwargs['separators'] = kwargs.get('separators', (',', ':'))
        return format, json.dumps(data[1], *args, **kwargs)

    def decode(self, data, *args, **kwargs):
        """decodes the given data from a json string.

        :param data: (sequence[str, obj]) a sequence of two elements where the
                     first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the
                 first item is the encoding format of the second item object"""
        import json
        if not data[0].startswith('json'):
            return data
        format = data[0].partition('_')[2]

        ensure_ascii = kwargs.pop('ensure_ascii', False)

        if isinstance(data[1], buffer_types):
            data = data[0], str(data[1])
        
        data = json.loads(data[1])
        if ensure_ascii:
            data = self._transform_ascii(data)
        return format, data

    def _transform_ascii(self, data):
        if isinstance(data, string_types):
            return data.encode('utf-8')
        elif isinstance(data, dict):
            return self._transform_dict(data)
        elif isinstance(data, list):
            return self._transform_list(data)
        elif isinstance(data, tuple):
            return tuple(self._transform_list(data))
        else:
            return data

    def _transform_list(self, lst):
        return [self._transform_ascii(item) for item in lst]

    def _transform_dict(self, dct):
        newdict = {}
        for k, v in dct.items():
            newdict[self._transform_ascii(k)] = self._transform_ascii(v)
        return newdict


class Utf8Codec(Codec):
    """A codec able to encode/decode utf8 strings to/from bytes.
    Useful to adapt i/o encodings in a codec pipe.

    Example::

        >>> from taurus.core.util.codecs import CodecFactory

        >>> cf = CodecFactory()
        >>> codec = cf.getCodec('zip_utf8_json')
        >>>
        >>> # first encode something
        >>> data = { 'hello' : 'world', 'goodbye' : 1000 }
        >>> format, encoded_data = codec.encode(("", data))
        >>>
        >>> # now decode it
        >>> _, decoded_data = codec.decode((format, encoded_data))
        >>> print decoded_data
    """

    def encode(self, data, *args, **kwargs):
        """
        Encodes the given utf8 string to bytes.

        :param data: (sequence[str, obj]) a sequence of two elements where the
                     first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the
                 first item is the encoding format of the second item object
        """
        format = 'utf8'
        fmt, data = data
        if len(fmt):
            format += '_%s' % fmt
        return format, str(data).encode()

    def decode(self, data, *args, **kwargs):
        """decodes the given data from a bytes.

        :param data: (sequence[str, obj]) a sequence of two elements where the
                     first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the
                 first item is the encoding format of the second item object
        """
        fmt, data = data
        fmt = fmt.partition('_')[2]
        return fmt, bytes(data).decode()


class BSONCodec(Codec):
    """A codec able to encode/decode to/from bson format. It uses the
    :mod:`bson` module.

    Example::

        >>> from taurus.core.util.codecs import CodecFactory

        >>> cf = CodecFactory()
        >>> codec = cf.getCodec('bson')
        >>>
        >>> # first encode something
        >>> data = { 'hello' : 'world', 'goodbye' : 1000 }
        >>> format, encoded_data = codec.encode(("", data))
        >>>
        >>> # now decode it
        >>> _, decoded_data = codec.decode((format, encoded_data))
        >>> print decoded_data
        {'hello': 'world', 'goodbye': 1000}"""

    def encode(self, data, *args, **kwargs):
        """encodes the given data to a bson string. The given data **must** be
        a python object that bson is able to convert.

        :param data: (sequence[str, obj]) a sequence of two elements where the
                     first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the
                 first item is the encoding format of the second item object"""
        import bson
        format = 'bson'
        if len(data[0]):
            format += '_%s' % data[0]
        return format, bson.BSON.encode(data[1], *args, **kwargs)

    def decode(self, data, *args, **kwargs):
        """decodes the given data from a bson string.

        :param data: (sequence[str, obj]) a sequence of two elements where the
                     first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the
                 first item is the encoding format of the second item object"""
        import bson
        if not data[0].startswith('bson'):
            return data
        format = data[0].partition('_')[2]
        ensure_ascii = kwargs.pop('ensure_ascii', False)

        data = data[0], bson.BSON(data[1])

        data = self.decode(data[1])
        if ensure_ascii:
            data = self._transform_ascii(data)
        return format, data

    def _transform_ascii(self, data):
        if isinstance(data, string_types):
            return data.encode('utf-8')
        elif isinstance(data, dict):
            return self._transform_dict(data)
        elif isinstance(data, list):
            return self._transform_list(data)
        elif isinstance(data, tuple):
            return tuple(self._transform_list(data))
        else:
            return data

    def _transform_list(self, lst):
        return [self._transform_ascii(item) for item in lst]

    def _transform_dict(self, dct):
        newdict = {}
        for k, v in dct.items():
            newdict[self._transform_ascii(k)] = self._transform_ascii(v)
        return newdict


class FunctionCodec(Codec):
    """A generic function codec"""

    def __init__(self, func_name):
        Codec.__init__(self)
        self._func_name = func_name

    def encode(self, data, *args, **kwargs):
        format = self._func_name
        if len(data[0]):
            format += '_%s' % data[0]
        return format, {'type': self._func_name, 'data': data[1]}

    def decode(self, data, *args, **kwargs):
        if not data[0].startswith(self._func_name):
            return data
        format = data[0].partition('_')[2]
        return format, data[1]


class PlotCodec(FunctionCodec):
    """A specialization of the :class:`FunctionCodec` for plot function"""

    def __init__(self):
        FunctionCodec.__init__(self, 'plot')


class VideoImageCodec(Codec):
    """A codec able to encode/decode to/from LImA video_image format.

    Example::

        >>> from taurus.core.util.codecs import CodecFactory
        >>> import PyTango

        >>> #first get an image from a LImA device to decode
        >>> data = PyTango.DeviceProxy(ccdName).read_attribute('video_last_image').value
        >>> cf = CodecFactory()
        >>> codec = cf.getCodec('VIDEO_IMAGE')
        >>> format,decoded_data = codec.decode(data)
        >>> # encode it again to check
        >>> format, encoded_data = codec.encode(("",decoded_data))
        >>> #compare images excluding the header:
        >>> data[1][32:] == encoded_data[32:]
        >>> #The headers can be different in the frameNumber
        >>> struct.unpack('!IHHqiiHHHH',data[1][:32])
        (1447314767, 1, 0, 6868, 1294, 964, 0, 32, 0, 0)
        >>> struct.unpack('!IHHqiiHHHH',encoded_data[:32])
        (1447314767, 1, 0, -1, 1294, 964, 0, 32, 0, 0)
    """

    VIDEO_HEADER_FORMAT = '!IHHqiiHHHH'

    def encode(self, data, *args, **kwargs):
        """encodes the given data to a LImA's video_image. The given data **must** be an numpy.array

        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""

        # TODO: support encoding for colour imgage modes

        fmt = 'videoimage'
        if len(data[0]):
            fmt += '_%s' % data[0]
        # imgMode depends on numpy.array dtype
        imgMode = self.__getModeId(str(data[1].dtype))
        # frameNumber, unknown then -1
        height, width = data[1].shape
        header = self.__packHeader(imgMode, -1, width, height)
        buffer = data[1].tobytes()
        return fmt, header + buffer

    def decode(self, data, *args, **kwargs):
        """decodes the given data from a LImA's video_image.

        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""

        if data[0].startswith('VIDEO_IMAGE'):
            fixedformat = data[0].replace('VIDEO_IMAGE', 'videoimage')
            _, _, fmt = fixedformat.partition('_')
        elif data[0].startswith('videoimage'):
            _, _, fmt = data[0].partition('_')
        else:
            return data
        header = self.__unpackHeader(
            data[1][:struct.calcsize(self.VIDEO_HEADER_FORMAT)])

        imgBuffer = data[1][struct.calcsize(self.VIDEO_HEADER_FORMAT):]
        dtype = self.__getDtypeId(header['imageMode'])

        if header['imageMode'] == 6:
            # RGB24, 3 bytes per pixel
            rgba = numpy.frombuffer(imgBuffer, dtype)
            bbuf = rgba[0::3]
            gbuf = rgba[1::3]
            rbuf = rgba[2::3]
            r = rbuf.reshape(header['height'], header['width'])
            g = gbuf.reshape(header['height'], header['width'])
            b = bbuf.reshape(header['height'], header['width'])
            img2D = numpy.dstack((r, g, b))

        elif header['imageMode'] == 7:
            # RGBA 4 bytes per pixel
            rgba = numpy.frombuffer(imgBuffer, dtype)
            bbuf = rgba[0::4]
            gbuf = rgba[1::4]
            rbuf = rgba[2::4]
            #abuf = rgba[3::4]
            r = rbuf.reshape(header['height'], header['width'])
            g = gbuf.reshape(header['height'], header['width'])
            b = bbuf.reshape(header['height'], header['width'])
            #a = abuf.reshape(header['height'],header['width'])
            img2D = numpy.dstack((r, g, b))

        elif header['imageMode'] == 17:
            # YUV444 3 bytes per pixel
            yuv = numpy.frombuffer(imgBuffer, dtype)
            y = yuv[0::3]
            u = yuv[1::3]
            v = yuv[2::3]

            rbuff, gbuff, bbuff = self.__yuv2rgb(y, u, v)

            # Shape buffers to image size
            r = rbuff.reshape(header['height'], header['width'])
            g = gbuff.reshape(header['height'], header['width'])
            b = bbuff.reshape(header['height'], header['width'])

            # Build the RGB image
            img2D = numpy.dstack((r, g, b))

        elif header['imageMode'] == 16:
            # YUV422 4 bytes per 2 pixels
            yuv = numpy.frombuffer(imgBuffer, dtype)
            u = yuv[0::4]
            y1 = yuv[1::4]
            v = yuv[2::4]
            y2 = yuv[3::4]

            r1, g1, b1 = self.__yuv2rgb(y1, u, v)
            r2, g2, b2 = self.__yuv2rgb(y2, u, v)

            # Create RGB buffers
            rbuff = numpy.dstack((r1, r2)).reshape(
                header['height'] * header['width'])
            gbuff = numpy.dstack((g1, g2)).reshape(
                header['height'] * header['width'])
            bbuff = numpy.dstack((b1, b2)).reshape(
                header['height'] * header['width'])

            # Shape buffers to image size
            r = rbuff.reshape(header['height'], header['width'])
            g = gbuff.reshape(header['height'], header['width'])
            b = bbuff.reshape(header['height'], header['width'])

            # Build the RGB image
            img2D = numpy.dstack((r, g, b))

        elif header['imageMode'] == 15:
            # YUV411 6 bytes per 4 pixels
            yuv = numpy.frombuffer(imgBuffer, dtype)
            u = yuv[0::6]
            y1 = yuv[1::6]
            y2 = yuv[2::6]
            v = yuv[3::6]
            y3 = yuv[4::6]
            y4 = yuv[5::6]

            r1, g1, b1 = self.__yuv2rgb(y1, u, v)
            r2, g2, b2 = self.__yuv2rgb(y2, u, v)
            r3, g3, b3 = self.__yuv2rgb(y3, u, v)
            r4, g4, b4 = self.__yuv2rgb(y4, u, v)

            # Create RGB buffers
            rbuff = numpy.dstack((r1, r2, r3, r4)).reshape(
                header['height'] * header['width'])
            gbuff = numpy.dstack((g1, g2, g3, g4)).reshape(
                header['height'] * header['width'])
            bbuff = numpy.dstack((b1, b2, b3, b4)).reshape(
                header['height'] * header['width'])

            # Shape buffers to image size
            r = rbuff.reshape(header['height'], header['width'])
            g = gbuff.reshape(header['height'], header['width'])
            b = bbuff.reshape(header['height'], header['width'])

            img2D = numpy.dstack((r, g, b))

        else:
            img1D = numpy.frombuffer(imgBuffer, dtype)
            img2D = img1D.reshape(header['height'], header['width'])

        return fmt, img2D

    def __yuv2rgb(self, y, u, v):
        '''YUV444 to RGB888 conversion'''
        Cr = v - 128.0
        Cb = u - 128.0

        R = y + 1.402 * Cr
        G = y - 0.344 * Cb - 0.714 * Cr
        B = y + 1.772 * Cb

        return (numpy.clip(R, 0, 255), numpy.clip(G, 0, 255), numpy.clip(B, 0, 255))

    def __unpackHeader(self, header):
        h = struct.unpack(self.VIDEO_HEADER_FORMAT, header)
        headerDict = {}
        headerDict['magic'] = h[0]
        headerDict['headerVersion'] = h[1]
        headerDict['imageMode'] = h[2]
        headerDict['frameNumber'] = h[3]
        headerDict['width'] = h[4]
        headerDict['height'] = h[5]
        headerDict['endianness'] = h[6]
        headerDict['headerSize'] = h[7]
        headerDict['padding'] = h[8:]
        return headerDict

    def __packHeader(self, imgMode, frameNumber, width, height):
        magic = 0x5644454f
        version = 1
        endian = 0 if sys.byteorder == 'little' else 1
        hsize = struct.calcsize(self.VIDEO_HEADER_FORMAT)
        return struct.pack(self.VIDEO_HEADER_FORMAT,
                           magic,
                           version,
                           imgMode,
                           frameNumber,
                           width,
                           height,
                           endian,
                           hsize,
                           0, 0)  # padding

    def __getModeId(self, mode):
        return {  # when encode
            'uint8': 0,  # Core.Y8,
            'uint16': 1,  # Core.Y16,
            'uint32': 2,  # Core.Y32,
            'uint64': 3,  # Core.Y64,
            # when decode
            'Y8': 0,  # Core.Y8,
            'Y16': 1,  # Core.Y16,
            'Y32': 2,  # Core.Y32,
            'Y64': 3,  # Core.Y64,
            # TODO: other modes
            #'RGB555'     : 4,#Core.RGB555,
            #'RGB565'     : 5,#Core.RGB565,
            'RGB24': 6,  # Core.RGB24,
            'RGB32': 7,  # Core.RGB32,
            #'BGR24'      : 8,#Core.BGR24,
            #'BGR32'      : 9,#Core.BGR32,
            #'BAYER RG8'  : 10,#Core.BAYER_RG8,
            #'BAYER RG16' : 11,#Core.BAYER_RG16,
            #'BAYER BG8'  : 12,#Core.BAYER_BG8,
            #'BAYER BG16' : 13,#Core.BAYER_BG16,
            #'I420'       : 14,#Core.I420,
            #'YUV411'     : 15,#Core.YUV411,
            'YUV422': 16,  # Core.YUV422,
            #'YUV444'     : 17,#Core.YUV444
        }[mode]

    def __getFormatId(self, mode):
        return {0: 'B',
                1: 'H',
                2: 'I',
                3: 'L',
                #'RGB555'     : Core.RGB555,
                #'RGB565'     : Core.RGB565,
                6: 'RGB24',  # Core.RGB24,
                7: 'RGB32',  # Core.RGB32,
                # 8     : 'BGR24',#Core.BGR24,
                #'BGR32'      : Core.BGR32,
                #'BAYER RG8'  : Core.BAYER_RG8,
                #'BAYER RG16' : Core.BAYER_RG16,
                #'BAYER BG8'  : Core.BAYER_BG8,
                #'BAYER BG16' : Core.BAYER_BG16,
                #'I420'       : Core.I420,
                #'YUV411'     : Core.YUV411,
                16: 'YUV422',  # Core.YUV422,
                #'YUV444'     : Core.YUV444
                }[mode]

    def __getDtypeId(self, mode):
        return {0: 'uint8',
                1: 'uint16',
                2: 'uint32',
                3: 'uint64',
                #'RGB555'     : Core.RGB555,
                #'RGB565'     : Core.RGB565,
                6: 'uint8',  # Core.RGB24,
                7: 'uint8',  # Core.RGB32,
                #'BGR24'      : Core.BGR24,
                #'BGR32'      : Core.BGR32,
                #'BAYER RG8'  : Core.BAYER_RG8,
                #'BAYER RG16' : Core.BAYER_RG16,
                #'BAYER BG8'  : Core.BAYER_BG8,
                #'BAYER BG16' : Core.BAYER_BG16,
                #'I420'       : Core.I420,
                #'YUV411'     : Core.YUV411,
                16: 'uint8',  # Core.YUV422,
                #'YUV444'     : Core.YUV444
                }[mode]


class CodecPipeline(Codec, list):
    """The codec class used when encoding/decoding data with multiple encoders

    Example usage::

        >>> from taurus.core.util.codecs import CodecPipeline

        >>> data = range(100000)
        >>> codec = CodecPipeline('bz2_json')
        >>> format, encoded_data = codec.encode(("", data))

        # decode it
        format, decoded_data = codec.decode((format, encoded_data))
        print decoded_data"""

    def __init__(self, format):
        """Constructor. The CodecPipeline object will be created using
        the :class:`CodecFactory` to search for format(s) given in the format
        parameter.

        :param format: (str) a string representing the format."""

        Codec.__init__(self)
        list.__init__(self)

        f = CodecFactory()
        for i in format.split('_'):
            codec = f.getCodec(i)
            self.debug("Appending %s => %s" % (i, codec))
            if codec is None:
                raise TypeError(
                    'Unsupported codec %s (namely %s)' % (format, i))
            self.append(codec)
        self.debug("Done")

    def encode(self, data, *args, **kwargs):
        """encodes the given data.

        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        for codec in reversed(self):
            data = codec.encode(data, *args, **kwargs)
        return data

    def decode(self, data, *args, **kwargs):
        """decodes the given data.

        :param data: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object

        :return: (sequence[str, obj]) a sequence of two elements where the first item is the encoding format of the second item object"""
        for codec in self:
            data = codec.decode(data, *args, **kwargs)
        return data


class CodecFactory(Singleton, Logger):
    """The singleton CodecFactory class.

    To get the singleton object do::

        from taurus.core.util.codecs import CodecFactory
        f = CodecFactory()

    The :class:`CodecFactory` class allows you to get a codec object for a given
    format and also to register new codecs.
    The :class:`CodecPipeline` is a special codec that is able to code/decode a
    sequence of codecs. This way you can have codecs 'inside' codecs.

    Example::

        >>> from taurus.core.util.codecs import CodecFactory
        >>> cf = CodecFactory()
        >>> json_codec = cf.getCodec('json')
        >>> bz2_json_codec = cf.getCodec('bz2_json')
        >>> data = range(100000)
        >>> f1, enc_d1 = json_codec.encode(('', data))
        >>> f2, enc_d2 = bz2_json_codec.encode(('', data))
        >>> print len(enc_d1), len(enc_d2)
        688890 123511
        >>>
        >>> f1, dec_d1 = json_codec.decode((f1, enc_d1))
        >>> f2, dec_d2 = bz2_json_codec.decode((f2, enc_d2))

    A Taurus related example::

        >>> # this example shows how to automatically get the data from a DEV_ENCODED attribute
        >>> import taurus
        >>> from taurus.core.util.codecs import CodecFactory
        >>> cf = CodecFactory()
        >>> devenc_attr = taurus.Attribute('a/b/c/devenc_attr')
        >>> v = devenc_attr.read()
        >>> codec = CodecFactory().getCodec(v.format)
        >>> f, d = codec.decode((v.format, v.value))
    """

    #: Default minimum map of registered codecs
    CODEC_MAP = CaselessDict({
        'json': JSONCodec,
        'utf8': Utf8Codec,
        'bson': BSONCodec,
        'bz2': BZ2Codec,
        'zip': ZIPCodec,
        'pickle': PickleCodec,
        'plot': PlotCodec,
        'VIDEO_IMAGE': VideoImageCodec,  # deprecated
        'videoimage': VideoImageCodec,
        'null': NullCodec,
        'none': NullCodec,
        '': NullCodec})

    def __init__(self):
        """ Initialization. Nothing to be done here for now."""
        pass

    def init(self, *args, **kwargs):
        """Singleton instance initialization."""
        name = self.__class__.__name__
        self.call__init__(Logger, name)

        self._codec_klasses = copy.copy(CodecFactory.CODEC_MAP)

        # dict<str, Codec>
        # where:
        #  - key is the codec format
        #  - value is the codec object that supports the format
        self._codecs = CaselessDict()

    def registerCodec(self, format, klass):
        """Registers a new codec. If a codec already exists for the given format
        it is removed.

        :param format: (str) the codec id
        :param klass: (Codec class) the class that handles the format"""
        self._codec_klasses[format] = klass

        # del old codec if exists
        if format in self._codecs:
            del self._codecs[format]

    def unregisterCodec(self, format):
        """Unregisters the given format. If the format does not exist an exception
        is thrown.

        :param format: (str) the codec id

        :raises: KeyError"""
        if format in self._codec_klasses:
            del self._codec_klasses[format]

        if format in self._codecs:
            del self._codecs[format]

    def getCodec(self, format):
        """Returns the codec object for the given format or None if no suitable
        codec is found

        :param format: (str) the codec id

        :return: (Codec or None) the codec object for the given format"""
        codec = self._codecs.get(format)
        if codec is None:
            codec = self._getNewCodec(format)
            if not codec is None:
                self._codecs[format] = codec
        return codec

    def _getNewCodec(self, format):
        klass = self._codec_klasses.get(format)
        if not klass is None:
            ret = klass()
        else:
            try:
                ret = CodecPipeline(format)
            except:
                ret = self._codec_klasses.get('')()
        return ret

    def decode(self, data, *args, **kwargs):
        while len(data[0]):
            data = self.getCodec(data[0]).decode(data, *args, **kwargs)
        return data[1]

    def encode(self, format, data, *args, **kwargs):
        return self.getCodec(format).encode(data, *args, **kwargs)

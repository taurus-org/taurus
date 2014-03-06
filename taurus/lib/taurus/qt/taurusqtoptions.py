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

"""The taurus.qt options submodule. It contains qt-specific part of taurus"""

__all__ = ["QT_API", "QT_USE_API2", "QT_API_PYQT", "QT_API_PYSIDE"]

__docformat__ = 'restructuredtext'

import os
import imp

QT_API_PYQT = 'pyqt'
QT_API_PYSIDE = 'pyside'
QT_USE_API2 = True


def get_logger():
    import taurus.core.util.log
    return taurus.core.util.log.Logger('TaurusQt')


def prepare_pyqt():
    if not QT_USE_API2:
        return
    # For PySide compatibility, use the new-style string API that
    # automatically converts QStrings to Unicode Python strings. Also,
    # automatically unpack QVariants to their underlying objects.
    import sip
    if sip.SIP_VERSION >= 0x040900:
        try:
            sip.setapi("QString", 2)
        except ValueError, e:
            get_logger().info("SIP: %s", e)
        try:
            sip.setapi('QVariant', 2)
        except ValueError, e:
            get_logger().info("SIP: %s", e)
    else:
        sip_ver = sip.SIP_VERSION_STR
        get_logger().debug("Using old SIP %s (advised >= 4.9)", sip_ver)


def prepare_pyside():
    pass

QT_APIs = {
    QT_API_PYQT: ('PyQt4', prepare_pyqt),
    QT_API_PYSIDE: ('PySide', prepare_pyside),
}

QT_PREFERED_APIs = QT_API_PYQT, QT_API_PYSIDE
#QT_PREFERED_APIs = (QT_API_PYSIDE,)

def init():
    # Select Qt binding, using the QT_API environment variable if available.
    ret_api = os.environ.get('QT_API')
    if ret_api is None:
        for api in QT_PREFERED_APIs:
            try:
                imp.find_module(QT_APIs[api][0])
                ret_api = api
                if ret_api is not None:
                    break
            except ImportError:
                pass
        if ret_api is None:
            raise ImportError('No Qt API available (known APIs : %s)'
                              % ", ".join(QT_PREFERED_APIs))

    prepare = QT_APIs[ret_api][1]
    prepare()
    return ret_api

QT_API = init()
get_logger().info('Using "%s" as Qt python binding', QT_API)

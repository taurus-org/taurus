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

"""This module provides widgets that display the database in a tree format"""

__all__ = [
    'getPixmap',
    'getIcon',
    'getThemePixmap',
    'getThemeIcon',
    'getThemeMembers',
    # the following are actually from taurus.qt.qtgui.icon
    'getStandardIcon',
    'getElementTypeToolTip',
    'getElementTypeSize',
    'getElementTypeIcon',
    'getElementTypeIconName',
    'getElementTypePixmap',
    'getDevStateToolTip',
    'getDevStateIcon',
    'getDevStatePixmap',]

__docformat__ = 'restructuredtext'

import os

from taurus.external.qt import Qt

from taurus.core.util.log import (deprecated, taurus4_deprecation,
                                  deprecation_decorator)

from taurus.qt.qtgui.icon import *


@deprecation_decorator(alt='QIcon.hasThemeIcon to test individual names',
                       rel='4.0')
def getThemeMembers():
    """Returns the current icon theme elements

    .. note:: Since its depredation, it returns an empty dict (there is no
    reasonable way of introspecting the list of available icon names).
    Alternatively Just test a given name using

    :return: the current icon theme elements in a dictionary where each key is
             a group name and the value is a sequence of theme icon name.
    :rtype: dict<str,seq<str>>"""
    return {}


def getPixmap(key, size=None):
    # handle resource syntax (deprecated)
    if key.startswith(':'):
        head, tail = os.path.split(key[1:])
        # logos used to be in the resource root. Now they are in 'logos'
        prefix = sanitizePrefix(head or 'logos')
        alt = 'getCachedPixmap("%s:%s [, size]")' % (prefix, tail)
        ret = getCachedPixmap('%s:%s' % (prefix, tail), size)
    deprecated(dep='getPixmap("%s" [, size])' % key, alt=alt, rel='4.0')
    return ret


def getIcon(key):
    """Returns a PyQt4.QtGui.QIcon object for the given key. It supports QDir's
    searchPath prefixes (see :meth:`QDir.setSearchPaths`).
    Note that taurus.qt.qtgui.resource already sets several search paths based
    on .path files

    :param key: (str) the pixmap file name. (optionally with a prefix)

    :return: (PyQt4.QtGui.QIcon) a PyQt4.QtGui.QIcon for the given key"""

    # handle resource syntax (deprecated)
    if key.startswith(':'):
        head, tail = os.path.split(key[1:])
        # logos used to be in the resource root. Now they are in 'logos'
        prefix = sanitizePrefix(head or 'logos')
        alt = 'Qt.QIcon("%s:%s")' % (prefix, tail)
        ret = Qt.QIcon('%s:%s' % (prefix, tail))
    elif not Qt.QFile.exists(key) and Qt.QIcon.hasThemeIcon(key):
        alt = 'QIcon.fromTheme("%s")' % key
        ret = Qt.QIcon.fromTheme(key)
    else:
        alt = 'QIcon("%s")' % key
        ret = Qt.QIcon(key)
    deprecated(dep='getIcon("%s")' % key, alt=alt, rel='4.0')
    return ret


@deprecation_decorator(alt='QIcon.fromTheme(key).pixmap(size, size)', rel='4.0')
def getThemePixmap(key, size=48):
    """Returns a PyQt4.QtGui.QPixmap object for the given key and size.
    Key should be a valid theme icon key. See :meth:`PyQt4.QIcon.fromTheme`.

    Note that if the OS does not define a theme, taurus.qt.qtgui.resource will
    use the bundled 'Tango' icons theme. See:
    `Tango Icon Library <http://tango.freedesktop.org/Tango_Icon_Library>`_.

    If the key cannot be found, it will return a null content Pixmap.

    :param key: (str) a string with the pixmap theme key (ex.: 'folder_open')
    :param size: (int) the pixmap size in pixels (will get a square pixmap).
                 Default size=48

    :return: (PyQt4.QtGui.QPixmap)
    """
    return Qt.QIcon.fromTheme(key).pixmap(size, size)


@deprecation_decorator(alt='QIcon.fromTheme', rel='4.0')
def getThemeIcon(key):
    """Returns the theme icon corresponding to the given key.
    Key should be a valid theme icon key. See :meth:`PyQt4.QIcon.fromTheme`.

    Note that if the OS does not define a theme, taurus.qt.qtgui.resource will
    use the bundled 'Tango' icons theme. See:
    `Tango Icon Library <http://tango.freedesktop.org/Tango_Icon_Library>`_.

    :param key: (str) a string with the icon theme key (e.g.: 'folder_open')

    :return: (PyQt4.QtGui.QIcon) a PyQt4.QtGui.QIcon for the given theme key
    """
    return Qt.QIcon.fromTheme(key)


@taurus4_deprecation(alt='getDevStateToolTip')
def getSWDevHealthToolTip(state):
    return getDevStateToolTip(state)


@taurus4_deprecation(alt='getDevStateIcon')
def getSWDevHealthIcon(state, fallback=None):
    return getDevStateIcon(state, fallback=fallback)


@taurus4_deprecation(alt='getDevStatePixmap')
def getSWDevHealthPixmap(state, fallback=None):
    return getDevStatePixmap(state, fallback=fallback)




if __name__ == '__main__':

    import sys
    from taurus.qt.qtgui.application import TaurusApplication

    app = TaurusApplication(cmd_line_parser=None)



    themekey = 'computer'
    b = Qt.QIcon.fromTheme(themekey)

    icons = [

        getIcon('actions:edit-cut.svg'),
        getIcon(':/actions/edit-cut.svg'),

        getIcon(":/apps/preferences-system-session.svg"),
        getIcon(":/designer/devs_tree.png"),

        getIcon(":/actions/process-stop.svg"), # from tango-icons/actions
        getIcon(":/actions/add.svg"), # from rrze-icons/actions
        getIcon(":/actions/stop.svg"), # from extra-icons/actions

        getIcon(":taurus.svg"),
        getIcon("computer"), # theme Icon via getIcon
        getThemeIcon("computer"), # theme Icon via getThemeIcon
        ]

    w = Qt.QWidget()
    l = Qt.QVBoxLayout()
    w.setLayout(l)
    for icon in icons:
        button = Qt.QPushButton(icon, 'kk')
        l.addWidget(button)

    w.show()

    sys.exit(app.exec_())

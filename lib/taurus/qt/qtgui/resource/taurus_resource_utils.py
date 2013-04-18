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

"""This module provides widgets that display the database in a tree format"""

__all__ = ['getPixmap', 'getThemePixmap', 'getIcon', 'getThemeIcon', 'getStandardIcon',
           'getElementTypeToolTip', 'getElementTypeIconName', 'getElementTypeIcon',
           'getElementTypePixmap', 'getElementTypeSize',
           'getSWDevHealthToolTip', 'getSWDevHealthIcon', 'getSWDevHealthPixmap',
           'getThemeMembers' ]

__docformat__ = 'restructuredtext'

import os

from taurus.qt import Qt

from taurus.core.taurusbasetypes import TaurusElementType, TaurusSWDevHealth
from taurus.core.util.log import Logger

__LOGGER = Logger(__name__)

ElemType = TaurusElementType
DevHealth = TaurusSWDevHealth
Size = Qt.QSize

__INITIALIZED = False
# Theme capacity was only added in Qt 4.6
__THEME_CAPACITY = hasattr(Qt.QIcon, "fromTheme")
# Uncomment the following line to force NOT to use OS theme.
#__THEME_CAPACITY = False 

__THEME_MEMBERS = {}

# Default width, height and QSize constants
__DW = 70
__DH = 24

__DQS = Size(__DW, __DH)
__1DQS = __DQS
__2DQS = Size(2*__DW, __DH)
__3DQS = Size(3*__DW, __DH)

def __init():
    global __INITIALIZED
    global __THEME_MEMBERS
    
    if __INITIALIZED: return
        
    #register only the tango-icons rcc files (and initialize the THEME_MEMBERS)
    res_dir = os.path.dirname(os.path.abspath(__file__))
    Qt.QDir.addSearchPath("resource", res_dir)
    prefix = 'qrc_tango_icons_'
    suffix = '.rcc'
    lp, ls = len(prefix),len(suffix)
    theme_members = {}
    other_rcc_files = []
    for f in os.listdir(res_dir):
        if f.endswith(suffix):
            if f.startswith(prefix):
                if Qt.QResource.registerResource("resource:" + f):
                    d = f[lp:-ls]
                    theme_members[d] = [str(e)[:-4] for e in Qt.QDir(":%s"%d).entryList() if str(e).endswith('.svg')] 
                else:
                    __LOGGER.info("Failed to load resource %s" % f)
            else:
                other_rcc_files.append(f) #we remember these and will register later
    __THEME_MEMBERS = theme_members
    
    #register the rest of the resource files
    for f in other_rcc_files:
        if not Qt.QResource.registerResource("resource:" + f):
            __LOGGER.info("Failed to load resource %s" % f)
    
    __INITIALIZED = True

__init()

def getThemeMembers():
    """Returns the current icon theme elements
    
    :return: the current icon theme elements in a dictionary where each key is
             a group name and the value is a sequence of theme icon name.
    :rtype: dict<str,seq<str>>"""
    global __THEME_MEMBERS
    return __THEME_MEMBERS

def getPixmap(key, size=None):
    """Returns a PyQt4.QtGui.QPixmap object for the given key and size
    
    :param key: (str) a string with the pixmap resource key (ex.: ':/status/folder_open.svg')
    :param size: (int) the pixmap size in pixels (will get a square pixmap). Default is None
                 meaning it will return the original size
    
    :return: (PyQt4.QtGui.QPixmap) a PyQt4.QtGui.QPixmap for the given key and size"""
    
    name = key
    if size is not None:
        key = key + "_%sx%s" % (size, size)
    pm = Qt.QPixmapCache.find(key)
    if pm is None:
        pm = Qt.QPixmap(name)
        if size is not None:
            pm = pm.scaled(size, size, Qt.Qt.KeepAspectRatio, Qt.Qt.SmoothTransformation)
        Qt.QPixmapCache.insert(key, pm)
    return Qt.QPixmap(pm)

def getIcon(key):
    """Returns a PyQt4.QtGui.QIcon object for the given key
    
    :param key: (str) a string with the pixmap resource key (ex.: ':/status/folder_open.svg')
    
    :return: (PyQt4.QtGui.QIcon) a PyQt4.QtGui.QIcon for the given key"""
    if key.startswith(':'):
        return Qt.QIcon(key)
    return getThemeIcon(key)

def getThemePixmap(key, size=None):
    """Returns a PyQt4.QtGui.QPixmap object for the given key and size. Key should be a valid theme
    key. See `Icon Naming Specification <http://standards.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html>`_
    for the list of valid theme keys.
    
    If theme is not supported by Qt (version < 4.6) or by the OS, the method will return a
    theme pixmap from the `Tango Icon Library <http://tango.freedesktop.org/Tango_Icon_Library>`_.
    
    If the key cannot be found, it will return a null content Pixmap.
    
    :param key: (str) a string with the pixmap theme key (ex.: 'folder_open')
    :param size: (int) the pixmap size in pixels (will get a square pixmap). Default is None
                 meaning it will return the original size
    
    :return: (PyQt4.QtGui.QPixmap) a PyQt4.QtGui.QPixmap for the given key and size"""

    global __THEME_CAPACITY
    global __LOGGER
    if __THEME_CAPACITY:
        if Qt.QIcon.hasThemeIcon(key):
            size = size or 48
            return Qt.QIcon.fromTheme(key).pixmap(size, size)
        else:
            __LOGGER.debug('Theme pixmap "%s" not supported. Trying to provide a fallback...',key)
    for member, items in getThemeMembers().items():
        if not key in items: continue
        return getPixmap(":/%s/%s.svg" % (member, key), size)
    __LOGGER.debug('Theme pixmap "%s" not supported.', key)
    return Qt.QPixmap()

def getThemeIcon(key):
    """Returns a PyQt4.QtGui.QIcon object for the given key. Key should be a valid theme key. See
    `Icon Naming Specification <http://standards.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html>`_
    for the list of valid theme keys.
    
    If theme is not supported by Qt (version < 4.6) or by the OS, the method will return a
    theme icon from the `Tango Icon Library <http://tango.freedesktop.org/Tango_Icon_Library>`_.
    
    If the key cannot be found, it will return a null content QIcon.
    
    :param key: (str) a string with the icon theme key (ex.: 'folder_open')
    
    :return: (PyQt4.QtGui.QIcon) a PyQt4.QtGui.QIcon for the given key"""

    global __THEME_CAPACITY
    global __LOGGER
    if __THEME_CAPACITY:
        if Qt.QIcon.hasThemeIcon(key):
            return Qt.QIcon.fromTheme(key)
        else:
            __LOGGER.debug('Theme icon "%s" not supported. Trying to provide a fallback...',key)
            __LOGGER.stack()
    for member, items in getThemeMembers().items():
        if not key in items: continue
        return Qt.QIcon(":/%s/%s.svg" % (member, key))
    __LOGGER.debug('Theme icon "%s" not supported.', key)
    return Qt.QIcon()

def getStandardIcon(key, widget=None):
    """Returns a PyQt4.QtGui.QIcon object for the given key. Key should be a 
    QStyle.StandardPixmap enumeration member. The widget argument is optional 
    and can also be used to aid the determination of the icon.
    
    :param key: (QStyle.StandardPixmap) a standard pixmap which can follow some existing GUI style or guideline
    :param widget: (Qt.QWidget) the widget argument (optional) can also be used to aid the determination of the icon.
    
    :return: (PyQt4.QtGui.QIcon) a PyQt4.QtGui.QIcon for the given key"""
    styleOption = None
    if widget is not None:
        styleOption = Qt.QStyleOption()
        styleOption.initFrom(widget)
    style = Qt.QApplication.instance().style()
    return style.standardIcon(key, styleOption, widget)
    
# Indexes for the map below
__IDX_ELEM_TYPE_ICON, __IDX_ELEM_TYPE_SIZE, __IDX_ELEM_TYPE_TOOLTIP = range(3)

# New default role map
# Elements are: icon theme, preferred size, description/tooltip
_ELEM_TYPE_MAP = { ElemType.Name : ("folder", __3DQS, None),
            ElemType.Device : ("applications-system", Size(210, __DH), "Tango device name"),
       ElemType.DeviceAlias : ("applications-system", Size(140, __DH), "Tango device alias"),
            ElemType.Domain : ("folder", Size(80, __DH), "Tango device domain"),
            ElemType.Family : ("folder", Size(80, __DH), "Tango device family"),
            ElemType.Member : ("applications-system", Size(80, __DH), "Tango device member"),
            ElemType.Server : ("application-x-executable", Size(190, __DH), "Tango server"),
        ElemType.ServerName : ("application-x-executable", Size(80, __DH), "Tango server name"),
    ElemType.ServerInstance : ("application-x-executable", Size(80, __DH), "Tango server instance"),
       ElemType.DeviceClass : ("text-x-script", Size(140, __DH), "Tango class name"),
          ElemType.Exported : ("start-here", Size(60, __DH), "Alive/not alive"),
              ElemType.Host : ("network-server", Size(100, __DH), "Host machine were last ran"),
         ElemType.Attribute : ("format-text-bold", Size(100, __DH), "Attribute name"), }

def getElementTypeToolTip(elemType):
    data = _ELEM_TYPE_MAP.get(elemType)
    if data is None:
        return
    return data[__IDX_ELEM_TYPE_TOOLTIP]

def getElementTypeSize(elemType):
    data = _ELEM_TYPE_MAP.get(elemType)
    if data is None:
        return
    return data[__IDX_ELEM_TYPE_SIZE]

def getElementTypeIconName(elemType):
    """Gets an icon name string for the given :class:`taurus.core.taurusbasetypes.TaurusElementType`.
    
    If an icon name cannot be found for the given :class:`taurus.core.taurusbasetypes.TaurusElementType`,
    None is returned.
    
    :param elemType: (TaurusElementType) the taurus element type
    
    :return: (str) a string representing the icon name for the given 
             :class:`taurus.core.taurusbasetypes.TaurusElementType`"""
    if elemType is None:
        return
    data = _ELEM_TYPE_MAP.get(elemType)
    if data is None:
        return
    return data[__IDX_ELEM_TYPE_ICON]

def getElementTypeIcon(elemType, fallback=None):
    """Gets a PyQt4.QtGui.QIcon object for the given :class:`taurus.core.taurusbasetypes.TaurusElementType`.
    
    If an icon cannot be found for the given :class:`taurus.core.taurusbasetypes.TaurusElementType`,
    fallback is returned.
    
    :param elemType: (TaurusElementType) the taurus element type
    :param fallback: (PyQt4.QtGui.QIcon) the fallback icon. Default is None.
    
    :return: (PyQt4.QtGui.QIcon) a PyQt4.QtGui.QIcon for the given :class:`taurus.core.taurusbasetypes.TaurusElementType`"""

    themeIconName = getElementTypeIconName(elemType)
    icon = getThemeIcon(themeIconName)
    if icon.isNull() and fallback is not None:
        icon = fallback
    return icon

def getElementTypePixmap(elemType, size=None):
    """Gets a PyQt4.QtGui.QPixmap object for the given :class:`taurus.core.taurusbasetypes.TaurusElementType`.
    
    If a pixmap cannot be found for the given :class:`taurus.core.taurusbasetypes.TaurusElementType`,
    fallback is returned.
    
    :param elemType: (TaurusElementType) the taurus element type
    :param fallback: (PyQt4.QtGui.QPixmap) the fallback pixmap. Default is None.
    
    :return: (PyQt4.QtGui.QPixmap) a PyQt4.QtGui.QPixmap for the given :class:`taurus.core.taurusbasetypes.TaurusElementType`"""

    if elemType is None:
        return
    data = _ELEM_TYPE_MAP.get(elemType)
    if data is None:
        return
    themeName = data[__IDX_ELEM_TYPE_ICON]
    return getThemePixmap(themeName, size)

# Indexes for the map below
__IDX_HEALTH_ICON, __IDX_HEALTH_TOOLTIP = range(2)

_HEALTH_MAP = { DevHealth.Exported   : ("face-smile", "Element reported to be alive") ,
            DevHealth.ExportedAlive  : ("face-smile-big", "Element confirmed to be alive"),
          DevHealth.ExportedNotAlive : ("face-surprise", "Element reported to be alive but there is no connection!"),
             DevHealth.NotExported   : ("face-sad", "Element reported to be shutdown"),
         DevHealth.NotExportedAlive  : ("face-plain", "Element reported to be shutdown but there is a connection!"),
       DevHealth.NotExportedNotAlive : ("face-sad", "Element reported to be shutdown") }

def getSWDevHealthToolTip(elemHealth):
    data = _HEALTH_MAP.get(elemHealth)
    if data is None:
        return
    return data[__IDX_HEALTH_TOOLTIP]

def getSWDevHealthIcon(elemHealth, fallback=None):
    """Gets a PyQt4.QtGui.QIcon object for the given :class:`taurus.core.taurusbasetypes.TaurusSWDevHealth`.
    
    If an icon cannot be found for the given :class:`taurus.core.taurusbasetypes.TaurusSWDevHealth`,
    fallback is returned.
    
    :param elemHealth: (TaurusSWDevHealth) the taurus software device health status
    :param fallback: (PyQt4.QtGui.QIcon) the fallback icon. Default is None.
    
    :return: (PyQt4.QtGui.QIcon) a PyQt4.QtGui.QIcon for the given :class:`taurus.core.taurusbasetypes.TaurusSWDevHealth`"""
    if elemHealth is None:
        return
    data = _HEALTH_MAP.get(elemHealth)
    if data is None:
        return
    themeIconName = data[__IDX_HEALTH_ICON]
    
    icon = getThemeIcon(themeIconName)
    if icon.isNull() and fallback is not None:
        icon = fallback
    return icon

def getSWDevHealthPixmap(elemHealth, size=None):
    """Gets a PyQt4.QtGui.QPixmap object for the given :class:`taurus.core.taurusbasetypes.TaurusSWDevHealth`.
    
    If a pixmap cannot be found for the given :class:`taurus.core.taurusbasetypes.TaurusSWDevHealth`,
    fallback is returned.
    
    :param elemHealth: (TaurusSWDevHealth) the taurus software device health status
    :param fallback: (PyQt4.QtGui.QPixmap) the fallback icon. Default is None.
    
    :return: (PyQt4.QtGui.QPixmap) a PyQt4.QtGui.QPixmap for the given :class:`taurus.core.taurusbasetypes.TaurusSWDevHealth`"""
    if elemHealth is None:
        return
    data = _HEALTH_MAP.get(elemHealth)
    if data is None:
        return
    themeName = data[__IDX_HEALTH_ICON]
    return getThemePixmap(themeName, size)

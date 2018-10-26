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

"""This module sets the taurus.core.util.log.Logger to be the Qt message handler"""

__all__ = ['getQtLogger', 'initTaurusQtLogger']

__docformat__ = 'restructuredtext'

from taurus.external.qt import Qt
from taurus import Logger

qtLogger = None

QT_LEVEL_MATCHER = {
    Qt.QtDebugMsg: Logger.debug,
    Qt.QtWarningMsg: Logger.warning,
    Qt.QtCriticalMsg: Logger.error,
    Qt.QtFatalMsg: Logger.error,
    Qt.QtSystemMsg: Logger.info
}


def getQtLogger():
    global qtLogger
    if qtLogger is None:
        qtLogger = Logger('QtLogger')
    return qtLogger


def qtTaurusMessageHandler(msg_type, log_ctx, msg):
    # Qt5 version
    global qtLogger
    if qtLogger is not None:
        caller = QT_LEVEL_MATCHER.get(msg_type)
        return caller("Qt%s %s.%s[%s]: %a", log_ctx.category, log_ctx.file,
                 log_ctx.function, log_ctx.line, msg)

def qtTaurusMsgHandler(msg_type, msg):
    # Qt4 version
    global qtLogger
    if qtLogger is not None:
        caller = QT_LEVEL_MATCHER.get(msg_type)
        caller(qtLogger, msg)


def initTaurusQtLogger():
    global qtLogger
    if not qtLogger:
        if hasattr(Qt, "qInstallMessageHandler"):
            # Qt5
            Qt.qInstallMessageHandler(qtTaurusMessageHandler)

        elif hasattr(Qt, "qInstallMsgHandler"):
            # Qt4
            Qt.qInstallMsgHandler(qtTaurusMsgHandler)


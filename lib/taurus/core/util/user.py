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
Finds out user inf (currently just the logged user name) for Windows and
Posix machines. sets a USER_NAME variable containing the logged user name
defines a UNKNOWN_USER variable to which username falls back.
It also provides the getSystemUserName() function"""

__all__ = ["getSystemUserName", "USER_NAME", "UNKNOWN_USER"]

__docformat__ = "restructuredtext"

#import os
import getpass

# fallback. The caller of this module can check if username != UNKNOWN_USER
UNKNOWN_USER = 'UnknownUser'


def getSystemUserName():
    """Finds out user inf (currently just the logged user name) for Windows and
    Posix machines. sets a USER_NAME variable containing the logged user name
    defines a UNKNOWN_USER variable to which username falls back.

    :return: (str) current user name
    """
    try:
        return getpass.getuser()
    except:
        return UNKNOWN_USER
#    username=''
#    if os.name is 'posix': #this works for linux and macOSX
#        username=os.getenv('USER', UNKNOWN_USER)
#    elif os.name is 'nt': #win NT, XP... (and Vista?)
#        username=os.getenv('USERNAME', UNKNOWN_USER)
#    if username == '': username=UNKNOWN_USER
#    return username

USER_NAME = getSystemUserName()

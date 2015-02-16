#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################################
##
## This file is part of Sardana
## 
## http://www.sardana-controls.org/
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""This package provides the spock generic utilities"""

def translate_version_str2list(version_str):
    """Translates a version string in format 'x[.y[.z[...]]]' into a list of
    numbers"""
    if version_str is None:
        ver = [0, 0]
    else:
        ver = []
        for i in version_str.split(".")[:2]:
            try:
                i = int(i)
            except:
                i = 0
            ver.append(i)
    return ver

def get_ipython_version():
    """Returns the current IPython version"""
    import IPython
    v = None
    try:
        try:
            v = IPython.Release.version
        except:
            try:
                v = IPython.release.version
            except:
                pass
    except:
        pass
    return v

def get_ipython_version_list():
    ipv_str = get_ipython_version()
    return translate_version_str2list(ipv_str)

ipv = get_ipython_version_list()
if ipv >= [0, 10] and ipv < [0, 11]:
    from ipython_00_10.genutils import *
elif ipv >= [0, 11] and ipv < [1, 0]:
    from ipython_00_11.genutils import *
else:
    from ipython_01_00.genutils import *



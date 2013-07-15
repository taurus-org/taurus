#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
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

""" """

__docformat__ = 'restructuredtext'

__all__ = ["check_requirements"]

import sys

__requires__ = {
#     module        minimum
    "Python"      : (2,6,0),
    "PyTango"     : (7,2,3),
    "taurus.core" : (3,1,0),
}

def check_requirements(exec_name=None):
    
    if exec_name is None:
        exec_name = sys.argv[0]
    
    pyver_ = __requires__['Python']
    pytangover_ = __requires__['PyTango']
    taurusver_ = __requires__['taurus.core']

    pyver_str_ = ".".join(map(str, pyver_))
    pytangover_str_ = ".".join(map(str, pytangover_))
    taurusver_str_ = ".".join(map(str,taurusver_))
    
    pyver = sys.version_info[:3]
    pyver_str = ".".join(map(str,pyver))

    if pyver < pyver_:
        print "Sardana requires python %s. Installed version is %s" % (pyver_str_, pyver_str)
        sys.exit(-1)
    
    pytangover = None
    try:
        import PyTango
        pytangover = PyTango.Release.version_info[:3]
    except ImportError:
        pass
    except:
        pytangover = tuple(map(int, PyTango.__version__.split('.', 3)))

    if pytangover is None:
        print "%s requires PyTango %s. No version installed" % (exec_name, pytangover_str_,)
        sys.exit(-1)
    if pytangover < pytangover_:
        pytangover_str = ".".join(map(str,pytangover))
        print "%s requires PyTango %s. Installed version is %s" % (exec_name, pytangover_str_, pytangover_str)
        sys.exit(-1)
    
    taurusver = None
    try:
        import taurus
        taurusver = taurus.Release.version_info[:3]
    except ImportError:
        pass
    except:
        taurusver = tuple(map(int, taurus.Release.version.split('.', 3)))

    if taurusver is None:
        print "%s requires taurus %s. No version installed" % (exec_name, taurusver_str_,)
        sys.exit(-1)
    if taurusver < taurusver_:
        taurusver_str = ".".join(map(str,taurusver))
        print "%s requires taurus %s. Installed version is %s" % (exec_name, taurusver_str_, taurusver_str)
        sys.exit(-1)
    
    try:
        from lxml import etree
    except:
        print "Could not find any suitable XML library"
        sys.exit(-1)

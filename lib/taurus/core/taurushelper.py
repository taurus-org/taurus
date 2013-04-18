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

"""a list of helper methods"""

__all__ = ['check_dependencies', 'log_dependencies', 'getSchemeFromName',
           'Manager', 'Factory', 'Device', 'Attribute', 'Configuration',
           'Database', 'Object', 'Logger',
           'Critical', 'Error', 'Warning', 'Info', 'Debug', 'Trace',
           'setLogLevel', 'setLogFormat', 'getLogLevel', 'getLogFormat',
           'resetLogLevel', 'resetLogFormat',
           'enableLogOutput', 'disableLogOutput',
           'log', 'trace', 'debug', 'info', 'warning', 'error', 'critical',
           'changeDefaultPollingPeriod']

__docformat__ = "restructuredtext"

import sys

def __translate_version_str2int(version_str):
    """Translates a version string in format x[.y[.z[...]]] into a 000000 number"""
    import math
    parts = version_str.split('.')
    i, v, l = 0, 0, len(parts)
    if not l: return v
    while i<3:
        try:
            v += int(parts[i])*int(math.pow(10,(2-i)*2))
            l -= 1
            i += 1
        except ValueError,ve:
            return v
        if not l: return v
    return v
    
    try:
        v += 10000*int(parts[0])
        l -= 1
    except ValueError,ve:
        return v
    if not l: return v
    
    try:
        v += 100*int(parts[1])
        l -= 1
    except ValueError,ve:
        return v
    if not l: return v

    try:
        v += int(parts[0])
        l -= 1
    except ValueError:
        return v
    if not l: return v

def __get_python_version():
    return '.'.join(map(str,sys.version_info[:3]))

def __get_python_version_number():
    pyver_str = __get_python_version()
    if pyver_str is None: return None
    return __translate_version_str2int(pyver_str)

def __get_pytango_version():
    try:
        import PyTango
    except:
        return None
    try:
        return PyTango.Release.version
    except:
        return '0.0.0'

def __get_pytango_version_number():
    tgver_str = __get_pytango_version()
    if tgver_str is None: return None
    return __translate_version_str2int(tgver_str)

def __get_pyqt_version():
    try:
        import PyQt4.Qt
        return PyQt4.Qt.QT_VERSION_STR
    except:
        return None

def __get_pyqt_version_number():
    pyqtver_str = __get_pyqt_version()
    if pyqtver_str is None: return None
    return __translate_version_str2int(pyqtver_str)

def __get_pyqwt_version():
    try:
        import PyQt4.Qwt5
        return PyQt4.Qwt5.QWT_VERSION_STR
    except:
        pass

def __get_pyqwt_version_number():
    pyqwtver_str = __get_pyqwt_version()
    if pyqwtver_str is None: return None
    return __translate_version_str2int(pyqwtver_str)

def __get_qub_version():
    try:
        import Qub4
        return "1.0.0"
    except:
        try:
            import Qub
            return "1.0.0"
        except:
            pass

def __get_qub_version_number():
    qubver_str = __get_qub_version()
    if qubver_str is None: return None
    return __translate_version_str2int(qubver_str)

def __get_qtcontrols_version():
    try:
        import qtcontrols
        return "1.0.0"
    except:
        pass

def __get_qtcontrols_version_number():
    qtcontrols_str = __get_qtcontrols_version()
    if qtcontrols_str is None: return None
    return __translate_version_str2int(qtcontrols_str)

def __get_spyderlib_version():
    try:
        import spyderlib
        return spyderlib.__version__
    except:
        pass

def __get_spyderlib_version_number():
    spyderlibver_str = __get_spyderlib_version()
    if spyderlibver_str is None: return None
    return __translate_version_str2int(spyderlibver_str)
    
def __w(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()

def __wn(msg):
    __w(msg+'\n')

def check_dependencies():
    for msg in _check_dependencies(forlog=False):
        m = msg[1]
        if msg[0] != -1: m = '\t%s' % m
        print m

def log_dependencies():
    from taurus.core.util.log import Logger
    l = Logger("taurus")
    for msg in _check_dependencies(forlog=True):
        if msg[0] != -1:
            l.info(msg[1])

def _check_dependencies(forlog=False):
    """Checks for the required and optional packages of taurus"""
    
    if forlog:
        MSG = { 'OK' : '[OK]', 'ERR' : '[ERROR]', 'WARN' : '[WARNING]' }
    else:
        MSG = { 
            'OK'   : "[\033[0;32mOK\033[0m]",
            'ERR'  : "[\033[0;31mERROR\033[0m]",
            'WARN' : "[\033[0;33mWARNING\033[0m]" }
        
    core_requirements = {
    #    module       minimum  recommended 
        "Python"   : ("2.6.0", "2.6.0"),
        "PyTango"  : ("7.1.0", "7.1.0"),
    }
    
    widget_requirements = {
    #    module       minimum  recommended 
        "PyQt"     : ("4.4.0", "4.4.0"),
        "PyQwt"     : ("5.2.0", "5.2.0"),
    }

    widget_optional_requirements = {
    #    module       minimum  recommended 
        "Qub"       : ("1.0.0", "1.0.0"),
        "qtcontrols": ("1.0.0", "1.0.0"),
        "spyderlib" : ("2.0.0", "2.0.0"),
    }
    
    yield -1, "Checking required dependencies of taurus.core..."
    r = core_requirements

    m = "Checking for Python >=%s..." % r["Python"][0]
    minPython, recPython = map(__translate_version_str2int, r["Python"])
    currPython, currPythonStr = __get_python_version_number(), __get_python_version()
    if currPython is None:
        yield 2, "{msg} {ERR} (Not found])".format(msg=m, **MSG)
    elif currPython < minPython:
        yield 1, "{msg} {WARN} (Found {fnd}. Recommended >={rec})".format(msg=m, fnd=currPythonStr, rec=r['Python'][1],**MSG)
    else:
        yield 0, "{msg} {OK} (Found {fnd})".format(msg=m, fnd=currPythonStr, **MSG)

    m = "Checking for PyTango >=%s..." % r["PyTango"][0]
    minPyTango, recPyTango = map(__translate_version_str2int, r["PyTango"])
    currPyTango, currPyTangoStr = __get_pytango_version_number(),__get_pytango_version()
    if currPyTango is None:
        yield 2, "{msg} {ERR} (Not found])".format(msg=m, **MSG)
    elif currPyTango < minPyTango:
        yield 1, "{msg} {WARN} (Found {fnd}. Recommended >={rec})".format(msg=m, fnd=currPyTangoStr, rec=r['PyTango'][1],**MSG)
    else:
        yield 0, "{msg} {OK} (Found {fnd})".format(msg=m, fnd=currPyTangoStr,**MSG)
    
    yield -1, "Checking required dependencies of taurus.qt..."
    r = widget_requirements

    m = "Checking for PyQt >=%s..." % r["PyQt"][0]
    minPyQt, recPyQt = map(__translate_version_str2int, r["PyQt"])
    currPyQt, currPyQtStr = __get_pyqt_version_number(), __get_pyqt_version()
    if currPyQt is None:
        yield 2, "{msg} {ERR} (Not found])".format(msg=m, **MSG)
    elif currPyQt < minPyQt:
        yield 1, "{msg} {WARN} (Found {fnd}. Recommended >={rec})".format(msg=m, fnd=currPyQtStr, rec=r['PyQt'][1],**MSG)
    else:
        yield 0, "{msg} {OK} (Found {fnd})".format(msg=m, fnd=currPyQtStr,**MSG)

    m = "Checking for PyQwt >=%s..." % r["PyQwt"][0]
    minPyQwt, recPyQwt = map(__translate_version_str2int, r["PyQwt"])
    currPyQwt, currPyQwtStr = __get_pyqwt_version_number(), __get_pyqwt_version()
    if currPyQwt is None:
        yield 1, "{msg} {ERR} (Not found])".format(msg=m, **MSG)
    elif currPyQwt < minPyQwt:
        yield 1, "{msg} {WARN} (Found {fnd}. Recommended >={rec})".format(msg=m, fnd=currPyQwtStr, rec=r['PyQwt'][1],**MSG)
    else:
        yield 0, "{msg} {OK} (Found {fnd})".format(msg=m, fnd=currPyQwtStr,**MSG)

    yield -1, "Checking OPTIONAL dependencies of taurus.qt..."
    r = widget_optional_requirements
    
    m = "Checking for Qub >=%s..." % r["Qub"][0]
    minQub, recQub = map(__translate_version_str2int, r["Qub"])
    currQub, currQubStr = __get_qub_version_number(), __get_qub_version()
    if currQub is None:
        yield 1, "{msg} {WARN} (Not found])".format(msg=m, **MSG)
    elif currQub < minQub:
        yield 1, "{msg} {WARN} (Found {fnd}. Recommended >={rec})".format(msg=m, fnd=currQubStr, rec=r['Qub'][1],**MSG)
    else:
        yield 0, "{msg} {OK} (Found {fnd})".format(msg=m, fnd=currQubStr,**MSG)

    m = "Checking for spyderlib >=%s..." % r["spyderlib"][0]
    minspyderlib, recspyderlib = map(__translate_version_str2int, r["spyderlib"])
    currspyderlib, currspyderlibStr = __get_spyderlib_version_number(), __get_spyderlib_version()
    if currspyderlib is None:
        yield 1, "{msg} {WARN} (Not found])".format(msg=m, **MSG)
    elif currspyderlib < minspyderlib:
        yield 1, "{msg} {WARN} (Found {fnd}. Recommended >={rec})".format(msg=m, fnd=currspyderlibStr, rec=r['spyderlib'][1],**MSG)
    else:
        yield 0, "{msg} {OK} (Found {fnd})".format(msg=m, fnd=currspyderlibStr,**MSG)
    
    m = "Checking for qtcontrols >=%s..." % r["qtcontrols"][0]
    minqtcontrols, recqtcontrols = map(__translate_version_str2int, r["qtcontrols"])
    currqtcontrols, currqtcontrolsStr = __get_qtcontrols_version_number(), __get_qtcontrols_version()
    if currqtcontrols is None:
        yield 1, "{msg} {WARN} (Not found])".format(msg=m, **MSG)
    elif currqtcontrols < minqtcontrols:
        yield 1, "{msg} {WARN} (Found {fnd}. Recommended >={rec})".format(msg=m, fnd=currqtcontrolsStr, rec=r['qtcontrols'][1],**MSG)
    else:
        yield 0, "{msg} {OK} (Found {fnd})".format(msg=m, fnd=currqtcontrolsStr,**MSG)


def getSchemeFromName(name):
    if name is None: return None
    i=name.find('://')
    if i == -1: return None
    return name[:i]

def Manager():
    """Returns the one and only TaurusManager
    
    It is a shortcut to::

        import taurus.core
        manager = taurus.core.taurusmanager.TaurusManager()
    
    :return: the TaurusManager
    :rtype: :class:`taurus.core.taurusmanager.TaurusManager`
    
    .. seealso:: :class:`taurus.core.taurusmanager.TaurusManager`"""
    from taurus.core.taurusmanager import TaurusManager
    return TaurusManager()

def Factory(scheme=None):
    """Returns the one and only Factory for the given scheme
    
    It is a shortcut to::

        import taurus.core.taurusmanager
        manager = taurus.core.taurusmanager.TaurusManager()
        factory = manager.getFactory(scheme)

    :param scheme: a string representing the scheme. Default value is None meaning ``tango`` scheme
    :type scheme: str
    :return: a taurus factory
    :rtype: :class:`taurus.core.taurusfactory.TaurusFactory`"""
    manager = Manager()
    f = manager.getFactory(scheme=scheme)
    if f is None:
        from taurus.core.taurusexception import TaurusException
        if scheme is None:
            scheme = "default scheme '" + manager.default_scheme + "'"
        else:
            scheme = "'" + scheme + "'"
        raise TaurusException('Cannot create Factory for %s' % scheme)
    return f()

def Device(device_name):
    """Returns the taurus device for the given device name

    It is a shortcut to::

        import taurus.core.taurusmanager
        manager = taurus.core.taurusmanager.TaurusManager()
        factory = manager.getFactory()
        device  = factory.getDevice(device_name)
    
    :param device_name: the device name
    :type device_name: str
    :return: a taurus device
    :rtype: :class:`taurus.core.taurusdevice.TaurusDevice`"""
    return Factory(scheme=getSchemeFromName(device_name)).getDevice(device_name)

def Attribute(dev_or_attr_name, attr_name=None):
    """Returns the taurus attribute for either the pair (device name, attribute name) 
    or full attribute name
    
    - Attribute(full_attribute_name)
    - Attribute(device_name, attribute_name)

    It is a shortcut to::

        import taurus.core.taurusmanager
        manager = taurus.core.taurusmanager.TaurusManager()
        factory = manager.getFactory()
        attribute  = factory.getAttribute(full_attribute_name)
    
    or::
    
        import taurus.core.taurusmanager
        manager = taurus.core.taurusmanager.TaurusManager()
        factory = manager.getFactory()
        device  = factory.getDevice(device_name)
        attribute = device.getAttribute(attribute_name)
    
    :param dev_or_attr_name: the device name or full attribute name
    :type dev_or_attr_name: str or TaurusDevice
    :param attr_name: attribute name
    :type attr_name: str
    :return: a taurus attribute
    :rtype: :class:`taurus.core.taurusattribute.TaurusAttribute`"""
    import types
    
    if attr_name is None:
        return Factory(scheme=getSchemeFromName(dev_or_attr_name)).getAttribute(dev_or_attr_name)
    else:
        if type(dev_or_attr_name) in types.StringTypes:
            dev = Device(dev_or_attr_name)
        else:
            dev = dev_or_attr_name
        return dev.getAttribute(attr_name)

def Configuration(attr_or_conf_name, conf_name=None):
    """Returns the taurus configuration for either the pair (attribute name, conf name) 
    or full conf name
    
    - Configuration(full_conf_name)
    - Configuration(attribute_name, conf_name)
    
    It is a shortcut to::

        import taurus.core.taurusmanager
        manager = taurus.core.taurusmanager.TaurusManager()
        factory = manager.getFactory()
        conf  = factory.getConfiguration(attr_or_conf_name)

    or::
    
        import taurus.core.taurusmanager
        manager = taurus.core.taurusmanager.TaurusManager()
        factory = manager.getFactory()
        attribute  = factory.getAttribute(attribute_name)
        conf = attribute.getConfig(conf_name)
        
    :param attr_or_conf_name: the full attribute name or full conf name
    :type attr_or_conf_name: str
    :param conf_name: conf name
    :type conf_name: str or None
    :return: a taurus configuration
    :rtype: :class:`taurus.core.taurusconfiguration.TaurusConfiguration`"""
    if conf_name is None:
        return Factory(scheme=getSchemeFromName(attr_or_conf_name)).getConfiguration(attr_or_conf_name)
    else:
        return Attribute(attr_or_conf_name).getConfig(conf_name)

def Database(db_name=None):
    """Returns the taurus database
    
    It is a shortcut to::

        import taurus.core.taurusmanager
        manager = taurus.core.taurusmanager.TaurusManager()
        factory = manager.getFactory()
        db  = factory.getDatabase(db_name)
        
    :param db_name: database name. If None (default) it will use the TANGO_HOST value
    :type db_name: str or None
    :return: a taurus database
    :rtype: :class:`taurus.core.taurusdatabase.TaurusDatabase`"""
    return Factory(getSchemeFromName(db_name)).getDatabase(db_name)

def Object(klass, name):
    """Returns an taurus object of given class for the given name
    
    It is a shortcut to::

        import taurus.core.taurusmanager
        manager = taurus.core.taurusmanager.TaurusManager()
        factory = manager.getFactory()
        obj  = factory.getObject(klass, name)

    :param klass: a taurus model subclass (TaurusDevice, for example)
    :type klass: class TaurusModel
    :param name: the full object name
    :type name: str
    :return: a taurus object
    :rtype: :class:`taurus.core.taurusmodel.TaurusModel`"""
    return Factory(getSchemeFromName(name)).getObject(klass, name)

from taurus.core.util import log as __log_mod

Logger   = __log_mod.Logger
Critical = Logger.Critical
Error    = Logger.Error
Warning  = Logger.Warning
Info     = Logger.Info
Debug    = Logger.Debug
Trace    = Logger.Trace

setLogLevel = Logger.setLogLevel
setLogFormat = Logger.setLogFormat
getLogLevel = Logger.getLogLevel
getLogFormat = Logger.getLogFormat
resetLogLevel = Logger.resetLogLevel
resetLogFormat = Logger.resetLogFormat

enableLogOutput = Logger.enableLogOutput
disableLogOutput = Logger.disableLogOutput

log = __log_mod._log
trace = __log_mod.trace
debug = __log_mod.debug
info = __log_mod.info
warning = __log_mod.warning
error = __log_mod.error
critical = __log_mod.critical

def changeDefaultPollingPeriod(period):
    Manager().changeDefaultPollingPeriod(period)

#del __log_mod
#del __translate_version_str2int
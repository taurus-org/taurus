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

"""a list of helper methods"""

from __future__ import print_function

from builtins import str
from future.utils import string_types
import re
from taurus import tauruscustomsettings
from .util.log import taurus4_deprecation
import click

__all__ = ['check_dependencies', 'log_dependencies', 'getSchemeFromName',
           'getValidTypesForName', 'isValidName', 'makeSchemeExplicit',
           'Manager', 'Factory', 'Device', 'Attribute', 'Configuration',
           'Database', 'Authority', 'Object', 'Logger',
           'Critical', 'Error', 'Warning', 'Info', 'Debug', 'Trace',
           'setLogLevel', 'setLogFormat', 'getLogLevel', 'getLogFormat',
           'resetLogLevel', 'resetLogFormat',
           'enableLogOutput', 'disableLogOutput',
           'log', 'trace', 'debug', 'info', 'warning', 'error', 'fatal',
           'critical', 'deprecated', 'changeDefaultPollingPeriod',
           'getValidatorFromName']

__docformat__ = "restructuredtext"

# regexp for finding the scheme
__SCHEME_RE = re.compile(r'([^:/?#]+):.*')

def __check_pyqt(req='4.8'):
    import PyQt4.Qt
    from pkg_resources import parse_version
    assert(parse_version(PyQt4.Qt.PYQT_VERSION_STR) >= parse_version(req))


def __check_pyqwt5(req='5.2'):
    import PyQt4.Qwt5
    from pkg_resources import parse_version
    assert(parse_version(PyQt4.Qwt5.QWT_VERSION_STR) >= parse_version(req))


def check_dependencies():
    """ 
    Prints a check-list of requirements and marks those that are fulfilled
    """

    # non_pypi is a dictionary with extra:req_list and req_list is a list of
    # (reqname, check) tuples where reqname is the name of a requirement and
    # check is a function that raises an exception if the requirement is not
    # fulfilled
    non_pypi = {'taurus-qt': [('PyQt4>=4.8', __check_pyqt),
                              ('PyQt4.Qwt5>=5.2', __check_pyqwt5),
                              ]
                }
    import pkg_resources
    d = pkg_resources.get_distribution('taurus')
    print("Dependencies for %s:" % d)
    # minimum requirements (without extras)
    for r in d.requires():
        try:
            pkg_resources.require(str(r))
            print('\t[*]', end=' ')
        except Exception:
            print('\t[ ]', end=' ')
        print('%s' % r)
    # requirements for the extras
    print('\nExtras:')
    for extra in sorted(d.extras):
        print("Dependencies for taurus[%s]:" % extra)
        # requirements from PyPI
        for r in d.requires(extras=[extra]):
            try:
                r = str(r).split(';')[0]  # remove marker if present (see #612)
                pkg_resources.require(r)
                print('\t[*]', end=' ')
            except Exception:
                print('\t[ ]', end=' ')
            print('%s' % r)
        # requirements outside PyPI
        for r, check in non_pypi.get(extra, ()):
            try:
                check()
                print('\t[*]', end=' ')
            except Exception:
                print('\t[ ]', end=' ')
            print('%s (not in PyPI)' % r)


def log_dependencies():
    """deprecated since '4.0.4'"""
    from taurus import deprecated
    deprecated(dep='taurus.log_dependencies', rel='4.0.4')


def getSchemeFromName(name, implicit=True):
    """Return the scheme from a taurus name.

    :param name: (str) taurus model name URI.
    :param implicit: (bool) controls whether to return the default scheme
                     (if implicit is True -default-) or None (if implicit is
                     False) in case `model` does not contain the scheme name
                     explicitly. The default scheme may be defined in
                     :ref:`tauruscustomsettings` ('tango' is assumed if
                     not defined)
    """
    m = __SCHEME_RE.match(name)
    if m is not None:
        return m.groups()[0]
    if implicit:
        return getattr(tauruscustomsettings, 'DEFAULT_SCHEME', "tango")
    else:
        return None


def getValidatorFromName(name):
    """Helper for obtaining the validator object corresponding to the
    given name.

    :return: model name validator or None if name is not a supported model name
    """

    try:
        factory = Factory(scheme=getSchemeFromName(name))
    except:
        return None
    return factory.getValidatorFromName(name)



def makeSchemeExplicit(name, default=None):
    """return the name guaranteeing that the scheme is present. If name already
    contains the scheme, it is returned unchanged.

    :param name: (str) taurus model name URI.
    :param default: (str) The default scheme to use. If no default is passed,
                     the one defined in tauruscustomsettings.DEFAULT_SCHEME is
                     used.

    :return: the name with the explicit scheme.
    """
    if getSchemeFromName(name, implicit=False) is None:
        if default is None:
            default = getattr(tauruscustomsettings, 'DEFAULT_SCHEME', "tango")
        return "%s:%s" % (default, name)
    else:
        return name


def getValidTypesForName(name, strict=None):
    """
    Returns a list of all Taurus element types for which `name` is a valid
    model name (while in many cases a name may only be valid for one
    element type, this is not necessarily true in general)

    :param name: (str) taurus model name
    :param strict: (bool) If True, names that are not RFC3986-compliant but
                   which would be accepted for backwards compatibility are
                   considered valid.

    :return: (list<TaurusElementType.element>) where element can be one of:
             `Attribute`, `Device` or `Authority`
    """
    try:
        factory = Factory(scheme=getSchemeFromName(name))
    except:
        return []
    return factory.getValidTypesForName(name, strict=strict)


def isValidName(name, etypes=None, strict=None):
    """Returns True is the given name is a valid Taurus model name. If
    `etypes` is passed, it returns True only if name is valid for at least
    one of the given the element types. Otherwise it returns False.
    For example::

        isValidName('tango:foo')--> True
        isValidName('tango:a/b/c', [TaurusElementType.Attribute]) --> False

    :param name: (str) the string to be checked for validity
    :param etypes: (seq<TaurusElementType>) if given, names will only be
                   considered valid if they represent one of the given
                   element types. Supported element types are:
                   `Attribute`, `Device` and `Authority`
    :param strict: (bool) If True, names that are not RFC3986-compliant but
                   which would be accepted for backwards compatibility are
                   considered valid.

    :return: (bool)
    """
    validtypes = getValidTypesForName(name, strict=strict)
    if etypes is None:
        return bool(validtypes)
    for e in etypes:
        if e in validtypes:
            return True
    return False


def Manager():
    """Returns the one and only TaurusManager

    It is a shortcut to::

        import taurus.core
        manager = taurus.core.taurusmanager.TaurusManager()

    :return: the TaurusManager
    :rtype: :class:`taurus.core.taurusmanager.TaurusManager`

    .. seealso:: :class:`taurus.core.taurusmanager.TaurusManager`
    """
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
    :rtype: :class:`taurus.core.taurusfactory.TaurusFactory`
    """
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
    :rtype: :class:`taurus.core.taurusdevice.TaurusDevice`
    """
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
    :rtype: :class:`taurus.core.taurusattribute.TaurusAttribute`
    """
    import types

    if attr_name is None:
        return Factory(scheme=getSchemeFromName(dev_or_attr_name)).getAttribute(dev_or_attr_name)
    else:
        if isinstance(dev_or_attr_name, string_types):
            dev = Device(dev_or_attr_name)
        else:
            dev = dev_or_attr_name
        return dev.getAttribute(attr_name)


@taurus4_deprecation(alt='Attribute')
def Configuration(attr_or_conf_name, conf_name=None):
    """Returns the taurus configuration for either the pair
    (attribute name, conf name) or full conf name

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
    :rtype: :class:`taurus.core.taurusconfiguration.TaurusConfiguration`
    """
    return Attribute(attr_or_conf_name)


@taurus4_deprecation(alt='Authority')
def Database(name=None):
    return Authority(name=name)


def Authority(name=None):
    """Returns a taurus authority

    It is a shortcut to::

        import taurus.core.taurusmanager
        manager = taurus.core.taurusmanager.TaurusManager()
        factory = manager.getFactory()
        db  = factory.getAuthority(dname)

    :param name: authority name. If None (default) it will return the default
                 authority of the default scheme. For example, if the default
                 scheme is tango, it will return the default TANGO_HOST database
    :type name: str or None
    :return: a taurus authority
    :rtype: :class:`taurus.core.taurusauthority.TaurusAuthority`
    """
    return Factory(getSchemeFromName(name or '')).getAuthority(name)


def Object(*args):
    """Returns an taurus object of given class for the given name

    Can be called as:

      - Object(name)
      - Object(cls, name)

    Where:

      - `name` is a model name (str)
      - `cls` is a class derived from TaurusModel

    If `cls` is not given, Object() will try to guess it from `name`.

    :return: a taurus object
    :rtype: :class:`taurus.core.taurusmodel.TaurusModel`
    """
    if len(args) == 1:
        klass, name = None, args[0]
    elif len(args) == 2:
        klass, name = args
    else:
        msg = 'Object() takes either 1 or 2 arguments (%i given)' % len(args)
        raise TypeError(msg)
    factory = Factory(getSchemeFromName(name))
    if klass is None:
        klass = factory.findObjectClass(name)
    return factory.getObject(klass, name)


@click.command('check-deps')
def check_dependencies_cmd():
    """
    Shows the taurus dependencies and checks if they are available
    """
    check_dependencies()


from taurus.core.util import log as __log_mod

Logger = __log_mod.Logger
Critical = Logger.Critical
Fatal = Logger.Fatal
Error = Logger.Error
Warning = Logger.Warning
Info = Logger.Info
Debug = Logger.Debug
Trace = Logger.Trace

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
fatal = __log_mod.fatal
critical = __log_mod.critical
deprecated = __log_mod.deprecated


def changeDefaultPollingPeriod(period):
    Manager().changeDefaultPollingPeriod(period)

#del __log_mod
#del __translate_version_str2int

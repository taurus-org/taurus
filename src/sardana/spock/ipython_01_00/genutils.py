#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""This package provides the spock generic utilities"""

__all__ = ['page', 'arg_split', 'get_gui_mode', 'get_pylab_mode',
           'get_color_mode', 'get_app',
           'get_shell', 'get_ipapi', 'get_config', 'get_editor', 'ask_yes_no',
           'spock_input',
           'translate_version_str2int', 'get_ipython_version',
           'get_ipython_version_number', 'get_python_version',
           'get_python_version_number', 'get_ipython_dir',
           'get_ipython_profiles',
           'get_pytango_version', 'get_pytango_version_number',
           'get_server_for_device', 'get_macroserver_for_door',
           'get_device_from_user', 'get_tango_db', 'get_tango_host_from_user',
           'print_dev_from_class', 'from_name_to_tango', 'clean_up',
           'get_taurus_core_version', 'get_taurus_core_version_number',
           'check_requirements', 'get_door', 'get_macro_server',
           'expose_magic', 'unexpose_magic', 'expose_variable',
           'expose_variables', 'unexpose_variable',
           'create_spock_profile', 'check_for_upgrade', 'get_args',
           'start', 'mainloop', 'run',
           'load_ipython_extension', 'unload_ipython_extension', 'load_config',
           'MSG_FAILED', 'MSG_FAILED_WR', 'MSG_R', 'MSG_ERROR',
           'MSG_DONE', 'MSG_OK']

__docformat__ = 'restructuredtext'

import sys
import os
import socket

import IPython
import IPython.core.magic
from IPython.core.page import page
from IPython.core.profiledir import ProfileDirError, ProfileDir
from IPython.core.application import BaseIPythonApplication
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.io import ask_yes_no as _ask_yes_no
from IPython.utils.path import get_ipython_dir
from IPython.utils.process import arg_split
from IPython.utils.coloransi import TermColors
from IPython.config.application import Application
from IPython.terminal.ipapp import TerminalIPythonApp, launch_new_instance

import taurus
#from taurus.core import Release as TCRelease

from taurus.core.taurushelper import Factory
from taurus.core.util.codecs import CodecFactory

# make sure Qt is properly initialized
from taurus.qt import Qt

from sardana.spock import exception
from sardana.spock import colors
from sardana.spock import release

SpockTermColors = colors.TermColors

requirements = {
#     module     minimum  recommended
    "IPython"     : ("0.11.0", "0.12.0"),
    "Python"      : ("2.6.0", "2.6.0"),
    "PyTango"     : ("7.2.0", "7.2.3"),
    "taurus.core" : ("3.0.0", "3.0.0")
}

ENV_NAME = "_E"

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# IPython utilities
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

def get_gui_mode():
    return 'qt'

def get_pylab_mode():
    return get_app().pylab

def get_color_mode():
    return get_config().InteractiveShell.colors

def get_app():
    #return TerminalIPythonApp.instance()
    return Application.instance()

def get_shell():
    """Get the global InteractiveShell instance."""
    return get_app().shell

def get_ipapi():
    """Get the global InteractiveShell instance."""
    return InteractiveShell.instance()

def get_config():
    return get_app().config

def get_editor():
    return get_ipapi().editor

def ask_yes_no(prompt,default=None):
    """Asks a question and returns a boolean (y/n) answer.

    If default is given (one of 'y','n'), it is used if the user input is
    empty. Otherwise the question is repeated until an answer is given.

    An EOF is treated as the default answer.  If there is no default, an
    exception is raised to prevent infinite loops.

    Valid answers are: y/yes/n/no (match is not case sensitive)."""

    if default:
        prompt = '%s [%s]' % (prompt, default)
    return _ask_yes_no(prompt, default)

def spock_input(prompt='',  ps2='... '):
    return raw_input(prompt)

def translate_version_str2int(version_str):
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
        except ValueError:
            return v
        if not l: return v
    return v

    try:
        v += 10000*int(parts[0])
        l -= 1
    except ValueError:
        return v
    if not l: return v

    try:
        v += 100*int(parts[1])
        l -= 1
    except ValueError:
        return v
    if not l: return v

    try:
        v += int(parts[0])
        l -= 1
    except ValueError:
        return v
    if not l: return v

def get_ipython_version():
    """Returns the current IPython version"""
    v = None
    try:
        try:
            v = IPython.Release.version
        except Exception:
            try:
                v = IPython.release.version
            except Exception, e2:
                print e2
    except Exception, e3:
        print e3
    return v

def get_ipython_version_number():
    """Returns the current IPython version number"""
    ipyver_str = get_ipython_version()
    if ipyver_str is None: return None
    return translate_version_str2int(ipyver_str)

def get_python_version():
    return '.'.join(map(str,sys.version_info[:3]))

def get_python_version_number():
    pyver_str = get_python_version()
    return translate_version_str2int(pyver_str)

def get_ipython_profiles(path=None):
    """list profiles in a given root directory"""
    if path is None:
        path = get_ipython_dir()
    files = os.listdir(path)
    profiles = []
    for f in files:
        full_path = os.path.join(path, f)
        if os.path.isdir(full_path) and f.startswith('profile_'):
            profiles.append(f.split('_',1)[-1])
    return profiles

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# PyTango utilities
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

def get_pytango_version():
    try:
        import PyTango
        try:
            return PyTango.Release.version
        except:
            return '0.0.0'
    except:
        return None

def get_pytango_version_number():
    tgver_str = get_pytango_version()
    if tgver_str is None: return None
    return translate_version_str2int(tgver_str)

def get_server_for_device(device_name):
    db = get_tango_db()
    device_name = device_name.lower()
    server_list = db.get_server_list()
    for server in server_list:
        for dev in db.get_device_class_list(server)[::2]:
            if dev.lower() == device_name:
                return server
    return None

def get_macroserver_for_door(door_name):
    """Returns the MacroServer device name in the same DeviceServer as the
    given door device"""
    _, door_name, _ = from_name_to_tango(door_name)
    db = get_tango_db()
    door_name = door_name.lower()
    server_list = list(db.get_server_list('MacroServer/*'))
    server_list += list(db.get_server_list('Sardana/*'))
    server_devs = None
    for server in server_list:
        server_devs = db.get_device_class_list(server)
        devs, klasses = server_devs[0::2], server_devs[1::2]
        for dev in devs:
            if dev.lower() == door_name:
                for i, klass in enumerate(klasses):
                    if klass == 'MacroServer':
                        return "%s:%s/%s" % (db.get_db_host(), db.get_db_port(), devs[i])
    else:
        return None

def get_device_from_user(expected_class, dft = None):
    """Gets a device of the given device class from user input"""
    dft = print_dev_from_class(expected_class, dft)
    prompt = "%s name from the list" % expected_class
    if not dft is None:
        prompt += "[%s]" % dft
    prompt += "? "
    from_user = raw_input(prompt).strip() or dft

    name = ''
    try:
        full_name, name, _ = from_name_to_tango(from_user)
    except:
        print "Warning: the given %s does not exist" % expected_class
        return name

    try:
        db = get_tango_db()
        cl_name = db.get_class_for_device(name)
        class_correct = cl_name == expected_class
        if not class_correct:
            print "Warning: the given name is not a %s (it is a %s)"%(expected_class,cl_name)
    except Exception as e:
        print "Warning: unable to confirm if '%s' is valid" % name
        print str(e)
    return full_name

def get_tango_db():
    import PyTango
    tg_host = PyTango.ApiUtil.get_env_var("TANGO_HOST")

    db = None
    if tg_host is None:
        host,port = get_tango_host_from_user()
        tg_host = "%s:%d" % (host,port)
        os.environ["TANGO_HOST"] = tg_host
        db = PyTango.Database()
    else:
        try:
            db = PyTango.Database()
        except:
            # tg host is not valid. Find a valid one
            host,port = get_tango_host_from_user()
            tg_host = "%s:%d" % (host,port)
            os.environ["TANGO_HOST"] = tg_host

            db = PyTango.Database()
    return db

def get_tango_host_from_user():
    import PyTango
    while True:
        prompt = "Please enter a valid tango host (<host>:<port>): "
        from_user = raw_input(prompt).strip()

        try:
            host, port = from_user.split(':')
            try:
                port = int(port)
                try:
                    socket.gethostbyname(host)
                    try:
                        PyTango.Database(host, port)
                        return (host, port)
                    except:
                        exp = "No tango database found at %s:%d" % (host, port)
                except:
                    exp = "Invalid host name %s" % host
            except:
                exp = "Port must be a number > 0"
        except:
            exp = "Invalid tango host. Must be in format <host>:<port>"
        exp = "Invalid tango host. %s " % exp
        print exp

def print_dev_from_class(classname, dft = None):

    db = get_tango_db()
    pytg_ver = get_pytango_version_number()
    if pytg_ver >= 030004:
        server_wildcard = '*'
        try:
            exp_dev_list = db.get_device_exported_for_class(classname)
        except:
            exp_dev_list = []
    else:
        server_wildcard = '%'
        exp_dev_list = []

    res = None
    dev_list = db.get_device_name(server_wildcard,classname)
    tg_host = "%s:%s" % (db.get_db_host(),db.get_db_port())
    print "Available",classname,"devices from",tg_host,":"
    for dev in dev_list:
        _, name, alias = from_name_to_tango(dev)
        out = alias or name
        if alias: out += ' (a.k.a. %s)' % name
        out = "%-25s" % out
        if dev in exp_dev_list:
            out += " (running)"
        print out
        if dft:
            if dft.lower() == name.lower(): res = name
            elif not alias is None and dft.lower() == alias.lower(): res = alias

    return res

def from_name_to_tango(name):

    db = get_tango_db()

    alias = None

    c = name.count('/')
    # if the db prefix is there, remove it first
    if c == 3 or c == 1:
        name = name[name.index("/")+1:]

    elems = name.split('/')
    l = len(elems)

    if l == 3:
        try:
            alias = db.get_alias(name)
            if alias.lower() == 'nada':
                alias = None
        except:
            alias = None
    elif l == 1:
        alias = name
        name = db.get_device_alias(alias)
    else:
        raise Exception("Invalid device name '%s'" % name)

    full_name = "%s:%s/%s" % (db.get_db_host(), db.get_db_port(), name)
    return full_name, name, alias

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# taurus utilities
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

def clean_up():
    taurus.Manager().cleanUp()

def get_taurus_core_version():
    try:
        import taurus
        return taurus.core.release.version
    except:
        import traceback
        traceback.print_exc()
        return '0.0.0'

def get_taurus_core_version_number():
    tgver_str = get_taurus_core_version()
    if tgver_str is None: return None
    return translate_version_str2int(tgver_str)

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# Requirements checking
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

def check_requirements():
    r = requirements
    minPyTango, recPyTango = map(translate_version_str2int, r["PyTango"])
    minIPython, recIPython = map(translate_version_str2int, r["IPython"])
    minPython, recPython = map(translate_version_str2int, r["Python"])
    minTaurusCore, recTaurusCore = map(translate_version_str2int, r["taurus.core"])

    currPython = get_python_version_number()
    currIPython = get_ipython_version_number()
    currPyTango = get_pytango_version_number()
    currTaurusCore = get_taurus_core_version_number()

    errMsg = ""
    warnMsg = ""

    errPython, errIPython, errPyTango, errTaurusCore = False, False, False, False
    if currPython is None:
        errMsg += "Spock needs Python version >= %s. No python installation found\n" % requirements["Python"][0]
        errPython = True
    elif currPython < minPython:
        errMsg += "Spock needs Python version >= %s. Current version is %s\n" % (requirements["Python"][0], get_python_version())
        errPython = True

    if currIPython is None:
        errMsg += "Spock needs IPython version >= %s. No IPython installation found\n" % requirements["IPython"][0]
        errIPython = True
    elif currIPython < minIPython:
        errMsg += "Spock needs IPython version >= %s. Current version is %s\n" % (requirements["IPython"][0], get_ipython_version())
        errIPython = True

    if currPyTango is None:
        errMsg += "Spock needs PyTango version >= %s. No PyTango installation found\n" % requirements["IPython"][0]
        errPyTango = True
    elif currPyTango < minPyTango:
        errMsg += "Spock needs PyTango version >= %s. " % requirements["PyTango"][0]
        if currPyTango > 0:
            errMsg += "Current version is %s\n" % get_pytango_version()
        else:
            errMsg += "Current version is unknown (most surely too old)\n"
        errPyTango = True

    if currTaurusCore is None:
        errMsg += "Spock needs taurus.core version >= %s. No taurus.core installation found\n" % requirements["taurus.core"][0]
        errTaurusCore = True
    elif currTaurusCore < minTaurusCore:
        errMsg += "Spock needs taurus.core version >= %s. " % requirements["taurus.core"][0]
        if currTaurusCore > 0:
            errMsg += "Current version is %s\n" % get_taurus_core_version()
        else:
            errMsg += "Current version is unknown (most surely too old)\n"
        errTaurusCore = True

    # Warnings
    if not errPython and currPython < recPython:
        warnMsg += "Spock recommends Python version >= %s. Current version " \
                   "is %s\n" % (requirements["Python"][1],
                                get_python_version())

    if not errIPython and currIPython < recIPython:
        warnMsg += "Spock recommends IPython version >= %s. Current version " \
                   "is %s\n" % (requirements["IPython"][1],
                                get_ipython_version())

    if not errPyTango and currPyTango < recPyTango:
        warnMsg += "Spock recommends PyTango version >= %s. Current version " \
                   "is %s\n" % (requirements["PyTango"][1],
                                get_pytango_version())

    if not errTaurusCore and currTaurusCore < recTaurusCore:
        warnMsg += "Spock recommends taurus.core version >= %s. Current " \
                   "version is %s\n" % (requirements["taurus.core"][1],
                                        get_taurus_core_version())

    if errMsg:
        errMsg += warnMsg
        raise exception.SpockMissingRequirement, errMsg

    if warnMsg:
        raise exception.SpockMissingRecommended, warnMsg

    return True

def _get_dev(dev_type):
    spock_config = get_config().Spock
    taurus_dev = None
    taurus_dev_var = "_" + dev_type
    if hasattr(spock_config, taurus_dev_var):
        taurus_dev = getattr(spock_config, taurus_dev_var)
    if taurus_dev is None:
        dev_name = getattr(spock_config, dev_type + '_name')
        factory = Factory()
        taurus_dev = factory.getDevice(dev_name)
        import PyTango
        dev = PyTango.DeviceProxy(dev_name)
        setattr(spock_config, dev_type, dev)
        setattr(spock_config, taurus_dev_var, taurus_dev)
        shell = get_shell()
        dev_type_upper = dev_type.upper()
        shell.user_ns[dev_type_upper] = dev
        shell.user_ns["_" + dev_type_upper] = taurus_dev
    return taurus_dev

def get_door():
    return _get_dev('door')

def get_macro_server():
    return _get_dev('macro_server')

def _macro_completer(self, event):
    """Method called by the IPython autocompleter. It will determine possible
       values for macro arguments.
    """
    ms = get_macro_server()

    macro_name = event.command.lstrip('%')
    # calculate parameter index
    param_idx = len(event.line.split()) - 1
    if not event.line.endswith(' '): param_idx -= 1
    # get macro info
    info = ms.getMacroInfoObj(macro_name)
    # if macro doesn't have parameters return
    if param_idx < 0 or not info.hasParams() : return
    # get the parameter info
    possible_params = info.getPossibleParams(param_idx)
    # return the existing elements for the given parameter type
    if possible_params:
        res = []
        for param in possible_params:
            res.extend(ms.getElementNamesWithInterface(param['type']))
        return res

def expose_magic(name, fn, completer_func=_macro_completer):
    shell = get_shell()
    fn.old_magic = shell.define_magic(name, fn)
    fn.old_completer = completer_func

    if completer_func is None:
        return

    # enable macro param completion
    if completer_func is not None:
        shell.set_hook('complete_command', completer_func, str_key = name)
        shell.set_hook('complete_command', completer_func, str_key = '%'+name)

def unexpose_magic(name):
    shell = get_shell()
    mg_name = 'magic_' + name
    if hasattr(shell, mg_name):
        magic_fn  = getattr(shell, mg_name)
        delattr(shell, mg_name)
        if hasattr(magic_fn, 'old_magic') and magic_fn.old_magic is not None:
            expose_magic(name, magic_fn.old_magic, magic_fn.old_completer)

def expose_variable(name, value):
    get_shell().user_ns[name] = value

def expose_variables(d):
    get_shell().user_ns.update(d)

def unexpose_variable(name):
    user_ns = get_shell().user_ns
    del user_ns[name]

def create_spock_profile(userdir, dft_profile, profile, door_name=None):
    """Create a profile file from a profile template file """
    if not os.path.isdir(userdir):
        ProfileDir.create_profile_dir(userdir)
    p_dir = ProfileDir.create_profile_dir_by_name(userdir, profile)
    ###########################################################################
    # NOTE: BaseIPythonApplication.config_file_name.default_value should return
    # the config file name, but it returns an empty string instead (at least 
    # in some cases). For now, we give a hardcoded name if it is empty
    # TODO: Check why this is the case
    config_file_name = BaseIPythonApplication.config_file_name.default_value 
    config_file_name = config_file_name or 'ipython_config.py' 
    ###########################################################################
    abs_config_file_name = os.path.join(p_dir.location, config_file_name)
    create_config = True
    if os.path.isfile(abs_config_file_name):
        create_config = ask_yes_no("Spock configuration file already exists. "\
                                   "Do you wish to replace it?", default='y')
    if not create_config:
        return

    src_data = """\
\"\"\"Settings for Spock session\"\"\"

#
# Please do not delete the next lines has they are used to check the version
# number for possible upgrades
# spock_creation_version = {version}
# door_name = {door_name}
#

import PyTango.ipython
import sardana.spock.genutils
from sardana.spock.config import Spock

config = get_config()
config.Spock.macro_server_name = '{macroserver_name}'
config.Spock.door_name = '{door_name}'

load_subconfig('ipython_config.py', profile='default')
sardana.spock.load_config(config)

# Put any additional environment here and/or overwrite default sardana config
config.IPKernelApp.pylab = 'inline'

"""
    #
    # Discover door name
    #
    if door_name is None:
        door_name = get_device_from_user("Door", profile)
    else:
        full_door_name, door_name, _ = from_name_to_tango(door_name)
        door_name = full_door_name

    #
    # Discover macro server name
    #
    ms_name = get_macroserver_for_door(door_name)

    dest_data = src_data.format(version=release.version,
                                macroserver_name=ms_name,
                                door_name=door_name)

    sys.stdout.write('Storing %s in %s... ' % (config_file_name, p_dir.location))
    sys.stdout.flush()

    with file(abs_config_file_name, "w") as f:
        f.write(dest_data)
        f.close()
    sys.stdout.write(MSG_DONE + '\n')

def check_for_upgrade(ipy_profile_file, ipythondir, session, profile):
    # Check if the current profile is up to date with the spock version
    spock_profile_ver_str = '0.0.0'
    door_name = None

    # search for version and door inside the ipy_profile file
    for i, line in enumerate(ipy_profile_file):
        if i > 20 : break; # give up after 20 lines
        if line.startswith('# spock_creation_version = '):
            spock_profile_ver_str = line[line.index('=')+1:].strip()
        if line.startswith('# door_name = '):
            door_name = line[line.index('=')+1:].strip()

    # convert version from string to numbers
    spocklib_ver = translate_version_str2int(release.version)
    spock_profile_ver = translate_version_str2int(spock_profile_ver_str)

    if spocklib_ver == spock_profile_ver:
        return
    if spocklib_ver < spock_profile_ver:
        print '%sYour spock profile (%s) is newer than your spock version ' \
              '(%s)!' % (SpockTermColors.Brown, spock_profile_ver_str, release.version)
        print 'Please upgrade spock or delete the current profile %s' % SpockTermColors.Normal
        sys.exit(1)

    # there was no version track of spock profiles since spock 0.2.0 so change
    # the message
    if spock_profile_ver_str == '0.0.0':
        spock_profile_ver_str = '<= 0.2.0'
    msg = 'Your current spock door extension profile has been created with spock %s.\n' \
          'Your current spock door extension version is %s, therefore a profile upgrade is needed.\n' \
          % (spock_profile_ver_str, release.version)
    print msg
    prompt = 'Do you wish to upgrade now (warn: this will shutdown the current spock session) ([y]/n)? '
    r = raw_input(prompt) or 'y'
    if r.lower() == 'y':
        create_spock_profile(ipythondir, session, profile, door_name)
        sys.exit(0)

def get_args(argv):

    script_name = argv[0]
    _, session = os.path.split(script_name)
    script_name = os.path.realpath(script_name)

    macro_server = None
    door = None

    # Define the profile file
    profile = "spockdoor"
    try:
        for _, arg in enumerate(argv[:1]):
            if arg.startswith('--profile='):
                profile=arg[10:]
                break
        else:
            argv.append("--profile=" + profile)
    except:
        pass

    ipython_dir = get_ipython_dir()
    try:
        ProfileDir.find_profile_dir_by_name(ipython_dir, profile)
    except ProfileDirError:
        r = ''
        while not r in ('y','n'):
            prompt = 'Profile \'%s\' does not exist. Do you want to create '\
                     'one now ([y]/n)? ' % profile
            r = raw_input(prompt) or 'y'
        if r.lower() == 'y':
            create_spock_profile(ipython_dir, session, profile)
        else:
            sys.stdout.write('No spock door extension profile was created. Starting normal spock...\n')
            sys.stdout.flush()
            profile = ''

    # inform the shell of the profile it should use
    if not '--profile=' in argv and profile:
        argv.append('--profile=' + profile)

    user_ns = { 'MACRO_SERVER_NAME' : macro_server,
                'DOOR_NAME'         : door,
                'PROFILE'           : profile }

    return user_ns

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# Useful constants
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

MSG_G = '[%s%%s%s]' % (SpockTermColors.Green, SpockTermColors.Normal)
MSG_R = '[%s%%s%s]' % (SpockTermColors.Red, SpockTermColors.Normal)
MSG_FAILED = MSG_R % 'FAILED'
MSG_FAILED_WR = MSG_R % 'FAILED: %s'
MSG_ERROR  = MSG_R % 'ERROR'
MSG_DONE   = MSG_G % 'DONE'
MSG_OK     = MSG_G % 'OK'

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# initialization methods
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

def init_taurus():
    # the CodecFactory is not thread safe. There are two attributes who will
    # request for it in the first event at startup in different threads
    # therefore this small hack: make sure CodecFactory is initialized.
    CodecFactory()

    factory = Factory()

    import sardana.spock.spockms
    macroserver = sardana.spock.spockms

    factory.registerDeviceClass('MacroServer', macroserver.SpockMacroServer)

    mode = get_gui_mode()
    if mode == 'qt':
        factory.registerDeviceClass('Door', macroserver.QSpockDoor)
    else:
        factory.registerDeviceClass('Door', macroserver.SpockDoor)


def load_ipython_extension(ipython):
    import sardana.spock.magic
    magic = sardana.spock.magic

    init_taurus()

    config = ipython.config
    user_ns = ipython.user_ns
    user_ns['MACRO_SERVER_NAME'] = config.Spock.macro_server_name
    user_ns['MACRO_SERVER_ALIAS'] = config.Spock.macro_server_alias
    user_ns['DOOR_NAME'] = config.Spock.door_name
    user_ns['DOOR_ALIAS'] = config.Spock.door_alias
    user_ns['DOOR_STATE'] = ""

    #shell.set_hook('late_startup_hook', magic.spock_late_startup_hook)
    ipython.set_hook('pre_prompt_hook', magic.spock_pre_prompt_hook)

    #if ip.IP.alias_table.has_key('mv'):
    #    del ip.IP.alias_table['mv']

    door = get_door()
    macro_server = get_macro_server()

    # Initialize the environment
    expose_variable(ENV_NAME, macro_server.getEnvironment())
    
    new_style_magics = hasattr(IPython.core.magic, 'Magics') and hasattr(IPython.core.magic, 'magics_class')
    
    if new_style_magics:
        @IPython.core.magic.magics_class
        class Sardana(IPython.core.magic.Magics):
            debug = IPython.core.magic.line_magic(magic.debug)
            www = IPython.core.magic.line_magic(magic.www)
            post_mortem = IPython.core.magic.line_magic(magic.post_mortem)
            spsplot = IPython.core.magic.line_magic(magic.post_mortem)
            macrodata = IPython.core.magic.line_magic(magic.macrodata)
            edmac = IPython.core.magic.line_magic(magic.edmac)
            showscan = IPython.core.magic.line_magic(magic.showscan)
            expconf = IPython.core.magic.line_magic(magic.expconf)
        
        ipython.register_magics(Sardana)
    else:
        expose_magic('debug', magic.debug, magic.debug_completer)
        expose_magic('www', magic.www, magic.www_completer)
        expose_magic('post_mortem', magic.post_mortem, magic.post_mortem_completer)
        expose_magic('spsplot', magic.spsplot, None)
        expose_magic('macrodata', magic.macrodata, None)
        expose_magic('edmac', magic.edmac, None)
        expose_magic('showscan', magic.showscan, None)
        expose_magic('expconf', magic.expconf, None)

    door.setConsoleReady(True)

def unload_ipython_extension(ipython):
    pass

def load_config(config):
    spockver = release.version
    pyver = get_python_version()
    ipyver = get_ipython_version()
    pytangover = get_pytango_version()
    tauruscorever = get_taurus_core_version()

    door = config.Spock.door_name

    if not hasattr(config.Spock, 'macro_server_name'):
        macro_server = get_macroserver_for_door(door)
    else:
        macro_server = config.Spock.macro_server_name

    full_door_tg_name, door_tg_name, door_tg_alias = from_name_to_tango(door)
    door_alias = door_tg_alias or door_tg_name
    full_ms_tg_name, ms_tg_name, ms_tg_alias = from_name_to_tango(macro_server)
    ms_alias = ms_tg_alias or ms_tg_name

    config.Spock.macro_server_name = full_ms_tg_name
    config.Spock.door_name = full_door_tg_name
    config.Spock.macro_server_alias = ms_alias
    config.Spock.door_alias = door_alias

    d = { "version" : spockver,
          "pyver" : pyver,
          "ipyver" : ipyver,
          "pytangover" : pytangover,
          "taurusver" : tauruscorever,
          #"profile" : ip.user_ns["PROFILE"],
          "door" : door_alias }

    d.update(TermColors.__dict__)

    gui_mode = get_gui_mode()

    banner = """\
%(Purple)sSpock %(version)s%(Normal)s -- An interactive laboratory application.

help      -> Spock's help system.
object?   -> Details about 'object'. ?object also works, ?? prints more.
"""
    banner = banner % d
    banner = banner.format(**d)

    ipy_ver = get_ipython_version_number()

    # ------------------------------------
    # Application
    # ------------------------------------
    app = config.Application
    app.log_level = 30

    # ------------------------------------
    # BaseIPythonApplication
    # ------------------------------------
    i_app = config.BaseIPythonApplication
    extensions = getattr(i_app, 'extensions', [])
    extensions.extend(["PyTango.ipython", "sardana.spock"])
    i_app.extensions = extensions

    # ------------------------------------
    # InteractiveShell
    # (IPython.core.interactiveshell)
    # ------------------------------------
    i_shell = config.InteractiveShell
    i_shell.autocall = 0
    i_shell.automagic = True
    i_shell.color_info = True
    i_shell.colors = 'Linux'
    i_shell.deep_reload = True
    i_shell.confirm_exit = False

    if ipy_ver >= 1200:
        # ------------------------------------
        # PromptManager (ipython >= 0.12)
        # ------------------------------------
        prompt = config.PromptManager
        prompt.in_template = '{DOOR_ALIAS} [\\#]: '
        prompt.in2_template = '   .\\D.: '
        prompt.out_template = 'Result [\\#]: '
        prompt.color_scheme = 'Linux'
    else:
        # (Deprecated in ipython >= 0.12 use PromptManager.in_template)
        i_shell.prompt_in1 = config.Spock.door_alias + ' [\\#]: '

        # (Deprecated in ipython >= 0.12 use PromptManager.in2_template)
        i_shell.prompt_in2 = '   .\\D.: '

        # (Deprecated in ipython >= 0.12 use PromptManager.out_template)
        i_shell.prompt_out = 'Result [\\#]: '

        # (Deprecated in ipython >= 0.12 use PromptManager.justify)
        i_shell.prompts_pad_left = True

    # ------------------------------------
    # IPCompleter
    # ------------------------------------
    completer = config.IPCompleter
    completer.omit__names = 2
    completer.greedy = False

    # ------------------------------------
    # InteractiveShellApp
    # ------------------------------------
    i_shell_app = config.InteractiveShellApp
    i_shell_app.ignore_old_config = True

    # ------------------------------------
    # TerminalIPythonApp: options for the IPython terminal (and not Qt Console)
    # ------------------------------------
    term_app = config.TerminalIPythonApp
    term_app.display_banner = True
    term_app.gui = gui_mode
    term_app.pylab='qt'
    #term_app.nosep = False
    #term_app.classic = True

    # ------------------------------------
    # IPKernelApp: options for the  Qt Console
    # ------------------------------------
    #kernel_app = config.IPKernelApp
    ipython_widget = config.IPythonWidget
    ipython_widget.in_prompt  = ' Spock [<span class="in-prompt-number">%i</span>]: '
    ipython_widget.out_prompt = 'Result [<span class="out-prompt-number">%i</span>]: '
    ipython_widget.input_sep = '\n'
    ipython_widget.output_sep = ''
    ipython_widget.output_sep2 = ''
    ipython_widget.enable_calltips = True
    if ipy_ver >= 1300:
        ipython_widget.gui_completion = 'droplist'
    else:
        ipython_widget.gui_completion = True
    ipython_widget.ansi_codes = True
    ipython_widget.paging = 'inside'
    #ipython_widget.pylab = 'inline'

    # ------------------------------------
    # ConsoleWidget
    # ------------------------------------
    # console_widget = config.ConsoleWidget

    # ------------------------------------
    # FrontendWidget
    # ------------------------------------
    frontend_widget = config.FrontendWidget
    frontend_widget.banner = banner

    # ------------------------------------
    # TerminalInteractiveShell
    # ------------------------------------
    term_i_shell = config.TerminalInteractiveShell
    term_i_shell.autocall = 2
    term_i_shell.automagic = True
    #term_i_shell.editor = 'gedit'
    #term_i_shell.editor = 'nano'

    term_i_shell.banner1 = banner
    term_i_shell.banner2 = "Connected to " + door_alias + "\n"
    #term_app.banner1 = banner
    #term_app.banner2 = "Connected to " + door_alias + "\n"

    # ------------------------------------
    # InlineBackend
    # ------------------------------------
    inline_backend = config.InlineBackend
    inline_backend.figure_format = 'svg'

    # ------------------------------------
    # InteractiveShellEmbed
    # ------------------------------------
    #i_shell_embed = config.InteractiveShellEmbed

    # ------------------------------------
    # NotebookApp
    # ------------------------------------
    #notebook_app = config.NotebookApp

    # ------------------------------------
    # NotebookManager
    # ------------------------------------
    #notebook_manager = config.NotebookManager

    # ------------------------------------
    # ZMQInteractiveShell
    # ------------------------------------
    #zmq_i_shell = config.ZMQInteractiveShell

    # Tell console everything is ready.
    config.Spock.ready = True
    return config

def start(user_ns=None):
    # Make sure the log level is changed to warning
    CodecFactory()
    taurus.setLogLevel(taurus.Warning)

    try:
        check_requirements()
    except exception.SpockMissingRequirement, requirement:
        print str(requirement)
        sys.exit(-1)
    except exception.SpockMissingRecommended, recommended:
        print str(recommended)

    user_ns = user_ns or {}
    try:
        user_ns.update(get_args(sys.argv))
    except exception.SpockException, e:
        print e.message
        print 'Starting normal IPython console'
    except KeyboardInterrupt:
        print "\nUser pressed Ctrl+C. Exiting..."
        sys.exit()
    except Exception, e:
        print 'spock exited with an unmanaged exception: %s' % str(e)
        sys.exit(-2)

    app = TerminalIPythonApp.instance()
    app.initialize()
    #config = get_config()
    return app

def mainloop(app=None, user_ns=None):
    if app is None:
        app = start(user_ns)
    app.start()

def prepare_input_handler():
    # initialize input handler as soon as possible
    import sardana.spock.inputhandler
    _ = sardana.spock.inputhandler.InputHandler()


def prepare_cmdline(argv=None):
    if argv is None:
        argv = sys.argv

    script_name = argv[0]
    _, session = os.path.split(script_name)
    script_name = os.path.realpath(script_name)

    # Define the profile file
    profile, append_profile = "spockdoor", True
    try:
        for _, arg in enumerate(argv[:1]):
            if arg.startswith('--profile='):
                profile=arg[10:]
                append_profile = False
                break
    except:
        pass

    ipython_dir = get_ipython_dir()
    try:
        ProfileDir.find_profile_dir_by_name(ipython_dir, profile)
    except ProfileDirError:
        r = ''
        while not r in ('y', 'n'):
            prompt = "Profile '%s' does not exist. Do you want to create "\
                     "one now ([y]/n)? " % profile
            r = raw_input(prompt) or 'y'
        if r.lower() == 'y':
            create_spock_profile(ipython_dir, session, profile)
        else:
            sys.stdout.write('No spock profile was created. '
                             'Starting ipython with default profile...\n')
            sys.stdout.flush()
            append_profile = False

    if append_profile:
        argv.append("--profile=" + profile)


def run():
    from IPython.utils.traitlets import Unicode
    from IPython.qt.console.rich_ipython_widget import RichIPythonWidget

    class SpockConsole(RichIPythonWidget):
        
        banner = Unicode(config=True)

        def _banner_default(self):
            config = get_config()
            return config.FrontendWidget.banner

    import IPython.qt.console.qtconsoleapp
    IPythonQtConsoleApp = IPython.qt.console.qtconsoleapp.IPythonQtConsoleApp
    IPythonQtConsoleApp.widget_factory = SpockConsole

    try:
        check_requirements()
    except exception.SpockMissingRequirement, requirement:
        print str(requirement)
        sys.exit(-1)
    except exception.SpockMissingRecommended, recommended:
        print str(recommended)
    
    prepare_input_handler()
    prepare_cmdline()

    launch_new_instance()


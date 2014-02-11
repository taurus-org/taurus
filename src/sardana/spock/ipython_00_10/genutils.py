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
           'get_color_mode', 'get_ipapi',
           'get_editor', 'ask_yes_no', 'spock_input',
           'translate_version_str2int', 'get_ipython_version',
           'get_ipython_version_number', 'get_python_version',
           'get_python_version_number', 'get_ipython_dir',
           'get_ipython_profiles', 'get_spock_profiles', 
           'get_non_spock_profiles', 'get_spock_user_profile_module',
           'get_pytango_version', 'get_pytango_version_number',
           'get_server_for_device', 'get_macroserver_for_door',
           'get_device_from_user', 'get_tango_db', 'get_tango_host_from_user',
           'print_dev_from_class', 'from_name_to_tango', 'clean_up',
           'get_taurus_core_version', 'get_taurus_core_version_number',
           'check_requirements', 'get_door', 'get_macro_server', 'expose_magic',
           'unexpose_magic', 'expose_variable', 'expose_variables',
           'unexpose_variable',
           'create_spock_profile', 'check_for_upgrade', 'get_args',
           'init_console', 'init_magic', 'init_pre_spock', 'init_post_spock',
           'init_spock', 'start', 'mainloop', 'run',
           'load_ipython_extension', 'unload_ipython_extension', 'load_config',
           'MSG_FAILED','MSG_FAILED_WR', 'MSG_R', 'MSG_ERROR',
           'MSG_DONE', 'MSG_OK' ]

__docformat__ = 'restructuredtext'

import sys
import os
import socket
import imp

import IPython
import IPython.genutils
import PyTango
import PyTango.ipython

from taurus.core.taurushelper import Factory
from taurus.core.util.codecs import CodecFactory

from sardana.spock import exception
from sardana.spock import colors
from sardana.spock import release

arg_split = IPython.iplib.arg_split
page = IPython.genutils.page
TermColors = colors.TermColors


requirements = {
#     module     minimum  recommended 
    "IPython"     : ("0.10.0", "0.10.0"),
    "Python"      : ("2.6.0", "2.6.0"),
    "PyTango"     : ("7.1.2", "7.2.0"),
    "taurus.core" : ("2.0.0", "2.1.0")
}

ENV_NAME = "_E"

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# IPython utilities
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

def get_gui_mode():
    if '-q4thread' in sys.argv:
        return 'qt'
    elif '-gthread' in sys.argv:
        return 'gtk'
    elif '-wthread' in sys.argv:
        return 'wx'
    return ''

def get_pylab_mode():
    return get_gui_mode()
    
def get_color_mode():
    return get_ipapi().options.colors
    
def get_ipapi():
    return IPython.ipapi.get()

def get_editor():
    return get_ipapi().options.editor

def ask_yes_no(prompt,default=None):
    """Asks a question and returns a boolean (y/n) answer.

    If default is given (one of 'y','n'), it is used if the user input is
    empty. Otherwise the question is repeated until an answer is given.

    An EOF is treated as the default answer.  If there is no default, an
    exception is raised to prevent infinite loops.

    Valid answers are: y/yes/n/no (match is not case sensitive)."""

    if default:
        prompt = '%s [%s]' % (prompt, default)
    return IPython.genutils.ask_yes_no(prompt, default)

def spock_input(prompt='',  ps2='... '):
    return IPython.genutils.raw_input_ext(prompt=prompt, ps2=ps2)   

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
            except Exception:
                pass
    except Exception:
        pass
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

def get_ipython_dir():
    """Find the ipython local directory. Usually is <home>/.ipython"""
    if hasattr(PyTango.ipython, "get_ipython_dir"):
        return PyTango.ipython.get_ipython_dir()
    
    if hasattr(IPython.iplib, 'get_ipython_dir'):
        # Starting from ipython 0.9 they hadded this method
        return IPython.iplib.get_ipython_dir()
    
    # Try to find the profile in the current directory and then in the 
    # default IPython dir
    #userdir = os.path.realpath(os.path.curdir)
    home_dir = IPython.genutils.get_home_dir()
    
    if os.name == 'posix':
        ipdir = '.ipython'
    else:
        ipdir = '_ipython'
    ipdir = os.path.join(home_dir, ipdir)
    ipythondir = os.path.abspath( os.environ.get('IPYTHONDIR', ipdir) )
    return ipythondir

def get_ipython_profiles():
    """Helper function to find all ipython profiles"""
    if hasattr(PyTango.ipython, "get_ipython_profiles"):
        return PyTango.ipython.get_ipython_profiles()

    ret = []
    ipydir = get_ipython_dir()
    if os.path.isdir(ipydir):
        for i in os.listdir(ipydir):
            fullname = os.path.join(ipydir, i)
            if i.startswith("ipy_profile_") and i.endswith(".py"):
                if os.path.isfile(fullname):
                    ret.append(i[len("ipy_profile_"):i.rfind(".")])
    return ret

def get_spock_profiles(ipython_profiles=None):
    """Helper function to find all spock ipython profiles"""
    ret = []
    ipydir = get_ipython_dir()
    if not os.path.isdir(ipydir):
        return ret
    if ipython_profiles is None:
        ipython_profiles = get_ipython_profiles()
    ret = []
    for profile in ipython_profiles:
        profile_f = os.path.join(ipydir, "ipy_profile_%s.py" % profile)
        if not os.path.isfile(profile_f): continue
        try:
            for i, l in enumerate(file(profile_f)):
                if i > 10: break
                if l.find("spock_creation_version") >= 0:
                    ret.append(profile)
                    break
        except:
            pass
    return ret

def get_non_spock_profiles(ipython_profiles=None):
    """Helper function to find all non spock ipython profiles"""
    if ipython_profiles is None:
        ipython_profiles = get_ipython_profiles()
    ipython_profiles = set(ipython_profiles)
    spock_profiles = set(get_spock_profiles(ipython_profiles=ipython_profiles))
    return ipython_profiles.difference(spock_profiles)

def get_spock_user_profile_module(profile_name):
    return 'ipy_profile_%s' % profile_name
    
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# PyTango utilities
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

def get_pytango_version():
    try:
        import PyTango
    except:
        return None
    try:
        return PyTango.Release.version
    except:
        return '0.0.0'

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
    full_door_name, door_name, door_alias = from_name_to_tango(door_name)
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
        full_name, name, alias = from_name_to_tango(from_user)
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
                        db = PyTango.Database(host,port)
                        return db.get_db_host(), db.get_db_port()
                    except:
                        exp = "No tango database found at %s:%d" % (host,port)
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
        except Exception:
            exp_dev_list = []
    else:
        server_wildcard = '%'
        exp_dev_list = []
    
    res = None
    dev_list = db.get_device_name(server_wildcard,classname)
    tg_host = "%s:%s" % (db.get_db_host(),db.get_db_port())
    print "Available",classname,"devices from",tg_host,":"
    for dev in dev_list:
        full_name, name, alias = from_name_to_tango(dev)
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
        warnMsg += "Spock recommends Python version >= %s. Current version is %s\n" % (requirements["Python"][1], get_python_version())

    if not errIPython and currIPython < recIPython:
        warnMsg += "Spock recommends IPython version >= %s. Current version is %s\n" % (requirements["IPython"][1], get_ipython_version())

    if not errPyTango and currPyTango < recPyTango:
        warnMsg += "Spock recommends PyTango version >= %s. Current version is %s\n" % (requirements["PyTango"][1], get_pytango_version())
            
    if not errTaurusCore and currTaurusCore < recTaurusCore:
        warnMsg += "Spock recommends taurus.core version >= %s. Current version is %s\n" % (requirements["taurus.core"][1], get_taurus_core_version())

    if errMsg:
        errMsg += warnMsg
        raise exception.SpockMissingRequirement, errMsg

    if warnMsg: 
        raise exception.SpockMissingRecommended, warnMsg
    
    return True

def _get_dev(dev_type):
    ip = get_ipapi()
    ret = ip.user_ns.get("_" + dev_type)
    if ret is not None:
        return ret
    
    dev_obj_name = '%s_NAME' % dev_type
    dev_name = ip.user_ns[dev_obj_name]
    factory = Factory()
    dev_obj = factory.getDevice(dev_name)
    ip.user_ns[dev_type] = PyTango.DeviceProxy(dev_name) 
    ip.user_ns["_" + dev_type] = dev_obj
    setattr(ip, '_%s' % dev_type, dev_obj)
    return dev_obj

def get_door():
    return _get_dev('DOOR')

def get_macro_server():
    return _get_dev('MACRO_SERVER')

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
    ip = get_ipapi()
    ip.expose_magic(name, fn)
    
    if completer_func is None:
        return
    
    # enable macro param completion
    ip.set_hook('complete_command', completer_func, str_key = name)

    # register also when the command as is typed with the magic prefix '%'
    name = str('%') + name
    ip.set_hook('complete_command', completer_func, str_key = name)
    
def unexpose_magic(name):
    ip = get_ipapi()
    mg = 'magic_%s' % name
    delattr(ip.IP, mg)

def expose_variable(name, value):
    get_ipapi().to_user_ns({ name : value })

def unexpose_variable(name):
    user_ns = get_ipapi().user_ns
    del user_ns[name]
    
def expose_variables(d):
    get_ipapi().to_user_ns(d)

#def _expose_device(name):
#    ip.to_user_ns({ name : PyTango.DeviceProxy(name) })
    
#def expose_device(name):
#    ip = get_ipapi()
#    ip.magic("bg _expose_device(%s)" % name)

def create_spock_profile(userdir, dft_profile, profile, door_name=None):
    """Create a profile file from a profile template file """

    src_data = """\
\"\"\"Settings for Spock session\"\"\"

#
# Please do not delete the next lines has they are used to check the version 
# number for possible upgrades
# spock_creation_version = {version}
# door_name = {door_name}
#

import IPython
from sardana.spock.genutils import init_spock

def main():
    ip = IPython.ipapi.get()
    init_spock(ip, '{macroserver_name}', '{door_name}')

main()
"""
    
    #
    # Discover door name
    #
    if door_name is None:
        door_name = get_device_from_user("Door", profile)
    else:
        full_door_name, door_name, door_alias = from_name_to_tango(door_name)
        door_name = full_door_name
    
    #
    # Discover macro server name
    #
    ms_name = get_macroserver_for_door(door_name)
    
    dest_data = src_data.format(version=release.version,
                                macroserver_name=ms_name,
                                door_name=door_name)
    
    f_name = '%s.py' % get_spock_user_profile_module(profile)
    
    dest_name = os.path.join(userdir, f_name)
    
    sys.stdout.write('Storing %s in %s... ' % (f_name, userdir))
    sys.stdout.flush()
    res = MSG_FAILED
    try:
        dest = open(dest_name,"w")
        dest.write(dest_data)
        dest.flush()
        dest.close()
        res = MSG_DONE
    finally:
        sys.stdout.write(res + '\n')
        sys.stdout.flush()

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
              '(%s)!' % (TermColors.Brown, spock_profile_ver_str, release.version)
        print 'Please upgrade spock or delete the current profile %s' % TermColors.Normal
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
    script_dir, session = os.path.split(script_name)
    script_name = os.path.realpath(script_name)
    #script_dir = os.path.dirname(script_name)
    
    macro_server = None
    door = None
    
    # Define the profile file
    profile = "spockdoor"
    try:
        profile_idx = argv.index('-p') + 1
        if len(argv) > profile_idx:
            profile = argv[profile_idx]
    except:
        pass

    profile_modulename = get_spock_user_profile_module(profile)
    
    # Try to find the profile in the current directory and then in the 
    # default IPython dir
    #userdir = os.path.realpath(os.path.curdir)
    ipythondir = get_ipython_dir()
    
    if not os.path.isdir(ipythondir):
        # Platform-dependent suffix.
        if os.name == 'posix':
            rc_suffix = ''
        else:
            rc_suffix = '.ini'
        IPython.iplib.user_setup(ipythondir, rc_suffix, mode='install',
                                 interactive=False)
    
    try:
        f, name, t = imp.find_module(profile_modulename, [ipythondir])
        check_for_upgrade(f, ipythondir, session, profile)
    except ImportError:
        # Create a new profile
        r = ''
        while not r in ['y','n']:
            prompt = 'Profile \'%s\' does not exist. Do you want to create '\
                     'one now ([y]/n)? ' % profile
            r = raw_input(prompt) or 'y'
        if r.lower() == 'y':
            create_spock_profile(ipythondir, session, profile)
        else:
            sys.stdout.write('No spock door extension profile was created. Starting normal spock...\n')
            sys.stdout.flush()
            profile = ''
    
    # inform the shell of the profile it should use
    if not '-p' in argv and profile:
        argv.append('-p')
        argv.append(profile)
    
    user_ns = { 'MACRO_SERVER_NAME' : macro_server,
                'DOOR_NAME'         : door,
                'PROFILE'           : profile }
    
    return user_ns

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# Useful constants
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

MSG_G = '[%s%%s%s]' % (TermColors.Green, TermColors.Normal)
MSG_R = '[%s%%s%s]' % (TermColors.Red, TermColors.Normal)
MSG_FAILED = MSG_R % 'FAILED'
MSG_FAILED_WR = MSG_R % 'FAILED: %s'
MSG_ERROR  = MSG_R % 'ERROR'
MSG_DONE   = MSG_G % 'DONE'
MSG_OK     = MSG_G % 'OK'

#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# initialization methods
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

def init_console(ip):
    # Handy tab-completers for %cd, %run, import etc.
    # Try commenting this out if you have completion problems/slowness
    import ipy_stock_completers

    spockver = release.version
    pyver = get_python_version()
    ipyver = get_ipython_version()
    pytangover = get_pytango_version()
    tauruscorever = get_taurus_core_version()
    
    TermColors = IPython.ColorANSI.TermColors
    
    d = { "version" : spockver,
          "pyver" : pyver,
          "ipyver" : ipyver,
          "pytangover" : pytangover,
          "taurusver" : tauruscorever,
          "profile" : ip.user_ns["PROFILE"],
          "door" : ip.user_ns["DOOR_ALIAS"] }
          
    d.update(TermColors.__dict__)

    # IPython options
    o = ip.options
    o.autocall = 1
    o.autoedit_syntax = 0
    o.autoindent = 1
    o.automagic = 1
    o.cache_size = 1000
    o.colors = 'Linux'
    o.color_info = 1
    o.confirm_exit = 0
    o.deep_reload = 0
    #o.editor = 'gedit'
    o.log = 0
    o.logfile = ''
    o.messages = 1
    o.pdb = 0
    o.pprint = 1
    o.quick = 0
    o.readline = 1
    o.screen_length = 0
    o.separate_in = '\n'
    o.separate_out = '\n'
    o.separate_out2 = ''
    o.nosep = 0
    o.wildcards_case_sensitive = 0
    o.object_info_string_level = 0
    o.xmode = 'Context'
    o.multi_line_specials = 1
    o.system_header = 'IPython system call: '
    o.system_verbose = 1
    o.wxversion = '0'
    o.colors = "GreenTango"
    o.prompt_in1 = "$DOOR_ALIAS$DOOR_STATE [\\#]: "
    o.prompt_out = "Result [\\#]: "
    o.readline_parse_and_bind.append('tab: complete')
    #o.readline_parse_and_bind.append('tab: menu-complete')
    o.readline_parse_and_bind.append('"\C-l": possible-completions')
    o.readline_parse_and_bind.append('set show-all-if-ambiguous on')
    o.readline_parse_and_bind.append('"\C-o": tab-insert')
    o.readline_parse_and_bind.append('"\M-i": "    "')
    o.readline_parse_and_bind.append('"\M-o": "\d\d\d\d"')
    o.readline_parse_and_bind.append('"\M-I": "\d\d\d\d"')
    o.readline_parse_and_bind.append('"\C-r": reverse-search-history')
    o.readline_parse_and_bind.append('"\C-s": forward-search-history')
    o.readline_parse_and_bind.append('"\C-p": history-search-backward')
    o.readline_parse_and_bind.append('"\C-n": history-search-forward')
    o.readline_parse_and_bind.append('"\e[A": history-search-backward')
    o.readline_parse_and_bind.append('"\e[B": history-search-forward')
    o.readline_parse_and_bind.append('"\C-k": kill-line')
    o.readline_parse_and_bind.append('"\C-u": unix-line-discard')
    o.readline_remove_delims = '-/~'
    o.readline_merge_completions = 1
    o.readline_omit__names = 0

    banner = """\
%(Purple)sSpock %(version)s%(Normal)s -- An interactive laboratory application.

help      -> Spock's help system.
object?   -> Details about 'object'. ?object also works, ?? prints more.
"""
    banner = banner % d
    banner = banner.format(**d)

    o.banner = banner

def init_magic(ip):
    import sardana.spock.magic
    magic = sardana.spock.magic
    expose_magic('debug', magic.debug, magic.debug_completer)
    expose_magic('www', magic.www, None)
    expose_magic('post_mortem', magic.post_mortem, None)
    expose_magic('spsplot', magic.spsplot, None)
    expose_magic('macrodata', magic.macrodata, None)
    expose_magic('edmac', magic.edmac, None)
    expose_magic('showscan', magic.showscan, None)
    expose_magic('expconf', magic.expconf, None)
    ip.set_hook('late_startup_hook', magic.spock_late_startup_hook)
    ip.set_hook('pre_prompt_hook', magic.spock_pre_prompt_hook)

def init_pre_spock(ip, macro_server, door):
    so = IPython.ipstruct.Struct()
    full_door_tg_name, door_tg_name, door_tg_alias = from_name_to_tango(door)
    #macro_server = get_ms_for_door(door_tg_name)
    full_ms_tg_name, ms_tg_name, ms_tg_alias = from_name_to_tango(macro_server)
    ip.user_ns['MACRO_SERVER_NAME'] = full_ms_tg_name
    ip.user_ns['MACRO_SERVER_ALIAS'] = ms_tg_alias or ms_tg_name
    ip.user_ns['DOOR_NAME'] = full_door_tg_name
    ip.user_ns['DOOR_ALIAS'] = door_tg_alias or door_tg_name
    ip.user_ns['DOOR_STATE'] = ""
    ip.user_ns['spock_options'] = so
    
    if ip.IP.alias_table.has_key('mv'):
        del ip.IP.alias_table['mv']
    
    v = release.version
    alias = ip.user_ns['DOOR_ALIAS']
    profile = ip.user_ns['PROFILE']
    
    so.spock_banner = """\
{Blue}Spock's sardana extension %s loaded with profile: %s (linked to door '%s'){Normal}
""" % (v, profile, alias)

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
    
    door = get_door()
    macro_server = get_macro_server()
    
    # Initialize the environment
    expose_variable(ENV_NAME, macro_server.getEnvironment())


def init_post_spock(ip):
    init_console(ip)
    init_magic(ip)
    
def init_spock(ip, macro_server, door):
    init_pre_spock(ip, macro_server, door)
    PyTango.ipython.init_ipython(ip)
    init_post_spock(ip)


def start(user_ns=None):
    if '-pylab' not in sys.argv: sys.argv.insert(1, '-pylab')
    if '-q4thread' not in sys.argv: sys.argv.insert(1, '-q4thread')

    # Make sure the log level is changed to warning
    from taurus.core.taurushelper import setLogLevel, Warning
    CodecFactory()
    setLogLevel(Warning)

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
        
    return IPython.Shell.start(user_ns=user_ns)

def mainloop(shell=None, user_ns=None):
    if shell is None:
        shell = start(user_ns)
    shell.mainloop()

def run(user_ns=None):
    # initialize input handler as soon as possible
    import sardana.spock.inputhandler
    input_handler = sardana.spock.inputhandler.InputHandler()

    try:
        mainloop(user_ns=user_ns)
    finally:
        try:
            clean_up()
        except Exception:
            pass

# for compatibility reasons with new IPython API (>=0.11) we add the following
# empty methods
            
def load_ipython_extension(ipython):
    pass

def unload_ipython_extension(ipython):
    pass
    
def load_config(config):
    pass

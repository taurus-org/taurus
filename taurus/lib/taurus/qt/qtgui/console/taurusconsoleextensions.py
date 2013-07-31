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

"""This package contains a collection of taurus console widgets"""

__docformat__ = 'restructuredtext'

import weakref

from taurus import Device
from taurus.core.util.enumeration import Enumeration 
from taurus.qt import Qt

from IPython.config.loader import Config


EnvironmentMode = Enumeration("EnvironmentMode", ("Overwrite", "Merge"))


class BaseConsoleExtension(object):
    
    Name = 'ipython'
    Label = 'IPython'
    
    def __init__(self, console_factory, profile='default', config=None,
                 mode=EnvironmentMode.Merge):
        self.console_factory = console_factory
        self.profile = profile
        self.profile_arg = '--profile=' + profile 
        self.config = config or Config()
        self.mode = mode
        
    def __enter__(self):
        app = self.console_factory.get_ipython_application()
        self.orig_config = app.config
        self.orig_kernel_argv = argv = app.kernel_argv
        argv, has_profile = list(argv), False
        for i, arg in enumerate(argv):
            if arg.startswith('--profile'):
                has_profile = True
                if self.mode == EnvironmentMode.Overwrite:
                    argv[i] = self.profile_arg
        if not has_profile:
            argv.append(self.profile_arg)
        app.kernel_argv = argv
        
        config = self.config
        if self.mode == EnvironmentMode.Merge:
            config = config.copy()
            config.update(app.config)
        app.config = config
    
    def __exit__(self,exc_type, exc_value, traceback):
        app = self.console_factory.get_ipython_application()
        app.config = self.orig_config
        app.kernel_argv = self.orig_kernel_argv

    @classmethod
    def is_enabled(cls):
        return True


class TangoConsoleExtension(BaseConsoleExtension):
    
    Name = 'tango'
    Label = 'Tango'
    
    def __init__(self, console_factory, config=None):
        if config is None:
            config = Config()
        import PyTango.ipython
        PyTango.ipython.load_config(config)
        super(TangoConsoleExtension, self).__init__(console_factory,
                                                    profile='tango',
                                                    config=config)
    
    @classmethod
    def is_enabled(cls):
        try:
            import PyTango
            v = list(PyTango.__version_info__[:2])
            return v >= [7,2]
        except:
            return False


from IPython.core.profiledir import ProfileDir, ProfileDirError
from IPython.utils.path import get_ipython_dir

from sardana.spock.genutils import create_spock_profile, get_macroserver_for_door

def create_sardana_profile(profile, door_name):

    ipython_dir = get_ipython_dir()
    try:
        ProfileDir.find_profile_dir_by_name(ipython_dir, profile)
    except ProfileDirError:
        create_spock_profile(ipython_dir, "spock", profile, door_name)

def get_profile_from_args(args):
    for arg in args:
        if arg.startswith("--profile="):
            profile = arg[10:]
            return True, profile
    return False, "spockdoor"

                
class SDMDoorReader(Qt.QObject):

    def __init__(self, console, sdm=None, parent=None):
        super(Qt.QObject, self).__init__(parent)
        self._console = weakref.ref(console)
        if sdm is None:
            if not hasattr(Qt.qApp, 'SDM'):
                raise Exception("Cannot connect to shared data manager")
            sdm = Qt.qApp.SDM
        sdm.connectReader("doorName", self.onDoorChanged)
        
    @property
    def console(self):
        return self._console()
    
    def onDoorChanged(self, door_name):
        door = Device(door_name)
        dalias, dname = door.getSimpleName(), door.getNormalName()
        create_sardana_profile(dalias, dname)

    
class SardanaConsoleExtension(BaseConsoleExtension):
    
    Name = 'spock'
    Label = 'Spock'
    
    def fill_sardana_config(self, config):
        import sardana.spock
        profile = 'spockdoor'
        if not config.Spock:
            if hasattr(Qt.qApp, 'SDM'):
                dm = Qt.qApp.SDM.getDataModelProxy('doorName')
                if dm is not None:
                    door_name = dm.getData()
                    door = Device(door_name)
                    dalias, dname = door.getSimpleName(), door.getNormalName()
                    create_sardana_profile(dalias, dname)
                    profile = dalias
                    config.Spock.door_name = dname
        sardana.spock.load_config(config)
        return profile
    
    def __init__(self, console_factory, config=None):
        if config is None:
            config = Config()
        profile = self.fill_sardana_config(config)
        super(SardanaConsoleExtension, self).__init__(console_factory,
                                                      profile=profile,
                                                      config=config)
    
    @classmethod
    def is_enabled(cls):
        try:
            import sardana
            v = list(sardana.Release.version_info[:2])
            return v >= [1,2]
        except:
            return False

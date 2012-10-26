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

from IPython.config.loader import Config

from taurus.core.util import Enumeration 

EnvironmentMode = Enumeration("EnvironmentMode", ("Overwrite", "Merge"))


class BaseConsoleExtension(object):
    
    Name = 'ipython'
    Label = 'IPython'
    
    def __init__(self, app, profile='default', config=None,
                 mode=EnvironmentMode.Merge):
        self.app = app
        self.profile = profile
        self.profile_arg = '--profile=' + profile 
        self.config = config or Config()
        self.mode = mode
        
    def __enter__(self):
        self.orig_config = self.app.config
        self.orig_kernel_argv = argv = self.app.kernel_argv
        argv, has_profile = list(argv), False
        for i, arg in enumerate(argv):
            if arg.startswith('--profile'):
                has_profile = True
                if self.mode == EnvironmentMode.Overwrite:
                    argv[i] = self.profile_arg
        if not has_profile:
            argv.append(self.profile_arg)
        self.app.kernel_argv = argv
        
        config = self.config
        if self.mode == EnvironmentMode.Merge:
            config = config.copy()
            config.update(self.app.config)
        self.app.config = config
    
    def __exit__(self,exc_type, exc_value, traceback):
        self.app.config = self.orig_config
        self.app.kernel_argv = self.orig_kernel_argv

    @classmethod
    def is_enabled(cls):
        return True


class TangoConsoleExtension(BaseConsoleExtension):
    
    Name = 'tango'
    Label = 'Tango'
    
    def __init__(self, app, config=None):
        if config is None:
            config = Config()
        import PyTango.ipython
        PyTango.ipython.load_config(config)
        super(TangoConsoleExtension, self).__init__(app, profile='tango', config=config)
    
    @classmethod
    def is_enabled(cls):
        try:
            import PyTango
            v = list(PyTango.__version_info__[:2])
            return v >= [7,2]
        except:
            return False
            

class SardanaConsoleExtension(BaseConsoleExtension):
    Name = 'spock'
    Label = 'Spock'
    
    def fill_sardana_config(self, config):
        import sardana.spock
        config.Spock.macro_server_name = 'pc151:10000/MacroServer/v3/1'
        config.Spock.door_name = 'pc151:10000/Door/v3/1'
        sardana.spock.load_config(config)
    
    def __init__(self, app, config=None):
        if config is None:
            config = Config()
        self.fill_sardana_config(config)
        super(SardanaConsoleExtension, self).__init__(app, profile='spockdoor', config=config)
    
    @classmethod
    def is_enabled(cls):
        try:
            import sardana
            v = list(sardana.Release.version_info[:2])
            return v >= [1,2]
        except:
            return False

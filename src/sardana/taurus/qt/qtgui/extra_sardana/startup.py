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

"""This file is executed by the python interpreter running as subprocess of
SpockShell"""

__docformat__ = 'restructuredtext'


import sys

def __run_pythonstartup_script():
    import os
    filename = os.environ.get('PYTHONSTARTUP')
    if filename and os.path.isfile(filename):
        execfile(filename)

def __run_init_commands():
    import os
    return os.environ.get('PYTHONINITCOMMANDS')

def __remove_from_syspath__():
    """Remove this module's path from sys.path"""
    import os.path as osp
    try:
        sys.path.remove(osp.dirname(__file__))
    except ValueError:
        pass


class UserModuleDeleter(object):
    """
    User Module Deleter (UMD) aims at deleting user modules 
    to force Python to deeply reload them during import
    
    pathlist [list]: blacklist in terms of module path
    namelist [list]: blacklist in terms of module name
    """
    def __init__(self, namelist=None, pathlist=None):
        if namelist is None:
            namelist = []
        self.namelist = namelist+['sitecustomize', 'spyderlib', 'spyderplugins']
        if pathlist is None:
            pathlist = []
        self.pathlist = pathlist
        self.previous_modules = sys.modules.keys()

    def is_module_blacklisted(self, modname, modpath):
        for path in [sys.prefix]+self.pathlist:
            if modpath.startswith(path):
                return True
        else:
            return set(modname.split('.')) & set(self.namelist)
        
    def run(self, verbose=False):
        """
        Del user modules to force Python to deeply reload them
        
        Do not del modules which are considered as system modules, i.e. 
        modules installed in subdirectories of Python interpreter's binary
        Do not del C modules
        """
        log = []
        for modname, module in sys.modules.items():
            if modname not in self.previous_modules:
                modpath = getattr(module, '__file__', None)
                if modpath is None:
                    # *module* is a C module that is statically linked into the 
                    # interpreter. There is no way to know its path, so we 
                    # choose to ignore it.
                    continue
                if not self.is_module_blacklisted(modname, modpath):
                    log.append(modname)
                    del sys.modules[modname]
        if verbose and log:
            print "\x1b[4;33m%s\x1b[24m%s\x1b[0m" % ("UMD has deleted",
                                                     ": "+", ".join(log))

__umd__ = None

def runfile(filename, args=None, wdir=None):
    """
    Run filename
    args: command line arguments (string)
    wdir: working directory
    """
    global __umd__
    import os
    if os.environ.get("UMD_ENABLED", "").lower() == "true":
        if __umd__ is None:
            namelist = os.environ.get("UMD_NAMELIST", None)
            if namelist is not None:
                namelist = namelist.split(',')
            __umd__ = UserModuleDeleter(namelist=namelist)
        else:
            verbose = os.environ.get("UMD_VERBOSE", "").lower() == "true"
            __umd__.run(verbose=verbose)
    if args is not None and not isinstance(args, basestring):
        raise TypeError("expected a character buffer object")
    glbs = globals()
    if '__ipythonshell__' in glbs:
        glbs = glbs['__ipythonshell__'].IP.user_ns
    glbs['__file__'] = filename
    sys.argv = [filename]
    if args is not None:
        for arg in args.split():
            sys.argv.append(arg)
    if wdir is not None:
        os.chdir(wdir)
    execfile(filename, glbs)
    sys.argv = ['']
    glbs.pop('__file__')
    

def debugfile(filename, args=None, wdir=None):
    """
    Debug filename
    args: command line arguments (string)
    wdir: working directory
    """
    import pdb
    debugger = pdb.Pdb()
    filename = debugger.canonic(filename)
    debugger._wait_for_mainpyfile = 1
    debugger.mainpyfile = filename
    debugger._user_requested_quit = 0
    debugger.run("runfile(%r, args=%r, wdir=%r)" % (filename, args, wdir))


if __name__ == "__main__":
    __remove_from_syspath__()
    
    __commands__ = __run_init_commands()
    if __commands__:
        for command in __commands__.split(';'):
            exec command
    else:
        __run_pythonstartup_script()

    for _name in ['__run_pythonstartup_script', '__run_init_commands',
                  '__create_banner', '__commands__', 'command', '__file__',
                  '__remove_sys_argv__']+['_name']:
        if _name in locals():
            locals().pop(_name)

    __doc__ = ''
    __name__ = '__main__'

    import os
    if os.name == 'nt':
        # Windows platforms: monkey-patching *pyreadline* module
        # to make IPython work in a remote process
        from pyreadline import unicode_helper
        unicode_helper.pyreadline_codepage = "ascii"
        import pyreadline
        pyreadline.GetOutputFile = lambda: None
    import spocklib.genutils
    
    __ipythonshell__ = spocklib.genutils.start(user_ns={'runfile': runfile,
                                                        'debugfile': debugfile})
    __ipythonshell__.IP.stdin_encoding = os.environ['SPYDER_ENCODING']
    
    spocklib.genutils.mainloop(shell=__ipythonshell__)

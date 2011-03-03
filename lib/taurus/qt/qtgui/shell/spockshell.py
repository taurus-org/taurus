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

"""This module contains a spock shell widget. The widget starts an ipython
interpreter in a subprocess with the spock profile"""

__all__ = ["SpockShellWidget", "SpockShell"]

__docformat__ = 'restructuredtext'

from taurusshell import *

#-------------------------------------------------------------------------------
# Spock shell. A pure tango shell based on IPython
#-------------------------------------------------------------------------------

class SpockShellWidget(TaurusPythonShellWidget):
    pass


class SpockShell(TaurusPythonShell):
    SHELL_CLASS = SpockShellWidget

    def _preprocess_arguments(self, args):
        if not '-p' in args.split(' '):
            args += "-p spock"
        return args
            
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('ipython'): kwargs['ipython'] = True
        arguments = kwargs.get('arguments')
        if arguments is None:
            arguments = ''
        kwargs['arguments'] = self._preprocess_arguments(arguments)
        if kwargs.has_key('designMode'): kwargs.pop('designMode')
        TaurusPythonShell.__init__(self, *args, **kwargs)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = TaurusPythonShell.getQtDesignerPluginInfo()
        ret['icon'] = ":/designer/spockshell.png"
        return ret

def demo():
    #"""Tango shell"""
    from spyderlib.plugins.variableexplorer import VariableExplorer
    settings = VariableExplorer.get_settings()
    shell = SpockShell(stand_alone=settings)
    shell.resize(768,768)
    shell.show()
    return shell

def main():
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication
    
    app = Application.instance()
    owns_app = app is None
    
    if owns_app:
        import taurus.core.util.argparse
        parser = taurus.core.util.argparse.get_taurus_parser()
        app = Application(sys.argv, cmd_line_parser=parser, 
                          app_name="Spock Shell demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")

    shell = demo()
    
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == '__main__':
    main()
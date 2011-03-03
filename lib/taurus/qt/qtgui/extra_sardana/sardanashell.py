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

"""This module contains a sardana shell widget. The widget starts an ipython
interpreter in a subprocess with the spock profile connected to sardana."""

__all__ = ["SardanaShellWidget", "SardanaShell"]

__docformat__ = 'restructuredtext'

import os.path

from taurus.qt.qtgui.shell import SpockShell, SpockShellWidget

class SardanaShellWidget(SpockShellWidget):
    pass


class SardanaShell(SpockShell):
    SHELL_CLASS = SardanaShellWidget

    def _preprocess_arguments(self, args):
        return args

    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('fname'):
            startup_dir = os.path.dirname(os.path.abspath(__file__))
            kwargs['fname'] = os.path.join(startup_dir, 'startup.py')
        SpockShell.__init__(self, *args, **kwargs)

    @classmethod
    def getQtDesignerPluginInfo(cls):
        ret = SpockShell.getQtDesignerPluginInfo()
        ret['icon'] = ":/designer/sardanashell.png"
        ret['module'] = "taurus.qt.qtgui.extra_sardana"
        return ret


def main():
    import sys
    import os.path
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication
    
    app = Application.instance()
    owns_app = app is None
    
    if owns_app:
        import taurus.core.util.argparse
        parser = taurus.core.util.argparse.get_taurus_parser()
        parser.add_option("-p", "--profile", dest="profile")
        app = Application(sys.argv, cmd_line_parser=parser, 
                          app_name="Sardana Shell demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")

    options = app.get_command_line_options()

    if not options.profile:
        parser = app.get_command_line_parser()
        parser.error("must give a valid profile")
    
    from spyderlib.plugins.variableexplorer import VariableExplorer
    settings = VariableExplorer.get_settings()
    shell = SardanaShell(arguments="-p %s" % options.profile, stand_alone=settings)
    shell.resize(768,768)
    shell.show()
    
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == '__main__':
    main()
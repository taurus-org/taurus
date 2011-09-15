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

"""This module contains a taurus python shell widget. The widget starts a python
interpreter in a subprocess and gives a python/IPython shell"""

__all__ = ["TaurusPythonShellWidget", "TaurusPythonShell", "TaurusShell"]

__docformat__ = 'restructuredtext'

import os

from taurus.qt import Qt

try:
    import spyderlib
    if int(spyderlib.__version__.split(".")[0]) < 2:
        raise Exception("TaurusShell needs spyderlib >= 2.0")
except ImportError: 
    raise Exception("TaurusShell needs spyderlib >= 2.0")

import PyTango.ipython

if PyTango.Release.version_info[:3] < (7,1,4):
    raise Exception("TaurusShell needs PyTango >= 7.1.4")

from spyderlib.widgets.externalshell.pythonshell import ExtPythonShellWidget
from spyderlib.widgets.externalshell.pythonshell import ExternalPythonShell
from spyderlib.widgets.externalshell import startup
from spyderlib.utils.qthelpers import create_toolbutton, translate
from spyderlib.utils.qthelpers import create_action, add_actions

from taurus.qt.qtgui.resource import getIcon, getThemeIcon

# old PyTango (< 7.2) doesn't have get_ipython_profiles function
if not hasattr(PyTango.ipython, "get_ipython_profiles"):
    def get_ipython_profiles():
        """Helper functions to find ipython profiles"""
        ret = []
        if IPython is None:
            return ret
        ipydir = IPython.iplib.get_ipython_dir()
        if os.path.isdir(ipydir):
            for i in os.listdir(ipydir):
                fullname = os.path.join(ipydir, i)
                if i.startswith("ipy_profile_") and i.endswith(".py"):
                    if os.path.isfile(fullname):
                        ret.append(i[len("ipy_profile_"):i.rfind(".")])
        return ret
    PyTango.ipython.get_ipython_profiles = get_ipython_profiles
    
    
try:
    import IPython
    import IPython.iplib
except:
    IPython = None

try:
    import spocklib
    import spocklib.genutils
except:
    spocklib = None

class TaurusPythonShellWidget(ExtPythonShellWidget):
    pass


class TaurusPythonShell(ExternalPythonShell):
    """A python shell widget"""
    
    SHELL_CLASS = TaurusPythonShellWidget
    
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('ipython'):
            kwargs['ipython'] = IPython is not None
        ExternalPythonShell.__init__(self, *args, **kwargs)
        
        self.shell.toggle_wrap_mode(True)
        self.shell.set_font(Qt.QFont("Monospace", 8))
        self.start_shell(False)
        
        
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return { 
            'module'    : 'taurus.qt.qtgui.shell',
            'group'     : 'Taurus Composite Widgets',
            'icon'      : ":/designer/shell.png",
            'container' : False
        }


class TaurusShellWidget(ExtPythonShellWidget):
    pass


class TaurusShell(ExternalPythonShell):
    """A super duper python shell widget"""
    
    SHELL_CLASS = TaurusShellWidget
    
    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('ipython'):
            kwargs['ipython'] = True
        if not kwargs.has_key('stand_alone'):
            import spyderlib.plugins.variableexplorer
            VE = spyderlib.plugins.variableexplorer.VariableExplorer
            kwargs['stand_alone'] = VE.get_settings()
        self.profile_button = None
        self.profile_menu_actions = None
        self.sardana_menu = None
        
        ExternalPythonShell.__init__(self, *args, **kwargs)
        
        self.shell.toggle_wrap_mode(True)
        self.shell.set_font(Qt.QFont("Monospace", 8))
        self.start_shell(False)
    
    def get_toolbar_buttons(self):
        buttons = ExternalPythonShell.get_toolbar_buttons(self)
        if self.profile_button is None:
            profile = self.get_profile_menu()
            self.profile_button = create_toolbutton(self,
                    text=translate('ExternalShellBase', "Profile"),
                    icon=getIcon(':/categories/user-employee.svg'),
                    tip='Select shell profile',
                    text_beside_icon=True)
            self.profile_button.setPopupMode(Qt.QToolButton.InstantPopup)
            menu = Qt.QMenu(self)
            add_actions(menu, profile)
            self.profile_button.setMenu(menu)
            buttons.insert(0, self.profile_button)
        return buttons
    
    def get_profile_menu(self):
        if self.profile_menu_actions is None:
            self.profile_menu_actions = []
            
            # ------------------------------------------------------------------
            # IPython items
            # ------------------------------------------------------------------
            ipy_icon = getIcon(':/ipython.png')
            pyconsole_icon = getIcon(':/python-console.png')
            ipy_action = create_action(self, self.tr("IPython"),
                    icon=ipy_icon,
                    tip='Pure IPython shell',
                    data="/IPython",
                    triggered=self.on_select_ipython_profile)

            if spocklib is None:
                ipy_profiles = PyTango.ipython.get_ipython_profiles()
            else:
                ipy_profiles = spocklib.genutils.get_non_spock_profiles()
            ipy_profiles = sorted(ipy_profiles)
            
            # make sure the ITango profile is not there
            try: ipy_profiles.remove("spock")
            except: pass
            
            ipy_actions = []
            for profile in ipy_profiles:
                action = create_action(self, self.tr(profile),
                    icon=pyconsole_icon,
                    tip='IPython shell (%s profile)',
                    data=profile,
                    triggered=self.on_select_ipython_profile)
                ipy_actions.append(action)
            ipy_actions.append(None)
            ipy_actions.append(ipy_action)
            ipy_menu = Qt.QMenu("IPython")
            ipy_menu.setIcon(ipy_icon)
            add_actions(ipy_menu, ipy_actions)
            
            self.profile_menu_actions.append(ipy_menu)

            # ------------------------------------------------------------------
            # ITango items
            # ------------------------------------------------------------------
            tango_icon = getIcon(':/tango.png')
            tango_action = create_action(self, self.tr("Tango"),
                    icon=tango_icon,
                    tip='Tango shell',
                    data="/Tango",
                    triggered=self.on_select_tango_profile)

            self.profile_menu_actions.append(tango_action)

            # ------------------------------------------------------------------
            # Sardana items
            # ------------------------------------------------------------------
            if spocklib is not None and self.has_sardana():
                sardana_icon = getIcon(':/categories/user-digital-person.svg')
                sardana_profiles = spocklib.genutils.get_spock_profiles()
                sardana_profiles = sorted(sardana_profiles)
                sardana_actions = []
                for profile in sardana_profiles:
                    sardana_action = create_action(self, self.tr(profile),
                        icon=sardana_icon,
                        tip='Sardana shell (%s profile)' % profile,
                        data=profile,
                        triggered=self.on_select_sardana_profile)
                    sardana_actions.append(sardana_action)
                new_sardana_action = create_action(self, self.tr("New..."),
                        icon=getIcon(':/categories/user-other-new.svg'),
                        tip='Create a new sardana profile',
                        data="_New",
                        triggered=self.on_select_new_sardana_profile)
                sardana_actions.append(None) # separator
                sardana_actions.append(new_sardana_action)

                self.sardana_menu = Qt.QMenu("Sardana")
                self.sardana_menu.setIcon(sardana_icon)
                add_actions(self.sardana_menu, sardana_actions)
                self.profile_menu_actions.append(self.sardana_menu)
        return self.profile_menu_actions
    
    def restart_shell(self, ask_for_arguments=False):
        p = self.process
        if p is not None and p.state() == Qt.QProcess.Running:
            p.terminate()
            p.waitForFinished(3000)
        self.start_shell(ask_for_arguments=ask_for_arguments)
    
    def _get_default_ipython_startup_file(self):
        startup_file = startup.__file__
        if 'library.zip' in startup_file:
            # py2exe distribution
            from spyderlib.config import DATA_DEV_PATH
            startup_file = os.path.join(DATA_DEV_PATH, "widgets", "externalshell",
                                        "startup.py")
        return startup_file
    
    def on_select_ipython_profile(self):
        if not self.new_profile_dialog():
            return
        action_name = self.sender().data().toString()
        if action_name == "/IPython":
            self.arguments = ""
        else:
            self.arguments = "-p %s" % action_name
        self.fname = self._get_default_ipython_startup_file()
        self.restart_shell()
    
    def _get_default_tango_startup_file(self):
        return self._get_default_ipython_startup_file()
    
    def on_select_tango_profile(self):
        if not self.new_profile_dialog():
            return
        self.arguments = "-p spock"
        self.fname = self._get_default_tango_startup_file()
        self.restart_shell()

    def has_sardana(self):
        return os.path.isdir(self._get_sardana_dir())

    def _get_sardana_dir(self):
        d = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(d, "..", "extra_sardana")

    def _get_default_sardana_startup_file(self):
        return os.path.join(self._get_sardana_dir(), 'startup.py')

    def on_select_sardana_profile(self):
        if not self.new_profile_dialog():
            return
        action_name = self.sender().data().toString()
        self.arguments = "-p %s" % action_name
        self.fname = self._get_default_sardana_startup_file()
        self.restart_shell()
        
    def on_select_new_sardana_profile(self):
        if not self.new_profile_dialog():
            return
        self.fname = self._get_default_sardana_startup_file()
        
        # get profile from user
        if not self.get_arguments():
            self.set_running_state(False)
        if not self.arguments.startswith("-p "):
            self.arguments = "-p %s" % self.arguments
        self.restart_shell()
        
        try:
            args = self.arguments.split()
            for i, arg in enumerate(args):
                if arg == "-p":
                    profile = args[i+1]
        except:
            return
        
        sardana_icon = getIcon(':/categories/user-digital-person.svg')
        sardana_action = create_action(self, self.tr(profile),
            icon=sardana_icon,
            tip='Sardana shell (%s profile)' % profile,
            data=profile,
            triggered=self.on_select_sardana_profile)
        actions = self.sardana_menu.actions()
        if len(actions)>0:
            self.sardana_menu.insertAction(actions[0], sardana_action)
        else:
            self.sardana_menu.addAction(sardana_action)
            
    def new_profile_dialog(self):
        return Qt.QMessageBox.warning(self, "Are you sure?",
            "Changing the profile implies restarting the shell.\n" \
            "All local variables will be lost!",
            buttons=Qt.QMessageBox.Yes | Qt.QMessageBox.No,
            defaultButton=Qt.QMessageBox.Yes) == Qt.QMessageBox.Yes
            
    @classmethod
    def getQtDesignerPluginInfo(cls):
        return { 
            'module'    : 'taurus.qt.qtgui.shell',
            'group'     : 'Taurus Composite Widgets',
            'icon'      : ":/designer/shell.png",
            'container' : False
        }

def demo():
    """Shell"""

    from spyderlib.plugins.variableexplorer import VariableExplorer
    settings = VariableExplorer.get_settings()
    shell = TaurusShell()
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
                          app_name="Taurus Shell demo", app_version="1.0",
                          org_domain="Taurus", org_name="Tango community")

    shell = demo()
    
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w

if __name__ == '__main__':
    main()
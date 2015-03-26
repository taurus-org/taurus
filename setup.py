#!/usr/bin/env python

##############################################################################
##
## This file is part of Taurus
##
## http://taurus-scada.org
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
##############################################################################

from __future__ import print_function

import os
import sys
import copy
import shutil
import imp
import StringIO

from distutils import log
from distutils.core import setup, Command
from distutils.command.build import build as dftbuild
from distutils.command.install import install as dftinstall
from distutils.command.install_lib import install_lib as dftinstall_lib
from distutils.command.install_scripts import install_scripts as dftinstall_scripts

try:
    import sphinx
    import sphinx.util.console
    sphinx.util.console.color_terminal = lambda : False
except:
    sphinx = None

def abspath(*path):
    """A method to determine absolute path for a given relative path to the
    directory where this setup.py script is located"""
    setup_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(setup_dir, *path)

def get_release_info():
    name = "release"
    release_dir = abspath('lib', 'taurus', 'core')
    data = imp.find_module(name, [release_dir])
    release = imp.load_module(name, *data)
    return release

Release = get_release_info()

author = Release.authors['Tiago']
maintainer = Release.authors['Pascual-Izarra']

package_dir = { 'taurus' : abspath('lib', 'taurus') }

packages = [
    'taurus',
    'taurus.test',

    'taurus.external',
    'taurus.external.argparse',
    'taurus.external.enum',
    'taurus.external.ordereddict',
    'taurus.external.pint',
    'taurus.external.qt',
    'taurus.external.unittest',
    'taurus.external.test',

    'taurus.core',
    'taurus.core.util',
    'taurus.core.util.argparse',
    'taurus.core.util.decorator',
    'taurus.core.util.report',
    'taurus.core.utils',  # old, deprecated: maintain for compatibility

    'taurus.core.resource',

    'taurus.core.simulation',

    'taurus.core.evaluation',

    'taurus.core.tango',
    'taurus.core.tango.img',

    'taurus.console',
    'taurus.console.util',

    'taurus.qt',

    'taurus.qt.qtcore',
    'taurus.qt.qtcore.communication',
    'taurus.qt.qtcore.configuration',
    'taurus.qt.qtcore.mimetypes',
    'taurus.qt.qtcore.model',
    'taurus.qt.qtcore.tango',

    'taurus.qt.qtcore.util',

    'taurus.qt.qtdesigner',
    'taurus.qt.qtdesigner.taurusplugin',

    'taurus.qt.qtgui',
    'taurus.qt.qtgui.test',
    'taurus.qt.qtgui.application',
    'taurus.qt.qtgui.base',
    'taurus.qt.qtgui.button',
    'taurus.qt.qtgui.button.test',
    'taurus.qt.qtgui.button.test.res',
    'taurus.qt.qtgui.compact',
#    'taurus.qt.qtgui.console',
    'taurus.qt.qtgui.container',
    'taurus.qt.qtgui.dialog',
    'taurus.qt.qtgui.display',
    'taurus.qt.qtgui.display.test',
    'taurus.qt.qtgui.display.demo',
    'taurus.qt.qtgui.editor',
    'taurus.qt.qtgui.gauge',
    'taurus.qt.qtgui.gauge.demo',
    'taurus.qt.qtgui.graphic',
    'taurus.qt.qtgui.graphic.jdraw',
    'taurus.qt.qtgui.graphic.jdraw.test.res',
    'taurus.qt.qtgui.help',
    'taurus.qt.qtgui.image',
    'taurus.qt.qtgui.input',
    'taurus.qt.qtgui.model',
    'taurus.qt.qtgui.panel',
    'taurus.qt.qtgui.panel.test',
    'taurus.qt.qtgui.panel.report',
    'taurus.qt.qtgui.plot',
    'taurus.qt.qtgui.resource',
#    'taurus.qt.qtgui.shell',
    'taurus.qt.qtgui.style',
    'taurus.qt.qtgui.table',
    'taurus.qt.qtgui.taurusgui',
    'taurus.qt.qtgui.taurusgui.conf',
    'taurus.qt.qtgui.tree',
    'taurus.qt.qtgui.ui',
    'taurus.qt.qtgui.util',
    'taurus.qt.qtgui.util.test',
    'taurus.qt.qtgui.util.test.test_ui',
    'taurus.qt.uic',
]

extra_packages = [
    'taurus.qt.qtgui.extra_nexus',
    'taurus.qt.qtgui.extra_xterm',
    'taurus.qt.qtgui.extra_guiqwt',

    'taurus.qt.qtgui.taurusgui.conf.tgconf_example01',
    'taurus.qt.qtgui.taurusgui.conf.tgconf_macrogui',
    
    #For backwards compat. They may be removed later on:
    'taurus.qt.qtgui.extra_macroexecutor',
    'taurus.qt.qtgui.extra_sardana',
    'taurus.qt.qtgui.extra_pool',
]

provides = [
    'taurus',
    'taurus.core',
    'taurus.qt',
]

requires = [
    'numpy (>=1.1)',
    'PyTango (>=7.1)',
    'PyQt4 (>=4.4)',
    'PyQt4.Qwt5 (>=5.2.0)',   # plotting
    'ply (>=2.3)',            # jdraw parser
    'lxml (>=2.1)',           # tau2taurus, taurusuic4
    'spyder (>=2.2)',         # shell, editor
]

package_data = {
    'taurus.core.epics'        : ['__taurus_plugin__'],
    'taurus.core.evaluation'   : ['__taurus_plugin__'],
    'taurus.core.resource'     : ['__taurus_plugin__'],
    'taurus.core.simulation'   : ['__taurus_plugin__'],
    'taurus.core.tango'        : ['__taurus_plugin__'],

    'taurus.qt.qtgui.resource' : ['*.rcc'],
    'taurus.qt.qtgui.util'     : ['tauruswidget_template',
                                  'tauruswidget_qtdesignerplugin_template'],
    'taurus.qt.uic'            : ['pyuic4/*'],
    'taurus.qt.qtgui.taurusgui.conf.tgconf_example01' : ['images/*'],
    'taurus.qt.qtgui.button.test' : ['res/*'],
    'taurus.qt.qtgui.graphic.jdraw.test' : ['res/*'],
        
    'taurus.qt.qtgui.help': ['ui/*.ui'],
    'taurus.qt.qtgui.panel.report': ['ui/*.ui'],
    'taurus.qt.qtgui.panel': ['ui/*.ui'],
    'taurus.qt.qtgui.plot': ['ui/*.ui'],
    'taurus.qt.qtgui.taurusgui': ['ui/*.ui'],
    'taurus.qt.qtgui.extra_guiqwt': ['ui/*.ui'],
    'taurus.qt.qtgui.util.test.test_ui' : ['ui/*.ui', 'ui/mywidget2/*.ui'],
}


# The files listed here will be made executable when installed.
# The file names are relative to the dir containing setup.py
# Note: They must also be listed in packages or package_data
executable_data = [
    'taurus/qt/qtgui/button/test/res/Timeout',
]

# check if local implementations of enum and pint are here (debian removes them
# before running setup to avoid license issues)
if os.path.isdir(abspath('lib', 'taurus', 'external', 'enum', 'enum')):
    packages.append('taurus.external.enum.enum')
if os.path.isdir(abspath('lib', 'taurus', 'external', 'pint', 'pint')):
    packages.append('taurus.external.pint.pint')
    package_data['taurus.external.pint.pint'] = ['*.txt']
    

def get_script_files():
    scripts_dir = abspath('scripts')
    scripts = []
    for item in os.listdir(scripts_dir):
        # avoid hidden files
        if item.startswith("."):
            continue
        abs_item = os.path.join(scripts_dir, item)
        # avoid non files
        if not os.path.isfile(abs_item):
            continue
        # avoid files that have any extension
        if len(os.path.splitext(abs_item)[1]) > 0:
            continue
        scripts.append('scripts/' + item)
    return scripts

scripts = get_script_files()

data_files = [
]

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Win32 (MS Windows)',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Unix',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: User Interfaces',
    'Topic :: Software Development :: Widget Sets',
]


class build_resources(Command):

    description = "\"build\" Qt resource files"
    user_options = [('logo=', None, "alternative logo file (default is taurus.png)")]
    AllowedExt = ('svg', 'png', 'jpg', 'jpeg', 'gif')

    def initialize_options (self):
        self.resource_dir = abspath('lib', 'taurus', 'qt', 'qtgui', 'resource')
        self.taurus = os.path.join(self.resource_dir, 'taurus.png')
        self.logo = None  #os.path.join(self.resource_dir,'taurus.png')
        if self.distribution.verbose:
            self.out = sys.stdout
        else:
            self.out = StringIO.StringIO()

    def finalize_options (self):
        if self.logo is None:
            build = self.get_finalized_command('build')
            if build:
                self.logo = build.logo
            if self.logo is None:
                self.logo = self.taurus
        if not os.path.isabs(self.logo):
            self.logo = os.path.abspath(self.logo)
        self.logo = os.path.realpath(self.logo)

        if os.name == 'nt':
            try:
                self.QTDIR = os.environ["QTDIR"]
                self.rcc_exec = self.rcc_exec = os.path.join(self.QTDIR, 'bin', 'rcc')
            except KeyError:
                msg = "Cannot find QT installation. " \
                    "You should set the env. variable QTDIR " \
                    "pointing to the Qt C++ installation directory"
                if build.with_tango_icons:
                    msg += ". Skipping creation of rcc files"
                    print (msg, file=self.out, end='')
                    self.rcc_exec = None
                else:
                    msg += " or allow skipping creation of the rcc files by " \
                           "passing --with-tango-icons parameter to the build command"
                    raise Exception(msg)
        else:
            self.rcc_exec = 'rcc'

    def run(self):
        orig_dir = os.path.abspath(os.curdir)
        os.chdir(self.resource_dir)
        try:
            cur_dir = os.path.abspath(os.curdir)

            result = self._build_general_res()
            result2 = self._build_res(cur_dir)

            result[0].extend(result2[0])
            result[1].extend(result2[1])
        finally:
            os.chdir(orig_dir)

    def _build_general_res(self):
        qrc_filename = 'general.qrc'
        rcc_filename = 'qrc_general.rcc'
        out = self.out
        print("Generating %s... " % qrc_filename, file=out, end='')
        out.flush()
        f = file(qrc_filename, 'w')
        try:
            logo_relpath = os.path.relpath(self.logo)
            taurus_relpath = os.path.relpath(self.taurus)
            f.write('<RCC>\n    <qresource>\n')
            f.write('        <file alias="logo.png">%s</file>\n' % logo_relpath)
            f.write('        <file alias="taurus.png">%s</file>\n' % taurus_relpath)
            f.write('    </qresource>\n')
            f.write('</RCC>\n')
        except Exception, e:
            print("[FAILED]\nDescription:\n%s" % str(e), file=out)
            raise e
        finally:
            f.close()
        print("[DONE]", file=out)

        # Generate binary rcc file

        if self.rcc_exec:
            print("Generating %s... " % rcc_filename, file=out, end='')
            out.flush()
            cmd = '%s -binary %s -o %s' % (self.rcc_exec, qrc_filename, rcc_filename)
            if os.system(cmd):
                print("[FAILED]", file=out)
            else:
                print("[DONE]", file=out)

        return [ [qrc_filename], [rcc_filename]]

    def _build_res(self, abs_dir, bases=list()):
        """Builds the resources in the abs_dir recursively.
        The result is a list of 2 items:
            - a list of generated qrc files
            - a list of generated rcc files
        """
        result = [[], []]
        res_name = os.path.basename(abs_dir)
        local_elems, local_bases = [], copy.copy(bases)
        local_bases.append(res_name)
        out = self.out
        for elem in os.listdir(abs_dir):
            if elem.startswith('.'): continue
            abs_elem = os.path.abspath(os.path.join(abs_dir, elem))
            if os.path.isdir(abs_elem):
                ret = self._build_res(abs_elem, local_bases)
                result[0].extend(ret[0])
                result[1].extend(ret[1])
            elif os.path.splitext(abs_elem)[1][1:].lower() in build_resources.AllowedExt:
                local_elems.append(elem)

        if local_elems and local_bases[1:]:
            base_dir = os.path.join(*local_bases[1:])
            base_filename = "_".join(local_bases[1:])
            base_filename = base_filename.replace('-', '_')
            qrc_filename = base_filename + ".qrc"
            rcc_filename = 'qrc_' + base_filename + ".rcc"

            # Generate qrc file
            print("Generating %s... " % qrc_filename, file=out, end='')
            out.flush()
            f = file(qrc_filename, 'w')
            try:
                qres_prefix = ""
                if len(local_bases) > 2:
                    qres_prefix = "/" + "/".join(local_bases[2:])
                    f.write('<RCC>\n    <qresource prefix="%s">\n' % qres_prefix)
                else:
                    f.write('<RCC>\n    <qresource>\n')
                qres_prefix = ":" + qres_prefix
                qres_prefix += "/"
                for elem in local_elems:
                    rel_elem = os.path.join(base_dir, elem)
                    f.write('        <file alias="%s">%s</file>\n' % (elem, rel_elem))
                f.write('    </qresource>\n</RCC>')
            except Exception, e:
                print("[FAILED]\nDescription:\n%s" % str(e), file=out)
                raise e
            finally:
                f.close()
            result[0].append(qrc_filename)
            print("[DONE]", file=out)

            # Generate binary rcc file
            if self.rcc_exec:
                print("Generating %s... " % rcc_filename, file=out, end='')
                out.flush()
                cmd = '%s -binary %s -o %s' % (self.rcc_exec, qrc_filename, rcc_filename)
                if os.system(cmd):
                    print("[FAILED]", file=out)
                else:
                    result[1].append(rcc_filename)
                    print("[DONE]", file=out)

        return result


class build(dftbuild):

    user_options = dftbuild.user_options + \
        [('logo=', None, "alternative logo file (default is taurus.png)"),
         ('with-extra-widgets', None, "distribute extra widgets"),
         ('no-doc', None, "do not build documentation"),
         ('with-tango-icons', None, "add Tango icons too (not just *.rcc files)")]

    boolean_options = dftbuild.boolean_options + ['with-extra-widgets', 'no-doc']

    def initialize_options (self):
        dftbuild.initialize_options(self)
        self.logo = None
        self.doc_fmt = None
        self.no_doc = None
        self.with_tango_icons = None
        self.with_extra_widgets = True

    def finalize_options (self):
        dftbuild.finalize_options(self)
        if self.logo is None:
            self.logo = abspath('lib', 'taurus', 'qt', 'qtgui', 'resource', 'taurus.png')

    def run(self):
        self.build_package_data()
        self.build_jdraw()
        dftbuild.run(self)

    def build_package_data(self):
        packages = self.distribution.packages
        package_data = self.distribution.package_data
        if self.with_extra_widgets:
            packages.extend(extra_packages)
        resource_package_data = self.get_extra_resource_package_data()
        package_data['taurus.qt.qtgui.resource'].extend(resource_package_data)

    def build_jdraw(self):
        print("Building jdraw grammar...", end='')
        taurus_dir = abspath('lib')
        sys.path.insert(0, taurus_dir)
        try:
            from taurus.qt.qtgui.graphic.jdraw import jdraw_parser
            jdraw_parser.new_parser()
            print(" [DONE]")
        except:
            print("[ERROR]")
        finally:
            sys.path.pop(0)
        
    def has_doc(self):
        if self.no_doc:
            return False
        if not sphinx:
            print("Sphinx not available: Documentation will not be build!")
            return False
        return os.path.isdir(abspath('doc'))

    def has_resources(self):
        return os.path.isdir(abspath('lib', 'taurus', 'qt', 'qtgui', 'resource'))

    def get_extra_resource_package_data(self):
        data = []
        import PyQt4.Qt
        if self.with_tango_icons or not hasattr(PyQt4.Qt.QIcon, "fromTheme"):
            tango_icons_dir = abspath('lib', 'taurus', 'qt', 'qtgui', 'resource',
                                      'tango-icons')
            for tango_icon_item in os.listdir(tango_icons_dir):
                if tango_icon_item.startswith("."):
                    continue
                abs_item = os.path.join(tango_icons_dir, tango_icon_item)
                if not os.path.isdir(abs_item):
                    continue
                data.append('tango-icons/%s/*' % tango_icon_item)
        return data

    sub_commands = [('build_resources', has_resources)] + \
                   dftbuild.sub_commands + \
                   [('build_doc', has_doc)]


class install_man(Command):

    user_options = [
        ('install-dir=', 'd', 'base directory for installing man page files')]

    def initialize_options(self):
        self.install_dir = None

    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('install_man', 'install_dir'))

    def run(self):
        src_man_dir = abspath('doc', 'man')
        man_elems = os.listdir(src_man_dir)
        man_pages = []
        for f in man_elems:
            f = os.path.join(src_man_dir, f)
            if not os.path.isfile(f): continue
            if not f.endswith(".1"): continue
            man_pages.append(f)

        install_dir = os.path.join(self.install_dir, 'man1')

        if not os.path.isdir(install_dir):
            os.makedirs(install_dir)

        for man_page in man_pages:
            self.copy_file(man_page, install_dir)


class install_html(Command):

    user_options = [
        ('install-dir=', 'd', 'base directory for installing HTML documentation files')]

    def initialize_options(self):
        self.install_dir = None

    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('install_html', 'install_dir'))

    def run(self):
        build_doc = self.get_finalized_command('build_doc')
        src_html_dir = abspath(build_doc.build_dir, 'html')
        self.copy_tree(src_html_dir, self.install_dir)


class install_scripts(dftinstall_scripts):
    '''Customization to create .bat wrappers for the scripts 
    when installing on windows.
    Adapted from a recipe by Matthew Brett (who licensed it under CC0):
    https://github.com/matthew-brett/myscripter/blob/master/setup.py
    See rationale in: 
    http://matthew-brett.github.io/pydagogue/installing_scripts.html
    '''

    user_options = list(dftinstall_scripts.user_options)
    user_options.extend(
            [
             ('wrappers', None, 'Install .bat wrappers for windows (enabled by default on windows)'),
             ('ignore-shebang', None, 'Use "python" as the interpreter in .bat wrappers (instead of using the interpreter found in the shebang line of the scripts). Note: this only affects to windows .bat wrappers!'),
             ])


    BAT_TEMPLATE_SHEBANG = \
r"""@echo off
REM wrapper to use shebang first line of {FNAME}
set mypath=%~dp0
set pyscript="%mypath%{FNAME}"
set /p line1=<%pyscript%
if "%line1:~0,2%" == "#!" (goto :goodstart)
echo First line of %pyscript% does not start with "#!"
exit /b 1
:goodstart
set py_exe=%line1:~2%
call %py_exe% %pyscript% %*
"""
    BAT_TEMPLATE_PATH = \
r"""@echo off
REM wrapper to launch {FNAME}
set mypath=%~dp0
set pyscript="%mypath%{FNAME}"
set py_exe="python"
call %py_exe% %pyscript% %*
"""

    def initialize_options(self):
        self.ignore_shebang = None
        self.wrappers = (os.name == "nt")
        dftinstall_scripts.initialize_options(self)

    def run(self):
        dftinstall_scripts.run(self)
        if self.wrappers:
            for filepath in self.get_outputs():
                # If we can find an executable name in the #! top line of the script
                # file, make .bat wrapper for script.
                with open(filepath, 'rt') as fobj:
                    first_line = fobj.readline()
                if not (first_line.startswith('#!') and
                        'python' in first_line.lower()):
                    print("No #!python executable found, skipping .bat wrapper")
                    continue
                pth, fname = os.path.split(filepath)
                froot, ext = os.path.splitext(fname)
                bat_file = os.path.join(pth, froot + '.bat')
                if self.ignore_shebang:
                    template = self.BAT_TEMPLATE_PATH
                else:
                    template = self.BAT_TEMPLATE_SHEBANG
                bat_contents = template.replace('{FNAME}', fname)
                print("Making %s wrapper for %s" % (bat_file, filepath))
                if self.dry_run:
                    continue
                with open(bat_file, 'wt') as fobj:
                    fobj.write(bat_contents)


class install_lib(dftinstall_lib):  
    def run(self):
        dftinstall_lib.run(self)
        # Set the executable bits (owner, group, and world) on
        # all executable_data
        exe_ouput = [os.path.join(self.install_dir,f) for f in executable_data]
        if os.name == 'posix':
            for fn in self.get_outputs():
                if fn in exe_ouput:
                    if self.dry_run:
                        log.info("changing mode of %s", fn)
                    else:
                        mode = ((os.stat(fn).st_mode) | 0555) & 07777
                        log.info("changing mode of %s to %o", fn, mode)
                        os.chmod(fn, mode)


class install(dftinstall):

    user_options = list(dftinstall.user_options)
    user_options.extend([
            ('install-man=', None, 'installation directory for Unix man pages'),
            ('install-html=', None, "installation directory for HTML documentation"),
            ('no-doc', None, "do not install HTML documentation")])

    def initialize_options(self):
        self.install_man = None
        self.install_html = None
        self.no_doc = None
        dftinstall.initialize_options(self)

    def finalize_options(self):

        # We do a hack here. We cannot trust the 'install_base' value because it
        # is not always the final target. For example, in unix, the install_base
        # is '/usr' and all other install_* are directly relative to it. However,
        # in unix-local (like ubuntu) install_base is still '/usr' but, for
        # example, install_data, is '$install_base/local' which breaks everything.
        #
        # The hack consists in using install_data instead of install_base since
        # install_data seems to be, in practice, the proper install_base on all
        # different systems.

        dftinstall.finalize_options(self)
        if os.name != "posix":
            if self.install_man is not None:
                self.warn("install-man option ignored on this platform")
                self.install_man = None
        else:
            if self.install_man is None:
                self.install_man = os.path.join(self.install_data, 'share', 'man')
        if self.install_html is None:
            self.install_html = os.path.join(self.install_data, 'share', 'doc', 'taurus', 'html')
        if self.no_doc is None:
            self.no_doc = False
        self.dump_dirs("Installation directories")

    def expand_dirs(self):
        dftinstall.expand_dirs(self)
        self._expand_attrs(['install_man'])

    def has_man(self):
        return os.name == "posix"

    def has_html(self):
        if self.no_doc:
            return False
        return sphinx is not None

    sub_commands = list(dftinstall.sub_commands)
    sub_commands.append(('install_man', has_man))
    sub_commands.append(('install_html', has_html))


cmdclass = { 'build' : build,
             'build_resources' : build_resources,
             'install' : install,
             'install_lib': install_lib,
             'install_man' : install_man,
             'install_html' : install_html,
             'install_scripts' : install_scripts}

if sphinx:
    from sphinx.setup_command import BuildDoc

    class build_catalog(object):
        '''builds an html catalog of icons. It links to png thumbnails that are 
        created in the _static dir
        '''

        AllowedExt = build_resources.AllowedExt

        HTML_IL = '<tr height="30">' \
                  '<td width="30" align="center">' \
                     '<img width="24" src="{thumbnail}"' \
                                    ' alt="{res_relpath}"/></td>' \
                  '<td width="400">{qres_prefix}{icon_name}</td>' \
                  '<td width="400">{res_relpath}</td>' \
                  '<td width="200">{theme}</td></tr>\n'
        HTML_T = '<table border="1" cellspacing="0" cellpadding="2">\n' \
                 '<th colspan="4">Resource: "%s" Directory: "%s"</th>\n' \
                 '<tr><th>Preview</th><th>Resouce</th><th>File name</th>' \
                 '<th>Theme</th></tr>\n'

        def run(self):
            self.resource_dir = abspath('lib', 'taurus', 'qt', 'qtgui', 
                                        'resource')
            pngs_dir = os.path.abspath(os.path.join(self.builder_target_dir,
                                                    '_static', 
                                                    'icon_thumbnails') )
            devel_dir = os.path.abspath(os.path.join(self.builder_target_dir,
                                                     'devel') )
            self.thumbnails_relpath = os.path.relpath(pngs_dir, devel_dir)
            
            orig_dir = os.path.abspath(os.curdir)
            os.chdir(self.resource_dir)
            
            # create temporary catalog file (to be removed at end of build_doc)
            catalog = file(self.fname, 'w')
            catalog.write("<html><head>\n<title>taurus Icon Catalog</title>\n" \
            "<style>table { border-collapse: collapse; }</style>\n</head>\n<body>\n")

            try:
                cur_dir = os.path.abspath(os.curdir)

                result = self._build_general_res()
                result2 = self._build_res(cur_dir)

                result[0].extend(result2[0])
                result[1].extend(result2[1])

                catalog.write("<h1>Index</h1>\n<ul>")
                for anchor in result[1]:
                    catalog.write("<li>%s</li>\n" % anchor)
                catalog.write("</ul>\n")
                catalog.writelines(result[0])
            finally:
                catalog.write("""</body></html>""")
                catalog.close()
                os.chdir(orig_dir)
            
            #make thumbnails 
            try:
                if self.thumbnails_source == 'wand':
                    from wand.image import Image
                    def transform(ifname, ofname):
                        with Image(filename=ifname) as img:
                            img.transform(resize='24x')
                            img.save(filename=ofname)
                            return True
                        return False
                elif self.thumbnails_source == 'qt':
                    import PyQt4.Qt
                    if PyQt4.Qt.qApp.instance() is None:
                        self.app = PyQt4.Qt.QApplication([])
                    from PyQt4 import Qt
                    def transform(ifname, ofname):
                        pixmap = Qt.QPixmap(ifname)
                        p = pixmap.scaledToWidth(24, Qt.Qt.SmoothTransformation)
                        return p.save(ofname)
                else:
                    if not os.path.isabs(self.thumbnails_source):
                        m = 'Absolute path required for Thumbnails dir or zip'
                        raise ValueError(m)
                    shutil.rmtree(pngs_dir, ignore_errors=True)
                    if self.thumbnails_source.lower().endswith('.zip'):
                        from zipfile import ZipFile
                        zfile = ZipFile(self.thumbnails_source)
                        zfile.extractall(pngs_dir)
                    else:
                        shutil.copytree(self.thumbnails_source, pngs_dir)
                    def transform(ifname, ofname):
                        #just check if the required thumbnail exists
                        return os.path.isfile(ofname) 

                print("\tCreating PNG thumbnails for icon catalog")
                os.path.walk(self.resource_dir, self._make_thumbnails, 
                             (self.resource_dir, pngs_dir, transform) )
                # create a zipped file for the thumbnails
                fname = abspath('doc', '~thumbnails.zip')
                if os.path.isfile(fname):
                    os.remove(fname)
                self._zipdir(pngs_dir, fname) 
                
            except ImportError, e:
                print("\tCannot create PNG thumbnails for icon catalog: %s" %
                       repr(e))
                
        @staticmethod
        def _make_thumbnails(arg, dirname, fnames):
            '''create thumbnails. To be called by a walker'''
            resource, target, transform = arg
            relpath = os.path.relpath(dirname, start=resource)
            path = os.path.join(target, relpath)
            if not os.path.isdir(path):
                os.makedirs(path)
            for fname in fnames:
                fbase, f_ext = os.path.splitext(fname)
                if f_ext[1:] in build_catalog.AllowedExt:
                    full_source_fname = os.path.join(dirname, fname)
                    target_fname = fbase + ".png"
                    full_target_fname = os.path.join(path, target_fname)
                    if not os.path.isfile(full_target_fname):
                        ok = transform(full_source_fname, full_target_fname)
                        print(ok and "[OK]" or "[FAIL]", full_source_fname, 
                              '->', full_target_fname)
        
        @staticmethod                
        def _zipdir(basedir, archivename):
            '''function to zip the contents of basedir into archivename. 
            Adapted from: http://stackoverflow.com/questions/296499
            '''
            from zipfile import ZipFile, ZIP_DEFLATED
            from contextlib import closing
            assert os.path.isdir(basedir)
            with closing(ZipFile(archivename, "w", ZIP_DEFLATED)) as z:
                for root, dirs, files in os.walk(basedir):
                    #NOTE: ignore empty directories
                    for fn in files:
                        absfn = os.path.join(root, fn)
                        zfn = absfn[len(basedir)+len(os.sep):] 
                        z.write(absfn, zfn)
                        
        def getThemeIcon(self, resource):
            try:
                import PyQt4.Qt
                if not hasattr(PyQt4.Qt.QIcon, "hasThemeIcon"):
                    return "Unknown"
                i = resource.rfind("/")
                if i >= 0: resource = resource[i + 1:]
                i = resource.rfind(".")
                if i >= 0: resource = resource[:i]
                if PyQt4.Qt.QIcon.hasThemeIcon(resource):
                    return resource
                return "No"
            except:
                return "Unknown"

        def _build_general_res(self):
            out = self.out
            html = '<h2><a name="_base">Base icons</a></h2>\n'
            html += self.HTML_T % (':/', '')
            anchor = '<a href="#_base">Base icons</a>'
            try:
                taurus_relpath = 'taurus.png'
                png_relpath = os.path.join(self.thumbnails_relpath, 
                                           taurus_relpath)
                html += self.HTML_IL.format(thumbnail=png_relpath,
                                            res_relpath=taurus_relpath,
                                            qres_prefix=":/",
                                            icon_name=taurus_relpath,
                                            theme=self.getThemeIcon("taurus.png")
                                            )
            except Exception, e:
                print("[FAILED]\nDescription:\n%s" % str(e), file=out)
                import traceback
                traceback.print_exc()
                raise e
            finally:
                html += '</table>\n'

            return [ [html], [anchor] ]

        def _build_res(self, abs_dir, bases=list()):
            """Builds the resources in the abs_dir recursively.
            The result is a list of 5 items:
                - a list of HTML strings
                - a list of HTML anchors
            """
            result = [[], []]
            res_name = os.path.basename(abs_dir)
            local_elems, local_bases = [], copy.copy(bases)
            local_bases.append(res_name)
            out = self.out
            for elem in os.listdir(abs_dir):
                if elem.startswith('.'): continue
                abs_elem = os.path.abspath(os.path.join(abs_dir, elem))
                if os.path.isdir(abs_elem):
                    ret = self._build_res(abs_elem, local_bases)
                    result[0].extend(ret[0])
                    result[1].extend(ret[1])
                elif os.path.splitext(abs_elem)[1][1:].lower() in build_resources.AllowedExt:
                    local_elems.append(elem)

            if local_elems and local_bases[1:]:
                base_dir = os.path.join(*local_bases[1:])
                base_filename = "_".join(local_bases[1:])
                base_filename = base_filename.replace('-', '_')

                html = ''
                anchor = ''
                try:
                    qres_prefix = ""
                    if len(local_bases) > 2:
                        qres_prefix = "/" + "/".join(local_bases[2:])
                    qres_prefix = ":" + qres_prefix
                    qres_prefix += "/"

                    html += '<h2><a name="%s">%s (%s)</a></h2>\n' % (base_dir, qres_prefix, base_dir)
                    html += self.HTML_T % (qres_prefix , base_dir)
                    anchor = '<a href="#%s">%s (%s)</a>' % (base_dir, base_dir, qres_prefix)
                    for elem in local_elems:
                        rel_elem = os.path.join(base_dir, elem)
                        base_elem, _ = os.path.splitext(rel_elem)
                        png_relpath = os.path.join(self.thumbnails_relpath,
                                                   base_elem + ".png")
                        html += self.HTML_IL.format(thumbnail=png_relpath,
                                                    res_relpath=rel_elem,
                                                    qres_prefix=qres_prefix,
                                                    icon_name=rel_elem,
                                                    theme=self.getThemeIcon(elem)
                                                    )
                except Exception, e:
                    print("[FAILED]\nDescription:\n%s" % str(e), file=out)
                    raise e
                finally:
                    html += '</table>\n'
                result[0].append(html)
                result[1].append(anchor)
            return result
        

    class build_doc(BuildDoc):
        user_options = BuildDoc.user_options + \
                     [('thumbnails-source=', None, 
                       ('Source for catalog thumbnails. Use "qt" for ' +
                        'transforming the icons in the resource dir using ' +
                        'QPixmap  (this is the default). Use "wand" to ' +
                        'transform using the wand module. Or provide an ' +
                        'absolute path to either a dir or a zipfile ' +
                        'containing a tree of pre-transformed thumbnails') ),
                      ('skip-api', None, 'skip api doc creation'),
                      ('skip-catalog', None, 'skip icon catalog creation')
                      ]
        boolean_options = BuildDoc.boolean_options + ['skip-api',
                                                      'skip-catalog'
                                                      ]

        def initialize_options (self):
            BuildDoc.initialize_options(self)
            self.thumbnails_source = 'qt'
            self.skip_api = False
            self.skip_catalog = False

        def run(self):
            try:
                return self.doit()
            except Exception, e:
                self.warn("Failed to build doc. Reason: %s" % str(e))

        def _build_doc_api(self, api_dir, doc_dir):
            if self.skip_api:
                return

            #import auto_rst4api from the doc dir
            name = 'auto_rst4api'
            data = imp.find_module(name, [doc_dir])
            auto_rst4api = imp.load_module(name, *data)
            API_Creator = auto_rst4api.Auto_rst4API_Creator
            
            # prepare api creator
            excl = ['_[^\.]*[^_]', '.*.extra_sardana', '.*.extra_pool', 
                    '.*.extra_macroexecutor', 'taurus.external']
            rstCreator = API_Creator(exclude_patterns=excl,
                                     templatespath=doc_dir,
                                     overwrite_old=True,
                                     verbose=self.distribution.verbose)
            # clean previously existing rst files
            rstCreator.cleanAutogenerated(api_dir)
            
            # generate api
            # IMPORTANT: 'taurus' here is already the one from source, since we went 
            #            through doc/conf.py already and inserted the lib dir in the
            #            path
            import taurus
            r = rstCreator.documentModule('taurus', api_dir)
            
            # report
            print("Auto Creation of API docs Finished with %i warnings:" % len(r))
            for i in r:
                print(i)
                
        def _build_catalog(self, fname):
            if self.skip_catalog:
                return            
            catalog = build_catalog()
            catalog.fname = fname
            catalog.builder_target_dir = self.builder_target_dir
            catalog.thumbnails_source = self.thumbnails_source
            catalog.verbose = self.distribution.verbose
            catalog.out = self.out
            catalog.run()
        
        def doit(self):
            if self.distribution.verbose:
                self.out = sys.stdout
            else:
                self.out = StringIO.StringIO()
            
            _catalog_file = abspath('doc', 'source', 'devel', 'catalog.html')
            _api_dir = abspath('doc', 'source', 'devel', 'api')
            _lib_dir = abspath('lib')
            _doc_dir = abspath('doc')
            _mock_path = os.path.join(_doc_dir, 'mock.zip') 
            # append mock dir to the sys path (mocks will be used if needed)
            sys.path.append(_mock_path)
            # Import taurus from src distribution
            sys.path.insert(0, os.path.abspath(_lib_dir))
                
            try:
                for cmd_name in self.get_sub_commands():
                    self.run_command(cmd_name)
                self._build_doc_api(_api_dir, _doc_dir)
                self._build_catalog(_catalog_file)
                BuildDoc.run(self)
            finally:
                sys.path.pop(0)
                print('Removing temporary api dir: ', _api_dir)
                shutil.rmtree(_api_dir, ignore_errors=True)
                print('Removing temporary catalog file', _catalog_file)
                try:
                    os.remove(_catalog_file)
                except:
                    pass

    cmdclass['build_doc'] = build_doc



def main():
    setup(name='taurus',
          version=Release.version,
          description=Release.description,
          long_description=Release.long_description,
          author=author[0],
          author_email=author[1],
          maintainer=maintainer[0],
          maintainer_email=maintainer[1],
          url=Release.url,
          download_url=Release.download_url,
          platforms=Release.platforms,
          license=Release.license,
          packages=packages,
          package_dir=package_dir,
          classifiers=classifiers,
          package_data=package_data,
          data_files=data_files,
          scripts=scripts,
          provides=provides,
          keywords=Release.keywords,
          requires=requires,
          cmdclass=cmdclass)

if __name__ == "__main__":
    try:
        main()
        print("Setup finished")
    except Exception as e:
        print("A error occured: %s\n\nSetup aborted" % str(e))

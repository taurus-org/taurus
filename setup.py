#!/usr/bin/env python

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

from __future__ import print_function

import os
import imp

from distutils.core import setup, Command
from distutils.command.build import build as dftbuild
from distutils.command.install import install as dftinstall
from distutils.command.install_scripts import install_scripts as dftinstall_scripts
from distutils.version import StrictVersion as V

try:
    import sphinx
    import sphinx.util.console
    sphinx.util.console.color_terminal = lambda: False
    if V(sphinx.__version__) < V("1.0.0") \
       or V(sphinx.__version__) == V("1.2.0"):
        print("Sphinx documentation can not be compiled"
              " with sphinx < 1.0.0 or the 1.2.0 version")
        sphinx = None
except ImportError:
    sphinx = None


def abspath(*path):
    """A method to determine absolute path for a given relative path to the
    directory where this setup.py script is located"""
    setup_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(setup_dir, *path)


def get_release_info():
    name = "release"
    release_dir = abspath('src', 'sardana')
    data = imp.find_module(name, [release_dir])
    release = imp.load_module(name, *data)
    return release


class build(dftbuild):

    user_options = dftbuild.user_options + \
        [('no-doc', None, "do not build documentation")]

    boolean_options = dftbuild.boolean_options + ['no-doc']

    def initialize_options(self):
        dftbuild.initialize_options(self)
        self.no_doc = None

    def finalize_options(self):
        dftbuild.finalize_options(self)

    def run(self):
        dftbuild.run(self)

    def has_doc(self):
        if self.no_doc:
            return False
        if not sphinx:
            print("Sphinx not available: Documentation will not be build!")
            return False
        return os.path.isdir(abspath('doc'))

    sub_commands = dftbuild.sub_commands + [('build_doc', has_doc)]


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
        ('install-dir=', 'd',
         'base directory for installing HTML documentation files')]

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


class install(dftinstall):

    user_options = list(dftinstall.user_options)
    user_options.extend([
        ('install-man=', None, 'install directory for Unix man pages'),
        ('install-html=', None, "install directory for HTML documentation")])

    def initialize_options(self):
        self.install_man = None
        self.install_html = None
        dftinstall.initialize_options(self)

    def finalize_options(self):

        # We do a hack here. We cannot trust the 'install_base' value
        # because it is not always the final target. For example, in
        # unix, the install_base is '/usr' and all other install_* are
        # directly relative to it. However, in unix-local (like
        # ubuntu) install_base is still '/usr' but, for example,
        # install_data, is '$install_base/local' which breaks
        # everything.
        #
        # The hack consists in using install_data instead of
        # install_base since install_data seems to be, in practice,
        # the proper install_base on all different systems.

        dftinstall.finalize_options(self)
        if os.name != "posix":
            if self.install_man is not None:
                self.warn("install-man option ignored on this platform")
                self.install_man = None
        elif self.install_man is None:
            self.install_man = os.path.join(self.install_data,
                                            'share', 'man')
        if self.install_html is None:
            self.install_html = os.path.join(self.install_data,
                                             'share', 'doc', 'sardana', 'html')

    def expand_dirs(self):
        dftinstall.expand_dirs(self)
        self._expand_attrs(['install_man'])

    def has_man(self):
        return os.name == "posix"

    def has_html(self):
        return sphinx is not None

    sub_commands = list(dftinstall.sub_commands)
    sub_commands.append(('install_man', has_man))
    sub_commands.append(('install_html', has_html))


cmdclass = {'build': build,
            'install': install,
            'install_man': install_man,
            'install_html': install_html,
            'install_scripts' : install_scripts}

if sphinx:
    from sphinx.setup_command import BuildDoc

    class build_doc(BuildDoc):

        def has_doc_api(self):
            return True

        def run(self):
            try:
                return self.doit()
            except Exception, e:
                self.warn("Failed to build doc. Reason: %s" % str(e))

        def doit(self):
            BuildDoc.run(self)

    cmdclass['build_doc'] = build_doc


def main():
    Release = get_release_info()

    author = Release.authors['Tiago']
    maintainer = Release.authors['Reszela']

    package_dir = {'sardana': abspath('src', 'sardana')}

    packages = [
        'sardana',

        'sardana.util',
        'sardana.util.motion',

        'sardana.pool',
        'sardana.pool.poolcontrollers',

        'sardana.macroserver',
        'sardana.macroserver.macros',
        'sardana.macroserver.macros.examples',
        'sardana.macroserver.scan',
        'sardana.macroserver.scan.recorder',

        'sardana.tango',
        'sardana.tango.core',
        'sardana.tango.pool',
        'sardana.tango.macroserver',

        'sardana.spock',
        'sardana.spock.ipython_00_10',
        'sardana.spock.ipython_00_11',
    ]

    provides = [
        'sardana',
        'sardana.pool',
        'sardana.macroserver',
        'sardana.spock',
        'sardana.tango',
    ]

    requires = [
        'PyTango (>=7.2.3)',
        'taurus (>= 3.1)',
        'lxml (>=2.1)',
        'ipython (>=0.10, !=0.11)'
    ]

    scripts = [
        "scripts/h5toascii",
        "scripts/h5tospec",
        "scripts/MacroServer",
        "scripts/Pool",
        "scripts/Sardana",
        "scripts/spectoascii",
        "scripts/spock"
    ]

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
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
    ]

    setup(name='sardana',
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
          scripts=scripts,
          provides=provides,
          keywords=Release.keywords,
          requires=requires,
          cmdclass=cmdclass)

if __name__ == "__main__":
    main()

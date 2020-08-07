#!/usr/bin/env python

##############################################################################
##
# This file is part of Taurus
##
# http://taurus-scada.org
##
# Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
##
# Taurus is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# Taurus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

import sys
from setuptools import setup, find_packages


def get_release_info():
    if sys.version_info >= (3, 5):
        from importlib.util import spec_from_file_location, module_from_spec
        from pathlib import Path
        path = Path(__file__).parent / 'lib' / 'taurus' / 'core' / 'release.py'
        spec = spec_from_file_location('release', path.as_posix())
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
    else:  # for py27
        import os
        import imp
        module_name = "release"
        setup_dir = os.path.dirname(os.path.abspath(__file__))
        release_dir = os.path.join(setup_dir, 'lib', 'taurus', 'core')
        data = imp.find_module(module_name, [release_dir])
        module = imp.load_module(module_name, *data)
    return module


release = get_release_info()

package_dir = {'': 'lib'}

packages = find_packages(where='lib')

provides = [
    'taurus',
]

install_requires = [
    'numpy>=1.1',
    'pint>=0.8',
    'future',
    'click',
    'enum34;python_version<"3.4"',
]

extras_require = {
    'taurus-qt': [# 'PyQt4 >=4.8',
                  # 'PyQt4.Qwt5 >=5.2.0',
                  'ply >=2.3',  # synoptics
                  'lxml >=2.1',  # taurusgui
                  'guiqwt >=3',  # extra_guiqwt
                  ],
    'taurus-tango': ['PyTango >=7.1',
                     ],
    'taurus-epics': ['pyepics >=3.2.4',
                     ],
    'taurus-h5file': ['h5file',
                      ],
    # separate the editor from 'taurus-qt' to avoid forcing spyder>3
    # which implies many more dependencies that may be hard on older system
    'taurus-qt-editor': ['spyder >=3',
                         ],
}

console_scripts = [
    'taurus = taurus.cli:main',
]

taurus_subcommands = [
    'testsuite = taurus.test.testsuite:testsuite_cmd',
    'config = taurus.qt.qtgui.panel.taurusconfigeditor:config_cmd',
    'qwt5 = taurus.qt.qtgui.qwt5.cli:qwt5',
    'device = taurus.qt.qtgui.panel.taurusdevicepanel:device_cmd',
    'panel = taurus.qt.qtgui.panel.taurusdevicepanel:panel_cmd',
    'gui = taurus.qt.qtgui.taurusgui.taurusgui:gui_cmd',
    'newgui = taurus.qt.qtgui.taurusgui.taurusgui:newgui_cmd',
    'designer = taurus.qt.qtdesigner.taurusdesigner:designer_cmd',
    'guiqwt = taurus.qt.qtgui.extra_guiqwt.cli:guiqwt',
    'icons = taurus.qt.qtgui.icon.catalog:icons_cmd',
    'form = taurus.qt.qtgui.panel.taurusform:form_cmd',
    'demo = taurus.qt.qtgui.panel.taurusdemo:demo_cmd',
    'logmon = taurus.core.util.remotelogmonitor:logmon_cmd',
    'qlogmon = taurus.qt.qtgui.table.qlogtable:qlogmon_cmd',
    'check-deps = taurus.core.taurushelper:check_dependencies_cmd',
    'plot = taurus.cli.alt:plot_cmd',
    'trend = taurus.cli.alt:trend_cmd',
    'trend2d = taurus.cli.alt:trend2d_cmd',
    'image = taurus.cli.alt:image_cmd',
]

plot_alternatives = [
    "qwt5 = taurus.qt.qtgui.qwt5:TaurusPlot",
]

trend_alternatives = [
    "qwt5 = taurus.qt.qtgui.qwt5:TaurusTrend",
]

trend2d_alternatives = [
    "guiqwt = taurus.qt.qtgui.extra_guiqwt:TaurusTrend2DDialog",
]

image_alternatives = [
    "guiqwt = taurus.qt.qtgui.extra_guiqwt:TaurusImageDialog",
]

model_selectors = [
    'Tango = taurus.qt.qtgui.panel.taurusmodelchooser:TangoModelSelectorItem',
]

formatters = [
    'taurus = taurus.qt.qtgui.base:defaultFormatter',
    'tango = taurus.core.tango.util:tangoFormatter',
    '{:2.3e} = taurus.qt.qtgui.base:expFormatter',
    '{:.5f} = taurus.qt.qtgui.base:floatFormatter',
]

entry_points = {
    'console_scripts': console_scripts,
    'taurus.cli.subcommands': taurus_subcommands,
    'taurus.model_selector.items': model_selectors,
    'taurus.qt.formatters': formatters,
    'taurus.plot.alts': plot_alternatives,
    'taurus.trend.alts': trend_alternatives,
    'taurus.trend2d.alts': trend2d_alternatives,
    'taurus.image.alts': image_alternatives,
}

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Win32 (MS Windows)',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
    'Natural Language :: English',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Unix',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: User Interfaces',
    'Topic :: Software Development :: Widget Sets',
]


setup(name='taurus',
      version=release.version,
      description=release.description,
      long_description=release.long_description,
      author=release.authors['Tiago_et_al'][0],
      maintainer=release.authors['Community'][0],
      maintainer_email=release.authors['Community'][1],
      url=release.url,
      download_url=release.download_url,
      platforms=release.platforms,
      license=release.license,
      keywords=release.keywords,
      packages=packages,
      package_dir=package_dir,
      classifiers=classifiers,
      include_package_data=True,
      entry_points=entry_points,
      provides=provides,
      python_requires='>=2.7',
      install_requires=install_requires,
      extras_require=extras_require,
      test_suite='taurus.test.testsuite.get_taurus_suite',
      )

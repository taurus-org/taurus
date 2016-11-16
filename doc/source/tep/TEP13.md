    Title: plugins support 
    TEP: 13
    State: DRAFT
    Date: 2015-03-25
    Drivers: Carlos Pascual-Izarra <cpascual@cells.es>
    URL: http://www.taurus-scada.org/tep?TEP13.md
    License: http://www.jclark.com/xml/copying.txt
    Abstract:
     Implement support for managing third-party code 
     (plugins) to extends Taurus. Identify, document,
     unify and systematise the various existing 
     approaches to plugins already found in Taurus, 
     and provide conventions and tools for creating more
     entry points in the future.
    

IMPORTANT
=========

This is still in pre-draft stage. For now we are using this this wiki page to collect various preparatory notes in order to write the proper drafts for TEP13


Introduction
============

At this moment, different mechanisms to support extensions are already implemented in various subsystems of Taurus (see APPENDIX IV). Most of these mechanisms, being ad-hoc implementations, are quite specific and present limitations such as requiring the plugin to have privileged access to Taurus installation directories, or not having a well defined interface, or not allowing to define dependencies/incompatibilities among plugins.

This situation can be improved by adopting a generic extension mechanism (e.g., [stevedore][] or [yapsy][]) and using it throughout the whole Taurus library.

The expected benefits are:

- facilitate the maintainability of the code (removing multiple different implementations and APIs)
- Increase Taurus modularity (since many subpackages that are currently monolithic could be reimplemented as a collection of optional extensions to be loaded on-demand).
- Sardana would also benefit from an "official" extension API in Taurus (first, by formally registering itself as a taurus extension and second, by using the same API internally for its own plugins.


Goals and constraints
=====================

(To be written)

APPENDIX I: Notes on terms and concepts used
============================================

Regardless of which solution we end up proposing in the draft, we find that the analysis and naming conventions used in the [stevedore docs][] are quite useful for analising the various aspects to consider of a plugin system.

We will therefore be using concepts such as "Driver", "Hook", "Extension", "Loading pattern", "Enabling pattern", etc. as defined in the [stevedore docs][].

More specifically, you should read the following parts of stevedore docs:

First an overview of what was out there in 2013:

- [discovery](http://docs.openstack.org/developer/stevedore/essays/pycon2013.html#discovery)
- [enabling](http://docs.openstack.org/developer/stevedore/essays/pycon2013.html#enabling)
- [importing](http://docs.openstack.org/developer/stevedore/essays/pycon2013.html#importing)
- [integration](http://docs.openstack.org/developer/stevedore/essays/pycon2013.html#application-plugin-integration)
- [api-enforcement](http://docs.openstack.org/developer/stevedore/essays/pycon2013.html#api-enforcement)
- [invocation](http://docs.openstack.org/developer/stevedore/essays/pycon2013.html#invocation)

And then some more formal description of patterns:

- [Loading Pattern](http://docs.openstack.org/developer/stevedore/patterns_loading.html)
- [Enabling Pattern](http://docs.openstack.org/developer/stevedore/patterns_enabling.html)

APPENDIX II: Notes on basic considerations when evaluating a solution
=====================================================================

What we look for in a plugin system:

- able to handle all existing and foreseen entry points in Taurus and Sardana
- not adding dependencies (as yapsy), ... or embedable... or as a worst case, adding light well-known, well supported deps (e.g. setuptools in the case of stevedore)
- well supported (if it is external) or simple enough to self-support
- must allow 3rd parties to provide plugins that can be installed, discovered, enabled, etc. without assuming direct coordination between the 3rd party and the sardana/Taurus authors

APPENDIX III: Possible candidates being explored
=================================================

- [stevedore][]
- [yapsy][]
- PCA (pyutilib component architecture) from [pyutilib](https://software.sandia.gov/trac/pyutilib)
- [Marty Alchin's 6-line plugin framework](http://martyalchin.com/2008/jan/10/simple-plugin-framework/)
- Custom implementation

APPENDIX IV: List of (potential) plugin systems in Taurus and Sardana
=====================================================================

The following is a list of Taurus & Sardana subsistems or APIs which are already implemented as plugins or which may benefit from being implemented as plugins.

Each system/API is described according to the following template:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
<System/API name>
------------------
- **Description:** <what does it provide?>
- **Pointer**: <Path(s)/entry point(s) in current code where it is implemented>
- **Existing plugins**: <which plugins are already available for this system?>
- **Foreseen plugins**: <which plugins would we want to be implemented for this system?>
- **Current discovery method**: <explicit VS scanned? ... File Path VS Py Object Name?>
- **Current activation method**: <explicit VS installation VS self-enabled>
- **Proposed Loading Patterns**: <Driver VS Hook VS Extension>
- **Proposed Enabling Patterns**: <explicit VS installation VS self-enabled>
- **Priority**: <MoSCoW-style priotization for this system to be adapted to sep13>
- **Notes**: <anything worth mentioning and not covered above>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Schemes
-------
- **Description**: access abstraction to data sources via data models
- **Pointer**: taurus.core (taurus factory, helper, etc. Refer to [SEP3](https://sourceforge.net/p/sardana/wiki/SEP3/))
- **Existing plugins**: Tango, Eval, Epics, Spec, Simulation
- **Foreseen plugins**: Hdf5, Ascii tables, xls/ods files, SQL, archiving, ...
- **Current discovery method**: Path based. Uses both scanning and explicit (via tauruscustomsettings.SCHEMES)
- **Current activation method**: self-enabled (based on availability of 3rd party modules)
- **Proposed Loading Patterns**: Drivers 
- **Proposed Enabling Patterns**: installation (maybe with the possibility of explicitly disabling them to save resources?)
- **Priority**: Should

Codecs
------
- **Description:** Codecs for the DEV_ENCODED data type
- **Pointer**: taurus.core.util.codecs
- **Existing plugins**: Null, Zip, BZ2, Pickle, Json, VideoImage (Lima),...
- **Foreseen plugins**: ?
- **Current discovery method**: scan import reference (functions defined in taurus.core.util.codecs)
- **Current activation method**: install
- **Proposed Loading Patterns**: Driver
- **Proposed Enabling Patterns**: installation
- **Priority**: Would

widgets
-------
- **Description:** adding new widgets, e.g. sardana's TaurusMacroExecutor
- **Pointer**: subdirs of taurus.qt.qtgui (except those that do not define QWidget-derived classes, such as base, test, ui,...)
- **Existing plugins**: all submodules of taurus.qt.qtgui which define classes that inherit from QWidget could be considered as plugins of this type. Still some widgets can be considered more "core" than others (e.g. those in the extra_XXXX subdirs are already considered "optional"). Also, sardana already defines several plugins of this type in its sardana.taurus.qt.qtgui module.
- **Foreseen plugins**: any taurus widget of sufficient general interest that someone may want to share
- **Current discovery method**: scan import reference 
- **Current activation method**: installation and in some cases self-enabled (based on availability of 3rd party modules)
- **Proposed Loading Patterns**: Extension
- **Proposed Enabling Patterns**: self-enabled
- **Priority**: Should

external modules
------------------
- **Description:** modules that unify APIs from 3rd party modules (e.g. provide a common access to PySide and PyQt, or to unittest across the various supported versions of Python, etc)
- **Pointer**: taurus.external
- **Existing plugins**: argparse, enum, ordereddict, pint, qt, unittest
- **Foreseen plugins**: any dependency that requires backporting for some version of Python supported by Taurus
- **Current discovery method**: scan import reference
- **Current activation method**: installation
- **Proposed Loading Patterns**: Extension
- **Proposed Enabling Patterns**: installation
- **Priority**: would

Tango FactoryExtension API
--------------------------
- **Description:** API for (un)registering custom classes to be returned by the factory when a Device or Attribute is requested. These are based on the Tango Device Class name and the tango attribute.
- **Pointer**: TangoFactory.{un,}register{Device,Attribute}Class methods (note, previous to SEP3, this was implemented at the TaurusFactory level, but it is moved to tango scheme folder by SEP3). 
- **Existing plugins**: 
    - those registered by spock: SpockMacroServer, QSpockDoor, SpockDoor
    - those registered by
      sardana.taurus.core.tango.sardana.macroserver.registerExtensions():  
      MacroServer, Door,...
    - those registered by sardana.taurus.core.tango.sardana.pool.registerExtensions():
      Pool, Controller, ComChannel, Motor,...
    - those registered by taurus.core.tango.img.registerExtensions(): PyImageViewer,
      ImgGrabber, Falcon,...
- **Foreseen plugins**: ?
- **Current discovery method**: explicit import reference
- **Current activation method**: self-enabled
- **Proposed Loading Patterns**: Driver
- **Proposed Enabling Patterns**: explicit
- **Priority**: could
- **Notes**: the {un,}registerAttributeClass methods are implemented but they do not seem to be used at all yet (only the {un,}registerDeviceClass are)

The TaurusModelChooser widget (support for non-tango schemes)
-------------------------------------------------------------
- **Description:** The ModelChooser uses a TaurusDbTreeWidget which is, 
  nowadays, Tango-centric. Other schemes may define alternative 
  widgets to interact with their models (e.g. the eval scheme may provide
  an eval attribute editor)
- **Pointer**: .../qtgui/panel/taurusmodelchooser.py (see also
  taurus.qt.qtgui.panel.QRawDataWidget which is used in plots together with
  TaurusModelChooser)
- **Existing plugins**: TaurusDbTreeWidget (and its associated QModel), 
- **Foreseen plugins**: Evaluation Attribute editor
- **Current discovery method**: N/A
- **Current activation method**: N/A
- **Proposed Loading Patterns**: Extension
- **Proposed Enabling Patterns**: installation (with scheme)
- **Priority**: Could
- **Notes**: Apart from allowing certain schemes to provide an extension for 
  the ModelChooser, it would be wise to implement a scheme-agnostic Tree View Widget

Icons
-------
- **Description**: adding icons for the standard Taurus icon catalog
- **Pointer**: implemented in taurus.qt.qtgui.resource. Also "build_resources" command from setup.py
- **Existing plugins**: tango-icons, rrze-icons, external, extra-icons, large
- **Foreseen plugins**: icon folders added by other plugins (e.g. sardana-icons)
- **Current discovery method**: Path based. Scanning (at install time) the subdirs of...gtgui/resource/ to generate qrc and rcc files that are later used used by the methods in taurus.qt.qtgui.resource.taurus_resource_utils
- **Current activation method**: install
- **Proposed Loading Patterns**: Extension 
- **Proposed Enabling Patterns**: installation
- **Priority**: Could
- **Notes**: There have been informal talks about implementing direct load of icons instead of using qrc/rcc files. This may affect the design of this plugin system.

Loggers
-------
- **Description**: Set the Taurus logger system (multiples loggers could be registered). 
- **Pointer**:  taurus.core.util.log, taurus.core, taurus.qt (refer to [TEP8](http://www.taurus-scada.org/tep?TEP8.md))
- **Existing plugins**:  Taurus logger only
- **Foreseen plugins**: loggers from external applications using Taurus, custom loggers, ...
- **Current discovery method**: Not discovered. Hardcoded in  taurus.core.util.log
- **Current activation method**: Not activated. TEP8 implementation proposes explicit mechanism, via tauruscustomsetting variable (ENABLE_TAURUS_LOGGER)
- **Proposed Loading Patterns**: Hook 
- **Proposed Enabling Patterns**: Explicit
- **Priority**: Could
- **Notes**:  The Taurus models use the Factory pattern, which creates Mementos for logged events, so the use of a Logger is a requirement.

TestSuite
-------
- **Description:** The unit test infrastructure (Implemented in [SEP5](https://sourceforge.net/p/sardana/wiki/SEP5/)). New tests for features or modules can be added. Particular tests may be (de)activated dynamically.
- **Pointer**:  taurus.test and test submodules of taurus modules.
- **Existing plugins**: all "test" submodules taurus modules
- **Foreseen plugins**: New tests.
- **Current discovery method**: unittest discovery (started from test suite in taurus.test)
- **Current activation method**: installation, explicit defined via variable in taurus custom settings, and in some cases self-enabled (based on availability of resources, or execution conditions. e.g.  Taurus Qt tests (widgets) are not executed if the X is not exported.
- **Proposed Loading Patterns**: Extension
- **Proposed Enabling Patterns**: self-enabled (e.g. based on the activation of other plugins or availability of resources), explicit (white/black lists could be used to deactivate certain tests).
- **Priority**: Could
- **Notes**:  The tests could be grouped by feature/module. e.g. taurus.core.test, taurus.core.tango, taurus.qt.qtgui.panel, etc. (maybe using particular test suites)

Macros
------------------
- **Description:** adding new macros to the MacroServer 
- **Pointer**: Paths set in MacroPath property of the MacroServer Device. (Class MacroManager: msmacromanager.py )
- **Existing plugins**: specific macros
- **Foreseen plugins**: all macros which are not provided by Sardana
- **Current discovery method**: Path based. Scanning the directories listed in the MacroPath property of the MacroServer
- **Current activation method**: Explicit (when the macro is executed).
- **Proposed Loading Patterns**: Drivers
- **Proposed Enabling Patterns**: Explicit
- **Priority**: Should
- **Notes**: 


Controllers
------------------
- **Description:** adding new controller libraries to the Pool.  
- **Pointer**: Paths set in PoolPath property of the Pool Device  (Class ControllerManager: poolcontrollermanager.py)
- **Existing plugins**: specific controllers which are not distributed by default. 
- **Foreseen plugins**: all controllers which are not provided by Sardana.
- **Current discovery method**: Path based. Scanning the directories listed in the PoolPath property of the PoolDevice
- **Current activation method**: Explicit (when an instance is created)
- **Proposed Loading Patterns**: Drivers
- **Proposed Enabling Patterns**: Explicit
- **Priority**: Should
- **Notes**: 


Recorders
------------------
- **Description:** adding new recorders to the MacroServer.  
- **Pointer**: Paths set in RecorderPath property of the MacroServer Device (**TODO**: point to relevant modules involved in the implementation)
- **Existing plugins**: Spec, Json, NXscan, NXsax, FIO, output, SharedMemory, ... 
- **Foreseen plugins**: Other specific recorders which are not provided by default. 
- **Current discovery method**: Path based. Scanning the folder (no the subdirs)
- **Current activation method**: Explicit (The output recorder is active by default)
- **Proposed Loading Patterns**: Extension 
- **Proposed Enabling Patterns**: Explicit
- **Priority**: Should
- **Notes**:  More information ticket: https://sourceforge.net/p/sardana/tickets/380/





(APIs/Sytems to be expanded with the above template)
----------------------------------------------------
- <s>schemes (adding new taurus.core schemes)</s>
- <s>codecs (extend taurus.core.util.codecs)</s>
- <s>widgets (adding new widgets, e.g. sardana's TaurusMacroExecutor)</s>
- <s>external modules (unifying interfaces e.g. taurus.external.unittest, or taurus.external.qt)</s>
- <s>Tango FactoryExtension API (API of TaurusFactory, used e.g. in sardana.taurus.core.tango.sardana.pool)</s>
- Extendable Taurus widgets: some Taurus widgets may provide entry
  points to be extended:
    - <s>The ModelBrowser widget (each scheme may provide an extension to support
       browsing/selection of its models)</s>
    - The entries in the panel catalog (when selecting "new panel" in a TaurusGUI)
    - The pages of the new-gui wizard (e.g. the sardana-related page should be 
      provided by sardana)
    - TaurusForm's Custom Widget Map (see tauruscustomsettings.T_FORM_CUSTOM_WIDGET_MAP)
    - Choice of alternative subwidgets in TaurusValue (see mechanism from 
      TaurusValue.getDefaultXXXXWidgetClass())
    - ...
- <s>Icons (adding icons for the standard Taurus icon catalog)</s>
- EventFilters (extend taurus.core.util.eventfilter)
- <s>Loggers (consider this in relation to [SEP8](https://sourceforge.net/p/sardana/wiki/SEP8/))</s>
- <s>testsuite (may be interesting for enabling/disabling certain tests in the testsuite... </s>
  (e.g for substituting the lib.taurus.test.skip mechanism)
- Qt Designer Pluggins (see https://sourceforge.net/p/tauruslib/tickets/144/)
- Synoptic extensions (e.g., jdraw allows to declare custom extensions...)
- Plot mechanisms (maybe too ambitious... but plugins could be used to provide the 
  plotting... like PyMca5 does when abstracting access to switch from pyqtgraph and
  matplotlib backends)
- The mechanism for loading/installing specific TaurusGUI (using `taurusgui <modulename>`)
  could based on plugins (maybe only if the plugin system is coupled with the installation
  system as in stevedore)
- widgets backend (e.g. taurus.qt VS taurus.web VS taurus.gtk,...) 
  Ideally, we could define a set of basic Taurus building blocks such as TaurusForm, 
  Taurus Label, TaurusPlot, TaurusGui,...etc and make them "back-end agnostic" so 
  that  a Taurus GUI app could be defined transparently and be ported to any 
  of those back-ends. This sounds nice but it means a huge refactoring and may meet 
  many practical issues, so for the moment it is not to be considered.

Sardana:

- <s>macros (discovering 3rd party macros)</s>
- <s>controllers (discovering 3rd party controllers)</s>
- <s>recorders (registering recorders. see gscan's  of DataHandler.addRecorder() )</s>
- custom macro executor widgets (see 
  sardana.taurus.qt.qtgui.extra_macroexecutor.macroparameterseditor.customeditors)
- hook API for macros? (maybe it makes sense defining the hookpoints of macros as 
  internal entry points)
- macro execution clients (does it make sense to define an entry point for the 
  macro execution clients (e.g. spock vs TaurusMacroExecutor))
- spock support for diffferent versions of ipython (i.e. the code forks in the 
  genutils submodule).
- spock's InputHandler support/selection (see sardanacustomsettings.SPOCK_INPUT_HANDLER)




Links to more details and discussions
=====================================

The main discussions for this SEP take place in the [sardana-devel mailing list](https://sourceforge.net/p/sardana/mailman/).

This SEP uses concepts and nomenclature from the [stevedore docs](http://docs.openstack.org/developer/stevedore/index.html)

License
=======

Copyright (c) 2015  Carlos Pascual-Izarra

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Changes
=======
* 2015-10-15: [cpascual](https://sourceforge.net/u/cpascual/) Moved pre-draft notes from [sardana:wiki:SEP13]
* 2015-01-27: [cpascual](https://sourceforge.net/u/cpascual/) 
  Initial pre-draft notes collection started
* 2016-11-16: [mrosanes](https://github.com/sagiss/) Adapt TEP format and URL according TEP16
  
[stevedore docs]: http://docs.openstack.org/developer/stevedore/index.html
[stevedore]: https://pypi.python.org/pypi/stevedore
[yapsy]: https://pypi.python.org/pypi/Yapsy

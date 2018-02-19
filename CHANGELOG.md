# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).
This file follows the formats and conventions from [keepachangelog.com]

Note: changes in the [support-3.x] branch (which was split from 
the master branch after [3.7.1] and maintained in parallel to the 
develop branch) won't be reflected in this file.

## [4.3.0] - 2018-02-2X
### Deprecated
- taurus.core.tango.search
- TaurusMainWindow's "Change Tango Host" action (#379)

### Added
- User Interface to set custom formatters (#564)
- Re-added `taurus.external.ordereddict` (#599)
- Option to ignore outdated Tango events (#559)
- Travis-built docs (not yet replacing the RTD ones) (#572)
- TaurusLed now supports non-boolean attributes (#617)
- Support for arbitrary bgRole in labels (#629)
- `--import-ascii` option in `taurusplot` launcher (#632)
- State and event support in TangoSchemeTest DS (#628, #655)
- Model info in widget tooltips (#640)
- (experimental) Delayed event subscription API (#605, #593)
- (experimental) Entry point for taurus.qt.qtgui extensions (#684)
- Support DevVoid in Tango-to-numpy type translation dicts (#666)

### Changed
- Treat unit="No unit" as unitless in Tango attributes (#662)
- taurus.qt widgets can now be used without installing PyTango (#590)
- Tango model name validators now always return FQDN instead of PQDN
  for the tango host (#488, #589)
- Improved docs (#525, #540, #546, #548, #636) (thanks @PhilLAL !)
- Make spyder dependency optional (#556)

### Fixed
- Wrong "missing units" warnings for non-numerical attributes (#580)
- Taurus3 backwards compatibility issues (#496, #550)
- False positives in taurus.check_dependencies (#612)
- Main Window Splash screen not showing (#595)
- TaurusTrend2DDialog not usable from designer (#597)
- Missing icons in buttons (#583, #598)
- Exception in TaurusCommandForm (#608)
- Launchers not showing output on MS Windows (#644)
- Various issues with input widgets (#623, #661, #663, #669, #674, #681)
- Regressions in:
  - TaurusTrend (#618)
  - TaurusGrid (#609)
  - TaurusGUI edit with `taurusgui --new-gui` (#532)
- [Many other issues](https://github.com/taurus-org/taurus/issues?utf8=%E2%9C%93&q=milestone%3AJan18%20label%3Abug%20)

### Removed
- taurus.qt.qtgui.panel.taurusfilterpanel

## [4.1.1] - 2017-07-21

### Fixed
- Issue with PyPI metadata (hotfix 4.1.1)


## [4.1.0] - 2017-07-21

### Added
- Formatting API in TaurusBaseComponent (#444)
- TangoAttribute.format_spec and taurus.core.util.tangoFormatter
- Write support for eval scheme (#425)
- Arbitrary module support in eval scheme (#423)
- TaurusGUI New GUI wizard generates setuptools distribution (#477)
- TaurusModel.parentObject property (#415)
- TangoAttribute.getAttributeProxy (#450)
- `taurusdemo` launcher (#416)

### Changed
- pint_local updated to v 0.8 (#445)
- Improve config properties of TaurusTrend2D (#489)
- Make taurusplot and taurustrend (re)store their geometry (#508)
- Improve logs when handling unsupported units in
  TangoAttributes (#420, #495, #403)
- Improve logs when TangoAttribute read fails (#478)
- Allow subscribing to Tango attributess without emiting firsat event (#482)
- Use dependencies (and optional deps) in setuptools distribution (#479)
- Make TaurusPlot inspector mode use the attribute format for display (#509)

### Deprecated
- TangoAttribute.format
- taurus.qt.qtgui.console (#385)
- taurustrend1d (#514)
- tauruscurve (#514)

### Removed
- `taurus.external.ordereddict` (#223)
- `taurus.qt.qtgui.Q*` modules (Qt, QtCore, QtGui, Qwt5,...)
- `taurus.qt.qtgui.util.taurusropepatch` module
- `taurusqt.qtgui.util.genwidget`

### Fixed
- Taurus4 ignoring Tango format (#392)
- Incompatibility with Tango9.2 (#458)
- Bug in handling of nanoseconds by TaurusTimeVal (#453)
- Import error when PyTango is not installed (#398)
- Issues affecting TaurusPlot (and Trends) (#422, #438, #440, #475, #508 )
- Issues affecting TaurusLCD (#467)
- Issues when changing tango host (#79, #378, #382, #487)
- Issues affecting Eval (#428, #448)
- Docs issues (#249, #267,  #397, #430, #490)
- [Many other issues](https://github.com/taurus-org/taurus/issues?q=milestone%3AJul17+label%3Abug)


## [4.0.3] - 2017-01-16
[Jan17 milestone](https://github.com/taurus-org/taurus/milestone/1)
Bugfix release.
For a full log of commits since Jul16, run (in your git repo):
`git log 4.0.1..4.0.3` 

### Added
- Generic Attribute, Device and  Authority getters in TaurusFactory
- spyder >=3 support (#343)
- bumpversion support (for maintainers) (#347)
- Contribution policy explicited in CONTRIBUTING.md
- Continuous Integration for Windows support (Appveyor) (PR#10)

### Changed
- TangoAttribute now decodes uchars as integers instead of strings (#367)
- Allow empty path in Attr and Dev URIs (#269)
- Project migrated to Github (TEP16)
- Versioning policy (use of `-alpha` suffix for unreleased branches)

### Deprecated
- `taurus.Release.version_info` and `taurus.Release.revision` variables
- `TaurusAttribute.isState` (#2)
- `taurus.external.ordereddict` (#8)

### Fixed
- Taurus4 regressions in:
    - TangoAttribute (when handling Tango config errors) (#365)
    - TaurusValueSpinBox (#7)
    - taurusgui --new-gui (#275)
    - TaurusGui Sardana instrument panels (#372)
    - Macrolistener (affects sardana) (#373)
    - Synoptics (#363)
    - TaurusValueLineEdit (#265)
    - taurusgui.macrolistener (#260)
    - TaurusEditor (#343)
- Bug causing high CPU usage in TaurusForms (#247)
- Deprecation warnings in `TaurusWheelEdit` (#337)
- Exceptions in `taurusconfigurationpanel` for non-tango models (#354)
- Exception when creating non-exported tango devices (#262)
- Bug causing random failures in the test suite(#261)
- Documentation issues(#351, #350, #349)

### Removed
- `TaurusBaseEditor2` class


## [4.0.1] - 2016-07-19
Jul16 milestone. 
First release of the Taurus 4 series.
Largely (but not 100%) compatible with taurus 3 series.
For a full log of commits since Jan16, run (in your git repo):
`git log 3.7.0..4.0.1` 

### Added
- Quantities (units) support ([TEP14])
- Scheme-agnostic core helpers ([TEP3])
- Model fragment support ([TEP14])
- PyQt new-style signals support (#187)
- support for guiqwt >= 3 (#270)
- New icon API (taurus.qt.qtgui.icon) (#280) 
- New `taurusiconcatalog` application (#280)
- Backwards compatibility layer for migration from Taurus 3.x ([TEP14])
- New deprecation API (`Logger.deprecated` and `deprecation_decorator`)
- new unit tests (from ~50 to ~550 unit tests)
- This CHANGELOG.md file

### Changed
- Tango dependency is now **optional** ([TEP3])
- Improved and simplified core API ([TEP3], [TEP14]):
    - Configuration and Attribute Models are now merged into Attribute
    - Taurus model base classes are now scheme-agnostic
    - Improved model name validators (enforcing RFC3986 -compliant model 
    names)
- Eval scheme improved (more natural and powerful syntax) ([TEP14])
- Epics scheme plugin improved (and is now installed) (#215)
- Improved installation and distribution scripts (now using setuptools),
(#279)
- Improved testsuite (new `taurustestsuite` command allowing regexp 
exclusions)
- Improved Icon Theme support (also for windows)
- taurus.qt now depends on PyQt>=4.8 (before was 4.4)
- taurus.qt.qtgui.extra_nexus now depends on PyMca5 (before was 4.7)
- Updated documentation (#221)

### Deprecated
- Support for old-style signals
- Support for PyQt API1
- Taurus3.x tango-centric API (see [TEP3], [TEP14])
- old-style tango and eval model names (non-RFC3986 compliant)
- taurus.qt.qtgui.resource module
- taurus.external.ordereddict

### Removed
- Deprecated modules (see #234 for details & replacements)
    - taurus.core.utils
    - taurus.core.util.decorator.deprecated
    - taurus.qt.qtgui.table.taurusvaluestable_ro
    - taurus.qt.qtgui.panel.taurusattributechooser
    - taurus.qt.qtgui.panel.taurusconfigbrowser
    - taurus.qt.qtgui.base.taurusqattribute
    - taurus.qt.gtgui.extra_xterm
    - taurus.qt.gtgui.extra_pool
    - taurus.qt.gtgui.extra_macroexecutor
    - taurus.qt.gtgui.extra_sardana
    - taurus.qt.gtgui.gauge
    - taurus.qt.qtgui.image
    - taurus.qt.qtopengl
    - taurus.qt.uic
    - taurus.web
- `spec` scheme plugin (#216)
- `sim` scheme plugin (#217)
- Obsolete `setup.py` commands (`build_resources`, `build_doc`,...) 
(#279)
- Icon resource files (but the icons are still available and accessible)
(#280)

### Fixed
- Installation now possible with pip (no need of --egg workaround)
- Documentation generation issues (#288, #273, #221)
- Several bugs and feature-req in TaurusTrend2D 
- Issues in TaurusArrayEditor (#260, #261) 
- TaurusTrend Export to ASCII issues (#300, #277, #253)
- `resource` scheme plugin (#218)
- windows installer (#278)
- [Many other issues](https://sf.net/p/tauruslib/tickets/milestone/Jul16/)


## [3.7.1] - 2016-03-17
Hotfix for RTD (no library changes)

### Fixed
- RTD issue (bug 273)  


## [3.7.0] - 2016-02-17 
Jan16 milestone. 
For a full log of commits since Jul15, run (in your git repo):
`git log 3.6.0..3.7.0` 

### Added
- Support for sqlite DB in Tango (ticket #148)

### Fixed
- Many usability bugs in TaurusTrend2D and other
  guiqwt-based widgets (#238, #240, #244, #247, #251, #258)
- Issues with "export to ASCII" feature of plots
- Issues with PLY optimization (#262)
- "taurus-polling-period" argument works for evaluation
  attributes now too (#249)
- [Many other issues](http://sf.net/p/tauruslib/tickets/milestone/Jan16/)
    

## [3.6.1] - 2015-10-01
Hotfix for docs (no library changes)

### Fixed
- documentation issues (#181, #191, #194)


## [3.6.0] - 2015-07-22 
Jul15 milestone. 
For a full log of commits since Jan15, run (in your git repo):
`git log 3.4.0..3.6.0` 

### Added
- support of user creation/removal of custom external application
launchers at run time (see #158)
- support of LimaCCDs DS (see #175) and improvements in the codecs

### Changed
- taurusplot/trend uses the same order than the legend for exported
data (see #161)
- Docs: several improvements and made ReadTheDocs-compliant

### Fixed
- Fixed memory leaks in plots/trends (see #171)
- [fixed many bugs in TaurusPlot,  TaurusWheel,  TaurusImageDialog,
and several other places](https://sf.net/p/tauruslib/tickets/milestone/Jul15/)



[keepachangelog.com]: http://keepachangelog.com
[TEP3]: http://www.taurus-scada.org/tep/?TEP3.md
[TEP14]: http://www.taurus-scada.org/tep/?TEP14.md
[Unreleased]: https://github.com/taurus-org/taurus/tree/develop
[4.1.0]: https://github.com/taurus-org/taurus/tree/4.1.0
[4.0.3]: https://github.com/taurus-org/taurus/tree/4.0.3
[4.0.1]: https://github.com/taurus-org/taurus/tree/4.0.1
[3.7.1]: https://github.com/taurus-org/taurus/tree/3.7.1
[3.7.0]: https://github.com/taurus-org/taurus/tree/3.7.0
[3.6.0]: https://github.com/taurus-org/taurus/tree/3.6.0
[support-3.x]: https://github.com/taurus-org/taurus/tree/support-3.x




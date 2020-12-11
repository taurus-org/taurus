    Title: plugins support 
    TEP: 13
    State: CANDIDATE
    Date: 2015-03-25
    Drivers: Carlos Pascual-Izarra <cpascual@cells.es>
    URL: http://www.taurus-scada.org/tep?TEP13.md
    License: http://www.jclark.com/xml/copying.txt
    Abstract:
     Define the generic rules and APIs for how taurus allows other code 
     (plugins) to extends Taurus. Describe a single approach that can be used
     to unify and systematise the various existing plugin mechanisms found 
     today in Taurus, as well as to create more entry points in the future.
     Provide a guide for how the pluggable components should be documented
    


# Introduction

Over the history of Taurus different mechanisms to support extensions were 
implemented in various subsystems of Taurus (see APPENDIX I). Most of these 
mechanisms, being ad-hoc implementations, are quite specific and present 
limitations such as requiring the plugin to have privileged access to Taurus 
installation directories, or not having a well defined interface, or not 
allowing to define dependencies/incompatibilities among plugins.

This situation can be improved by adopting a generic extension mechanism and 
using it throughout the whole Taurus library.

The expected benefits are:

- facilitate the maintainability of the code (unifying the current
  implementations of plugins support in taurus)
- Increase Taurus modularity (since many subpackages that are currently 
  monolithic could be reimplemented as a collection of optional extensions to 
  be loaded on-demand). For example, all tango-centric code in taurus could be 
  moved to a separate "taurus_tango" plugin project.
- Sardana would also benefit from an "official" extension API in Taurus (first, 
  by formally registering itself as a taurus extension and second, by using the 
  same API internally for its own plugins.
  
## Considered implementation options

During the many years since we first discussed this TEP, we studied several 
alternatives ([yapsy][], pyutilib, [Marty Alchin's 6-line plugin framework][], 
...) but we ended up deciding among using [stevedore][] or using [setuptools][] 
entry points directly.

Stevedore is appealing because it provides a well defined formal framework, but
it introduces a dependency to the `stevedore` module  which is not used by a 
large number of projects. In contrast, with setuptools having become the 
de-facto standard for python distribution, its entry-point mechanism is more  
accessible to the potential plugin developers. In fact, all the recent 
plugins created for Taurus are already using setuptools entry points directly 
and hence the decision has been made to use that for this TEP.
  
## Note on terminology

Even if we decided not commit to use [stevedore][], we find that the analysis 
and naming conventions used in its docs are quite useful for describing the 
various aspects to consider of a plugin system.

We will therefore be using concepts such as "Driver", "Hook", "Extension", 
"Loading pattern", "Enabling pattern", etc. as defined in the 
[stevedore docs][].

Also, we will use the term "taurus pluggable component" to refer to a part of 
the taurus code that is or may be implemented with plugin support. 

## Scope of this TEP

This TEP focuses on providing a generalised solution and convention for 
supporting the various components of taurus that can be implemented as plugins.

What it is **not** in the scope of this TEP is the implementation of each and 
all of the possible pluggable interfaces. This is to be treated as future work.

The initial draft of this TEP covered Sardana plugins as well, but this 
has been now moved out of the scope of this TEP and will be treated by Sardana's 
[SEP19][]. See also [this comment](https://github.com/sardana-org/sardana/pull/1328#issuecomment-741907800)

# Rules for TEP13-compliant plugins

This proposal covers the following aspects of the plugin support:
- The plugin interface definition and documentation: how taurus should define 
and document its pluggable components  
- The advertising mechanism: how 3rd party code (or taurus itself) can "plug" 
to a given pluggable interface
- The internal taurus loading and enabling mechanisms: how taurus should 
implement the discovery/loading/enabling of the available plugged code

These three aspects are based on [python entry points][ep_spec].

## Plugin interface definition and documentation

For each pluggable component, taurus should define and document the following:

- a description of the component
- the *entry point group* associated with this pluggable component
- the API that is expected from the objects to be loaded in this group 
- the name convention applying to the *entry point names* in this group 
- the *loading pattern* that will be used
- the *enabling pattern* that will be used

This information can be documented where it is more appropriate attending to 
the context (e.g the taurus subcommands entry point mechanism can be 
documented in the docs of the `taurus.cli` submodule), but it should also be 
**referenced in a dedicated part of the docs that enumerates and centralizes all 
the existing extension points provided by taurus** (as of now, this is the 
[taurus plugins][plugins] page).

The following subsections provide some more details on each required 
documentation item. 

### Description

A human-readable description of the pluggable component. Can contain links to 
docs, examples, etc.

### Entry point group

The entry point group is a string that identifies the particular pluggable 
component in taurus and which follows the syntax rules from the
[entry_points API][pkg_resources]. To avoid group name collisions, all taurus 
groups should start with `"taurus."` and then be followed by a preferably short 
string that identifies the component, and which may use dots for grouping 
related components.

Some recommendations:

- While the group names may totally or partially match a submodule name, it 
is not necessarily the case. Descriptive and reasonably short and unambiguous 
names are preferred over long submodule-matching names. e.g:
`taurus.form.item_factories` and not `taurus.qt.qtgui.panel.taurusform.item_factories`

- The last part of the name will in general be a plural name, reflecting the
fact that this is a group of entry points

- For consistency, all-lowercase group names are preferred, but this may be 
ignored if there is a strong reason against it (e.g. specific context 
consistency)  

### Expected API

This describes which is the object type /  API that taurus expects from objects 
loaded in this group. This can be done by referring to a concrete type, or by 
describing the minimal required object API, but it is probably a good idea to
formalize the description by providing an [Abstract Base Class][abc].

### Name convention

When a distribution advertises an object of a given group, it must provide a 
name. This name may be used by taurus while loading or enabling the plugin, 
and therefore taurus may impose or recommend some rules for that name. 

For example: the alternative implementations for TaurusPlot (`taurus.plot.alts`
group) can be listed and selected by the user using the advertised name, and 
therefore taurus expects the name to be a short string identifying the 
specific implementation.

### Loading pattern

This describes how will the registered object be loaded by taurus.
It can typically be one of "Driver", "Hook", or "Extension", as described in:
https://docs.openstack.org/stevedore/latest/user/patterns_loading.html

For example: the schemes in taurus core (`taurus.core.schemes` group) are 
loaded using the *Drivers* pattern, while the taurus CLI subcommands 
( `taurus.cli.subcommands` group) are loaded with the *Extensions* pattern

### Enabling pattern

This describes the mechanism by which the registered object will be enabled 
(or not) in taurus. In other words, a package may advertise objects 
for a given taurus group, but taurus may or may not make use of those objects.

It can typically be one of "Installation", "Explicit", or "Self-enabled", as
described in: 
https://docs.openstack.org/stevedore/latest/user/patterns_enabling.html

It may also provide more details such as which mechanisms are used in the case 
of the *explicit* or *self-enabled* patterns

For example: the schemes in taurus core (`taurus.core.schemes` group) are 
enabled by installation, whereas the formatters (`taurus.qt.formatters`) are
enabled explicitly (e.g. by the user or programmer setting them with 
`TaurusBaseComponent.setFormatter()`)

## Advertising

Any python module (or more strictly speaking, any python *distribution*) may
advertise objects for entry point groups defined by Taurus.

In general, this can be done by any means allowed by the [entry points 
specification][ep_spec], and is typically done with the `entry_points` 
argument for `setuptools.setup()` (or by defining them in `setup.cfg`), with the
following syntax: 

`name = some.module:some.attr`
 
where:

- `name` is the entry point name
- `some.module:some.attr` refers to the object (`:some.attr` may be omitted if 
referring to a module)
 
Note that a given distribution can advertise objects for more than one group.
For example, the [taurus_tangoarchiving][] package, which provides support 
for Tango archiving models, advertises the module itself as a taurus scheme 
(`taurus.core.schemes` group) and also a model chooser extension widget 
(`taurus.model_selector.items` group) 

## Implementation of taurus loading and enabling mechanisms

Taurus should use the setuptools' [`pkg-resources` API][pkg_resources] or 
the [`importlib.metadata`][metadata] equivalent to discover and load the 
advertised objects.

The specific implementation will depend on each case, but the following general 
considerations apply:

- performance: since taurus won't have control over 3rd-party code that may 
advertise its objects, strategies to minimize potential performance hits 
should be considered (e.g. delay entry point loading until needed, provide 
mechanisms for selecting available plugins, consider parallelization when 
loading, etc)

- robustness: since we do not have control over plugin quality, the 
loading of advertised objects should be protected and allow taurus to fail 
gracefully if an advertised object fails to load. 

## Full Example

The documentation for "taurus subcommands plugin" is:

- Description: register subcommands for the `taurus` CLI command.
- Group: `taurus.cli.subcommands`
- Expected API: [`click.Command`](https://click.palletsprojects.com/en/7.x/api/#click.Command) 
- Entry point name convention: None, the name is ignored. Suggestion: use the subcommand name 
- Loading pattern: extension
- Enabling pattern: installation

Now, if a module called `foo_mod` implements a `click`-based command as 
the `foo_mod.cli.foo` object and wants it exposed by Taurus as a subcommand of 
the `taurus` command, it can achieve it by using the following code in its 
`setup.py`:

```
import setuptools

entry_points = {}
...
entry_points["taurus.cli.subcommands"] = ["foo = foo_mod.cli:foo"]

setuptools.setup(
    entry_points=entry_points,
    ...
)
```

The implementation in this case is done by the `taurus.cli.` module, which 
iterates over the advertised entry points for the `taurus.cli.subcommands` group
and safely loads them only when the `taurus` command is executed in the CLI.


# Existing TEP13-compliant plugins

At the moment of writing, taurus already supports the following pluggable 
components that comply to this TEP rules (for details, check the 
[taurus plugins documentation][plugins])

- `taurus.cli.subcommands` (click subcommands for the taurus command)
- `taurus.core.schemes` (new schemes in taurus.core to support other sources of data)
- `taurus.qt.qtgui` (adding submodules to taurus.qt.qtgui)
- `taurus.qt.formatters` (formatter objects for taurus widgets)
- `taurus.model_selector.items` (items for `TaurusModelSelector`)
- `taurus.plot.alts` (alternative implementations of `TaurusPlot`)
- `taurus.trend.alts` (alternative implementations of `TaurusTrend`)
- `taurus.trend2d.alts` (alternative implementations of `TaurusTrend2D`) 
- `taurus.image.alts`  (alternative implementations of `TaurusImage`)
- `taurus.form.item_factories` (factories for custom "taurus value" widgets to 
be used in taurus forms)


# Future work

The following is non-exhaustive list of taurus components that may benefit from 
being refactored according to this TEP. Some are currently plugabble using an 
ad-hoc (non TEP13-compliant) mechanism while others are not yet pluggable at 
all. The proposed "group name" is only tentative, and subject to change on 
implementation: 

- adding new codecs as those in `taurus.core.util.codecs`
- extending `taurus.core.util.eventfilter`
- refactoring the `TaurusFactory.registerDeviceClass` (and related) mechanisms
- adding entries to the panel catalog in a TaurusGUI
- adding pages to the the `AppSettingsWizard` (e.g. the sardana-related page 
should be provided by `sardana`)
- adding icons for the standard Taurus icon catalog
- ...


# Links to more details and discussions

The implementation and discussion is done in the PR associated to this TEP


# License

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

# Changes

- 2015-10-15: [cpascual][] Moved pre-draft notes from [sardana:wiki:SEP13]
- 2015-01-27: [cpascual][] 
  Initial pre-draft notes collection started
- 2016-11-16: [mrosanes][] Adapt TEP format and URL according TEP16
- 2020-12-11: [cpascual][] Full re-writing of the DRAFT and promotion to 
  CANDIDATE state
  
[stevedore docs]: https://docs.openstack.org/stevedore/latest/
[stevedore]: https://pypi.python.org/pypi/stevedore
[yapsy]: https://pypi.python.org/pypi/Yapsy
[SEP19]: https://github.com/reszelaz/sardana/blob/sep19/doc/source/sep/SEP19.md
[pkg_resources]: https://setuptools.readthedocs.io/en/latest/pkg_resources.html
[ep_spec]: https://packaging.python.org/specifications/entry-points/
[metadata]: https://docs.python.org/3/library/importlib.metadata.html
[plugins]: http://taurus-scada.org/devel/plugins.html
[abc]: https://docs.python.org/3/library/abc.html
[taurus_tangoarchiving]: https://github.com/taurus-org/taurus_tangoarchiving
[cpascual]: https://github.com/cpascual/
[mrosanes]: https://github.com/sagiss/


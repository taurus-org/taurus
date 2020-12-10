    Title: Implement plots with pyqtgraph
    TEP: 17
    State: CANDIDATE
    Date: 2017-03-10
    Drivers: Carlos Pascual-Izarra cpascual@cells.es
    URL: http://www.taurus-scada.org/tep?TEP17.md
    License: http://www.jclark.com/xml/copying.txt
    Abstract: 
     Replace TaurusPlot and TaurusTrend implementations from the deprecated
     taurus.qt.qtgui.qwt5 by taurus_pyqtgraph implementations
 
## Introduction

Taurus currently depends on [PyQwt5][] for its `taurus.qt.qtgui.plot` and 
`taurus.qt.qtgui.qwt5` modules.

PyQwt5 has been unmaintained for a long time and is not supported in  
most modern linux distros and is not compatible with PyQt5 and Python3.

This TEP proposes using the [taurus_pyqtgraph][] plugin as a replacement for
`taurus.qt.qtgui.qwt5`.

## Goals

For the scope of this TEP, only a basic subset of the features that were 
supported by `taurus.qt.qtgui.qwt5` are implemented in the current version of
the [taurus_pyqtgraph][] plugin. The rest would be treated as future 
enhancements. 

The following is a list of features provided and planned by the 
`taurus_pyqtgraph` plugin  (the checked features are already implemented 
in the latest release of the plugin, v0.4.9, at the moment of writing):

### For 1D plots

- [x] 1D plot: plot of multiple 1D models with auto-changing color and
    availability of legend
- [x] Date-time support on X axis (display only, see "UI for
    setting scale limits *in date/time format*" below)
- [x] Stand-alone widget (`TaurusPlot`)
- [x] Zooming & panning with "restore original view" option (not the same
    as zoom stacking, see below)
- [x] Possibility to use (at least) 2 Y-scales
- [x] UI for adding taurus curves via ModelChooser. See also
    "Improved Model Chooser" below
- [x] Store/retreive configuration (save/load settings)
- [x] Support for non-taurus curves in same plot (aka "raw data")
- [x] UI for setting scale limits and lin/log options
- [x] Export data as ascii: without date-time support
- [x] Export plot as image (S0)
- [x] UI for moving a curve from one Y-scale to another
- [x] UI for choosing line color, thickness symbol, filling...
- [x] Arbitrary Label scale (aka FixedLabelsScale)
- [x] configurable properties support (setting permanence)

Outside TEP17 scope:

- [ ] UI for setting scale limits *in date/time format* (S16)
- [x] Point-picking (aka "inspect mode") (S4)
- [ ] Date-time support in "export data as ascii" (S24)
- [ ] Plot freeze (pause) (S8)
- [x] Improved Model Chooser: replacement of the "input data selection"
  dialog allowing to choose *both* X and Y models (see curve selection
  dialog in extra_guiqwt's tauruscurve) (C16)
- [x] Drop support for taurus attributes (C4)
- [ ] Zoom stack: possibility of stacking zoom levels and navigating back
  one level at a time. (C16)
- [ ] Cursor position info (display X-Y position of cursor in active axis
  coords) (C2)
- [ ] 1D ROI selector (C2)
- [ ] Curve statistics calculator (mean, stdev...) as in curve stats
  dialog of TaurusPlot/Trend (C8)
- [ ] UI for changing curve names (C8)
- [ ] Peak locator: Visual label min/max of curves (C12)
- [ ] UI for adding raw data (W8)

### For 1D trends

Most of the features mentioned for 1D plots affect the 1D trends as
well. Apart from those, here is a list of more specific features of
trends:

- [x] "1D trends": plot of scalars vs event number or timestamp
- [x] Fixed-range scale (aka oscilloscope mode)
- [x] UI to switch between fixed and free scale mode
- [x] Stand-alone Widget (`TaurusTrend`)
- [x] Support for forced-reading of attributes (aka "-r mode") 
- [x] UI for forced-reading mode
- [x] configurable properties support (setting permanence)

Outside TEP17 scope:

- [x] "Trend sets": plot of 1D attribute vs time interpreting it as a set
  of 1D scalars (M16)
- [x] Accessing Archived values (M40). Done via [taurus_tangoarchiving][] plugin
- [ ] Accessing Tango Polling buffer (W24)
- [x] Support for limiting curve buffers (C8)
- [ ] UI for curve buffers (C2)


## Implementation strategies

The implementation of this TEP is done as the `taurus_pyqtgraph` plugin:

https://github.com/taurus-org/taurus_pyqtgraph

The next subsections discuss some design decisions for the proposed
implementation:

### Modular vs Monolithic approach

One design decision for our initial implementation is that the
required features not already present in pyqtgraph should be
implemented by our plugin as small, self-contained "items"
or "tools" that may be used in place of (or as a complement to) the
generic pyqtgraph classes, with as little inter-dependency as possible
from one another. This approach (which we call "Modular")
is similar to what we did in `taurus.qt.qtgui.extra_guiqwt`.

This contrasts with the "Monolithic" approach that we followed in the
`taurus.qt.qtgui.qwt5` module, in which two main classes (`TaurusPlot`
and `TaurusTrend`) implemented all the required features and
provided their own API (different from the standard `PyQwt5` API).

### High level plot widgets & compatibility with the old classes

While we focus on providing a modular, tool/item based usage
pattern, it would be useful to also provide convenience high-level
plot widgets which incorporate by default most of the implemented
features and which could roughly substitute `TaurusPlot`,
`TaurusTrend`, etc. The important thing to note is that these
high-level classes would be implemented as an aggregation of the
smaller, modular ones, and instead of providing an ad-hoc API
for customizing them, the specialised needs would be covered by
building a new class from the generic pyqtgraph classes and our
tools/items.

In terms of backwards compatibility with the existing classes,
we aim for *feature*-compatibility, but *not* for full
*API*-compatibility. Providing full API compatibility would be
difficult in some cases, would clutter the plot classes and would
result in workflows that are not natural in the context of
pyqtgraph. Still, the simplest use cases with the old classes
(e.g. instantiating a plot and calling `setModel`) should work
identically in the new high-level classes. This should allow
a large majority of the GUIs to do the switch by just replacing
an old plot class by a new one.

### "attach-to" vs "addItem"

In pyqtgraph, the typical pattern to add an item (e.g. a curve -a
`PlotDataItem`-) to a container (e.g. a ViewBox) consists in a call
of the type `viewBox.addItem(curve)`.

Whenever possible, the classes implemented in our module should allow
to be treated just as their generic pyqtgraph analogs. For example,
consider `TaurusPlotDataItem`, which is a curve that autoupdates its
values when its associated Taurus model is updated): in this case,
adding it to a ViewBox should just be `viewBox.addItem(tauruscurve)`.

But in some occasions, the pyqtgraph classes do not provide the
required API for adding and enabling *in a simple way* a required
feature. For example, adding a secondary Y axis to a plot requires
several non-trivial lines of code involving linking axes,
connecting signals, etc. In such cases, we opted for inverting the
control and using an "attach-to" pattern. For example, the secondary
Y axis feature is implemented as a especialised ViewBox that has a
method called `attachToPlotItem`, so instead of a more natural
(but unavailable) call `plotItem.addAxis(y2Axis)`, we do:
`y2Axis.attachToPlotItem(plotItem)`

This solution is not ideal but allows us to quickly prototype
without having to fork pyqtgraph. Our intention is that once our
implementation is past the prototyping phase, we would propose
changes to pyqtgraph to support the more natural "direct" way
(e.g., `PlotItem.addAxis`) and, if those are accepted, use them
instead of the "attach-to".


## Links to more details and discussions

Discussions for this TEP are conducted in its associated Pull Request:
https://github.com/taurus-org/taurus/pull/452

Also see the Issues and Pull Requests from the [taurus_pyqtgraph][] project.


## Follow-on

Originally the scope of TEP17 also included providing a replacement for the 
following 2D widgets: 

- `TaurusImageDialog`
- `TaurusTrend2DDialog`

This was later reconsidered and the scope was reduced to the 1D plots and 
trends. Future work may include the 2D widgets and also some other features. 
See [taurus_pyqtgraph][] for more details and updated information iabout it.

## License

Copyright (c) 2017 Carlos Pascual-Izarra

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

## Changes


- 2017-03-10 [cpascual][]. Initial version
- 2017-05-17 [cpascual][]. TEP text updated and proof-of-concept
  implementation by [oscarprades][] added
- 2020-12-09 [cpascual][]. TEP text updated to reflect the use of the 
  taurus_pyqtgraph plugin. Changed state to CANDIDATE and proposed for APPROVAL

[PyQwt5]: http://pyqwt.sourceforge.net/
[taurus_pyqtgraph]: https://github.com/taurus-org/taurus_pyqtgraph
[taurus_tangoarchiving]: https://github.com/taurus-org/taurus_tangoarchiving
[cpascual]: https://github.com/cpascual
[oscarprades]: https://github.com/oscarprades

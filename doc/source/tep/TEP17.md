    Title: Implement plots with pyqtgraph
    TEP: 17
    State: DRAFT
    Date: 2017-03-10
    Drivers: Carlos Pascual-Izarra cpascual@cells.es
    URL: http://www.taurus-scada.org/tep?TEP17.md
    License: http://www.jclark.com/xml/copying.txt
    Abstract: 
     Deprecate qwt and guiqwt-based widgets and substitute them by 
     pyqtgraph-based ones
 
## Introduction

Taurus currently depends on [PyQwt5][] for its `taurus.qt.qtgui.plot` 
module. The `taurus.qt.qtgui.extra_guiqwt` also partially depends on it
for the date-time scales.

PyQwt5 has been unmaintained for a long time and is likely to disapear 
from most linux distros (apart from not providing support for PyQt5 or 
Python3).

So it is about time to deal with the migration to a newer, maintained
library for our plots.

The main objective is to cover the use cases currently handled by:

- TaurusPlot
- TaurusTrend
- TaurusImageDialog
- TaurusTrend2DDialog

Note: the `taurus.qt.qtgui.extra_guiqwt` module also provides 2 other 
plot widgets: `TaurusCurveDialog` and `TaurusTrend1DDialog` which are 
unfinished attempts to replace `TaurusPlot` and `TaurusTrend` 
respectively using `guiqwt`. The uncertainties with the future of guiqwt
put a stop on the development of those replacements and therefore we 
only consider them in this TEP as possible inspirations for the proposed
new implementation.
 
The main library candidates considered for the new plotting system are:

- [guiqwt](https://pythonhosted.org/guiqwt/)
- [pyqtgraph](http://pyqtgraph.org/)
- [silx](http://www.silx.org/)

This TEP proposes to choose pyqtgraph as the base of the new plotting 
infrastructure because:

- It matches perfectly with the technology stack in taurus
- It provides 2D and 3D plotting
- It is reasonably well documented and provides comprehensive examples
- It is reasonably mature and popular

Guiqwt was discarded in favour of pyqtgraph because its lack of 3D
support and the perceived less-responsive support from its author.

Silx was discarded in favour of pyqtgraph because its plot API was
considered not yet mature enough for the current needs (specially its
object oriented API, whose first release was in May 2017).
 
## Goals

For the scope of this TEP, only a basic set of features currently 
supported in the deprecated modules would be implemented in the new
ones, and the rest would be treated as future enhancements.

The following is a list of features, with a rough classification using a
[MoSCoW][] code followed by a (very optimistic) cost estimation in
hours. **The features selected for impementation as part of
this TEP marked with `(*)`**:

### For 1D plots/trends

  - (*) 1D plot: plot of multiple 1D models with auto-changing color and
    availability of legend (M8)
  - (*) Date-time support on X axis (display only, see "UI for
    setting scale limits *in date/time format*" below) (M16)
  - (*) Stand-alone widget (M2)
  - (*) Zooming & panning with "restore original view" option (not the same
    as zoom stacking, see below) (M0)
  - (*) Possibility to use (at least) 2 Y-scales (M12)
  - (*) UI for adding taurus curves via ModelChooser. See also
    "Improved Model Chooser" below  (M4)
  - (*) Store/retreive configuration (save/load settings) (M8)
  - (*) Support for non-taurus curves in same plot (aka "raw data") (S0)
  - (*) UI for setting scale limits and lin/log options (S0)
  - UI for setting scale limits *in date/time format* (S16)
  - Point-picking (aka "inspect mode") (S4)
  - (*) Export data as ascii: without date-time support (S0)
  - Export data as ascii: date-time support (S24)
  - (*) Export plot as image (S0)
  - Plot freeze (pause) (S8)
  - (*) UI for moving a curve from one Y-scale to another (S12)
  - (*) UI for choosing line color, thickness symbol, filling... (S16)
  - Improved Model Chooser: replacement of the "input data selection"
    dialog allowing to choose *both* X and Y models (see curve selection
    dialog in extra_guiqwt's tauruscurve) (C16)
  - Drop support for taurus attributes (C4)
  - (*) Arbitrary Label scale (aka FixedLabelsScale) (C8)
  - Zoom stack: possibility of stacking zoom levels and navigating back 
    one level at a time. (C16)
  - Cursor position info (display X-Y position of cursor in active axis
    coords) (C2)
  - 1D ROI selector (C2)
  - Curve statistics calculator (mean, stdev...) as in curve stats
    dialog of TaurusPlot/Trend (C8)
  - UI for changing curve names (C8)
  - Peak locator: Visual label min/max of curves (C12)
  - UI for adding raw data (W8)
  - *Relative* date/times display support (aka, deltatime scale) (W8)

### For 1D trends

Most of the features mentioned for 1D plots affect the 1D trends as
well. Apart from those, here is a list of more specific features of
trends:

  - (*) "1D trends": plot of scalars vs event number or timestamp (M16)
  - "Trend sets": plot of 1D attribute vs time interpreting it as a set
    of 1D scalars (M16)
  - (*) Fixed-range scale (aka oscilloscope mode) (M8)
  - (*) UI to switch between fixed and free scale mode (S12)
  - Accessing Archived values (M40)
  - Accessing Tango Polling buffer (W24)
  - (*) Support for forced-reading of attributes (aka "-r mode") (M10)
  - (*) UI for forced-reading mode (C2)
  - Support for limiting curve buffers (C8)
  - UI for curve buffers (C2)


### For 2D plots (images)

  - (*) Plot a single image (M0)
  - (*) UI for Add/remove image (M4)
  - Cross sections (slicing) (S4)
  - (*) "calibrated" XYImage (assigning values to X and Y scale, as in
    guiqwt's XYImageItem) S8
  - 2D ROI Selector (S4)
  - LUT/contrast control (S0)
  - Drop support for taurus attributes (C4)
  - LogZ scale (C?)
  - Annotation/measure tools (C16)


### For 2D trends (spectrograms)

Most of the features for 2D plots affect also the 2D trends. Apart
from those, here is a list of more specific features of 2D trends:

  - (*) Absolute date-time scale (display, see same feat in TaurusPlot)
  - (*) Fixed-range scale (aka oscilloscope mode, same as for 1Dtrends) (M8)
  - (*) UI to switch between fixed and free scale mode (S12)


## Implementation

The current status of the implementation can be followed in:

https://github.com/taurus-org/taurus/pull/452

The next subsections discuss some design decisions for the proposed
implementation:

### Modular vs Monolithic approach

One design decision for our initial implementation is that the
required features not already present in pyqtgraph should be
implemented by our module as small, self-contained "items"
or "tools" that may be used in place of (or as a complement to) the
generic pyqtgraph classes, with as little inter-dependency as possible
from one another. This approach (which we call "Modular")
is similar to what we did in `taurus.qt.qtgui.extra_guiqwt`.

This contrasts with the "Monolithic" approach that we followed in the
`taurus.qt.qtgui.plot` module, in which two main classes (`TaurusPlot`
and `TaurusTrend`) implemented all the required features and
provided their own API (different from the standard PyQWt5 API).

### High level plot widgets & compatibility with the old classes

While we focus on providing a modular, tool/item based usage
pattern, it would be useful to also provide convenience high-level
plot widgets which incorporate by default most of the implemented
features and which could roughly substitute `TaurusPlot`,
`TaurusTrend`, etc. The important thing to note is that these
high-level classes would be implemented as an aggregation of the
smaller, modular ones, and instead of providing an ad-hoc API
for customizing them, the specialized needs would covered buy
building a new class from the generic pyqtgraph classes and our
tools/items.

In terms of backwards compatibility with the existing classes,
we aim for *feature*-compatibility, but *not* for full
*API*-compatibility. Providing full API compatibility would be
difficult in some cases, would clutter the plot classes and would
result in workflows that are not natural in the context of
pyqtgraph. Still, the simplest use cases with the old classes
(e.g. instantiating a plot and calling `setModel`) should work
identically in the new high-level classes. This should actually
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

[PyQwt5]: http://pyqwt.sourceforge.net/
[MoSCoW]: https://en.wikipedia.org/wiki/MoSCoW_method
[cpascual]: https://github.com/cpascual
[oscarprades]: https://github.com/oscarprades


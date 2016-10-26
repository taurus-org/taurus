    Title: Compact Read+Write widgets in Taurus
    TEP: 9
    State: DRAFT
    Date: 2014-01-27
    Drivers: Carlos Pascual-Izarra <cpascual@cells.es>; Tiago Coutinho <coutinho@esrf.fr>
    URL: https://sourceforge.net/p/tauruslib/wiki/TEP9
    License: http://www.jclark.com/xml/copying.txt
    Abstract:
     Providing a common pattern for compact widgets which
     both display the read value of an attribute and allow 
     the user to change the write value


Introduction
============

*This TEP is a copy of [SEP9](https://sourceforge.net/p/sardana/wiki/SEP9 "Sardana Enhancement Proposal 9")*

Taurus currently provides a set of widgets for displaying values of attributes (implemented mostly in the taurus.qt.qtgui.display module) and a separate set of widgets allowing to modify such values (implemented mostly in the taurus.qt.qtgui.input module and which inherit from TaurusBaseWritableWidget abstract class).

In practice, these two sets are often used together to provide control of an attribute, and very often this is done via a TaurusForm which puts a display widget next to an input widget for the same attribute (an also typically uses another widget for a label and another for displaying units).

A recurrent feature request from users is to provide a more compact way of viewing and writing to an attribute. This TEP intends to provide a "canonical" way of doing it.


Goals and Constrains
====================

The following goals and constraints are taken into consideration for this proposal:

1. Existing widgets should be used as much as possible (i.e., combine, not rewrite)
2. The resulting compact widgets should work well stand-alone
3. The resulting compact widgets should be integrable with TaurusForms
4. TaurusForms should offer a choice of showing a "compact" or "extended" (aka "traditional") mode . Possibly even allow for system-wide configuration.
5. The aspect of existing GUIs should be kept (i.e., the "compact" mode should not be imposed as default)
6. All the expected features of both display and input widgets should be implemented in the compact version (e.g., a compact viewer+editor of an scalar attribute, should allow displaying quality of the attribute **and** notifying pending operations from the input widget)
7. If possible, a common abstract class (or limited set of abstract classes) should be implemented to help in creating compact widgets for different types of attributes. 

Implementation
==============

A sep9 branch in the official repository has being created to host an implementation proposal:
https://sf.net/p/sardana/sardana.git/ci/sep9/tree/

Proposed implementation 1
-------------------------
The compact widget is implemented by adding a "read" widget and a "write" widget to a QStackLayout, and allowing the user to switch between the two.

A very basic prototype which already fulfilled goals 1, 2, 3 and 6 was submitted to the sardana-devel mailing list:
https://sf.net/p/sardana/mailman/message/31624240/
This prototype was further developed in the [sep9 branch](https://sourceforge.net/p/sardana/sardana.git/ci/sep9/tree/) which, at its [commit f90ed28](https://sourceforge.net/p/sardana/sardana.git/ci/f90ed285c5ccb0295389426dd1eeef1205c0aea1/) already fulfilled all stated goals of this TEP.


Other considerations
--------------------

- Should we go further and include the units in the "display widget"? (e.g., for a Taurus Label, use a suffix).
    - pros: 
        - much more compact
    - cons: 
        - more complicated to integrate (not all display widgets would be ale to implement this, so we should allow combinations of "compactness")
        - requires new display widgets

- Widgets inheritting from TaurusValue: Sardana currently provides some widgets which inherit from TaurusValue (PoolMotorTV, PoolIORegisterTV,...) and users may have created their own versions as well. Some of these widgets may not be currently compatible with the compact mode (note that at least the compact mode is not used by default). Since the user may switch to compact mode, we propose that, until the widgets support it, they should just reimplement setCompact() to ignore the compact mode request:

~~~~~
     def setCompact(*a):
         pass
~~~~~

Links to more details and discussions
=====================================

The main discussions for this TEP take place in the [tauruslib-devel mailing list](https://sourceforge.net/p/tauruslib/mailman/). See:
- The [initial SEP9 thread](https://sourceforge.net/p/sardana/mailman/message/31709538/).


License
=======

This document is under the Expat License. The following copyright statement and license apply to this document.

Copyright (c) 2014  Carlos Pascual-Izarra

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
-------

* 2014-01-27
  [tiagocoutinho](https://sourceforge.net/u/tiagocoutinho/) Initial version written as a copy of SEP9

* 2013-12-09:
  [cpascual](https://sourceforge.net/u/cpascual/) Promoting to CANDIDATE

* 2013-12-03:
  [cpascual](https://sourceforge.net/u/cpascual/) Initial draft written

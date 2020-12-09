    Title: Implement support for Qt5 in taurus
    TEP: 18
    State: ACCEPTED
    Date: 2019-01-28
    Drivers: Carlos Pascual-Izarra cpascual@cells.es
    URL: http://www.taurus-scada.org/tep/?TEP18.md
    License: http://www.jclark.com/xml/copying.txt
    Abstract: 
     Implement support for Qt5 in taurus. Also define the 
     migration strategy for applications using taurus. 
     

## Intro

PyQt4 has been deprecated and unsupported for quite some time.

Support for Qt4 is going to be dropped in debian buster (freeze
coming in Jan2019) and packages depending on Qt4 will be dropped.
A release critical bug on taurus is already pending (see [taurus_bug])

### Current situation

The current Taurus stable release (4.4) provides a shim module 
(`taurus.external.qt`) which is used throughout the taurus and which is 
recommended for apps using taurus.

The current implementation of `taurus.external.qt` was adapted
from an early version in `spyder` and heavily modified by
us, but it is definitely buggy for bindings other than PyQt4.
It is also "dirty" due to legacy code related to sip API 1
(which is no longer supported in Taurus 4).

The taurus files (and the apps using taurus 4) are currently written in PyQt4 style,
(e.g. without differentiating QtGui and QtWidgets).

### Goals

These are **desired** goals in rough order of importance. They are **not**
all compatible with each other:

1. Allow taurus to run with PyQt5 binding
2. Do not force apps using taurus to migrate to Qt5 (i.e. still support 
   the PyQt4 binding and respect the app choice of bindings)
3. Keep backwards-compat (do not impose code changes on apps that use`taurus.external.qt`)
4. Avoid patching the loaded binding (or at most make only "inoquous" patches)
5. Use existing solution. Avoid reinventing / maintaining our own solution.
6. Modernize the code style in taurus (use Qt5 code style throughout taurus)
7. Minimize the amount of changes needed in the taurus code
8. Avoid introducing heavy dependencies in the `taurus.qt` submodule


## Proposed implementation

This section describes and justifies the key decisions behind the proposed implementation.

### Existing shims used as references

We studied Qt shims implemented by other projects:

- spyder:  [qtpy] : Emulates <s>PyQt5</s> PySide2 binding for the other bindings. It may patch the 
  existing binding in incompatible ways (side-effects). It provides some wrappers. 
  It is popular and has an active and responsive community. It is intended to be used by other projects.
- Qt.py: [Qt.py] : Emulates PySide2 binding for the other bindings. It avoids patching by 
  design in favour of wrappers. It is intended to be used by other projects.
- silx: [silx.qt] : Provides a custom consolidated module that is uniform across bindings 
  (e.g. the `silx.qt` module provides all classes from QtCore, QtGui, QtWidgets, ....). 
  It also provides some wrappers and does limited inocuous patching. It is more of a 
  custom solution, not designed to be used by other projects.
- pyqtgraph [pyqtgraph.Qt] : Emulates PyQt4 binding for the other bindings. It patches existing bindings 
  adding members (e.g. if using the PyQt5 module, it monkey-patches all QtWidgets into QtGui). 
  It is more of a custom solution, not designed to be used by other projects.

### Necessity of writing our own shim (but not from scratch!)

After studying all the mentioned implementations, we conclude that all of them fulfill 
Goals 1 and 2 but none of them, if used directly *as-is* fulfills Goal 3: qtpy 
and Qt.py impose using PySide2 style (e.g. they do not expose pyqtSignal). In the case 
of silx.qt, the layout of the consolidated `silx.qt` does not provide, e.g. `QtGui` or `QtCore`, 
which is expected by apps that use `taurus.external.qt.QtGui`. In the case of `pyqtgraph.Qt`,
since it does not separate the submodules into subpackages, something like 
`from pyqtgraph.Qt.QtCore import QObject` fails.

Therefore we are forced to do some custom shimming if we want to keep backwards compatibility
for apps using `taurus.external.qt`. While this necessarily implies renouncing to fulfill 
Goal 5, we still considered importing one of the existing shims in order to "outsource"
some of the maintenance effort.

Unfortunately, importing `silx.gui.qt` or `pyqtgraph.Qt` would go 
against Goal 8 (even if both silx and pyqtgraph are dependencies for some submodules 
of `taurus.qt.qtgui`, we would like to avoid making them mandatory at the `taurus.qt` 
level since they are relatively heavy). 

On the other hand, `qtpy` and `Qt.py` are probably light enough to consider using them but 
the fact that `Qt.py` is not yet packaged for debian and that the version of `qtpy` packaged 
in debian9 introduces disruptive patching of the PyQt4 binding ([qtpy_issue119]) weighted
against it. 

In conclusion, for the proposed implementation we opted for writing our own shim based heavily
on the qtpy implementation, but with enough changes that Goal 5 cannot be considered 
as being fulfilled.

### Patching instead of wrapping

Regarding the way of smoothing binding incompatibilities, we should avoid patching existing 
bindings (Goal 4). In this regard, the approaches of Qt.py and silx.gui.qt should be our 
reference. The preferred solution is to use adapters (`taurus.external.qt.Qt*`)
and provide compatibility wrappers whenever this cannot be done. In the worst case, we could
accept patching an existing binding, but only if the result never introduces 
a side-efect in an application that uses valid code (similar to the compromise taken in 
[qtpy_issue121]).

### Bindings support

Our priority is on adding PyQt5 (v>=5.6) binding support while maintaining the PyQt4 binding 
(v>=4.6) support. 
The proposed implementation also attempts to provide PySide and PySide2 support, but the 
development and testing is done on PyQt4 and PyQt5 and therefore this first proposed 
implementation is likely not expected to be fully functional under PySide/Pyside2. 
Nevertheless, this situation is subject to change if there is enough interest in the 
community to dedicate more efforts to test and support taurus with PySide and/or PySide2.

The proposed implementation allows the user to select the QT binding by declaring 
the `QT_API` environment variable with one of the currently accepted values:

- `pyqt` (or `pyqt4`) for PyQt4
- `pyqt5` for PyQt5
- `pyside2` for PySide2
- `pyside` for PySide

If the `QT_API` environment variable is not declared, Taurus will fall back to the value set in
`taurus.tauruscustomsettings.DEFAULT_QT_API`.

If the selected binding is not available in the system, Taurus will try the next 
ones from the list above.

### Support for multiple Qt styles within taurus.external.qt

Independently of which plugins are supported as backends, we had to decide which programming 
style(s) are be supported. For example, qtpy supports all 4 plugins but only one programming 
style (that of PySide2). 

In our case, the Goal 3 immediately dictates that we must support at least the PyQt4 style.
Also, by guaranteeing  backwards compatibility for the apps using `taurus.external.qt`, we 
are also allowing `taurus.qt` itself to keep using the old style (fulfilling Goal 7).

On the other hand, Goal 6 demands that we also support PyQt5 or PySide2 style but 
for simplicity, we focused the proposed implementation in providing good support for the currently 
supported style (PyQt4) regardless of the binding. In other words, the proposed 
implementation does not fulfill Goal 6 (but it still is flexible enough to allow the support of
a more modern style in the future)

## How to import Qt modules when writing taurus code.

Until v 4.4, we have recommended taurus users to always import QtCore, QtGui, etc
from `taurus.external.qt`. But with the improved support of multiple bindings
provided by this TEP, this recommendation can be revised as follows:

- *For code that is going to be part of Taurus* (and consequently potentially
  used as library by other other people), Qt, QtGui, QtCore, etc. should still be
  imported from `taurus.external.qt`. The same applies to plugins to taurus
  that intend to be used as a library (otherwise, the plugins should be capable
  of failing gracefully in case of incompatible bindings).

- *For an end-user application based on taurus* it is probably better to import
  directly from a specific binding (PyQt5 is the best supported) and let taurus to
  adapt to that choice. In this way, one can write idiomatic code that better
  matches the chosen binding. Using the `taurus.external.qt` shim 
  is also possible if one wants to make the code binding-agnostic, but in that
  case one must keep in mind that the resulting code will be less idiomatic 
  and that the shim's API may be eventually altered to better fit with taurus 
  own requirements (and that those changes may not be aligned with the 
  application needs).
  
Notes: 
- See the APPENDIX I for tips for writing code that is Qt binding agnostic
- See the APPENDIX II for code snippets that exemplify different ways of using 
  the `taurus.external.qt` shim  from the proposed implementation. 


## Links to more details and discussions

Discussions for this TEP (and the proposed implementation) are conducted in its 
associated Pull Request:

https://github.com/taurus-org/taurus/pull/814

Related issues are:

https://github.com/taurus-org/taurus/issues/203
https://github.com/taurus-org/taurus/issues/148


## APPENDIX I: Tips for writing code that is Qt binding agnostic:

Apart from using taurus.external.qt for importing the Qt submodules, the
following tips were found useful when porting applications to taurus 4.5

- all signal usage must be ["new-style signals"](http://pyqt.sourceforge.net/Docs/PyQt4/new_style_signals_slots.html)
    - and keep in mind that signals with default arguments are not 
      supported in exposed as various signals in PyQt>=5.3 

- Use only APIv2 (e.g. QString should *not* be used,...). One way to ensure that
  your code uses APIv2 (in case that you use PyQt4) is to 
  [explicitly set it](http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html) 
  **before importing PyQt4**:
  ```python
  import sip  
  sip.setapi('QString', 2)
  sip.setapi('QVariant', 2)
  sip.setapi('QDate', 2)
  sip.setapi('QDateTime', 2)
  sip.setapi('QTextStream', 2)
  sip.setapi('QTime', 2)
  sip.setapi('QUrl', 2)
  ```
  
- [QVariant should not be used at all](http://pyqt.sourceforge.net/Docs/PyQt5/pyqt_qvariant.html):
  replace `QVariant(foo)`, `from_qvariant(foo)` and `to_qvariant(foo)` 
  by `foo`. Also replace any occurrence of `QVariant()` (i.e. null `QVariant`) 
  by `None`.
  
- The code should not use Qt deprecated features. See the following for a 
  list of things to keep in mind:
    - https://pyqt.readthedocs.io/en/latest/incompatibilities.html 
    - https://pyqt.readthedocs.io/en/latest/pyqt4_differences.html

- Multiple inheritance. See
  http://pyqt.sf.net/Docs/PyQt5/pyqt4_differences.html#cooperative-multi-inheritance
    - Note that in Taurus we use explicit calls to __init__ methods which
      in some cases it can lead to double-calls to initialization code in pyqt5.
      This needs to be addressed.
    - Also note that we had to convert some positional args into keyword args in
      our mixin classes (TaurusBaseComponent,...) to make them work with Qt5
      
- The `taurus.qt.qtgui.plot` module depends on the Qwt5 module to provide its
  full API, but Qwt5 is only available in the PyQt4 binding and therefore the
  `taurus.qt.qtgui.plot` module has been deprecated. For the other bindings,
  this module attempts to provide a very limited backwards compatibility API
  if the `taurus_pyqtgraph` module is installed. If an application is intended 
  to support PyQt4 only, then it can avoid the deprecation warnings by replacing
  `taurus.qt.qtgui.plot` by `taurus.qt.qtgui.qwt5`. Otherwise, using 
  `taurus.qt.qtgui.tpg` (provided by the `taurus_pyqtgraph` plugin) is recommended.

- `QLayout.margin` and `.setMargin` were [deprecated in Qt 4.8](http://doc.qt.io/archives/qt-4.8/qlayout-obsolete.html)
  Use `.getContentsMargins()` and `setContentsMargins()` instead.
  
- be careful with qInstallMsgHandler (Qt4) vs qInstallMessageHandler (Qt5).
  The following code can be used as a reference:

  ```python
    if hasattr(QtCore, "qInstallMessageHandler"):
        # Qt5
        def taurusMessageHandler(msg_type, log_ctx, msg):
            f = QT_LEVEL_MATCHER.get(msg_type)
            return f("Qt%s %s.%s[%s]: %a", log_ctx.category, log_ctx.file,
                     log_ctx.function, log_ctx.line, msg)

        QtCore.qInstallMessageHandler(taurusMessageHandler)
    elif hasattr(QtCore, "qInstallMsgHandler"):
        # Qt4
        def taurusMsgHandler(msg_type, msg):
            f = QT_LEVEL_MATCHER.get(msg_type)
            return f("Qt: " + msg)

        QtCore.qInstallMsgHandler(taurusMsgHandler)
  ```
  
- Be aware of the [renamed methods in QHeaderView](http://doc.qt.io/qt-5/sourcebreaks.html#changes-to-qheaderview) (from Qt4 to Qt5) 
  and the fact that in Qt5, setSectionResizeMode may **crash the GUI** if 
  called on an empty header. The following code snippet takes care of both 
  issues:
  ```python
  headerView = ... # <-- QHeaderView
  if headerView.length() > 0:
      try:
          headerView.setSectionResizeMode(headerView.Stretch)
      except AttributeError:  # PyQt4
          headerView.setResizeMode(headerView.Stretch)
  ```
  
- Note that the `getOpenFileName`, `getOpenFileNames` and `getSaveFileName` 
  static methods from `QFileDialog` only return the name (or names) in PyQt4 
  but they return a  (name/s, filter) tuple in the other bindings. 
  In order to facilitate writing binding-agnostic code, we provide the
  `getOpenFileName`, `getOpenFileNames` and `getSaveFileName` functions in
  the `taurus.external.qt.compat` module which return the tuple regardless 
  of the binding.

- Beware of [a bug in KDE](https://bugs.kde.org/show_bug.cgi?id=345023) which
  modifies the `text` property of buttons and actions by auto-inserting and
  "&" character in unpredictable positions when running under KDE and using 
  Qt5. In practice the best is to avoid relying on the return value of the
  `text` property of buttons or actions in the program logic.  
  


## APPENDIX II: Some examples of code 

### Code that already works in v4.4:

The following snippets work on taurus 4.4. They should also work after refactoring.

Most common use of `taurus.external.qt` (with implicit selection of PyQt4 binding):

```python
# emulate an application that has previously imported PyQt4 (with API 2)
import sys
import sip
API_NAMES = ["QDate", "QDateTime", "QString", "QTextStream", "QTime", "QUrl",
             "QVariant"]
for name in API_NAMES:
    sip.setapi(name, 2)

import PyQt4.QtGui 

from taurus.external.qt import Qt, QtGui, QtCore
from taurus.qt.qtgui.display import TaurusLabel

a = Qt.QApplication(sys.argv)
o = QtCore.QObject()
w = QtGui.QLabel()
l = TaurusLabel()
```

Most common use of `taurus.external.qt` (with explicit selection of PyQt4 binding) :

```python
import sys
from taurus import tauruscustomsettings
tauruscustomsettings.DEFAULT_QT_API = 'pyqt'

from taurus.external.qt import Qt, QtGui, QtCore
from taurus.qt.qtgui.display import TaurusLabel

a = Qt.QApplication(sys.argv)
o = QtCore.QObject()
w = QtGui.QLabel()
l = TaurusLabel()
```

Exotic (but allowed) use of `taurus.external.qt` (with implicit selection of PyQt4 binding):

```python
# emulate an application that has previously imported PyQt4 (with API 2)
import sys
import sip
API_NAMES = ["QDate", "QDateTime", "QString", "QTextStream", "QTime", "QUrl",
             "QVariant"]
for name in API_NAMES:
    sip.setapi(name, 2)

import PyQt4.QtGui

import taurus.external.qt.Qt
import taurus.external.qt.QtCore
import taurus.external.qt.QtGui
from taurus.qt.qtgui.display import TaurusLabel

a = taurus.external.qt.Qt.QApplication(sys.argv)
o = taurus.external.qt.QtCore.QObject()
w = taurus.external.qt.QtGui.QLabel()
l = TaurusLabel()
```

### code that works with the proposed implementation of this TEP:

Most common use of `taurus.external.qt` (with implicit selection of PyQt5 binding) :

```python
import sys
import PyQt5.QtWidgets  # force using PyQt5 

from taurus.external.qt import Qt, QtGui, QtCore
from taurus.qt.qtgui.display import TaurusLabel

a = Qt.QApplication(sys.argv)
o = QtCore.QObject()
w = QtGui.QLabel()
l = TaurusLabel()

assert(QtGui.QLabel is PyQt5.QtWidgets.QLabel)
```

Most common use of `taurus.external.qt` (with explicit selection of PyQt5 binding) :

```python
import sys 
from taurus import tauruscustomsettings
tauruscustomsettings.DEFAULT_QT_API = 'pyqt5'

from taurus.external.qt import Qt, QtGui, QtCore
from taurus.qt.qtgui.display import TaurusLabel

a = Qt.QApplication(sys.argv)
o = QtCore.QObject()
w = QtGui.QLabel()
l = TaurusLabel()

import PyQt5.QtWidgets
assert(QtGui.QLabel is PyQt5.QtWidgets.QLabel)
```


Exotic (but allowed) use of `taurus.external.qt`:

```python
import sys
import PyQt5.QtWidgets  # force using PyQt5 

import taurus.external.qt.Qt
import taurus.external.qt.QtCore
import taurus.external.qt.QtGui
from taurus.qt.qtgui.display import TaurusLabel

a = taurus.external.qt.Qt.QApplication(sys.argv)
o = taurus.external.qt.QtCore.QObject()
w = taurus.external.qt.QtGui.QLabel()
l = TaurusLabel()
```

Using `taurus.external.qt` with PyQt5 style and Pyqt5 binding:

```python
import sys
from taurus import tauruscustomsettings
tauruscustomsettings.DEFAULT_QT_API = 'pyqt5'

from taurus.external.qt import Qt, QtGui, QtCore, QtWidgets
from taurus.qt.qtgui.display import TaurusLabel

g = QtGui.QGuiApplication(sys.argv)
a = Qt.QApplication(sys.argv)
o = QtCore.QObject()
w = QtWidgets.QLabel()
l = TaurusLabel()
```

## Cases not fully covered in the proposed implementation.

The possibility of using `taurus.external.qt` with Qt5 style but a PyQt4 
binding would be desirable because it would smooth the transition of 
taurus and taurus-based applications towards the newer style (Goal 6) but
out of the scope of the current implementation. 
The following snippet shows an example of some APIs that work in this 
scenario while some other APIs are not yet supported. 

```python
import sys
from taurus import tauruscustomsettings
tauruscustomsettings.DEFAULT_QT_API = 'pyqt'

from taurus.external.qt import Qt, QtGui, QtCore, QtWidgets
from taurus.qt.qtgui.display import TaurusLabel

g = QtGui.QGuiApplication(sys.argv)  # <-- this is Qt5 style and not supported
a = Qt.QApplication(sys.argv)
o = QtCore.QObject()
w = QtWidgets.QLabel()  # <-- this is Qt5 style but is supported
l = TaurusLabel()
```

## License

Copyright (c) 2018 Carlos Pascual-Izarra

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

- 2018-10-04 [cpascual][]. Initial version
- 2018-11-27 [cpascual][]. Moving to CANDIDATE. Prototype implementation underway
- 2019-01-16 [cpascual][]. Update text to reflect the finished proposed implementation.
- 2019-01-28 [cpascual][]. Moving to ACCEPTED (merged https://github.com/taurus-org/taurus/pull/814)



[taurus_bug]: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=875202
[qtpy_issue119]: https://github.com/spyder-ide/qtpy/issues/119
[qtpy_issue121]: https://github.com/spyder-ide/qtpy/issues/121

[qtpy]: https://github.com/spyder-ide/qtpy
[silx.qt]:  https://github.com/silx-kit/silx/blob/master/silx/gui/qt
[pyqtgraph.Qt]: https://github.com/pyqtgraph/pyqtgraph/blob/develop/pyqtgraph/Qt.py
[Qt.py]: https://github.com/mottosso/Qt.py

[cpascual]: https://github.com/cpascual

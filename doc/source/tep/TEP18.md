    Title: Implement support for Qt5 in taurus
    TEP: 18
    State: DRAFT
    Date: 2018-10-04
    Drivers: Carlos Pascual-Izarra cpascual@cells.es
    URL: XXXXX (TODO)
    License: http://www.jclark.com/xml/copying.txt
    Abstract: 
     Implement support for Qt5 in taurus. Also define the 
     migration strategy for applications using taurus. 
     

## Intro

PyQt4 has been deprecated and unsupported for quite some time.

Support for Qt is going to be dropped in debian buster (freeze
coming in Jan2019) and packages depending on Qt4 will be dropped.
A release critical bug on taurus is already pending (see [taurus_bug])

### Current situation

Taurus currently provides a shim module (`taurus.external.qt`) which is
used throughout the taurus and which is recommended for apps using taurus.

The current implementation of `taurus.external.qt` was adapted
from an early version in spyder and heavily modified by
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
6. Modernice the code style in taurus (use Qt5 code style throughout taurus)
7. Minimize the amount of changes needed in the taurus code
8. Avoid introducing heavy dependencies in the `taurus.qt` submodule


## Considerations about implementation

We studied shims implemented by other projects:

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

### Consequences of goals 1, 2 and 3 on the implementation decisions (and on goal 5)

After studying all the mentioned implementations, we conclude that all of them fulfill 
goals 1 and 2 but none of them , if used directly as it is fulfills goal 3. 

Some custom wrapping is necessary in all cases. For example: qtpy 
and Qt.py impose using PySide2 style (e.g. they do not expose pyqtSignal). In the case 
of silx.qt, the layout of the consolidated `silx.qt` does not provide, e.g. `QtGui` or `QtCore`, 
which is expected by apps that use `taurus.external.qt.QtGui`. In the case of `pyqtgraph.Qt`,
since it does not separate the submodules into subpackages, something like 
`from pyqtgraph.Qt.QtCore import QObject` fails.

Therefore we are forced to do some custom shimming if we want to keep backwards compatibility
for apps using `taurus.external.qt`. While this necessarily implies renouncing to fulfill 
goal 5, we can still borrow most of the solutions implemented in the above projects.

### Patching vs wrapping

Regarding the way of smoothing binding incompatibilities, we should avoid patching existing 
bindings (goal 4). In this regard, the approaches of Qt.py and silx.gui.qt should be our 
reference. The preferred solutions are to use adapters `taurus.external.qt.Qt*`
and provide compatibility wrappers whenever this cannot be done. In the worst case, we could
accept patching patching an existing binding, but only if the result never introduces 
a side-efect in an application that uses valid code (similar to the compromise taken in 
[qtpy_issue121]).

### Plugin support

The priority is on adding PyQt5 binding support while maintaining the PyQt4 binding support. 
PySide and PySide2 support is also desirable (and probably easy since we already have the 
examples of the existing implementations that do so), but it is not the main goal of this 
propossal and therefore the TEP may get accepted even if the support for PiSide/PySide2 is 
not complete.    

### Support for multiple Qt styles within taurus.external.qt

A related but not identical decision to the previous one. Independently of which plugins 
are supported as backends, we need to decide on which programming style(s) will be supported.
For example, qtpy supports all 4 plugins but only on programming style (that of PySide2). 

In our case, the goal 3 immediately dictates that we must support at least the PyQt4 style.
Also, by guaranteeing  backwards compatibility for the apps using `taurus.external.qt`, we 
are also allowing `taurus.qt` itself to keep using the old style (fulfilling goal 7).

On the other hand, Goal 6 demands that we also support PyQt5 or PySide2 style but 
for simplicity, we propose to focus this TEP in providing good support for the currently 
supported style (PyQt4) regardless of the binding, and just keep the design flexible enough to
possibilitate the support of a more modern style in the future. In other words, fulfilling 
goal 6 would be optional for this TEP but the chosen design should not block its 
implementation in the future).

Similarly, the same conclusion from the previous paragraph is valid for the PySide and 
PySide2 style support. 

### Reusing existim shims

Another implementation decission revolves around whether importing some of the existing shims 
*within our own shim* to simplify the implementation and maintenance of our own shim 
(i.e., to partially comply with Goal 5). 

In this case, importing `silx.gui.qt` or `pyqtgraph.Qt` would go against goal 8 
(even if both silx and pyqtgraph are dependencies for some submodules of `taurus.qt.qtgui`, 
we would like to avoid making them mandatory at the `taurus.qt` level
since they are relatively heavy). 

On the other hand, qtpy and Qt.py are probably light 
enough to consider using them but the fact that Qt.py is not yet packaged for 
debian and that the version of qtpy packaged in debian9 introduces disruptive patching
of the PyQt4 binding ([qtpy_issue119]). The final decision on this aspect can be left to 
the implementation phase itself and tested in practice. 


## Some examples of code that should work

### code that currently works:

The following snippets work on taurus 4.4. They should also work after refactoring.

Most common use of `taurus.external.qt` (with implicit selection of PyQt4 binding):

```python
# emulate an application that has previously imported PyQt4 (with API 2)
import sip
API_NAMES = ["QDate", "QDateTime", "QString", "QTextStream", "QTime", "QUrl",
             "QVariant"]
for name in API_NAMES:
    sip.setapi(name, 2)

import PyQt4.QtGui 

from taurus.external.qt import Qt, QtGui, QtCore
from taurus.qt.qtgui.display import TaurusLabel

a = Qt.QApplication([])
o = QtCore.QObject()
w = QtGui.QLabel()
l = TaurusLabel()
```

Most common use of `taurus.external.qt` (with explicit selection of PyQt4 binding) :

```python
 
from taurus import tauruscustomsettings
tauruscustomsettings.DEFAULT_QT_API = 'pyqt'

from taurus.external.qt import Qt, QtGui, QtCore
from taurus.qt.qtgui.display import TaurusLabel

a = Qt.QApplication([])
o = QtCore.QObject()
w = QtGui.QLabel()
l = TaurusLabel()
```

Exotic (but allowed) use of `taurus.external.qt` (with implicit selection of PyQt4 binding):

```python
# emulate an application that has previously imported PyQt4 (with API 2)
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

a = taurus.external.qt.Qt.QApplication([])
o = taurus.external.qt.QtCore.QObject()
w = taurus.external.qt.QtGui.QLabel()
l = TaurusLabel()
```

### code that should work after the refactoring:

Most common use of `taurus.external.qt` (with implicit selection of PyQt5 binding) :

```python
import PyQt5.QtWidgets  # force using PyQt5 

from taurus.external.qt import Qt, QtGui, QtCore
from taurus.qt.qtgui.display import TaurusLabel

a = Qt.QApplication([])
o = QtCore.QObject()
w = QtGui.QLabel()
l = TaurusLabel()

assert(QtGui.QLabel is PyQt5.QtWidgets.QLabel)
```

Most common use of `taurus.external.qt` (with explicit selection of PyQt5 binding) :

```python
 
from taurus import tauruscustomsettings
tauruscustomsettings.DEFAULT_QT_API = 'pyqt5'

from taurus.external.qt import Qt, QtGui, QtCore
from taurus.qt.qtgui.display import TaurusLabel

a = Qt.QApplication([])
o = QtCore.QObject()
w = QtGui.QLabel()
l = TaurusLabel()

import PyQt5.QtWidgets
assert(QtGui.QLabel is PyQt5.QtWidgets.QLabel)
```


Exotic (but allowed) use of `taurus.external.qt`:

```python
import PyQt5.QtWidgets  # force using PyQt5 

import taurus.external.qt.Qt
import taurus.external.qt.QtCore
import taurus.external.qt.QtGui
from taurus.qt.qtgui.display import TaurusLabel

a = taurus.external.qt.Qt.QApplication([])
o = taurus.external.qt.QtCore.QObject()
w = taurus.external.qt.QtGui.QLabel()
l = TaurusLabel()
```

## Code that would be nice if it worked, but which is optional

Using `taurus.external.qt` with PyQt5 style and Pyqt5 binding:

```python
from taurus import tauruscustomsettings
tauruscustomsettings.DEFAULT_QT_API = 'pyqt5'

from taurus.external.qt import Qt, QtGui, QtCore, QtWidgets
from taurus.qt.qtgui.display import TaurusLabel

g = QtGui.QGuiApplication([])
a = Qt.QApplication([])
o = QtCore.QObject()
w = QtWidgets.QLabel()
l = TaurusLabel()
```

Using `taurus.external.qt` with PyQt5 style and Pyqt4 binding:

```python
from taurus import tauruscustomsettings
tauruscustomsettings.DEFAULT_QT_API = 'pyqt'

from taurus.external.qt import Qt, QtGui, QtCore, QtWidgets
from taurus.qt.qtgui.display import TaurusLabel

g = QtGui.QGuiApplication([])
a = Qt.QApplication([])
o = QtCore.QObject()
w = QtWidgets.QLabel()
l = TaurusLabel()
```

## Links to more details and discussions

Discussions for this TEP are conducted in its associated Pull Request:

https://github.com/taurus-org/taurus/pull/XXXXX (TODO)

Related issues are:

https://github.com/taurus-org/taurus/issues/203
https://github.com/taurus-org/taurus/issues/148


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



[taurus_bug]: https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=875202
[qtpy_issue119]: https://github.com/spyder-ide/qtpy/issues/119
[qtpy_issue121]: https://github.com/spyder-ide/qtpy/issues/121

[qtpy]: https://github.com/spyder-ide/qtpy
[silx.qt]:  https://github.com/silx-kit/silx/blob/master/silx/gui/qt
[pyqtgraph.Qt]: https://github.com/pyqtgraph/pyqtgraph/blob/develop/pyqtgraph/Qt.py
[Qt.py]: https://github.com/mottosso/Qt.py

[cpascual]: https://github.com/cpascual

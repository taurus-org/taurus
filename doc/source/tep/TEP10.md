    Title: Taurus separation
    TEP: 10
    State: CANDIDATE
    Date: 2014-01-27
    Drivers: Tiago Coutinho <coutinho@esrf.fr>, Carlos Pascual-Izarra <cpascual@cells.es>
    URL: https://sourceforge.net/p/sardana/wiki/SEP10
    License: http://www.jclark.com/xml/copying.txt
    Abstract:
     Separate taurus from sardana. Move taurus to a separate SF project.
     This will allow taurus to have it's own development life cycle.
     This obsoletes items on [SEP1]

Introduction
============

*This TEP is a copy of [SEP10](https://sourceforge.net/p/sardana/wiki/SEP10 "Sardana Enhancement Proposal 10")*

This SEP describes the intention of moving taurus into a separate SF project. 
It obsoletes requirement 2 of [SEP1](https://sourceforge.net/p/sardana/wiki/SEP1). It does *not* obsolete the *sardana suite* concept. 

Motivation
==========

Currently, after the acceptance and implementation of [SEP1](https://sourceforge.net/p/sardana/wiki/SEP1), taurus became a product of the sardana project. Specifically the taurus code became a sub-directory of the sardana git repository.
Many potential users of taurus will be drawn away due to the fact that taurus is a sub-product of sardana. Taurus collaborators feel that taurus should have its own life cycle independent from sardana. Taurus should its own web page, repository, Memorandum Of Understanding (MOU), Taurus Enhancement Proposals (TEP), mailing list, ticket tracker, developers and integration managers.

The main motivation behind requirement 2 of [SEP1](https://sourceforge.net/p/sardana/wiki/SEP1) was to ease development, specifically the tracking of problems in sardana caused by taurus. By having the two libraries (sardana and taurus) in the same repository one could easily identify and revert from revisions that cause problems. While this is a valid requirement it is believed that it can be achieved through a proper code contribution workflow which is already described by the accepted [SEP7](https://sourceforge.net/p/sardana/wiki/SEP7).

Goals
=====

The goals are roughly described in order of priority:

  1. create a new SF taurus project
  2. create a taurus MOU (based on sardana MOU)
  3. create mailing list (developers, users)
  4. create wiki
  5. create ticket tracker

Implementation
==============

The first goal is to create a new SF taurus project. This implies:

1. register new taurus project in SF
2. migrate taurus code from sardana GIT to taurus GIT
    2.1 create a SEP10 branch in sardana GIT and start development there
    2.3 move taurus code from sardana SEP10 GIT branch to taurus GIT
3. develop an extension mechanism in taurus that allows third parties to register widget add-ons
4. move sardana specific code from taurus to sardana. Specifically the python modules:
    4.1. taurus.core.tango.sardana
    4.2. taurus.qt.qtgui.extra_{pool,macroexecutor,sardana}
5. inherit applicable SEPs from sardana
6. activate & configure mailing list
    6.1 copy members of sardana lists to taurus lists
7. activate & configure wiki
8. activate & configure ticket tracker
    8.1 migrate existent sardana tickets with category taurus-* to the new ticket tracker
9. register developers and roles
  


License
=======

Copyright (c) 2014 Tiago Coutinho, Carlos Pascual-Izarra

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

* 2014-01-27 [tiagocoutinho](https://sourceforge.net/u/tiagocoutinho/)
  Initial version written as a copy of SEP10

* 2014-01-15 [tiagocoutinho](https://sourceforge.net/u/tiagocoutinho/)
  Changes to Goals and Implementation according to Carlos comments

* 2014-01-13 [tiagocoutinho](https://sourceforge.net/u/tiagocoutinho/)
  Initial version
 

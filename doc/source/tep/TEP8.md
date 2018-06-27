    Title: Remove from Taurus objects the direct Logger dependence.
    TEP: 8
    State: REJECTED
    Date: 2013-10-30
    Drivers: Carlos Falcon Torres <cfalcon@cells.es>; Tiago Coutinho Macara <tiago.coutinho@esrf.fr>
    URL: http://www.taurus-scada.org/tep?TEP8.md
    License: http://www.jclark.com/xml/copying.txt
    Abstract:
     This document describes the process to remove from Taurus objects 
     the direct Logger dependence.

Introduction
-----
Nowadays, the most of Taurus objects inherited from Logger. This inheritance provide to those objects unnecessary functions and attributes that are using for internal Logger business. Moreover the current Logger design does not allow integrate Taurus with others libraries.

The goal of TEP8 is simplify the Taurus objects inheritance, abstracting the Taurus Logger control functions and attributes, and adapt Taurus Logger API to be able to use external  logger system.

We propose to transfer of the the control Logger functions and attributes to a new intermediate class, using a [Delegation pattern](http://en.wikipedia.org/wiki/Delegation_pattern). With it we will move part of the  inherited features to an inherited (private) object. Besides we propose separate into two step the Logger system: Initialization and Instantiation, doing this second part optional. 


Motivation
-----
The main reason for this change is solve the mixed feature. For the one hand, these changes will simplify the objects, doing their more "light" and easy to understand. For example, a Tango device will reduce the number of attributes and functions visible by a third. For the other hand, removing the direct dependence of Taurus Logger and not assuming the automatically instantiation we could use an external logger, doing Taurus more friendly and compatible with other libraries.


Requirements
-----
Taurus [TEP8] and Sardana [SEP8](https://sourceforge.net/p/sardana/wiki/SEP8/) classes must be backward compatibility. For this reason, the evolution of every change will be prove in a high level, through the cross checking with the current Sardana's applications: Sardana, spock, taurusdesigner, taurusgui, ...

Taurus Logger has to be created in two steps: Taurus Logger initialization and Taurus Logger instantiation. Moreover, to have a Logger system more standard is convenient to use the python logging module as much as possible.

The gross of changes have to be done in log.py file but also the Logger dependencies have to be removed from other files:
```
src/sardana/macroserver/macro.py
src/sardana/macroserver/macros/examples/hooks.py
src/sardana/macroserver/macros/standard.py
src/sardana/macroserver/msdoor.py
src/sardana/macroserver/scan/recorder/output.py
src/sardana/pool/controller.py
src/sardana/pool/pool.py
src/sardana/pool/poolacquisition.py
src/sardana/pool/poolcontroller.py
src/sardana/spock/ipython_00_11/genutils.py
src/sardana/tango/core/util.py
src/sardana/tango/macroserver/Door.py
src/sardana/tango/macroserver/_init_.py
taurus/lib/taurus/core/taurusconfiguration.py
taurus/lib/taurus/core/taurushelper.py
taurus/lib/taurus/core/taurusmanager.py
taurus/lib/taurus/core/taurusmodel.py
taurus/lib/taurus/core/util/log.py
taurus/lib/taurus/core/util/threadpool.py
taurus/lib/taurus/qt/qtcore/util/emitter.py
taurus/lib/taurus/qt/qtdesigner/tauruspluginplugin.py
taurus/lib/taurus/qt/qtgui/application/taurusapplication.py
taurus/lib/taurus/qt/qtgui/base/taurusbase.py
taurus/lib/taurus/qt/qtgui/display/taurusvaluelabel.py
taurus/lib/taurus/qt/qtgui/graphic/taurusgraphic.py
taurus/lib/taurus/qt/qtgui/table/qlogtable.py
taurus/lib/taurus/qt/qtgui/taurusgui/taurusgui.py
taurus/lib/taurus/qt/qtgui/tree/taurusdevicetree.py
```


This is the current Taurus Logger API.

|                            |  Current Taurus Logger API |                            |
| ---------------------------|----------------------------|----------------------------|
|Logger.Critical             |Logger.addLogHandler        |Logger.error                |
|Logger.getParent            |Logger.root_inited          |Logger.exception            |   
|Logger.Debug                |Logger.addRootLogHandler    |Logger.root_init_lock       |
|Logger.getRootLog           |Logger.setLogFormat         |Logger.resetLogLevel        |
|Logger.DftLogFormat         |Logger.call__init__         |Logger.fatal                |
|Logger.info                 |Logger.setLogLevel          |Logger.DftLogLevel          |
|Logger.call__init__wo_kw    |Logger.flushOutput          |Logger.initRoot             |
|Logger.stack                |Logger.DftLogMessageFormat  |Logger.changeLogName        |
|Logger.getAttrDict          |Logger.log                  |Logger.stream_handler       |
|Logger.Error                |Logger.cleanUp              |Logger.getChildren          |
|Logger.log_format           |Logger.syncLog              |Logger.Fatal                |
|Logger.copyLogHandlers      |Logger.getLogFormat         |Logger.log_level            |
|Logger.trace                |Logger.Info                 |Logger.critical             |
|Logger.getLogFullName       |Logger.mro                  |Logger.traceback            |
|Logger.Trace                |Logger.debug                |Logger.getLogLevel          |
|Logger.removeRootLogHandler |Logger.updateAttrDict       |Logger.Warning              |
|Logger.deprecated           |Logger.getLogName           |Logger.resetLogFormat       |
|Logger.warning              |Logger.addChild             |Logger.disableLogOutput     |
|Logger.getLogObj            |Logger.addLevelName         |Logger.enableLogOutput      |
|Logger.getLogger            |



Implementation
----
The main changes have been done in taurus/lib/taurus/core/util/log.py. 
If we compare [fork](https://sourceforge.net/u/cmft/sardana_logger/ci/master/tree/taurus/lib/taurus/core/util/log.py) version with the [current](https://sourceforge.net/p/tauruslib/taurus.git/ci/develop/tree/taurus/lib/taurus/core/util/log.py) version you can see a new class LoggingHelper where was moved the control functions and attributes of Logger class. This solution is 99.99% backward compatible.

Following the patter design, the rest of changes corresponding to change the code for access to the new class members. Logger was replaced by _LoggerHelper and obj.FUNCTION_OR_ATTRIBUTE by obj._logger.FUNCTION_OR_ATTRIBUTE


The Logger functions flushOutput and syncLog were considered deprecated. Them were used internally and were removed from the code. 

The Taurus Logger Trace level was market as deprecated. Right now the Tace level was setting to Debug. The callings of trace function were remplaced by debug.

To uncouple the Taurus Logger initialization and instantiation, The old function initRoot was split in __init__ and  initLogger functions. 

Following one of the requirement Taurus Logger uses internally logging.getLogger instead of getLogger function to access to logger.

To be backward compatible, the variable ENABLE_TAURUS_LOGGER  was added to TaurusCustomSettings. This  variable is used in the functions, __getrootlogger , and in the __init__ of _LoggerHelper class, both defined in taurus.core.util.log. Allowing instantiate the logger class when the variable is equal True or does not defined. In the other case Taurus Logger asume an external logger system. 

    #!/usr/bin/python
    # Code goes here ...
    # Use Taurus Logger API: 
    # True (or commented out) enables the initiatialization of Taurus logger.
    # False Taurus assumed an external Logger system; If it does not exist, 
    #       the Logger API will not work. Showing the following message 
    #       the first time that any Logger message (warning, debug, info, etc)
    #       was executed.
    #
    #    i.e.    Logger.warning('asd')
    #            No handlers could be found for logger "TaurusRootLogger"
    
    ENABLE_TAURUS_LOGGER = True


This is the new Taurus Logger API after the changes:

|                            |   New Taurus Logger API    |                            | 
| ---------------------------|----------------------------|----------------------------|
|Logger.call__init__         |Logger.debug                |Logger.exception            |
|Logger.log                  |Logger.traceback            |Logger.call__init__wo_kw    |
|Logger.deprecated           |Logger.getAttrDict          |Logger.mro                  |
|Logger.updateAttrDict       |Logger.critical             |Logger.error                |
|Logger.info                 |Logger.trace                |Logger.warning              |


Recommendations
----
Nowadays Taurus can work with an external Logger, but if we assumed that Taurus will use its own Logger we recommend manage it from Taurus API instead of the Logger API. This last option was removed (hide) in the new API.

    #!/usr/bin/python
    # Code goes here ...
    import taurus
    taurus.getLogLevel()
    taurus.setLogLevel(LEVEL)
    taurus.getLogFormat()
    taurus.setLogFormat(FORMAT)
    taurus.resetLogLevel()
    taurus.resetLogFormat()
    taurus.enableLogOutput() 
    taurus.disableLogOutput()

  
How to use the new API
----

The code below show how Taurus Logger could be used:

1-If ENABLE_TAURUS_LOGGER = True or does not exist (backward compatibility)

    #!/usr/bin/python
    # Code goes here ...
    import taurus
    taurus.warning('asd')
    MainThread     WARNING  2014-04-24 17:11:03,511 TaurusRootLogger: asd


2-If ENABLE_TAURUS_LOGGER = True and exists external Logger.

    #!/usr/bin/python
    # Code goes here ...
    import taurus
    # External logger
    import logging
    logging.basicConfig()
    taurus.warning('asd')
    WARNING:TaurusRootLogger:asd
    MainThread     WARNING  2014-04-24 17:15:01,619 TaurusRootLogger: asd



3-If ENABLE_TAURUS_LOGGER = False and does not exist external Logger.

    #!/usr/bin/python
    # Code goes here ...
    import taurus
    taurus.warning('asd')
    No handlers could be found for logger "TaurusRootLogger"



4-If ENABLE_TAURUS_LOGGER = False and exists external Logger.

    #!/usr/bin/python
    # Code goes here ...
    import taurus
    import logging             # External logger module
    logging.basicConfig()
    taurus.warning('asd')
    WARNING:TaurusRootLogger:asd


5-If ENABLE_TAURUS_LOGGER = False and manual initialization:

    #!/usr/bin/python
    # Code goes here ...
    import taurus
    taurus.initLogger()
    taurus.warning('asd')
    MainThread     WARNING  2014-04-24 17:02:03,881 TaurusRootLogger: asd


License
-----
The following copyright statement and license apply to TEP8 (this
document).

Copyright (c) 2013 Carlos Falcon Torres - Tiago Coutinho Macara

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
-----
2018-06-27 [cpascual](https://github.com/cpascual/) Change state CANDIDATE --> REJECTED. 
The [proposed implementation](https://github.com/taurus-org/taurus/pull/348) never got 
properly reviewed and it was rendered obsolete by the evolving code. But note that the 
motivation behind this TEP is still valid and as such, another implementation may be
proposed in the future if there is enough interest.

2016-11-16 [mrosanes](https://github.com/sagiss/) Adapt format and URL according to TEP16

2015-05-15 Create TEP8 using SEP8, Fix links according to [TEP10], pass TEP8 to CANDIDATE

2014-04-24 Code review and SEP documentation

2013-10-30
[cmft](https://sourceforge.net/u/cfalcon/) Creation of SEP8


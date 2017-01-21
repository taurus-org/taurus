    Title: Tango-Independent
    TEP: 3
    State: ACCEPTED
    Date: 2016-03-16
    Drivers: Carlos Falcon-Torres <cfalcon@cells.es>, Carlos Pascual-Izarra <cpascual@cells.es>
    URL: http://www.taurus-scada.org/tep/?TEP3.md
    License: http://www.jclark.com/xml/copying.txt
    Abstract:
     The goal of this TEP is to refactor the Taurus core to make the Tango 
     dependency optional instead of mandatory. The idea is to have a generic
     core that accepts any scheme without forcing PyTango. 


Introduction
==================

This TEP describes an enhancement proposal for a refactoring of Taurus to make the Tango dependency optional instead of mandatory.

PS: see also [TEP14][], which extends and complements this proposal.

The TEP3 was created from [SEP3][] after the split of Taurus from sardana according to [SEP10][]. 

Motivation
==================

Taurus evolved from Tau which was conceived as a library for creating GUIs & CLIs on top of a Tango control system. As such, Taurus models incorporate concepts such as "Device", "Attribute", etc that are heavily influenced by Tango.

Lately, however, Taurus models have been extended to allow the interaction with other control systems and/or hardware via the "schemes" extensions (current schemes are: "tango", "simulation", "eval", "epics", "spec").

The tango scheme was the one initially developed, and is not completely isolated from the rest of Taurus. Taurus uses objects from the PyTango module, and assumes naming conventions in many parts of the code, making it impossible to even import taurus if Tango is not installed.

The objective of this proposal is to define a pure Taurus interface so that at least the Taurus core treats Tango just as another (optional) scheme.

Requirements
==================

* It should be possible to use all the features of taurus.core without having PyTango installed. PyTango should not be imported and PyTango objects should not be assumed outside taurus.core.tango

* A clear API should be offered to facilitate the creation of new schemes

* A minimum set of functionality should be defined in an abstract Taurus API so that code using taurus.core can work transparently regardless of the type of scheme that provides the model object

* The refactored taurus.core should be backwards-compatible in general, and in particular it must be backwards-compatible with the tango and evaluation schemes. In case of object name or other API changes, the old names/API should still be usable too (although deprecation warnings may be issued)

API for taurus schemes
======================

Taurus Base/Abstract API for schemes
-------------------------------------

taurus.core must provide the following Base/Abstract classes to be inherited or used in each scheme:   

* TaurusFactory

* TaurusAuthority (corresponding to which was previously known as TaurusDatabase)

* TaurusDevice

* TaurusAttribute  

* TaurusConfiguration        

* TaurusAuthorityNameValidator 

* TaurusDeviceNameValidator

* TaurusAttributeNameValidator

* TaurusConfigurationNameValidator


Specific scheme API
--------------------

A scheme to be used in Taurus must provide the following classes (xxx is the name of the scheme, and the corresponding base class to use is given in parenthesis):

* xxxFactory(TaurusFactory)

* xxxAuthority(TaurusAuthority)

* xxxDevice(TaurusDevice)

* xxxAttribute(TaurusAttribute)

* xxxConfiguration(TaurusConfiguration)

* xxxAuthorityNameValidator(TaurusAuthorityNameValidator) 

* xxxDeviceNameValidator(TaurusDeviceNameValidator)

* xxxAttributeNameValidator(TaurusAttributeNameValidator)

* xxxConfigurationNameValidator(TaurusConfigurationNameValidator)

Keep in mind the following notes:

- The value object returned when reading an attribute model object must be an instance of TaurusAttributeValue (or of a subclass of it).

- The value object returned when reading a configuration model object must be an instance of TaurusConfigValue (or of a subclass of it).

- Note: the validator classes should ideally be implemented using name parsing only (e.g. avoiding to instantiate TaurusModel ojects), and, if possible, avoid requiring the import of optional modules. The base classes provided for validators allow defining a new validator by providing just a few partial regexps for each URI component.


Generic ("scheme-agnostic") Taurus helpers
-------------------------------------------

Users of Taurus are encouraged to write "scheme-agnostic" code whenever it is possible (e.g., code using the taurus.core should try to avoid assuming that a given attribute is of a certain scheme type). 
Checks should be done (whenever it is possible) against the Base/Abstract classes instead of scheme-specific.

Also, taurus.core must provide the following scheme-agnostic factory functions:

* Factory(modelname). Returns a xxxFactory instance.

* Authority(modelname). Returns a xxxAuthority instance.

* Device(modelname). Returns a xxxDevice instance.

* Attribute(modelname). Returns a xxxAttribute instance.

* Configuration(modelname). Returns a xxxConfiguration instance.

taurus.core should also provide utility functions for the following tasks:

- find out cheaply whether a certain model name corresponds to a given Taurus Element Type (Attribute, Device, Database or Configuration). It can be achieved with taurus.isValidName()

- find the scheme associated to a given model name. It can be achieved with taurus.getSchemeFromName()

- find the supported schemes that are available.It can be achieved with taurus.Manager().getPlugins()

Case-sensitivity in models
--------------------------

Tango models are case-insensitive, but this is not generally the case for other schemes. Case insensitivity is assumed in many parts of the code (e.g. through the use of CaselessList and CaselessDict containers to store models). The Factory classes should declare whether the scheme naming is case sensitive or not via a xxxFactory.caseSensitive class attribute (or property).


Refactoring of Model name syntax
================================

The refactoring of the validator classes brings the opportunity of making the model names proper [URIs][1] (i.e., to comply with [RFC3986][2].

Parsing any Taurus model name must yield at least a dictionary with the 
following keys: 'scheme', 'authority', 'path', 'query', 'fragment', 
corresponding to the basic URI components. Additionally, the dictionary 
resulting from parsing the URI of a Taurus device should contain the device name
under the key 'devname'. Similarly for the attribute name in the case of a 
Taurus Attribute (under 'attrname') and for the configuration key in the case of 
Configuration objects (under 'cfgkey'). 

Apart from the keys mentioned above, the dictionary resulting from parsing a 
given URI can contain also other keys for convenience (e.g. for scheme-specific 
definitions) but it is recommended that those keys are prefixed with an 
underscore ("_") to differentiate them from the generic ones.

The validator classes must provide an attribute called 
'namePattern' containing a regexp which validates the model names and which may 
define named groups to help in constructing the dictionary with the above 
mentioned keys.

In the proposed implementation, the validator base classes are created assuming 
the following RFC3986-compliant structure of the names for the Authority, Device, 
Attribute and Configuration element types respectively (note we use Auth instead 
of Database to be scheme-agnostic):

~~~~
Auth: <scheme>:<authority>[/<path>][?<query>][#<fragment>]   
Dev:  <scheme>:[<authority>/]<path>[?<query>][#<fragment>]
Attr: <scheme>:[<authority>/]<path>[?<query>][#<fragment>]
Conf: <scheme>:[<authority>/]<path>[?<query>]#<fragment>
~~~~

Note about syntax: square brackets indicate "optionality" and segment names 
are represented between angle brackets. The rest of the characters are literal)

The proposed base validator classes can then use the mentioned structure to simplify the creation of the 'namePattern'. A base implementation of 'namePattern' exists as a property that returns the name pattern by constructing it from the following attributes:
    
    - scheme
    - authority
    - path
    - query
    - fragment

Each of these attributes should contain the regexp for the same-named segment of the URI

For example, the validator for a Tango database name is:

~~~~
class TangoAuthorityNameValidator(TaurusAuthorityNameValidator):
    '''Validator for Tango authority names. Apart from the standard named 
    groups (scheme, authority, path, query and fragment), the following named 
    groups are created:
    
     - host: tango host name, without port.
     - port: port number
    '''

    scheme = 'tango'
    authority = '//(?P<host>([\w\-_]+\.)*[\w\-_]+):(?P<port>\d{1,5})'
    path = '(?!)'
    query = '(?!)'
    fragment = '(?!)'
~~~~

and the resulting 'namePattern' is:

~~~~
^(?P<scheme>tango):(?P<authority>//(?P<host>([\w\-_]+\.)*[\w\-_]+):(?P<port>\d{1,5}))((?=/)(?P<path>(?!)))?(\?(?P<query>(?!)))?(#(?P<fragment>(?!)))?$
~~~~


Handling backwards compatibility 
--------------------------------

A mechanism should be implemented to provide compatibility with previous syntax.

For example, in pre-TEP3 implementations, '//' was used as part of a separator between the scheme and the rest of the model name instead of as a prefix of authority (which is what RFC3986 dictates).

Usage of old-style model names should be accepted to the maximum possible extent (although deprecation warnings may be issued) 

The proposed API for this is that those validator classes that need to provide backwards compatibility should expose an attribute called 'nonStrictNamePattern' containing a regexp that matches the "old-style" names. Then, the validator's isValid() methods accept a 'strict' flag which, in case of being False, would allow to fall back to the nonStrictNamePattern if the regular validation failed.


New evaluation syntax
---------------------

In order to be RFC3986-compliant, the evaluation scheme model names 
need a radical transformation. 

In the proposed implementation, the following changes have been made:

- 'evaluation' is no longer accepted as an alias of 'eval' as a scheme name
- the model names conform to the structure given in the base validator
classes 
- substitution expressions are handled as part of the path, not the query, 
and must precede the expression itself

So, for example, the old-style model name 

'evaluation://dev=foo;x+y?x=1;y=2' 

would now be written as:

'eval:@foo/x=1;y=2;x+y'


Change in the syntax for TangoConfiguration and EvaluationConfiguration names
-----------------------------------------------------------------------------

The proposed implementation changes the model name syntax for the configuration objects of both the tango and eval schemes. Where before the suffix "?configuration" was used, now "#" is used. Similarly, when a configuration key was defined with the suffix "?configuration=`<cfg_key>`", now it is defined as "`#<cfg_key>`". 

This new syntax has the following advantages: 

- it yields more compact names
- it is easier to parse and handle
- it prepares the field for [TEP14][]'s merge of TaurusConfiguration objects into TaurusAttribute objects.


Adapting existing schemes to TEP3
=================================

Previous to TEP3, five schemes were included in Taurus. The following list summarizes how they are adapted to the TEP3 changes:

- *tango*: the proposed implementation completely ports the tango scheme, including providing backwards compatibility.

- *eval*: the proposed implementation completely ports the eval scheme, including providing backwards compatibility. 

- *simulation*: the proposed implementation removes the simulation scheme (which was used only by the taurusdesigner to provide an offline mock for tango and which was already broken). The necessary changes have been done in taurusdesigner.

- *epics*: the epics scheme is left in an unfinished (unusable) state after the proposed implementation of TEP3. This scheme was just a proof-of-concept and not used in production, so it can be adapted on a later moment (e.g. after [TEP14][]) without blocking the TEP3 acceptance.

- *spec*: the spec scheme is left in an unfinished (unusable) state after the proposed implementation of TEP3. This scheme was just a proof-of-concept and not used in production, so it can be adapted on a later moment (e.g. after [TEP14][]) without blocking the TEP3 acceptance.

- *res*: the res scheme (which provides a model indirection mechanism) is left in an unfinished (unusable) state after the proposed implementation of TEP3. This scheme is not used in production, so it can be adapted on a later moment (e.g. after [TEP14][]) without blocking the TEP3 acceptance.


Refactoring of Value Types, enumerations, etc
=============================================

A description of a refactoring of other taurus.core features such as TaurusAttributeValue and TaurusConfigValue was included into the draft of TEP3, but it has now been moved to [TEP14][].


Links to more details and discussions
======================================

The initial discussions about the SEP3 itself are in the sardana-devel mailing list.
Further (post [SEP10][] split) discussions about TEP3 are held on the tauruslib-devel mailing list.


Follow on and relations with other Enhancement Proposals
========================================================

- This TEP effectively makes the Taurus core tango-independent at the import level (i.e., it makes it possible to import taurus without importing PyTango). But there many implementations details remain that are inherited from the Tango-dependency history. The [TEP14][] proposes a further taurus.core refactoring that eliminates some of the most evident of these "tangoisms", thus simplifying even more the creation of new schemes.

- Once the taurus.core is independent of Tango (and maybe also after [TEP14][]), other proposals should be made to a) make as many widgets from taurus.qt both scheme-agnostic and Tango-independent; and b) to identify and document those that are for some reason bound to one or another scheme.

- The TEP3 was created from [SEP3][] after the split of Taurus from sardana according to [SEP10][]. The [SEP3][] still remains to cover the changes necessary in sardana to adapt to the TEP3 changes.


APPENDIX: Implementation details history
=======================================

Implementation is currently in the tep3 branch of git://git.code.sf.net/p/tauruslib/taurus

The following compilation of tasks was started on 12/08/2014 (by then, many of the requirements from this TEP were already implemented) and was used as a checklist of pending issues before submitting the implementation of TEP3 for approval. The list is kept in this appendix of the TEP3 to provide a historical reference:

- <s>Refactor validators: move code from Taurus to Tango scheme and clean base/abstract validator classes (see [Taurus_URIRefactoring]). Remove some previous implementations. Deprecate "matchLevel" keyword of isValid implementations.</s>
- <s>Tests: provide tests for TDD: Create tests for case (in)sensitivity; clean, document, refactor and/or remove existing tests in taurus.core.test; Implement basic test for tango-independence</s>
- <s>Adapt evaluation scheme to the new design (make more use of Taurus abstract classes)</s>
- <s>Adapt (or remove) simulation scheme (at the moment it is used by the taurusdesigner). Update: the Simulation scheme has been removed</s>
- <s>Clean git history / commit messages and prepare for integration (pushing a cleaner history to sep3 branch in the canonical repo)</s>
- <s>Move Tango-centric code still existing in taurusdatabase.py to the Tango scheme (the code is already clean of PyTango imports, but many tango concepts are still implemented in there and could be moved to the Tango scheme).</s>
- <s>Remove PyTango dependency from TaurusExceptionListener (specific schemes should transform their own specific exceptions into agnostic Taurus-supported exception types if they need to be handled in an special way by Taurus)</s>
- <s>Remove PyTango dependency from the release info of Taurus</s> 
- <s>Check documentation and explain the models in a scheme-agnostic way (see, e.g. http://taurus-scada.org/devel/core_tutorial.html#model-concept)</s>
- <s>TaurusPollingTimer.addAttribute treats tango attributes in a special way (regarding case-sensitivity) by a hardcoded check of the tango scheme. This should be generic. Maybe using a property declared by the scheme.</s>
- <s>Use "authority" instead of "database" everywhere. Still support (but deprecate) the use of "Database". Consider also substituting "Device" by "object"</s>
- <s>Change configuration model name syntax (substitute "?configuration[=cfgkey]" by "#[cfgkey]")</s>
- <s>make sure that the installation procedure is independent of PyTango.</s>

The following  tasks were previously part of the above requirements list, but have been moved to the [TEP14][]:

- Implement quantities support 
- TaurusConfiguration class still has some potentially tango-centric code (concepts such as "Standard unit vs Display unit" or classification into spectrum/image/scalars may require to be re-thought).

The following tasks were previously part of the above requirements list, but have been left out of TEP3 for not being critical. They can be handled as feature requests after approval of TEP3:

- Adapt epics scheme (not strictly needed for TEP3 since epics scheme is a proof-of-concept)
- Adapt spec scheme (not strictly needed for TEP3 since spec scheme is a proof-of-concept)

License
==================

The following copyright statement and license apply to TEP3 (this
document).

Copyright (c) 2013 CELLS / ALBA Synchrotron, Bellaterra, Spain

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
========

2013-06-26
[cmft](http://sf.net/u/cmft/) First draft based on previous documents and discussions with [tiagocoutinho](https://sourceforge.net/u/https://sf.net/u/tiagocoutinho/) and [cpascual](http://sf.net/u/cpascual/)

2013-11-04
[cpascual](http://sf.net/u/cpascual/) Partial rewrite of section on implementation. Also some spellchecking.

2013-11-04
[cpascual](http://sf.net/u/cpascual/) Partial rewrite of section on implementation. Also some spellchecking.

2013-11-06
[cmft](http://sf.net/u/cmft/) Including  "getting things done" section

2014-04-28
[cmft](http://sf.net/u/cmft/) Changed API description for validators

2014-08-13
[cpascual](http://sf.net/u/cpascual/) General update of the document based on code review and discussions with [cmft](https://sf.net/u/cmft/). Also added the "Changes" section.

2014-08-14
[cpascual](http://sf.net/u/cpascual/) Added some more tasks to implementation plan and reference to [Taurus_URIRefactoring](https://sourceforge.net/p/sardana/wiki/Taurus_URIRefactoring/) document

2014-10-03
[cpascual](http://sf.net/u/cpascual/) Updated pending tasks and completed some info about validators

2015-04-28
[cpascual](http://sf.net/u/cpascual/) Adapted latest version of [SEP3][] to update TEP3 and move some parts to [TEP14][]

2015-04-30
[cpascual](http://sf.net/u/cpascual/) Added 'Refactoring of Model name syntax' section using info from [Taurus_URIRefactoring](https://sourceforge.net/p/sardana/wiki/Taurus_URIRefactoring/). Also several other minor changes and improvements.

2015-04-30
[cpascual](http://sf.net/u/cpascual/) passing to CANDIDATE

2015-05-06
[cpascual](http://sf.net/u/cpascual/) Introduced some minor changes according to comments from [zreszela](http://sf.net/u/zreszela/)

2015-05-06
[cpascual](http://sf.net/u/cpascual/) Added the adapting existing schemes to TEP3, and updated the Implementation plan

2015-05-08
[cpascual](http://sf.net/u/cpascual/) Updated the Implementation plan (cross last task) and added section about change in configuration name syntax.

2016-03-16
[cpascual](http://sf.net/u/cpascual/) Passing to ACCEPTED

2016-06-13
[cpascual](http://sf.net/u/cpascual/) Minor formatting fix

2016-11-16
[mrosanes](https://github.com/sagiss/) Adapt TEP format and URL according TEP16

[1]: https://en.wikipedia.org/wiki/URI_scheme#Generic_syntax
[2]: https://tools.ietf.org/html/rfc3986
[TEP14]: http://www.taurus-scada.org/tep/?TEP14.md
[SEP3]: https://sourceforge.net/p/sardana/wiki/SEP3/
[SEP10]: https://sourceforge.net/p/sardana/wiki/SEP10/

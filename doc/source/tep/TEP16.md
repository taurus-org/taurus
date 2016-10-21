Title: Moving Taurus to Github
TEP: 16
State: DRAFT
Date: 2016-10-21
Drivers: Carlos Pascual-Izarra cpascual@cells.es
URL: https://sourceforge.net/p/tauruslib/wiki/TEP16
License: http://www.jclark.com/xml/copying.txt
Abstract: Move Taurus project from its current hosting in SourceForge to 
 GitHub. The move affects the code repository, the ticket tracker and the wiki
 pages. It also proposes to change the contribution workflow to make use of the
 Pull Request feature

Introduction
------------

This SEP describes the intention of migrating the taurus project from its
current hostinf in SourceForge (SF) to the GitHub (GH) service, and to change 
contribution workflow (defined in TEP7) to one based on Pull Requests (PR).

The following reasons are considered in favour of migrating to GH:

- It would alleviate the current saturation of the -devel mailing list 
  (since the code review would be done via PR)
- PR-based workflow for contribution is preferred by all the integrators and
  most of the current contributors and is expected to attract more new 
  contributors
- It would enable the use of Travis for *public* Continuous Integration and 
  Deployment
- GH is perceived as more user friendly than SF
- GH is perceived as providing more visibility than SF
- Tango (with which we share a lot of developers and uers) is currently doing a 
  similar transition.
- Most developers already have an account in GH


The following reasons were considered against migrating to GH:

- GH is a closed-source product (which may raise ethic concerns and increase 
  the risk of lock-in). Gitlab would be preferred in this particular aspect.


Relationship with other Enhancement Proposals
---------------------------------------------

This TEP obsoletes totallly or partially some previous Enhancement 
Proposals (EP), as summarized in the following table:

  Enhancement Proposal  | Part(s) affected
  ------------- | -------------
  TEP7 | most of the contribution procedure (no longer applicable due to adoption of PR-based workflow
  TEP0  | `https://sourceforge.net/p/tauruslib/wiki/TEP` is no longer the index for TEPs, nor it is a wiki
  TEP10 / SEP10 | references to SF
  SEP1 | references to SF
  
A similar Enhancement proposal should be done to the Sardana Community, once
the implementation is tested for this one.

Goals
-----

The goals are roughly described in order of priority:

1. move create a taurus repo within a Taurus GH organization
2. define the new contribution policy
3. define the policy for bug reports / feature requests
4. migrate SF tickets to GH Issues
5. move the TEP pages to a service-independent URL
6. define what to do with the mailing lists

Implementation
--------------

The implementation steps to accomplish each of the goals are listed below:

### Create a taurus repo within a Taurus GH organization

Create an organization: the `taurus` name is already taken in GH. Use 
`taurus-org`. (alternatively we could use `taurus-scada` or `taurus-controls`...

The repo will be created and the following branches pushed:
 
- master
- develop
- support-3.x

The Travis and Appveyor continuous integration services will be enabled for this
repo.

### Define the new contribution policy

Note: A `CONTRIBUTING.md` file should be created at the taurus repo root

TODO: describe new PR-based workflow


### define the policy for bug reports / feature requests

Bugs and feature requests should be reported via Github Issues. Major


### migrate SF tickets to GH Issues

TODO: describe. (see tango migration doc)


### Migrate TEP pages and index


TODO: decide among option a or b  below (I personally prefer option 1)

1. Existing TEP pages will be moved to the source code (somewhere under the doc 
subdir). If we use the .md suffix and copy the actual source, we can visualize 
them from the repo itself. 
2. Instead of moving them to the doc directory, we could put them in the github
wiki.
3. Alternatively, they can be converted into GH issues. This can be combined 
with option 1 (i.e., creating issues that reference the source code  file)


The TEP index page (the one that lists the status) as well 
as the existing TEP pages should be accessible from a URL that can be redirected
to arbitrary URLS (e.g., using the subdomain `tep.taurus-scada.org` subdomain).

A note should be added to EPs affected by this TEP 

### Define what to do with the mailing lists

GH does not provide mailing list hosting. For now, leave them as they are in SF.


License
-------

Copyright (c) 2016 Carlos Pascual-Izarra

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

    2016-10-21 cpascual
    Initial version


```
Title: Moving Taurus to Github
TEP: 16
State: DRAFT
Date: 2016-10-21
Drivers: Carlos Pascual-Izarra cpascual@cells.es
URL: https://github.com/cpascual/taurus/blob/tep16/doc/source/tep/TEP16.md
License: http://www.jclark.com/xml/copying.txt
Abstract: Move Taurus project from its current hosting in SourceForge to 
 GitHub. The move affects the code repository, the ticket tracker and the 
 wiki pages. It also proposes to change the contribution and the TEP 
 workflow to make use of the Pull Request feature.
```
 
## Introduction

This TEP proposes the migration of the taurus project from its
current hosting in SourceForge (SF) to the GitHub (GH) service, and to change 
the contribution workflow (defined in TEP7) to one based on Pull Requests (PR).

The following reasons are considered in favour of migrating to GH:

- It would alleviate the current saturation of the -devel mailing list 
  (since the code review would be done via PR)
- A PR-based workflow for contributions is preferred by all the integrators and
  most of the current contributors and is expected to attract more new 
  contributors
- It would enable the use of Travis for *public* Continuous Integration and 
  Deployment
- GH is perceived as more user friendly than SF
- GH is perceived as providing more visibility than SF
- Tango (with which we share a lot of developers and users) is currently doing
  a similar transition.
- Most developers already have an account in GH


The following reasons were considered against migrating to GH:

- GH is a closed-source product (which may raise ethic concerns and increase 
  the risk of lock-in). Gitlab would be preferred in this particular aspect.


## Relationship with other Enhancement Proposals

This TEP obsoletes totallly or partially some previous Enhancement 
Proposals (EP), as summarized here:

- TEP7: most of the contribution procedure is no longer applicable due 
  to the adoption of PR-based workflow.
- TEP0: `https://sourceforge.net/p/tauruslib/wiki/TEP` is no longer the 
  index for TEPs, nor it is a wiki. The "Creating a TEP section" of TEP0 
  is superseded by the one with the same name in this TEP 
- TEP10 / SEP10:references to SF
- SEP1: references to SF
  
A similar Enhancement proposal should be done to the Sardana Community, 
once the implementation is tested for this one.

## Goals

The goals are roughly described in order of priority:

1. create a taurus repo within a Taurus GH organization
2. define the new contribution policy
3. define the policy for bug reports / feature requests
4. migrate SF tickets to GH Issues
5. move the TEP pages to a service-independent URL
6. define what to do with the mailing lists

## Implementation

The implementation steps to accomplish each of the goals are listed 
below:

### Create a taurus repo within a Taurus GH organization

Create an organization: the `taurus` name is already taken in GH. Use 
`taurus-org`. (alternatively we could use `taurus-scada` or 
`taurus-controls`...

The repo will be created and the following branches pushed:
 
- master
- develop
- support-3.x

The Travis and Appveyor continuous integration services will be enabled 
for this repo.

### Define the new contribution policy

Taurus welcomes contributions via Pull Requests against the `develop` 
branch. For more details, see the `CONTRIBUTING.md` file at the root of 
the repository.


### define the policy for bug reports / feature requests

Bugs and feature requests should be reported via [Github Issues][].


### migrate SF tickets to GH Issues

- Existing tickets in the ticket tracker for the tauruslib project in SF 
  will be migrated using the same tools and procedure described for 
  migrating the tickets of the Tango projects:

https://github.com/tango-controls/svn2git-migration/tree/master/utils/tickets_migration

- The SF ticket tracker will be locked to prevent further ticket 
  creation, and the tool will be renamed to "Old Tickets" in SF. A 
  new SF tool menu entry called "Tickets" will be added pointing to 
  the new taurus GH issues URL

### Migrate existing TEP pages and index

- A file called `TEPX.md` will be created for each existing TEP (X being
  the TEP  number). These files will be located in `<new_tep_location>` 
  within the source code repo. For example, we propose 
  `<new_tep_location>` to be defined as `doc/source/tep`.

- A file called `index.md` will be created in `<new_tep_location>`, 
  containing the info currently in `https://sourceforge.net/p/tauruslib/wiki/TEP`. 
  The provisions in TEP0 for that page now apply to `index.md` (i.e., 
  TEP drivers are required to update the status of their TEP in this 
  page).

- One or more service-provider independent URLs (e.g., `tep.taurus-scada.org`) 
  should be configured to redirect to the new location of the TEPs and the index.
  This service-agnostic URL(s) should be used instead of the GH-specific location
  in all documentation from now on (this allows us to change the location in the 
  future without altering the docs).

- The wiki pages currently served under `https://sourceforge.net/p/tauruslib/wiki/TEP/`
  should now redirect to the new location (if possible, do an automatic redirection,
  but that is too much work, a link in the contents of the files would suffice)

### Define how to start new TEPs

- the process starts when the TEP driver submits PR containing, at least, one
  file called `TEPX[.md|.txt|.rst|...]`, where X is the TEP number and the 
  extension depends on the the markup language used if any (as of today, we 
  recommend `.md`). 
  
- The discussion for this new TEP should take place using the comments and
  similar tools within the PR itself. 
  
- If the TEP includes some proposal of implementation in the form of code, 
  the changes committed as part of the same PR (and reviewed with it).
  
- If the TEP reaches the ACCEPTED stage, the PR is merged (which, at the 
  same time, will bring the source code implementation changes, if any). 
  If the TEP is REJECTED, the integrator will issue a commit in the PR 
  reverting any implementation changes (if any) and then he/she will 
  merge the PR so that the whole discussion history is not lost. 

### Define what to do with the mailing lists

GH does not provide mailing list hosting. For now, continue using 
the existing mailing lists provided by SF. 


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

- 2016-10-21 cpascual
  Initial version



[Github Issues]: https://guides.github.com/features/issues/
    Title: Moving Taurus to GitHub
    TEP: 16
    State: ACCEPTED
    Date: 2016-11-17
    Drivers: Carlos Pascual-Izarra cpascual@cells.es
    URL: http://www.taurus-scada.org/tep?TEP16.md
    License: http://www.jclark.com/xml/copying.txt
    Abstract: 
     Move Taurus project from its current hosting in SourceForge to 
     GitHub. The move affects the code repository, the ticket tracker and the 
     wiki pages. It also proposes to change the contribution and the TEP 
     workflow to make use of the Pull Request feature.
 
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

This TEP obsoletes totally or partially some previous Enhancement 
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

### New taurus repo within a Taurus GH organization

- A GH organization called `taurus-org` will be created (the `taurus`
  name is already taken in GH)

- A `taurus` project will be created within `taurus-org` and the current `master`,
  `develop` and `support-3.x` branches pushed to it

- The Travis and Appveyor continuous integration services will be enabled 
  for this repo.

### New contribution policy

- The new contribution policy will be detailed in the `CONTRIBUTING.md` file 
  at the root of the repository. It should be based on Pull Requests 
  instead of the current email-based policy described in TEP7.

### New policy for bug reports and feature requests

- Bugs and feature requests will be reported via [GitHub Issues][] instead of
  using SF tickets.

### Migration of SF tickets to GH Issues

- Existing tickets in the ticket tracker for the tauruslib project in SF 
  will be migrated using the same tools and procedure described for 
  migrating the tickets of the Tango projects. To this purpose, some tools
  from https://github.com/taurus-org/svn2git-migration will be used.

- The SF ticket tracker will be locked to prevent further ticket 
  creation, and its SF tool menu entry will be renamed to "Old Tickets". A 
  new SF tool menu entry called "Tickets" will be added pointing to 
  the new taurus GH issues URL
  
- Prominent notices will be added in the SF ticket tracker indicating that
  the new GH tracker shouold be used instead.

### New policy for TEPs

- All TEPs will be stored as files in `<new_tep_location>` in the repository. 
  We propose `<new_tep_location>` to be defined as `doc/source/tep`.

- To start a new TEP, the TEP driver submits a PR containing, at least, one
  file called `<new_tep_location>/TEPX[.md|.txt|.rst|...]`, where X is the 
  TEP number and the extension depends on the the markup language used 
  (as of today, we recommend `.md`). 
  
- The discussion for this new TEP should take place using the comments and
  similar tools within the PR itself. 
  
- If the TEP includes some proposal of implementation in the form of code, 
  the changes should be committed as part of the same PR (and reviewed with it).
  
- If the TEP reaches the ACCEPTED stage, the PR is merged (which, at the 
  same time, will bring the source code implementation changes, if any). 
  If the TEP is REJECTED, the integrator will issue a commit in the PR 
  reverting any implementation changes (if any) and then he/she will 
  merge the PR so that the whole discussion history is not lost. 

### Migration of existing TEP pages and index

- A file called `<new_tep_location>/TEPX.md` will be created for each 
  existing TEP (X being the TEP  number).

- A file called `index.md` will be created in `<new_tep_location>`, 
  containing the info currently in `https://sourceforge.net/p/tauruslib/wiki/TEP`. 
  The provisions in TEP0 for that page now apply to `index.md` (i.e., 
  **TEP drivers are required to update the status of their TEP in this 
  page**).

- Service-provider independent URLs will be configured to redirect to the new 
  locations of the TEPs and the index.
  This service-agnostic URLs should be used instead of the SF or GH specific location
  in all documentation from now on (this allows us to change the location in the 
  future without altering the docs). In the proposed implementation, these URLs are:
  
  - `https://www.taurus-scada.org/tep/` (for the TEP index)
  - `https://www.taurus-scada.org/tep/?<TEP_FILE_NAME>` (e.g., for TEP16, this agnostic 
    URL would be https://www.taurus-scada.org/tep/?TEP16.md)

- The wiki pages currently served under `https://sourceforge.net/p/tauruslib/wiki/TEP/`
  should redirect to the new location

### Mailing lists

GH does not provide mailing list hosting. For now, continue using 
the existing mailing lists provided by SF. 

## Links to more details and discussions

Discussions for this TEP are conducted in its associated Pull Request:
https://github.com/taurus-org/taurus/pull/1


## License

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

## Changes

- 2016-11-17 [cpascual][]. Changed state to ACCEPTED
- 2016-11-15 [cpascual][]. Reflect the latest implementation decisions
- 2016-11-02 [cpascual][]. Changed state from DRAFT to CANDIDATE
- 2016-10-26 [cpascual][]. Several changes to get it ready for first announcement of DRAFT
- 2016-10-21 [cpascual][]. Initial version


[GitHub Issues]: https://guides.github.com/features/issues/
[cpascual]: https://github.com/cpascual

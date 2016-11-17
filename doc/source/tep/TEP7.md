    Title: Code contribution workflow
    TEP: 7
    State: OBSOLETE
    Reason: 
     TEP16 obsoletes TEP7. Most of the contribution procedure is 
     no longer applicable due to the adoption of a workflow based on Pull Requests.
    Date: 2014-01-23
    Drivers: Carlos Pascual-Izarra <cpascual@cells.es>, Tiago Coutinho <coutinho@esrf.fr>
    URL: http://www.taurus-scada.org/tep?TEP7.md
    License: http://www.jclark.com/xml/copying.txt
    Abstract:
     Define the procedures for contributing code to taurus. It covers git 
     repository conventions and organization as well as workflows and tools
     for reviewing code contributions.


Introduction
============

*This TEP is a "translation" of [SEP7](https://sourceforge.net/p/sardana/wiki/SEP7 "Sardana Enhancement Proposal 7"). References to sardana have been changed to taurus*

This is a proposal to define the mechanisms for contributing code to Taurus. It describes the agreed conventions for using the git repository as well as the workflow(s) and tools used for reviewing code prior to its acceptance into the official taurus repository.

This proposal tries to answer the following questions:

- Which conventions (e.g., naming, organization...) are used in the official git repository?
- How should one submit a proposed contribution?
- Who approves/rejects proposed contributions?
- Which tools/workflows are used for reviewing the proposed contributed code?


Goals and constraints
=====================

The following goals and constraints are taken into consideration for this proposal:

General:

- **Open development**: we want to encourage participation and contribution. We want an open development project (not just open source). 
- **Code review**: we want taurus to be robust. Contributed code should be reviewed.
- **Integration manager availability**: currently none of the involved people can dedicate 100% of time to coordination tasks. We need to minimize and share the load of coordination/integration.

Specific/technical:

- **SF account required**: we assume that all contributors already have a sourceforge.net account
- **Minimise platform lock-down**: it should be possible to move the project to a different platform if needed in the future, without data loss and without forcing big workflow changes.
- **Minimise imposed log-ins**: contributors and reviewers should be able to do most (if possible, all) their daily work without needing to log into SourceForge. Workflows of contribution/code review which integrate a mailing-list interface are preferred.
- **Contributions traceability**: We would like to have a way of tracking the status of contributions (e.g., proposed / changes needed / accepted / rejected).


Which conventions (e.g., naming, organization...) are used in the official git repository?
==========================================================================================

Branching model for the core repository of taurus
--------------------------------------------------

The official repository of taurus (from now on also called "origin") is organised following the [gitflow](http://nvie.com/posts/a-successful-git-branching-model/) branching model, in which there are two main long-running branches (*master* and *develop*) and a number of support finite-life branches (feature, release and hotfix branches). 

Please refer to http://nvie.com/posts/a-successful-git-branching-model for a full description of the gitflow. The following are notes to complement the gitflow general information with specific details on the implementation of the gitflow model in Taurus:

- The *master* branch reflects the latest official Taurus release. Only the Integration/Release Managers can push to the *master* branch.
- The *develop* branch reflects the latest development changes that have already been integrated for the next release. Only the Integration Managers can push to the *develop* branch.
- New features, bug fixes, etc. must be developed in *feature* branches. They branch off *develop*. Once they are ready and the code passed the review, the feature branch can be merged into *develop* by an Integration Manager. These branches may exist only in local clones of contributors, or in repositories forked from development or, in certain cases, in the official repository (see below).
- The two other types of supporting branches (release branches and hotfix branches) are managed by the Integration/Release managers for the purpose of preparing official releases.

In the Taurus project, we use a special type of *feature* branches called *tepX* branches: unlike other *feature* branches which typically only exist in the contributor local repository (or maybe in a public fork of the official repository), the *tepX* feature branches are hosted in the oficial repository. The *tepX* branch may be created if required during the DRAFT or CANDIDATE phases of the *X*th Taurus Enhancement Proposal, and is merged to *develop* if the TEPX is APPROVED. Only the person(s) dessignated by the TEPX driver -and approved by the Taurus project Admins- can push to the official *tepX* branch. These designated person(s) are considered **"TepX Integration Lieutenants"**.

**Tip**: You can find a set of practical examples on working with the taurus branching model in the [taurus git recipes][]

How should one submit a proposed contribution?
==============================================

In general, code submissions for inclusion in the taurus repositories should take the following into account:

- It must comply with the [**Taurus coding conventions**](http://www.taurus-scada.org/devel/coding_guide.html).
- The **contributor must be clearly identified** and provide a valid email address which can be used to contact him/her.
- Commit messages  should be [properly formatted](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html).
- The **licensing terms** for the contributed code must be compatible with (and preferably the same as) the license chosen for the Taurus project (at the time of writing this TEP, it is the [LGPL](http://www.gnu.org/licenses/lgpl.html), version 3 *or later*).


Submitting code for the core repository of taurus
-------------------------------------------------

The discussion and public tracking of contributed code is done on the [tauruslib-devel mailing list](https://lists.sf.net/lists/listinfo/tauruslib-devel).

Code contributions should be sent to tauruslib-devel@lists.sourceforge.net either in form of patches (formatted with **git format-patch**, as explained [here](http://www.git-scm.com/book/en/Distributed-Git-Contributing-to-a-Project#Public-Large-Project)) or as a pull request (formatted with **git request-pull** as explained [here](http://www.git-scm.com/book/en/Distributed-Git-Contributing-to-a-Project#Public-Small-Project)).

Specific notes for contributing via patches:

- The preferred way of sending the patch formatted with *git format-patch* is using *git send-email*
- Please read http://www.git-scm.com/book/en/Distributed-Git-Contributing-to-a-Project#Public-Large-Project (and use it as a guide)


Specific notes for contributing via pull requests:

- Please read http://www.git-scm.com/book/en/Distributed-Git-Contributing-to-a-Project#Public-Small-Project (and use it as a guide)
- Important: prepend the subject of your email to the mailing list with **`[PULL]`**
- If the changes are not too big, consider using the "-p" option to *git request-pull* (it includes the diff info in the body of the email)

**Tip**: You can find a set of practical examples on how to submit code according to the TEP7 specifications in the [taurus git recipes][]

Who approves/rejects proposed contributions?
============================================

The Taurus community elects a group of people to act as "Integration Managers".

For a given contribution to be accepted into the *develop* branch of the official repository, it has to be submitted to the tauruslib-devel mailing list (as explained before) and approved by at least one **Integration Manager**. If the contributor happens to be an Integration Manager, it is considered good practice to get the approval of *another* Integration Manager before accepting it (although this can be relaxed for trivial contributions).

For a given contribution to be accepted into the *tepX* branch of the official repository, it has to be submitted to the tauruslib-devel mailing list (as explained before) and approved by at least one **TepX Integration Lieutenant**. If the contributor happens to be a TepX Integration Lieutenant, the previous rule can be relaxed, and direct pushes may be allowed. Note that ultimately, the approval of an **Integration Manager** is required once the *tepX* branch is to be merged into the *develop* branch.


Which tools/workflows are used for reviewing the proposed contributed code?
===========================================================================

The code review process for contributions to the official taurus **core** repository is as follows:

1- The contributor submits a contribution to the mailing list (see "How should one submit a proposed contribution?" above).
2- The contribution is publicly reviewed in the mailing list (everyone is encouraged to participate in the review). 
3- During this phase, the contributor may be asked for further clarifications and/or corrections to the contributed code (in which case a resubmission may be required).
4- Eventually, an Integration Manager (or a TepX Integration Lieutenant if the contribution is for a *tepX* branch) may either accept the contribution and integrate it into the official repository, or reject it. In both cases, he/she is posts a message in the mailing list informing of the decision.

**Tip**: You can find a set of practical examples on how to integrate contributed code according to the TEP7 specifications in the [taurus git recipes][]


Naming convention for feature branches
--------------------------------------

The integration of contributed code by an Integration Manager (or Lieutenant) usually involves merging some local branch (let's call it *A*) into the branch that tracks the official repository. Although the *A* branch itself stays local, its name appears in the merge commit message (ending up in the official history). Therefore the following naming convention should be used:

- If the contributed code is related to a bug in the ticket tracker, the branch *A* should be called *bug-N*, where *N* is the ticket number.

- If the contributed code is related to a feature-request in the ticket tracker, the branch *A* should be called *feature-N*, where *N* is the ticket number.

- In the remaining cases, any descriptive name can be used for branch *A* (preferably lower case and reasonably short) provided that it doesn't use any of the reserved names (i.e. master, develop, release-\*, hotfix-\*, tepX, bug-N, feature-N)

Note that those who contribute code via patches do not need to worry about this convention since their local branch names do not affect the official repository history. Nevertheless, it can be a good practice to follow anyway.
 


Links to more details and discussions
=====================================

The main discussions affecting this proposal were held for SEP7 in the [sardana-devel mailing list](https://sourceforge.net/p/sardana/mailman/).

This TEP uses concepts and nomenclature from [chapter 5 of Pro-Git book](http://git-scm.com/book/en/Distributed-Git)

License
=======

Copyright (c) 2014 Carlos Pascual-Izarra

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
* 2016-11-16: [mrosanes](https://github.com/sagiss/) Adapt format, 
  modify URL and change state to OBSOLETE according to TEP16.
  
* 2015-05-13: [cpascual](https://sourceforge.net/u/cpascual/). Made final 
  adaptations in the "translation" from SEP7. Fixed state in header 
  (it was outdated as DRAFT, when it really inherited the ACCEPTED state 
  from SEP7). 

* 2014-01-27: [tiagocoutinho](https://sourceforge.net/u/tiagocoutinho/) 
  Change main author and copyright

* 2014-01-23: [tiagocoutinho](https://sourceforge.net/u/tiagocoutinho/) 
  Initial version written (from SEP7)
  


  [taurus git recipes]: http://sf.net/p/tauruslib/wiki/git-recipes/

# How to release (draft)

This is a guide for taurus release managers: it details the
steps for making an official release, including a checklist
of stuff that should be manually tested.

## The release process

1. During all the development, use the Milestones to keep track of the intended release for each issue
2. Previous to the release deadline, re-check the open issues/PR and update the assignation issues/PR to the release milestone. Request feedback from the devel community.
3. Work to close all the PR/issues remaining open in the milestone. This can be either done in develop or in a release branch called `release-XXX` (where `XXX` is the milestone name, e.g. `Jul17`). If a release branch is used, `develop` is freed to continue with integrations that may not be suitable for this release. On the other hand, it adds a bit more work  because the release-related PRs (which are done against the `release-XXX` branch), may need to be also merged to develop. Note: the `release-XXX` branch *can* live in the taurus-org repo or on a personal fork (in which case you should do step 4.4 and **now** to allow other integrators to push directly to it).
4. Create the release branch if it was not done already in the previous step and:
4.1. Review and update the CHANGELOG.md if necessary. See [this](http://keepachangelog.com)
4.2. Bump version using `bumpversion <major|minor|patch> && bumpversion release`  (use [semver](http://semver.org/) criteria to choose amongst `major`, `minor` or `patch`
4.3. Update man pages:
       `cd <taurus>/doc`
       `./makeman`
       `git add man`
       `git commit -m "Update man pages"`
4.4. Create a PR to merge the `release-XXX` against the **`master`** branch of the taurus-org repo
5. Request reviews in the PR from at least one integrator from each participating institute. The master branch is protected, so the reviews need to be cleared (or dismissed with an explanation) before the release can be merged.
6. Perform manual tests (see checklist below). You may use the CI artifacts (e.g., from appveyor) and post the results in the comments of the PR.
7. Once all reviews a cleared, merge the PR and tag in master
8. Merge also the  `release-XXX` branch into develop, and bump the version of develop with `bumpversion patch`


## Manual test checklist

This is a check-list of manual tests. It is just orientative. Expand it at will.
This list assumes a clean environment with all Taurus dependencies already installed
and access to a Tango system with the TangoTest DS running.

Hint: this list can be used as a template to be copy-pasted on a release PR

### Installation
- [ ] Install Taurus from the tar.gz : `pip install <tarball_artifact_URL>`

### Taurusdemo

- [ ] Test all of the buttons of the taurusdemo. All demos should launch correctly and without raising exceptions
- [ ] For TaurusLabel, check foreground role, the background role, the prefix, the suffix, etc.
- [ ] For TaurusLabel, use a model with fragment (e.g., `sys/tg_test/1/ampli#magnitude`, `eval:Q('1mm')#unit"`)
- [ ] For LCD: Test the foreground roles and the background role
- [ ] For Led: Test the colors, ON color, Off color.

### taurusplot
(basically try all features described in the [user's guide](http://taurus-scada.org/en/latest/users/ui/index.html)

- [ ] Execute: `taurusplot "eval:Q(rand(333),'mm')" sys/tg_test/1/wave`
- [ ] Check region Zoom in and out with region zoom and go back stacked zoom levels with
- [ ] Check mouse wheel Zoom
- [ ] Test panning (dragging with CTRL pressed)
- [ ] Test inspector mode
- [ ] Test pause mode
- [ ] Move curves between axes by clicking on legend (and test zoom on Y2)
- [ ] Test plot configuration dialog
- [ ] Test changing curve titles
- [ ] Test Save & restore config (change curve properties, zoom, etc & check that everything is restored)
- [ ] ... other features from [user's guide](http://taurus-scada.org/en/latest/users/ui/index.html)

### taurustrend
(basically try all features described in the [user's guide](http://taurus-scada.org/en/latest/users/ui/index.html)

- [ ] Execute: `taurustrend "eval:Q(rand(),'mm')" sys/tg_test/1/ampli`
- [ ] Execute: `taurustrend -xe "eval:Q(rand(),'mm')" sys/tg_test/1/ampli`
- [ ] Check region Zoom in and out with region zoom and go back stacked zoom levels with
- [ ] Check mouse wheel Zoom
- [ ] Test panning (dragging with CTRL pressed)
- [ ] Test inspector mode
- [ ] Test pause mode
- [ ] Move curves between axes by clicking on legend (and test zoom on Y2)
- [ ] Test plot configuration dialog
- [ ] Test Forced reading mode
- [ ] Test Save & restore config (change curve properties, zoom, etc & check that everything is restored)
- [ ] ... other features from [user's guide](http://taurus-scada.org/en/latest/users/ui/index.html)

### Test taurusimage

- [ ] Execute `taurusimage --demo`
- [ ] try to resize the image and move it using the mouse.

### taurustrend2d

- [ ] Execute: `taurustrend2d --demo --taurus-polling-period 333`
- [ ] Execute: `taurustrend2d -xt --demo --taurus-polling-period 333`  **(known to fail in 4.1.0)**
- [ ] Execute: `taurustrend2d -xe --demo --taurus-polling-period 333`
- [ ] Test auto-scroll and auto-scale tools
- [ ] Test Save & restore config (change axes range, zoom, tool status colormap etc & check that everything is restored)

### Tauruscurve & taurustrend1d
(unused and to be deprecated, you may test but **do not worry too much if they fail**)

- [ ] Execute: `tauruscurve --demo` and `taurustrend1d "eval:Q(rand(),'mm')"`
- [ ] Change size
- [ ] Move curve with mouse
- [ ] Resize curve with mouse
- [ ] Test some option of the menu with mouse.

### taurusdesigner
- [ ] Check that taurusdesigner is correctly opened and taurus widgets are present in the catalog
- [ ] Create an empty widget and drag various taurus widgets to it (they should be correctly dropped)

### taurusdevicepanel
- [ ] Execute: `taurusdevicepanel sys/tg_test/1`
- [ ] Check that it opens correctly and that the attrs and commands are populated
- [ ] Execute SwitchStates command (see that the state label changes to FAULT and its color to red)
      and then execute the Init command and the label returns to RUNNING (green)

### tauruspanel
- [ ] Execute: `tauruspanel`
- [ ] Navigate in the tree and select the TangoTest device (the attr an command panels should be populated)

### taurusform
(basically try all features described in the [user's guide](http://taurus-scada.org/en/latest/users/ui/index.html)

- [ ] Launch `taurusform sys/tg_test/1/short_scalar`
- [ ] Test to drag and drop of this attribute onto the same form many times (4 times)
      (If it crashes, you are seeing bug #96)
- [ ] Open "Modify Contents" and add sys/tg_test/1 and all of its attributes. They should all show ok
- [ ] Test the compact mode  (switch to compact, noncompact; edit when in compact mode, ...) for a single
      value (from the context menu of a value label)
- [ ] Test compact mode for all values (from the context menu of the whole form)
- [ ] Test changing labels
- [ ] Test re-order of values with "Modify contents"
- [ ] Test the different "show" buttons (tables, images, spectra)
- [ ] Change the write widget of double_scalar by a TaurusWheelEdit
- [ ] Change other read and write widgets
- [ ] ... other features from [user's guide](http://taurus-scada.org/en/latest/users/ui/index.html)

### taurusgui
(basically try all features described in the [user's guide](http://taurus-scada.org/en/latest/users/ui/index.html)

- [ ] Launch `taurusgui example01`
- [ ] Test (un)lock view
- [ ] Create a new panel (a TaurusForm) and drag and drop several models from other forms
- [ ] Move panels around (with view unlocked!) and hide ("close") and re-show them
- [ ] Test saving and restoring perspectives
- [ ] Test drag&drop from a form to a trend
- [ ] Test drag&drop from a form to a trend
- [ ] Test clicking on "example01 synoptic" elements and check that the panels raised
- [ ] Test that selecting a panel changes the selection on "example01 synoptic"
- [ ] Test the actions in the menus
- [ ] Create a new TaurusGui (call it `foogui`) with `taurusgui --new-gui` (follow the wizard)
- [ ] Install `foogui` with pip (using a virtualenv may be a good idea)
- [ ] launch `foogui` using the script that has been installed
- [ ] ... other features from [user's guide](http://taurus-scada.org/en/latest/users/ui/index.html)


### taurusconfigbrowser
- [ ] Open an ini file with taurusconfigbrowser and check that it is loaded correctly.

### taurusiconcatalog
- [ ] Launch `taurusiconcatalog`. Several tabs with an array of icons [should be displayed](http://taurus-scada.org/en/latest/devel/icon_guide.html#taurus-icon-catalog)
- [ ] Check that tooltips give info on each icon
- [ ] Click on some icons and check that they give a bigger view of the icon and more info.
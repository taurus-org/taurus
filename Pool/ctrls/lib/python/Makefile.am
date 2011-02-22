# Sardana device pool tango system

RSYNC_OPTS = -r --cvs-exclude

install-data-local:
	mkdir -p $(pythondir)/poolcontrollers
	rsync $(RSYNC_OPTS) $(srcdir)/communication/* $(pythondir)/poolcontrollers
	rsync $(RSYNC_OPTS) $(srcdir)/countertimer/* $(pythondir)/poolcontrollers
	rsync $(RSYNC_OPTS) $(srcdir)/motor/* $(pythondir)/poolcontrollers
	rsync $(RSYNC_OPTS) $(srcdir)/pseudomotor/* $(pythondir)/poolcontrollers
	rsync $(RSYNC_OPTS) $(srcdir)/pseudocounter/* $(pythondir)/poolcontrollers
	rsync $(RSYNC_OPTS) $(srcdir)/zerod/* $(pythondir)/poolcontrollers
#	rsync $(RSYNC_OPTS) $(srcdir)/oned/* $(pythondir)/poolcontrollers
#	rsync $(RSYNC_OPTS) $(srcdir)/twod/* $(pythondir)/poolcontrollers
	rsync $(RSYNC_OPTS) $(srcdir)/ioregister/* $(pythondir)/poolcontrollers

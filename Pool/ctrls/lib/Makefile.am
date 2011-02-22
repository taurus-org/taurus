SUBDIRS = cpp python
DIST_SUBDIRS = cpp python

RSYNC_OPTS = -r --cvs-exclude

dist-hook:
	mkdir -p $(distdir)/python
	rsync $(RSYNC_OPTS) $(srcdir)/python $(distdir)
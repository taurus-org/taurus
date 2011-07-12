# Sardana device pool tango system
# Adapted from Jens Meyer Makefile.am

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

if MACRO_SERVER

SCRIPTS_IN = MacroServer.in

bin_SCRIPTS = MacroServer
CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = $(SCRIPTS_IN)

do_subst = sed -e 's,[@]pkgpythondir[@],$(pkgpythondir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g'

MacroServer: $(SCRIPTS_IN)
	$(do_subst) < $(top_srcdir)/MacroServer.in > MacroServer
	chmod +x MacroServer

pkgpython_PYTHON = $(top_srcdir)/__init__.py \
		$(top_srcdir)/attributehandler.py \
		$(top_srcdir)/basetypes.py \
		$(top_srcdir)/Door.py \
		$(top_srcdir)/envmanager.py \
		$(top_srcdir)/exception.py \
		$(top_srcdir)/gscan.py \
		$(top_srcdir)/macro.py \
		$(top_srcdir)/macromanager.py \
		$(top_srcdir)/MacroServer.py \
		$(top_srcdir)/manager.py \
		$(top_srcdir)/metamacro.py \
		$(top_srcdir)/modulemanager.py \
		$(top_srcdir)/parameter.py \
		$(top_srcdir)/typemanager.py

RSYNC_OPTS = -r --cvs-exclude

install-data-local:
	rsync $(RSYNC_OPTS) --exclude=*.pyc $(top_srcdir)/scan $(pkgpythondir)
	rsync $(RSYNC_OPTS) --exclude=*.pyc $(top_srcdir)/macros $(pkgpythondir)
	rsync $(top_srcdir)/macro_template.txt $(pkgpythondir)

dist-hook:
	rsync $(RSYNC_OPTS) --exclude=*.pyc $(top_srcdir)/scan $(pkgpythondir)
	rsync $(RSYNC_OPTS) --exclude=*.pyc $(top_srcdir)/macros $(distdir)
	rsync $(top_srcdir)/macro_template.txt $(distdir)
	

endif


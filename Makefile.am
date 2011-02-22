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

SUBDIRS = Pool MacroServer Spock

# In the doc directory we don't want to do anything, just
# make sure it is in the dist.
EXTRA_DIST = README doc

# Even though we do not want to compile anything in the
# doc directory, we still want to install the documentation in
# prefix/classes/doc

rpm: dist
	$(RPM_PROG) $(RPM_ARGS) $(RPM_TARBALL)

RSYNC_OPTS = -r --cvs-exclude

dist-hook:
	rsync $(RSYNC_OPTS) $(top_srcdir)/sardanaGUI $(distdir)
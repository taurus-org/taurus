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

if SPOCK

bin_SCRIPTS = spock
CLEANFILES = $(bin_SCRIPTS)

install-data-local:
	mkdir -p $(pythondir)/spocklib
	rsync $(top_srcdir)/spocklib/__init__.py $(pythondir)/spocklib
	rsync $(top_srcdir)/spocklib/colors.py $(pythondir)/spocklib
	rsync $(top_srcdir)/spocklib/exception.py $(pythondir)/spocklib
	rsync $(top_srcdir)/spocklib/genutils.py $(pythondir)/spocklib
	rsync $(top_srcdir)/spocklib/macroserver.py $(pythondir)/spocklib
	rsync $(top_srcdir)/spocklib/magic.py $(pythondir)/spocklib
	rsync $(top_srcdir)/spocklib/parameter.py $(pythondir)/spocklib
	rsync $(top_srcdir)/spocklib/release.py $(pythondir)/spocklib
    
endif


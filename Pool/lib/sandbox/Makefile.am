# Sardana device pool tango system - pool lib
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


pkgpyexec_LTLIBRARIES = libpypool.la

libpypool_la_LIBADD = -L@TANGO_ROOT@/lib \
    -L@OMNI_ROOT@/lib \
    $(PYTHON_LDFLAGS) \
    -ltango \
    -llog4tango \
    -lomniORB4 \
    -lomniDynamic4 \
    -lomnithread \
    -lCOS4 \
    -lltdl \
    -lpthread

libpypool_la_LDFLAGS = -module -avoid-version
libpypool_la_CXXFLAGS = -Wall -ansi -Wno-invalid-offsetof
libpypool_la_CPPFLAGS = \
    -I@TANGO_ROOT@/include \
    -I@TANGO_ROOT@/include/tango \
    -I@OMNI_ROOT@/include \
    $(PYTHON_CPPFLAGS) \
    -I$(srcdir)/../../include \
    -DREENTRANT 

libpypool_ladir = $(pkgincludedir)

libpypool_la_SOURCES = \
    $(srcdir)/PoolAPI.cpp \
    $(srcdir)/PyPoolAPI.cpp

install-data-local:
	cd $(pkgpythondir) && ln -sf libpypool.so pool.so

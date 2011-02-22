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

pkglib_LTLIBRARIES = poolcom.la

AM_CPPFLAGS = -I@TANGO_ROOT@/include \
				-I@OMNI_ROOT@/include \
				-I/usr/include/python \
				-I$(top_srcdir)/lib
				 
AM_CXXFLAGS = -DREENTRANT 
AM_LDFLAGS = -module -version-info @VERSION_INFO@ 

LDADD = -L@TANGO_ROOT@/lib \
		-L@OMNI_ROOT@/lib \
		-L$(top_builddir)/lib \
		-ltango \
		-llog4tango \
		/usr/lib/libpython2.5.so \
		-lomniORB4 \
		-lomniDynamic4 \
		-lomnithread \
		-lCOS4 \
		-lltdl \
		-lpthread \
		-lpool

poolcom_ladir = $(pkgincludedir)

poolcom_la_HEADERS =

poolcom_la_SOURCES =  $(top_srcdir)/Communication/CommunicationChannel.h \
			$(top_srcdir)/Communication/CommunicationChannelClass.h \
			$(top_srcdir)/Communication/CommunicationChannelUtil.h \
			$(top_srcdir)/Communication/CommunicationChannelPlugin.h \
			$(top_srcdir)/Communication/CommunicationChannel.cpp \
			$(top_srcdir)/Communication/CommunicationChannelClass.cpp \
			$(top_srcdir)/Communication/CommunicationChannelPlugin.cpp \
			$(top_srcdir)/Communication/CommunicationChannelUtil.cpp \
			$(top_srcdir)/Communication/CommunicationChannelStateMachine.cpp




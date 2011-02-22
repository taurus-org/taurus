# Sardana device pool tango system
# Adapted from Jens Meyer configuration script

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



###########################################################################
# AC_INIT initializes autoconf, The first argument is the
# packagename, the second is the version used for the tar file,
# the third is an email address for bug reports (shouldn't be necessary)
AC_INIT([Simulation],[0.0.0],[tcoutinho@cells.es])

###########################################################################
# -version-info CURRENT[:REVISION[:AGE]]
# From the libtool documentation (info libtool)
# So, libtool library versions are described by three integers:

# CURRENT = The most recent interface number that this library implements.

# REVISION = The implementation number of the CURRENT interface.

# AGE = The difference between the newest and oldest interfaces that this
#       library implements.  In other words, the library implements all the
#       interface numbers in the range from number `CURRENT - AGE' to
#       `CURRENT'.
VERSION_INFO=0:0:0


#############################################################################

AC_PREREQ(2.61)
AC_CONFIG_AUX_DIR([.])
AM_INIT_AUTOMAKE([-Wall -Werror])
AM_PATH_PYTHON([2.4])


#########################################################################################
# check if simulation configuration tool (python QT client) should also be compiled and installed
#
AC_ARG_ENABLE([simuconfig],
	[  --enable-simuconfig    Install simulation configuration tool (python QT client) [default=yes]],
	[case "${enableval}" in
		yes) simuconfig=true ;;
		no)  simuconfig=false ;;
		*) AC_MSG_ERROR([bad value ${enableval} for --enable-simuconfig]) ;;
	esac],
	[simuconfig=true])
AM_CONDITIONAL([SIMUCONFIG], [test x$simuconfig = xtrue])

#
# Here we propagate the constants into the makefiles.
#
AC_SUBST(VERSION_INFO)

AC_CONFIG_FILES([Makefile])             
AC_OUTPUT
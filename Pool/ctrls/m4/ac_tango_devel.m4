#
# SYNOPSIS
#
#   AC_TANGO_DEVEL([version])
#
# DESCRIPTION
#
#   Note: Defines as a precious variables "TANGO_VERSION" and 
#   "TANGO_VERSION_HEX". Don't override it in your configure.ac.
#
#   This macro checks for tango and tries to get the include path to
#   'tango.h'. It provides the 
#
#   You can search for some particular version of tango by passing a
#   parameter to this macro, for example ">= '7.1.1'", or "== '7.2'". Please
#   note that you *have* to pass also an operator along with the version to
#   match, and pay special attention to the single quotes surrounding the
#   version number. Don't use "TANGO_VERSION" for this: that environment
#   variable is declared as precious and thus reserved for the end-user.
#
#   This macro should work for all versions of tango >= 7.0. As an end
#   user, you can disable the check for the python version by setting the
#   TANGO_NOVERSIONCHECK environment variable to something else than the
#   empty string.
#
#   If you need to use this macro for an older tango version, please
#   contact the authors. We're always open for feedback.
#
# LAST MODIFICATION
#
#   2011-04-19
#
# COPYLEFT
#
#   Copyright (c) 2011
#
#   This program is free software: you can redistribute it and/or modify it
#   under the terms of the GNU Lesser General Public License as published by the
#   Free Software Foundation, either version 3 of the License, or (at your
#   option) any later version.
#
#   This program is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
#   General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
#

AC_DEFUN([AC_TANGO_DEVEL],[
	AC_MSG_CHECKING([for Tango])
	TANGO_VERSION_HEX=`python -c "import PyTango; \
		v = map(int, PyTango.constants.TgLibVers.split('.')); \
		print '0x%02d%02d%02d00' % (v[[0]],v[[1]],v[[2]])"`
	AC_SUBST([TANGO_VERSION_HEX])
	TANGO_VERSION=`python -c "import PyTango; \
		print PyTango.constants.TgLibVers"`
	AC_SUBST([TANGO_VERSION])
	AC_MSG_RESULT([$TANGO_VERSION])
	#
	# all done!
	#
])

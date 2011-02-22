#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# Device pool - part of the Sardana Tango system
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
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
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

#-------------------------------------------------------------------------------
# AC_INIT initializes autoconf, The first argument is the
# packagename, the second is the version used for the tar file,
# the third is an email address for bug reports (shouldn't be necessary)
#-------------------------------------------------------------------------------
AC_INIT([pool],[0.3.0],[tcoutinho@cells.es])

#-------------------------------------------------------------------------------
# -version-info CURRENT[:REVISION[:AGE]]
# From the libtool documentation (info libtool)
# So, libtool library versions are described by three integers:

# CURRENT = The most recent interface number that this library implements.

# REVISION = The implementation number of the CURRENT interface.

# AGE = The difference between the newest and oldest interfaces that this
#       library implements.  In other words, the library implements all the
#       interface numbers in the range from number `CURRENT - AGE' to
#       `CURRENT'.
#-------------------------------------------------------------------------------
VERSION_INFO=0:3:0

#-------------------------------------------------------------------------------
# Check general prerequisites
#-------------------------------------------------------------------------------
AC_PREREQ(2.61)
AC_CONFIG_SRCDIR([src/Pool.cpp])
AC_CONFIG_AUX_DIR([.])
AM_INIT_AUTOMAKE([1.9 tar-ustar -Wall -Werror])
AM_PATH_PYTHON
AC_PYTHON_DEVEL([>='2.4'])

AC_LIBTOOL_DLOPEN
AC_ENABLE_SHARED(yes)
AC_ENABLE_STATIC(no)
AC_PROG_LIBTOOL

AC_CONFIG_HEADERS([config.h])
AC_CONFIG_LIBOBJ_DIR([lib])
AC_CONFIG_MACRO_DIR([m4])

#-------------------------------------------------------------------------------
# Check for SWIG.
#-------------------------------------------------------------------------------
AC_PROG_SWIG(1.3)
  
#-------------------------------------------------------------------------------
# Checks for programs.
#-------------------------------------------------------------------------------
AC_LANG(C++)
AC_PROG_CXX      dnl check for a c++ compiler
AC_PROG_CXXCPP   dnl check for a c++ preprocessor
AC_PROG_CPP dnl check for a c preprocessor
AC_PROG_INSTALL  dnl check for an install program
AC_PROG_LN_S     dnl check if ln supports the -s switch
AC_PROG_MAKE_SET dnl check if make sets $(MAKE)

#-------------------------------------------------------------------------------
# Checks for header files.
#-------------------------------------------------------------------------------
AC_HEADER_DIRENT
AC_HEADER_STDC
AC_HEADER_STDBOOL
AC_HEADER_TIME
AC_CHECK_HEADERS([limits.h stdlib.h sys/time.h unistd.h])

#-------------------------------------------------------------------------------
# Checks for typedefs, structures, and compiler characteristics.
#-------------------------------------------------------------------------------
AC_C_CONST
AC_C_INLINE

#-------------------------------------------------------------------------------
# Checks for library functions.
#-------------------------------------------------------------------------------
AC_FUNC_CLOSEDIR_VOID
AC_FUNC_ERROR_AT_LINE
AC_FUNC_STRTOD
AC_TYPE_SIGNAL
AC_CHECK_FUNCS([gettimeofday])

#-------------------------------------------------------------------------------
# Check for doxygen
#-------------------------------------------------------------------------------
BB_ENABLE_DOXYGEN


#-------------------------------------------------------------------------------
# Change ld and ar if we're using sunpro compiler  
#-------------------------------------------------------------------------------
RSSH_CHECK_SUNPRO_CC
if test "x$rssh_cv_check_sunpro_cc" = "xyes"; then
   AR="$CXX -xar"
   AR_FLAGS="-o"
   LD="$CXX -pta -G"
#	AC_DISABLE_STATIC

else
	# check the gcc version to use	 
	if test "$CXX" = "c++" -o "$CXX" = "g++"
 	then
		gcc_AC_HAVE_GCC_VERSION(3,3,6)
     		if test "x$ac_cv_gcc_version_3_3_6" = "xno"; then
         	AC_MSG_ERROR([Not supported gcc release. Should be 3.3.6 or above. Please update!], -1)
     	fi
 	fi
fi

#-------------------------------------------------------------------------------
# check if extra controllers should also be compiled and installed
#-------------------------------------------------------------------------------
AC_ARG_ENABLE([extra-ctrls],
	[  --enable-extra-ctrls    Install additional controllers (python and C++) [default=yes]],
	[case "${enableval}" in
		yes) extra_ctrls=true ;;
		no)  extra_ctrls=false ;;
		*) AC_MSG_ERROR([bad value ${enableval} for --enable-extra-ctrls]) ;;
	esac],
	[extra_ctrls=true])
AM_CONDITIONAL([EXTRA_CTRLS], [test x$extra_ctrls = xtrue])


#-------------------------------------------------------------------------------
# get the path to the omniORB installation from the environment variable OMNI_ROOT
# or the --with-omni-prefix configuration option.
#-------------------------------------------------------------------------------
OMNI_ROOT="$OMNI_ROOT"
AC_ARG_WITH(omni-prefix, AC_HELP_STRING([--with-omni-prefix],[prefix to the omniORB installation (default: $OMNI_ROOT)]) ,\
            OMNI_PREFIX=${with_omni_prefix} , OMNI_PREFIX=/usr/local )

if test "x$OMNI_ROOT" = "x"
then
   OMNI_ROOT="$OMNI_PREFIX"
fi

#-------------------------------------------------------------------------------
# Check for the availability of omniORB4/omniORB.h
#-------------------------------------------------------------------------------
if test -f $OMNI_ROOT/include/omniORB4/omniORB.h
then
	# make $OMNI_ROOT available for the Makefiles
	AC_SUBST([OMNI_ROOT], [$OMNI_ROOT])
else
	AC_MSG_ERROR([Cannot find the omniORB.h include file under $OMNI_ROOT/include/omniORB4], -1)
fi


#-------------------------------------------------------------------------------
# get the path to the Tango installation from the environment variable TANGO_ROOT
# or the --with-tango-prefix configuration option.
#-------------------------------------------------------------------------------
AC_ARG_WITH(tango-prefix, AC_HELP_STRING([--with-tango-prefix],[prefix to the Tango installation (default: $TANGO_ROOT)]) ,\
            TANGO_PREFIX=${with_tango_prefix} , TANGO_PREFIX=/usr/local )

if test "x$TANGO_ROOT" = "x"
then
   TANGO_ROOT="$TANGO_PREFIX"
fi
#
# Check for the availability of tango.h
#
if test -f $TANGO_ROOT/include/tango.h
then
	# make $TANGO_ROOT available for the Makefiles
	AC_SUBST([TANGO_ROOT], [$TANGO_ROOT])
else
	AC_MSG_ERROR([Cannot find the tango.h include file under $TANGO_ROOT/include], -1)
fi

#-------------------------------------------------------------------------------
# get the path to the python installation.
#-------------------------------------------------------------------------------

#AC_CACHE_CHECK([for default $PYTHON prefix], [py_prefix],
#  [py_prefix=`$PYTHON -c "import sys; print sys.prefix"`])
#AC_ARG_WITH(python-prefix, AC_HELP_STRING([--with-python-prefix],[prefix to python]) ,\
#            PY_PREFIX=${with_python_prefix} , PY_PREFIX=$py_prefix )
#AC_SUBST([PY_PREFIX], [$py_prefix])

#-------------------------------------------------------------------------------
# Here we propagate the constants into the makefiles.
#-------------------------------------------------------------------------------

AC_SUBST(VERSION_INFO)

AC_CONFIG_FILES([Makefile
                 include/Makefile
                 include/pool/Makefile
                 lib/Makefile
                 lib/Ctrl/Makefile
                 lib/sandbox/Makefile
                 src/Makefile
                 python/Makefile
                 doc/Makefile
                 doc/api/Makefile
                 doc/api/Doxyfile
                 doc/api/html/Makefile])

AC_CONFIG_SUBDIRS([ctrls])

AC_OUTPUT


# do not delete this line. some automake versions have a bug when this file ends with AC_OUTPUT 
# and no new line at the end of the file



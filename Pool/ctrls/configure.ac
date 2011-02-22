#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-
# Device pool controller library - part of the Sardana Tango system
#-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

#-------------------------------------------------------------------------------
# AC_INIT initializes autoconf, The first argument is the
# packagename, the second is the version used for the tar file,
# the third is an email address for bug reports (shouldn't be necessary)
#-------------------------------------------------------------------------------
AC_INIT([PoolControllers],[0.2.0],[tcoutinho@cells.es])

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
VERSION_INFO=0:2:0

#-------------------------------------------------------------------------------
# Check general prerequisites
#-------------------------------------------------------------------------------
AC_PREREQ(2.61)
AC_CONFIG_AUX_DIR([.])
AM_INIT_AUTOMAKE([-Wall -Werror])
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
# Checks for programs.
#-------------------------------------------------------------------------------
AC_LANG(C++)
AC_PROG_CXX      dnl check for a c++ compiler
AC_PROG_CXXCPP   dnl check for a c++ preprocessor
AC_PROG_CPP	 	  dnl check for a c preprocessor
AC_PROG_INSTALL  dnl check for an install program
AC_PROG_LN_S     dnl check if ln supports the -s switch
AC_PROG_MAKE_SET dnl check if make sets $(MAKE)

#-------------------------------------------------------------------------------
# Checks for header files.
#-------------------------------------------------------------------------------
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
	AC_MSG_ERROR([Cannot find the omnORB.h include file under $OMNI_ROOT/include/omniORB4], -1)
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
# get the path to the Pool installation from the environment variable POOL_ROOT
# or the --with-pool-prefix configuration option.
#-------------------------------------------------------------------------------
AC_ARG_WITH(pool-prefix, AC_HELP_STRING([--with-pool-prefix],[prefix to the Pool installation (default: $POOL_ROOT)]) ,\
	        POOL_PREFIX=${with_pool_prefix} )

if test "x$POOL_PREFIX" = "x"
then
	AC_MSG_NOTICE([no pool-prefix was given. Assuming to be invoked by a super package])
	POOL_ROOT=".."
else
	POOL_ROOT="$POOL_PREFIX"
#
# Check for the availability of Ctrl.h
#
	if test -f $POOL_ROOT/include/pool/Ctrl.h
	then
		# make $POOL_ROOT available for the Makefiles
		AC_SUBST([POOL_ROOT], [$POOL_ROOT])
	else
		AC_MSG_ERROR([Cannot find the Ctrl.h include file under $POOL_ROOT/include/pool], -1)
	fi
fi
AM_CONDITIONAL([USE_PARENT_AS_POOL_PATH], [test "x$POOL_PREFIX" = "x"])

#-------------------------------------------------------------------------------
# get the path to the python installation.
#-------------------------------------------------------------------------------

#AC_CACHE_CHECK([for default $PYTHON prefix], [py_prefix],
#  [py_prefix=`$PYTHON -c "import sys; print sys.prefix"`])
 
#AC_ARG_WITH(python-prefix, AC_HELP_STRING([--with-python-prefix],[prefix to python]) ,\
#            PY_PREFIX=${with_python_prefix} , PY_PREFIX=$py_prefix )
#AC_SUBST([PY_PREFIX], [$py_prefix])

#-------------------------------------------------------------------------------
# get the path to the HKL installation from the environment variable HKL_ROOT
# or the --with-hkl-prefix configuration option.
#-------------------------------------------------------------------------------
AC_ARG_WITH(hkl-prefix, AC_HELP_STRING([--with-hkl-prefix],[prefix to the HKL installation (default: $HKL_ROOT)]) ,\
            HKL_PREFIX=${with_hkl_prefix} , HKL_PREFIX=/usr/local )

if test "x$HKL_ROOT" = "x"
then
   HKL_ROOT="$HKL_PREFIX"
fi
#
# Check for the availability of diffractometer.h
#
if test -f $HKL_ROOT/include/hkl/diffractometer.h
then
	# make $HKL_ROOT available for the Makefiles
	AC_SUBST([HKL_ROOT], [$HKL_ROOT])
else
	AC_MSG_NOTICE([Cannot find the diffractometer.h include file under $HKL_ROOT/include/hkl. Diffractometer lib will not be built])
	HKL_ROOT=
fi
AM_CONDITIONAL([DONT_BUILD_DIFFRAC], [test "x$HKL_ROOT" = "x"])

#-------------------------------------------------------------------------------
# Here we propagate the constants into the makefiles.
#-------------------------------------------------------------------------------

AC_SUBST(VERSION_INFO)

AC_CONFIG_FILES([Makefile
                 lib/Makefile
                 lib/cpp/Makefile
                 lib/cpp/communication/Makefile
                 lib/cpp/communication/echo/Makefile
                 lib/cpp/countertimer/Makefile
                 lib/cpp/countertimer/uxtimer/Makefile
                 lib/cpp/motor/Makefile
                 lib/cpp/pseudocounter/Makefile
                 lib/cpp/pseudomotor/Makefile
                 lib/cpp/zerod/Makefile
                 lib/cpp/oned/Makefile
                 lib/cpp/ioregister/Makefile
		         lib/cpp/ioregister/fake/Makefile
                 lib/cpp/twod/Makefile
                 lib/python/Makefile])

AC_OUTPUT

AC_MSG_RESULT([
Configuration ($PACKAGE):
	
	Source code location:       ${srcdir}
	Version:                    ${VERSION}
	Compiler:                   ${ac_ct_CC},${ac_ct_CXX}
        Python:
            Version:                ${PYTHON_VERSION}
            CPP flags:              ${PYTHON_CPPFLAGS}
            LD flags:               ${PYTHON_LDFLAGS}
            site-packages:          ${PYTHON_SITE_PKG}
            

	OMNIORB PATH:               ${OMNI_ROOT} 
	TANGO PATH:                 ${TANGO_ROOT}
	POOL PATH:                  ${POOL_ROOT}
	HKL PATH:                   ${HKL_ROOT}
])

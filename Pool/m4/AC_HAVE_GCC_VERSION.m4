dnl Determine whether we have gcc of a particular version or later,
dnl based on major, minor, patchlevel versions and date.
dnl
dnl gcc_AC_HAVE_GCC_VERSION(MAJOR_VERSION, MINOR_VERSION, PATCH_LEVEL) 
dnl   

AC_DEFUN([gcc_AC_HAVE_GCC_VERSION],
	 [AC_CACHE_CHECK([for gcc compiler release (at least version $1.$2.$3)],
	                 ac_cv_gcc_version_$1_$2_$3,
                         [if test x$GCC = x ; then 
			      ac_cv_gcc_version_$1_$2_$3=no
                          else 
			     ac_gcc_date=0 ; 
                             AC_EGREP_CPP(yes,
    				      	  [#define HAVE_GCC_VERSION(MAJOR, MINOR, MICRO, DATE) \
					  (__GNUC__ > (MAJOR) \
					  || (__GNUC__ == (MAJOR) && __GNUC_MINOR__ > (MINOR)) \
					  || (__GNUC__ == (MAJOR) && __GNUC_MINOR__ == (MINOR) \
    				          && __GNUC_PATCHLEVEL__ > (MICRO)) \
					  || (__GNUC__ == (MAJOR) && __GNUC_MINOR__ == (MINOR) \
    				          && __GNUC_PATCHLEVEL__ == (MICRO) && ${ac_gcc_date}L >= (DATE)))
                                          #if HAVE_GCC_VERSION($1,$2,$3,0)
                                          yes
                                          #endif],
					  ac_cv_gcc_version_$1_$2_$3=yes,
					  ac_cv_gcc_version_$1_$2_$3=no)
		           fi
	                  ])
	  if test x$ac_cv_gcc_version_$1_$2_$3 = xyes; then
	       AC_DEFINE_UNQUOTED(HAVE_GCC_VERSION_$1_$2_$3,
			          1,
				  [Define to 1 if we have gcc $1.$2.$3 ])
	  fi        
         ])

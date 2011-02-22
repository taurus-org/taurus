
BUILT_SOURCES = $(srcdir)/interface_wrap.cpp

SWIG_SOURCES = interface.i

pkgpython_PYTHON = Pool.py

pkgpyexec_LTLIBRARIES = _Pool.la

top_incdir = $(top_srcdir)/src

incdirs = $(PYTHON_CPPFLAGS) \
		-I$(top_srcdir)/include \
		-I$(top_incdir) \
		-I$(top_incdir)/Ctrl \
		-I$(top_incdir)/Controller \
		-I$(top_incdir)/Motor \
		-I$(top_incdir)/MotorGroup \
		-I$(top_incdir)/PseudoMotor \
		-I$(top_incdir)/CTExpChannel \
		-I$(top_incdir)/ZeroDExpChannel \
		-I$(top_incdir)/OneDExpChannel \
		-I$(top_incdir)/TwoDExpChannel \
		-I$(top_incdir)/MeasurementGroup \
		-I$(top_incdir)/CommunicationChannel \
		-I$(top_incdir)/IORegister \
		-I$(top_incdir)/PoolBaseDev \
		-I$(top_incdir)/PoolIndBaseDev \
		-I$(top_incdir)/PoolGroupBaseDev \
		-I$(top_incdir)/PseudoCounter

		
_Pool_la_SOURCES = $(srcdir)/interface_wrap.cpp $(SWIG_SOURCES)
_Pool_la_CPPFLAGS = $(SWIG_PYTHON_CPPFLAGS) $(incdirs)
_Pool_la_LDFLAGS = -module
_Pool_la_LIBADD = ../libpool.la

$(srcdir)/interface_wrap.cpp : $(SWIG_SOURCES)
	$(SWIG) $(SWIG_PYTHON_OPT) $(incdirs) -o $@ $<




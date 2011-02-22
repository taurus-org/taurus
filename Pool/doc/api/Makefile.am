
SUBDIRS = html

docdir  = $(prefix)/doc/@PACKAGE_TARNAME@

.PHONY: dox pdf

all-local: dox 

dox: html html/api/index.html
html/api/index.html: Doxyfile
	@DOXYGEN@

install-data-local:
	$(mkinstalldirs) $(docdir)
	cp -r html/. $(docdir)
	$(RM) -r -f $(docdir)/CVS \
		$(docdir)/.svn \
		$(docdir)/Makefile.am \
		$(docdir)/Makefile.in \
		$(docdir)/Makefile

uninstall-local:
	$(RM) -r -f $(docdir)

clean-local:
	$(RM) -r latex
	$(RM) -r html/api man @PACKAGE_TARNAME@.ps @PACKAGE_TARNAME@.pdf
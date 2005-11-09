export VERSION = 0.70.5
export TOPDIR = $(shell pwd)
export DISTDIR = $(TOPDIR)/epdb-$(VERSION)
export sitedir = $(libdir)/python$(PYVERSION)/site-packages/
export epdb = $(sitedir)/epdb

extra_files =  \
    LICENSE    \
    Make.rules \
    Makefile   \
    NEWS

python_files = __init__.py	\
               epdb.py          \
               stackutil.py     

dist_files = $(extra_files)

.PHONY: clean dist install subdirs

dist: $(dist_files)
	if ! grep "^Changes in $(VERSION)" NEWS > /dev/null 2>&1; then \
		echo "no NEWS entry"; \
		exit 1; \
	fi
	rm -rf $(DISTDIR)
	mkdir $(DISTDIR)
	for d in $(SUBDIRS); do make -C $$d DIR=$$d dist || exit 1; done
	for f in $(dist_files); do \
		mkdir -p $(DISTDIR)/`dirname $$f`; \
		cp -a $$f $(DISTDIR)/$$f; \
	done; \
	tar cjf $(DISTDIR).tar.bz2 `basename $(DISTDIR)`
	@echo "=== sanity building/testing conary ==="; \
	cd $(DISTDIR); \
	make > /dev/null; \
	./conary --version > /dev/null || echo "CONARY DOES NOT WORK"; \
	cd -; \
	rm -rf $(DISTDIR)

tag:
	hg tag epdb-$(VERSION)

clean: default-clean

include Make.rules

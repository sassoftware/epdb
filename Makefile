export VERSION = 0.11
export TOPDIR = $(shell pwd)
export DISTDIR = $(TOPDIR)/epdb-$(VERSION)
export sitedir = $(libdir)/python$(PYVERSION)/site-packages/
export epdbdir = $(sitedir)/epdb

extra_files =  \
    LICENSE    \
    Make.rules \
    Makefile   \
    NEWS

dist_files = $(extra_files)

SUBDIRS=epdb

.PHONY: clean dist install subdirs

all: subdirs

subdirs: default-subdirs

install: all install-subdirs pyfiles-install

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
	rm -rf $(DISTDIR)

tag:
	hg tag epdb-$(VERSION)

clean: default-clean

include Make.rules

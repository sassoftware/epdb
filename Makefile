#
# Copyright (c) rPath, Inc.
#
# This program is distributed under the terms of the MIT License as found 
# in a file called LICENSE. If it is not present, the license
# is always available at http://www.opensource.org/licenses/mit-license.php.
#
# This program is distributed in the hope that it will be useful, but
# without any waranty; without even the implied warranty of merchantability
# or fitness for a particular purpose. See the MIT License for full details.
#

export VERSION = 0.14
export TOPDIR = $(shell pwd)
export DISTDIR = $(TOPDIR)/epdb-$(VERSION)
export sitedir = $(libdir)/python$(PYVERSION)/site-packages/
export epdbdir = $(sitedir)/epdb

extra_files =  \
    LICENSE    \
    Make.rules \
    Makefile   \
    NEWS       \
    setup.py

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

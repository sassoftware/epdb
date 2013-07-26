#
# Copyright (c) SAS Institute, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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

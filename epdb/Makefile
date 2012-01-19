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

all: default-all

extra_files =  \
    Makefile   

python_files = __init__.py	\
               erlcompleter.py  \
               epdb_server.py  \
               epdb_client.py  \
               epdb_stackutil.py \
               formattrace.py \
               excepthook.py

dist_files = $(extra_files) $(python_files)

.PHONY: clean dist install subdirs

install: all pyfiles-install

dist: default-dist

tag:
	hg tag epdb-$(VERSION)

clean: default-clean

include ../Make.rules

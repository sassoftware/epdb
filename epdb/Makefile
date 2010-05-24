all: default-all

extra_files =  \
    Makefile   

python_files = __init__.py	\
               erlcompleter.py  \
               epdb_server.py  \
               epdb_client.py  \
               epdb_stackutil.py     

dist_files = $(extra_files) $(python_files)

.PHONY: clean dist install subdirs

install: all pyfiles-install

dist: default-dist

tag:
	hg tag epdb-$(VERSION)

clean: default-clean

include ../Make.rules

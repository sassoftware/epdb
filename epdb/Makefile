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


all: default-all

extra_files =  \
    Makefile   

python_files = __init__.py	\
               erlcompleter.py  \
               epdb_server.py  \
               epdb_client.py  \
               epdb_stackutil.py \
               formattrace.py

dist_files = $(extra_files) $(python_files)

.PHONY: clean dist install subdirs

install: all pyfiles-install

dist: default-dist

tag:
	hg tag epdb-$(VERSION)

clean: default-clean

include ../Make.rules

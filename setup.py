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


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

Version = "0.12"

setup(name = "epdb",
      version = Version,
      description = "Enhanced Python Debugger",
      long_description="Adds functionality to the python debugger, including support for remote debugging",
      author = "rPath, Inc.",
      author_email = "elliot@rpath.com",
      url = "http://bitbucket.org/rpathsync/epdb/",
      packages = [ 'epdb' ],
      license = 'MIT',
      platforms = 'Posix; MacOS X; Windows',
      classifiers = [ 'Intended Audience :: Developers',
                      'License :: OSI Approved :: BSD License',
                      'Operating System :: OS Independent',
                      'Topic :: Development',
                      ],
      entry_points = {
            'nose.plugins.0.10': [
                'epdb-debug = epdb.epdb_nose:Epdb'
            ]
        }
      )

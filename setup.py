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

#
# Copyright (c) SAS Institute, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

Version = "0.15"

install_requires = ["six",
                    ]

setup(name = "epdb",
      version = Version,
      description = "Enhanced Python Debugger",
      long_description="Adds functionality to the python debugger, including support for remote debugging",
      author = "SAS Institute, Inc.",
      author_email = "elliot.peele@sas.com",
      url = "https://github.com/sassoftware/epdb",
      packages = [ 'epdb' ],
      license = 'MIT',
      platforms = 'Posix; MacOS X; Windows',
      classifiers = [ 'Operating System :: OS Independent',
                      'Intended Audience :: Developers',
                      'License :: OSI Approved :: MIT License',
                      'Topic :: Software Development :: Debuggers',
                      'Programming Language :: Python :: 2',
                      'Programming Language :: Python :: 3',
                      ],
      entry_points = {
            'nose.plugins.0.10': [
                'epdb-debug = epdb.epdb_nose:Epdb'
                ],
            'console_scripts': [
                'epdb = epdb.epdb_client:main',
                ]
            },
      install_requires = install_requires,
      )


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
Version = "0.12"

setup(name = "epdb",
      version = Version,
      description = "Enhanced Python Debugger",
      long_description="Adds functionality to the python debugger, including support for remote debugging",
      author = "David Christian",
      author_email = "dbc@rpath.com",
      url = "http://bitbucket.org/dugan/epdb/",
      packages = [ 'epdb' ],
      license = 'BSD',
      platforms = 'Posix; MacOS X; Windows',
      classifiers = [ 'Intended Audience :: Developers',
                      'License :: OSI Approved :: BSD License',
                      'Operating System :: OS Independent',
                      'Topic :: Development',
                      ],
      )


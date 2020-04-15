Change Log
==========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <http://keepachangelog.com/>`_ and this
project adheres to `Semantic Versioning <http://semver.org/>`_ from version
0.15.1 on.

0.16.0 - 2020-04-14
-------------------

Added
~~~~~

* Support for finding an unused port when serving
* python 3.8 support

Fixed
~~~~~
* CTRL+C was attempting to send a string through the socket, instead of a byte array

0.15.1 - 2016-12-22
-------------------

Added
~~~~~

* Basic documentation in README.rst

Changed
~~~~~~~

* Changed release notes from the NEWS file to this CHANGELOG.rst format.

Fixed
~~~~~

* Fix encoding for python3
* Fix handling of byte arrays in epdb.serve()
* Pass file mode to SavedFile.save()

0.15 - 2015-10-09
-----------------

* Added support for python 3

0.14 - 2014-09-22
-----------------

Added
~~~~~

* Added a 'epdb' client script that waits for a server to appear on a specified port
* Added backtrace formatter and exception hook
* Added contributor agreement

Changed
~~~~~~~

* Updated Copyright to SAS Institute, Inc.

Fixed
~~~~~

* client: fix crash when detaching
* server: play nicer with environments where sys.stdout is not a regular file

0.13 - 2011-12-09
-----------------

Fixed
~~~~~

* Fixed a crash in epdb_client when the terminal is > 255 columns wide
* Fixed terminal control bytes being emitted when epdb is imported

0.12 - 2011-05-03
-----------------

Changed
~~~~~~~
* Changed license to MIT

Fixed
~~~~~

* Fixed crash when trying to serve() from a secondary thread

0.11 - 2007-12-11
-----------------

Fixed
~~~~~

* The post_mortem() command was broken in 0.10, this has been fixed.

0.10 - 2007-09-21
-----------------

Added
~~~~~

* epdb now supports a "serve()" command to serve epdb requests remotely

0.9.1.1 - 2006-07-05
--------------------

Fixed
~~~~~

* epdb will automatically switch to the process group with session control, so
  that in programs where setpgrp() has been called, such processes can still be
  debugged.

0.9.1 - 2006-06-17
------------------

Fixed
~~~~~

* until now works with filenames
* breakpoints/etc that take filenames will also now take sys.module entries,
  e.g. foo.bar, if sys.modules['foo.bar'] exists.

0.9 - 2006-04-03
----------------

Added
~~~~~

* The new fail_silently_on_ioerror config value will allow you to avoid
  raising an exception when a breakpoint is hit an no terminal is
  available. Use with caution as it could allow you to leave unintended
  breakpoints in your program.

Changed
~~~~~~~

* input is set to /dev/tty as well as output if the current input stream
  in not a terminal
* multiline entries will be stored as one entry

Fixed
~~~~~

* readline history should be much more well behaved

0.8.1 - 2005-12-20
------------------

Fixed
~~~~~

* Add cross-session readline history

0.8 - 2005-11-10
----------------

* Initial seperate epdb release
